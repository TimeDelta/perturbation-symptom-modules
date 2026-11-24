"""Keep the study sheet's diagrams current with the decisions and the code they depict (the owner, 5 November 2026).

The owner's study sheet is a Claude Docs document outside the repository, so nothing here reads it. What the
repository holds is configs/study_sheet_diagrams.json: one entry per diagram, with the decision rows of
docs/open_decisions.md and the code files it depicts, and a SHA-256 of each, taken when a session last checked the
diagram against them. tests/test_study_sheet_diagrams_current.py fails while any of those has changed since, so a
commit that changes a depicted decision or file does not pass the suite until the diagram is checked, corrected in the
doc where it is wrong, and re-stamped here.

Each diagram shows one of two states, as the owner asked ("there has to be two versions. The most recently built and
according to set decisions"): "built", the code and graph as last built, or "decided", the architecture once every
ruled decision is built. Where the two agree, or where one diagram draws the decided changes over the built picture
(dashed, and said so in its key), that diagram is "built_and_decided"; otherwise the diagram has a partner of the other
state, named in "partner". Diagrams that are dated records (a plan of one day, a measurement on a named graph) are
listed under "records" with the date they stand for; they are not checked against the decisions, since a record is
not revised to match a later one.

A fingerprint says that something changed, not that the diagram is wrong: a dated addition to a row changes its hash.
Re-stamping is the record that a session looked and found the diagram right, or corrected it first.

Since 24 November 2026 the guard has two more kinds of entry and one more kind of depicted thing, because the guard
had missed the pipeline diagrams: they drew the encoder but declared none of the encoder's decisions, so item 37f
changed what they show and nothing flagged them (the owner: "the first architecture diagram shows it so it's not
just the prose and the existing test failed"). The guard checks only what an entry declares, so an entry lists
everything its diagram or passage depicts.
- "passages": prose of the study sheet that describes the architecture, keyed by the block id of its paragraph,
  table or list, checked and stamped like a diagram (the owner, 24 November 2026, extending the rule to the prose:
  "2 yes"). A passage has no state or partner: prose says in its own words which state it describes.
- "items" in `depicts`: amendment items of docs/preregistration.md by id ("37f", "38"), fingerprinted by the
  item's own text, so a diagram can depict one registered ruling without going stale at every amendment, as
  depicting the whole file does.

Usage:
  PYTHONPATH=. python experiments/check_study_sheet_diagrams.py               # report what is out of date
  PYTHONPATH=. python experiments/check_study_sheet_diagrams.py --stamp ID    # after checking diagram ID (widget id)
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = REPOSITORY_ROOT / "configs" / "study_sheet_diagrams.json"
DECISION_LOG_PATH = REPOSITORY_ROOT / "docs" / "open_decisions.md"
REGISTRATION_PATH = REPOSITORY_ROOT / "docs" / "preregistration.md"
ENTRY_SECTIONS = ("diagrams", "passages")
# An amendment item's heading, `**37f. ...` or, for a sub-item added later inside a bullet, `- **23a. ...`, the form
# mechanistic_pathway_learning.documentation.item_ids_in_registration reads.
ITEM_HEADING = re.compile(r"^(?:- )?\*\*(?P<id>\d+[a-z]?)\.\s")
# What ends an item besides the next item's heading: the next amendment's date line, or the file's closing paragraph.
ITEM_END = re.compile(r"^(?:Amendment, |To fill in:)")
STATES = ("built", "decided", "built_and_decided")


def sha256_of_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def decision_row_text(decision_id: str, log_text: str | None = None) -> str:
    """The one physical line of the decision log that holds this decision's row, struck through or not."""
    log_text = DECISION_LOG_PATH.read_text(encoding="utf-8") if log_text is None else log_text
    row_pattern = re.compile(rf"^\| (?:~~)?{re.escape(decision_id)}(?:~~)? \|")
    rows = [line for line in log_text.splitlines() if row_pattern.match(line)]
    if len(rows) != 1:
        raise ValueError(f"decision {decision_id}: {len(rows)} rows in {DECISION_LOG_PATH.name}, expected 1")
    return rows[0]


def registration_item_text(item_id: str, registration_text: str | None = None) -> str:
    """An amendment item's text, from its heading line to the next item's heading, the next amendment's date line or
    the file's closing paragraph. Item 37's own text is its preamble; 37a to 37o are items of their own."""
    registration_text = REGISTRATION_PATH.read_text(encoding="utf-8") if registration_text is None else registration_text
    lines = registration_text.splitlines()
    starts = [index for index, line in enumerate(lines) if (match := ITEM_HEADING.match(line)) and match.group("id") == item_id]
    if len(starts) != 1:
        raise ValueError(f"amendment item {item_id}: {len(starts)} headings in {REGISTRATION_PATH.name}, expected 1")
    end = len(lines)
    for index in range(starts[0] + 1, len(lines)):
        if ITEM_HEADING.match(lines[index]) or ITEM_END.match(lines[index]):
            end = index
            break
    return "\n".join(lines[starts[0]:end])


