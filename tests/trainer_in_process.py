"""Run experiments/run_main_model.py for a test, in the test's own process by default.

Why (26 October 2026): a toy trainer run spends about 1 s training and about 5 s starting a fresh interpreter and
importing torch, scikit-learn and scipy. The end-to-end trainer tests start 21 such runs, so most of their time was
imports. Calling main() in-process imports once per test session.

What a subprocess gave that this keeps:
- one torch thread, as OMP_NUM_THREADS=1 gave the subprocess (restored afterwards);
- the working directory at the repository root (restored afterwards);
- a fresh CHECKPOINT_REQUESTED and the previous SIGUSR1 handler (main() installs its own);
- the exit status, stdout and stderr, returned in the shape of subprocess.CompletedProcess.

main() seeds torch from --seed on every call, so two runs with equal arguments give equal predictions, as before.
Set TRAINER_TESTS_IN_SUBPROCESS=1 to run every call in a fresh interpreter instead, to check that the in-process
results match the isolated ones.
"""
from __future__ import annotations

import contextlib
import io
import os
import signal
import subprocess
import sys
import traceback
from pathlib import Path

import torch

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SUBPROCESS_ENVIRONMENT = {"PYTHONPATH": ".", "PATH": "/usr/bin:/bin:/usr/local/bin", "OMP_NUM_THREADS": "1"}


def run_main_model(arguments: list[str]) -> subprocess.CompletedProcess:
    """Run the trainer with these command-line arguments (without the script name) and return its exit status and output."""
    if os.environ.get("TRAINER_TESTS_IN_SUBPROCESS") == "1":
        command = [sys.executable, "experiments/run_main_model.py", *arguments]
        return subprocess.run(command, cwd=REPOSITORY_ROOT, capture_output=True, text=True, env=SUBPROCESS_ENVIRONMENT)
    import experiments.run_main_model as trainer_module

    captured_stdout, captured_stderr = io.StringIO(), io.StringIO()
    previous_argv, previous_directory = sys.argv, os.getcwd()
    previous_thread_count = torch.get_num_threads()
    previous_signal_handler = signal.getsignal(signal.SIGUSR1)
    return_code = 0
    try:
        sys.argv = ["experiments/run_main_model.py", *arguments]
        os.chdir(REPOSITORY_ROOT)
        torch.set_num_threads(1)
        trainer_module.CHECKPOINT_REQUESTED = False
        with contextlib.redirect_stdout(captured_stdout), contextlib.redirect_stderr(captured_stderr):
            try:
                trainer_module.main()
            except SystemExit as exit_request:  # argparse errors and explicit exits
                return_code = exit_request.code if isinstance(exit_request.code, int) else (0 if exit_request.code is None else 1)
                if not isinstance(exit_request.code, (int, type(None))):
                    print(exit_request.code, file=sys.stderr)
            except Exception:  # a crash in the subprocess was a nonzero exit with the traceback on stderr
                return_code = 1
                traceback.print_exc()
    finally:
        sys.argv = previous_argv
        os.chdir(previous_directory)
        torch.set_num_threads(previous_thread_count)
        signal.signal(signal.SIGUSR1, previous_signal_handler)
    return subprocess.CompletedProcess(sys.argv, return_code, captured_stdout.getvalue(), captured_stderr.getvalue())
