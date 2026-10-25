"""SIDER drug names that are not names, and the names that replace them (decision 9.93, 24 October 2026).

SIDER 4.1's drug_names.tsv gives some drugs a truncated or coded name: it cuts a development code at its first space
(vortioxetine, PubChem CID 9966051, is "Lu", from Lu AA21004; fulvestrant is "ICI", from ICI 182,780) or keeps the code
itself (enzalutamide is "MDV3100"). Every SIDER and OnSIDES report table took its perturbation_label from that file, so
the v5 label table named vortioxetine "Lu". configs/sider_drug_name_corrections.csv lists each such name with the name
that replaces it and where that name was read (ChEMBL 37's pinned files, or the ChEMBL connector), and this module is
the one place both label loaders read SIDER names through.

Which names were looked at: every drug_names.tsv name of four characters or fewer, or shaped like a development code
(up to four letters, then three or more digits), 62 of 1,430 on 24 October 2026. A name in use as a name was left as it
is (PGE2, DMSO, EDTA, 5-FU, zinc, iron); a truncation or code was corrected where ChEMBL gave a preferred name for the
CID. Left uncorrected because no ChEMBL preferred name was found: v (CID 2909), NSC (54949), CAS (65281), Glat (65370),
SU5416 (123015), ALX (3325225), PEP005 (6918670), LY146032 (16129629), o291 (16158473), n-3 (56842239),
x (70683024) and K779 (71306834). PubChem, the other source for a CID's name, was not read: its robots file disallows
the /rest/ path for automated readers (read 24 October 2026), a refusal this project respects. None of the
uncorrected drugs is in the v5 evidence tables.
"""
from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path

DEFAULT_CORRECTIONS_PATH = Path(__file__).resolve().parents[2] / "configs" / "sider_drug_name_corrections.csv"


@lru_cache(maxsize=4)
def read_corrections(path: Path = DEFAULT_CORRECTIONS_PATH) -> dict[str, tuple[str, str]]:
    """STITCH flat id -> (SIDER's name, the corrected name)."""
    with open(path, newline="", encoding="utf-8") as handle:
        return {row["stitch_flat_id"].strip(): (row["sider_name"].strip(), row["corrected_name"].strip()) for row in csv.DictReader(handle)}


def readable_drug_name(stitch_flat_id: str | None, sider_name: str | None, path: Path = DEFAULT_CORRECTIONS_PATH) -> str | None:
    """The corrected name where the corrections list SIDER's name for this drug, else SIDER's name. A correction applies
    only while SIDER still gives the name it was written against, so a later SIDER release that fixes the name wins."""
    if stitch_flat_id is None or sider_name is None:
        return sider_name
    correction = read_corrections(path).get(str(stitch_flat_id).strip())
    if correction is None or correction[0] != str(sider_name).strip():
        return sider_name
    return correction[1]


def corrected_drug_names(drug_names: dict[str, str], path: Path = DEFAULT_CORRECTIONS_PATH) -> dict[str, str]:
    """drug_names.tsv as {STITCH flat id: name} with the corrections applied."""
    return {stitch_flat_id: readable_drug_name(stitch_flat_id, name, path) for stitch_flat_id, name in drug_names.items()}
