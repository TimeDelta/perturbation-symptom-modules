"""The limits of the shell fallback for public pages (experiments/read_public_page.py), checked without the network."""
from __future__ import annotations

import importlib.util
import urllib.error
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


def test_a_busy_or_unavailable_service_is_not_a_refusal():
    """429 and 503 say the service is busy or down, which is no statement about permission (the owner, 17 November
    2026: "429 and 503 status codes should not count as refusals"); 500 goes with them (item 37 rulings draft,
    section 13). A challenge marker in the body is still a refusal whatever the status."""
    assert not read_public_page.looks_like_challenge(429, "Too Many Requests")
    assert not read_public_page.looks_like_challenge(503, "Service Unavailable")
    assert not read_public_page.looks_like_challenge(500, "Internal Server Error")
    assert read_public_page.TRANSIENT_STATUS_CODES == frozenset({429, 500, 503})
    assert not read_public_page.TRANSIENT_STATUS_CODES & read_public_page.CHALLENGE_STATUS_CODES
    assert read_public_page.looks_like_challenge(503, "<html><body>Checking your browser before accessing the site.</body></html>")


@pytest.mark.parametrize("status_code", [429, 500, 503])
def test_a_transient_status_is_reported_for_a_retry_and_nothing_is_saved(tmp_path, monkeypatch, status_code):
    def answer(address):
        if address.endswith("/robots.txt"):
            return 200, "text/plain", b"User-agent: *\nDisallow: /private/\n"
        return status_code, "text/html", b"<html><body>Server error</body></html>"

    monkeypatch.setattr(read_public_page, "request_bytes", answer)
    monkeypatch.setattr(read_public_page, "SECONDS_BETWEEN_REQUESTS_TO_ONE_HOST", 0.0)
    record = read_public_page.PublicPageReader(tmp_path).read("https://example.org/page")
    assert record["read"] is False and record["transient"] is True
    assert "not a refusal" in record["reason"] and "same address on this same host" in record["reason"]
    assert not any(tmp_path.iterdir())


@pytest.mark.parametrize("error", [TimeoutError("timed out"),
                                   urllib.error.URLError(TimeoutError("timed out"))])
def test_a_timed_out_request_is_transient_and_another_failure_is_not(tmp_path, monkeypatch, error):
    """A timeout is transient as a 500 is (item 37 rulings draft, section 13); a refused connection is not."""
    def answer(address):
        if address.endswith("/robots.txt"):
            return 404, "text/plain", b""
        raise error

    monkeypatch.setattr(read_public_page, "request_bytes", answer)
    monkeypatch.setattr(read_public_page, "SECONDS_BETWEEN_REQUESTS_TO_ONE_HOST", 0.0)
    record = read_public_page.PublicPageReader(tmp_path).read("https://example.org/page")
    assert record["read"] is False and record.get("transient") is True and "timed out" in record["reason"]
    assert not read_public_page.is_timeout(ConnectionRefusedError("refused"))
    assert not read_public_page.is_timeout(urllib.error.URLError(ConnectionRefusedError("refused")))


