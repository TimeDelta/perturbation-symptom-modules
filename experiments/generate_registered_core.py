"""Generate docs/registered_core.md: one entry per registered rule, with its value, its reason and where it is enforced.

Why this exists (the owner, 27 October 2026, on the project being the qualifying exam itself: "i just need to make
sure it doesn't go too far for me to be able to understand the project"). The examinable core of the project is
small - 12 rules in configs/registered_rules.json as of that date - while the justification for it is not: on the
same day docs/open_decisions.md held 154 rows and 424 KB of table, with 25 rows over 5,000 characters and a mean row
length that had grown from about 2,000 characters over ids 9.1 to 9.30 to about 6,700 over 9.96 to 9.102. A complete
record that no one re-reads is not a record anyone can defend, so this page is the short way in: every registered
value on one page, each with the decision that set it, so the long rows are read on purpose rather than swept.

It is generated, not written, for the reason the amendment history is: a hand-kept digest can claim a value the
configuration does not hold. This one cannot drift, because it has no content of its own. It states what
configs/registered_rules.json says and where the references in it resolve to; it adds no interpretation, which is
also why it is not a substitute for the registration or the decision log.

Three checks run while it is written, and each one appears on the page rather than only in the exit status:

  code_location resolves      every rule names a file that exists. A location may be a path, a path plus a flag, or
                              a module path with a symbol on the end (experiments/score_confirmatory.MINIMUM_POSITIVES_TO_SCORE),
                              which resolves to the module file.
  references resolve          every decision id a rule's text names is in docs/open_decisions.md and every amendment
                              item it names heads an item of docs/preregistration.md. CLAUDE.md: "A comment that
                              names a symbol, flag, file or decision id names one that exists."
  origin is traceable         every rule's text names a decision id, an amendment item or a dated registration. Six
                              of the twelve named neither a decision id nor an item on 27 October 2026
                              (floor_rule, robustness_models, bootstrap_unit, num_bootstrap,
                              minimum_positives_to_score, validation_fold_rule); each carries a date and, for
                              floor_rule, the owner's words. A rule whose origin is a date alone is listed as such
                              on the page, because "where did this value come from" is the question an examiner asks
                              and a date is a weaker answer than a decision row.

What this does not do. It does not say whether a value is right, whether it is the physiological choice or a
numerical one (CLAUDE.md requires a justification recorded with the decision when a numerical choice wins), or
whether the code still holds it. tests/test_registration_matches_the_code.py is what asserts the code; this page
asserts only that the registration is readable and its references land.

Usage:
  PYTHONPATH=. python experiments/generate_registered_core.py            # writes docs/registered_core.md
  PYTHONPATH=. python experiments/generate_registered_core.py --check    # fails if the committed file is out of date
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from mechanistic_pathway_learning.documentation import (
    ITEM_ID,
    decision_ids_in_log,
    decision_references,
    item_ids_in_registration,
    provenance_stamp,
    unresolved_decision_references,
    unresolved_item_references,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
REGISTERED_RULES_PATH = REPOSITORY_ROOT / "configs" / "registered_rules.json"
DECISION_LOG_PATH = REPOSITORY_ROOT / "docs" / "open_decisions.md"
REGISTRATION_PATH = REPOSITORY_ROOT / "docs" / "preregistration.md"
DEFAULT_OUTPUT_PATH = REPOSITORY_ROOT / "docs" / "registered_core.md"

# A trailing .SYMBOL on a module path, as in experiments/score_confirmatory.MINIMUM_POSITIVES_TO_SCORE: the file is
# the part before the symbol, with .py added. Only upper-case symbols are treated this way, so a real file name is
# never mistaken for one.
MODULE_SYMBOL = re.compile(r"^(?P<module>[\w/]+)\.(?P<symbol>[A-Z][A-Z0-9_]*)$")


def resolved_path(code_location: str) -> tuple[str, bool]:
    """(the path the location names, whether it exists). The first token is the path; a flag or prose may follow."""
    first_token = code_location.split()[0].rstrip(",")
    if (REPOSITORY_ROOT / first_token).exists():
        return first_token, True
    match = MODULE_SYMBOL.match(first_token)
    if match:
        module_file = match.group("module") + ".py"
        return module_file, (REPOSITORY_ROOT / module_file).exists()
    return first_token, False


def rendered_location(code_location: str) -> str:
    """The location as prose, with a module path and its symbol apart. A `module.SYMBOL` form written whole reads as a
    path that does not exist, which tests/test_documentation_process.py rightly fails
    (test_paths_named_by_living_and_generated_documents_exist), so the file is named as a file and the symbol beside
    it."""
    first_token = code_location.split()[0].rstrip(",")
    rest = code_location[len(first_token):].lstrip(" ,")
    match = MODULE_SYMBOL.match(first_token)
    if match and not (REPOSITORY_ROOT / first_token).exists():
        rendered = f"`{match.group('module')}.py`, symbol `{match.group('symbol')}`"
    else:
        rendered = f"`{first_token}`"
    return f"{rendered} {rest}".strip() if rest else rendered


def item_references(text: str) -> set[str]:
    return {match.group("id") for match in ITEM_ID.finditer(text)}


def dated_registration(text: str) -> str | None:
    """The date a rule's own text gives for its registration, for a rule that names no decision and no item."""
    match = re.search(r"((?:Registered|registered|Amended|amended|since)\s+\d{1,2}\s+\w+\s+\d{4})", text)
    return match.group(1) if match else None


