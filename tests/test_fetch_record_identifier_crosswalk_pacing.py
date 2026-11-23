"""The Europe PMC pace of experiments/fetch_record_identifier_crosswalk.py: one request a second, with backoff on a
throttling answer (the owner, 23 November 2026: "1 a second with backoff"; amendment item 38)."""
from __future__ import annotations

import email.message
import sys
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import fetch_record_identifier_crosswalk as crosswalk  # noqa: E402


def http_error(code: int, retry_after: str | None = None) -> urllib.error.HTTPError:
    headers = email.message.Message()
    if retry_after is not None:
        headers["Retry-After"] = retry_after
    return urllib.error.HTTPError("https://www.ebi.ac.uk/europepmc/webservices/rest/search", code, "refused", headers, None)


def test_the_europe_pmc_pace_is_one_request_a_second_with_the_crawl_delay_as_its_ceiling():
    assert crosswalk.EUROPEPMC_PAUSE_SECONDS == 1.0
    assert crosswalk.MAXIMUM_EUROPEPMC_PAUSE_SECONDS == 10.0


def test_a_throttling_answer_waits_as_long_as_its_retry_after_says():
    assert crosswalk.retry_delay_seconds(http_error(429, "37"), attempt=0) == 37.0


def test_a_throttling_answer_without_retry_after_waits_a_doubling_delay():
    delays = [crosswalk.retry_delay_seconds(http_error(503), attempt) for attempt in range(3)]
    assert delays == [10.0, 20.0, 40.0]


def test_any_other_failure_keeps_the_widening_delay():
    assert [crosswalk.retry_delay_seconds(TimeoutError(), attempt) for attempt in range(3)] == [10.0, 20.0, 30.0]


def test_the_pace_doubles_after_throttling_and_stops_at_the_ceiling():
    pause = crosswalk.EUROPEPMC_PAUSE_SECONDS
    paces = []
    for _ in range(6):
        pause = crosswalk.slowed_pause(pause)
        paces.append(pause)
    assert paces == [2.0, 4.0, 8.0, 10.0, 10.0, 10.0]


def test_with_retries_reports_throttling_so_the_caller_can_slow_down(monkeypatch):
    monkeypatch.setattr(crosswalk.time, "sleep", lambda seconds: None)
    answers = iter([http_error(429), {"1": {"doi": "", "pmc": ""}}])

    def fetch(batch):
        answer = next(answers)
        if isinstance(answer, Exception):
            raise answer
        return answer

    throttled = []
    assert crosswalk.with_retries(fetch, ["1"], "test", on_throttled=lambda: throttled.append(True)) == {"1": {"doi": "", "pmc": ""}}
    assert throttled == [True]
