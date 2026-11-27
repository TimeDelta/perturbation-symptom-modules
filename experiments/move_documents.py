"""Move files under docs/ to the place the placement rule gives them, one phase of configs/moved_paths.json at a time
(20 November 2026, after the owner called docs/ "insanely bloated"; docs/documentation_process.md, "Where documents
live", states the rule and its exceptions).

What --apply does, in order:
  1. renames each planned file of the phase with `git mv`, its name unchanged;
  2. rewrites the references that must name the new path: code, scripts, tests, YAML configs, living documents,
     drafts and the bibliography. Each whole old path is replaced by the new one, with a boundary check so that
     docs/x.md does not match inside docs/x_v2.md, and a relative Markdown link that resolves to an old path is
     pointed at the new one;
  3. renames the moved documents' keys in configs/documentation_registry.json where they stand, and gives each
     generated page that names an old path an allowance in its `names_absent_paths` until its generator writes the
     new path (a generated page is never edited by hand);
  4. records the moves in configs/moved_paths.json with the date;
  5. stages all of it and checks it: git shows every moved file as a pure rename (R100), no record and no frozen file
     changed, and no old path is left in code, YAML configs, living documents, drafts or the bibliography.

What it leaves as written, and lists: records (the decision log among them), the frozen baseline, the tables and
quotations under configs/ other than YAML (a provenance column records where a row came from, as a record does), the
immutable releases under data/, the TOPICS rules of the docs index (TOPIC_RULE_SOURCES: they name a document without
its class directory on purpose), and the moved files themselves. A moved file is never edited in the commit that moves
it, so that commit stays a set of pure renames; a moved draft that names another moved file is listed, for an edit in
a commit of its own after the move. The pages the generators write (docs/README.md, docs/file_index.md,
docs/status.md) are regenerated after it, by the generators CLAUDE.md lists under Documents.

Without --apply it is a dry run: it prints every rename, register change and rewritten line, every reference it
leaves as written (by kind), and every bare file name or directory a source writes without the moved path (a path
assembled at run time, or a name without its directory), for a hand edit; it changes nothing. It refuses, changing
nothing, when the clone is shallow, a destination exists, a source is not tracked, a file it would move or edit has
uncommitted changes, a moved Markdown document is not registered, or a relative link would break.

Usage, from the repository root:
  PYTHONPATH=. python experiments/move_documents.py --phase 1                 # dry run
  PYTHONPATH=. python experiments/move_documents.py --phase 1 --apply         # move, rewrite, record, stage, check
  PYTHONPATH=. python experiments/move_documents.py --phase 2 --only docs/a.md --apply   # one planned file of a phase
"""
from __future__ import annotations

import argparse
import collections
import json
import posixpath
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from mechanistic_pathway_learning.documentation import (
    MARKDOWN_LINK,
    REPOSITORY_ROOT,
    TOPIC_RULE_SOURCES,
    git_output,
    load_moved_paths,
    moved_paths_text,
    referenced_repository_paths,
    registry_text,
    renamed_in_place,
    repository_is_shallow,
    whole_path_pattern,
)

# Pages a generator rewrites whole after the move; their references are regenerated, not edited.
REGENERATED = ("docs/README.md", "docs/file_index.md", "docs/status.md")
REGISTRY = "configs/documentation_registry.json"
MOVED_PATHS = "configs/moved_paths.json"
CODE_ROOTS = ("experiments/", "mechanistic_pathway_learning/", "scripts/", "tests/", "slurm/", ".claude/")
BINARY_SUFFIXES = (".png", ".jpg", ".jpeg", ".pdf", ".parquet", ".gz", ".zip", ".xlsx", ".h5", ".h5ad", ".pt", ".npz", ".pkl")
# The kinds of source (source_kind) whose references are rewritten; a generated page gets an allowance instead, and
# every other kind (record, frozen, a table or quotation under configs/, a release, a data file under docs/, the topic
# rules) is left as written.
EDITED = ("code", "yaml config", "living", "draft", "bibliography")
HTML_LINK = re.compile(r"(?:src|href)=\"(?P<target>[^\"#]+)\"")


