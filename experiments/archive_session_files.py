"""Pack what a session holds that a script cannot fetch again into zip archives of at most a given size.

Why this exists. A cloud session's container is reclaimed after the session, and with it the files the owner uploaded
(papers, supplements, data files), the scratchpad's research reports, progress logs, draft rows and saved provenance
pages, and the session transcript. The repository keeps none of them, and several cannot be fetched again without the
owner (a paper behind a login, a page saved before a site began refusing the reader). The owner, 20 November 2026,
asked for "a script or skill that will compress all of the papers and data, etc that I uploaded during the session
(basically anything that might be wanted later by another session and isn't easily fetchable) into a series of archives
at most 30MB each".

What goes in, by category (each file's category is recorded in the index):
  upload      every file in --uploads-dir, whatever its kind: the owner supplied it (CLAUDE.md, Jobs: a file the owner
              supplied is never treated as re-fetchable).
  transcript  each --transcript file (the session's JSONL), which no other place holds.
  scratchpad  files under --scratchpad-dir whose extension is in RESEARCH_EXTENSIONS (reports, logs, draft tables,
              bibliography drafts, the tools' scripts, saved pages as text, HTML, XML or PDF), skipping any path with a
              component matching DEFAULT_EXCLUDED_DIRECTORY_PATTERNS or --exclude, and any file larger than
              --max-scratchpad-file-mb. Binary intermediates (parquet, npz, h5ad, provider archives) are left out:
              they are a provider's download or are recomputed by the tools' scripts, which go in.
--dry-run prints what would go in, per category and per top-level scratchpad directory, and writes nothing.

How the archives are packed. Each file's deflated size is measured first, and the files are packed first-fit by
decreasing size, so no archive exceeds --max-archive-mb (decimal megabytes, 30 MB = 30,000,000 bytes) once the zip
headers and its own manifest are counted. A file whose deflated size alone exceeds the limit is gzip-compressed and its
bytes split into parts named <path>.gz.part001, .part002, ..., each in an archive of its own; `cat` the parts in order
and gunzip to restore it. Every archive holds ARCHIVE_MANIFEST.tsv (what it holds), and the first also holds
README.txt; the whole index, with each file's SHA-256, is written beside the archives as session_archive_index.tsv.

Usage:
  python experiments/archive_session_files.py --uploads-dir <dir> --scratchpad-dir <dir> --transcript <file.jsonl> \\
      --output-dir session_archives/<date> [--dry-run]
"""
from __future__ import annotations

import argparse
import csv
import fnmatch
import gzip
import hashlib
import io
import zipfile
import zlib
from dataclasses import dataclass
from pathlib import Path

RESEARCH_EXTENSIONS = frozenset({".md", ".bib", ".csv", ".tsv", ".txt", ".json", ".jsonl", ".py", ".sh", ".xml",
                                 ".html", ".htm", ".pdf", ".yml", ".yaml", ".out", ".log"})
# Directory names under the scratchpad that hold provider downloads or their unpacked copies, which a script fetches
# again unattended (CLAUDE.md, Jobs), and caches of no use to a later session.
DEFAULT_EXCLUDED_DIRECTORY_PATTERNS = ("__pycache__", "*_clone", "*download*", "dl_*", "*_unzip", ".git")
MANIFEST_NAME = "ARCHIVE_MANIFEST.tsv"
README_NAME = "README.txt"
INDEX_NAME = "session_archive_index.tsv"
# Bytes a zip adds per entry beyond the compressed data and twice the name (local header 30, central directory 46,
# zip64 extra fields and data descriptor at most 48), rounded up.
ZIP_ENTRY_OVERHEAD_BYTES = 160
# Kept free in every archive for the end-of-central-directory records and the manifest's own entry.
ARCHIVE_RESERVE_BYTES = 256 * 1024


@dataclass
class ArchiveMember:
    source_path: Path | None  # None for a part of a split file, whose bytes are in part_bytes
    archive_name: str
    category: str
    original_size: int
    sha256: str
    deflated_size: int
    part_bytes: bytes | None = None


def is_excluded(relative_path: Path, excluded_patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatch(component, pattern) for component in relative_path.parts[:-1] for pattern in excluded_patterns)


