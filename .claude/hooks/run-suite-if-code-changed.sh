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
# a hook that finds the lock held leaves the work to the run already going. Exit 2 (a failing suite) wakes the session
# that finished, through asyncRewake, with pytest's FAILED and ERROR lines and its summary line; every other outcome
# exits 0.
#
# Two outcomes are nothing to report, and exit 0 without waking anyone or recording a pass (so the next run tests the
# code again). A checkout that no longer exists: a workflow can delete an agent's worktree while the hook is still
# fingerprinting it or running its suite, and on 28 November 2026 that gave "line 34: <path>: No such file or
# directory" from the fingerprint and then a failure report with no test output in it. And a pytest run that reported
# no result at all: no FAILED or ERROR line, no summary line ("1 failed, 2 passed in ..."), and none of the reports
# pytest gives when it stops before running a test (a conftest that would not import, an internal error), as when
# Python could not start in a deleted directory or pytest was killed. A conftest that would not import still wakes the
# session, with the end of pytest's output, since that is a broken suite and not a missing one.
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
if OMP_NUM_THREADS=1 PYTHONPATH=. nice -n 15 python3 -m pytest -q -p no:cacheprovider > "$output_file" 2>&1; then
    { printf '%s\n' "$fingerprint" > "$fingerprint_file"; } 2>/dev/null
    rm -f "$output_file"
    exit 0
fi
if ! checkout_still_exists \
    || ! grep -qE '^(FAILED|ERROR|INTERNALERROR)|^ImportError while loading conftest|[0-9]+ (passed|failed|errors?)\b|no tests ran' "$output_file"; then
    rm -f "$output_file"
    exit 0  # the checkout was deleted while its suite ran, or pytest reported no result: nothing to report
fi
report="$(grep -E "^(FAILED|ERROR)|passed|failed" "$output_file" | tail -25)"
[ -n "$report" ] || report="$(tail -25 "$output_file")"  # pytest stopped before running a test; show what it said
{
    echo "The full test suite failed in $checkout_root after the code changed (run by .claude/hooks/run-suite-if-code-changed.sh):"
    printf '%s\n' "$report"
} >&2
rm -f "$output_file"
exit 2
