"""Expand configs/admitted_receptor_g_alpha_coupling.csv from its receptor-family rows to the family's member genes.

GtoPdb annotates a receptor's primary and secondary transducers by G-protein family (Gs, Gi/o, Gq/11, G12/13), and
decision 9.23 admits a receptor-to-G-alpha edge when the G alpha gene is a member of an annotated family. The table
was written once with the families expanded by hand to GNAS and GNAL, GNAI1 to GNAI3 with GNAO1 and GNAZ, GNAQ and
GNA11, and GNA12 and GNA13. That left out GNA14 and GNA15 from Gq/11 and the transducins GNAT1 to GNAT3 from Gi/o,
so the filter never saw an edge into them (decision 9.86, measured on v5 on 20 October 2026: 142 signed edges from
annotated receptors into those four genes, 24 receptors into GNA14 and 2 into GNA15 from receptors annotated for
another family).

What `primary_pubmed_id` is (the owner, 26 October 2026, decision 9.99: "have the rows cite whatever is supported").
It is the evidence for the row it sits on: the papers that support that receptor coupling to that G-protein family in
that role. What every run before 26 October 2026 held instead was GPCRdb's `primary_PMID` field verbatim, one list per
receptor, which this expansion copies onto every row of that receptor, so a paper was attached to couplings it does not
support. HRH2 was the case found: all six of its rows cited `8961278|2553705`, and PMID 2553705 (Mitsuhashi et al.
1989) concludes that the H2 calcium response is "inhibited by cholera toxin but not by pertussis toxin", which excludes
Gq/11, so its four Gq/11 rows now cite 8961278 alone (Kuehn et al. 1996, which reports H2 labelling of alpha q and
alpha 11) while its two Gs rows keep both. A receptor whose list has not been checked row by row still carries
GPCRdb's field as before: 84 of the 253 receptors share one multi-PMID list across two or more family or role groups,
the shape of the HRH2 defect, and are owed that check (decision 9.99).

The members are read from HGNC's gene groups rather than kept by hand: group 1426 "G protein subunits alpha, group
s", 1428 "group i", 1427 "group q" and 1429 "group 12/13", from the pinned data/raw/hgnc/hgnc_complete_set.txt. The
table keeps its columns, its ids and its row order (receptor, then G alpha gene).

Usage:
  python experiments/expand_receptor_g_alpha_families.py            # rewrites the table
  python experiments/expand_receptor_g_alpha_families.py --check    # fails if the table is not the expansion
"""
from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path

import pandas as pd

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TABLE_PATH = REPOSITORY_ROOT / "configs" / "admitted_receptor_g_alpha_coupling.csv"
HGNC_PATH = REPOSITORY_ROOT / "data" / "raw" / "hgnc" / "hgnc_complete_set.txt"
HGNC_GROUP_OF_FAMILY = {"Gs": "1426", "Gi/o": "1428", "Gq/11": "1427", "G12/13": "1429"}
FAMILY_ROW_COLUMNS = ["receptor_gene_symbol", "g_alpha_family", "transducer_role", "iuphar_target_id", "primary_pubmed_id"]


def members_from_hgnc(hgnc_path: Path) -> dict[str, list[str]]:
    """{family: sorted member symbols} from the HGNC gene group ids of HGNC_GROUP_OF_FAMILY."""
    table = pd.read_csv(hgnc_path, sep="\t", usecols=["symbol", "gene_group_id", "locus_group"], dtype=str, keep_default_na=False)
    members: dict[str, list[str]] = {}
    for family, group_id in HGNC_GROUP_OF_FAMILY.items():
        in_group = table.gene_group_id.str.split("|").apply(lambda ids: group_id in ids)
        members[family] = sorted(table.loc[in_group & table.locus_group.eq("protein-coding gene"), "symbol"])
        if not members[family]:
            raise ValueError(f"HGNC gene group {group_id} ({family}) has no protein-coding member in {hgnc_path}")
    return members


def expanded_table(table: pd.DataFrame, members: dict[str, list[str]]) -> pd.DataFrame:
    """The table with each receptor-family-role group replaced by one row per member gene of the family."""
    family_rows = table[FAMILY_ROW_COLUMNS].drop_duplicates()
    if family_rows.duplicated(["receptor_gene_symbol", "g_alpha_family", "transducer_role"]).any():
        raise ValueError("a receptor-family-role group carries more than one target id or reference; the table cannot be expanded unambiguously")
    unknown = set(family_rows.g_alpha_family) - set(members)
    if unknown:
        raise ValueError(f"families with no member list: {sorted(unknown)}")
    rows = [{**row, "g_alpha_gene_symbol": gene} for row in family_rows.to_dict(orient="records") for gene in members[row["g_alpha_family"]]]
    expanded = pd.DataFrame(rows, columns=list(table.columns))
    return expanded.sort_values(["receptor_gene_symbol", "g_alpha_gene_symbol"], kind="stable").reset_index(drop=True)


def as_csv_text(table: pd.DataFrame) -> str:
    buffer = io.StringIO()
    table.to_csv(buffer, index=False, lineterminator="\n", quoting=csv.QUOTE_MINIMAL)
    return buffer.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--table", type=Path, default=TABLE_PATH)
    parser.add_argument("--hgnc", type=Path, default=HGNC_PATH)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    table = pd.read_csv(arguments.table, dtype=str, keep_default_na=False)
    members = members_from_hgnc(arguments.hgnc)
    text = as_csv_text(expanded_table(table, members))
    if arguments.check:
        if text != arguments.table.read_text(encoding="utf-8"):
            sys.exit(f"{arguments.table} is not the expansion of its family rows over HGNC's members; run this script without --check")
        print(f"{arguments.table} is the expansion ({text.count(chr(10)) - 1} rows)")
        return
    arguments.table.write_text(text, encoding="utf-8")
    print(f"wrote {arguments.table}: {text.count(chr(10)) - 1} rows; members {members}")


if __name__ == "__main__":
    main()