@pytest.mark.parametrize("robots_status_code, expect_transient", [(503, True), (500, True), (429, True), (502, False)])
def test_a_robots_file_answered_with_a_server_error_or_429_leaves_the_page_unread(tmp_path, monkeypatch,
                                                                                   robots_status_code, expect_transient):
    """Until 28 November 2026 a robots file that answered 429 or a server error was cached as not served, so the page
    and every later page of the host were read as if the site had no robots file. Its rules are not known, so the page
    is not read, nothing is cached, and the record says to wait and retry when the status is one the owner ruled not a
    refusal (TRANSIENT_STATUS_CODES), as it does for a page."""
    requested = []

    def answer(address):
        requested.append(address)
        if address.endswith("/robots.txt"):
            return robots_status_code, "text/html", b"<html><body>Service Unavailable</body></html>"
        return 200, "text/html", b"<html><body>The article.</body></html>"

    monkeypatch.setattr(read_public_page, "request_bytes", answer)
    monkeypatch.setattr(read_public_page, "SECONDS_BETWEEN_REQUESTS_TO_ONE_HOST", 0.0)
    reader = read_public_page.PublicPageReader(tmp_path)
    record = reader.read("https://busy.example.org/page.html")
    assert record["read"] is False, record
    assert f"robots file answered HTTP {robots_status_code}" in record["reason"]
    assert record.get("transient", False) is expect_transient
    if expect_transient:
        assert "not a refusal" in record["reason"] and "same address on this same host" in record["reason"]
    assert reader.read("https://busy.example.org/other.html")["read"] is False
    assert requested == ["https://busy.example.org/robots.txt", "https://busy.example.org/robots.txt"]
    assert not any(tmp_path.iterdir())


def test_a_host_read_past_its_robots_file_is_read_when_its_robots_file_answers_a_server_error(tmp_path, monkeypatch):
    """A host read past its robots file on a ruling of the owner's is read whatever the rules say, so rules not known
    do not hold it back; the robots file's answer is still recorded beside the page."""
    def answer(address):
        if address.endswith("/robots.txt"):
            return 503, "text/html", b"<html><body>Service Unavailable</body></html>"
        return 200, "text/plain", b"IntAct release notes"

    monkeypatch.setattr(read_public_page, "request_bytes", answer)
    monkeypatch.setattr(read_public_page, "SECONDS_BETWEEN_REQUESTS_TO_ONE_HOST", 0.0)
    record = read_public_page.PublicPageReader(tmp_path).read("https://ftp.ebi.ac.uk/pub/databases/intact/current/psimitab/README")
    assert record["read"] is True, record
    assert "answered HTTP 503" in record["robots_file"] and "don't refuse FTP from EBI" in record["robots_file"]


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


PUBCHEM_PKA_LISTING = ("https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/annotations/heading/JSON"
                       "?heading=Dissociation+Constants&page=3")
PUBCHEM_PKA_RECORD = "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/5743/JSON?heading=Dissociation%20Constants"


def test_pubchem_pka_records_are_read_past_its_robots_rule_on_the_owners_ruling(tmp_path, monkeypatch):
    """The owner, 19 November 2026, extended the exception to PubChem's measured pKa records ("yes"), and accepted on
    20 November 2026 the scope of the "Dissociation Constants" heading of /rest/pug_view (item 37, ruling I1)."""
    for address in (PUBCHEM_PKA_LISTING, PUBCHEM_PKA_RECORD):
        reader, requested = reader_answered_by(tmp_path, monkeypatch, ROBOTS_FILE_THAT_CLOSES_EVERYTHING)
        record = reader.read(address)
        assert record["read"] is True, record
        assert "19 November 2026" in record["robots_file"] and "disallows" in record["robots_file"]
        assert requested == ["https://pubchem.ncbi.nlm.nih.gov/robots.txt", address]


@pytest.mark.parametrize("address", [
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/lithium/cids/JSON",  # the refused service itself
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/5743/JSON",  # a whole record, not the heading
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/5743/JSON?heading=Toxicity",  # another heading
    "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/5743/JSON?heading=Dissociation+Constants&heading=Toxicity",
    "https://pubchem.ncbi.nlm.nih.gov/compound/Lithium",  # the website
])
def test_pubchem_outside_its_pka_records_is_not_requested_at_all(tmp_path, monkeypatch, address):
    assert "measured pKa records only" in read_public_page.reason_address_is_not_requested(address)
    reader, requested = reader_answered_by(tmp_path, monkeypatch, ROBOTS_FILE_THAT_CLOSES_EVERYTHING)
    assert reader.read(address)["read"] is False
    assert requested == []


def test_pubchems_robots_file_is_still_requested():
    assert read_public_page.reason_address_is_not_requested("https://pubchem.ncbi.nlm.nih.gov/robots.txt") is None


