"""The held-out draw's opt-in options (target_held_out_split.HeldOutDrawOptions, built 28 November 2026 from
docs/drafts/held_out_draw_methods_2026-11-28.md, M1 and M2; none is ruled): the identity option of channel 2, M1's
closure and M2's seeded group prefix, and the default path, which must draw what it drew before they existed.
Synthetic fixtures only."""
import argparse
import random
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from mechanistic_pathway_learning.evaluation.experiment_data import (
    GENE_TO_PROTEIN_FILE, read_protein_of_gene, read_proteins_encoded_by_gene)
from mechanistic_pathway_learning.evaluation.perturbation_wise_and_pathway_wise_splits import assign_grouped_folds
from mechanistic_pathway_learning.evaluation.target_held_out_split import (
    REGISTERED_HELD_OUT_FRACTION,
    HeldOutDrawOptions,
    held_out_perturbations,
    seeded_group_prefix,
    targets_of_drugs,
    two_sided_held_out_draw,
    two_sided_held_out_perturbations,
)
from tests.test_measure_leakage_only_adversary import synthetic_data

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))

IDENTITY = HeldOutDrawOptions(hold_out_genes_encoding_held_out_targets=True)
M2 = HeldOutDrawOptions(gene_side_rule="seeded_group_prefix")
M1_WITH_M2 = HeldOutDrawOptions(hold_out_genes_encoding_held_out_targets=True, hold_out_whole_groups_of_those_genes=True,
                                gene_side_rule="seeded_group_prefix")
M1_WITH_FOLD_ZERO = HeldOutDrawOptions(hold_out_genes_encoding_held_out_targets=True, hold_out_whole_groups_of_those_genes=True)


# ---------------------------------------------------------------- the code as it stood at c24727c, copied unchanged


def assign_grouped_folds_as_of_c24727c(perturbation_identifiers, group_identifiers, num_folds, random_seed=0):
    members_by_group = defaultdict(list)
    for perturbation_identifier, group_identifier in zip(perturbation_identifiers, group_identifiers):
        members_by_group[group_identifier].append(perturbation_identifier)
    group_order = list(members_by_group)
    random.Random(random_seed).shuffle(group_order)
    group_order.sort(key=lambda group_identifier: -len(members_by_group[group_identifier]))
    fold_sizes = [0] * num_folds
    fold_by_perturbation = {}
    for group_identifier in group_order:
        smallest_fold = min(range(num_folds), key=lambda fold_index: fold_sizes[fold_index])
        for perturbation_identifier in members_by_group[group_identifier]:
            fold_by_perturbation[perturbation_identifier] = smallest_fold
        fold_sizes[smallest_fold] += len(members_by_group[group_identifier])
    return fold_by_perturbation


def held_out_targets_as_of_c24727c(targets_of_drug, seed, held_out_fraction=1 / 7):
    drugs = sorted(targets_of_drug)
    if not drugs:
        return set()
    order = sorted({target for own in targets_of_drug.values() for target in own})
    random.Random(seed).shuffle(order)
    held, best_gap, best = set(), abs(0.0 - held_out_fraction), set()
    for target in order:
        held = held | {target}
        share = sum(1 for drug in drugs if targets_of_drug[drug] & held) / len(drugs)
        gap = abs(share - held_out_fraction)
        if gap < best_gap:
            best_gap, best = gap, set(held)
        elif share > held_out_fraction + 0.05:
            break
    return best


