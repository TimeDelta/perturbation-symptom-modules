"""The module-support reach rule (models/support_reach.py, experiments/run_main_model.py --module-support-minimum-reach):
how many perturbation sources can reach each node, which nodes the rule then keeps out of every module, and that the
mask a run trains under is the one its checkpoint restores."""
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from experiments.run_main_model import build_argument_parser, build_models
from mechanistic_pathway_learning.models.noisy_or_pathway_module_model import HardConcreteNodeGate, NoisyOrPathwayModuleHead
from mechanistic_pathway_learning.models.support_reach import (
    distinct_seed_nodes,
    encoder_walkable_adjacency,
    nodes_below_minimum_reach,
    source_reach,
    walkable_adjacency,
)
from tests.test_comparative_checks import toy_data

# 0 -> 2 <- 1, 2 -> 3 -> 4, and apart from them 5 -> 6: two sources converge on 2, 3 and 4, and 6 is a lookup for 5
EDGE_SOURCE = np.array([0, 1, 2, 3, 5])
EDGE_TARGET = np.array([2, 2, 3, 4, 6])
NUM_NODES = 8  # node 7 is reached by nothing


def fake_encoder(class_weight: np.ndarray | None = None, entry_nodes: np.ndarray | None = None) -> SimpleNamespace:
    return SimpleNamespace(bottleneck_edge_source=torch.as_tensor(EDGE_SOURCE), bottleneck_edge_target=torch.as_tensor(EDGE_TARGET),
                           cell_class_node_weight=None if class_weight is None else torch.as_tensor(class_weight, dtype=torch.float32),
                           entry_node_mask=None if entry_nodes is None else torch.as_tensor(entry_nodes))


def test_a_node_counts_every_seed_a_route_reaches_it_from() -> None:
    adjacency, carries = encoder_walkable_adjacency(fake_encoder(), NUM_NODES)
    reach = source_reach(adjacency, [0, 1, 5], carries)
    assert reach.tolist() == [1, 1, 2, 2, 2, 1, 1, 0]


def test_a_route_stops_at_a_node_no_class_expresses_and_a_seed_without_weight_starts_none() -> None:
    class_weight = np.ones((NUM_NODES, 2))
    class_weight[3] = 0.0  # node 3 expressed by no class
    class_weight[5] = 0.0  # nor the seed 5
    adjacency, carries = encoder_walkable_adjacency(fake_encoder(class_weight), NUM_NODES)
    reach = source_reach(adjacency, [0, 1, 5], carries)
    assert reach.tolist() == [1, 1, 2, 0, 0, 0, 0, 0]


def test_no_route_enters_an_entry_node() -> None:
    entry_nodes = np.zeros(NUM_NODES, dtype=bool)
    entry_nodes[6] = True
    adjacency, carries = encoder_walkable_adjacency(fake_encoder(entry_nodes=entry_nodes), NUM_NODES)
    assert source_reach(adjacency, [5], carries)[6] == 0


def test_a_gene_seeded_by_two_perturbations_is_one_source() -> None:
    assert distinct_seed_nodes([[0], [0], [1, 0]]) == [0, 1]


def test_the_rule_at_two_excludes_every_node_one_source_or_none_reaches_and_leaves_entry_nodes_to_their_own_mask() -> None:
    entry_nodes = np.zeros(NUM_NODES, dtype=bool)
    entry_nodes[7] = True
    below, summary = nodes_below_minimum_reach(fake_encoder(entry_nodes=entry_nodes), NUM_NODES, [[0], [1], [5], [0]], 2, entry_node_mask=entry_nodes)
    assert np.flatnonzero(below).tolist() == [0, 1, 5, 6]
    assert summary == {"minimum_reach": 2, "perturbations_counted": 4, "seed_nodes": 3, "seed_nodes_starting_a_route": 3,
                       "nodes_eligible_before": 7, "nodes_excluded": 4, "nodes_with_reach_0": 0, "nodes_with_reach_1": 4, "nodes_with_reach_2_to_5": 3}


def test_a_minimum_below_one_is_refused() -> None:
    with pytest.raises(ValueError, match="excludes nothing"):
        nodes_below_minimum_reach(fake_encoder(), NUM_NODES, [[0]], 0)


def test_an_encoder_without_walked_edges_is_refused() -> None:
    with pytest.raises(ValueError, match="walked edges"):
        encoder_walkable_adjacency(SimpleNamespace(), NUM_NODES)


def test_the_measurement_script_and_the_rule_share_one_definition_of_where_a_route_can_go() -> None:
    from experiments import measure_perturbation_reach
    assert measure_perturbation_reach.walkable_adjacency is walkable_adjacency


def reach_mask(*excluded: int) -> torch.Tensor:
    mask = torch.zeros(NUM_NODES, dtype=torch.bool)
    mask[list(excluded)] = True
    return mask


