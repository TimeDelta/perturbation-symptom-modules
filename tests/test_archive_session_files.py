"""experiments/archive_session_files.py: every archive within the limit, every file restorable, the selection rules."""
import gzip
import hashlib
import os
import zipfile
from pathlib import Path

from experiments import archive_session_files


def make_session(tmp_path: Path) -> tuple[Path, Path, Path]:
    uploads = tmp_path / "uploads"
    scratchpad = tmp_path / "scratchpad"
    (uploads).mkdir()
    (scratchpad / "report_pages").mkdir(parents=True)
    (scratchpad / "humangem_clone").mkdir()
    (scratchpad / "__pycache__").mkdir()
    (uploads / "paper.pdf").write_bytes(os.urandom(300_000))  # incompressible, like a PDF
    (uploads / "big_upload.bin").write_bytes(os.urandom(2_500_000))  # larger than one archive: split
    (scratchpad / "report.md").write_text("finding\n" * 20_000)
    (scratchpad / "report_pages" / "page.txt").write_text("saved page\n" * 5_000)
    (scratchpad / "humangem_clone" / "model.yml").write_text("a provider download")
    (scratchpad / "__pycache__" / "x.py").write_text("cache")
    (scratchpad / "intermediate.parquet").write_bytes(b"binary")
    transcript = tmp_path / "session.jsonl"
    transcript.write_text('{"turn": 1}\n' * 50_000)
    return uploads, scratchpad, transcript


def test_selection_skips_downloads_caches_and_binary_intermediates(tmp_path):
    uploads, scratchpad, _ = make_session(tmp_path)
    selected = {path.relative_to(scratchpad).as_posix() for path in archive_session_files.scratchpad_files(
        scratchpad, archive_session_files.DEFAULT_EXCLUDED_DIRECTORY_PATTERNS, 25_000_000)}
    assert selected == {"report.md", "report_pages/page.txt"}


def test_archives_stay_within_the_limit_and_restore_every_file(tmp_path):
    uploads, scratchpad, transcript = make_session(tmp_path)
    limit = 1_000_000
    members = archive_session_files.collect_members([uploads], [transcript], [scratchpad],
                                                    archive_session_files.DEFAULT_EXCLUDED_DIRECTORY_PATTERNS, 25_000_000, limit)
    bins = archive_session_files.pack_first_fit_decreasing(members, limit)
    written = archive_session_files.write_archives(bins, tmp_path / "out", "test", limit)
    assert len(written) >= 4 and all(path.stat().st_size <= limit for path in written)

    restored: dict[str, bytes] = {}
    parts: dict[str, list[tuple[str, bytes]]] = {}
    for path in written:
        with zipfile.ZipFile(path) as archive:
            assert archive_session_files.MANIFEST_NAME in archive.namelist()
            for name in archive.namelist():
                if name in (archive_session_files.MANIFEST_NAME, archive_session_files.README_NAME):
                    continue
                if ".gz.part" in name:
                    parts.setdefault(name.rsplit(".gz.part", 1)[0], []).append((name, archive.read(name)))
                else:
                    restored[name] = archive.read(name)
    for name, pieces in parts.items():
        restored[name] = gzip.decompress(b"".join(piece for _, piece in sorted(pieces)))
    assert "uploads/big_upload.bin" in parts, "the file larger than one archive is split"
    expected = {"uploads/paper.pdf": uploads / "paper.pdf", "uploads/big_upload.bin": uploads / "big_upload.bin",
                "transcript/session.jsonl": transcript, "scratchpad/report.md": scratchpad / "report.md",
                "scratchpad/report_pages/page.txt": scratchpad / "report_pages" / "page.txt"}
    assert set(restored) == set(expected)
    for name, source in expected.items():
        assert hashlib.sha256(restored[name]).digest() == hashlib.sha256(source.read_bytes()).digest(), name