def source_kind(path: str, registry: dict) -> str:
    """How a file that names a moved path is treated: edited, given an allowance, regenerated, or left as written."""
    if path in REGENERATED:
        return "regenerated"
    if path == REGISTRY:
        return "register"
    if path == MOVED_PATHS:
        return "moved paths"
    if path in TOPIC_RULE_SOURCES:
        return "topic rules"
    if path.startswith(CODE_ROOTS):
        return "code"
    if path.startswith("configs/"):
        return "yaml config" if path.endswith((".yaml", ".yml")) else "configs table or quotation"
    if path.startswith("data/"):
        return "release"
    if path == "docs/references.bib":
        return "bibliography"
    entry = registry.get(path)
    if entry is not None:
        return entry["class"]
    if path.startswith("docs/"):
        return "docs data file"
    return "code"


@dataclass
class Plan:
    moves: list[dict]
    renames: dict[str, str]                                   # old path -> new path, every file of the phase
    edits: dict[str, list[tuple[int, str, str]]] = field(default_factory=dict)       # source -> (line, before, after)
    allowances: dict[str, dict[str, str]] = field(default_factory=dict)              # register key -> {old path: why}
    key_renames: dict[str, str] = field(default_factory=dict)                        # register key -> new key
    left: dict[str, list[tuple[str, int, str]]] = field(default_factory=lambda: collections.defaultdict(list))  # kind -> (source, line, old)
    by_hand: list[tuple[str, int, str]] = field(default_factory=list)                # (source, line, what)
    after_the_move: list[tuple[str, int, str]] = field(default_factory=list)         # moved drafts naming moved paths
    refusals: list[str] = field(default_factory=list)


def tracked_files(root: Path) -> list[str]:
    return [line for line in git_output("ls-files", cwd=root).splitlines() if line]


def uncommitted(paths: list[str], root: Path) -> list[str]:
    if not paths:
        return []
    changed = []
    for start in range(0, len(paths), 200):
        status = git_output("status", "--porcelain", "--", *paths[start:start + 200], cwd=root)
        changed.extend(line[3:].split(" -> ")[-1] for line in status.splitlines() if line.strip())
    return changed


def relative_link_rewrites(line: str, source: str, renames: dict[str, str]) -> tuple[str, list[str]]:
    """The line with every relative link that resolves to an old path pointed at the new one, and the old paths."""
    found = []

    def rewrite(match: re.Match, group: str) -> str:
        target = match.group(group)
        if re.match(r"[a-z]+:", target) or target.startswith(("#", "/")):
            return match.group(0)
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source), target))
        if resolved not in renames:
            return match.group(0)
        found.append(resolved)
        new_target = posixpath.relpath(renames[resolved], posixpath.dirname(source) or ".")
        start, end = match.span(group)
        whole_start = match.start(0)
        text = match.group(0)
        return text[: start - whole_start] + new_target + text[end - whole_start:]

    line = MARKDOWN_LINK.sub(lambda match: rewrite(match, "target"), line)
    line = HTML_LINK.sub(lambda match: rewrite(match, "target"), line)
    return line, found


def unhandled_names(line: str, source: str, by_name: dict[str, list[str]], renames: dict[str, str], name_pattern: re.Pattern) -> list[str]:
    """What a line still says about a moved file once its whole paths and links are rewritten: a bare name, a path
    written relative to some directory, or an old path behind a prefix the whole-path rule does not rewrite
    (`../docs/x.md`). Each is for a hand edit or a look; a bare name still finds the file, since names do not change."""
    found = []
    new_paths = set(renames.values())
    for match in name_pattern.finditer(line):
        name = match.group(1)
        token = re.search(r"[A-Za-z0-9_./\-]*$", line[: match.start()]).group(0) + name
        if token in new_paths or any(token.endswith("/" + path) for path in new_paths if path.endswith("/" + name)):
            continue
        olds = by_name[name]
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source), token)) if "/" in token else None
        if resolved is not None and resolved in new_paths:
            continue  # a relative link already pointed at the new place
        if token == name:
            found.append(f"names {name} without its directory")
        elif any(token.endswith(old) for old in olds):
            found.append(f"names {token}, an old path behind a prefix it does not rewrite")
        elif resolved in olds or posixpath.normpath(posixpath.join("docs", token)) in olds:
            found.append(f"names {token}, a path relative to its directory or to docs/")
        else:
            found.append(f"names {token}")
    return found


