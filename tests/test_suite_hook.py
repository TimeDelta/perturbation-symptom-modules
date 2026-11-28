""".claude/hooks/run-suite-if-code-changed.sh, the Stop and SubagentStop hook that runs the full suite once when the
code changed, tested without running the real suite (added 28 November 2026).

Each test makes a throwaway git checkout holding mechanistic_pathway_learning/ and tests/, and runs the hook on it
with a stub `python3` first on PATH, so "the suite" is a shell script that prints what the case needs and exits as
pytest would. The cases that matter are the ones of 28 November 2026, when a workflow deleted an agent's worktree
while the hook ran and the hook woke the session with "The full test suite failed" and no test output: a checkout
that is gone, or a run that reported no result and did not crash, is nothing to report (exit 0), while a failing
suite, a conftest that would not import, and a crash (python3 killed by a signal, or pytest's internal-error code 3)
still wake the session (exit 2). The crash cases were added later on 28 November 2026, after the no-result rule had
been found to keep a segfault or a kill in a checkout that still exists as quiet as a deleted checkout.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
HOOK = REPOSITORY_ROOT / ".claude" / "hooks" / "run-suite-if-code-changed.sh"

pytestmark = pytest.mark.skipif(
    not HOOK.exists() or any(shutil.which(tool) is None for tool in ("bash", "git", "jq", "flock", "sha256sum")),
    reason="the hook, or a tool it calls (bash, git, jq, flock, sha256sum), is not in this checkout or on PATH")


def make_checkout(root: Path) -> Path:
    """A git checkout with one untracked .py file in each of the two directories the hook fingerprints."""
    checkout = root / "checkout"
    (checkout / "mechanistic_pathway_learning").mkdir(parents=True)
    (checkout / "tests").mkdir()
    (checkout / "mechanistic_pathway_learning" / "__init__.py").write_text("")
    (checkout / "tests" / "test_example.py").write_text("def test_example():\n    pass\n")
    subprocess.run(["git", "init", "-q", str(checkout)], check=True)
    return checkout.resolve()


def stub_suite(root: Path, body: str) -> Path:
    """A directory holding a `python3` that runs `body` (a POSIX shell script) in place of the suite."""
    stub_directory = root / "stub"
    stub_directory.mkdir()
    stub = stub_directory / "python3"
    stub.write_text("#!/bin/sh\n" + body)
    stub.chmod(0o755)
    return stub_directory


def run_hook(cwd: Path, stub_directory: Path | None = None, dry_run: bool = False, extra_env: dict | None = None,
             process_cwd: Path | None = None) -> subprocess.CompletedProcess:
    environment = {key: value for key, value in os.environ.items()
                   if key not in ("CLAUDE_PROJECT_DIR", "CLAUDE_SUITE_HOOK_DRY_RUN")}
    environment["CLAUDE_SUITE_HOOK_DRY_RUN"] = "1" if dry_run else "0"
    if stub_directory is not None:
        environment["PATH"] = f"{stub_directory}{os.pathsep}{environment.get('PATH', '')}"
    environment.update(extra_env or {})
    return subprocess.run(["bash", str(HOOK)], input=json.dumps({"cwd": str(cwd)}), capture_output=True, text=True,
                          env=environment, cwd=process_cwd or REPOSITORY_ROOT, timeout=60)


def test_a_checkout_that_no_longer_exists_is_nothing_to_report(tmp_path):
    """The hook started from inside a directory that was then deleted, naming it as the checkout, as when a workflow
    removes the worktree of the agent that just finished. The dry run makes a regression visible (it would print what
    it was about to run) without running anything."""
    checkout = make_checkout(tmp_path)
    hook_input = tmp_path / "input.json"
    hook_input.write_text(json.dumps({"cwd": str(checkout)}))
    shutil.rmtree(checkout)
    environment = {key: value for key, value in os.environ.items() if key != "CLAUDE_PROJECT_DIR"}
    environment["CLAUDE_SUITE_HOOK_DRY_RUN"] = "1"
    result = subprocess.run(  # bash enters the directory, deletes it, and runs the hook from inside it
        ["bash", "-c", 'mkdir "$1" && cd "$1" && rmdir "$1" && exec bash "$2" < "$3"', "_", str(checkout), str(HOOK),
         str(hook_input)], capture_output=True, text=True, timeout=60, cwd=tmp_path, env=environment)
    assert result.returncode == 0 and result.stdout == "", result
    # bash itself says "shell-init: error retrieving current directory" when it starts in a deleted directory, before
    # the hook's first line runs; the hook adds nothing to that
    assert all(line.startswith("shell-init:") for line in result.stderr.splitlines()), result


def test_a_checkout_deleted_while_it_is_fingerprinted_is_nothing_to_report(tmp_path):
    """A stub sha256sum deletes the checkout at its first call, before the rest of its files are read. The dry run
    would print "would run the full suite" had the hook gone on."""
    checkout = make_checkout(tmp_path)
    stub_directory = tmp_path / "stub"
    stub_directory.mkdir()
    stub = stub_directory / "sha256sum"
    stub.write_text(f'#!/bin/sh\nrm -rf "$CHECKOUT_TO_REMOVE"\nexec {shutil.which("sha256sum")} "$@"\n')
    stub.chmod(0o755)
    result = run_hook(checkout, stub_directory, dry_run=True, extra_env={"CHECKOUT_TO_REMOVE": str(checkout)})
    assert not checkout.exists(), "the stub sha256sum was not called"
    assert result.returncode == 0 and result.stdout == "" and result.stderr == "", result


def test_a_checkout_deleted_while_its_suite_runs_wakes_nobody(tmp_path):
    """The stub deletes the checkout and exits 1 with the message Python gives when its directory has gone, which is
    what a real run there prints instead of a test result."""
    checkout = make_checkout(tmp_path)
    stub_directory = stub_suite(tmp_path, 'rm -rf "$CHECKOUT_TO_REMOVE"\necho "Fatal Python error: error evaluating path" >&2\nexit 1\n')
    result = run_hook(checkout, stub_directory, extra_env={"CHECKOUT_TO_REMOVE": str(checkout)})
    assert not checkout.exists(), "the stub suite was not run"
    # the stub's own shell complains that its directory has gone ("getcwd() failed"); the hook reports nothing
    assert result.returncode == 0 and "The full test suite failed" not in result.stderr, result


def test_a_checkout_deleted_after_its_suite_reported_failures_wakes_nobody(tmp_path):
    """A worktree removed late in a run leaves pytest reporting the tests whose files went as failures, with a summary
    line, so the output alone looks like a failing suite; only the check that the checkout still exists, made after
    the run, keeps this from waking the session. The case above cannot tell that check from the no-result one, since
    its stub prints no result (added 28 November 2026, when removing that check left every other case passing)."""
    checkout = make_checkout(tmp_path)
    stub_directory = stub_suite(tmp_path, 'echo "FAILED tests/test_example.py::test_example - FileNotFoundError"\n'
                                          'echo "1 failed in 0.10s"\nrm -rf "$CHECKOUT_TO_REMOVE"\nexit 1\n')
    result = run_hook(checkout, stub_directory, extra_env={"CHECKOUT_TO_REMOVE": str(checkout)})
    assert not checkout.exists(), "the stub suite was not run"
    assert result.returncode == 0 and "The full test suite failed" not in result.stderr, result


def test_a_run_that_reported_no_result_wakes_nobody_and_records_no_pass(tmp_path):
    checkout = make_checkout(tmp_path)
    stub_directory = stub_suite(tmp_path, 'echo "Fatal Python error: error evaluating path" >&2\nexit 1\n')
    result = run_hook(checkout, stub_directory)
    assert result.returncode == 0 and result.stderr == "", result
    assert not (checkout / ".git" / "claude_suite_last_passing_fingerprint").exists(), \
        "a run that said nothing is not a pass, so the next run must test the code again"
    assert "would run the full suite" in run_hook(checkout, dry_run=True).stdout


def test_a_failing_suite_still_wakes_the_session_with_its_result(tmp_path):
    checkout = make_checkout(tmp_path)
    stub_directory = stub_suite(tmp_path, 'echo ".F"\necho "FAILED tests/test_example.py::test_example - assert 0"\n'
                                          'echo "1 failed, 1 passed in 0.10s"\nexit 1\n')
    result = run_hook(checkout, stub_directory)
    assert result.returncode == 2, result
    assert "The full test suite failed in" in result.stderr
    assert "FAILED tests/test_example.py::test_example - assert 0" in result.stderr
    assert "1 failed, 1 passed in 0.10s" in result.stderr


def test_a_conftest_that_will_not_import_still_wakes_the_session(tmp_path):
    """pytest stops before running a test and prints no summary line, with its usage-error code 4; that is a broken
    suite, not a missing one, so it is reported as a crash, with the exit status and the end of what pytest said."""
    checkout = make_checkout(tmp_path)
    stub_directory = stub_suite(tmp_path, "echo \"ImportError while loading conftest '$PWD/tests/conftest.py'.\"\n"
                                          'echo "E   ModuleNotFoundError: No module named \'missing\'"\nexit 4\n')
    result = run_hook(checkout, stub_directory)
    assert result.returncode == 2, result
    assert "ImportError while loading conftest" in result.stderr and "ModuleNotFoundError" in result.stderr
    assert "exit status 4" in result.stderr and "ExitCode.USAGE_ERROR" in result.stderr


BASH_NOTICE_OF_A_KILLED_CHILD = "run-suite-if-code-changed.sh: line"  # "<script>: line N: <pid> Segmentation fault ..."


def test_a_suite_that_segfaults_wakes_the_session_with_the_signal_and_the_crashing_frame(tmp_path):
    """The stub prints what faulthandler prints after a segfault (the crashing frame first, then more frames than the
    last 25 lines would leave room for) and kills itself with SIGSEGV, so bash sees status 139. Measured on 28 November
    2026 with a real test that read address 0 under pytest 9.1.1: status 139, that dump, and no summary line."""
    checkout = make_checkout(tmp_path)
    stub_directory = stub_suite(tmp_path, 'ulimit -c 0\n'
                                          'echo "Fatal Python error: Segmentation fault"\necho ""\n'
                                          'echo "Current thread 0x00007f (most recent call first):"\n'
                                          'echo "  File \\"tests/test_example.py\\", line 2 in test_example"\n'
                                          'frame=0\nwhile [ $frame -lt 30 ]; do\n'
                                          '    echo "  File \\"pluggy/_callers.py\\", line 121 in _multicall"\n'
                                          '    frame=$((frame + 1))\ndone\n'
                                          'kill -s SEGV $$\n')
    result = run_hook(checkout, stub_directory)
    assert result.returncode == 2, result
    assert "The full test suite crashed in" in result.stderr
    assert "exit status 139, python3 was killed by signal 11 (SIGSEGV)" in result.stderr
    assert 'File "tests/test_example.py", line 2 in test_example' in result.stderr, \
        "the report starts at faulthandler's first line, where the crashing frame is, not at the last 25 lines"
    assert BASH_NOTICE_OF_A_KILLED_CHILD not in result.stderr, "bash's own notice of the signal is silenced"
    assert not (checkout / ".git" / "claude_suite_last_passing_fingerprint").exists()


def test_a_suite_killed_with_sigkill_wakes_the_session_with_the_signal(tmp_path):
    """SIGKILL is what the kernel's out-of-memory killer sends; nothing can catch it, so pytest prints no last word
    and the report shows the end of its progress output."""
    checkout = make_checkout(tmp_path)
    stub_directory = stub_suite(tmp_path, 'echo "....................  [ 40%]"\nkill -s KILL $$\n')
    result = run_hook(checkout, stub_directory)
    assert result.returncode == 2, result
    assert "exit status 137, python3 was killed by signal 9 (SIGKILL)" in result.stderr
    assert "....................  [ 40%]" in result.stderr
    assert BASH_NOTICE_OF_A_KILLED_CHILD not in result.stderr, "bash's own notice of the signal is silenced"
    assert not (checkout / ".git" / "claude_suite_last_passing_fingerprint").exists()


def test_an_internal_error_exit_wakes_the_session_even_when_the_output_shows_no_result(tmp_path):
    """Exit status 3 is pytest's ExitCode.INTERNAL_ERROR. The stub's output holds none of the lines the no-result rule
    looks for (no INTERNALERROR line, no summary), so only the exit status makes this a report."""
    checkout = make_checkout(tmp_path)
    stub_directory = stub_suite(tmp_path, 'echo "Traceback (most recent call last):"\n'
                                          'echo "RuntimeError: a plugin failed outside any test"\nexit 3\n')
    result = run_hook(checkout, stub_directory)
    assert result.returncode == 2, result
    assert "exit status 3, pytest stopped with its internal-error code (ExitCode.INTERNAL_ERROR)" in result.stderr
    assert "RuntimeError: a plugin failed outside any test" in result.stderr
    assert not (checkout / ".git" / "claude_suite_last_passing_fingerprint").exists()


def test_a_suite_killed_in_a_checkout_that_was_deleted_wakes_nobody(tmp_path):
    """A crash is reported only while the checkout exists: the stub deletes it and then kills itself with SIGSEGV."""
    checkout = make_checkout(tmp_path)
    stub_directory = stub_suite(tmp_path, 'ulimit -c 0\nrm -rf "$CHECKOUT_TO_REMOVE"\nkill -s SEGV $$\n')
    result = run_hook(checkout, stub_directory, extra_env={"CHECKOUT_TO_REMOVE": str(checkout)})
    assert not checkout.exists(), "the stub suite was not run"
    assert result.returncode == 0 and "The full test suite" not in result.stderr, result
    assert BASH_NOTICE_OF_A_KILLED_CHILD not in result.stderr, "bash's own notice of the signal is silenced"


def test_a_passing_suite_records_its_fingerprint_and_is_not_rerun_on_the_same_code(tmp_path):
    checkout = make_checkout(tmp_path)
    stub_directory = stub_suite(tmp_path, 'echo "1 passed in 0.01s"\nexit 0\n')
    assert run_hook(checkout, stub_directory).returncode == 0
    assert (checkout / ".git" / "claude_suite_last_passing_fingerprint").exists()
    assert run_hook(checkout, dry_run=True).stdout == "", "the code is unchanged since the passing run"
    (checkout / "tests" / "test_example.py").write_text("def test_example():\n    assert True\n")
    assert "would run the full suite" in run_hook(checkout, dry_run=True).stdout