def test_the_pubchem_scope_is_the_one_host():
    assert read_public_page.robots_rule_exemption(PUBCHEM_PKA_RECORD.replace("pubchem.ncbi.nlm.nih.gov", "pubchem.example.org")) is None
    assert read_public_page.robots_rule_exemption(PUBCHEM_PKA_RECORD.replace("pubchem.", "www.")) is None


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


def test_an_akamai_bm_verify_gate_is_a_refusal():
    """www.tga.gov.au answered 200 with an Akamai interstitial of about 2,300 bytes, an empty title and a form posting a
    bm-verify token to /_sec/verify, and a research pass of 8 November 2026 saved it as read."""
    gate = ('<!DOCTYPE html><html><head><title>&nbsp;</title></head><body>'
            '<form id="sec-if-cpt" method="POST" action="/_sec/verify?provider=interstitial">'
            '<input type="hidden" name="bm-verify" value=""/></form>'
            '<script>document.forms[0].submit();</script></body></html>')
    assert read_public_page.looks_like_challenge(200, gate)
    assert not read_public_page.looks_like_challenge(200, "<html><body><h1>Product information</h1><p>"
                                                     + "Verify the dose before use. " * 400 + "</p></body></html>")


def test_pubmeds_http_203_cookie_and_proof_of_work_gate_is_a_refusal():
    """pubmed.ncbi.nlm.nih.gov answered HTTP 203 with a 5,591-byte page whose only markers are "Cookies must be
    enabled" and the constants of a proof-of-work script, and the reader reported it as a plain "HTTP 203" (a research
    pass of 18 November 2026; item 37 rulings draft, section 13, "the reader's missed case")."""
    gate = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>pubmed.ncbi.nlm.nih.gov</title>'
            '<style>body { visibility: hidden; }</style></head><body>'
            '<div id="cookie-required" class="cookie-required-message" hidden><h1>Cookies must be enabled</h1>'
            '<p>Enable cookies for <span id="cookie-domain">pubmed.ncbi.nlm.nih.gov</span> and reload this page to '
            'continue.</p></div><script>const challengeId = "abc"; const challengeDomain = "pubmed.ncbi.nlm.nih.gov";'
            ' const bits = 18; const maxMs = 313000;</script></body></html>')
    assert read_public_page.looks_like_challenge(203, gate)
    assert read_public_page.looks_like_challenge(203, gate.replace("Cookies must be enabled", "Loading"))
    assert not read_public_page.looks_like_challenge(200, "<html><body><h1>Why cookies must be enabled</h1><p>"
                                                     + "A long help page about cookies. " * 800 + "</p></body></html>")


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


def test_a_challenge_page_padded_past_the_raw_size_limit_is_still_a_refusal():
    """Decision 9.102 (c): PubMed Central answered 200 with a 21,362-byte reCAPTCHA interstitial, "Checking your browser
    before accessing pmc.ncbi.nlm.nih.gov", and the raw-size test alone let it through as a page read. Its readable text
    is a sentence or two; the rest is script and markup."""
    padded_interstitial = ("<html><head><script>" + "var a=1;" * 3000 + "</script></head><body><p>Checking your browser "
                           "before accessing pmc.ncbi.nlm.nih.gov</p></body></html>")
    assert len(padded_interstitial) > read_public_page.CHALLENGE_SCAN_CHARACTERS
    # the marker must sit within the scanned head of the page, as it did on the page of 27 October 2026
    padded_interstitial = padded_interstitial.replace("<head>", "<head><title>Checking your browser</title>", 1)
    assert read_public_page.looks_like_challenge(200, padded_interstitial)
    long_article_that_mentions_a_captcha = "<html><body>" + "A study of captcha design. " * 2000 + "</body></html>"
    assert not read_public_page.looks_like_challenge(200, long_article_that_mentions_a_captcha)