def two_sided_as_of_c24727c(perturbation_ids, perturbation_types, perturbation_seeds, node_ids, group_ids, seed,
                            held_out_fraction=1 / 7):
    targets_of_drug = targets_of_drugs(perturbation_ids, perturbation_types, perturbation_seeds, node_ids)
    held_targets = held_out_targets_as_of_c24727c(targets_of_drug, seed, held_out_fraction)
    held = {drug for drug, own in targets_of_drug.items() if own & held_targets}
    names = list(node_ids)
    for perturbation_id, kind, seeds in zip(perturbation_ids, perturbation_types, perturbation_seeds):
        if kind == "drug":
            continue
        own = {names[int(index)] for index in seeds if 0 <= int(index) < len(names)}
        if own & held_targets:
            held.add(str(perturbation_id))
    fold_of_perturbation = assign_grouped_folds_as_of_c24727c(perturbation_ids, group_ids, int(round(1 / held_out_fraction)), seed)
    for perturbation_id, kind in zip(perturbation_ids, perturbation_types):
        if kind != "drug" and fold_of_perturbation[perturbation_id] == 0:
            held.add(str(perturbation_id))
    return held, held_targets


# ---------------------------------------------------------------- fixtures


def split_graph_fixture(rng_seed=0, num_genes=60, num_drugs=30, num_targets=12, genes_per_group=3):
    """A gene/protein split graph's arrays: gene i seeds GENE:i and encodes PROTEIN:i for i < num_targets (one gene,
    GENE:{num_targets - 1}, has no protein node, so a drug targeting it seeds its gene node); drugs seed proteins. Genes
    are grouped in consecutive triples, so groups have members on both sides of an identity match."""
    generator = np.random.default_rng(rng_seed)
    gene_nodes = [f"GENE:{index}" for index in range(num_genes)]
    protein_nodes = [f"PROTEIN:{index}" for index in range(num_targets - 1)]
    node_ids = protein_nodes + gene_nodes
    node_index = {name: position for position, name in enumerate(node_ids)}
    target_nodes = protein_nodes + [f"GENE:{num_targets - 1}"]  # the last target gene has no protein node
    drug_seeds = [sorted({node_index[target_nodes[index]] for index in generator.choice(num_targets, size=int(generator.integers(1, 3)), replace=False)})
                  for _ in range(num_drugs)]
    gene_seeds = [[node_index[name]] for name in gene_nodes]
    perturbation_ids = [f"d{index}" for index in range(num_drugs)] + [f"g{index}" for index in range(num_genes)]
    perturbation_types = ["drug"] * num_drugs + ["gene"] * num_genes
    group_ids = [f"drug_group_{index}" for index in range(num_drugs)] + [f"cluster_{index // genes_per_group}" for index in range(num_genes)]
    proteins_encoded_by_gene = {f"GENE:{index}": {f"PROTEIN:{index}"} for index in range(num_targets - 1)}
    return perturbation_ids, perturbation_types, [np.array(seed) for seed in drug_seeds + gene_seeds], node_ids, group_ids, proteins_encoded_by_gene


def merged_graph_fixture(rng_seed=1, num_genes=50, num_drugs=25, num_targets=10):
    """A merged graph: drugs seed the gene nodes of their targets, and some groups join a drug to genes, as
    disease_cluster_and_targets does."""
    generator = np.random.default_rng(rng_seed)
    node_ids = [f"GENE:{index}" for index in range(num_genes)]
    drug_seeds = [sorted(generator.choice(num_targets, size=int(generator.integers(1, 4)), replace=False).tolist()) for _ in range(num_drugs)]
    gene_seeds = [[index] for index in range(num_genes)]
    perturbation_ids = [f"d{index}" for index in range(num_drugs)] + [f"g{index}" for index in range(num_genes)]
    perturbation_types = ["drug"] * num_drugs + ["gene"] * num_genes
    group_ids = [f"cluster_{index % 7}" if index % 3 == 0 else f"drug_group_{index}" for index in range(num_drugs)]
    group_ids += [f"cluster_{index // 4}" for index in range(num_genes)]
    return perturbation_ids, perturbation_types, [np.array(seed) for seed in drug_seeds + gene_seeds], node_ids, group_ids


def fixtures():
    data = synthetic_data()
    yield data.perturbation_ids, data.perturbation_types, data.perturbation_seeds, data.node_ids, data.group_ids
    yield split_graph_fixture()[:5]
    yield split_graph_fixture(rng_seed=5, num_genes=90, num_drugs=40, genes_per_group=5)[:5]
    yield merged_graph_fixture()


