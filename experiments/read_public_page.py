"""Read a public web page from the shell, for the case where the fetch tool would wait for the owner's approval.

Why this exists. In the Claude app the fetch tool reads an address only when it came from a search result or from a
message of the owner, and asks the owner about any other address; the request is withdrawn after five minutes without
an answer. The owner's ruling of 11 October 2026 (CLAUDE.md) makes the shell the standing fallback for such pages.
This script is that fallback with its limits written into code, so that a research pass cannot forget them:

  1. the site's robots file is read first, and a page it disallows for automated readers is left unread. A site
     that serves no robots file places no restriction, which is what the protocol says, so that is read;
     --treat-missing-robots-as-refusal restores the stricter behaviour this script started with. A robots file that
     answers 429 or a server error (5xx) has not said whether it has rules, so the page is not read then
     (RobotsFileNotKnown), unless its host is one read past its robots file (below); for 429, 500 and 503 the record
     is transient, as in limit 2. A redirect is
     followed by this script, one hop at a time, and every limit here is applied again at each address it reaches,
     a robots file's own redirects included (REDIRECT_STATUS_CODES): the robots file of a host a redirect leads to
     binds as the first host's does;
  2. a page that answers with a check that the visitor is human is reported as refused and not saved. A status that
     says the service is busy or down rather than closed to this reader (429, 503, and 500 and a timeout with them)
     is reported as transient and not as a refusal, so the caller may wait and request the same address on the same
     host again (the owner, 17 November 2026: "429 and 503 status codes should not count as refusals"; 500 and the
     timeout as the item 37 rulings draft records, section 13);
  3. an address that carries a personal identifier (an e-mail address) is not requested;
  4. every page read is saved with its address, time and SHA-256, in a directory that holds nothing else.

It does not log in, solve challenges, or use caches and mirrors of a page that refused it, and a redirect to a login
form is reported as a refusal (LOGIN_FORM_PATH), as CLAUDE.md classes a login.

Three hosts are read past their robots file, each on a ruling of the owner's, over https only; the robots file is
still read and its answer recorded beside the page, and limits 2 to 4 hold there as everywhere else. Each exception is
the exact host name and no other host of the same organisation:

  ftp.ebi.ac.uk             EMBL-EBI's FTP host, whose robots file disallows every path for every reader (22 October
                            2026, "don't refuse FTP from EBI");
  dblp.org                  the computer science bibliography, whose search interface refused the reader on 27 October
                            2026 while two entries of docs/references.bib claiming ICLR could not otherwise be verified
                            (the owner, 27 October 2026, asked whether to extend the exception to it: "Yes");
  pubchem.ncbi.nlm.nih.gov  for its measured pKa records only: an address under /rest/pug_view/ whose heading is
                            "Dissociation Constants" (PUBCHEM_PKA_SCOPE). Every other PubChem address, robots file
                            aside, is not requested at all. The owner extended the exception on 19 November 2026 and
                            set its scope on 20 November 2026 (item 37, ruling I1).

One host is not requested at all, other than its robots file, on a ruling of the owner's (REQUESTED_BLOCK_HOSTS):

  api.cellxgene.cziscience.com   named by a whole-address Disallow line in cellxgene.cziscience.com's robots file
                                 (16 November 2026, "yes it should be treated as a requested block").

Usage:
  python experiments/read_public_page.py https://example.org/page.html
  python experiments/read_public_page.py --output-directory data/raw/public_pages --print-text URL [URL ...]
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import string
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from pathlib import Path

USER_AGENT = "mechanistic-pathway-learning/0.1 (research reading of public pages; no login)"
# The robots rules are checked for this script's own name, for every reader ("*") and for the names under which the
# fetch tool and its provider's crawler announce themselves, because a site that turns those away has said it does
# not want an assistant reading the page.
ROBOTS_USER_AGENTS_CHECKED = ("mechanistic-pathway-learning", "*", "Claude-User", "ClaudeBot", "anthropic-ai")
REQUEST_TIMEOUT_SECONDS = 60
SECONDS_BETWEEN_REQUESTS_TO_ONE_HOST = 2.0
CHALLENGE_STATUS_CODES = frozenset({401, 403, 407})
# 429 (too many requests) and 503 (service unavailable) were in this set until 17 November 2026. They say the service
# is busy or down, which is no statement about permission, unlike a robots rule, a login or a human check: three
# research passes of 17 November 2026 met them from Europe PMC while sending several requests at once, and the same
# addresses on the same host answered 200 a few minutes later, one at a time. Counting them as refusals wrote "the
# site refused the reader" into records where the reader had only been throttled, and the rule that a refused page is
# not read elsewhere then closed off routes the site had not closed. The owner, 17 November 2026: "429 and 503 status
# codes should not count as refusals". A page that carries a challenge marker in its body is still a refusal at any
# status, and the throttling is still obeyed: the caller waits and retries the same address on the same host rather
# than going to a cache, a mirror or another host.
# 500 (internal server error) and a request that times out are treated the same way, the reading the item 37 rulings
# draft records beside the owner's repeat of the ruling (section 13, 18 November 2026: "they don't count as blocks so
# retry them"; "The session treats 500 and a timeout the same way"), confirmed with the draft on 20 November 2026:
# both say the service failed, not that it closed itself to this reader. Europe PMC answered 500 to a research pass of
# 20 November 2026 (section 22).
TRANSIENT_STATUS_CODES = frozenset({429, 500, 503})
# Redirects are followed by PublicPageReader.read and not by urllib. Until 27 November 2026 request_bytes let urllib
# follow them, so the robots file was read for the host first named and never for the host a redirect led to: a Fable
# pass of decision 9.99 (batch 5, 27 November 2026) found doi.org addresses saved as nature.com articles that
# nature.com's robots file disallows. Now each hop is a request of its own, refused or read under the same limits as
# the first. A robots file is itself fetched through its redirects, as RFC 9309 (section 2.3.1.2) says a crawler
# should, up to MAXIMUM_ROBOTS_FILE_REDIRECTS, past which it is taken as not served; a redirect of the robots file to an
# address reason_address_is_not_requested refuses (away from https, among others) is not requested and leaves the page
# unread (PublicPageReader._request_robots_file).
REDIRECT_STATUS_CODES = frozenset({301, 302, 303, 307, 308})
MAXIMUM_PAGE_REDIRECTS = 10  # urllib's own limit (HTTPRedirectHandler.max_redirections)
MAXIMUM_ROBOTS_FILE_REDIRECTS = 5
CHALLENGE_MARKERS = (
    "verify you are a human", "verify you are human", "are you a robot", "captcha", "altcha-widget", "cf-chl",
    "challenge-platform", "enable javascript and cookies to continue", "unusual traffic", "access denied",
    # proof-of-work gates that answer with status 200 (a research pass of 11 October 2026 found two saved as pages)
    "anubis", "making sure you're not a bot", "making sure you&#39;re not a bot", "checking your browser", "checking if the site connection is secure", "proof-of-work", "proof of work",
    # The markers a gate puts in its script rather than in its prose, which the words above miss. A research pass of
    # 12 October 2026 found PubMed Central's scanned-PDF gate saved as if it were the document: 200, 1,816 bytes,
    # "Preparing to download ...", and the challenge only in POW_CHALLENGE, POW_DIFFICULTY and pow.init.
    "pow_challenge", "pow_difficulty", "pow.init", "preparing to download",
    # A research pass of 22 October 2026 found nature.com's gate saved as if it were the article: 200, 3,038 bytes,
    # titled "Client Challenge", with its assets under a /_fs-ch- path and none of the words above.
    "client challenge", "/_fs-ch-",
    # A research pass of 8 November 2026 found www.tga.gov.au's Akamai gate saved as if it were the page: 200, about
    # 2,300 bytes, an empty title, and the check only in a form posting to /_sec/verify with a bm-verify field.
    "bm-verify", "/_sec/verify",
    # A research pass of 18 November 2026 met pubmed.ncbi.nlm.nih.gov's gate: HTTP 203, 5,591 bytes, a page titled with
    # the host name alone, "Cookies must be enabled" in a hidden block, and a JavaScript proof-of-work whose only
    # markers are its constants (const challengeId, challengeDomain, bits). None of the words above matched, so it was
    # reported as a plain "HTTP 203" rather than a refusal (item 37 rulings draft, section 13: "the reader's missed case").
    "cookies must be enabled", "challengeid", "challengedomain",
)
# Cloudflare injects its passive bot-telemetry script (/cdn-cgi/challenge-platform/scripts/jsd/main.js) into ordinary
# pages it serves in full, so a "challenge-platform" match inside that script alone is not a check that the visitor is
# human (decision 9.95: WormBase's release directory listing, 200 and 5,173 bytes, was refused on 24 October 2026 for
# that script alone). A real Cloudflare challenge loads /cdn-cgi/challenge-platform/h/... and carries cf-chl markers,
# which still match after this script is set aside.
PASSIVE_TELEMETRY_SCRIPT = re.compile(r"<script\b[^>]*>(?:(?!</script>).)*?/cdn-cgi/challenge-platform/scripts/jsd/(?:(?!</script>).)*?</script>",
                                      re.S | re.I)
# A redirect whose target path ends in a login form's name (login, log-in, sign_in, logon, with or without an extension
# such as .jsp) is a refusal. CLAUDE.md records that GtoPdb's target pages "answer 302 to `/login.jsp`" and that "its
# website login stays a refusal", and that "a check that the visitor is human or a login stays a refusal". A plain login
# form carries none of the CHALLENGE_MARKERS, so until 28 November 2026 the reader followed such a redirect and saved the
# form as the page read. A login form served at the address requested itself is not caught by this.
LOGIN_FORM_PATH = re.compile(r"/(?:log[-_]?in|sign[-_]?in|log[-_]?on)(?:\.[a-z]+)?/?$", re.I)
DEFAULT_OUTPUT_DIRECTORY = Path("data/raw/public_pages")
# The hosts read past a robots rule, each with the ruling that admits it. The match is on the exact host name, so
# www.ebi.ac.uk and every other host of either organisation keeps its own robots rules.
#   ftp.ebi.ac.uk: its robots file reads "User-agent: *" and "Disallow: /" (read 22 October 2026), which closed the
#     releases scripts/fetch_raw_sources.sh already fetches from it (IntAct's negative interactions, IMPC), so the
#     owner ruled on 22 October 2026: "don't refuse FTP from EBI".
#   dblp.org: the computer science bibliography. Its search interface refused this reader on 27 October 2026 during
#     the bibliography sweep of decision 9.101, where it was the one route that would have settled whether
#     loshchilov2019decoupled and alon2021bottleneck are peer-reviewed conference papers, ICLR registering no DOIs.
#     The pass did not assume the exception; asked for it, the owner answered "Yes" (27 October 2026).
ROBOTS_RULE_EXEMPT_HOSTS = {
    "ftp.ebi.ac.uk": "the owner, 22 October 2026: \"don't refuse FTP from EBI\"",
    "dblp.org": "the owner, 27 October 2026, asked whether to extend the exception to dblp.org: \"Yes\"",
}
# PubChem is exempt for one kind of record, not as a host. Its programmatic service refused this reader on 18 and 19
# November 2026 during the ion-state passes of item 37, where it holds most of the measured acid dissociation constants
# the carrier-share class needs; the owner answered "yes" to extending the exception to its measured pKa records (19
# November 2026). The refusal was met under /rest/pug, but the records are served by PUG-View under /rest/pug_view,
# and the scope the owner accepted on 20 November 2026 (ruling I1) is the "Dissociation Constants" heading of
# /rest/pug_view. A depositor's licence is still verified before a value is relied on, since PubChem serves each
# depositor's own terms, and DrugBank's deposits stay unread under the project's DrugBank ruling; neither is something
# this reader can check.
PUBCHEM_HOST = "pubchem.ncbi.nlm.nih.gov"
PUBCHEM_PKA_SCOPE_PATH_PREFIX = "/rest/pug_view/"
PUBCHEM_PKA_SCOPE_HEADING = "dissociation constants"
PUBCHEM_PKA_RULING = ("the owner, 19 November 2026, extending the exception to PubChem's measured pKa records (\"yes\"), "
                      "scoped on 20 November 2026 to the \"Dissociation Constants\" heading of /rest/pug_view")


def is_in_pubchem_pka_scope(address: str) -> bool:
    """True for a PUG-View address whose heading is "Dissociation Constants", given as a heading= query parameter or
    as the last path segment of /rest/pug_view/data/.../JSON?heading=..."""
    parsed_address = urllib.parse.urlsplit(address)
    if (parsed_address.hostname or "").lower() != PUBCHEM_HOST:
        return False
    if not parsed_address.path.startswith(PUBCHEM_PKA_SCOPE_PATH_PREFIX):
        return False
    headings = urllib.parse.parse_qs(parsed_address.query).get("heading", [])
    return bool(headings) and all(heading.strip().lower() == PUBCHEM_PKA_SCOPE_HEADING for heading in headings)


def robots_rule_exemption(address: str) -> str | None:
    """The ruling under which this address is read past its robots rule, or None when the rule applies."""
    host = (urllib.parse.urlsplit(address).hostname or "").lower()
    if host == PUBCHEM_HOST:
        return PUBCHEM_PKA_RULING if is_in_pubchem_pka_scope(address) else None
    return ROBOTS_RULE_EXEMPT_HOSTS.get(host)


# Hosts not requested at all, each on a ruling of the owner's, because another host of the same site asks for it in a
# form the host's own robots file cannot express. Only the host's robots file itself is read, so that its answer can be
# recorded.
#   api.cellxgene.cziscience.com: the robots file of cellxgene.cziscience.com carries the line
#     "Disallow: https://api.cellxgene.cziscience.com/*", a whole address where the protocol expects a path, so a
#     reader that checks only the API host's own robots file is let through, as a Fable pass was on 16 November 2026.
#     Asked whether that line is a refusal, the owner answered "yes it should be treated as a requested block"
#     (16 November 2026).
REQUESTED_BLOCK_HOSTS = {
    "api.cellxgene.cziscience.com": "the owner, 16 November 2026, on the line \"Disallow: "
                                    "https://api.cellxgene.cziscience.com/*\" in cellxgene.cziscience.com's robots "
                                    "file: \"yes it should be treated as a requested block\"",
}


def reason_address_is_not_requested(address: str) -> str | None:
    """Why this address must not be requested, or None when it may be."""
    parsed_address = urllib.parse.urlsplit(address)
    if parsed_address.scheme != "https":
        return "only https addresses are read"
    if not parsed_address.hostname or "." not in parsed_address.hostname:
        return "the address has no public host name"
    blocking_ruling = REQUESTED_BLOCK_HOSTS.get(parsed_address.hostname.lower())
    if blocking_ruling and parsed_address.path != "/robots.txt":
        return f"the host is treated as a requested block ({blocking_ruling})"
    if (parsed_address.hostname.lower() == PUBCHEM_HOST and parsed_address.path != "/robots.txt"
            and not is_in_pubchem_pka_scope(address)):
        return ("PubChem is read for its measured pKa records only, the \"Dissociation Constants\" heading of "
                "/rest/pug_view (" + PUBCHEM_PKA_RULING + ")")
    if parsed_address.username or parsed_address.password:
        return "the address carries credentials"
    decoded_address = urllib.parse.unquote(address)
    if re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", decoded_address):
        return "the address carries an e-mail address, and no personal identifier goes into a request"
    return None


def robots_file_allows(robots_file_text: str, address: str, user_agents: tuple[str, ...] = ROBOTS_USER_AGENTS_CHECKED) -> bool:
    """True when the robots rules allow the address for every one of the user agents checked."""
    parser = urllib.robotparser.RobotFileParser()
    parser.parse(robots_file_text.splitlines())
    return all(parser.can_fetch(user_agent, address) for user_agent in user_agents)


def looks_like_robots_file(response_text: str) -> bool:
    """A robots file is plain text; a site that answers the request for it with a web page has not served one."""
    leading_text = response_text.lstrip()[:400].lower()
    return not (leading_text.startswith("<!doctype") or leading_text.startswith("<html") or "<head" in leading_text)


# An interstitial is short in what a reader sees, however much markup carries it, while an article that mentions a
# captcha is long in readable text. The 20,000-character test on the raw page alone let a 21,362-byte PubMed Central
# reCAPTCHA page ("Checking your browser before accessing pmc.ncbi.nlm.nih.gov") pass as a page read on 27 October 2026
# (decision 9.102 (c)), so a page over that size is still a challenge when its readable text is under this ceiling.
CHALLENGE_SCAN_CHARACTERS = 20000
CHALLENGE_READABLE_TEXT_CEILING = 3000


def looks_like_challenge(status_code: int, response_text: str) -> bool:
    """True when the answer is a refusal or a check that the visitor is human rather than the page asked for."""
    if status_code in CHALLENGE_STATUS_CODES:
        return True
    without_passive_telemetry = PASSIVE_TELEMETRY_SCRIPT.sub(" ", response_text)
    leading_text = without_passive_telemetry[:CHALLENGE_SCAN_CHARACTERS].lower()
    if not any(marker in leading_text for marker in CHALLENGE_MARKERS):
        return False
    return (len(without_passive_telemetry) < CHALLENGE_SCAN_CHARACTERS
            or len(text_of_page(without_passive_telemetry)) < CHALLENGE_READABLE_TEXT_CEILING)


def text_of_page(page_source: str) -> str:
    """The readable text of an HTML page: scripts and styles removed, tags dropped, entities decoded."""
    without_scripts = re.sub(r"<(script|style|noscript)\b.*?</\1>", " ", page_source, flags=re.S | re.I)
    without_tags = re.sub(r"<[^>]+>", " ", without_scripts)
    return re.sub(r"\s+", " ", html.unescape(without_tags)).strip()


def is_timeout(error: BaseException) -> bool:
    """True when a request failed by timing out: a read that timed out raises TimeoutError (socket.timeout), and a
    connection that timed out arrives as a URLError whose reason is one."""
    if isinstance(error, TimeoutError):
        return True
    return isinstance(error, urllib.error.URLError) and isinstance(getattr(error, "reason", None), TimeoutError)


class RobotsFileNotKnown(Exception):
    """The robots file answered 429 or a server error (5xx), so its rules are not known and the page is not read then,
    unless it is read past its robots file (PublicPageReader.robots_file_of_host and _robots_answer); nothing is
    cached, so a later request asks for the robots file again."""

    def __init__(self, status_code: int) -> None:
        super().__init__(f"HTTP {status_code}")
        self.status_code = status_code


class RedirectAnswer(Exception):
    """The server answered with a redirect, which the caller follows (or refuses) as a request of its own."""

    def __init__(self, status_code: int, location: str) -> None:
        super().__init__(f"HTTP {status_code} to {location}")
        self.status_code = status_code
        self.location = location


class DoNotFollowRedirects(urllib.request.HTTPRedirectHandler):
    """Makes urllib hand a redirect back as an HTTPError instead of following it."""

    def redirect_request(self, request, response_file, status_code, message, headers, new_address):  # noqa: D102
        return None


OPENER_THAT_DOES_NOT_FOLLOW_REDIRECTS = urllib.request.build_opener(DoNotFollowRedirects)


def request_bytes(address: str) -> tuple[int, str, bytes]:
    """Status code, content type and body of one GET. An HTTP error status is returned, not raised; a redirect is not
    followed but raised as RedirectAnswer, with its target percent-encoded as urllib's own redirect handler encodes it
    (HTTPRedirectHandler.http_error_302) and made absolute. From 27 to 28 November 2026 the target was not encoded, so
    a Location with a space or a non-ASCII character failed at the next hop. The HTTPError holds the answer's connection
    open, so it is closed on both paths (after its body is read on the error path) rather than left to garbage
    collection."""
    request = urllib.request.Request(address, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,text/plain,application/pdf;q=0.9,*/*;q=0.5"})
    try:
        with OPENER_THAT_DOES_NOT_FOLLOW_REDIRECTS.open(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            return response.status, response.headers.get("Content-Type", ""), response.read()
    except urllib.error.HTTPError as error:
        try:
            location = error.headers.get("Location") if error.headers else None
            if error.code in REDIRECT_STATUS_CODES and location:
                # http.client decodes a header as ISO-8859-1: this recovers the bytes sent and percent-encodes the
                # non-ASCII ones and characters such as a space, leaving what is already encoded ("%" is punctuation)
                location = urllib.parse.quote(location, encoding="iso-8859-1", safe=string.punctuation)
                raise RedirectAnswer(error.code, urllib.parse.urljoin(address, location)) from None
            return error.code, error.headers.get("Content-Type", "") if error.headers else "", error.read() or b""
        finally:
            error.close()


class PublicPageReader:
    """Reads pages one at a time, with one robots file per host and a pause between requests to the same host."""

    def __init__(self, output_directory: Path, treat_missing_robots_as_refusal: bool = False) -> None:
        self.output_directory = Path(output_directory)
        self.treat_missing_robots_as_refusal = treat_missing_robots_as_refusal
        self.robots_file_by_host: dict[str, str | None] = {}
        self.last_request_time_by_host: dict[str, float] = {}

    def _wait_for_host(self, host: str) -> None:
        elapsed_seconds = time.monotonic() - self.last_request_time_by_host.get(host, 0.0)
        if elapsed_seconds < SECONDS_BETWEEN_REQUESTS_TO_ONE_HOST:
            time.sleep(SECONDS_BETWEEN_REQUESTS_TO_ONE_HOST - elapsed_seconds)
        self.last_request_time_by_host[host] = time.monotonic()

    def _request_robots_file(self, host: str) -> tuple[int, bytes] | None:
        """Status and body of the host's robots file, through at most MAXIMUM_ROBOTS_FILE_REDIRECTS redirects (RFC 9309,
        section 2.3.1.2); None when it redirects further than that. Each hop is held to reason_address_is_not_requested,
        as every page address is: a hop it refuses (away from https, to a requested-block host, ...) is not requested
        and raises, so that the page is left unread, as one whose robots file cannot be requested is. Until 28 November
        2026 a hop was checked for https alone, and from 27 November a hop away from https returned None, which dropped
        the site's rules as if it served none (before 27 November urllib followed it to http and read them)."""
        robots_address = f"https://{host}/robots.txt"
        for _ in range(MAXIMUM_ROBOTS_FILE_REDIRECTS + 1):
            self._wait_for_host(urllib.parse.urlsplit(robots_address).hostname or "")
            try:
                status_code, _, body = request_bytes(robots_address)
                return status_code, body
            except RedirectAnswer as redirect:
                reason_hop_is_not_requested = reason_address_is_not_requested(redirect.location)
                if reason_hop_is_not_requested:
                    raise RuntimeError(f"it redirected to {redirect.location}, and {reason_hop_is_not_requested}") from None
                robots_address = redirect.location
        return None

    def robots_file_of_host(self, host: str) -> str | None:
        """The host's robots rules as text; an empty string when it has none; None when it would not serve them.

        A robots file that answers 429 or a server error (5xx) has not said whether it has rules, so RobotsFileNotKnown
        is raised and nothing is cached: the page is not read then, unless it is read past its robots file
        (_robots_answer). The installed standard library's
        urllib.robotparser assumes complete disallow for a 5xx (its comment cites RFC 9309, section 2.3.1.4); 429 is
        taken with them because it asks the reader to wait, which a page requested straight after it would not do
        (TRANSIENT_STATUS_CODES). Until 28 November 2026 such an answer was cached as None, and every page of the host
        was read as if it served none."""
        if host not in self.robots_file_by_host:
            robots_answer = self._request_robots_file(host)
            if robots_answer is None:
                self.robots_file_by_host[host] = None
                return None
            status_code, body = robots_answer
            if status_code in TRANSIENT_STATUS_CODES or 500 <= status_code < 600:
                raise RobotsFileNotKnown(status_code)
            robots_file_text = body.decode("utf-8", errors="replace")
            if status_code == 404:
                self.robots_file_by_host[host] = ""
            elif status_code == 200 and looks_like_robots_file(robots_file_text):
                self.robots_file_by_host[host] = robots_file_text
            else:
                self.robots_file_by_host[host] = None
        return self.robots_file_by_host[host]

    def _robots_answer(self, address: str) -> tuple[str | None, str | None]:
        """(why the address may not be read, or None; the note on the robots file to record, or None). RobotsFileNotKnown
        is raised on to read(), which reports it as transient when its status is (TRANSIENT_STATUS_CODES), except for an
        address read past its robots file (robots_rule_exemption), which is read with the answer recorded."""
        host = urllib.parse.urlsplit(address).hostname or ""
        try:
            robots_file_text = self.robots_file_of_host(host)
        except RobotsFileNotKnown as robots_file_not_known:
            exemption = robots_rule_exemption(address)
            if exemption is None:
                raise
            # a host read past its robots file is read whatever the rules say, so rules not known do not hold it back
            return None, f"answered HTTP {robots_file_not_known.status_code}; read under the ruling of {exemption}"
        except Exception as error:  # noqa: BLE001 - a network failure, or a redirect not requested, is reported, not raised
            return f"the robots file could not be requested ({error})", None
        if robots_file_text is None:
            # The Robots Exclusion Protocol says an absent robots file places no restriction, so treating one as a
            # refusal was this script's own policy and not the site's answer (the owner, 14 October 2026: "can you
            # please just try to route around that GtoPdb refusal"). Guide to PHARMACOLOGY serves no robots file and
            # the project already holds two of its files, so the policy was turning away a source it had read before.
            # A real Disallow rule and a check that the visitor is human are still refusals and are still respected.
            if self.treat_missing_robots_as_refusal:
                return "the site did not serve a robots file, and this reader was asked to treat that as a refusal", None
            return None, "none served, which the protocol treats as no restriction"
        if not robots_file_allows(robots_file_text, address):
            exemption = robots_rule_exemption(address)
            if exemption is None:
                return "the site's robots file disallows this address for automated readers", None
            return None, f"disallows this address; read under the ruling of {exemption}"
        return None, None

    def read(self, address: str) -> dict:
        """One record per address: whether it was read, why not when it was not, and where the page was saved. A
        redirect is followed here, one hop at a time, and each address it reaches is refused or read under every
        limit the first address was (REDIRECT_STATUS_CODES), and a redirect to a login form is a refusal
        (LOGIN_FORM_PATH); the record lists the hops under "redirects"."""
        record: dict = {"address": address, "read": False, "requested_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        current_address = address
        redirects: list[dict] = []
        while True:
            on_redirect = f"the address redirected to {current_address}, and " if redirects else ""
            refusal_reason = reason_address_is_not_requested(current_address)
            if refusal_reason:
                return record | {"reason": on_redirect + refusal_reason}
            try:
                robots_refusal, robots_note = self._robots_answer(current_address)
            except RobotsFileNotKnown as robots_file_not_known:
                robots_status_code = robots_file_not_known.status_code
                if robots_status_code not in TRANSIENT_STATUS_CODES:
                    return record | {"reason": on_redirect + f"the robots file answered HTTP {robots_status_code}, so its "
                                                              f"rules are not known and the page is not read"}
                return record | {"reason": on_redirect + f"the robots file answered HTTP {robots_status_code}, which is "
                                                          f"not a refusal, but its rules are not known, so the page is not read "
                                                          f"now; wait and request this same address on this same host "
                                                          f"again, rather than a cache, a mirror or another host",
                                 "transient": True}
            if robots_refusal:
                return record | {"reason": on_redirect + robots_refusal}
            if robots_note:
                record["robots_file"] = robots_note if not redirects else f"at {current_address}: {robots_note}"
            self._wait_for_host(urllib.parse.urlsplit(current_address).hostname or "")
            try:
                status_code, content_type, body = request_bytes(current_address)
                break
            except RedirectAnswer as redirect:
                redirects.append({"from": current_address, "status_code": redirect.status_code, "to": redirect.location})
                record["redirects"] = redirects
                if len(redirects) > MAXIMUM_PAGE_REDIRECTS:
                    return record | {"reason": f"more than {MAXIMUM_PAGE_REDIRECTS} redirects"}
                if LOGIN_FORM_PATH.search(urllib.parse.urlsplit(redirect.location).path):
                    return record | {"reason": f"the address redirected to {redirect.location}, a login form, and a login "
                                               f"is a refusal (this reader does not log in)"}
                current_address = redirect.location
                continue
            except Exception as error:  # noqa: BLE001
                if is_timeout(error):  # transient, as a 500 is (TRANSIENT_STATUS_CODES)
                    return record | {"reason": f"the request timed out, which is not a refusal ({error}); "
                                               f"wait and request this same address on this same host again, rather "
                                               f"than a cache, a mirror or another host",
                                     "transient": True}
                return record | {"reason": f"the request failed ({error})"}
        if redirects:
            record["final_address"] = current_address
        is_text = "pdf" not in content_type.lower() and not body.startswith(b"%PDF")
        response_text = body.decode("utf-8", errors="replace") if is_text else ""
        record |= {"status_code": status_code, "content_type": content_type, "bytes": len(body)}
        if looks_like_challenge(status_code, response_text):
            return record | {"reason": f"the site answered with a refusal or a check that the visitor is human (HTTP {status_code})"}
        if status_code in TRANSIENT_STATUS_CODES:
            return record | {"reason": f"the service was busy or unavailable, which is not a refusal (HTTP {status_code}); "
                                       f"wait and request this same address on this same host again, rather than a cache, "
                                       f"a mirror or another host",
                             "transient": True}
        if status_code != 200:
            return record | {"reason": f"HTTP {status_code}"}
        digest = hashlib.sha256(body).hexdigest()
        self.output_directory.mkdir(parents=True, exist_ok=True)
        extension = ".pdf" if not is_text else (".html" if "html" in content_type.lower() else ".txt")
        saved_path = self.output_directory / f"{digest[:16]}{extension}"
        saved_path.write_bytes(body)
        record |= {"read": True, "sha256": digest, "saved_as": str(saved_path)}
        saved_path.with_suffix(saved_path.suffix + ".json").write_text(json.dumps(record, indent=1))
        if is_text:
            record["text"] = text_of_page(response_text) if extension == ".html" else response_text
        return record


def main() -> int:
    argument_parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    argument_parser.add_argument("addresses", nargs="+")
    argument_parser.add_argument("--output-directory", type=Path, default=DEFAULT_OUTPUT_DIRECTORY)
    argument_parser.add_argument("--treat-missing-robots-as-refusal", action="store_true",
                                 help="leave a page unread when the site serves no robots file; the protocol treats an absent file as no restriction, so this is stricter than the standard")
    argument_parser.add_argument("--print-text", action="store_true", help="print the readable text of each page read")
    argument_parser.add_argument("--text-characters", type=int, default=6000, help="how much text --print-text shows per page")
    arguments = argument_parser.parse_args()
    reader = PublicPageReader(arguments.output_directory, arguments.treat_missing_robots_as_refusal)
    pages_not_read = 0
    for address in arguments.addresses:
        record = reader.read(address)
        page_text = record.pop("text", None)
        print(json.dumps(record))
        if not record["read"]:
            pages_not_read += 1
        elif arguments.print_text and page_text is not None:
            print(page_text[: arguments.text_characters])
    return 1 if pages_not_read else 0


if __name__ == "__main__":
    sys.exit(main())
