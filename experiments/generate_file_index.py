"""Generate docs/file_index.md: every file git tracks under docs/, what it is, and what reads it.

Why this exists beside docs/README.md. That page is the index of *registered documents* by topic, and the register
covers tracked Markdown only (`configs/documentation_registry.json`, and `tests/test_documentation_process.py`
fails for a tracked Markdown document that is not registered). On 2 November 2026 git tracked 241 files under docs/,
of which 180 are Markdown, so **61 files had no index anywhere**: the figures the explanatory-figure script writes, the
curated CSV tables the graph build reads, the measurement JSON that decisions quote, the bibliography, one prompt and
one study sheet in HTML. A reader looking for `docs/curated_oxidant_targets.csv` found it by knowing it was there.

So this page lists everything, and for each file says the one thing a reader most needs: for a Markdown document, the
class the register gives it, which is how far to trust it as a statement of the current state; and for every other
file, which scripts and modules name it, so a data file that nothing reads is visible as such rather than looking
load-bearing. The "read by" column is a textual search for the file's path in the repository's own Python and shell
sources, so it finds a file named in a default argument or a constant, and it does not find one built up from parts at
run time; the page says so rather than implying the list is exhaustive.

It is generated, not written, for the reason docs/README.md is: a hand-kept list of 241 files goes stale on the first
commit that adds one. Nothing here is a judgement about a file, only what the register and the sources say about it.

Since the reorganization of 20 November 2026 the page also says where the files are (a count per directory) and
prints configs/moved_paths.json: every move made, old path, new path and date, so that an old path a record, the
decision log or the frozen baseline still writes leads to the file; and every move planned, with its phase.

Usage, from the repository root:
  PYTHONPATH=. python experiments/generate_file_index.py            # writes docs/file_index.md
  PYTHONPATH=. python experiments/generate_file_index.py --check    # fails if the committed file is out of date
"""
from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

from mechanistic_pathway_learning.documentation import git_output, load_moved_paths, provenance_stamp

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPOSITORY_ROOT / "configs" / "documentation_registry.json"
DEFAULT_OUTPUT_PATH = REPOSITORY_ROOT / "docs" / "file_index.md"
MOVED_PATHS_PATH = REPOSITORY_ROOT / "configs" / "moved_paths.json"
# where a reference to a docs/ file would be written: the repository's own executable sources
SOURCE_DIRECTORIES = ("experiments", "mechanistic_pathway_learning", "scripts", "tests")
KINDS = {".md": "Markdown documents", ".csv": "Tables (CSV)", ".json": "Measurements and summaries (JSON)",
          ".png": "Figures (PNG)", ".svg": "Figures (SVG)", ".bib": "Bibliography", ".txt": "Plain text",
          ".html": "HTML"}


def tracked_docs_files() -> list[str]:
    """Every path git tracks under docs/, sorted."""
    return sorted(line for line in git_output("ls-files", "docs").splitlines() if line)


def source_text() -> str:
    """Every Python and shell source of the repository, concatenated once, to search for file references."""
    chunks = []
    this_script = Path(__file__).resolve()
    for directory in SOURCE_DIRECTORIES:
        for path in sorted((REPOSITORY_ROOT / directory).rglob("*")):
            # this generator names example paths in its own documentation; a mention there is not a reader
            if path.resolve() == this_script:
                continue
            if path.suffix in (".py", ".sh") and path.is_file():
                chunks.append(f"\n<<<{path.relative_to(REPOSITORY_ROOT)}>>>\n" + path.read_text(encoding="utf-8", errors="replace"))
    return "".join(chunks)


def readers_of(path: str, sources: str) -> list[str]:
    """Which sources name this path. The search is textual, so it finds a path written whole and not one assembled at
    run time; the page states that limit."""
    readers = []
    for block in sources.split("\n<<<")[1:]:
        name, _, body = block.partition(">>>\n")
        if path in body:
            readers.append(name)
    return readers


