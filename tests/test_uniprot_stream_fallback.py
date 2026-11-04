"""The UniProt stream fallback of experiments/fetch_node_descriptor_sources.py, with simulated responses.

On 4 November 2026 UniProt's stream endpoint answered "503 Streaming temporarily unavailable" for minutes at a time and
stopped the rebuild. A 503 is now retried at the interval UniProt names, and if the stream stays unavailable the same
query is read through the paged search and its rows are checked against X-Total-Results.
"""
import gzip
import io
import json
import urllib.error

import pytest

import experiments.fetch_node_descriptor_sources as fetcher

STREAM_URL = (fetcher.UNIPROT_STREAM_PREFIX + "query=(organism_id:9606)%20AND%20(reviewed:true)"
              "&fields=accession,gene_primary&format=tsv&compressed=true")


class FakeResponse(io.BytesIO):
    def __init__(self, body: bytes, headers: dict):
        super().__init__(body)
        self.headers = headers


def unavailable(url):
    return urllib.error.HTTPError(url, 503, "Streaming temporarily unavailable", {"Retry-After": "5"}, None)


def serve(monkeypatch, answers):
    """Replace urlopen with a function that answers each call from the list, in order, and records the URLs asked."""
    asked = []

    def fake_urlopen(request, timeout=None):
        asked.append(request.full_url)
        answer = answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer

    monkeypatch.setattr(fetcher.urllib.request, "urlopen", fake_urlopen)
    monkeypatch.setattr(fetcher.time, "sleep", lambda seconds: None)
    return asked


def test_a_stream_that_stays_unavailable_is_read_through_the_paged_search(monkeypatch, tmp_path):
    page_two_url = fetcher.UNIPROT_SEARCH_PREFIX + "cursor=abc&size=500"
    asked = serve(monkeypatch, [unavailable(STREAM_URL)] * fetcher.UNAVAILABLE_ATTEMPTS + [
        FakeResponse(b"Entry\tGene Names (primary)\nP04637\tTP53\nQ00987\tMDM2\n",
                     {"X-Total-Results": "3", "X-UniProt-Release": "2026_04", "Link": f'<{page_two_url}>; rel="next"'}),
        FakeResponse(b"Entry\tGene Names (primary)\nP38398\tBRCA1\n", {"X-Total-Results": "3"}),
    ])
    pin = fetcher.download_and_pin(tmp_path, "uniprot", "proteome.tsv.gz", STREAM_URL, refresh=False)

    with gzip.open(tmp_path / "uniprot" / "proteome.tsv.gz", "rt") as handle:
        assert handle.read() == "Entry\tGene Names (primary)\nP04637\tTP53\nQ00987\tMDM2\nP38398\tBRCA1\n"
    assert pin["retrieved_by"].startswith("paged search") and pin["rows"] == 3 and pin["pages"] == 2
    assert pin["url"] == STREAM_URL and pin["x_uniprot_release"] == "2026_04"
    assert asked[fetcher.UNAVAILABLE_ATTEMPTS].startswith(fetcher.UNIPROT_SEARCH_PREFIX)
    assert "compressed" not in asked[fetcher.UNAVAILABLE_ATTEMPTS] and "size=500" in asked[fetcher.UNAVAILABLE_ATTEMPTS]
    assert asked[-1] == page_two_url
    assert json.loads((tmp_path / "uniprot" / "proteome.tsv.gz.pin.json").read_text())["rows"] == 3


def test_a_short_paged_read_is_an_error_and_writes_no_file(monkeypatch, tmp_path):
    serve(monkeypatch, [unavailable(STREAM_URL)] * fetcher.UNAVAILABLE_ATTEMPTS + [
        FakeResponse(b"Entry\tGene Names (primary)\nP04637\tTP53\n", {"X-Total-Results": "2"}),
    ])
    with pytest.raises(RuntimeError, match="X-Total-Results"):
        fetcher.download_and_pin(tmp_path, "uniprot", "proteome.tsv.gz", STREAM_URL, refresh=False)
    assert not (tmp_path / "uniprot" / "proteome.tsv.gz").exists()
    assert not (tmp_path / "uniprot" / "proteome.tsv.gz.pin.json").exists()


def test_a_stream_that_recovers_is_used_and_recorded_as_the_stream(monkeypatch, tmp_path):
    body = gzip.compress(b"Entry\tGene Names (primary)\nP04637\tTP53\n")
    serve(monkeypatch, [unavailable(STREAM_URL), FakeResponse(body, {"X-UniProt-Release": "2026_04"})])
    pin = fetcher.download_and_pin(tmp_path, "uniprot", "proteome.tsv.gz", STREAM_URL, refresh=False)
    assert pin["retrieved_by"] == "stream"
    assert (tmp_path / "uniprot" / "proteome.tsv.gz").read_bytes() == body


def test_an_error_other_than_unavailable_is_raised_at_once(monkeypatch, tmp_path):
    asked = serve(monkeypatch, [urllib.error.HTTPError(STREAM_URL, 400, "Bad Request", {}, None)])
    with pytest.raises(urllib.error.HTTPError):
        fetcher.download_and_pin(tmp_path, "uniprot", "proteome.tsv.gz", STREAM_URL, refresh=False)
    assert len(asked) == 1
