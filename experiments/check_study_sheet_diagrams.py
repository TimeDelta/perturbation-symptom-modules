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


def current_fingerprints(depicts: dict) -> dict[str, str]:
    """{"decision:9.112": sha256, "file:path": sha256} for what a diagram depicts, as the working tree holds it."""
    log_text = DECISION_LOG_PATH.read_text(encoding="utf-8")
    fingerprints = {}
    for decision_id in depicts.get("decisions", []):
        fingerprints[f"decision:{decision_id}"] = sha256_of_text(decision_row_text(decision_id, log_text))
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


def stamp(widget_id: str) -> None:
    registry = read_registry()
    if widget_id not in registry["diagrams"]:
        raise SystemExit(f"{widget_id} is not in {REGISTRY_PATH.relative_to(REPOSITORY_ROOT)}")
    entry = registry["diagrams"][widget_id]
    entry["fingerprints"] = current_fingerprints(entry.get("depicts", {}))
    entry["checked"] = datetime.date.today().isoformat()
    entry["checked_at_commit"] = head_commit()
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"stamped {widget_id} ({entry.get('title', '')}) at {entry['checked_at_commit']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--stamp", metavar="WIDGET_ID", help="record that this diagram was checked against what it depicts now")
    arguments = parser.parse_args()
    if arguments.stamp:
        stamp(arguments.stamp)
        return 0
    registry = read_registry()
    problems = registry_problems(registry)
    for widget_id, entry in registry["diagrams"].items():
        for item in stale_items(entry):
            problems.append(f"{widget_id} ({entry.get('title', '')}): {item} changed since it was checked")
    print("\n".join(problems) if problems else "every study-sheet diagram is current with what it depicts")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