def plan_phase(phase: int, root: Path = REPOSITORY_ROOT, only: list[str] | None = None, today: date | None = None) -> Plan:
    moved = load_moved_paths(root / MOVED_PATHS)
    moves = [entry for entry in moved["planned"] if entry["phase"] == phase and (not only or entry["from"] in only)]
    plan = Plan(moves, {entry["from"]: entry["to"] for entry in moves})
    if only:
        plan.refusals += [f"{path} is not planned for phase {phase} in {MOVED_PATHS}" for path in sorted(set(only) - set(plan.renames))]
    if not moves:
        plan.refusals.append(f"no planned move of phase {phase} in {MOVED_PATHS}")
        return plan
    registry = json.loads((root / REGISTRY).read_text(encoding="utf-8"))["documents"]
    tracked = tracked_files(root)
    tracked_set = set(tracked)
    renames = plan.renames
    day = (today or date.today()).isoformat()

    if repository_is_shallow(root):
        plan.refusals.append("the clone is shallow; run `git fetch --depth=1000 origin main` first")
    for old, new in renames.items():
        if old not in tracked_set:
            plan.refusals.append(f"{old} is not tracked")
        if (root / new).exists():
            plan.refusals.append(f"{new} exists already")
        if old.endswith(".md"):
            if old in registry:
                plan.key_renames[old] = new
            else:
                plan.refusals.append(f"{old} is a Markdown document the register does not name")

    patterns = {old: whole_path_pattern(old) for old in renames}
    by_name: dict[str, list[str]] = collections.defaultdict(list)
    for old in renames:
        by_name[posixpath.basename(old)].append(old)
    name_pattern = re.compile(r"(?<![A-Za-z0-9_\-])(" + "|".join(re.escape(name) for name in sorted(by_name, key=len, reverse=True)) + r")(?![A-Za-z0-9_\-])")
    # a folder every file of which moves (as docs/exposure_sources did whole in phase 2, 27 November 2026), as a source
    # may name it whole
    folders = {posixpath.dirname(old) for old in renames if posixpath.dirname(old) != "docs"}
    folders = sorted(folder for folder in folders if all(path in renames for path in tracked if path.startswith(folder + "/")))
    folder_pattern = re.compile(r"(?<![A-Za-z0-9_\-./])(" + "|".join(re.escape(folder) for folder in folders) + r")(?![A-Za-z0-9_\-.])") if folders else None

    for source in tracked:
        if source.endswith(BINARY_SUFFIXES) or source == MOVED_PATHS:
            continue
        try:
            text = (root / source).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue
        if not name_pattern.search(text) and not (folder_pattern and folder_pattern.search(text)):
            continue
        kind = source_kind(source, registry)
        if kind in ("regenerated", "register"):
            continue
        moving = source in renames
        is_markdown = source.endswith((".md", ".html"))
        named = referenced_repository_paths(text) if kind == "generated" else set()
        for number, line in enumerate(text.splitlines(), start=1):
            hits = [old for old, pattern in patterns.items() if posixpath.basename(old) in line and pattern.search(line)]
            rewritten, link_hits = line, []
            if is_markdown:
                rewritten, link_hits = relative_link_rewrites(line, source, renames)
            for old in hits:
                rewritten = patterns[old].sub(renames[old], rewritten)
            if kind in EDITED:
                for what in unhandled_names(rewritten, source, by_name, renames, name_pattern):
                    plan.by_hand.append((source, number, f"{kind}: {what}"))
                if folder_pattern:
                    for match in folder_pattern.finditer(rewritten):
                        plan.by_hand.append((source, number, f"{kind}: names the folder {match.group(1)}, every file of which moves"))
            if not hits and not link_hits:
                continue
            if kind in EDITED and moving:
                plan.after_the_move.append((renames[source], number, ", ".join(sorted(set(hits + link_hits)))))
            elif kind in EDITED:
                plan.edits.setdefault(source, []).append((number, line, rewritten))
            elif kind == "generated":
                key = plan.key_renames.get(source, source)
                for old in sorted(set(hits) & named):
                    plan.allowances.setdefault(key, {})[old] = allowance_reason(renames[old], day)
                plan.refusals += [f"{source}:{number} links to {old} relatively; a generated page is not edited by hand, so the link would break"
                                  for old in link_hits]
            else:
                plan.left[kind] += [(source, number, old) for old in sorted(set(hits + link_hits))]
                if link_hits and kind in ("record", "frozen"):
                    plan.refusals.append(f"{source}:{number} links to {', '.join(link_hits)} relatively; a {kind} is not edited, so the link would break")
    # a moved document is not edited, so its own relative links must still resolve from its new directory
    for old, new in renames.items():
        if not old.endswith((".md", ".html")) or posixpath.dirname(old) == posixpath.dirname(new):
            continue
        for number, line in enumerate((root / old).read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            for match in list(MARKDOWN_LINK.finditer(line)) + list(HTML_LINK.finditer(line)):
                target = match.group("target")
                if re.match(r"[a-z]+:", target) or target.startswith(("#", "/")):
                    continue
                resolved = posixpath.normpath(posixpath.join(posixpath.dirname(old), target))
                if posixpath.normpath(posixpath.join(posixpath.dirname(new), target)) != renames.get(resolved, resolved):
                    plan.refusals.append(f"{old}:{number} links to {target}, which would not resolve from {posixpath.dirname(new)}/")
    dirty = uncommitted(sorted(set(renames) | set(plan.edits) | {REGISTRY, MOVED_PATHS}), root)
    plan.refusals += [f"{path} has uncommitted changes; commit or set them aside first" for path in dirty]
    return plan


def allowance_reason(new: str, day: str) -> str:
    return (f"moved to `{new}` on {day} (configs/moved_paths.json); this page predates the move and is not regenerated in "
            "the move commit, so it names the old path until its generator writes it again")


def report(plan: Plan, phase: int) -> str:
    lines = [f"phase {phase}: {len(plan.moves)} files"]
    for entry in plan.moves:
        lines.append(f"  git mv {entry['from']} {entry['to']}")
    lines.append(f"register keys renamed in place: {len(plan.key_renames)}")
    lines.append(f"allowances (names_absent_paths) for generated pages: {sum(len(v) for v in plan.allowances.values())} on {len(plan.allowances)} pages")
    for key, allowed in sorted(plan.allowances.items()):
        lines.append(f"  {key}: {', '.join(sorted(allowed))}")
    lines.append(f"lines rewritten: {sum(len(v) for v in plan.edits.values())} in {len(plan.edits)} files")
    for source, edits in sorted(plan.edits.items()):
        for number, before, after in edits:
            lines.append(f"  {source}:{number}")
            lines.append(f"    - {before.strip()[:240]}")
            lines.append(f"    + {after.strip()[:240]}")
    lines.append("left as written, by kind:")
    for kind, rows in sorted(plan.left.items()):
        lines.append(f"  {kind}: {len(rows)} lines in {len({source for source, _, _ in rows})} files ({', '.join(sorted({source for source, _, _ in rows})[:12])})")
    lines.append(f"moved drafts and living documents that name a moved path, to edit after the move commit: {len(plan.after_the_move)}")
    for source, number, olds in plan.after_the_move:
        lines.append(f"  {source}:{number}: {olds}")
    lines.append(f"for a hand edit or a look (bare names, assembled paths, folders): {len(plan.by_hand)}")
    for source, number, what in plan.by_hand:
        lines.append(f"  {source}:{number}: {what[:260]}")
    if plan.refusals:
        lines.append("REFUSED:")
        lines += [f"  {why}" for why in plan.refusals]
    return "\n".join(lines)


def apply_plan(plan: Plan, root: Path = REPOSITORY_ROOT, today: date | None = None) -> list[str]:
    """Do the moves and edits, record and stage them, and return what the checks found wrong (nothing, when right)."""
    day = (today or date.today()).isoformat()
    for entry in plan.moves:
        (root / entry["to"]).parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "mv", entry["from"], entry["to"]], cwd=root, check=True)
    # a folder whose every file moved is left empty on disk by git mv; remove it, up to docs/ itself
    for entry in plan.moves:
        folder = (root / entry["from"]).parent
        while folder != root / "docs" and folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()
            folder = folder.parent
    for source, edits in plan.edits.items():
        path = root / source
        lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        for number, before, after in edits:
            assert lines[number - 1].rstrip("\r\n") == before, f"{source}:{number} changed under the plan"
            ending = lines[number - 1][len(lines[number - 1].rstrip("\r\n")):]
            lines[number - 1] = after + ending
        path.write_text("".join(lines), encoding="utf-8")
    registry_path = root / REGISTRY
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    registry["documents"] = renamed_in_place(registry["documents"], plan.key_renames)
    for key, allowed in plan.allowances.items():
        entry = registry["documents"][key]
        entry.setdefault("names_absent_paths", {}).update(allowed)
    registry_path.write_text(registry_text(registry), encoding="utf-8")
    moved_path = root / MOVED_PATHS
    moved = load_moved_paths(moved_path)
    made = {entry["from"] for entry in plan.moves}
    moved["planned"] = [entry for entry in moved["planned"] if entry["from"] not in made]
    moved["moves"] += [{"from": entry["from"], "to": entry["to"], "date": day, "phase": entry["phase"]} for entry in plan.moves]
    moved_path.write_text(moved_paths_text(moved), encoding="utf-8")
    subprocess.run(["git", "add", "--", REGISTRY, MOVED_PATHS, *plan.edits], cwd=root, check=True)
    return check_staged(plan, root)


