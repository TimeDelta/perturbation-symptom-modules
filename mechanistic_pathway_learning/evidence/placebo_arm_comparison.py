"""Is a drug-label event more frequent on the drug than on placebo? (label source review of 10 October 2026)

SIDER's meddra_freq.tsv.gz gives, for some labels, the frequency of an event in the drug arm and in the placebo arm of
the same trials. The evidence table reads the drug arm alone, so an event listed at 4 percent on the drug and 6
percent on placebo is a positive like any other; docs/evidence_reports_spec.md records the gap ("A treatment frequency
at or below the placebo frequency is not counted as evidence against"). This module makes the comparison, and
experiments/build_label_selection.py --mask-never-above-placebo sets aside the pairs it finds.

The comparison is made inside one label and one preferred term at a time, because only those two arms come from the
same trials and count the same event. A (drug, symptom) pair is "never above placebo" when at least one of its
(label, preferred term) entries gives both arms and in none of them the drug arm's mean frequency is above the placebo
arm's. A pair with no placebo arm anywhere is not judged.

Only rows that state a number enter an arm (decision 9.124, the owner, 8 November 2026: "Non-numeric bands exclusion
accepted"). SIDER gives a qualitative band a range ("common" 0.01 to 1.0, "rare" 0 to 0.001), and its midpoint is not a
frequency: "common" entered an arm as 0.505, so entacapone's parkinsonism arm, 13.9 percent beside a "common" row,
averaged 32 percent against placebo's 14.8 and was read as above placebo. Numeric rows that are themselves intervals
("<1%", stored as 0 to 0.01; "1-10%") still enter at their midpoints.
"""
from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import dataclass

from mechanistic_pathway_learning.evidence.load_drug_label_events import SiderFrequencyRow


def states_a_number(frequency_row: SiderFrequencyRow) -> bool:
    """True when the row's frequency text holds a digit ("13.9%", "<1%", "1-10%"); False for a qualitative band
    ("common", "rare", "postmarketing"), whose range is a category and not a measured frequency."""
    return re.search(r"\d", frequency_row.frequency_text) is not None


@dataclass(frozen=True)
class PlaceboArmComparison:
    """Over the (label, preferred term) entries of one (drug, symptom) pair that give a drug arm and a placebo arm."""

    entries_with_both_arms: int
    entries_with_drug_arm_above: int

    @property
    def never_above_placebo(self) -> bool:
        return self.entries_with_both_arms > 0 and self.entries_with_drug_arm_above == 0


def compare_drug_arm_with_placebo_arm(
    frequency_rows_by_pair: Mapping[tuple[str, str], list[SiderFrequencyRow]],
    preferred_term_to_symptom: Mapping[str, str],
) -> dict[tuple[str, str], PlaceboArmComparison]:
    """(STITCH flat id, target symptom) -> the comparison, for every pair with an entry that gives both arms.

    frequency_rows_by_pair is load_sider_frequency_rows' result, keyed by (STITCH flat id, preferred term lowercase);
    preferred_term_to_symptom is read_preferred_term_to_target_symptom's. An arm's frequency in an entry is the mean of
    the range midpoints of its rows that state a number (states_a_number); an entry whose rows in one arm are all
    qualitative has no frequency in that arm and is not compared.
    """
    arm_midpoints: dict[tuple[str, str, str, str], tuple[list[float], list[float]]] = defaultdict(lambda: ([], []))
    for (stitch_flat_id, preferred_term), frequency_rows in frequency_rows_by_pair.items():
        target_symptom = preferred_term_to_symptom.get(preferred_term)
        if target_symptom is None:
            continue
        for frequency_row in frequency_rows:
            if not states_a_number(frequency_row):
                continue
            drug_arm, placebo_arm = arm_midpoints[(stitch_flat_id, target_symptom, frequency_row.label_cui, preferred_term)]
            (placebo_arm if frequency_row.is_placebo else drug_arm).append(frequency_row.midpoint)
    entries_with_both_arms: dict[tuple[str, str], int] = defaultdict(int)
    entries_with_drug_arm_above: dict[tuple[str, str], int] = defaultdict(int)
    for (stitch_flat_id, target_symptom, _, _), (drug_arm, placebo_arm) in arm_midpoints.items():
        if not drug_arm or not placebo_arm:
            continue
        entries_with_both_arms[(stitch_flat_id, target_symptom)] += 1
        if sum(drug_arm) / len(drug_arm) > sum(placebo_arm) / len(placebo_arm):
            entries_with_drug_arm_above[(stitch_flat_id, target_symptom)] += 1
    return {pair: PlaceboArmComparison(entry_count, entries_with_drug_arm_above.get(pair, 0)) for pair, entry_count in entries_with_both_arms.items()}


def pairs_never_above_placebo(comparisons: Mapping[tuple[str, str], PlaceboArmComparison]) -> set[tuple[str, str]]:
    return {pair for pair, comparison in comparisons.items() if comparison.never_above_placebo}