def test_a_host_the_owner_ruled_a_requested_block_is_not_requested_except_its_robots_file():
    """The owner, 16 November 2026: the whole-address Disallow line naming api.cellxgene.cziscience.com in
    cellxgene.cziscience.com's robots file is "to be treated as a requested block". The API host's own robots file is
    still read, so that its answer can be recorded."""
    blocked = "https://api.cellxgene.cziscience.com/curation/v1/collections/283d65eb-dd53-496d-adb7-7570c7caa443"
    assert "requested block" in read_public_page.reason_address_is_not_requested(blocked)
    assert read_public_page.reason_address_is_not_requested("https://api.cellxgene.cziscience.com/robots.txt") is None
    assert read_public_page.reason_address_is_not_requested("https://datasets.cellxgene.cziscience.com/x.h5ad") is None
    assert read_public_page.reason_address_is_not_requested("https://cellxgene.cziscience.com/collections/x") is None


def reader_with_redirects(tmp_path, monkeypatch, redirect_target_by_address: dict, robots_file_by_host: dict) -> tuple:
    """A reader whose requests are answered locally: a redirect for each address in redirect_target_by_address, the
    robots file given for each host (none, so 404, for a host not named) and a short page for anything else."""
    requested = []

    def answer(address):
        requested.append(address)
        if address in redirect_target_by_address:
            raise read_public_page.RedirectAnswer(302, redirect_target_by_address[address])
        if address.endswith("/robots.txt"):
            host = address.split("/")[2]
            if host in robots_file_by_host:
                return 200, "text/plain", robots_file_by_host[host].encode()
            return 404, "text/plain", b""
        return 200, "text/html", b"<html><body>The article.</body></html>"

    monkeypatch.setattr(read_public_page, "request_bytes", answer)
    monkeypatch.setattr(read_public_page, "SECONDS_BETWEEN_REQUESTS_TO_ONE_HOST", 0.0)
    return read_public_page.PublicPageReader(tmp_path), requested


def test_a_redirect_to_a_page_its_hosts_robots_file_disallows_is_not_read(tmp_path, monkeypatch):
    """A Fable pass of decision 9.99 (batch 5, 27 November 2026) found doi.org addresses saved as nature.com articles
    that nature.com's robots file disallows, because urllib followed the redirect and only doi.org's robots file was
    read. The host a redirect leads to is held to its own robots file, and the page is not requested."""
    doi_address = "https://doi.org/10.1038/example"
    article_address = "https://www.nature.com/articles/example"
    reader, requested = reader_with_redirects(tmp_path, monkeypatch, {doi_address: article_address},
                                              {"www.nature.com": "User-agent: *\nDisallow: /articles/\n"})
    record = reader.read(doi_address)
    assert record["read"] is False
    assert "redirected to https://www.nature.com/articles/example" in record["reason"]
    assert "robots file disallows" in record["reason"]
    assert record["redirects"] == [{"from": doi_address, "status_code": 302, "to": article_address}]
    assert article_address not in requested
    assert requested == ["https://doi.org/robots.txt", doi_address, "https://www.nature.com/robots.txt"]
    assert not any(tmp_path.iterdir())


def test_a_redirect_to_an_allowed_page_is_followed_and_recorded(tmp_path, monkeypatch):
    doi_address = "https://doi.org/10.1000/allowed"
    article_address = "https://journal.example.org/article/allowed"
    reader, requested = reader_with_redirects(tmp_path, monkeypatch, {doi_address: article_address},
                                              {"journal.example.org": "User-agent: *\nDisallow: /private/\n"})
    record = reader.read(doi_address)
    assert record["read"] is True, record
    assert record["address"] == doi_address and record["final_address"] == article_address
    assert record["redirects"] == [{"from": doi_address, "status_code": 302, "to": article_address}]
    assert requested == ["https://doi.org/robots.txt", doi_address, "https://journal.example.org/robots.txt", article_address]