def check_staged(plan: Plan, root: Path = REPOSITORY_ROOT) -> list[str]:
    problems = []
    status = git_output("diff", "--cached", "-M100%", "--name-status", cwd=root).splitlines()
    pure = {tuple(line.split("\t")[1:]) for line in status if line.startswith("R100\t")}
    for entry in plan.moves:
        if (entry["from"], entry["to"]) not in pure:
            problems.append(f"{entry['from']} -> {entry['to']} is not staged as a pure rename (R100)")
    registry = json.loads((root / REGISTRY).read_text(encoding="utf-8"))["documents"]
    for line in status:
        fields = line.split("\t")
        if fields[0].startswith("R100"):
            continue
        for path in fields[1:]:
            if registry.get(path, {}).get("class") in ("record", "frozen"):
                problems.append(f"{path} is a {registry[path]['class']} and changed in the move ({fields[0]})")
    patterns = {old: whole_path_pattern(old) for old in plan.renames}
    for source in tracked_files(root):
        kind = source_kind(source, registry)
        if kind not in EDITED or source in plan.renames.values() or source.endswith(BINARY_SUFFIXES):
            continue
        try:
            text = (root / source).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        for old, pattern in patterns.items():
            if posixpath.basename(old) in text and pattern.search(text):
                problems.append(f"{source} ({kind}) still names {old}")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--phase", type=int, required=True)
    parser.add_argument("--only", nargs="+", help="move only these planned files of the phase (their old paths)")
    parser.add_argument("--apply", action="store_true", help="move, rewrite, record and stage; without it, a dry run")
    arguments = parser.parse_args()
    plan = plan_phase(arguments.phase, only=arguments.only)
    print(report(plan, arguments.phase))
    if plan.refusals:
        return 1
    if not arguments.apply:
        print("\ndry run: nothing was changed; pass --apply to make the moves")
        return 0
    problems = apply_plan(plan)
    if problems:
        print("\nCHECKS FAILED after staging (nothing was committed):")
        print("\n".join(f"  {problem}" for problem in problems))
        return 1
    print(f"\nmoved and staged {len(plan.moves)} files; every move is a pure rename and no record or frozen file changed. "
          "Next: the hand edits the list above names, the generators CLAUDE.md lists under Documents, the full suite, the commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
