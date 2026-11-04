"""The chloride charge-sum defect of 14 October 2026, held so it cannot drift while it waits for the rebuild.

Found by the physiology review of 13-14 October. The graph carries chloride under two identifiers: `MAM01442*`,
which is Human-GEM's chloride (CHEBI:17996, SBML charge -1), and `MAM02144*`, three of whose four compartments are
display-named "Cl-" and which is in **neither** the Human-GEM SBML nor its metabolites table. `INORGANIC_IONS` keys
chloride on `MAM01442` alone, `ion_charges` is built by filtering SBML charges to those bases, and
`reactome_import.py` computes `inward_charge = sum(ion_charges.get(base, 0) * amount ...)`. So a Reactome reaction
whose chloride is `MAM02144` contributes nothing to the charge sum and is not even counted as moving an ion.

These tests asserted the defect as it stood rather than the behaviour that is wanted, because the fix requires the
graph to be rebuilt and the rebuild is decision 1.2, the owner's. Each one named what it should say after the fix,
so whoever rebuilds the graph could invert them and watch them pass.

The rebuild of 15 October 2026 (a new container, scripts/rebuild_data_layer.sh, with the charge guard of commit
090f001 in the code) gave the post-fix graph: GABA_A and the glycine receptor each carry `changes_membrane_potential`
at -1, and NKCC1 and KCC2 carry no membrane-potential edge. The two tests below that pinned those defects are
inverted to that, as their docstrings asked. The two chloride identifiers still exist and no MAM02144 reaction
reaches the neuronal chloride pool, so the first and last tests still hold the defect they pin.

The rebuild of 4 November 2026 (Reactome release 98, decision 9.111) is the first since two rulings that change what
these tests read, and two of them were inverted again to it. Decision 9.87 ruled the membrane potential
`computed_from_the_pools` (26 October 2026): "the 412 reaction edges into `VM_c` are not made", so no reaction carries
`changes_membrane_potential` and a channel's current reaches the potential through the ion pools and their
`driving_force` edges. Decision 9.75 added `ION_POOL_ALIASES` (`MAM02144` -> `MAM01442`), so a reaction moving
`MAM02144` chloride now reaches the neuronal chloride pool. The two chloride identifiers still both exist as nodes, so
the first test holds as before.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

GRAPH = Path("data/processed/graph_full_neuronal")
ELECTRICAL = ("changes_membrane_potential", "changes_ion_pool")

pytestmark = pytest.mark.skipif(not (GRAPH / "edges.parquet").exists(),
                                reason="the confirmatory graph is not built in this checkout")


@pytest.fixture(scope="module")
def graph() -> tuple[pd.DataFrame, pd.DataFrame]:
    return (pd.read_parquet(GRAPH / "nodes.parquet"),
            pd.read_parquet(GRAPH / "edges.parquet", columns=["source_id", "target_id", "relation_type", "sign"]))


def test_two_chloride_identifiers_exist_and_only_one_is_in_the_charge_table(graph):
    """The root of it: `MAM02144` is named "Cl-" in three compartments and is in no Human-GEM table."""
    nodes, _ = graph
    human_gem_chloride = sorted(nodes.node_id[nodes.node_id.str.startswith("MAM01442")])
    reactome_chloride = sorted(nodes.node_id[nodes.node_id.str.startswith("MAM02144")])
    assert human_gem_chloride, "Human-GEM chloride must be present"
    assert reactome_chloride, "if this is empty the rebuild has merged the two pools and this file can be deleted"
    named_chloride = nodes[nodes.node_id.isin(reactome_chloride) & (nodes.display_name == "Cl-")]
    assert len(named_chloride) >= 3, "three of MAM02144's compartments are display-named Cl-"


def test_the_ligand_gated_chloride_channels_move_chloride_into_the_cell(graph):
    """GABA_A and the glycine receptor move only chloride, from outside the cell to the cytosol. While chloride's charge
    was dropped they had no electrical edge at all; the rebuild of 15 October 2026 gave each a
    `changes_membrane_potential` edge at -1. Under decision 9.87 (`computed_from_the_pools`) no reaction carries that
    edge, so since the rebuild of 4 November 2026 each carries `changes_ion_pool` edges only: +1 into the cytosolic
    chloride pool and -1 into the extracellular one."""
    _, edges = graph
    for reaction, what in (("RCT_975340", "GABA_A heteropentamer"), ("RCT_975389", "glycine receptor")):
        electrical = edges[(edges.source_id == reaction) & edges.relation_type.isin(ELECTRICAL)]
        assert set(electrical.relation_type) == {"changes_ion_pool"}, f"{what} ({reaction}) reaches the potential through the pools only (9.87)"
        sign_into_pool = dict(zip(electrical.target_id, electrical.sign.astype(float)))
        assert sign_into_pool == {"NEURON_MAM01442c": 1.0, "NEURON_MAM01442e": -1.0}, f"{what} ({reaction}) moves chloride inward"


def test_two_electroneutral_cotransporters_carry_no_current(graph):
    """NKCC1 moves Na+ + K+ + 2Cl- inward and KCC2 moves K+ + Cl- outward. Both are electroneutral.

    While chloride's charge was dropped, NKCC1's Na+ and K+ left +1 and KCC2's K+ left -1, and the graph carried the
    two as opposing currents. With chloride counted, neither carries a `changes_membrane_potential` edge at all.
    Inverted after the rebuild of 15 October 2026. Since decision 9.87 no reaction carries that edge, so on the rebuild
    of 4 November 2026 this holds for every reaction and no longer tells the charge sum apart."""
    _, edges = graph
    for reaction, what in (("RCT_426086", "NKCC1"), ("RCT_426155", "KCC2")):
        row = edges[(edges.source_id == reaction) & (edges.relation_type == "changes_membrane_potential")]
        assert row.empty, f"{what} ({reaction}) is electroneutral and should carry no membrane-potential edge"


def test_the_reactions_moving_reactome_chloride_feed_the_neuronal_chloride_pool(graph):
    """The pool node exists and the reactions that move `MAM02144` chloride reach it, through the alias of decision 9.75
    (`ION_POOL_ALIASES`). Until the rebuild of 4 November 2026 this test held the defect, that none reached it."""
    nodes, edges = graph
    assert "NEURON_MAM01442c" in set(nodes.node_id), "the neuronal chloride pool is built"
    reactome_chloride = set(nodes.node_id[nodes.node_id.str.startswith("MAM02144")])
    touching = edges[edges.source_id.isin(reactome_chloride) | edges.target_id.isin(reactome_chloride)]
    reactions = set(touching.source_id) | set(touching.target_id)
    into_the_pool = edges[(edges.target_id == "NEURON_MAM01442c") & edges.source_id.isin(reactions)]
    assert {"RCT_975340", "RCT_975389"} <= set(into_the_pool.source_id), "GABA_A and the glycine receptor fill the chloride pool"
