"""Which special-population subgroups the carrier reading uses.

Every subgroup is read (decision 9.89). From 10 to 22 October 2026 the reading left out newborn through toddler on the
owner's ruling of 10 October ("Only NEWBORN through TODDLER"); the owner withdrew it on 22 October 2026: "that old
decision doesn't apply now that I've included neurodevelopment". The band stays a named stratum so its own reading is
reported, and --excluded-subgroups can still leave subgroups out of a run.
"""
import math

import pandas as pd

from experiments.measure_special_population_carrier_signal import (DEFAULT_EXCLUDED_SUBGROUPS, NEWBORN_THROUGH_TODDLER_SUBGROUPS,
                                                                   leave_one_drug_out_predictions, population_readings)

NEWBORN_THROUGH_TODDLER = {name.lower() for name in NEWBORN_THROUGH_TODDLER_SUBGROUPS}


def rows_with_subgroups(subgroups: list[str]) -> pd.DataFrame:
    """Two carriers per subgroup, enough for a reading, with the ratio ordered so orosomucoid sits above albumin."""
    collected = []
    for index, subgroup in enumerate(subgroups):
        for carrier, ratio in (("albumin", 0.9), ("orosomucoid", 1.4)):
            collected.append({"carrier": carrier, "drug": f"{carrier}_drug_{index}", "subgroup": subgroup,
                              "population": "paediatric", "fraction_unbound_reference": 0.1,
                              "fraction_unbound_special": 0.1 * ratio, "log_ratio": math.log(ratio)})
    return pd.DataFrame(collected)


def without(rows: pd.DataFrame, excluded_subgroups) -> pd.DataFrame:
    excluded_names = {name.lower() for name in excluded_subgroups}
    return rows[~rows.subgroup.str.strip().str.lower().isin(excluded_names)]


def test_no_subgroup_is_left_out_by_default():
    assert tuple(DEFAULT_EXCLUDED_SUBGROUPS) == ()
    rows = rows_with_subgroups(["Neonate", "Infant", "Toddler", "School age"])
    assert len(without(rows, DEFAULT_EXCLUDED_SUBGROUPS)) == len(rows)


def test_the_newborn_through_toddler_band_is_named_as_a_stratum():
    for subgroup in ("Neonate", "Newborn", "Preterm", "Infant", "Toddler"):
        assert subgroup.lower() in NEWBORN_THROUGH_TODDLER, subgroup
    for subgroup in ("Child", "School age", "Adolescent", "Preschool"):
        assert subgroup.lower() not in NEWBORN_THROUGH_TODDLER, subgroup


def test_the_band_gives_a_reading_of_its_own():
    rows = rows_with_subgroups(["Neonate", "Infant", "School age"])
    band_rows = rows[rows.subgroup.str.lower().isin(NEWBORN_THROUGH_TODDLER)]
    readings = population_readings(band_rows)
    assert len(readings) == 1
    assert int(readings.iloc[0].measurements) == 4


def test_a_run_can_still_leave_subgroups_out():
    rows = rows_with_subgroups(["Neonate", "Infant", "School age"])
    assert set(without(rows, NEWBORN_THROUGH_TODDLER_SUBGROUPS).subgroup) == {"School age"}


def test_every_subgroup_reaches_the_classifier_by_default():
    rows = rows_with_subgroups(["Neonate", "Infant"])
    assert len(leave_one_drug_out_predictions(without(rows, DEFAULT_EXCLUDED_SUBGROUPS).reset_index(drop=True))) > 0
