"""Observations of edge absence (and their presence counterparts) from sources other than IntAct, and the likelihood
ratio each takes into the edge prior (decision 9.91, 22 October 2026).

Why. The only negative edge evidence the edge priors carried was IntAct's curated non-interacting pairs
(graph/edge_negatives.py, a Beta update of fixed size). The owner asked for more sources of negative edge observations
and for each source's reliability to be measured, not fitted, since a fitted low sensitivity is what failed in
decisions 9.55 and 9.56, and that it "has to cover negatives and positives separately per source": a source's positive
reports and its negative reports each take their own rate.

What a source contributes. Each source module maps its observations onto the graph's edges and returns, per edge row,
`<source>_negative` and `<source>_positive` (the number of independent observations of each kind) and columns of its
own that say what was observed (a status, a detection limit, a cell line). The columns of every source are written into
the edge evidence table by experiments/build_edge_evidence.py (or added to an existing table by
experiments/build_edge_negative_evidence.py), one row per row of the graph's edges.parquet, so the trainer reads them
through the same row check as the rest of the table.

  negatome     Negatome 2.0: curated (manual) and structure-derived (PDB) non-interacting protein pairs; binds edges
               (graph/negatome_negatives.py)
  huri         HuRI's tested space: a pair of screened proteins HuRI did not detect is a negative, a detected pair a
               positive; binds edges only (graph/huri_tested_space.py)
  perturbseq   genome-wide Perturb-seq in K562 (Replogle et al. 2022): a factor knocked down with the target expressed
               and unchanged is a negative, a significant change a positive with its sign; regulation edges
               (graph/perturbseq_responses.py)
  chembl       ChEMBL 37 activity records on human single-protein targets: Inactive or Not Active, or a ">" value at a
               stated limit of at least 10 uM, is a negative, a measured potency of 10 uM or better a positive;
               metabolite-to-enzyme, small-molecule and drug edges (graph/chembl_activity_negatives.py)
  go_not       Gene Ontology NOT-qualified molecular functions that rule out an edge type out of the gene's protein
               (graph/go_not_annotations.py)

The likelihood ratio. configs/edge_negative_likelihood_ratios.csv holds, per source and kind of report, the probability
of that report when the edge is present and when it is absent, read from published measurements (the quotes and their
sources are in the table and below). The ratio is their quotient; a negative report's ratio is below 1 and a positive
report's above 1. `PUBLISHED` holds the published numbers and `derived_likelihood_ratios` the arithmetic from them to the
table, which tests/test_edge_negative_evidence.py holds the committed table to. Nothing in it is fitted.

  negatome negative   0.08 / 0.92. Smialowski et al. 2010 (doi 10.1093/nar/gkp1026) followed Negatome 1.0 against
                      IntAct over time: "the percentage of PDB non-interacting pairs contradicted by protein-protein
                      interaction data grew substantially from 0% in 1999 to 7% in 2002 where it stabilized,
                      oscillating between 6.5% and 8%", and for the manual set it "stabilized after increasing ... from 2
                      to 6% in 2004". Blohm et al. 2014 (doi 10.1093/nar/gkt1079), for Negatome 2.0: "The fraction of
                      non-interacting pairs removed by filtering against IntAct is thus 8%, 5% and 6% for the manual,
                      structure and merged dataset". The upper end, 8%, is read as the probability that an entry is wrong
                      whatever the pair's class (the report is right with probability 0.92 for an absent pair and wrong
                      with probability 0.08 for a present one). A contradiction rate is a precision, and turning a
                      precision into a ratio needs the base rate of the pairs Negatome draws from, which is not
                      published; this reading takes those pairs at even odds (put to the owner, decision 9.91). The
                      unfiltered text-mined candidates were "20%" correct (Blohm 2014); they are not in the database,
                      which holds only the manually verified pairs.
  huri negative       (1 - s) / (1 - f), huri positive s / f, for a pair inside the tested space. f is the false-report
                      rate of Y2H-CCSB per screen, "approximately eight out of every million non-interacting pairs tested
                      falsely report positive" (Venkatesan et al. 2009, doi 10.1038/nmeth.1280), times HuRI's nine
                      screens: 7.2e-5, an upper bound, since HuRI kept only pairs verified by retesting. s is the
                      sensitivity of the nine screens together: "HuRI is estimated to represent 2-11% of the binary
                      protein interactome" (Luck et al. 2020, doi 10.1038/s41586-020-2188-x), over a search space of
                      "~90% of the protein-coding genome", so 0.81 of the interactome's pairs if they are spread evenly;
                      s = 0.02 / 0.81 = 0.0247, the lower end, which gives the ratio nearest 1 on both sides. For
                      comparison, one screen of Y2H-CCSB detects a real pair with probability 0.17 x 0.53 = 0.09
                      ("assay sensitivity of Y2H-CCSB ... 17%", "sampling sensitivity per screen is 53%"), measured on a
                      reference set of well-studied pairs, against which HuRI's larger estimate of the interactome is
                      the reason the 2-11% is lower.
  perturbseq negative (1 - s) / (1 - f), positive s / f. s = 0.079: in siRNA knockdowns of 59 factors in a
                      lymphoblastoid line "the fraction of bound genes that were also differentially expressed in a
                      given experiment was generally quite low (median = 7.9%; ... mean relative enrichment = 1.02)",
                      with a median of 85.4% of expressed genes bound (Cusanovich et al. 2014, doi
                      10.1371/journal.pgen.1004226). Reading the enrichment as the bound genes' response rate over all
                      genes' response rate, the unbound genes respond at f = (s / 1.02 - 0.854 s) / 0.146 = 0.068.
                      Medians and a mean are combined, so f is approximate; at f = 0 the negative ratio would be 0.921,
                      and the 0.989 used here is the nearer to 1.
  chembl              negative e / (1 - e), positive (1 - e) / e. Landrum and Riniker 2024 (doi 10.1021/acs.jcim.4c00049)
                      compared pairs of ChEMBL assays measuring the same compound on the same target: binned at
                      pchembl 5 (10 uM) Cohen's kappa is 0.50 for IC50 and 0.40 for Ki under activity-only curation
                      (their Table 2), and "the confusion matrices are generally quite symmetric". Two assays that each
                      err with probability e whatever the truth agree with kappa at most (1 - 2e)^2 (the bound is
                      reached when half the pairs are active), so e is at most (1 - sqrt(kappa)) / 2: 0.184 at the
                      lower kappa, 0.40, which gives the ratio nearest 1.
  go_not              no published measurement of how often a NOT annotation is wrong was found (PubMed and Consensus
                      searched, 22 October 2026); the rows are blank, the ratio is 1 and the observations are recorded
                      without moving any prior until the owner names a measurement.

How the prior takes them. For a gated edge with prior probability p (graph/edge_evidence.py, edge_priors) the
observations of the sources asked for multiply its odds: logit p' = logit p + sum over sources and kinds of
min(n, cap) log ratio, with n the source's independent observations of that kind on the edge and cap the count cap of
the record side (2: Cusick et al. 2009 support the step from one independent publication to two, and little beyond).
A ratio applies only to the relations the table names for it. The pseudo-count n of the prior is unchanged: a
likelihood ratio says how far the evidence moves the belief, not how many observations stand behind the belief. An
ungated edge (a family without a tier) and an edge label (decision 9.63 (b)) are not moved; how many labels carry
negative observations is reported.
"""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_LIKELIHOOD_RATIOS_PATH = Path("configs/edge_negative_likelihood_ratios.csv")
SOURCES: tuple[str, ...] = ("negatome", "huri", "perturbseq", "chembl", "go_not")
REPORT_KINDS: tuple[str, ...] = ("negative", "positive")
DEFAULT_OBSERVATION_CAP = 2
PROBABILITY_FLOOR = 1e-4  # the edge prior is held inside [1e-4, 1 - 1e-4], as models/edge_gates.py holds it
LIKELIHOOD_RATIO_COLUMNS = ("source", "report", "applies_to_relations", "probability_given_present", "probability_given_absent", "likelihood_ratio",
                            "basis", "quote", "reference")

