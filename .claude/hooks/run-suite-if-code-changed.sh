#!/usr/bin/env bash
# Runs the full test suite once when a session or a subagent finishes (Stop and SubagentStop hooks in
# .claude/settings.json), only if the code under mechanistic_pathway_learning/ or tests/ changed since the last
# passing run in that checkout. It replaces the PostToolUse hook that ran the whole suite after every single edit of a
# .py file there (the owner, 20 November 2026: "can you stop it from running the full suite for every code edit and
# only do it when each is done?"), which with several agents at once ran a dozen suites side by side, and always in the
# main checkout even when the edit was in an agent's worktree.
#
# The checkout is the one the hook input names in "cwd" (an agent in a worktree is tested in its worktree), else
# $CLAUDE_PROJECT_DIR. The fingerprint is the SHA-256 of every tracked and untracked, not ignored, .py file under those
# two directories, kept per checkout in its git directory; a passing run records the fingerprint it started from, so a
# change made while the suite ran is tested by the next one. Concurrent runs in one checkout are serialised by a lock:
# a hook that finds the lock held leaves the work to the run already going. Exit 2 (a suite that failed or crashed)
# wakes the session that finished, through asyncRewake, with pytest's FAILED and ERROR lines and its summary line, or
# for a crash with its exit status and what it printed; every other outcome exits 0.
#
# Two outcomes are nothing to report, and exit 0 without waking anyone or recording a pass (so the next run tests the
# code again). A checkout that no longer exists, whatever pytest's exit status: a workflow can delete an agent's
# worktree while the hook is still fingerprinting it or running its suite, and on 28 November 2026 that gave "line 34:
# <path>: No such file or directory" from the fingerprint's read of a vanished file (line 34 of the hook as it then
# was) and then a failure report with no test output in it. And, in a checkout that still exists, a run that did not
# crash (next paragraph) and in which pytest reported no result at all: no FAILED or ERROR line, no summary line ("1
# failed, 2 passed in ..."), and none of the reports pytest gives when it stops before running a test (a conftest that
# would not import, an internal error), as when Python could not start ("Fatal Python error: error evaluating path",
# exit status 1, which is what it gives in a deleted directory).
#
# A crash is reported by its exit status, whatever pytest printed, when the checkout still exists: python3 killed by a
# signal (bash's status 128 + the signal's number: 139 for a segfault, 137 for SIGKILL, which is what the kernel's
# out-of-memory killer sends; a status above 128 that names no signal is reported too, without one), or pytest's
# INTERNAL_ERROR (3) or USAGE_ERROR (4), the code it also gives when a conftest will not import (pytest's ExitCode enum,
# read in _pytest/config/__init__.py of the installed pytest 9.1.1 on 28 November 2026). The report names the status and
# the signal and gives what pytest printed: the 25 lines from the line where Python's "Fatal Python error" first
# appears, where faulthandler's dump names the crashing frame first, else the last 25 lines. That line does not start
# with it when a test ran before the crash, since pytest's progress dots have no newline yet ("...Fatal Python error:
# Segmentation fault", measured on 28 November 2026). Until this was added on 28 November 2026, such a run fell under
# the no-result rule above: a segfault or a kill woke nobody, and since no pass is recorded it ran again, as silently,
# at every later stop.
#
# CLAUDE_SUITE_HOOK_DRY_RUN=1 prints what the hook would do and runs nothing. tests/test_suite_hook.py uses it, and a
# stub python3 on PATH, to test the hook without running the real suite.
set -uo pipefail

hook_input="$(cat)"
working_directory="$(printf '%s' "$hook_input" | jq -r '.cwd // empty' 2>/dev/null)"
[ -n "$working_directory" ] || working_directory="${CLAUDE_PROJECT_DIR:-.}"
checkout_root="$(git -C "$working_directory" rev-parse --show-toplevel 2>/dev/null)" || exit 0
cd "$checkout_root" || exit 0
[ -d mechanistic_pathway_learning ] && [ -d tests ] || exit 0

# True while $checkout_root is still the top of a git checkout. Asked by absolute path, so it answers even after the
# directory this shell is in was deleted; a checkout whose .git is already gone resolves to an enclosing repository, or
# to none, and so does not count.
checkout_still_exists() {
    [ "$(git -C "$checkout_root" rev-parse --show-toplevel 2>/dev/null)" = "$checkout_root" ]
}

git_directory="$(git rev-parse --absolute-git-dir 2>/dev/null)" && [ -n "$git_directory" ] || exit 0
fingerprint_file="$git_directory/claude_suite_last_passing_fingerprint"
lock_file="$git_directory/claude_suite.lock"