def render_page(files: list[str], registry: dict, sources: str, moved: dict | None = None) -> str:
    stamp = provenance_stamp("experiments/generate_file_index.py",
                             inputs=["git ls-files docs", "configs/documentation_registry.json", "configs/moved_paths.json",
                                     "the repository's Python and shell sources"])
    moved = moved if moved is not None else {"moves": [], "planned": []}
    by_kind: dict[str, list[str]] = collections.defaultdict(list)
    for path in files:
        by_kind[KINDS.get(Path(path).suffix, "Other")].append(path)
    registered = registry["documents"]
    unregistered_markdown = [path for path in by_kind.get("Markdown documents", []) if path not in registered]

    lines = [
        "# Every file under docs/ (generated by experiments/generate_file_index.py — do not edit by hand)",
        "",
        stamp,
        "",
        f"All {len(files)} files git tracks under `docs/`, by kind. **This is the complete list; "
        "[docs/README.md](README.md) is the index of registered *documents* by topic**, and the register covers "
        "tracked Markdown only, so the files that are not Markdown appear here and nowhere else.",
        "",
        "For a Markdown document the class is the register's, and says how far to trust it as a statement of the "
        "current state (`docs/documentation_process.md` defines them). For every other file the last column names the "
        "scripts and modules that mention its path. **That search is textual**: it finds a path written whole, in a "
        "default argument or a constant, and it does not find one assembled at run time, so an empty cell means no "
        "source names the path and not that nothing reads the file.",
        "",
        "| kind | files |",
        "|---|---|",
    ]
    for kind in list(KINDS.values()) + ["Other"]:
        if by_kind.get(kind):
            lines.append(f"| {kind} | {len(by_kind[kind])} |")
    by_directory = collections.Counter(str(Path(path).parent) for path in files)
    lines += ["", "## Where the files are", "",
              "One row per directory, with the files git tracks directly in it (docs/documentation_process.md, \"Where documents live\", "
              "says which class goes where).", "", "| directory | files |", "|---|---|"]
    for directory in sorted(by_directory, key=lambda name: (name != "docs", name)):
        lines.append(f"| `{directory}/` | {by_directory[directory]} |")
    docs_registered = [path for path in registered if path.startswith("docs/")]
    lines += ["", f"The register holds {len(registered)} documents, of which {len(docs_registered)} are under `docs/` "
              f"and the rest are the repository's own `README.md` and `CLAUDE.md`. Tracked Markdown under `docs/` that "
              f"the register does not name: {len(unregistered_markdown)}"
              + (f" ({', '.join(f'`{path}`' for path in unregistered_markdown)})" if unregistered_markdown
                 else ", which is what tests/test_documentation_process.py requires") + ".", ""]

    for kind in list(KINDS.values()) + ["Other"]:
        paths = by_kind.get(kind)
        if not paths:
            continue
        lines += [f"## {kind} ({len(paths)})", ""]
        if kind == "Markdown documents":
            lines += ["| document | class | when |", "|---|---|---|"]
            for path in paths:
                entry = registered.get(path, {})
                klass = entry.get("class", "**not registered**")
                when = (entry.get("reviewed") and f"reviewed {entry['reviewed']}") or \
                       (entry.get("recorded") and f"recorded {entry['recorded']}") or \
                       (entry.get("generator") and f"written by `{entry['generator']}`") or ""
                # the link is the path relative to docs/, not the bare file name: a document in a subdirectory
                # (docs/generated/, docs/records/<YYYY-MM>/, docs/drafts/) would otherwise link to a sibling that is
                # not there, which tests/test_documentation_process.py::test_relative_links_in_every_document_resolve
                # fails on
                relative = path[len("docs/"):]
                lines.append(f"| [{relative}]({relative}) | {klass} | {when} |")
        else:
            lines += ["| file | named by |", "|---|---|"]
            for path in paths:
                readers = readers_of(path, sources)
                shown = ", ".join(f"`{reader}`" for reader in readers[:3])
                if len(readers) > 3:
                    shown += f" and {len(readers) - 3} more"
                relative = path[len("docs/"):]
                lines.append(f"| [{relative}]({relative}) | {shown} |")
        lines.append("")
    lines += moved_files_section(moved, set(files))
    return "\n".join(lines)


def link_or_path(path: str, files: set[str]) -> str:
    """A link from this page when the file is under docs/ and tracked, else the path as code."""
    if path.startswith("docs/") and path in files:
        relative = path[len("docs/"):]
        return f"[{relative}]({relative})"
    return f"`{path}`"


def moved_files_section(moved: dict, files: set[str]) -> list[str]:
    lines = ["## Moved files", "",
             "Every move of `configs/moved_paths.json`. A record, the decision log, the frozen baseline or a table's provenance column "
             "may still write the old path, as it was written; the new path is here, and the file's name did not change, so the name "
             "finds it too.", ""]
    if moved["moves"]:
        lines += ["| old path | new path | moved |", "|---|---|---|"]
        lines += [f"| `{entry['from']}` | {link_or_path(entry['to'], files)} | {entry['date']} |" for entry in moved["moves"]]
    else:
        lines.append("No file has moved yet.")
    if moved["planned"]:
        lines += ["", f"Planned and not yet made ({len(moved['planned'])}): phase 2 waits until no work in flight, and nothing awaiting the "
                  "owner, holds a file the move must edit; phase 3 holds the build inputs, moved just before a data-layer rebuild.", "",
                  "| path now | will move to | phase |", "|---|---|---|"]
        lines += [f"| {link_or_path(entry['from'], files)} | `{entry['to']}` | {entry['phase']} |" for entry in moved["planned"]]
    lines.append("")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--check", action="store_true",
                        help="write nothing and exit non-zero if the committed file differs from what would be "
                             "generated, so a stale index fails rather than misleads")
    arguments = parser.parse_args()

    files = tracked_docs_files()
    registry = json.loads(REGISTRY_PATH.read_text())
    rendered = render_page(files, registry, source_text(), load_moved_paths(MOVED_PATHS_PATH)) + "\n"

    if arguments.check:
        existing = arguments.output.read_text(encoding="utf-8") if arguments.output.exists() else ""

        def without_stamp(text: str) -> str:
            return "\n".join(line for line in text.splitlines() if not line.startswith("Generated by `"))

        if without_stamp(existing) != without_stamp(rendered):
            raise SystemExit(f"{arguments.output} is out of date; run PYTHONPATH=. python experiments/generate_file_index.py")
        print(f"{arguments.output} is up to date ({len(files)} files)")
        return
    arguments.output.write_text(rendered, encoding="utf-8")
    print(f"wrote {arguments.output}: {len(files)} files")


if __name__ == "__main__":
    main()