# The published numbers every ratio is computed from (the module docstring quotes each).
PUBLISHED = {
    "negatome_contradiction_rate": 0.08,  # Smialowski et al. 2010, "oscillating between 6.5% and 8%"; Blohm et al. 2014, "8%, 5% and 6%"
    "y2h_false_reports_per_screen": 8e-6,  # Venkatesan et al. 2009, "approximately eight out of every million non-interacting pairs"
    "huri_screens": 9,  # Luck et al. 2020, "We screened this search space a total of nine times"
    "huri_interactome_fraction": 0.02,  # Luck et al. 2020, "2-11% of the binary protein interactome": the lower end
    "huri_genome_fraction": 0.90,  # Luck et al. 2020, "the ORFeome collection to encompass ~90% of the protein-coding genome"
    "knockdown_bound_response": 0.079,  # Cusanovich et al. 2014, "median = 7.9%"
    "knockdown_relative_enrichment": 1.02,  # Cusanovich et al. 2014, "mean relative enrichment = 1.02"
    "knockdown_bound_fraction": 0.854,  # Cusanovich et al. 2014, "with a median of 85.4%"
    "chembl_kappa_at_10_um": 0.40,  # Landrum and Riniker 2024, Table 2: Ki, activity-only curation, pchembl 5
}
NEGATIVE_EVIDENCE_COLUMNS = tuple(f"{source}_{kind}" for source in SOURCES for kind in REPORT_KINDS)