# A file deleted between the -f test and the read leaves an empty hash for its path, and the redirect's complaint is
# discarded; when the whole checkout went, checkout_still_exists below stops the hook.
code_fingerprint() {
    git ls-files -z --cached --others --exclude-standard -- mechanistic_pathway_learning tests 2>/dev/null \
        | tr '\0' '\n' | grep '\.py$' | LC_ALL=C sort \
        | while IFS= read -r path; do
              [ -f "$path" ] && printf '%s  %s\n' "$(sha256sum 2>/dev/null < "$path" | cut -d' ' -f1)" "$path"
          done \
        | sha256sum | cut -d' ' -f1
}

fingerprint="$(code_fingerprint)"
checkout_still_exists || exit 0  # deleted while it was being fingerprinted
if [ -f "$fingerprint_file" ] && [ "$(cat "$fingerprint_file")" = "$fingerprint" ]; then
    exit 0  # no code changed since the last passing run in this checkout
fi

if [ "${CLAUDE_SUITE_HOOK_DRY_RUN:-0}" = "1" ]; then
    echo "would run the full suite in $checkout_root (code fingerprint $fingerprint, last passing $(cat "$fingerprint_file" 2>/dev/null || echo none))"
    exit 0
fi

{ exec 9>"$lock_file"; } 2>/dev/null || exit 0  # the git directory went with the checkout
flock -n 9 || exit 0  # a suite is already running in this checkout

output_file="$(mktemp)"
# The braces' 2>/dev/null silences bash's own notice of a child that a signal killed ("<this script>: line N: <pid>
# Segmentation fault ..."), which would otherwise go to the hook's stderr; the crash report below names the signal.
{ OMP_NUM_THREADS=1 PYTHONPATH=. nice -n 15 python3 -m pytest -q -p no:cacheprovider > "$output_file" 2>&1; } 2>/dev/null
pytest_exit_status=$?
if [ "$pytest_exit_status" -eq 0 ]; then
    { printf '%s\n' "$fingerprint" > "$fingerprint_file"; } 2>/dev/null
    rm -f "$output_file"
    exit 0
fi
if ! checkout_still_exists; then
    rm -f "$output_file"
    exit 0  # the checkout was deleted while its suite ran: nothing to report, whatever pytest's exit status
fi

# A crash, by its exit status: above 128 is bash's 128 + the number of the signal that killed python3, and 3 and 4 are
# pytest's ExitCode.INTERNAL_ERROR and ExitCode.USAGE_ERROR. A status above 128 that names no signal (Linux's signals
# run to 64, so 193 to 255, as sys.exit(-1) gives 255) is an abnormal end too, and is reported without a signal.
crash_cause=""
if [ "$pytest_exit_status" -gt 128 ]; then
    signal_number=$((pytest_exit_status - 128))
    # kill -l answers a signal's name, or an empty one for 32 and 33 (measured), and fails for a number above 64
    if signal_name="$(kill -l "$signal_number" 2>/dev/null)"; then
        crash_cause="python3 was killed by signal $signal_number${signal_name:+ (SIG$signal_name)}"
    else
        crash_cause="python3 ended with a status above 128 that names no signal"
    fi
elif [ "$pytest_exit_status" -eq 3 ]; then
    crash_cause="pytest stopped with its internal-error code (ExitCode.INTERNAL_ERROR)"
elif [ "$pytest_exit_status" -eq 4 ]; then
    crash_cause="pytest stopped with its usage-error code (ExitCode.USAGE_ERROR), as when a conftest will not import"
fi
if [ -n "$crash_cause" ]; then
    crash_output="$(grep -m1 -A24 'Fatal Python error' "$output_file")"  # unanchored: progress dots can precede it
    [ -n "$crash_output" ] || crash_output="$(tail -25 "$output_file")"
    {
        echo "The full test suite crashed in $checkout_root after the code changed (run by .claude/hooks/run-suite-if-code-changed.sh):"
        echo "exit status $pytest_exit_status, $crash_cause. What it printed:"
        printf '%s\n' "$crash_output"
    } >&2
    rm -f "$output_file"
    exit 2
fi

# INTERNALERROR and the conftest report normally come with status 3 and 4, reported above; they are kept here for a
# plugin that ends the run with a code of its own, which pytest's ExitCode allows.
if ! grep -qE '^(FAILED|ERROR|INTERNALERROR)|^ImportError while loading conftest|[0-9]+ (passed|failed|errors?)\b|no tests ran' "$output_file"; then
    rm -f "$output_file"
    exit 0  # pytest reported no result and did not crash: nothing to report
fi
report="$(grep -E "^(FAILED|ERROR)|passed|failed" "$output_file" | tail -25)"
[ -n "$report" ] || report="$(tail -25 "$output_file")"  # pytest stopped before running a test; show what it said
{
    echo "The full test suite failed in $checkout_root after the code changed (run by .claude/hooks/run-suite-if-code-changed.sh):"
    printf '%s\n' "$report"
} >&2
rm -f "$output_file"
exit 2