# ---------------------------------------------------------------- the default path


@pytest.mark.parametrize("fixture_index", range(4))
def test_the_default_path_draws_what_it_drew_before_the_options(fixture_index):
    arrays = list(fixtures())[fixture_index]
    for seed in range(12):
        before = two_sided_as_of_c24727c(*arrays, seed)
        assert two_sided_held_out_perturbations(*arrays, seed) == before, seed
        assert two_sided_held_out_perturbations(*arrays, seed, options=HeldOutDrawOptions()) == before, seed
        draw = two_sided_held_out_draw(*arrays, seed)
        assert (draw.held_out_ids, draw.held_out_target_ids) == before
        assert draw.forced_group_ids == set() and draw.overshoot == 0.0 and not draw.forced_groups_pass_the_fraction
    for fraction in (0.2, 0.34):
        assert two_sided_held_out_perturbations(*arrays, 3, fraction) == two_sided_as_of_c24727c(*arrays, 3, fraction)


def test_grouped_folds_without_groups_placed_first_are_what_they_were():
    perturbation_ids, _, _, _, group_ids = merged_graph_fixture()
    for seed in range(10):
        assert assign_grouped_folds(perturbation_ids, group_ids, 7, seed) == assign_grouped_folds_as_of_c24727c(perturbation_ids, group_ids, 7, seed)


def test_groups_placed_in_fold_zero_are_there_and_counted_in_the_balance():
    perturbation_ids, _, _, _, group_ids = merged_graph_fixture()
    folds = assign_grouped_folds(perturbation_ids, group_ids, 7, 4, groups_placed_in_fold_zero={"cluster_3", "cluster_5"})
    group_of = dict(zip(perturbation_ids, group_ids))
    assert all(folds[perturbation_id] == 0 for perturbation_id in perturbation_ids if group_of[perturbation_id] in {"cluster_3", "cluster_5"})
    sizes = np.bincount(list(folds.values()), minlength=7)
    assert sizes.max() - sizes.min() <= max(sum(1 for group in group_ids if group == name) for name in set(group_ids))


# ---------------------------------------------------------------- channel 2: identity


def test_on_a_split_graph_the_default_leaves_a_held_out_targets_gene_in_training_and_the_identity_option_holds_it_out():
    nodes = ["PROTEIN:A", "PROTEIN:B", "GENE:A", "GENE:B"]
    ids, kinds = ["d1", "d2", "gA", "gB"], ["drug", "drug", "gene", "gene"]
    seeds = [[0], [1], [2], [3]]
    encoded = {"GENE:A": {"PROTEIN:A"}, "GENE:B": {"PROTEIN:B"}}
    for seed in range(6):
        held, held_targets = held_out_perturbations(ids, kinds, seeds, nodes, seed=seed, held_out_fraction=0.5)
        assert held_targets and not ({"gA", "gB"} & held)  # no gene seed is a protein target
        identity_held, identity_targets = held_out_perturbations(ids, kinds, seeds, nodes, seed=seed, held_out_fraction=0.5,
                                                                 proteins_encoded_by_gene=encoded)
        assert identity_targets == held_targets
        assert identity_held == held | {gene for gene, node in (("gA", "GENE:A"), ("gB", "GENE:B")) if encoded[node] & held_targets}


def test_the_gene_node_map_route_never_matches_a_protein_target():
    """held_out_perturbations' gene_node_of_perturbation adds a gene node, and a gene node is never a protein node."""
    nodes = ["PROTEIN:A", "PROTEIN:B", "GENE:A", "GENE:B"]
    ids, kinds, seeds = ["d1", "d2", "gA", "gB"], ["drug", "drug", "gene", "gene"], [[0], [1], [2], [3]]
    for seed in range(6):
        held, _ = held_out_perturbations(ids, kinds, seeds, nodes, seed=seed, held_out_fraction=0.5,
                                         gene_node_of_perturbation={"gA": "GENE:A", "gB": "GENE:B"})
        assert not ({"gA", "gB"} & held)