def test_an_excluded_node_has_no_gate_in_training_in_evaluation_or_in_the_count() -> None:
    gate = HardConcreteNodeGate(2, NUM_NODES, initial_log_alpha=3.0, reach_excluded_node_mask=reach_mask(0, 6))
    assert torch.all(gate()[:, [0, 6]] == 0) and torch.all(gate.expected_gate()[:, [0, 6]] == 0)
    unruled = HardConcreteNodeGate(2, NUM_NODES, initial_log_alpha=3.0)
    unruled.log_alpha.data.copy_(gate.log_alpha.data)
    assert torch.allclose(unruled.expected_active_node_count() - gate.expected_active_node_count(),
                          torch.sigmoid(gate.log_alpha[:, [0, 6]] - gate.temperature * np.log(0.1 / 1.1)).sum(dim=1))


def test_the_mask_is_saved_only_when_the_rule_runs() -> None:
    assert set(HardConcreteNodeGate(2, NUM_NODES).state_dict()) == {"log_alpha"}
    assert set(HardConcreteNodeGate(2, NUM_NODES, reach_excluded_node_mask=reach_mask(0)).state_dict()) == {"log_alpha", "reach_excluded_node_mask"}


def test_loading_a_checkpoint_restores_the_mask_the_run_was_trained_under() -> None:
    trained = HardConcreteNodeGate(2, NUM_NODES, initial_log_alpha=3.0, reach_excluded_node_mask=reach_mask(0, 6))
    rebuilt_elsewhere = HardConcreteNodeGate(2, NUM_NODES, initial_log_alpha=3.0, reach_excluded_node_mask=reach_mask(4))
    rebuilt_elsewhere.load_state_dict(trained.state_dict())
    assert rebuilt_elsewhere.reach_excluded_node_mask.tolist() == reach_mask(0, 6).tolist()
    assert torch.equal(rebuilt_elsewhere.expected_gate(), trained.expected_gate())


def test_a_checkpoint_and_a_gate_that_disagree_about_the_rule_do_not_load() -> None:
    with pytest.raises(RuntimeError, match="reach_excluded_node_mask"):
        HardConcreteNodeGate(2, NUM_NODES, reach_excluded_node_mask=reach_mask(0)).load_state_dict(HardConcreteNodeGate(2, NUM_NODES).state_dict())
    with pytest.raises(RuntimeError, match="reach_excluded_node_mask"):
        HardConcreteNodeGate(2, NUM_NODES).load_state_dict(HardConcreteNodeGate(2, NUM_NODES, reach_excluded_node_mask=reach_mask(0)).state_dict())


def test_the_head_passes_the_mask_to_its_gate() -> None:
    head = NoisyOrPathwayModuleHead(NUM_NODES, 3, 2, 4, gate_initial_log_alpha=3.0, reach_excluded_node_mask=reach_mask(2))
    assert torch.all(head.module_support()[:, 2] == 0)


def trainer_arguments(tmp_path: Path, *extra: str):
    return build_argument_parser().parse_args(["--graph-dir", str(tmp_path / "graph"), "--evidence-dir", str(tmp_path / "evidence"), "--encoder", "linear_response",
                                               "--node-state-dim", "6", "--num-modules", "2", "--batch-size", "3", *extra])


def test_the_trainer_leaves_the_rule_off_by_default(tmp_path: Path) -> None:
    data = toy_data(tmp_path)
    _, head = build_models(data, trainer_arguments(tmp_path), torch.device("cpu"))
    assert head.support_reach_summary is None and head.support_gate.reach_excluded_node_mask is None


def test_the_trainer_counts_only_the_rows_it_is_given(tmp_path: Path) -> None:
    data = toy_data(tmp_path)
    arguments = trainer_arguments(tmp_path, "--module-support-minimum-reach", "2")
    _, head_on_all_rows = build_models(data, arguments, torch.device("cpu"))
    _, head_on_one_row = build_models(data, arguments, torch.device("cpu"), support_reach_rows=np.array([0]))
    assert head_on_one_row.support_reach_summary["perturbations_counted"] == 1
    assert head_on_all_rows.support_reach_summary["perturbations_counted"] == len(data.perturbation_ids)
    # one perturbation's seeds can give no node a reach of 2, so every eligible node is out
    assert head_on_one_row.support_reach_summary["nodes_excluded"] == head_on_one_row.support_reach_summary["nodes_eligible_before"]
    assert int(head_on_one_row.support_gate.reach_excluded_node_mask.sum()) >= int(head_on_all_rows.support_gate.reach_excluded_node_mask.sum())


def test_the_sigmoid_head_refuses_the_rule(tmp_path: Path) -> None:
    data = toy_data(tmp_path)
    with pytest.raises(ValueError, match="sigmoid head has none"):
        build_models(data, trainer_arguments(tmp_path, "--module-support-minimum-reach", "2", "--head", "sigmoid"), torch.device("cpu"))
