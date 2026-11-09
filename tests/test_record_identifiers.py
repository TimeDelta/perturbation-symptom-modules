"""The record identifier resolver: what it parses, what it refuses to parse and what collapses to one record."""
from __future__ import annotations

import pytest

from mechanistic_pathway_learning.evidence.record_identifiers import (
    DOI_KIND, PMC_ID_KIND, PUBMED_ID_KIND, IdentifierCrosswalk, RecordIdentifier,
    deduplicate_reference_list, normalise_doi, normalise_pmc_id, normalise_pubmed_id,
    parse_record_identifiers, parse_resource_prefixed_references)


def test_a_doi_is_lowercased_because_a_doi_is_case_insensitive():
    assert normalise_doi("10.1038/S41589-020-0644-4") == "10.1038/s41589-020-0644-4"
    assert normalise_doi("https://doi.org/10.1038/S41589") == "10.1038/s41589"
    assert normalise_doi("doi:10.1016/0005-2760(86)90170-0.") == "10.1016/0005-2760(86)90170-0"


def test_a_pubmed_id_loses_its_leading_zeros_and_a_pmc_id_gains_its_prefix():
    assert normalise_pubmed_id("0012345") == "12345"
    assert normalise_pmc_id("pmc7678813") == "PMC7678813"


def test_human_gems_two_prefix_spellings_and_its_empty_tokens_are_both_handled():
    """Release 2.0.1 writes nine tokens as "PubMed:" rather than "PMID:", and some tokens carry no number."""
    parsed = parse_record_identifiers("PMID:16919238;PMID:;PubMed:10215651")
    assert parsed == [RecordIdentifier(PUBMED_ID_KIND, "16919238"), RecordIdentifier(PUBMED_ID_KIND, "10215651")]


def test_a_repeated_identifier_is_kept_in_the_parse_so_a_caller_can_count_it():
    parsed = parse_record_identifiers("PMID:3443096;PMID:3443096;PMID:7759508")
    assert [identifier.value for identifier in parsed] == ["3443096", "3443096", "7759508"]


def test_a_journal_citation_is_not_read_as_an_identifier():
    """configs/curated_drug_targets.csv cites "J Neural Transm Suppl 56:83-105"; "56:83" is a volume and page, and a
    CIS number and a content hash are not identifiers either. parse_record_identifiers must find none of them."""
    assert parse_record_identifiers("J Neural Transm Suppl 56:83-105") == []
    assert parse_record_identifiers("ANSM RCP NEULEPTIL 10 mg gelule (CIS 64676824, sha 89b532f7033be751) 5.1") == []


def test_the_resource_prefixed_column_shape_is_read_and_its_repeats_are_visible():
    """One CollecTRI row names PubMed id 10022869 under four resource prefixes. graph/edge_evidence.py already
    collapses those; this parser must see all four so the collapse can be reported rather than assumed."""
    parsed = parse_resource_prefixed_references(
        "CollecTRI:10022869;DoRothEA:10022869;TRRUST:10022869;CollecTRI2:10022869")
    assert [identifier.value for identifier in parsed] == ["10022869"] * 4


def test_the_resource_prefixed_parser_falls_through_to_the_prose_parser_for_a_doi_token():
    parsed = parse_resource_prefixed_references("TRIP:12601176;10.1038/s41589-020-0644-4")
    assert parsed == [RecordIdentifier(PUBMED_ID_KIND, "12601176"),
                      RecordIdentifier(DOI_KIND, "10.1038/s41589-020-0644-4")]


def test_a_doi_and_the_pubmed_id_of_the_same_paper_collapse_to_one_record():
    crosswalk = IdentifierCrosswalk(doi_by_pubmed_id={"33199904": "10.1038/s41589-020-0644-4"})
    result = deduplicate_reference_list("PMID:33199904;10.1038/s41589-020-0644-4", crosswalk)
    assert result.cited_count == 2
    assert result.distinct_count == 1
    assert result.inflation == 1
    assert len(result.merged_across_identifier_types) == 1


def test_a_paper_with_no_known_doi_keys_by_its_pubmed_id_and_never_merges_with_a_doi():
    """PMID 1279089 has no DOI in PubMed's own esummary. It must keep its own key, not join some DOI's record."""
    crosswalk = IdentifierCrosswalk(doi_by_pubmed_id={"33199904": "10.1038/s41589-020-0644-4"})
    result = deduplicate_reference_list("PMID:1279089;10.1038/s41589-020-0644-4", crosswalk)
    assert result.distinct_count == 2
    assert result.merged_across_identifier_types == {}


def test_two_services_disagreeing_on_a_doi_leaves_the_record_unmerged_rather_than_picking_one():
    """CLAUDE.md: a disagreement between sources is recorded beside the row, not settled silently."""
    crosswalk = IdentifierCrosswalk(
        disagreements={"1279089": ("10.1016/s0022-2275(20)40768-0", "10.1016/s0022-2275(99)00001-x")})
    result = deduplicate_reference_list("PMID:1279089;10.1016/s0022-2275(20)40768-0", crosswalk)
    assert result.distinct_count == 2
    assert result.merged_across_identifier_types == {}


def test_the_same_identifier_twice_is_reported_apart_from_a_cross_type_merge():
    """The two collapses mean different things: a repeat is a defect in the source's list, a merge is the crosswalk
    working. MAR04740 of Human-GEM names 30 tokens that are 3 papers."""
    result = deduplicate_reference_list("PMID:3443096;PMID:3443096;PMID:7759508", IdentifierCrosswalk())
    assert result.repeated_same_identifier == {"pubmed:3443096": 2}
    assert result.merged_across_identifier_types == {}
    assert result.distinct_count == 2


def test_a_pmc_id_resolves_through_its_pubmed_id_to_the_same_record_as_the_doi():
    crosswalk = IdentifierCrosswalk(doi_by_pubmed_id={"33199904": "10.1038/x"},
                                    pmc_id_by_pubmed_id={"33199904": "PMC7678813"})
    result = deduplicate_reference_list("PMC7678813;PMID:33199904;10.1038/x", crosswalk)
    assert result.distinct_count == 1


def test_an_empty_or_absent_reference_string_yields_nothing():
    for empty in ("", None, float("nan")):
        assert parse_record_identifiers(empty if isinstance(empty, str) else "") == []
    assert parse_resource_prefixed_references("") == []