def test_a_target_gene_without_a_protein_node_is_matched_by_the_default():
    """The exception the docstrings name: a drug seeds the gene node of a target gene the split gave no protein node."""
    nodes = ["PROTEIN:A", "GENE:A", "GENE:C"]
    ids, kinds, seeds = ["d1", "d3", "gA", "gC"], ["drug", "drug", "gene", "gene"], [[0], [2], [1], [2]]
    for seed in range(6):
        held, held_targets = held_out_perturbations(ids, kinds, seeds, nodes, seed=seed, held_out_fraction=0.5)
        assert ("gC" in held) == ("GENE:C" in held_targets)


def test_on_a_merged_graph_the_identity_option_changes_nothing():
    arrays = merged_graph_fixture()
    for seed in range(8):
        assert two_sided_held_out_perturbations(*arrays, seed, options=IDENTITY, proteins_encoded_by_gene={}) == \
            two_sided_held_out_perturbations(*arrays, seed)


def test_the_identity_option_alone_adds_exactly_the_genes_encoding_held_out_targets():
    *arrays, encoded = split_graph_fixture()
    for seed in range(10):
        default = two_sided_held_out_draw(*arrays, seed)
        identity = two_sided_held_out_draw(*arrays, seed, options=IDENTITY, proteins_encoded_by_gene=encoded)
        assert identity.held_out_target_ids == default.held_out_target_ids
        encoding = {f"g{gene}" for gene in range(60) if encoded.get(f"GENE:{gene}", set()) & identity.held_out_target_ids}
        assert identity.held_with_their_targets_ids == default.held_with_their_targets_ids | encoding
        assert identity.held_out_ids == default.held_out_ids | encoding


# ---------------------------------------------------------------- M2: the seeded group prefix


def test_the_prefix_keeps_the_nearest_whole_groups_and_follows_the_seed():
    counts = {f"group_{index}": 1 + index % 3 for index in range(30)}  # 60 members
    sides = []
    for seed in range(20):
        prefix = seeded_group_prefix(counts, seed, 0.2, 60)
        order = sorted(counts)
        random.Random(seed).shuffle(order)
        assert prefix == order[:len(prefix)]  # a prefix of the seed's order
        totals = np.cumsum([counts[group] for group in order]) / 60
        assert abs(totals[len(prefix) - 1] - 0.2) == pytest.approx(np.min(np.abs(totals - 0.2)))
        sides.append(frozenset(prefix))
    assert len(set(sides)) > 10  # the seed decides the side


def test_the_prefix_is_never_empty_when_the_first_group_is_larger_than_twice_the_fraction():
    counts = {"huge": 40, "a": 1, "b": 1, "c": 1}
    for seed in range(30):
        order = sorted(counts)
        random.Random(seed).shuffle(order)
        prefix = seeded_group_prefix(counts, seed, 0.1, 43)
        assert prefix  # held_out_targets' rule as written would return the empty prefix when "huge" comes first
        if order[0] == "huge":
            assert prefix == ["huge"]


def test_with_forced_members_the_empty_prefix_is_a_candidate():
    counts = {"a": 5, "b": 5}
    assert seeded_group_prefix(counts, 0, 0.1, 100, forced_count=10) == []  # 10 of 100 is the fraction already
    assert seeded_group_prefix(counts, 0, 0.1, 100, forced_count=20) == []  # past it: adding only moves away
    assert len(seeded_group_prefix(counts, 0, 0.2, 100, forced_count=10)) == 2  # 10 + 5 + 5 = 20
    assert seeded_group_prefix({}, 0, 0.1, 0) == []


def test_a_tie_keeps_the_shorter_prefix():
    # of 8 members, "a" alone is 0.125 and "a" then "b" 0.375, equally far from 0.25 (exact in binary); "b" alone is
    # 0.25 itself. Either way the one-group prefix is kept, as held_out_targets keeps the shorter on a tie.
    counts = {"a": 1, "b": 2}
    for seed in range(10):
        order = sorted(counts)
        random.Random(seed).shuffle(order)
        assert seeded_group_prefix(counts, seed, 0.25, 8) == order[:1]


