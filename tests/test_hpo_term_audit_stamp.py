"""The HPO term-expansion audit (experiments/audit_hpo_term_expansion.py) writes its page under a provenance stamp that
names its inputs and the HPO release, checked on a fixture ontology without the raw downloads."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from mechanistic_pathway_learning.documentation import REPOSITORY_ROOT, parse_stamp

sys.path.insert(0, str(REPOSITORY_ROOT / "experiments"))
from audit_hpo_term_expansion import obo_data_version  # noqa: E402

FIXTURE_ONTOLOGY = """format-version: 1.2
data-version: hp/releases/2026-09-01

[Term]
id: HP:0000001
name: All

[Term]
id: HP:0000716
name: Depression
is_a: HP:0000001 ! All

[Term]
id: HP:0000717
name: Fixture child of depression
is_a: HP:0000716 ! Depression
"""


def test_the_obo_data_version_is_read_from_the_header_and_only_there(tmp_path):
    with_header = tmp_path / "with_header.obo"
    with_header.write_text(FIXTURE_ONTOLOGY, encoding="utf-8")
    assert obo_data_version(with_header) == "hp/releases/2026-09-01"
    without_header = tmp_path / "without_header.obo"
    without_header.write_text("format-version: 1.2\n\n[Term]\nid: HP:0000001\nname: All\ndata-version: not a header\n", encoding="utf-8")
    assert obo_data_version(without_header) is None


def test_the_audit_page_carries_a_stamp_naming_its_inputs_and_the_hpo_release(tmp_path):
    ontology = tmp_path / "hp.obo"
    ontology.write_text(FIXTURE_ONTOLOGY, encoding="utf-8")
    annotations = tmp_path / "genes_to_phenotype.txt"
    annotations.write_text("ncbi_gene_id\tgene_symbol\thpo_id\thpo_name\tfrequency\tdisease_id\n"
                           "1\tGENEA\tHP:0000717\tFixture child of depression\t-\tOMIM:100000\n", encoding="utf-8")
    human_gem_genes = tmp_path / "genes.tsv"
    human_gem_genes.write_text("genes\tgeneSymbols\nENSG1\tGENEA\n", encoding="utf-8")
    crosswalk = tmp_path / "crosswalk.csv"
    crosswalk.write_text("target_symptom,hpo_ids,excluded_hpo_ids\ndepressed_mood,HP:0000716,\n", encoding="utf-8")
    page = tmp_path / "hpo_term_audit.md"
    subprocess.run([sys.executable, str(REPOSITORY_ROOT / "experiments" / "audit_hpo_term_expansion.py"), "--crosswalk", str(crosswalk),
                    "--hpo-obo", str(ontology), "--hpo-annotations", str(annotations), "--human-gem-genes", str(human_gem_genes),
                    "--markdown-output", str(page), "--json-output", str(tmp_path / "hpo_term_audit.json")],
                   check=True, cwd=REPOSITORY_ROOT, env={**os.environ, "PYTHONPATH": str(REPOSITORY_ROOT)}, capture_output=True)
    text = page.read_text(encoding="utf-8")
    stamp = parse_stamp(text)
    assert stamp is not None and stamp["generator"] == "experiments/audit_hpo_term_expansion.py"
    stamp_line = text.splitlines()[2]
    assert f"{ontology} (hp/releases/2026-09-01)" in stamp_line
    for input_path in (crosswalk, annotations, human_gem_genes):
        assert str(input_path) in stamp_line
    assert "| HP:0000717 | Fixture child of depression | descendant | 1 |" in text