@dataclass(frozen=True)
class LikelihoodRatio:
    source: str
    report: str
    relations: frozenset[str]
    probability_given_present: float | None
    probability_given_absent: float | None
    basis: str = ""
    quote: str = ""
    reference: str = ""

    @property
    def measured(self) -> bool:
        return self.probability_given_present is not None and self.probability_given_absent is not None

    @property
    def ratio(self) -> float:
        """The report's probability when the edge is present over its probability when it is absent; 1 when unmeasured."""
        return self.probability_given_present / self.probability_given_absent if self.measured else 1.0


def derived_likelihood_ratios(published: dict | None = None) -> dict[tuple[str, str], tuple[float | None, float | None]]:
    """(source, report) -> (probability of the report when the edge is present, when it is absent), computed from the
    published numbers; (None, None) where no measurement exists."""
    values = {**PUBLISHED, **(published or {})}
    contradiction = values["negatome_contradiction_rate"]
    huri_sensitivity = values["huri_interactome_fraction"] / values["huri_genome_fraction"] ** 2
    huri_false_reports = values["huri_screens"] * values["y2h_false_reports_per_screen"]
    knockdown_sensitivity = values["knockdown_bound_response"]
    any_gene_response = knockdown_sensitivity / values["knockdown_relative_enrichment"]
    bound = values["knockdown_bound_fraction"]
    knockdown_false_reports = (any_gene_response - bound * knockdown_sensitivity) / (1.0 - bound)
    chembl_error = (1.0 - math.sqrt(values["chembl_kappa_at_10_um"])) / 2.0
    return {("negatome", "negative"): (contradiction, 1.0 - contradiction),
            ("huri", "negative"): (1.0 - huri_sensitivity, 1.0 - huri_false_reports),
            ("huri", "positive"): (huri_sensitivity, huri_false_reports),
            ("perturbseq", "negative"): (1.0 - knockdown_sensitivity, 1.0 - knockdown_false_reports),
            ("perturbseq", "positive"): (knockdown_sensitivity, knockdown_false_reports),
            ("chembl", "negative"): (chembl_error, 1.0 - chembl_error),
            ("chembl", "positive"): (1.0 - chembl_error, chembl_error),
            ("go_not", "negative"): (None, None)}


def _probability(cell: str) -> float | None:
    text = (cell or "").strip()
    if not text:
        return None
    value = float(text)
    if not 0.0 < value <= 1.0:
        raise ValueError(f"a report probability must lie in (0, 1], not {value}")
    return value


def read_likelihood_ratios(path: Path = DEFAULT_LIKELIHOOD_RATIOS_PATH) -> dict[tuple[str, str], LikelihoodRatio]:
    """configs/edge_negative_likelihood_ratios.csv as {(source, report): LikelihoodRatio}. The table's likelihood_ratio
    column is for the reader and is checked against the two probabilities."""
    ratios = {}
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            source, report = row["source"].strip(), row["report"].strip()
            if source not in SOURCES or report not in REPORT_KINDS:
                raise ValueError(f"{path}: unknown source or report {source!r} {report!r}")
            ratio = LikelihoodRatio(source, report, frozenset(part.strip() for part in row["applies_to_relations"].split(";") if part.strip()),
                                    _probability(row["probability_given_present"]), _probability(row["probability_given_absent"]),
                                    row.get("basis", ""), row.get("quote", ""), row.get("reference", ""))
            stated = (row.get("likelihood_ratio") or "").strip()
            if ratio.measured and stated and not math.isclose(float(stated), ratio.ratio, rel_tol=1e-3):
                raise ValueError(f"{path}: {source} {report} states a ratio of {stated}, its probabilities give {ratio.ratio:.6g}")
            ratios[(source, report)] = ratio
    return ratios


