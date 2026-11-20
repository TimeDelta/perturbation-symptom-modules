"""Release regulation by auto- and heteroreceptors (graph/neurotransmission_regulation.py) and the curated oxidant
sources and targets (graph/oxidative_regulation.py)."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from mechanistic_pathway_learning.graph.neurotransmission_regulation import add_release_regulation
from mechanistic_pathway_learning.graph.oxidative_regulation import (
    OXIDANT_BASES, add_oxidative_regulation, oxidant_bases, oxidant_node)

NODE_COLUMNS = ["node_id", "node_type", "display_name", "compartment", "base_metabolite_id", "degree", "gene_symbol", "in_metabolic_layer", "is_currency"]
EDGE_COLUMNS = ["source_id", "target_id", "relation_type", "sign", "evidence_source"]
DOPAMINE, SEROTONIN, HYDROGEN_PEROXIDE, SUPEROXIDE = "MAM01736", "MAM02897", "MAM02041", "MAM02631"


def base_graph() -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
    rows = [{"node_id": f"{base}{letter}", "node_type": "metabolite", "display_name": name, "compartment": letter, "base_metabolite_id": base,
             "is_currency": True, "in_metabolic_layer": True, "degree": 0}
            for base, name in ((DOPAMINE, "dopamine"), (SEROTONIN, "serotonin"), (HYDROGEN_PEROXIDE, "H2O2"), (SUPEROXIDE, "O2-")) for letter in ("c", "e", "m")]
    rows += [{"node_id": reaction, "node_type": "reaction", "display_name": reaction, "compartment": "c;e", "is_currency": False, "degree": 0}
             for reaction in ("RCT_380869", "RCT_380901")]
    rows += [{"node_id": f"GENE:{gene}", "node_type": "gene", "display_name": gene, "gene_symbol": gene, "in_metabolic_layer": False, "degree": 0}
             for gene in ("DRD2", "HTR1A", "KEAP1", "NFE2L2", "SOD2", "MAOA", "NDUFV1")]
    nodes = pd.DataFrame(rows).reindex(columns=NODE_COLUMNS)
    edges = pd.DataFrame([{"source_id": "RCT_380869", "target_id": f"{DOPAMINE}e", "relation_type": "product_of", "sign": 1.0, "evidence_source": "Reactome"}],
                         columns=EDGE_COLUMNS)
    return nodes, edges, ["product_of"]


def receptor_table() -> pd.DataFrame:
    return pd.DataFrame([
        {"receptor_gene": "DRD2", "endogenous_ligand": "dopamine", "population": "dopaminergic", "role": "autoreceptor", "site": "presynaptic_terminal", "effect_on_release": -1, "pmid": 29030431},
        {"receptor_gene": "HTR1A", "endogenous_ligand": "serotonin", "population": "serotonergic", "role": "autoreceptor", "site": "somatodendritic", "effect_on_release": -1, "pmid": 11821026},
        {"receptor_gene": "DRD2", "endogenous_ligand": "dopamine", "population": "serotonergic", "role": "heteroreceptor", "site": "presynaptic_terminal", "effect_on_release": -1, "pmid": 18064418},
        {"receptor_gene": "HTR1A", "endogenous_ligand": "serotonin", "population": "histaminergic", "role": "heteroreceptor", "site": "somatodendritic", "effect_on_release": -1, "pmid": 11111111},
    ])


def test_receptor_activation_nodes_and_signed_regulation():
    nodes, edges, relation_types = base_graph()
    new_nodes, new_edges, new_relations, summary = add_release_regulation(
        nodes, edges, relation_types, receptor_table(), {DOPAMINE: ["RCT_380869"], SEROTONIN: ["RCT_380901"]})
    node_table = new_nodes.set_index("node_id")
    assert node_table.loc["RCPT_DRD2", "node_type"] == "protein_entity"
    assert node_table.loc["RCPT_DRD2", "display_name"] == "DRD2 activated by dopamine"
    # the gene and its ligand outside the cell both feed the activation node
    assert ((new_edges.source_id == "GENE:DRD2") & (new_edges.target_id == "RCPT_DRD2") & (new_edges.relation_type == "member_of")).any()
    ligand = new_edges[(new_edges.target_id == "RCPT_DRD2") & (new_edges.relation_type == "activates")]
    assert ligand.source_id.tolist() == [f"{DOPAMINE}e"]
    # the autoreceptor loop and the heteroreceptor on another population
    regulation = new_edges[new_edges.relation_type == "regulates_release"].set_index(["source_id", "target_id"]).sign
    assert regulation[("RCPT_DRD2", "RCT_380869")] == -1.0 and regulation[("RCPT_DRD2", "RCT_380901")] == -1.0
    assert regulation[("RCPT_HTR1A", "RCT_380901")] == -1.0
    assert summary["receptors"] == 2 and summary["regulation_edges"] == 3 and summary["inhibitory_edges"] == 3
    # the histaminergic row has no release reaction here and is reported, not invented
    assert summary["rows_without_a_release_reaction"] == ["HTR1A on histaminergic (serotonin)"]
    # a transmitter that signals is no longer currency
    assert not node_table.loc[f"{DOPAMINE}e", "is_currency"]
    assert "regulates_release" in new_relations


def test_conflicting_receptor_signs_are_left_out():
    table = pd.concat([receptor_table(), pd.DataFrame([
        {"receptor_gene": "DRD2", "endogenous_ligand": "dopamine", "population": "dopaminergic", "role": "heteroreceptor", "site": "somatodendritic", "effect_on_release": 1, "pmid": 1}])])
    nodes, edges, relation_types = base_graph()
    _, new_edges, _, summary = add_release_regulation(nodes, edges, relation_types, table, {DOPAMINE: ["RCT_380869"], SEROTONIN: ["RCT_380901"]})
    assert summary["conflicting_signs_left_out"] == ["DRD2 on dopaminergic"]
    assert not ((new_edges.relation_type == "regulates_release") & (new_edges.target_id == "RCT_380869")).any()
    assert ((new_edges.relation_type == "regulates_release") & (new_edges.source_id == "RCPT_HTR1A")).any()  # the other receptor is unaffected


def test_oxidant_species_and_compartment_resolution():
    assert oxidant_bases("hydrogen peroxide") == [HYDROGEN_PEROXIDE]
    assert sorted(oxidant_bases("superoxide and hydrogen peroxide")) == sorted([HYDROGEN_PEROXIDE, SUPEROXIDE])
    assert oxidant_bases("reactive oxygen species (unspecified oxidant)") == []
    assert oxidant_bases("lipid hydroperoxides") == []
    node_ids = {f"{HYDROGEN_PEROXIDE}{letter}" for letter in ("c", "m")}
    assert oxidant_node(HYDROGEN_PEROXIDE, "mitochondrial inner membrane, matrix", node_ids) == f"{HYDROGEN_PEROXIDE}m"
    assert oxidant_node(HYDROGEN_PEROXIDE, "plasma membrane", node_ids) == f"{HYDROGEN_PEROXIDE}c"
    assert oxidant_node(HYDROGEN_PEROXIDE, "peroxisome", node_ids) == f"{HYDROGEN_PEROXIDE}c"  # no peroxisomal copy here


def test_oxidant_target_and_source_edges():
    nodes, edges, relation_types = base_graph()
    targets = pd.DataFrame([
        {"species": "hydrogen peroxide", "target_gene": "KEAP1", "effect_sign": -1, "compartment": "cytosol", "pmid": 14585973},
        {"species": "hydrogen peroxide", "target_gene": "NFE2L2", "effect_sign": 1, "compartment": "cytosol", "pmid": 14585973},
        {"species": "peroxynitrite", "target_gene": "SOD2", "effect_sign": -1, "compartment": "mitochondrion", "pmid": 12791589},
        {"species": "reactive oxygen species (unspecified oxidant)", "target_gene": "KEAP1", "effect_sign": -1, "compartment": "cytosol", "pmid": 1},
        {"species": "hydrogen peroxide", "target_gene": "PTPN1", "effect_sign": -1, "compartment": "cytosol", "pmid": 9624118},
    ])
    sources = pd.DataFrame([
        {"source_gene": "MAOA", "species_produced": "hydrogen peroxide", "compartment": "mitochondrial outer membrane", "pmid": 17158340},
        {"source_gene": "NDUFV1", "species_produced": "superoxide", "compartment": "mitochondrial inner membrane, matrix", "pmid": 21393237},
        {"source_gene": "ALOX15", "species_produced": "lipid hydroperoxides", "compartment": "cytosol", "pmid": 14607519},
    ])
    new_nodes, new_edges, new_relations, summary = add_oxidative_regulation(nodes, edges, relation_types, targets, sources)
    modifications = new_edges[new_edges.relation_type == "oxidatively_modifies"].set_index(["source_id", "target_id"]).sign
    assert modifications[(f"{HYDROGEN_PEROXIDE}c", "GENE:KEAP1")] == -1.0
    assert modifications[(f"{HYDROGEN_PEROXIDE}c", "GENE:NFE2L2")] == 1.0
    assert ("MAM02714m", "GENE:SOD2") not in modifications.index  # peroxynitrite is not in this small graph
    production = new_edges[new_edges.relation_type == "produces_oxidant"].set_index(["source_id", "target_id"]).sign
    assert production[("GENE:MAOA", f"{HYDROGEN_PEROXIDE}m")] == 1.0
    assert production[("GENE:NDUFV1", f"{SUPEROXIDE}m")] == 1.0
    assert summary["genes_absent_from_the_graph"] == ["PTPN1"]
    assert "ALOX15 -> lipid hydroperoxides" in summary["species_without_a_human_gem_metabolite"]
    assert summary["inactivating_edges"] == 1 and summary["activating_edges"] == 1
    # the oxidants stop being currency, so a change in them propagates
    assert not new_nodes.set_index("node_id").loc[f"{HYDROGEN_PEROXIDE}c", "is_currency"]
    assert "oxidatively_modifies" in new_relations and "produces_oxidant" in new_relations


def test_curated_tables_in_the_repository_are_well_formed():
    receptors = pd.read_csv(Path("docs/curated_presynaptic_receptors.csv"))
    assert set(receptors.effect_on_release) <= {-1, 1}
    assert receptors.role.isin({"autoreceptor", "heteroreceptor"}).all()
    assert receptors.pmid.notna().all() and receptors.doi.notna().all() and receptors.supporting_quote.str.len().min() > 20
    assert not receptors.duplicated(["receptor_gene", "population", "role", "site"]).any()
    targets = pd.read_csv(Path("docs/curated_oxidant_targets.csv"))
    assert set(targets.effect_sign) <= {-1, 1} and targets.pmid.notna().all() and targets.doi.notna().all()
    sources = pd.read_csv(Path("docs/curated_oxidant_sources.csv"))
    assert sources.pmid.notna().all() and sources.doi.notna().all() and sources.compartment.notna().all()


def test_redox_pools_from_human_gem_stoichiometry():
    from mechanistic_pathway_learning.graph.redox_pools import add_redox_pools, pool_node

    glutathione, disulphide, nadph, nadp, peroxide, thioredoxin = "MAM02026", "MAM02027", "MAM02555", "MAM02554", "MAM02041", "MAM02990"
    rows = [{"node_id": f"{base}c", "node_type": "metabolite", "display_name": base, "compartment": "c", "base_metabolite_id": base,
             "is_currency": base in {glutathione, nadph, nadp}, "in_metabolic_layer": True, "degree": 0}
            for base in (glutathione, disulphide, nadph, nadp, peroxide, thioredoxin)]
    rows += [{"node_id": f"{glutathione}m", "node_type": "metabolite", "display_name": glutathione, "compartment": "m", "base_metabolite_id": glutathione,
              "is_currency": False, "in_metabolic_layer": True, "degree": 0}]
    reactions = {"GPX1": "glutathione peroxidase", "GSR": "glutathione reductase", "GST": "glutathione S-transferase", "G6PD": "glucose-6-phosphate dehydrogenase",
                 "TRANSPORT": "transport of glutathione (cytosol to mitochondrion)", "FASN": "fatty acid synthase"}
    rows += [{"node_id": reaction, "node_type": "reaction", "display_name": name, "compartment": "c", "is_currency": False, "degree": 0}
             for reaction, name in reactions.items()]
    nodes = pd.DataFrame(rows).reindex(columns=NODE_COLUMNS)
    def edge(source, target, relation):
        return {"source_id": source, "target_id": target, "relation_type": relation, "sign": 1.0, "evidence_source": "Human-GEM"}
    edge_rows = [edge(f"{glutathione}c", "GPX1", "substrate_of"), edge(f"{peroxide}c", "GPX1", "substrate_of"), edge("GPX1", f"{disulphide}c", "product_of"),
                 edge(f"{disulphide}c", "GSR", "substrate_of"), edge(f"{nadph}c", "GSR", "substrate_of"), edge("GSR", f"{glutathione}c", "product_of"),
                 edge("GSR", f"{nadp}c", "product_of"),
                 edge(f"{glutathione}c", "GST", "substrate_of"), edge("GST", f"{disulphide}c", "product_of"),
                 edge(f"{nadp}c", "G6PD", "substrate_of"), edge("G6PD", f"{nadph}c", "product_of"),
                 edge(f"{glutathione}c", "TRANSPORT", "substrate_of"), edge("TRANSPORT", f"{glutathione}m", "product_of"),
                 edge(f"{nadph}c", "FASN", "substrate_of"), edge("FASN", f"{nadp}c", "product_of")]
    edges = pd.DataFrame(edge_rows, columns=EDGE_COLUMNS)
    new_nodes, new_edges, new_relations, summary = add_redox_pools(nodes, edges, ["substrate_of", "product_of"])
    glutathione_pool, nadph_pool = pool_node("GSH", "c"), pool_node("NADPH", "c")
    changes = new_edges[new_edges.relation_type == "changes_redox_pool"].set_index(["source_id", "target_id"]).sign
    assert changes[("GPX1", glutathione_pool)] == -1.0 and changes[("GST", glutathione_pool)] == -1.0
    assert changes[("GSR", glutathione_pool)] == 1.0
    # transport out of the cytosol lowers the cytosolic pool and raises the mitochondrial one
    assert changes[("TRANSPORT", glutathione_pool)] == -1.0 and changes[("TRANSPORT", pool_node("GSH", "m"))] == 1.0
    assert changes[("G6PD", nadph_pool)] == 1.0 and changes[("GSR", nadph_pool)] == -1.0
    assert ("FASN", nadph_pool) not in changes.index  # a competing demand, left out
    # the pools feed back only to the reactions that handle an oxidant
    capacity = new_edges[new_edges.relation_type == "redox_capacity"]
    assert set(zip(capacity.source_id, capacity.target_id)) == {(glutathione_pool, "GPX1"), (nadph_pool, "GSR")}
    assert (capacity.sign == 1.0).all()
    assert not new_nodes.set_index("node_id").loc[glutathione_pool, "is_currency"]
    assert summary["largest_pool_out_degree"] == 1 and "redox_capacity" in new_relations


def test_peroxynitrite_does_not_also_produce_a_nitrite_edge():
    """The curated species names are matched by substring, because a row names its species in prose and may name two.
    The nine keys have exactly one substring relation, "nitrite" inside "peroxynitrite", so before 9 November 2026
    every peroxynitrite row also produced a nitrite edge: 8 rows of the two curated tables (1 source, 7 target)."""
    assert oxidant_bases("peroxynitrite") == [OXIDANT_BASES["peroxynitrite"]]
    assert OXIDANT_BASES["nitrite"] not in oxidant_bases("peroxynitrite")
    assert oxidant_bases("superoxide and peroxynitrite (when L-arginine depleted)") == [
        OXIDANT_BASES["superoxide"], OXIDANT_BASES["peroxynitrite"]]


def test_a_row_naming_two_species_still_gives_both():
    """The nitrite fix drops a key that is a proper substring of another matched key, and must not touch a row that
    names two unrelated species. Two values of docs/curated_oxidant_sources.csv name superoxide and hydrogen peroxide
    together, on three rows: XDH's and CYP2E1's 'superoxide and hydrogen peroxide' and PRODH's 'reactive oxygen species
    (superoxide/hydrogen peroxide)' (NOS2's 'superoxide and peroxynitrite (when L-arginine depleted)' is held by
    test_peroxynitrite_does_not_also_produce_a_nitrite_edge). SOD1's 'hydrogen peroxide (from superoxide dismutation)'
    was asserted here as a third value until 20 November 2026; it names hydrogen peroxide and its precursor, and now
    gives hydrogen peroxide alone (test_sod1_row_names_hydrogen_peroxide_and_not_its_precursor)."""
    both = [OXIDANT_BASES["hydrogen peroxide"], OXIDANT_BASES["superoxide"]]
    assert oxidant_bases("superoxide and hydrogen peroxide") == both
    assert oxidant_bases("reactive oxygen species (superoxide/hydrogen peroxide)") == both


def test_sod1_row_names_hydrogen_peroxide_and_not_its_precursor():
    """SOD1 dismutes superoxide to hydrogen peroxide, and its row of docs/curated_oxidant_sources.csv says so in prose,
    'hydrogen peroxide (from superoxide dismutation)'. Until 20 November 2026 the substring match also found
    'superoxide' there and gave SOD1 a produces_oxidant edge to superoxide, the reverse of its physiology (defect (1) of
    decision 9.122; GENE:SOD1 -> MAM02631m on the graph data/processed/graph_full_neuronal built 12 November 2026). The
    words after 'from', up to the next parenthesis or the end of the name, now name a precursor and are not matched."""
    sources = pd.read_csv(Path("docs/curated_oxidant_sources.csv"))
    sod1 = sources[sources.source_gene == "SOD1"]
    assert sod1.species_produced.tolist() == ["hydrogen peroxide (from superoxide dismutation)"]
    assert oxidant_bases(sod1.species_produced.iloc[0]) == [HYDROGEN_PEROXIDE]
    nodes, edges, relation_types = base_graph()
    sod1_node = {"node_id": "GENE:SOD1", "node_type": "gene", "display_name": "SOD1", "gene_symbol": "SOD1", "in_metabolic_layer": False, "degree": 0}
    nodes = pd.concat([nodes, pd.DataFrame([sod1_node])], ignore_index=True).reindex(columns=NODE_COLUMNS)
    no_targets = pd.DataFrame(columns=["species", "target_gene", "effect_sign", "pmid"])
    _, new_edges, _, summary = add_oxidative_regulation(nodes, edges, relation_types, no_targets, sod1)
    production = new_edges[new_edges.relation_type == "produces_oxidant"]
    base_of = nodes.set_index("node_id").base_metabolite_id
    assert production.source_id.tolist() == ["GENE:SOD1"] and base_of[production.target_id].tolist() == [HYDROGEN_PEROXIDE]
    assert summary["source_edges"] == 1
    # the clause holds every precursor it names, up to the parenthesis
    assert oxidant_bases("peroxynitrite (from superoxide and nitric oxide)") == [OXIDANT_BASES["peroxynitrite"]]


# Every species value of the two curated oxidant tables on 20 November 2026, with the oxidants it resolved to under the
# rule of 9 November 2026 (before: the substring match and the nitrite drop, commit ce4350c9) and under the precursor
# rule added on 20 November 2026 (after). A row's oxidants depend on its species value alone, so the 61 rows the tables
# held that day (38 targets, 23 sources) are pinned through their 18 values. A value added later goes in with before
# None and the oxidants its row's quote names.
RESOLUTION_BEFORE_AND_AFTER_THE_PRECURSOR_RULE = {
    ("targets", "hydrogen peroxide"): (["hydrogen peroxide"], ["hydrogen peroxide"]),
    ("targets", "4-hydroxynonenal"): (["4-hydroxynonenal"], ["4-hydroxynonenal"]),
    ("targets", "superoxide"): (["superoxide"], ["superoxide"]),
    ("targets", "peroxynitrite"): (["peroxynitrite"], ["peroxynitrite"]),
    ("targets", "nitric oxide"): (["nitric oxide"], ["nitric oxide"]),
    ("targets", "hydroxyl radical"): (["hydroxyl radical"], ["hydroxyl radical"]),
    ("targets", "reactive oxygen species (unspecified oxidant)"): ([], []),
    ("targets", "reactive oxygen species (unspecified; thiol oxidant diamide / cadmium-induced oxidation)"): ([], []),
    ("sources", "superoxide"): (["superoxide"], ["superoxide"]),
    ("sources", "hydrogen peroxide"): (["hydrogen peroxide"], ["hydrogen peroxide"]),
    ("sources", "reactive oxygen species (superoxide/hydrogen peroxide)"): (["hydrogen peroxide", "superoxide"], ["hydrogen peroxide", "superoxide"]),
    ("sources", "superoxide and hydrogen peroxide"): (["hydrogen peroxide", "superoxide"], ["hydrogen peroxide", "superoxide"]),
    ("sources", "hydrogen peroxide (reactive oxygen species from monoamine deamination)"): (["hydrogen peroxide"], ["hydrogen peroxide"]),
    ("sources", "hypochlorous acid (from H2O2 and chloride)"): (["hypochlorous acid"], ["hypochlorous acid"]),
    ("sources", "lipid hydroperoxides"): ([], []),
    ("sources", "superoxide (when BH4-deficient/uncoupled)"): (["superoxide"], ["superoxide"]),
    ("sources", "superoxide and peroxynitrite (when L-arginine depleted)"): (["superoxide", "peroxynitrite"], ["superoxide", "peroxynitrite"]),
    ("sources", "hydrogen peroxide (from superoxide dismutation)"): (["hydrogen peroxide", "superoxide"], ["hydrogen peroxide"]),
}


def test_the_precursor_rule_changed_sod1_row_alone():
    """The before/after table above: every value resolves as its after column says, and SOD1's is the one value
    whose oxidants the precursor rule changed."""
    name_of = {base: key for key, base in OXIDANT_BASES.items()}
    for (table, value), (_, after) in RESOLUTION_BEFORE_AND_AFTER_THE_PRECURSOR_RULE.items():
        assert [name_of[base] for base in oxidant_bases(value)] == after, (table, value)
    changed = {key: (before, after) for key, (before, after) in RESOLUTION_BEFORE_AND_AFTER_THE_PRECURSOR_RULE.items()
               if before is not None and before != after}
    assert changed == {("sources", "hydrogen peroxide (from superoxide dismutation)"): (["hydrogen peroxide", "superoxide"], ["hydrogen peroxide"])}


def test_every_species_value_of_the_curated_oxidant_tables_is_pinned():
    """Every row of both tables, read from the CSVs, has its species value in the table above, so that table is the
    full one, and a value added later is checked against its row's quote before it reaches the graph."""
    for table, path, column in (("targets", "docs/curated_oxidant_targets.csv", "species"),
                                ("sources", "docs/curated_oxidant_sources.csv", "species_produced")):
        pinned = {value for pinned_table, value in RESOLUTION_BEFORE_AND_AFTER_THE_PRECURSOR_RULE if pinned_table == table}
        unpinned = sorted(set(pd.read_csv(Path(path))[column]) - pinned)
        assert not unpinned, (f"{path} holds species values that RESOLUTION_BEFORE_AND_AFTER_THE_PRECURSOR_RULE lacks: {unpinned}; "
                              "add each with before None and the oxidants its row's quote names")


def test_nitrite_still_resolves_when_a_row_names_it_alone():
    """Nitrite's entry is unreachable from the tables as they stand, and is kept for a row that names it."""
    assert oxidant_bases("nitrite") == [OXIDANT_BASES["nitrite"]]


def test_an_unresolved_species_gives_nothing():
    assert oxidant_bases("lipid hydroperoxides") == []
    assert oxidant_bases("reactive oxygen species (unspecified oxidant)") == []