def test_the_m2_gene_side_holds_whole_groups_near_the_fraction_and_not_always_the_largest():
    *arrays, _ = split_graph_fixture(rng_seed=3, num_genes=90, genes_per_group=3)
    perturbation_ids, perturbation_types, _, _, group_ids = arrays
    group_ids = list(group_ids)
    group_ids[30 + 0:30 + 12] = ["cluster_big"] * 12  # one group of 12 genes, the largest
    arrays[4] = group_ids
    group_of = dict(zip(perturbation_ids, group_ids))
    genes = [perturbation_id for perturbation_id, kind in zip(perturbation_ids, perturbation_types) if kind == "gene"]
    largest_held = []
    for seed in range(20):
        draw = two_sided_held_out_draw(*arrays, seed, options=M2)
        gene_side = {gene for gene in genes if gene in draw.held_out_ids} - draw.held_with_their_targets_ids
        held_groups = {group_of[gene] for gene in gene_side}
        assert all(gene in draw.held_out_ids for gene in genes if group_of[gene] in held_groups)  # whole groups
        assert abs(len(gene_side) / len(genes) - REGISTERED_HELD_OUT_FRACTION) <= 12 / len(genes)
        largest_held.append("cluster_big" in held_groups)
        default = two_sided_held_out_draw(*arrays, seed)
        assert any(gene in default.held_out_ids for gene in genes if group_of[gene] == "cluster_big")  # fold 0, always
    assert not all(largest_held)


# ---------------------------------------------------------------- M1: the closure


def test_m1_holds_out_the_whole_group_of_each_identity_gene_counted_first():
    *arrays, encoded = split_graph_fixture()
    perturbation_ids, perturbation_types, _, _, group_ids = arrays
    group_of = dict(zip(perturbation_ids, group_ids))
    genes = [perturbation_id for perturbation_id, kind in zip(perturbation_ids, perturbation_types) if kind == "gene"]
    for seed in range(15):
        identity = two_sided_held_out_draw(*arrays, seed, options=IDENTITY, proteins_encoded_by_gene=encoded)
        draw = two_sided_held_out_draw(*arrays, seed, options=M1_WITH_M2, proteins_encoded_by_gene=encoded)
        assert draw.held_with_their_targets_ids == identity.held_with_their_targets_ids
        assert draw.forced_group_ids == {group_of[gene] for gene in draw.held_with_their_targets_ids}
        assert draw.forced_gene_side_ids == {gene for gene in genes if group_of[gene] in draw.forced_group_ids}
        assert draw.forced_gene_side_ids <= draw.held_out_ids
        assert draw.forced_share_of_the_gene_side == pytest.approx(len(draw.forced_gene_side_ids) / len(genes))
        gene_side = {gene for gene in genes if gene in draw.held_out_ids}
        held_groups = {group_of[gene] for gene in gene_side}
        assert gene_side == {gene for gene in genes if group_of[gene] in held_groups}  # nothing straddles on the gene side
        if not draw.forced_groups_pass_the_fraction:  # the rest is M2's prefix, counted after the forced genes
            rest = held_groups - draw.forced_group_ids
            candidates = {group: sum(1 for gene in genes if group_of[gene] == group) for group in set(group_of[gene] for gene in genes) - draw.forced_group_ids}
            expected = set(seeded_group_prefix(candidates, seed, REGISTERED_HELD_OUT_FRACTION, len(genes), len(draw.forced_gene_side_ids)))
            assert rest == expected


