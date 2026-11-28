"""Decision 9.22's zero-coupling count, taken on the inputs of decision 9.23's coupling filter before graph assembly (an
engineering measurement, read-only; nothing here interprets a count for a decision).

Why. Decision 9.22 (docs/open_decisions.md) named, as the cost to measure before family-level couplings were dropped,
"how many receptors would be left with no G-alpha edge at all, because a receptor that couples to nothing propagates
nothing", and its status records that the count "was owed before anything was dropped and was not taken: 9.23's filter
(commit `37fbdef`, 14 October 2026) dropped the receptor-to-G-alpha pairs GtoPdb does not list and left a receptor the
sheet does not annotate with every edge, and no record holds how many annotated receptors were left with no G-alpha
edge". This script takes that count on the filter's own inputs, the OmniPath interactions and the admitted table.

What it runs. build_signaling_layer of mechanistic_pathway_learning/graph/build_physiology_graph.py, the function
build_physiology_graph calls for the signalling layer, twice over the same OmniPath interactions and the same curated
sign overrides (load_curated_edge_sign_overrides, decision 9.10(a)): once with no admitted pairs, which is the layer
before the filter, and once with load_admitted_receptor_g_alpha_coupling's pairs and the transducer roles of
load_receptor_g_alpha_transducer_roles with the coupling edge types on (decision 9.86), as build_physiology_graph passes
them, which is the layer after it. It calls the build's function rather than copying its loop because the filter,
receptor_g_alpha_edge_is_dropped, reads each edge's sign only after expand_complex has expanded the complexes,
interaction_sign has signed the row and the curated override has corrected the sign, and a copy of that loop could drift
from the build. The coupling edge types rename edges and drop none, so the counts do not depend on them.

What is counted, over the annotated receptors (the receptor_gene_symbol column of the admitted table, the second value
load_admitted_receptor_g_alpha_coupling returns), each edge read from the receptor as source to a gene of
G_ALPHA_GENE_SYMBOLS as target, as the graph stores it (a binds edge is stored in both directions, so a binds row
written either way round counts). A signed edge is one whose sign is not 0, as receptor_g_alpha_edge_is_dropped reads
it; an unsigned edge is a binds edge, which the filter passes.

1. Receptors with at least one signed edge into a G alpha before the filter and none after it, by name, split into
   those left with no edge into a G alpha at all and those left with binds edges only.
2. Receptors with no signed edge into a G alpha before the filter, which the filter cannot change, split into those
   with binds edges only and those with no edge into a G alpha at all, the latter split again by whether the
   receptor's symbol is a participant of any OmniPath row.
3. Receptors that keep at least one signed edge into a G alpha after the filter, with those whose kept signed edges are
   all negatively signed named apart (typed_coupling_relation types only a positively signed edge as a coupling).

With them: the signed receptor-to-G-alpha edges before and after (distinct source, target and sign), the build's own
counters from the run after the filter (receptor_g_alpha_edges_dropped_as_unlisted counts once per expanded pair of
every OmniPath row, before duplicates are dropped), and the curated override rows whose target is a G alpha.

What it records. The SHA-256, size and modification time of each input, of the build module whose functions it runs
and of this script, with the last commit that changed each file git tracks and whether the file as read differs from it
(a tracked file's modification time is when the checkout wrote it), the date of the run and the repository commit. The
record is of the inputs, not of a graph: no graph is assembled, so no later step of build_physiology_graph (the other
layers, the node filter, the transcription gate) is applied, and a figure on a built graph is a separate measurement
(CLAUDE.md, "A measurement carries the graph it was taken on").

Every input is a required argument with no default, so a record names the files it read. An absent input, and an
admitted table that holds no pair, are refused rather than read as no filter (the build's loaders return nothing for an
absent path, and receptor_g_alpha_edge_is_dropped drops nothing without admitted pairs); an OmniPath or overrides table
that exists but holds no row is read as it is. It changes nothing it reads and writes one JSON file, which it refuses
to put under the repository's data/ directory.

Usage, from the repository root:
  PYTHONPATH=. python experiments/measure_zero_coupling_receptors.py \\
      --omnipath-interactions data/raw/omnipath/omnipath_interactions.tsv \\
      --admitted-coupling configs/admitted_receptor_g_alpha_coupling.csv \\
      --curated-edge-sign-overrides configs/curated_edge_sign_overrides.csv --output <path outside data/>
"""
from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import time
from collections import defaultdict
from pathlib import Path

import pandas as pd