@pytest.mark.parametrize("target, expected_reason", [
    ("http://journal.example.org/article", "only https"),
    ("https://api.cellxgene.cziscience.com/curation/v1/collections/x", "requested block"),
    ("https://pubchem.ncbi.nlm.nih.gov/compound/Lithium", "measured pKa records only"),
    ("https://journal.example.org/article?contact=someone%40example.org", "e-mail address"),
])
def test_every_limit_on_the_first_address_holds_on_an_address_a_redirect_reaches(tmp_path, monkeypatch, target, expected_reason):
    start_address = "https://doi.org/10.1000/start"
    reader, requested = reader_with_redirects(tmp_path, monkeypatch, {start_address: target}, {})
    record = reader.read(start_address)
    assert record["read"] is False and expected_reason in record["reason"], record
    assert target not in requested
    assert not any(tmp_path.iterdir())


@pytest.mark.parametrize("start_address, login_address", [
    ("https://www.guidetopharmacology.org/GRAC/ObjectDisplayForward?objectId=1", "https://www.guidetopharmacology.org/login.jsp"),
    ("https://journal.example.org/article/7", "https://journal.example.org/accounts/login/?next=/article/7"),
    ("https://journal.example.org/article/7", "https://journal.example.org/users/sign_in"),
])
def test_a_redirect_to_a_login_form_is_a_refusal_and_the_form_is_not_read(tmp_path, monkeypatch, start_address, login_address):
    """CLAUDE.md records that GtoPdb's target pages "answer 302 to `/login.jsp`" and that "its website login stays a
    refusal". Until 28 November 2026 the reader followed such a redirect and, with no robots file served and no
    challenge marker in a plain login form, saved the form as the page read. The hop is recorded, the form is not
    requested, and nothing is saved."""
    reader, requested = reader_with_redirects(tmp_path, monkeypatch, {start_address: login_address}, {})
    record = reader.read(start_address)
    assert record["read"] is False, record
    assert "login form" in record["reason"] and "refusal" in record["reason"]
    assert record["redirects"] == [{"from": start_address, "status_code": 302, "to": login_address}]
    assert login_address not in requested
    assert not any(tmp_path.iterdir())


def test_a_redirect_to_a_page_that_only_mentions_a_login_is_followed(tmp_path, monkeypatch):
    start_address, help_address = "https://journal.example.org/help", "https://journal.example.org/help/how-to-login"
    reader, requested = reader_with_redirects(tmp_path, monkeypatch, {start_address: help_address}, {})
    assert reader.read(start_address)["read"] is True
    assert help_address in requested


def test_a_redirect_loop_is_cut_off(tmp_path, monkeypatch):
    first, second = "https://a.example.org/one", "https://a.example.org/two"
    reader, requested = reader_with_redirects(tmp_path, monkeypatch, {first: second, second: first}, {})
    record = reader.read(first)
    assert record["read"] is False and "redirects" in record["reason"]
    assert len(record["redirects"]) == read_public_page.MAXIMUM_PAGE_REDIRECTS + 1


def test_a_robots_file_is_read_through_its_redirects(tmp_path, monkeypatch):
    """RFC 9309, section 2.3.1.2: a crawler should follow at least five redirects of the robots file."""
    reader, requested = reader_with_redirects(
        tmp_path, monkeypatch, {"https://example.org/robots.txt": "https://www.example.org/robots.txt"},
        {"www.example.org": "User-agent: *\nDisallow: /closed/\n"})
    assert reader.read("https://example.org/closed/page")["read"] is False
    assert requested == ["https://example.org/robots.txt", "https://www.example.org/robots.txt"]


