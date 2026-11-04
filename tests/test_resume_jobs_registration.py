"""scripts/resume_jobs.sh registers only a command it can later find running.

The harness finds a running job by matching its exact command line (pgrep -f -x). A command with a shell operator, a
redirect or a quote runs as "bash -c ..." or loses its quotes, so it never matches, and every check-in would start
another copy beside the one running. On 4 November 2026 the graphs stage of the rebuild was registered that way and the
first check-in would have started a second build into the same directories; --register now refuses such a command.

Each case is safe even if the guard regressed: the done marker exists before registering, so the harness would report
the job done rather than launch it, and any job file written is removed.
"""
import subprocess
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
JOB_NAME = "test_registration_guard_should_not_exist"


@pytest.mark.parametrize("command", [
    "bash -c 'true && true'",
    "true && true",
    "true || true",
    "true; true",
    "true | cat",
    "true > /dev/null",
    "true < /dev/null",
    "echo $(true)",
    "echo `true`",
    "echo 'quoted'",
    'echo "quoted"',
])
def test_a_command_the_harness_could_not_find_running_is_refused(command, tmp_path):
    done_marker = tmp_path / "done"
    done_marker.touch()
    job_file = REPOSITORY_ROOT / "runs" / "jobs" / f"{JOB_NAME}.job"
    try:
        result = subprocess.run(["bash", "scripts/resume_jobs.sh", "--register", JOB_NAME, command, str(done_marker)],
                                cwd=REPOSITORY_ROOT, capture_output=True, text=True, timeout=60)
        assert result.returncode == 2, result.stdout + result.stderr
        assert "refusing job" in result.stderr
        assert not job_file.exists()
    finally:
        job_file.unlink(missing_ok=True)