def empty_negative_evidence(rows: int, index=None) -> pd.DataFrame:
    """The two count columns of every source, all zero."""
    return pd.DataFrame({column: np.zeros(rows, dtype=np.int64) for column in NEGATIVE_EVIDENCE_COLUMNS}, index=index)


def log_likelihood_ratio(evidence: pd.DataFrame, ratios: dict[tuple[str, str], LikelihoodRatio], sources: tuple[str, ...] | list[str],
                         observation_cap: int = DEFAULT_OBSERVATION_CAP) -> tuple[np.ndarray, dict]:
    """Per edge, the summed log likelihood ratio of the observations of the sources asked for, each source and kind
    taking min(n, cap) observations at its ratio on the relations the table names for it; with what each source and kind
    contributed. A source whose columns the table lacks is refused, since a missing column is not an absence of
    observations."""
    total = np.zeros(len(evidence))
    relation = evidence["relation_type"].astype(str).to_numpy() if "relation_type" in evidence.columns else np.full(len(evidence), "", dtype=object)
    contributions = {}
    for source in sources:
        if source not in SOURCES:
            raise ValueError(f"unknown negative evidence source {source!r}; the sources are {SOURCES}")
        for kind in REPORT_KINDS:
            column = f"{source}_{kind}"
            if column not in evidence.columns:
                raise ValueError(f"the edge evidence table has no {column} column; add the {source} columns with experiments/build_edge_negative_evidence.py")
            counts = np.minimum(evidence[column].fillna(0).to_numpy(dtype=float), float(observation_cap))
            ratio = ratios.get((source, kind))
            applies = np.isin(relation, sorted(ratio.relations)) if ratio is not None else np.zeros(len(evidence), dtype=bool)
            observed = counts > 0
            if ratio is None or not ratio.measured:
                contributions[column] = {"edges_observed": int(observed.sum()), "edges_moved": 0, "ratio": None,
                                         "why_not_applied": "no published measurement in the table" if ratio is not None else "no row in the table"}
                continue
            moved = observed & applies
            total += np.where(moved, counts * math.log(ratio.ratio), 0.0)
            contributions[column] = {"edges_observed": int(observed.sum()), "edges_moved": int(moved.sum()), "ratio": ratio.ratio,
                                     "observed_on_relations_the_ratio_does_not_cover": int((observed & ~applies).sum())}
    return total, contributions


def apply_likelihood_ratios(probability: np.ndarray, gated: np.ndarray, log_ratio: np.ndarray) -> np.ndarray:
    """logit p' = logit p + log ratio on the gated edges, the result held inside [PROBABILITY_FLOOR, 1 - PROBABILITY_FLOOR];
    ungated edges keep their NaN."""
    probability = np.array(probability, dtype=float, copy=True)
    moved = np.asarray(gated, dtype=bool) & (np.asarray(log_ratio) != 0.0)
    if moved.any():
        held = np.clip(probability[moved], PROBABILITY_FLOOR, 1.0 - PROBABILITY_FLOOR)
        logit = np.log(held) - np.log1p(-held) + np.asarray(log_ratio)[moved]
        probability[moved] = np.clip(1.0 / (1.0 + np.exp(-logit)), PROBABILITY_FLOOR, 1.0 - PROBABILITY_FLOOR)
    return probability


def summarise_negative_evidence(evidence: pd.DataFrame) -> dict:
    """Per source: edges with negative and with positive observations, by family and relation, and the observations."""
    summary = {}
    family = evidence["family"].astype(str) if "family" in evidence.columns else pd.Series("", index=evidence.index)
    relation = evidence["relation_type"].astype(str) if "relation_type" in evidence.columns else pd.Series("", index=evidence.index)
    for source in SOURCES:
        if f"{source}_negative" not in evidence.columns:
            continue
        entry = {}
        for kind in REPORT_KINDS:
            counts = evidence[f"{source}_{kind}"].fillna(0).astype(int)
            observed = counts > 0
            entry[kind] = {"edges": int(observed.sum()), "observations": int(counts.sum()),
                           "by_family_and_relation": {f"{f}:{r}": int(n) for (f, r), n in
                                                      pd.DataFrame({"f": family[observed], "r": relation[observed]}).value_counts().sort_index().items()}}
        summary[source] = entry
    return summary