def test_a_robots_file_that_redirects_away_from_https_leaves_the_page_unread(tmp_path, monkeypatch):
    """From 27 to 28 November 2026 a robots file that redirected to http was taken as not served, so the rules the site
    serves there were dropped and the page was read as if the site had no robots file. This reader requests only
    https, so it cannot read those rules: the page is left unread, as a page whose robots file cannot be requested is,
    and the http address is not requested."""
    reader, requested = reader_with_redirects(
        tmp_path, monkeypatch, {"https://old.example.org/robots.txt": "http://old.example.org/robots.txt"},
        {"old.example.org": "User-agent: *\nDisallow: /\n"})
    record = reader.read("https://old.example.org/closed/page.html")
    assert record["read"] is False, record
    assert "robots file could not be requested" in record["reason"] and "only https" in record["reason"]
    assert requested == ["https://old.example.org/robots.txt"]
    assert not any(tmp_path.iterdir())


@pytest.mark.parametrize("robots_file_redirect_target, expected_reason", [
    ("https://api.cellxgene.cziscience.com/curation/v1/collections", "requested block"),
    ("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/aspirin/JSON", "measured pKa records only"),
    ("https://www.example.org/robots.txt?contact=someone%40example.org", "e-mail address"),
])
def test_every_limit_holds_on_an_address_a_robots_file_redirects_to(tmp_path, monkeypatch, robots_file_redirect_target,
                                                                     expected_reason):
    """Until 28 November 2026 a redirect of the robots file was checked for https alone, so it could lead the reader
    to request an address that reason_address_is_not_requested refuses: a host the owner ruled a requested block,
    PubChem outside its pKa records, or an address carrying an e-mail address. Such a hop is not requested, and the
    page is left unread."""
    reader, requested = reader_with_redirects(
        tmp_path, monkeypatch, {"https://example.org/robots.txt": robots_file_redirect_target}, {})
    record = reader.read("https://example.org/page")
    assert record["read"] is False, record
    assert "robots file could not be requested" in record["reason"] and expected_reason in record["reason"]
    assert requested == ["https://example.org/robots.txt"]
    assert not any(tmp_path.iterdir())


def test_a_robots_file_may_redirect_to_the_robots_file_of_a_host_that_is_otherwise_not_requested(tmp_path, monkeypatch):
    """reason_address_is_not_requested lets the robots file of a requested-block host be read, and so does a robots
    file's redirect to it: its rules then bind the page as any robots file's do."""
    blocked_hosts_robots_file = "https://api.cellxgene.cziscience.com/robots.txt"
    reader, requested = reader_with_redirects(
        tmp_path, monkeypatch, {"https://example.org/robots.txt": blocked_hosts_robots_file},
        {"api.cellxgene.cziscience.com": "User-agent: *\nDisallow: /closed/\n"})
    assert reader.read("https://example.org/open/page")["read"] is True
    assert reader.read("https://example.org/closed/page")["read"] is False
    assert requested == ["https://example.org/robots.txt", blocked_hosts_robots_file, "https://example.org/open/page"]


def test_request_bytes_hands_a_redirect_back_instead_of_following_it(monkeypatch):
    """Against a local server, with no proxy: the answer to a redirect is RedirectAnswer with the target made
    absolute, and the target is not requested."""
    import http.server
    import threading
    import urllib.request

    paths_requested = []

    class RedirectingHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            paths_requested.append(self.path)
            self.send_response(302)
            self.send_header("Location", "/elsewhere")
            self.end_headers()

        def log_message(self, *arguments):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), RedirectingHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setattr(read_public_page, "OPENER_THAT_DOES_NOT_FOLLOW_REDIRECTS",
                        urllib.request.build_opener(urllib.request.ProxyHandler({}), read_public_page.DoNotFollowRedirects))
    try:
        address = f"http://127.0.0.1:{server.server_address[1]}/start"
        with pytest.raises(read_public_page.RedirectAnswer) as raised:
            read_public_page.request_bytes(address)
        assert raised.value.status_code == 302
        assert raised.value.location == f"http://127.0.0.1:{server.server_address[1]}/elsewhere"
        assert paths_requested == ["/start"]
    finally:
        server.shutdown()
        server.server_close()


