"""Measure the mouse report sources of decision 9.93 against a label selection, fit the calibrated reliability regression
with and without them, and write the generated record docs/mouse_sources_measured_v5.md.

For each mouse source (IMPC-knockout and the three of 9.93: MGI-literature, MGI-screen, SFARI-mouse-models):
  1. calls and absences (relation induces; the relieves calls are counted apart), the human genes they cover and the
     label genes among them;
  2. per symptom, the label-positive rate among label genes given a call and given an absence, against the base rate
     (the cross-method comparison of the research pass of 24 October 2026, recomputed with this code);
  3. the gene-symptom pairs and the genes each source adds that IMPC does not, and how often IMPC reproduced an
     MGI-literature call on a gene it tested for the symptom;
  4. the calibrated regression (evidence/calibrated_reliability.py) on the development perturbations (the lockbox
     removed): with IMPC as the only mouse source (the form before 9.93) and with all four, the second at three
     source-deviation penalties, and the symptoms it reports with no label positive.

A label gene is a gene perturbation (a gene or "<gene>|gain_of_function") with at least one kept positive in the label
selection; a label positive is a kept pair. Literature mice are often made for genes already tied to the human
phenotype, so a rate given a call mixes agreement between species with how the genes were chosen; the record says so.

Usage:
  PYTHONPATH=. python experiments/measure_mouse_sources.py --processed-dir data/processed \
      --graph-dir data/processed/graph_full_neuronal_split_binders_drugs_v5 --evidence-dir data/processed/evidence_full_v5 \
      --label-selection data/processed/label_selection/better_v2_full_v5.parquet
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd

from mechanistic_pathway_learning.documentation import provenance_stamp
from mechanistic_pathway_learning.evaluation.experiment_data import load_experiment_data
from mechanistic_pathway_learning.evidence.calibrated_reliability import SOURCE_DEVIATION_PENALTY, fit_calibration

MOUSE_TABLES = {"IMPC-knockout": "impc_v5/impc_reports.parquet", "MGI-literature": "mgi_literature_v5/mgi_literature_reports.parquet",
                "MGI-screen": "mgi_screen_v5/mgi_screen_reports.parquet", "SFARI-mouse-models": "sfari_v5/sfari_reports.parquet"}
HUMAN_TABLES = ("clinical_trials_v5/clinical_trial_reports.parquet", "faers_v5/faers_reports.parquet", "literature_v5/literature_reports.parquet")
PENALTIES = (1.0, SOURCE_DEVIATION_PENALTY, 100.0)
LOCKBOX = Path("configs/lockbox_v2.json")


def trainer_module():
    path = Path(__file__).resolve().parent / "run_main_model.py"
    specification = importlib.util.spec_from_file_location("run_main_model", path)
    module = importlib.util.module_from_spec(specification)
    sys.modules["run_main_model"] = module
    specification.loader.exec_module(module)
    return module


def label_positives(selection: pd.DataFrame) -> tuple[set[str], dict[str, set[str]]]:
    kept = selection[selection.keep.astype(bool) & (selection.perturbation_type == "gene")]
    positives: dict[str, set[str]] = {}
    for perturbation_id, symptom in zip(kept.perturbation_id, kept.symptom):
        positives.setdefault(symptom, set()).add(str(perturbation_id))
    return set(kept.perturbation_id.astype(str)), positives


def rate(genes: set[str], positive: set[str]) -> str:
    return f"{len(genes & positive)}/{len(genes)} ({len(genes & positive) / len(genes):.2f})" if genes else "-"


def source_tables(processed: Path) -> dict[str, pd.DataFrame]:
    tables = {}
    for source, relative in MOUSE_TABLES.items():
        path = processed / relative
        tables[source] = pd.read_parquet(path, columns=["perturbation_id", "symptom", "relation", "report_value"]) if path.is_file() else None
    return tables


def coefficient_rows(calibration, names: list[str]) -> list[str]:
    return [f"| `{name}` | {calibration.coefficients[name]:+.3f} |" for name in names if name in calibration.coefficients]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--processed-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--graph-dir", type=Path, default=Path("data/processed/graph_full_neuronal_split_binders_drugs_v5"))
    parser.add_argument("--evidence-dir", type=Path, default=Path("data/processed/evidence_full_v5"))
    parser.add_argument("--label-selection", type=Path, default=Path("data/processed/label_selection/better_v2_full_v5.parquet"))
    parser.add_argument("--mouse-dir", type=Path, default=None, help="where the three tables of 9.93 are, when not under --processed-dir")
    parser.add_argument("--graph-note", default="the v5 data layer rebuilt on 22 October 2026 from main at 608df34, before the coupling edge types of pull request #11")
    parser.add_argument("--output", type=Path, default=Path("docs/mouse_sources_measured_v5.md"))
    arguments = parser.parse_args()

    processed = arguments.processed_dir
    tables = source_tables(processed)
    if arguments.mouse_dir is not None:
        for source in ("MGI-literature", "MGI-screen", "SFARI-mouse-models"):
            path = arguments.mouse_dir / MOUSE_TABLES[source]
            tables[source] = pd.read_parquet(path, columns=["perturbation_id", "symptom", "relation", "report_value"]) if path.is_file() else None
    missing = [source for source, table in tables.items() if table is None]
    if missing:
        raise SystemExit(f"report tables missing for {missing}; build them with experiments/build_impc_reports.py and experiments/build_mouse_source_reports.py")
    selection = pd.read_parquet(arguments.label_selection)
    universe, positives = label_positives(selection)
    symptoms = sorted({symptom for table in tables.values() for symptom in table[(table.relation == "induces")].symptom.unique()})

    lines = ["# Mouse report sources beyond IMPC, measured on v5 (decision 9.93)", "",
             provenance_stamp("experiments/measure_mouse_sources.py", [str(arguments.label_selection), str(arguments.evidence_dir), str(arguments.graph_dir),
                                                                       *[MOUSE_TABLES[source] for source in MOUSE_TABLES], *HUMAN_TABLES]), "",
             f"Graph and tables: {arguments.graph_note}. The numbers are measured on those tables and are not evidence about a later graph. "
             f"A label gene is a gene perturbation with at least one kept positive in `{arguments.label_selection.name}` ({len(universe):,} genes); a label "
             "positive is a kept pair. Calls and absences are relation induces; MGI-literature and MGI-screen have no absences, because MP:0002169 is not "
             "read as one by default (`--count-no-abnormal-phenotype-as-absence`).", "",
             "**Caveat.** Literature mice, and SFARI's autism genes, are often made for genes already tied to the human phenotype, so a label rate given a call "
             "mixes agreement between species with how the genes were chosen. IMPC phenotypes genes in a fixed order regardless of phenotype, which is why its "
             "rates are the cleanest reading of the mouse readout.", "",
             "## 1. What each source holds", "",
             "| source | calls | absences | relieves calls | human genes | label genes covered | genes not in IMPC | gene-symptom pairs not in IMPC |",
             "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    impc = tables["IMPC-knockout"]
    impc_genes = set(impc.perturbation_id.astype(str))
    impc_pairs = set(zip(impc.perturbation_id.astype(str), impc.symptom))
    for source, table in tables.items():
        induces = table[table.relation == "induces"]
        genes = set(table.perturbation_id.astype(str))
        pairs = set(zip(table.perturbation_id.astype(str), table.symptom))
        lines.append(f"| {source} | {int((induces.report_value == 1).sum()):,} | {int((induces.report_value == 0).sum()):,} | "
                     f"{int(((table.relation == 'relieves') & (table.report_value == 1)).sum()):,} | {len(genes):,} | {len(genes & universe):,} | "
                     f"{'-' if source == 'IMPC-knockout' else f'{len(genes - impc_genes):,}'} | {'-' if source == 'IMPC-knockout' else f'{len(pairs - impc_pairs):,}'} |")
    lines += ["", "## 2. Label-positive rate among label genes, given a call and given an absence", "",
              "Each cell is positives/genes (rate). The base rate is the share of all label genes that are label positives for the symptom.", "",
              "| symptom | base rate | " + " | ".join(f"{source} call | {source} absence" for source in tables) + " |",
              "| --- | --- | " + " | ".join("--- | ---" for _ in tables) + " |"]
    for symptom in symptoms:
        positive = positives.get(symptom, set())
        cells = []
        for table in tables.values():
            induces = table[(table.relation == "induces") & (table.symptom == symptom)]
            cells.append(rate(set(induces[induces.report_value == 1].perturbation_id.astype(str)) & universe, positive))
            cells.append(rate(set(induces[induces.report_value == 0].perturbation_id.astype(str)) & universe, positive))
        lines.append(f"| {symptom} | {len(positive)}/{len(universe)} ({len(positive) / len(universe):.3f}) | " + " | ".join(cells) + " |")
    lines += ["", "The same base rate among the label genes each source covers (any report on any symptom), which separates how the source's genes "
              "were chosen from what its calls and absences add:", "",
              "| symptom | " + " | ".join(tables) + " |", "| --- | " + " | ".join("---" for _ in tables) + " |"]
    for symptom in symptoms:
        positive = positives.get(symptom, set())
        lines.append(f"| {symptom} | " + " | ".join(rate(set(table.perturbation_id.astype(str)) & universe, positive) for table in tables.values()) + " |")
    lines += ["", "## 3. How often IMPC reproduced an MGI-literature call", "",
              "Among genes with an MGI-literature call for the symptom that IMPC tested for it (an IMPC call or absence), the share with an IMPC call.", "",
              "| symptom | MGI-literature genes tested by IMPC | with an IMPC call |", "| --- | --- | --- |"]
    literature = tables["MGI-literature"]
    for symptom in symptoms:
        called = set(literature[(literature.relation == "induces") & (literature.symptom == symptom) & (literature.report_value == 1)].perturbation_id.astype(str))
        tested = set(impc[(impc.relation == "induces") & (impc.symptom == symptom)].perturbation_id.astype(str))
        impc_called = set(impc[(impc.relation == "induces") & (impc.symptom == symptom) & (impc.report_value == 1)].perturbation_id.astype(str))
        both = called & tested
        if both:
            lines.append(f"| {symptom} | {len(both)} | {len(both & impc_called)} ({len(both & impc_called) / len(both):.2f}) |")

    # 4. the regression, as the trainer fits it
    trainer = trainer_module()
    data = load_experiment_data(arguments.graph_dir, arguments.evidence_dir, label_selection=arguments.label_selection, group_by="disease_cluster_and_targets")
    lockbox = set(json.loads(LOCKBOX.read_text(encoding="utf-8"))["perturbation_ids"])
    fit_rows = np.array([index for index, identifier in enumerate(data.perturbation_ids) if identifier not in lockbox])
    row_is_drug = np.asarray(data.perturbation_types) == "drug"
    human = [processed / relative for relative in HUMAN_TABLES]

    def cells_for(report_paths):
        namespace = SimpleNamespace(soft_prior_strength=1.0, soft_prior_tiers=Path("configs/soft_prior_tiers.csv"), evidence_dir=arguments.evidence_dir,
                                    soft_prior_record_grades=["C"], soft_prior_reports=report_paths, soft_prior_tempering=0.5, soft_prior_count_cap=2,
                                    soft_prior_probability="calibrated")
        return trainer.build_soft_priors(data, namespace)[4]

    mouse_paths = {source: (arguments.mouse_dir or processed) / relative if source != "IMPC-knockout" else processed / relative for source, relative in MOUSE_TABLES.items()}
    before = cells_for([*human, mouse_paths["IMPC-knockout"]])
    after = cells_for([*human, *mouse_paths.values()])
    fit_before = fit_calibration(before, data.outcomes, data.label_mask, fit_rows, symptom_names=list(data.symptoms), row_is_drug=row_is_drug)
    fits_after = {penalty: fit_calibration(after, data.outcomes, data.label_mask, fit_rows, source_deviation_penalty=penalty, symptom_names=list(data.symptoms),
                                           row_is_drug=row_is_drug) for penalty in PENALTIES}
    excluded = fit_calibration(after, data.outcomes, data.label_mask, fit_rows, symptom_names=list(data.symptoms), row_is_drug=row_is_drug,
                               exclude_symptoms_without_label_positives=True)
    mouse_terms = ["species:mouse", "species_direction:mouse:negative", *[f"source:{source}" for source in MOUSE_TABLES],
                   *[f"source_direction:{source}:negative" for source in MOUSE_TABLES], "direction:positive", "class:animal"]
    lines += ["", "## 4. The calibrated reliability regression", "",
              f"Fitted as `--soft-prior-probability calibrated` fits it (evidence/calibrated_reliability.py), on the {len(fit_rows):,} perturbations outside "
              f"`{LOCKBOX}` of {len(data.perturbation_ids):,} loaded, with the grade-C records of `{arguments.evidence_dir.name}` and the report tables "
              f"{', '.join(f'`{relative}`' for relative in HUMAN_TABLES)}; the base L2 strength is that of C = 1.", "",
              f"**Before 9.93** (IMPC the only mouse source; {fit_before.training_rows:,} training cells, {fit_before.training_positives:,} positive): "
              "species:mouse, source:IMPC-knockout and class:animal are one column three times over, so the fit splits one effect between them "
              "and only their sum is read.", "",
              "| term | coefficient |", "| --- | --- |", *coefficient_rows(fit_before, mouse_terms), ""]
    for penalty, fitted in fits_after.items():
        lines += [f"**With the three sources of 9.93, source-deviation penalty {penalty:g}** ({fitted.training_rows:,} training cells, "
                  f"{fitted.training_positives:,} positive{', the default' if penalty == SOURCE_DEVIATION_PENALTY else ''}):", "",
                  "| term | coefficient |", "| --- | --- |", *coefficient_rows(fitted, mouse_terms), ""]
    default_fit = fits_after[SOURCE_DEVIATION_PENALTY]
    lines += ["class:animal and species:mouse remain one column while every animal source is a mouse one, so the species effect is their sum; a "
              "source's absences are weighted by species_direction:mouse:negative plus its own source_direction term, against direction:positive for its calls.", "",
              "Species effect (species:mouse + class:animal) by penalty: "
              + ", ".join(f"{penalty:g}: {fitted.coefficients.get('species:mouse', 0.0) + fitted.coefficients.get('class:animal', 0.0):+.3f}" for penalty, fitted in fits_after.items())
              + f"; before 9.93 the same sum with source:IMPC-knockout: {sum(fit_before.coefficients.get(name, 0.0) for name in ('species:mouse', 'class:animal', 'source:IMPC-knockout')):+.3f}.", "",
              "Mean prediction by class and direction at the median popularity (penalty 10): "
              + ", ".join(f"{group} {value:.3f}" for group, value in default_fit.predicted_by_class_and_direction.items()) + ".", "",
              "### Symptoms with no label positive on the fit rows of their cells' kind", "",
              "| symptom | kinds | cells | by source |", "| --- | --- | --- | --- |"]
    for symptom, entry in sorted(default_fit.symptoms_without_label_positives.items()):
        lines.append(f"| {symptom} | {', '.join(entry['kinds'])} | {entry['cells']:,} | {', '.join(f'{name} {count:,}' for name, count in sorted(entry['cells_by_source'].items()))} |")
    lines += ["", f"With those cells left out (`--soft-prior-calibration-exclude-unlabelled-symptoms`, penalty 10): {excluded.training_rows:,} training cells; "
              + ", ".join(f"`{name}` {excluded.coefficients[name]:+.3f}" for name in mouse_terms if name in excluded.coefficients) + ".", ""]
    arguments.output.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {arguments.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
