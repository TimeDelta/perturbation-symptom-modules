"""The limits of the shell fallback for public pages (experiments/read_public_page.py), checked without the network."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "experiments" / "read_public_page.py"
module_specification = importlib.util.spec_from_file_location("read_public_page", MODULE_PATH)
read_public_page = importlib.util.module_from_spec(module_specification)
module_specification.loader.exec_module(read_public_page)

ROBOTS_FILE_THAT_TURNS_ASSISTANTS_AWAY = """
User-agent: *
Disallow: /private/

User-agent: ClaudeBot
Disallow: /
"""

ROBOTS_FILE_WITH_ONE_CLOSED_FOLDER = """
User-agent: *
Disallow: /private/
"""


def test_an_address_with_an_email_address_is_not_requested():
    assert read_public_page.reason_address_is_not_requested("https://api.example.org/v2/10.1/x?email=someone%40example.org") is not None
    assert read_public_page.reason_address_is_not_requested("https://api.example.org/v2/10.1/x?email=someone@example.org") is not None


def test_only_public_https_addresses_without_credentials_are_requested():
    assert read_public_page.reason_address_is_not_requested("http://example.org/page") is not None
    assert read_public_page.reason_address_is_not_requested("https://localhost/page") is not None
    assert read_public_page.reason_address_is_not_requested("https://user:secret@example.org/page") is not None
    assert read_public_page.reason_address_is_not_requested("https://example.org/page?id=7") is None


def test_a_rule_against_the_assistant_crawler_closes_the_whole_site():
    assert not read_public_page.robots_file_allows(ROBOTS_FILE_THAT_TURNS_ASSISTANTS_AWAY, "https://example.org/open/page")


def test_a_rule_for_every_reader_closes_only_what_it_names():
    assert read_public_page.robots_file_allows(ROBOTS_FILE_WITH_ONE_CLOSED_FOLDER, "https://example.org/open/page")
    assert not read_public_page.robots_file_allows(ROBOTS_FILE_WITH_ONE_CLOSED_FOLDER, "https://example.org/private/page")


def test_an_empty_robots_file_allows_every_address():
    assert read_public_page.robots_file_allows("", "https://example.org/any/page")


def test_a_web_page_served_in_place_of_the_robots_file_is_not_a_robots_file():
    assert not read_public_page.looks_like_robots_file("<!DOCTYPE html><html><head><title>Verify</title></head></html>")
    assert read_public_page.looks_like_robots_file("User-agent: *\nDisallow:\n")


def test_a_human_check_is_recognised_and_an_ordinary_page_is_not():
    assert read_public_page.looks_like_challenge(403, "Forbidden")
    assert read_public_page.looks_like_challenge(200, "<html><body>To continue, we need to verify you are a human.</body></html>")
    # a proof-of-work gate answers with status 200 and a short page of its own
    assert read_public_page.looks_like_challenge(200, "<html><head><title>Making sure you're not a bot!</title></head><body><script src='/.within.website/x/cmd/anubis/static/js/main.mjs'></script></body></html>")
    assert read_public_page.looks_like_challenge(200, "<html><body>Checking your browser before accessing the site.</body></html>")
    long_article_that_mentions_a_captcha = "<html><body>" + "A study of captcha design. " * 2000 + "</body></html>"
    assert not read_public_page.looks_like_challenge(200, long_article_that_mentions_a_captcha)
    assert not read_public_page.looks_like_challenge(200, "<html><body>Release 24.0, 16 March 2026.</body></html>")


def test_a_refused_address_makes_no_request(tmp_path):
    reader = read_public_page.PublicPageReader(tmp_path)
    record = reader.read("http://example.org/page")
    assert record["read"] is False and "https" in record["reason"]
    assert not any(tmp_path.iterdir())


ROBOTS_FILE_THAT_CLOSES_EVERYTHING = "User-agent: *\nDisallow: /\n"  # what ftp.ebi.ac.uk serves (read 22 October 2026)


def reader_answered_by(tmp_path, monkeypatch, robots_file_text: str) -> tuple:
    """A reader whose requests are answered locally: the robots file given and a short page for anything else."""
    requested = []

    def answer(address):
        requested.append(address)
        if address.endswith("/robots.txt"):
            return 200, "text/plain", robots_file_text.encode()
        return 200, "text/plain", b"IntAct release notes"

    monkeypatch.setattr(read_public_page, "request_bytes", answer)
    monkeypatch.setattr(read_public_page, "SECONDS_BETWEEN_REQUESTS_TO_ONE_HOST", 0.0)
    return read_public_page.PublicPageReader(tmp_path), requested


def test_ebi_ftp_host_is_read_past_its_robots_rule_on_the_owners_ruling(tmp_path, monkeypatch):
    """The owner, 22 October 2026: "don't refuse FTP from EBI". The robots file is still read and its answer recorded."""
    reader, requested = reader_answered_by(tmp_path, monkeypatch, ROBOTS_FILE_THAT_CLOSES_EVERYTHING)
    record = reader.read("https://ftp.ebi.ac.uk/pub/databases/intact/current/psimitab/README")
    assert record["read"] is True, record
    assert "don't refuse FTP from EBI" in record["robots_file"] and "disallows" in record["robots_file"]
    assert requested == ["https://ftp.ebi.ac.uk/robots.txt", "https://ftp.ebi.ac.uk/pub/databases/intact/current/psimitab/README"]


def test_dblp_is_read_past_its_robots_rule_on_the_owners_ruling(tmp_path, monkeypatch):
    """The owner, 27 October 2026, asked whether to extend the exception to dblp.org: "Yes".

    It was the one route that would have settled whether two entries of docs/references.bib claiming ICLR are
    peer-reviewed conference papers, in the bibliography sweep of decision 9.101.
    """
    reader, requested = reader_answered_by(tmp_path, monkeypatch, ROBOTS_FILE_THAT_CLOSES_EVERYTHING)
    record = reader.read("https://dblp.org/search/publ/api?q=decoupled+weight+decay+regularization")
    assert record["read"] is True, record
    assert "27 October 2026" in record["robots_file"] and "disallows" in record["robots_file"]


@pytest.mark.parametrize("address", [
    "https://www.ebi.ac.uk/gene2phenotype/api/panel/all/download",  # another EBI host keeps its own robots rules
    "https://ftp.ebi.ac.uk.example.org/pub/file.txt",  # a host that only begins with the exempt name
    "https://ftp.example.org/pub/file.txt",
    "https://www.dblp.org/search/publ/api?q=anything",  # another dblp host keeps its own robots rules
    "https://dblp.org.example.org/search/publ/api?q=anything",
])
def test_the_exemption_is_the_one_host_and_every_other_robots_rule_still_refuses(tmp_path, monkeypatch, address):
    reader, requested = reader_answered_by(tmp_path, monkeypatch, ROBOTS_FILE_THAT_CLOSES_EVERYTHING)
    record = reader.read(address)
    assert record["read"] is False and "robots file disallows" in record["reason"], record
    assert len(requested) == 1 and requested[0].endswith("/robots.txt")


def test_the_other_limits_still_hold_on_the_exempt_host(tmp_path, monkeypatch):
    reader, requested = reader_answered_by(tmp_path, monkeypatch, ROBOTS_FILE_THAT_CLOSES_EVERYTHING)
    assert reader.read("http://ftp.ebi.ac.uk/pub/file.txt")["read"] is False  # only https
    assert reader.read("https://ftp.ebi.ac.uk/pub/file.txt?mail=someone%40example.org")["read"] is False  # no e-mail address
    assert requested == []


def test_text_of_page_drops_scripts_and_tags():
    page_source = "<html><head><style>p {color: red}</style><script>var a = 1;</script></head><body><p>Dose &amp; effect</p></body></html>"
    assert read_public_page.text_of_page(page_source) == "Dose & effect"


def test_a_proof_of_work_gate_whose_challenge_is_only_in_its_script_is_a_refusal():
    """PubMed Central's scanned-PDF gate answers 200 with a short interstitial whose only challenge markers are in its
    script, so the prose markers missed it and a research pass of 12 October 2026 saved it as if it were the document."""
    interstitial = ('<!DOCTYPE html><html><head><title>Preparing to download</title></head><body>'
                    '<p>Preparing to download ...</p><script>var POW_CHALLENGE="ab12"; var POW_DIFFICULTY=4;'
                    'window.ncbi.pmc.pow.init(POW_CHALLENGE, POW_DIFFICULTY);</script></body></html>')
    assert read_public_page.looks_like_challenge(200, interstitial)
    assert not read_public_page.looks_like_challenge(200, "<!DOCTYPE html><html><body><p>" + "the article itself. " * 2000 + "</p></body></html>")


def test_a_gate_titled_client_challenge_is_a_refusal():
    """nature.com answered 200 with a 3,038-byte page titled "Client Challenge" whose assets sit under a /_fs-ch- path,
    and a research pass of 22 October 2026 saved it as read because none of the earlier markers matched."""
    gate = ('<!DOCTYPE html><html lang="en"><head><title>Client Challenge</title>'
            '<link href="/_fs-ch-1T1wmsGaOgGaSxcX/assets/styles.css" rel="stylesheet" /></head>'
            '<body><noscript>JavaScript is disabled in your browser.</noscript></body></html>')
    assert read_public_page.looks_like_challenge(200, gate)
    assert read_public_page.looks_like_challenge(200, gate.replace("Client Challenge", "Loading"))
    assert not read_public_page.looks_like_challenge(200, "<html><body><h1>A client's challenge to the model</h1><p>"
                                                     + "text " * 5000 + "</p></body></html>")


def test_a_page_carrying_only_cloudflares_passive_telemetry_script_is_read():
    """WormBase's release directory listing (200, 5,173 bytes) was refused on 24 October 2026 because Cloudflare had
    injected its bot-telemetry script, whose path holds "challenge-platform", into the full page (decision 9.95)."""
    listing = ('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><html><head>'
               '<title>Index of /releases/current-production-release/ONTOLOGY</title></head><body>'
               '<h1>Index of /releases/current-production-release/ONTOLOGY</h1><table><tr><td>'
               '<a href="phenotype_association.WS298.wb.gz">phenotype_association.WS298.wb.gz</a></td></tr></table>'
               "<script>(function(){function c(){var b=a.contentDocument||a.contentWindow.document;"
               "var d=b.createElement('script');d.src='/cdn-cgi/challenge-platform/scripts/jsd/main.js';"
               "b.getElementsByTagName('head')[0].appendChild(d);}})();</script></body></html>")
    assert not read_public_page.looks_like_challenge(200, listing)


def test_a_real_cloudflare_challenge_is_still_a_refusal():
    interstitial = ('<!DOCTYPE html><html><head><title>Just a moment...</title></head><body>'
                    '<div id="challenge-body"></div><script>window._cf_chl_opt={cvId: "3"};</script>'
                    '<script src="/cdn-cgi/challenge-platform/h/b/orchestrate/chl_page/v1"></script></body></html>')
    assert read_public_page.looks_like_challenge(200, interstitial)
    passive_and_real = interstitial.replace("</body>", "<script>d.src='/cdn-cgi/challenge-platform/scripts/jsd/main.js';</script></body>")
    assert read_public_page.looks_like_challenge(200, passive_and_real)