@pytest.mark.parametrize("location_header, expected_target_path", [
    ("/the article.html", "/the%20article.html"),  # a space
    ("/caf\xc3\xa9.html", "/caf%C3%A9.html"),  # the UTF-8 bytes of "café", which http.client decodes as ISO-8859-1
    ("/caf%C3%A9.html", "/caf%C3%A9.html"),  # already encoded, so not encoded twice
])
def test_request_bytes_percent_encodes_a_redirect_target_as_urllib_did(monkeypatch, location_header, expected_target_path):
    """From 27 to 28 November 2026 the target of a redirect was made absolute but not percent-encoded, so a Location with a
    space or a non-ASCII character made the next hop fail (http.client.InvalidURL, "URL can't contain control
    characters"), where urllib's own redirect handler, which followed redirects before 27 November 2026, encodes it.
    Against a local server, with no proxy: the target is encoded as that handler encodes it, and the next hop reaches
    the page."""
    import http.server
    import threading
    import urllib.request

    class RedirectingHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            if self.path == "/start":
                self.send_response(302)
                self.send_header("Location", location_header)
                self.end_headers()
                return
            self.send_response(200 if self.path == expected_target_path else 404)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"the article")

        def log_message(self, *arguments):
            pass

    server = http.server.HTTPServer(("127.0.0.1", 0), RedirectingHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    monkeypatch.setattr(read_public_page, "OPENER_THAT_DOES_NOT_FOLLOW_REDIRECTS",
                        urllib.request.build_opener(urllib.request.ProxyHandler({}), read_public_page.DoNotFollowRedirects))
    try:
        server_address = f"http://127.0.0.1:{server.server_address[1]}"
        with pytest.raises(read_public_page.RedirectAnswer) as raised:
            read_public_page.request_bytes(f"{server_address}/start")
        assert raised.value.location == f"{server_address}{expected_target_path}"
        assert read_public_page.request_bytes(raised.value.location) == (200, "text/plain", b"the article")
    finally:
        server.shutdown()
        server.server_close()


class BodyThatRecordsItsClosing:
    """A stand-in for the connection an HTTPError holds: it serves a body and records whether it was closed."""

    def __init__(self, body: bytes) -> None:
        import io
        self.stream = io.BytesIO(body)
        self.closed_by_caller = False

    def read(self, *arguments):
        return self.stream.read(*arguments)

    def close(self):
        self.closed_by_caller = True
        self.stream.close()


class OpenerThatAnswersWithAnError:
    def __init__(self, error: urllib.error.HTTPError) -> None:
        self.error = error

    def open(self, request, timeout=None):  # noqa: D102
        raise self.error


@pytest.mark.parametrize("status_code, headers, expect_redirect", [(302, {"Location": "/elsewhere"}, True),
                                                                    (404, {"Content-Type": "text/plain"}, False)])
def test_request_bytes_closes_the_error_answer_on_the_redirect_and_the_error_paths(monkeypatch, status_code, headers, expect_redirect):
    """The HTTPError urllib raises holds the answer's connection; request_bytes closes it whether it raises
    RedirectAnswer or returns the error status with its body, so no socket is left to garbage collection."""
    import email.message
    message = email.message.Message()
    for name, value in headers.items():
        message[name] = value
    body = BodyThatRecordsItsClosing(b"not found")
    error = urllib.error.HTTPError("https://example.org/start", status_code, "answer", message, body)
    monkeypatch.setattr(read_public_page, "OPENER_THAT_DOES_NOT_FOLLOW_REDIRECTS", OpenerThatAnswersWithAnError(error))
    if expect_redirect:
        with pytest.raises(read_public_page.RedirectAnswer) as raised:
            read_public_page.request_bytes("https://example.org/start")
        assert raised.value.location == "https://example.org/elsewhere"
    else:
        assert read_public_page.request_bytes("https://example.org/start") == (404, "text/plain", b"not found")
    assert body.closed_by_caller