def scratchpad_files(scratchpad_dir: Path, excluded_patterns: tuple[str, ...], max_file_bytes: int) -> list[Path]:
    """The scratchpad's research files, by the rules of the module docstring, sorted."""
    selected = []
    for path in sorted(scratchpad_dir.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(scratchpad_dir)
        if is_excluded(relative, excluded_patterns) or path.suffix.lower() not in RESEARCH_EXTENSIONS:
            continue
        if path.stat().st_size > max_file_bytes:
            continue
        selected.append(path)
    return selected


def deflated_size(data: bytes) -> int:
    compressor = zlib.compressobj(6, zlib.DEFLATED, -15)
    return len(compressor.compress(data)) + len(compressor.flush())


def entry_cost(member: ArchiveMember) -> int:
    return member.deflated_size + 2 * len(member.archive_name.encode()) + ZIP_ENTRY_OVERHEAD_BYTES


def members_of_file(source_path: Path, archive_name: str, category: str, max_archive_bytes: int) -> list[ArchiveMember]:
    """One member for a file that fits an archive; gzip parts, each filling at most one archive, for one that does not."""
    data = source_path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    member = ArchiveMember(source_path, archive_name, category, len(data), digest, deflated_size(data))
    if entry_cost(member) <= max_archive_bytes - ARCHIVE_RESERVE_BYTES:
        return [member]
    compressed = gzip.compress(data, compresslevel=6, mtime=0)
    part_name_bytes = len(f"{archive_name}.gz.part000".encode())
    part_capacity = max_archive_bytes - ARCHIVE_RESERVE_BYTES - 2 * part_name_bytes - 64 - ZIP_ENTRY_OVERHEAD_BYTES
    parts = [compressed[start:start + part_capacity] for start in range(0, len(compressed), part_capacity)]
    return [ArchiveMember(None, f"{archive_name}.gz.part{number:03d}", category, len(data), digest,
                          len(part) + 64, part_bytes=part)  # stored, not deflated: gzip bytes do not shrink
            for number, part in enumerate(parts, start=1)]


def pack_first_fit_decreasing(members: list[ArchiveMember], max_archive_bytes: int) -> list[list[ArchiveMember]]:
    capacity = max_archive_bytes - ARCHIVE_RESERVE_BYTES
    bins: list[list[ArchiveMember]] = []
    used: list[int] = []
    for member in sorted(members, key=lambda each: (-entry_cost(each), each.archive_name)):
        cost = entry_cost(member)
        if cost > capacity:
            raise ValueError(f"{member.archive_name} needs {cost} bytes, more than an archive holds ({capacity})")
        for index, already_used in enumerate(used):
            if already_used + cost <= capacity:
                bins[index].append(member)
                used[index] += cost
                break
        else:
            bins.append([member])
            used.append(cost)
    return bins


def manifest_text(members: list[ArchiveMember]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter="\t", lineterminator="\n")
    writer.writerow(["archive_name", "category", "original_size_bytes", "sha256_of_whole_file", "original_path"])
    for member in sorted(members, key=lambda each: each.archive_name):
        writer.writerow([member.archive_name, member.category, member.original_size, member.sha256,
                         str(member.source_path) if member.source_path else "(part of a split file)"])
    return buffer.getvalue()


README_TEXT = """Archives written by experiments/archive_session_files.py (repository perturbation-symptom-modules).

Each archive holds ARCHIVE_MANIFEST.tsv listing its files, their category (upload, transcript, scratchpad), size and
SHA-256. The index of every archive is session_archive_index.tsv, written beside them.

Paths: uploads/ holds the files the owner uploaded, transcript/ the session transcript, scratchpad/ the session's
research reports, progress logs, draft tables, tools and saved pages, at their scratchpad-relative paths.

A file too large for one archive is stored as <path>.gz.part001, .part002, ... in separate archives. To restore it:
  cat <path>.gz.part* > <path>.gz && gunzip <path>.gz
and check its SHA-256 against the manifest.
"""


def write_archives(bins: list[list[ArchiveMember]], output_dir: Path, archive_stem: str, max_archive_bytes: int) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for number, members in enumerate(bins, start=1):
        archive_path = output_dir / f"{archive_stem}_{number:03d}_of_{len(bins):03d}.zip"
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as archive:
            if number == 1:
                archive.writestr(README_NAME, README_TEXT)
            archive.writestr(MANIFEST_NAME, manifest_text(members))
            for member in sorted(members, key=lambda each: each.archive_name):
                if member.part_bytes is not None:
                    archive.writestr(zipfile.ZipInfo(member.archive_name), member.part_bytes, compress_type=zipfile.ZIP_STORED)
                else:
                    archive.write(member.source_path, member.archive_name)
        size = archive_path.stat().st_size
        if size > max_archive_bytes:
            raise RuntimeError(f"{archive_path} is {size} bytes, over the limit of {max_archive_bytes}")
        written.append(archive_path)
    return written


def collect_members(uploads_dirs: list[Path], transcripts: list[Path], scratchpad_dirs: list[Path],
                    excluded_patterns: tuple[str, ...], max_scratchpad_file_bytes: int, max_archive_bytes: int) -> list[ArchiveMember]:
    members: list[ArchiveMember] = []
    for uploads_dir in uploads_dirs:
        for path in sorted(p for p in uploads_dir.rglob("*") if p.is_file() and not p.is_symlink()):
            members += members_of_file(path, f"uploads/{path.relative_to(uploads_dir).as_posix()}", "upload", max_archive_bytes)
    for transcript in transcripts:
        members += members_of_file(transcript, f"transcript/{transcript.name}", "transcript", max_archive_bytes)
    for scratchpad_dir in scratchpad_dirs:
        for path in scratchpad_files(scratchpad_dir, excluded_patterns, max_scratchpad_file_bytes):
            members += members_of_file(path, f"scratchpad/{path.relative_to(scratchpad_dir).as_posix()}", "scratchpad", max_archive_bytes)
    names = [member.archive_name for member in members]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError(f"two sources map to one archive path: {duplicates[:5]}")
    return members


def summary_lines(members: list[ArchiveMember]) -> list[str]:
    totals: dict[str, list[int]] = {}
    counted_split_files: set[str] = set()
    for member in members:
        whole_name = member.archive_name.rsplit(".gz.part", 1)[0] if member.part_bytes is not None else member.archive_name
        if member.category == "scratchpad":
            top = member.archive_name.split("/")[1] if member.archive_name.count("/") > 1 else "(top level)"
            key = f"scratchpad/{top}"
        else:
            key = member.category
        entry = totals.setdefault(key, [0, 0, 0])
        if whole_name not in counted_split_files:  # a split file counts once, however many parts it has
            entry[0] += 1
            entry[1] += member.original_size
            counted_split_files.add(whole_name)
        entry[2] += member.deflated_size
    return [f"{key}\t{count} files\t{original / 1e6:.1f} MB\t{deflated / 1e6:.1f} MB deflated"
            for key, (count, original, deflated) in sorted(totals.items(), key=lambda item: -item[1][2])]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--uploads-dir", type=Path, action="append", default=[])
    parser.add_argument("--scratchpad-dir", type=Path, action="append", default=[])
    parser.add_argument("--transcript", type=Path, action="append", default=[])
    parser.add_argument("--exclude", action="append", default=[], help="a further directory-name pattern to leave out")
    parser.add_argument("--max-archive-mb", type=float, default=30.0)
    parser.add_argument("--max-scratchpad-file-mb", type=float, default=25.0)
    parser.add_argument("--output-dir", type=Path, default=Path("session_archives"))
    parser.add_argument("--archive-stem", default="session_archive")
    parser.add_argument("--dry-run", action="store_true")
    arguments = parser.parse_args()

    max_archive_bytes = int(arguments.max_archive_mb * 1_000_000)
    excluded = DEFAULT_EXCLUDED_DIRECTORY_PATTERNS + tuple(arguments.exclude)
    members = collect_members(arguments.uploads_dir, arguments.transcript, arguments.scratchpad_dir, excluded,
                              int(arguments.max_scratchpad_file_mb * 1_000_000), max_archive_bytes)
    bins = pack_first_fit_decreasing(members, max_archive_bytes)
    for line in summary_lines(members):
        print(line)
    print(f"{len(members)} members in {len(bins)} archives of at most {arguments.max_archive_mb:g} MB")
    if arguments.dry_run:
        return
    written = write_archives(bins, arguments.output_dir, arguments.archive_stem, max_archive_bytes)
    archive_of_member = {member.archive_name: path.name for path, members_in in zip(written, bins) for member in members_in}
    with open(arguments.output_dir / INDEX_NAME, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["archive", "archive_name", "category", "original_size_bytes", "sha256_of_whole_file"])
        for member in sorted(members, key=lambda each: each.archive_name):
            writer.writerow([archive_of_member[member.archive_name], member.archive_name, member.category,
                             member.original_size, member.sha256])
    for path in written:
        print(f"{path}\t{path.stat().st_size / 1e6:.2f} MB")


if __name__ == "__main__":
    main()
