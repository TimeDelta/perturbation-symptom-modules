""".claude/hooks/run-suite-if-code-changed.sh, the Stop and SubagentStop hook that runs the full suite once when the
code changed, tested without running the real suite (added 28 November 2026).

Each test makes a throwaway git checkout holding mechanistic_pathway_learning/ and tests/, and runs the hook on it
with a stub `python3` first on PATH, so "the suite" is a shell script that prints what the case needs and exits as
pytest would. The cases that matter are the ones of 28 November 2026, when a workflow deleted an agent's worktree
while the hook ran and the hook woke the session with "The full test suite failed" and no test output: a checkout
that is gone, or a run that reported no result, is nothing to report (exit 0), while a failing suite and a conftest
that would not import still wake the session (exit 2).
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
    """pytest stops before running a test and prints no summary line (exit 4); that is a broken suite, not a missing
    one, so it is reported with the end of what pytest said."""
    checkout = make_checkout(tmp_path)
    stub_directory = stub_suite(tmp_path, "echo \"ImportError while loading conftest '$PWD/tests/conftest.py'.\"\n"
                                          'echo "E   ModuleNotFoundError: No module named \'missing\'"\nexit 4\n')
    result = run_hook(checkout, stub_directory)
    assert result.returncode == 2, result
    assert "ImportError while loading conftest" in result.stderr and "ModuleNotFoundError" in result.stderr


def test_a_passing_suite_records_its_fingerprint_and_is_not_rerun_on_the_same_code(tmp_path):
    checkout = make_checkout(tmp_path)
    stub_directory = stub_suite(tmp_path, 'echo "1 passed in 0.01s"\nexit 0\n')
    assert run_hook(checkout, stub_directory).returncode == 0
    assert (checkout / ".git" / "claude_suite_last_passing_fingerprint").exists()
    assert run_hook(checkout, dry_run=True).stdout == "", "the code is unchanged since the passing run"
    (checkout / "tests" / "test_example.py").write_text("def test_example():\n    assert True\n")
    assert "would run the full suite" in run_hook(checkout, dry_run=True).stdout