def test_when_the_forced_groups_pass_the_fraction_the_side_stops_there_and_the_overshoot_is_recorded():
    """Five drugs on five proteins, so at 0.15 one target is held out (one drug in five); the gene encoding it sits in
    a cluster of 10 of the 50 genes, so its forced cluster alone is 0.2 of the gene side, past 0.15."""
    nodes = [f"PROTEIN:{index}" for index in range(5)] + [f"GENE:{index}_{member}" for index in range(5) for member in range(10)]
    node_index = {name: position for position, name in enumerate(nodes)}
    ids = [f"d{index}" for index in range(5)] + [f"g{index}_{member}" for index in range(5) for member in range(10)]
    kinds = ["drug"] * 5 + ["gene"] * 50
    seeds = [[index] for index in range(5)] + [[node_index[f"GENE:{index}_{member}"]] for index in range(5) for member in range(10)]
    groups = [f"drug_group_{index}" for index in range(5)] + [f"cluster_{index}" for index in range(5) for _ in range(10)]
    encoded = {f"GENE:{index}_0": {f"PROTEIN:{index}"} for index in range(5)}
    for seed in range(4):
        for options in (M1_WITH_M2, M1_WITH_FOLD_ZERO):
            draw = two_sided_held_out_draw(ids, kinds, seeds, nodes, groups, seed=seed, held_out_fraction=0.15,
                                           options=options, proteins_encoded_by_gene=encoded)
            assert len(draw.held_out_target_ids) == 1
            (target,) = draw.held_out_target_ids
            index = target.removeprefix("PROTEIN:")
            assert draw.held_with_their_targets_ids == {f"g{index}_0"}
            assert draw.forced_group_ids == {f"cluster_{index}"}
            assert draw.forced_gene_side_ids == {f"g{index}_{member}" for member in range(10)}
            assert draw.forced_groups_pass_the_fraction and draw.overshoot == pytest.approx(0.2 - 0.15)
            # stopped at the forced set, and the seed is not refused
            assert draw.held_out_ids == {f"d{index}"} | draw.forced_gene_side_ids


def test_m1_under_fold_zero_places_the_forced_groups_in_fold_zero():
    *arrays, encoded = split_graph_fixture(rng_seed=7, num_genes=120, genes_per_group=2)
    perturbation_ids, perturbation_types, _, _, group_ids = arrays
    for seed in range(10):
        draw = two_sided_held_out_draw(*arrays, seed, options=M1_WITH_FOLD_ZERO, proteins_encoded_by_gene=encoded)
        assert not draw.forced_groups_pass_the_fraction
        folds = assign_grouped_folds(perturbation_ids, group_ids, 7, seed, groups_placed_in_fold_zero=draw.forced_group_ids)
        expected = draw.held_with_their_targets_ids | {perturbation_id for perturbation_id, kind in zip(perturbation_ids, perturbation_types)
                                                       if kind != "drug" and folds[perturbation_id] == 0}
        assert {perturbation_id for perturbation_id in draw.held_out_ids if not perturbation_id.startswith("d")} == expected
        assert draw.forced_gene_side_ids <= draw.held_out_ids


def test_a_forced_groups_drugs_stay_where_the_target_rule_puts_them():
    arrays = merged_graph_fixture()
    perturbation_ids, perturbation_types, perturbation_seeds, node_ids, _ = arrays
    targets = targets_of_drugs(perturbation_ids, perturbation_types, perturbation_seeds, node_ids)
    for seed in range(10):
        draw = two_sided_held_out_draw(*arrays, seed, options=M1_WITH_M2, proteins_encoded_by_gene={})
        held_drugs = {perturbation_id for perturbation_id in draw.held_out_ids if perturbation_id.startswith("d")}
        assert held_drugs == {drug for drug, own in targets.items() if own & draw.held_out_target_ids}


# ---------------------------------------------------------------- the options themselves


def test_the_options_refuse_what_they_cannot_draw():
    with pytest.raises(ValueError, match="gene_side_rule"):
        HeldOutDrawOptions(gene_side_rule="fold_one")
    with pytest.raises(ValueError, match="closure"):
        HeldOutDrawOptions(hold_out_whole_groups_of_those_genes=True)
    with pytest.raises(ValueError, match="proteins_encoded_by_gene"):
        two_sided_held_out_draw(*split_graph_fixture()[:5], 0, options=IDENTITY)
    assert HeldOutDrawOptions().is_default() and not M2.is_default()
    assert HeldOutDrawOptions.from_record(None) == HeldOutDrawOptions()
    assert HeldOutDrawOptions.from_record(M1_WITH_M2.as_record()) == M1_WITH_M2