def origin_of(rule_text: str) -> dict:
    decisions = sorted(decision_references(rule_text), key=lambda identifier: [int(part) for part in
                                                                              re.findall(r"\d+", identifier)])
    items = sorted(item_references(rule_text), key=lambda identifier: int(re.match(r"\d+", identifier).group()))
    return {"decisions": decisions, "items": items, "date": dated_registration(rule_text)}


def render_value(value) -> str:
    if isinstance(value, list):
        return ", ".join(f"`{entry}`" for entry in value)
    return f"`{value}`"


def render_page(rules: dict, known_decision_ids: set[str], known_items: set[str]) -> str:
    stamp = provenance_stamp("experiments/generate_registered_core.py",
                             inputs=["configs/registered_rules.json", "docs/open_decisions.md",
                                     "docs/preregistration.md"])
    origins = {name: origin_of(rule["means"]) for name, rule in rules.items()}
    untraced = [name for name, origin in origins.items() if not origin["decisions"] and not origin["items"]]
    missing_files = {name: resolved_path(rule["code_location"])[0] for name, rule in rules.items()
                     if not resolved_path(rule["code_location"])[1]}
    dangling_decisions = {name: unresolved_decision_references(rule["means"], known_decision_ids)
                          for name, rule in rules.items()
                          if unresolved_decision_references(rule["means"], known_decision_ids)}
    dangling_items = {name: unresolved_item_references(rule["means"], known_items)
                      for name, rule in rules.items()
                      if unresolved_item_references(rule["means"], known_items)}

    lines = [
        "# The registered core (generated by experiments/generate_registered_core.py — do not edit by hand)",
        "",
        stamp,
        "",
        f"Every registered rule of this project, {len(rules)} of them, with the value in force, the reason the "
        "configuration gives for it, the decisions and amendment items its text names and the code that holds it. "
        "This is the short way into the registration: it restates `configs/registered_rules.json` and resolves its "
        "references, and it adds nothing of its own, so where it is thin the configuration is thin. The references "
        "are the ones the rule's own text names, which can include an item the rule replaced rather than the one "
        "that set it: `membrane_potential_build` names item 13 because item 35 superseded it.",
        "",
        "`configs/registered_rules.json` is the single place each value is written; "
        "`tests/test_registration_matches_the_code.py` asserts the code still holds it; `docs/amendment_history.md` "
        "says how each value got there from `Amends:` trailers; `docs/preregistration.md` carries the hypotheses and "
        "the analyses these rules serve. This page says only what is registered now and where to read why.",
        "",
        "## The rules",
        "",
        "| rule | value | decisions and items named | enforced at |",
        "|---|---|---|---|",
    ]
    for name, rule in rules.items():
        origin = origins[name]
        named = ", ".join([f"decision {identifier}" for identifier in origin["decisions"]]
                          + [f"item {identifier}" for identifier in origin["items"]])
        if not named:
            named = origin["date"] or "**not traced**"
        path, exists = resolved_path(rule["code_location"])
        lines.append(f"| `{name}` | {render_value(rule['value'])} | {named} | `{path}`"
                     f"{'' if exists else ' **(missing)**'} |")
    lines.append("")

    lines += ["## What each rule means", ""]
    for name, rule in rules.items():
        origin = origins[name]
        lines.append(f"### `{name}` = {render_value(rule['value'])}")
        lines.append("")
        lines.append(rule["means"])
        lines.append("")
        lines.append(f"- Enforced at: {rendered_location(rule['code_location'])}")
        if origin["decisions"]:
            lines.append("- Decisions: " + ", ".join(f"{identifier} (`docs/open_decisions.md`)"
                                                     for identifier in origin["decisions"]))
        if origin["items"]:
            lines.append("- Amendment items: " + ", ".join(f"{identifier} (`docs/preregistration.md`)"
                                                           for identifier in origin["items"]))
        if not origin["decisions"] and not origin["items"]:
            lines.append(f"- Origin: {origin['date'] or 'not stated in the rule'}, with no decision id or amendment "
                         "item named in the rule's text, so the row or item behind it has to be found by hand")
        if rule.get("superseded"):
            lines.append("- Superseded values: " + ", ".join(f"`{value}`" for value in rule["superseded"]))
        lines.append("")

    lines += ["## What this page found", ""]
    if missing_files:
        lines += ["**A rule names code that is not there.**", ""]
        lines += [f"- `{name}`: `{path}`" for name, path in missing_files.items()] + [""]
    if dangling_decisions or dangling_items:
        lines += ["**A rule names a decision or an item that does not exist.**", ""]
        lines += [f"- `{name}`: decision(s) {', '.join(identifiers)}"
                  for name, identifiers in dangling_decisions.items()]
        lines += [f"- `{name}`: item(s) {', '.join(identifiers)}" for name, identifiers in dangling_items.items()]
        lines += [""]
    if untraced:
        lines += [f"**{len(untraced)} of {len(rules)} rules name no decision id and no amendment item in their own "
                  "text**, so the question an examiner asks first — who decided this and when — is answered by a "
                  "date rather than by a row that can be read:", ""]
        lines += [f"- `{name}`: {origins[name]['date'] or 'no date either'}" for name in untraced] + [""]
    if not missing_files and not dangling_decisions and not dangling_items and not untraced:
        lines += ["Every rule names code that exists, references that resolve and a decision or an amendment item.",
                  ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--check", action="store_true",
                        help="write nothing and exit non-zero if the committed file differs from what would be "
                             "generated, so a stale digest fails rather than misleads")
    arguments = parser.parse_args()

    rules = json.loads(REGISTERED_RULES_PATH.read_text())["rules"]
    known_decision_ids = set(decision_ids_in_log(DECISION_LOG_PATH.read_text(encoding="utf-8")))
    known_items = item_ids_in_registration(REGISTRATION_PATH.read_text(encoding="utf-8"))
    rendered = render_page(rules, known_decision_ids, known_items) + "\n"

    if arguments.check:
        existing = arguments.output.read_text(encoding="utf-8") if arguments.output.exists() else ""

        def without_stamp(text: str) -> str:
            return "\n".join(line for line in text.splitlines() if not line.startswith("Generated by `"))

        if without_stamp(existing) != without_stamp(rendered):
            raise SystemExit(f"{arguments.output} is out of date; run "
                             "PYTHONPATH=. python experiments/generate_registered_core.py")
        print(f"{arguments.output} is up to date ({len(rules)} rules)")
        return
    arguments.output.write_text(rendered, encoding="utf-8")
    print(f"wrote {arguments.output}: {len(rules)} rules")


if __name__ == "__main__":
    main()