def current_fingerprints(depicts: dict) -> dict[str, str]:
    """{"decision:9.112": sha256, "item:37f": sha256, "file:path": sha256} for what a diagram or passage depicts, as
    the working tree holds it."""
    log_text = DECISION_LOG_PATH.read_text(encoding="utf-8")
    fingerprints = {}
    for decision_id in depicts.get("decisions", []):
        fingerprints[f"decision:{decision_id}"] = sha256_of_text(decision_row_text(decision_id, log_text))
    if depicts.get("items"):
        registration_text = REGISTRATION_PATH.read_text(encoding="utf-8")
        for item_id in depicts["items"]:
            fingerprints[f"item:{item_id}"] = sha256_of_text(registration_item_text(item_id, registration_text))
    for relative_path in depicts.get("files", []):
        path = REPOSITORY_ROOT / relative_path
        if not path.is_file():
            raise FileNotFoundError(f"{relative_path} is named by configs/study_sheet_diagrams.json and does not exist")
        fingerprints[f"file:{relative_path}"] = hashlib.sha256(path.read_bytes()).hexdigest()
    return fingerprints


def read_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def registry_problems(registry: dict) -> list[str]:
    """Shape errors: a state that is not one of STATES, a partner missing or not pointing back, a differing pair."""
    problems = []
    diagrams = registry["diagrams"]
    for widget_id, entry in diagrams.items():
        state = entry.get("state")
        if state not in STATES:
            problems.append(f"{widget_id}: state {state!r} is not one of {STATES}")
        partner = entry.get("partner")
        if state == "built_and_decided":
            if partner:
                problems.append(f"{widget_id}: a diagram showing both states has no partner, but names {partner}")
            continue
        if not partner:
            problems.append(f"{widget_id}: a {state} diagram needs its partner of the other state")
        elif partner not in diagrams:
            problems.append(f"{widget_id}: partner {partner} is not in the registry")
        else:
            other = diagrams[partner]
            if other.get("partner") != widget_id:
                problems.append(f"{widget_id}: partner {partner} does not name it back")
            if {state, other.get("state")} != {"built", "decided"}:
                problems.append(f"{widget_id}: a pair is one built and one decided diagram, not {state} and {other.get('state')}")
    for block_id, entry in registry.get("passages", {}).items():
        if "state" in entry or "partner" in entry:
            problems.append(f"{block_id}: a passage says in its own words which state it describes, so it has no state or partner")
        if not any(entry.get("depicts", {}).get(kind) for kind in ("decisions", "items", "files")):
            problems.append(f"{block_id}: a passage depicts at least one decision, amendment item or file")
    shared = set(registry["diagrams"]) & set(registry.get("passages", {}))
    problems += [f"{entry_id}: listed both as a diagram and as a passage" for entry_id in sorted(shared)]
    return problems


def stale_items(entry: dict) -> list[str]:
    """What a diagram depicts that changed since it was stamped (or was never stamped)."""
    recorded = entry.get("fingerprints", {})
    now = current_fingerprints(entry.get("depicts", {}))
    changed = [key for key, value in now.items() if recorded.get(key) != value]
    dropped = [key for key in recorded if key not in now]
    return changed + [f"{key} (no longer depicted; stamp again)" for key in dropped]


def head_commit() -> str:
    completed = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPOSITORY_ROOT, capture_output=True, text=True)
    return completed.stdout.strip() or "unknown"


def entries(registry: dict):
    """(section, id, entry) for every checked diagram and passage."""
    for section in ENTRY_SECTIONS:
        for entry_id, entry in registry.get(section, {}).items():
            yield section, entry_id, entry


def stamp(widget_id: str) -> None:
    """Record that the diagram (by widget id) or passage (by block id) was checked against what it depicts now."""
    registry = read_registry()
    sections = [section for section in ENTRY_SECTIONS if widget_id in registry.get(section, {})]
    if not sections:
        raise SystemExit(f"{widget_id} is not in {REGISTRY_PATH.relative_to(REPOSITORY_ROOT)}")
    entry = registry[sections[0]][widget_id]
    entry["fingerprints"] = current_fingerprints(entry.get("depicts", {}))
    entry["checked"] = datetime.date.today().isoformat()
    entry["checked_at_commit"] = head_commit()
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"stamped {widget_id} ({entry.get('title', '')}) at {entry['checked_at_commit']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--stamp", metavar="ID", help="record that this diagram (widget id) or passage (block id) was checked "
                                                     "against what it depicts now")
    arguments = parser.parse_args()
    if arguments.stamp:
        stamp(arguments.stamp)
        return 0
    registry = read_registry()
    problems = registry_problems(registry)
    for section, entry_id, entry in entries(registry):
        for item in stale_items(entry):
            problems.append(f"{entry_id} ({entry.get('title', '')}): {item} changed since it was checked")
    print("\n".join(problems) if problems else "every study-sheet diagram and passage is current with what it depicts")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