def test_the_identity_map_is_every_encodes_row_and_not_only_the_drug_target_rows(tmp_path):
    pd.DataFrame({"gene_node_id": ["GENE:A", "GENE:A", "GENE:B"], "protein_node_id": ["PROTEIN:A:P1", "PROTEIN:A:P2", "PROTEIN:B"],
                  "drug_target": [True, False, True]}).to_parquet(tmp_path / GENE_TO_PROTEIN_FILE)
    assert read_proteins_encoded_by_gene(tmp_path) == {"GENE:A": {"PROTEIN:A:P1", "PROTEIN:A:P2"}, "GENE:B": {"PROTEIN:B"}}
    assert read_protein_of_gene(tmp_path) == {"GENE:A": ["PROTEIN:A:P1"], "GENE:B": ["PROTEIN:B"]}  # what a drug seeds
    assert read_proteins_encoded_by_gene(tmp_path / "merged") == {}


# ---------------------------------------------------------------- the three scripts: one rule for the pseudo-draws and the draw


def script_parser():
    from measure_leakage_only_adversary import add_held_out_draw_option_arguments
    parser = argparse.ArgumentParser()
    add_held_out_draw_option_arguments(parser)
    for name in ("--checkpoint-dir", "--json-output", "--markdown-output"):
        parser.add_argument(name, type=Path, default=None)
    return parser


def test_the_flags_are_off_by_default_and_name_the_options():
    from measure_leakage_only_adversary import held_out_draw_options_from_arguments
    parser = script_parser()
    assert held_out_draw_options_from_arguments(parser, parser.parse_args([])) == HeldOutDrawOptions()
    on = parser.parse_args(["--hold-out-genes-encoding-held-out-targets", "--hold-out-whole-groups-of-those-genes",
                            "--gene-side-rule", "seeded_group_prefix"])
    assert held_out_draw_options_from_arguments(parser, on) == M1_WITH_M2
    with pytest.raises(SystemExit):  # the closure without the identity option is a usage error
        held_out_draw_options_from_arguments(parser, parser.parse_args(["--hold-out-whole-groups-of-those-genes"]))
    with pytest.raises(SystemExit):
        parser.parse_args(["--gene-side-rule", "fold_one"])


def test_a_measurement_with_a_draw_option_must_name_its_own_paths(tmp_path):
    from measure_leakage_only_adversary import SHARED_SEED_NODE_RUN_DEFAULTS, refuse_shared_run_paths_for_draw_options
    parser = script_parser()
    refuse_shared_run_paths_for_draw_options(parser, parser.parse_args([]), HeldOutDrawOptions())  # the default run keeps its paths
    with pytest.raises(SystemExit):
        refuse_shared_run_paths_for_draw_options(parser, parser.parse_args([]), M2)
    shared = parser.parse_args(["--checkpoint-dir", str(SHARED_SEED_NODE_RUN_DEFAULTS["checkpoint_dir"]),
                                "--json-output", str(tmp_path / "a.json"), "--markdown-output", str(tmp_path / "a.md")])
    with pytest.raises(SystemExit):
        refuse_shared_run_paths_for_draw_options(parser, shared, M2)
    own = parser.parse_args(["--checkpoint-dir", str(tmp_path / "draws"), "--json-output", str(tmp_path / "a.json"),
                             "--markdown-output", str(tmp_path / "a.md")])
    refuse_shared_run_paths_for_draw_options(parser, own, M2)


