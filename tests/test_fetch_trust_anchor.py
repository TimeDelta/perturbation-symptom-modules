"""The one extra root scripts/fetch_raw_sources.sh trusts, and only for zfin.org.

zfin.org's certificate chains to emSign Root CA - G1, which Ubuntu's current ca-certificates no longer ships; the owner
asked on 4 November 2026 that it be trusted again ("add those ZFIN back to the trusted certificates please"). These
tests keep the three things that make that safe from drifting apart: the committed root is the one the script pins, the
script refuses any other root, and the extra bundle reaches the zfin.org fetches and no other.
"""
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
FETCH_SCRIPT = REPOSITORY_ROOT / "scripts" / "fetch_raw_sources.sh"
TRUST_ANCHOR = REPOSITORY_ROOT / "configs" / "tls" / "emsign_root_ca_g1.pem"
needs_openssl = pytest.mark.skipif(shutil.which("openssl") is None, reason="openssl is not installed")


def pinned_fingerprint() -> str:
    match = re.search(r'^zfin_trust_anchor_fingerprint="([0-9A-F:]+)"$', FETCH_SCRIPT.read_text(), flags=re.MULTILINE)
    assert match, "the fetch script no longer pins the ZFIN trust anchor's fingerprint"
    return match.group(1)


def anchor_function() -> str:
    match = re.search(r"^bundle_with_trust_anchor\(\) \{\n.*?^\}\n", FETCH_SCRIPT.read_text(), flags=re.MULTILINE | re.DOTALL)
    assert match, "bundle_with_trust_anchor is not in the fetch script"
    return match.group(0)


@needs_openssl
def test_the_committed_root_is_the_one_the_script_pins():
    measured = subprocess.run(["openssl", "x509", "-in", str(TRUST_ANCHOR), "-noout", "-fingerprint", "-sha256"],
                              capture_output=True, text=True, check=True).stdout.strip().split("=", 1)[1]
    assert measured == pinned_fingerprint()
    subject = subprocess.run(["openssl", "x509", "-in", str(TRUST_ANCHOR), "-noout", "-subject"],
                             capture_output=True, text=True, check=True).stdout
    assert "emSign Root CA - G1" in subject


@needs_openssl
def test_a_root_other_than_the_pinned_one_is_refused(tmp_path):
    """A valid certificate that is not the pinned root makes no bundle, so a swapped file cannot widen what is trusted."""
    other_root = tmp_path / "other_root.pem"
    subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", str(tmp_path / "key.pem"),
                    "-out", str(other_root), "-days", "1", "-subj", "/CN=not the pinned root"], capture_output=True, check=True)
    result = subprocess.run(["bash", "-c", anchor_function() + f'bundle_with_trust_anchor "{other_root}" "{pinned_fingerprint()}"'],
                            capture_output=True, text=True)
    assert result.returncode != 0 and "REFUSED" in result.stderr and result.stdout == ""


def test_the_extra_bundle_reaches_the_zfin_fetches_and_no_other():
    """The root is trusted for zfin.org alone: every fetch line passing the bundle is a zfin.org download, and every
    zfin.org download passes it."""
    fetch_lines = [line.strip() for line in FETCH_SCRIPT.read_text().splitlines() if line.strip().startswith("fetch ")]
    with_bundle = [line for line in fetch_lines if "$zfin_ca_bundle" in line]
    zfin_lines = [line for line in fetch_lines if "https://zfin.org/" in line]
    assert with_bundle and with_bundle == zfin_lines
    assert all("--cacert" not in line for line in FETCH_SCRIPT.read_text().splitlines() if "curl" in line and "curl_trust" not in line)
