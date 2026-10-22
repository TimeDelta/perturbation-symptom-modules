"""The curated organelle channel reactions (decision 9.75) against the UniProt catalytic activities they rest on
(experiments/fetch_organelle_channel_annotations.py)."""
from __future__ import annotations

import gzip
from pathlib import Path

import pytest

from experiments.build_neuronal_graph_variant import CURATED_REACTIONS
from experiments.fetch_organelle_channel_annotations import DEFAULT_PINNED_PATH, ORGANELLE_CHANNEL_GENES, organelle_channel_query, transport_reactions

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PINNED_PATH = REPOSITORY_ROOT / DEFAULT_PINNED_PATH
# the Rhea reaction each curated reaction's ion is, and the membrane word the entry's location must name
RHEA_OF_ION = {"MAM02200": "RHEA:29463", "MAM01413": "RHEA:29671"}
MEMBRANE_WORD_OF_COMPARTMENT = {"r": "reticulum membrane", "l": "ysosome membrane"}
ORGANELLE_REACTION_IDS = ("MAR_TRIC_A_POTASSIUM", "MAR_TRIC_B_POTASSIUM", "MAR_TMEM175_POTASSIUM", "MAR_TRPML_CALCIUM_RELEASE")

SMALL_TSV = ("Entry\tGene Names (primary)\tProtein names\tCatalytic activity\tRhea ID\tSubcellular location [CC]\n"
             "Q9NVV0\tTMEM38B\tTRIC-B\tCATALYTIC ACTIVITY: Reaction=K(+)(in) = K(+)(out); Xref=Rhea:RHEA:29463, ChEBI:CHEBI:29103; "
             "Evidence={ECO:0000250|UniProtKB:Q6GN30};\tRHEA:29463\tSUBCELLULAR LOCATION: Endoplasmic reticulum membrane {ECO:0000250}.\n"
             "Q9BSA9\tTMEM175\tlysosomal K+ channel\tCATALYTIC ACTIVITY: Reaction=H(+)(in) = H(+)(out); Xref=Rhea:RHEA:34979, ChEBI:CHEBI:15378; "
             "Evidence={ECO:0000269|PubMed:1, ECO:0000269|PubMed:2}; CATALYTIC ACTIVITY: Reaction=K(+)(in) = K(+)(out); Xref=Rhea:RHEA:29463, "
             "ChEBI:CHEBI:29103; Evidence={ECO:0000269|PubMed:3};\tRHEA:34979 RHEA:29463\tSUBCELLULAR LOCATION: Lysosome membrane {ECO:0000269}.\n")


def organelle_reactions():
    return [curated for curated in CURATED_REACTIONS if curated.reaction_id in ORGANELLE_REACTION_IDS]


def test_the_query_names_the_genes_rather_than_a_keyword():
    query = organelle_channel_query()
    assert "reviewed:true" in query and "organism_id:9606" in query
    assert all(f"gene_exact:{gene}" in query for gene in ORGANELLE_CHANNEL_GENES)


def test_transport_reactions_reads_one_row_per_catalytic_activity(tmp_path):
    path = tmp_path / "small.tsv.gz"
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        handle.write(SMALL_TSV)
    table = transport_reactions(path)
    assert table[["gene", "reaction", "rhea", "evidence"]].values.tolist() == [
        ["TMEM38B", "K(+)(in) = K(+)(out)", "RHEA:29463", "ECO:0000250"],
        ["TMEM175", "H(+)(in) = H(+)(out)", "RHEA:34979", "ECO:0000269"],
        ["TMEM175", "K(+)(in) = K(+)(out)", "RHEA:29463", "ECO:0000269"]]
    assert table.subcellular_location.iloc[0].startswith("SUBCELLULAR LOCATION: Endoplasmic reticulum membrane")


def test_each_curated_organelle_reaction_moves_one_ion_across_one_organelle_membrane_and_cites_uniprot():
    reactions = organelle_reactions()
    assert len(reactions) == 4
    for curated in reactions:
        assert len(curated.substrates) == 1 and len(curated.products) == 1
        (substrate,), (product,) = curated.substrates, curated.products
        bases = {substrate.replace("NEURON_", "")[:-1], product.replace("NEURON_", "")[:-1]}
        assert len(bases) == 1 and bases <= set(RHEA_OF_ION), "one ion on both sides"
        assert {substrate[-1], product[-1]} & set(MEMBRANE_WORD_OF_COMPARTMENT) and "c" in {substrate[-1], product[-1]}
        assert "UniProt" in curated.evidence and RHEA_OF_ION[bases.pop()] in curated.evidence
        assert curated.membrane_potential_sign is None, "a movement inside the cell tells the plasma membrane potential nothing"


@pytest.mark.skipif(not PINNED_PATH.exists(), reason="the pinned UniProt file is fetched by experiments/fetch_organelle_channel_annotations.py")
def test_each_curated_organelle_reaction_is_a_uniprot_catalytic_activity_at_that_membrane():
    table = transport_reactions(PINNED_PATH)
    assert set(table.gene) == set(ORGANELLE_CHANNEL_GENES)
    for curated in organelle_reactions():
        (substrate,), (product,) = curated.substrates, curated.products
        base = substrate.replace("NEURON_", "")[:-1]
        organelle = next(letter for letter in (substrate[-1], product[-1]) if letter in MEMBRANE_WORD_OF_COMPARTMENT)
        for gene in curated.catalysts:
            rows = table[(table.gene == gene) & (table.rhea == RHEA_OF_ION[base])]
            assert len(rows) == 1, f"{gene} has no UniProt {RHEA_OF_ION[base]} activity"
            assert MEMBRANE_WORD_OF_COMPARTMENT[organelle] in rows.subcellular_location.iloc[0], f"{gene} is not placed on the {organelle} membrane"
            assert "ECO:0000269" in rows.evidence.iloc[0] or gene.startswith("TMEM38"), f"{gene}: only the TRIC activities are by similarity"
