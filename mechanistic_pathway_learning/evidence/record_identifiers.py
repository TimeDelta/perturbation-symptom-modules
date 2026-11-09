"""Literature record identifiers, resolved to each other so that one paper counts once (the owner, 9 November 2026:
"just make it so that it tries to convert whichever id exists to all other types and check each list for duplicates").

Why the module exists. A count of distinct records is the currency of every row of `configs/edge_prior_tiers.csv`: the
strength of an edge's prior is `unit_strength * min(n, cap) ** tempering` over its distinct records
(`graph/edge_evidence.py`, `evidence/soft_priors.py`), and the edge-label rule of decision 9.63 (b) asks for at least
two. So a paper counted twice buys an edge strength it has not earned, and it does so on exactly the edges whose
evidence looks strongest. Two ways that happens today:

  - **the same identifier twice in one list.** Human-GEM writes reaction references as a semicolon-joined string and
    some strings repeat an id (MAR01417's list names PMID:16919238 at positions 1 and 6). Nothing deduplicates them.
  - **one paper under two identifier types.** A source that cites a DOI and a source that cites the PubMed id of the
    same paper are two records to a counter that compares strings. PubMed covers the biology and misses the methods
    and resource literature, so the project's own bibliography already holds 167 entries with a DOI and no PubMed id
    (`docs/references.bib`, measured 9 November 2026), and a curated row may cite either.

What a record is here. One published work, named by any of three identifier types: a PubMed id, a DOI or a PMC id. The
crosswalk `data/raw/record_identifiers/record_identifier_crosswalk.parquet` holds, per PubMed id, the DOI and PMC id
that PubMed's own esummary and Europe PMC report, each kept separately so that a disagreement between the two is
recorded rather than settled silently (CLAUDE.md, "a disagreement between sources is recorded beside the row").
`experiments/fetch_record_identifier_crosswalk.py` builds it.

The canonical key, and why a missing DOI is not a problem. A record's key is its DOI when one is known, and otherwise
the identifier it was cited by. That cannot collide: a work with no DOI cannot be cited by DOI, so a work keyed by its
PubMed id is never the same work as one keyed by a DOI. The converse case, a work cited by DOI by one source and by
PubMed id by another, is exactly what the crosswalk collapses. What this does NOT do is rescue a work with no
identifier at all: the agency labels and product monographs of `configs/curated_label_events.csv` and
`configs/curated_drug_targets.csv` name a label address, a CIS number and a content hash, which no crosswalk reaches.
Those are a separate question and are not records here.

What this module does not decide. Whether a DOI-only record may count toward a tier's strength, and whether it may
satisfy the human-evidence half of the edge-label rule, are the owner's to rule: iCite's species scores are keyed on
PubMed id alone (`experiments/fetch_icite_species.py`), so a record with no PubMed id can carry strength but cannot be
shown to be human evidence. This module reports what the identifiers are and which collapse; it sets no prior.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

CROSSWALK_PATH = Path("data/raw/record_identifiers/record_identifier_crosswalk.parquet")

PUBMED_ID_KIND, DOI_KIND, PMC_ID_KIND = "pubmed", "doi", "pmcid"

# Human-GEM writes "PMID:123" and, in nine tokens of release 2.0.1, "PubMed:123"; OmniPath and CollecTRI write bare
# digits in a separator-joined field; this project's curated rows write "PMID 123" inside a prose evidence_source.
PUBMED_ID_PATTERN = re.compile(r"\b(?:PMID|PubMed|pubmed)\s*[:=]?\s*(\d{1,9})\b")
# A DOI is "10." then a registrant code, a slash and a suffix. The suffix may hold almost anything, so the pattern
# stops at whitespace, a semicolon or a closing bracket, and trailing sentence punctuation is stripped afterwards.
DOI_PATTERN = re.compile(r"\b(10\.\d{4,9}/[^\s;,)\]}<>\"']+)")
PMC_ID_PATTERN = re.compile(r"\b(PMC\d{4,9})\b", re.IGNORECASE)
TRAILING_PUNCTUATION = ".,;:)]}>\"'"


@dataclass(frozen=True)
class RecordIdentifier:
    """One identifier as it was cited, normalised but not yet resolved against the crosswalk."""

    kind: str
    value: str

    def __str__(self) -> str:
        return f"{self.kind}:{self.value}"


def normalise_doi(raw_doi: str) -> str:
    """A DOI in the form used as a key: the bare "10.x/y", lowercased.

    Lowercased because a DOI is case-insensitive by its specification, so "10.1038/S41589" and "10.1038/s41589" are
    one work and must share a key. Any resolver prefix and trailing sentence punctuation are stripped.
    """
    cleaned = raw_doi.strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "http://dx.doi.org/", "doi:", "DOI:"):
        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix):]
    return cleaned.strip().rstrip(TRAILING_PUNCTUATION).lower()


def normalise_pubmed_id(raw_pubmed_id: str) -> str:
    """A PubMed id as a key: digits with no leading zeros, so "0012345" and "12345" are one work."""
    digits = raw_pubmed_id.strip().lstrip("0")
    return digits or "0"


def normalise_pmc_id(raw_pmc_id: str) -> str:
    """A PMC id as a key: upper-case "PMC" and the digits."""
    return "PMC" + re.sub(r"\D", "", raw_pmc_id)


def parse_record_identifiers(reference_text: str) -> list[RecordIdentifier]:
    """Every identifier a reference string names, in the order cited, keeping repeats so a caller can see them.

    Handles the four shapes the project's sources use: Human-GEM's "PMID:1;PMID:2" (and its nine "PubMed:" tokens),
    a prose evidence_source naming "PMID 123", a DOI with or without a resolver prefix, and a PMC id. An empty token
    such as Human-GEM's "PMID:" yields nothing.
    """
    if not reference_text:
        return []
    text = str(reference_text)
    identifiers: list[tuple[int, RecordIdentifier]] = []
    for match in DOI_PATTERN.finditer(text):
        identifiers.append((match.start(), RecordIdentifier(DOI_KIND, normalise_doi(match.group(1)))))
    doi_spans = [(m.start(), m.end()) for m in DOI_PATTERN.finditer(text)]

    def inside_a_doi(position: int) -> bool:
        return any(start <= position < end for start, end in doi_spans)

    for match in PUBMED_ID_PATTERN.finditer(text):
        if not inside_a_doi(match.start(1)):
            identifiers.append((match.start(), RecordIdentifier(PUBMED_ID_KIND, normalise_pubmed_id(match.group(1)))))
    for match in PMC_ID_PATTERN.finditer(text):
        if not inside_a_doi(match.start(1)):
            identifiers.append((match.start(), RecordIdentifier(PMC_ID_KIND, normalise_pmc_id(match.group(1)))))
    return [identifier for _, identifier in sorted(identifiers, key=lambda pair: pair[0])]


# A `references` column of OmniPath or CollecTRI is "Resource:PMID;Resource:PMID", where the same PubMed id recurs
# under several resource prefixes (one CollecTRI row names 10022869 as CollecTRI, CollecTRI2, DoRothEA and TRRUST).
# `graph/edge_evidence.py:pmids_of` already collapses those into a set, so this function exists to read the same
# shape here, not to repair a defect. It is kept apart from parse_record_identifiers because the bare "word:digits"
# form is only safe where the column's format is known: in prose it would read the "56:83" of a journal citation
# such as "J Neural Transm Suppl 56:83-105", or a CIS number, as an identifier.
RESOURCE_PREFIXED_PUBMED_ID = re.compile(r"^[A-Za-z][\w.+-]*:(\d{1,9})$")


def parse_resource_prefixed_references(reference_cell: str) -> list[RecordIdentifier]:
    """Every identifier a "Resource:PMID;..." cell names, in order, keeping repeats.

    Tokens that are not of that shape are passed to parse_record_identifiers, so a cell that mixes the resource form
    with a DOI or a bare "PMID:123" is read whole rather than partly.
    """
    if not reference_cell or not isinstance(reference_cell, str):
        return []
    identifiers: list[RecordIdentifier] = []
    for token in reference_cell.split(";"):
        token = token.strip()
        if not token:
            continue
        match = RESOURCE_PREFIXED_PUBMED_ID.match(token)
        if match:
            identifiers.append(RecordIdentifier(PUBMED_ID_KIND, normalise_pubmed_id(match.group(1))))
        else:
            identifiers.extend(parse_record_identifiers(token))
    return identifiers


@dataclass
class IdentifierCrosswalk:
    """Which identifiers name the same work, as the two services report them.

    `doi_by_pubmed_id` and `pmc_id_by_pubmed_id` hold the agreed value; `disagreements` names the PubMed ids where
    PubMed's esummary and Europe PMC gave different DOIs, which are left unresolved rather than picked between.
    """

    doi_by_pubmed_id: dict[str, str] = field(default_factory=dict)
    pmc_id_by_pubmed_id: dict[str, str] = field(default_factory=dict)
    disagreements: dict[str, tuple[str, str]] = field(default_factory=dict)

    def pubmed_id_by_doi(self) -> dict[str, str]:
        return {doi: pubmed_id for pubmed_id, doi in self.doi_by_pubmed_id.items()}

    def canonical_key(self, identifier: RecordIdentifier) -> str:
        """The key this identifier's work counts under: its DOI when one is known, else the identifier itself.

        A work with no DOI cannot be cited by DOI, so keying it by its PubMed or PMC id never collides with a work
        keyed by a DOI. A PubMed id whose two services disagree keeps its own key, so a disagreement never merges two
        works nor splits one silently: it shows up as an unresolved record the caller can report.
        """
        if identifier.kind == DOI_KIND:
            return f"{DOI_KIND}:{identifier.value}"
        if identifier.kind == PUBMED_ID_KIND:
            if identifier.value in self.disagreements:
                return str(identifier)
            doi = self.doi_by_pubmed_id.get(identifier.value)
            return f"{DOI_KIND}:{doi}" if doi else str(identifier)
        if identifier.kind == PMC_ID_KIND:
            for pubmed_id, pmc_id in self.pmc_id_by_pubmed_id.items():
                if pmc_id == identifier.value:
                    return self.canonical_key(RecordIdentifier(PUBMED_ID_KIND, pubmed_id))
        return str(identifier)


def read_identifier_crosswalk(path: Path = CROSSWALK_PATH) -> IdentifierCrosswalk:
    """The crosswalk parquet as an IdentifierCrosswalk; an absent file gives an empty one, under which every
    identifier keys as itself and only same-type repeats are found."""
    crosswalk = IdentifierCrosswalk()
    if not path.exists():
        return crosswalk
    import pandas as pd

    table = pd.read_parquet(path)
    for row in table.itertuples(index=False):
        pubmed_id = normalise_pubmed_id(str(row.pubmed_id))
        pubmed_service_doi = normalise_doi(str(getattr(row, "pubmed_service_doi", "") or ""))
        europepmc_doi = normalise_doi(str(getattr(row, "europepmc_doi", "") or ""))
        if pubmed_service_doi and europepmc_doi and pubmed_service_doi != europepmc_doi:
            crosswalk.disagreements[pubmed_id] = (pubmed_service_doi, europepmc_doi)
        elif pubmed_service_doi or europepmc_doi:
            crosswalk.doi_by_pubmed_id[pubmed_id] = pubmed_service_doi or europepmc_doi
        pmc_id = str(getattr(row, "pmc_id", "") or "")
        if pmc_id and pmc_id.lower() not in ("none", "nan"):
            crosswalk.pmc_id_by_pubmed_id[pubmed_id] = normalise_pmc_id(pmc_id)
    return crosswalk


@dataclass
class DeduplicatedRecordList:
    """One reference list after resolution: the works it names, and what collapsed."""

    cited: list[RecordIdentifier]
    distinct_keys: list[str]
    repeated_same_identifier: dict[str, int]
    merged_across_identifier_types: dict[str, list[RecordIdentifier]]
    unresolved_pubmed_ids: list[str]

    @property
    def cited_count(self) -> int:
        """How many records a counter comparing strings would see."""
        return len({str(identifier) for identifier in self.cited})

    @property
    def distinct_count(self) -> int:
        """How many works the list actually names."""
        return len(self.distinct_keys)

    @property
    def inflation(self) -> int:
        """Records the naive count would have over-counted."""
        return self.cited_count - self.distinct_count


def deduplicate_reference_list(reference_text: str, crosswalk: IdentifierCrosswalk) -> DeduplicatedRecordList:
    """Resolve a reference string to the distinct works it names, reporting every collapse.

    Two kinds of collapse are reported apart, because they mean different things: the same identifier cited twice is a
    defect in the source's own list, while two identifier types resolving to one work is the crosswalk doing its job.
    """
    cited = parse_record_identifiers(reference_text)
    occurrences_by_identifier: dict[str, int] = {}
    for identifier in cited:
        occurrences_by_identifier[str(identifier)] = occurrences_by_identifier.get(str(identifier), 0) + 1
    identifiers_by_key: dict[str, list[RecordIdentifier]] = {}
    for identifier in cited:
        key = crosswalk.canonical_key(identifier)
        if identifier not in identifiers_by_key.setdefault(key, []):
            identifiers_by_key[key].append(identifier)
    return DeduplicatedRecordList(
        cited=cited,
        distinct_keys=list(identifiers_by_key),
        repeated_same_identifier={name: count for name, count in occurrences_by_identifier.items() if count > 1},
        merged_across_identifier_types={key: group for key, group in identifiers_by_key.items() if len(group) > 1},
        unresolved_pubmed_ids=[identifier.value for identifier in cited if identifier.kind == PUBMED_ID_KIND
                               and identifier.value not in crosswalk.doi_by_pubmed_id],
    )