from experiments.measure_saturation_counts import refuse_output_under_data, sha256_of
from mechanistic_pathway_learning.graph import build_physiology_graph as build_module
from mechanistic_pathway_learning.graph.build_physiology_graph import (
    G_ALPHA_FAMILY_MEMBERS,
    G_ALPHA_GENE_SYMBOLS,
    build_signaling_layer,
    load_admitted_receptor_g_alpha_coupling,
    load_curated_edge_sign_overrides,
    load_receptor_g_alpha_transducer_roles,
)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
GENE_NODE_PREFIX = "GENE:"
FAMILY_OF_G_ALPHA_GENE = {gene: family for family, members in G_ALPHA_FAMILY_MEMBERS.items() for gene in members}


def git_output(*git_arguments: str) -> str | None:
    """What git prints for these arguments in the repository, or None where git cannot say (no git, a path outside the
    repository, an untracked file)."""
    try:
        printed = subprocess.run(["git", *git_arguments], cwd=REPOSITORY_ROOT, capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    return printed or None


def file_provenance(path: Path) -> dict:
    """The SHA-256, size and modification time (UTC) of one file the measurement read, and, for a file git tracks, the
    last commit that changed it with that commit's date and whether the file as read differs from that commit. A
    tracked file's modification time is when the checkout wrote it, so the commit dates its content; an untracked
    download has only its modification time. The path is given to git resolved, so a relative path read from another
    directory than the repository root names the same file."""
    resolved_path = str(Path(path).resolve())
    status = Path(path).stat()
    last_commit = git_output("log", "-1", "--format=%H %cs", "--", resolved_path)
    return {"sha256": sha256_of(Path(path)), "bytes": status.st_size,
            "modified_utc": datetime.datetime.fromtimestamp(status.st_mtime, tz=datetime.timezone.utc).isoformat(timespec="seconds"),
            "last_commit": last_commit.split(" ")[0] if last_commit else None,
            "last_commit_date": last_commit.split(" ")[1] if last_commit else None,
            "differs_from_last_commit": (git_output("status", "--porcelain", "--", resolved_path) is not None) if last_commit else None}


def repository_commit() -> str | None:
    """The commit the repository's code is at, or None where git cannot say."""
    return git_output("rev-parse", "HEAD")


def gene_symbol_of_node(node_id: str) -> str | None:
    """The symbol of a GENE:<symbol> node, or None for any other node."""
    return node_id[len(GENE_NODE_PREFIX):] if isinstance(node_id, str) and node_id.startswith(GENE_NODE_PREFIX) else None


def receptor_to_g_alpha_edges(signaling_edges: pd.DataFrame, annotated_receptors: set[str]) -> dict[str, dict[str, set]]:
    """{receptor: {"signed": {(G alpha, sign)}, "unsigned": {G alpha}}} over the stored edges whose source is an
    annotated receptor and whose target is a gene of G_ALPHA_GENE_SYMBOLS, symbols compared in upper case as
    receptor_g_alpha_edge_is_dropped compares them. A receptor with no such edge is absent. A layer with no edge gives
    {}: build_signaling_layer then returns a frame with no columns, which has no source_id to read (until 28 November
    2026 that raised AttributeError, so an OmniPath table holding no row stopped the run)."""
    if signaling_edges.empty:
        return {}
    edges_by_receptor: dict[str, dict[str, set]] = defaultdict(lambda: {"signed": set(), "unsigned": set()})
    for source_id, target_id, sign in zip(signaling_edges.source_id, signaling_edges.target_id, signaling_edges.sign):
        source_symbol, target_symbol = gene_symbol_of_node(source_id), gene_symbol_of_node(target_id)
        if source_symbol is None or target_symbol is None:
            continue
        receptor, g_alpha = source_symbol.upper(), target_symbol.upper()
        if receptor not in annotated_receptors or g_alpha not in G_ALPHA_GENE_SYMBOLS:
            continue
        if float(sign) == 0.0:
            edges_by_receptor[receptor]["unsigned"].add(g_alpha)
        else:
            edges_by_receptor[receptor]["signed"].add((g_alpha, float(sign)))
    return dict(edges_by_receptor)


def signed_edge_labels(signed_edges: set[tuple[str, float]]) -> list[str]:
    """Each signed edge as "<G alpha> (<family>) <+1 or -1>", sorted."""
    return sorted(f"{g_alpha} ({FAMILY_OF_G_ALPHA_GENE[g_alpha]}) {sign:+.0f}" for g_alpha, sign in signed_edges)


def classify_annotated_receptors(edges_before: dict[str, dict[str, set]], edges_after: dict[str, dict[str, set]],
                                 annotated_receptors: set[str], omnipath_participants: set[str],
                                 admitted_families_of_receptor: dict[str, set[str]]) -> dict:
    """Every annotated receptor in exactly one of the module docstring's three groups and their subgroups, by name.

    edges_before and edges_after are receptor_to_g_alpha_edges of the layer without and with the filter;
    omnipath_participants is every gene symbol of the layer, in upper case; admitted_families_of_receptor is each
    receptor's G-alpha families in the admitted table, reported beside the receptors the filter leaves with no signed
    edge."""
    empty = {"signed": set(), "unsigned": set()}
    lost_every_signed_edge_and_no_g_alpha_edge_left: list[dict] = []
    lost_every_signed_edge_and_binds_left: list[dict] = []
    no_signed_edge_before_binds_only: list[str] = []
    no_g_alpha_edge_before_in_omnipath: list[str] = []
    no_g_alpha_edge_before_absent_from_omnipath: list[str] = []
    keeps_signed_edge: list[str] = []
    keeps_only_negatively_signed_edges: list[str] = []
    for receptor in sorted(annotated_receptors):
        before, after = edges_before.get(receptor, empty), edges_after.get(receptor, empty)
        if before["signed"]:
            if after["signed"]:
                keeps_signed_edge.append(receptor)
                if all(sign < 0 for _, sign in after["signed"]):
                    keeps_only_negatively_signed_edges.append(receptor)
                continue
            entry = {"receptor": receptor, "signed_edges_before_the_filter": signed_edge_labels(before["signed"]),
                     "admitted_families": sorted(admitted_families_of_receptor.get(receptor, set()))}
            if after["unsigned"]:
                entry["binds_edges_left"] = sorted(after["unsigned"])
                lost_every_signed_edge_and_binds_left.append(entry)
            else:
                lost_every_signed_edge_and_no_g_alpha_edge_left.append(entry)
        elif before["unsigned"]:
            no_signed_edge_before_binds_only.append(receptor)
        elif receptor in omnipath_participants:
            no_g_alpha_edge_before_in_omnipath.append(receptor)
        else:
            no_g_alpha_edge_before_absent_from_omnipath.append(receptor)
    groups = {
        "signed_edge_before_and_none_after": {
            "count": len(lost_every_signed_edge_and_no_g_alpha_edge_left) + len(lost_every_signed_edge_and_binds_left),
            "left_with_no_edge_into_a_g_alpha": {"count": len(lost_every_signed_edge_and_no_g_alpha_edge_left),
                                                  "receptors": lost_every_signed_edge_and_no_g_alpha_edge_left},
            "left_with_binds_edges_only": {"count": len(lost_every_signed_edge_and_binds_left),
                                           "receptors": lost_every_signed_edge_and_binds_left},
        },
        "no_signed_edge_before_the_filter": {
            "count": len(no_signed_edge_before_binds_only) + len(no_g_alpha_edge_before_in_omnipath) + len(no_g_alpha_edge_before_absent_from_omnipath),
            "binds_edges_only": {"count": len(no_signed_edge_before_binds_only), "receptors": no_signed_edge_before_binds_only},
            "no_edge_into_a_g_alpha_and_in_omnipath": {"count": len(no_g_alpha_edge_before_in_omnipath), "receptors": no_g_alpha_edge_before_in_omnipath},
            "no_edge_into_a_g_alpha_and_absent_from_omnipath": {"count": len(no_g_alpha_edge_before_absent_from_omnipath),
                                                                "receptors": no_g_alpha_edge_before_absent_from_omnipath},
        },
        "keeps_a_signed_edge_after_the_filter": {
            "count": len(keeps_signed_edge),
            "receptors": keeps_signed_edge,
            "only_negatively_signed_edges_kept": {"count": len(keeps_only_negatively_signed_edges), "receptors": keeps_only_negatively_signed_edges},
        },
    }
    counted = sum(groups[group]["count"] for group in groups)
    if counted != len(annotated_receptors):
        raise AssertionError(f"{counted} receptors classified, {len(annotated_receptors)} annotated")
    return groups


def admitted_families_by_receptor(admitted_pairs: set[tuple[str, str]]) -> dict[str, set[str]]:
    families: dict[str, set[str]] = defaultdict(set)
    for receptor, g_alpha in admitted_pairs:
        families[receptor].add(FAMILY_OF_G_ALPHA_GENE.get(g_alpha, g_alpha))
    return dict(families)


def distinct_signed_edges(edges_by_receptor: dict[str, dict[str, set]]) -> set[tuple[str, str, float]]:
    return {(receptor, g_alpha, sign) for receptor, edges in edges_by_receptor.items() for g_alpha, sign in edges["signed"]}


def require_input(path: Path, what: str) -> Path:
    if not Path(path).is_file():
        raise FileNotFoundError(f"{what} {path} is not a file; the measurement reads it and is refused without it")
    return Path(path)


def measure_zero_coupling(omnipath_interactions_path: Path, admitted_coupling_path: Path, curated_edge_sign_overrides_path: Path) -> dict:
    """The counts of the module docstring on these three inputs (each must exist)."""
    admitted_pairs, annotated_receptors = load_admitted_receptor_g_alpha_coupling(admitted_coupling_path)
    if not admitted_pairs:
        raise ValueError(f"{admitted_coupling_path} holds no admitted pair, so the filter would drop nothing")
    overrides = load_curated_edge_sign_overrides(curated_edge_sign_overrides_path)
    transducer_roles = load_receptor_g_alpha_transducer_roles(admitted_coupling_path)
    no_nodes = pd.DataFrame({"node_id": pd.Series([], dtype=str)})

    nodes_before, signaling_edges_before, counters_before = build_signaling_layer(
        no_nodes, omnipath_interactions_path, curated_sign_overrides=overrides, admitted_receptor_g_alpha_coupling=None,
        transducer_role_of_pair=transducer_roles, typed_coupling_relations=True)
    _, signaling_edges_after, counters_after = build_signaling_layer(
        no_nodes, omnipath_interactions_path, curated_sign_overrides=overrides,
        admitted_receptor_g_alpha_coupling=(admitted_pairs, annotated_receptors),
        transducer_role_of_pair=transducer_roles, typed_coupling_relations=True)

    omnipath_participants = {symbol.upper() for symbol in (gene_symbol_of_node(node_id) for node_id in nodes_before.node_id) if symbol}
    edges_before = receptor_to_g_alpha_edges(signaling_edges_before, annotated_receptors)
    edges_after = receptor_to_g_alpha_edges(signaling_edges_after, annotated_receptors)
    signed_before, signed_after = distinct_signed_edges(edges_before), distinct_signed_edges(edges_after)
    if not signed_after <= signed_before:
        raise AssertionError("the filtered layer holds a signed receptor-to-G-alpha edge the unfiltered one does not")
    return {
        "annotated_receptors": len(annotated_receptors),
        "admitted_pairs": len(admitted_pairs),
        "g_alpha_gene_symbols": sorted(G_ALPHA_GENE_SYMBOLS),
        "curated_override_rows": len(overrides),
        "curated_override_rows_whose_target_is_a_g_alpha": sum(1 for _, target in overrides if target.upper() in G_ALPHA_GENE_SYMBOLS),
        "signed_receptor_to_g_alpha_edges": {"before_the_filter": len(signed_before), "after_the_filter": len(signed_after),
                                             "dropped": len(signed_before - signed_after)},
        "build_counters_without_the_filter": counters_before,
        "build_counters_with_the_filter": counters_after,
        "receptors": classify_annotated_receptors(edges_before, edges_after, annotated_receptors, omnipath_participants,
                                                  admitted_families_by_receptor(admitted_pairs)),
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--omnipath-interactions", type=Path, required=True,
                        help="the OmniPath interactions table build_physiology_graph reads as --signaling")
    parser.add_argument("--admitted-coupling", type=Path, required=True,
                        help="the admitted receptor-to-G-alpha table of decision 9.23 (build_physiology_graph's --admitted-receptor-g-alpha-coupling)")
    parser.add_argument("--curated-edge-sign-overrides", type=Path, required=True,
                        help="the curated sign overrides of decision 9.10(a) (build_physiology_graph's --curated-edge-sign-overrides), applied before the filter as the build applies them")
    parser.add_argument("--output", type=Path, required=True, help="the JSON file written, outside data/")
    arguments = parser.parse_args(argv)
    refuse_output_under_data(arguments.output)
    inputs = {"omnipath_interactions": require_input(arguments.omnipath_interactions, "--omnipath-interactions"),
              "admitted_coupling": require_input(arguments.admitted_coupling, "--admitted-coupling"),
              "curated_edge_sign_overrides": require_input(arguments.curated_edge_sign_overrides, "--curated-edge-sign-overrides")}
    build_module_path = Path(build_module.__file__).resolve()
    record = {"what": "decision 9.22's zero-coupling count on the inputs of decision 9.23's coupling filter (experiments/measure_zero_coupling_receptors.py)",
              "taken_on": "the filter's inputs, before graph assembly: no graph was assembled, so no figure here is of a graph",
              "date": time.strftime("%Y-%m-%d"), "repository_commit": repository_commit(),
              "inputs": {name: {"path": str(path), **file_provenance(path)} for name, path in inputs.items()},
              **{name: {"path": str(path.relative_to(REPOSITORY_ROOT)) if path.is_relative_to(REPOSITORY_ROOT) else str(path), **file_provenance(path)}
                 for name, path in (("build_module", build_module_path), ("measurement_script", Path(__file__).resolve()))},
              **measure_zero_coupling(inputs["omnipath_interactions"], inputs["admitted_coupling"], inputs["curated_edge_sign_overrides"])}
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    receptors = record["receptors"]
    print(json.dumps({"date": record["date"], "annotated_receptors": record["annotated_receptors"],
                      "signed_receptor_to_g_alpha_edges": record["signed_receptor_to_g_alpha_edges"],
                      **{group: receptors[group]["count"] for group in receptors}}, indent=1))


if __name__ == "__main__":
    main()