def test_a_checkpoint_directory_of_a_run_without_options_still_serves_one_and_refuses_one_with_them(tmp_path):
    from measure_leakage_only_adversary import CHECKPOINT_INPUT_KEYS, DRAW_OPTIONS_KEY, claim_checkpoint_directory
    default_inputs = {key: "x" for key in CHECKPOINT_INPUT_KEYS if key != DRAW_OPTIONS_KEY}  # what a run before 28 Nov wrote
    claim_checkpoint_directory(tmp_path / "draws", default_inputs)
    claim_checkpoint_directory(tmp_path / "draws", default_inputs)
    with pytest.raises(SystemExit, match=DRAW_OPTIONS_KEY):
        claim_checkpoint_directory(tmp_path / "draws", {**default_inputs, DRAW_OPTIONS_KEY: M2.as_record()})


def test_the_measurement_draws_by_the_options_it_is_given():
    from measure_leakage_only_adversary import registered_two_sided_draw
    data = synthetic_data()
    arrays = (data.perturbation_ids, data.perturbation_types, data.perturbation_seeds, data.node_ids, data.group_ids)
    for seed in range(6):
        assert registered_two_sided_draw(data, seed) == two_sided_as_of_c24727c(*arrays, seed)
        assert registered_two_sided_draw(data, seed, M2) == two_sided_held_out_perturbations(*arrays, seed, options=M2)


def test_the_measurement_page_names_the_options_only_when_one_is_on():
    from measure_leakage_only_adversary import DRAW_OPTIONS_KEY, _draw_options_lines
    assert _draw_options_lines({}) == []
    assert "not pseudo-draws of the registered rule" in _draw_options_lines({DRAW_OPTIONS_KEY: M2.as_record()})[0]


def test_the_calibration_refuses_a_measurement_drawn_by_other_options_and_records_its_own():
    from calibrate_leakage_ceiling import calibrate
    from measure_leakage_only_adversary import DRAW_OPTIONS_KEY
    from tests.test_leakage_ceiling import measurement_record
    arguments = ("base_rate_shrunk_mean", "seen_target_share", "drug_stratum_macro_advantage_over_type_popularity", 0.05,
                 "least_squares_line", 6)
    assert DRAW_OPTIONS_KEY not in calibrate(measurement_record(), *arguments)  # a record without them: the rule as it stands
    with pytest.raises(ValueError, match="one rule"):
        calibrate(measurement_record(), *arguments, M2)
    measured_with_m2 = {**measurement_record(), DRAW_OPTIONS_KEY: M2.as_record()}
    with pytest.raises(ValueError, match="one rule"):
        calibrate(measured_with_m2, *arguments)
    assert calibrate(measured_with_m2, *arguments, M2)[DRAW_OPTIONS_KEY] == M2.as_record()


def test_the_draw_refuses_a_calibration_of_other_options_and_draws_by_its_own():
    from draw_held_out_set import ceilings_of_calibrations, draw_held_out_set
    from measure_leakage_only_adversary import DRAW_OPTIONS_KEY
    from tests.test_leakage_ceiling import DIGESTS, calibration_record
    with pytest.raises(ValueError, match="one rule"):
        ceilings_of_calibrations([calibration_record()], "disease_cluster", DIGESTS, M2)
    with pytest.raises(ValueError, match="one rule"):
        ceilings_of_calibrations([{**calibration_record(), DRAW_OPTIONS_KEY: M2.as_record()}], "disease_cluster", DIGESTS)
    data = synthetic_data()
    record = draw_held_out_set(data, [100, 101, 102], [{**calibration_record(ceiling=2.0), DRAW_OPTIONS_KEY: M2.as_record()}],
                               "disease_cluster", DIGESTS, M2)
    assert record["accepted_seed"] == 100 and record[DRAW_OPTIONS_KEY] == M2.as_record()
    expected, _ = two_sided_held_out_perturbations(data.perturbation_ids, data.perturbation_types, data.perturbation_seeds,
                                                   data.node_ids, data.group_ids, 100, options=M2)
    assert record["perturbation_ids"] == sorted(expected)
    default = draw_held_out_set(data, [100], [calibration_record(ceiling=2.0)], "disease_cluster", DIGESTS)
    assert DRAW_OPTIONS_KEY not in default and DRAW_OPTIONS_KEY not in default["rule"]
