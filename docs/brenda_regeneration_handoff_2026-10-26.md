# Handoff: BRENDA regeneration (decision 9.88), for the session that does the v5 rebuild

Written 26 October 2026 as the Project note `claude/handoff_brenda_regeneration_2026-10-26.md`, against `main` at
`0d4d62f`. **Moved into the repository on 27 October 2026** under the owner's ruling that the repository is the single
source of truth ("Everything should rely on the repository moving forward"); the Project note was deleted once this page
held its content. The text below is the note as written, with this header added. It is a record: what was true when it
was written stays as written, and a later correction is a dated addition.

What this page adds to the repository, which held the rest already: the first-pass reading of the 47 activator notes,
the note-class counts behind the 184 `no_inhibition` rows, the two file hashes, the implementation shape of section 1b,
the mapping procedure and its ordering trap, and the UniProt FTP substitution. The owner's ruling of section 1 is
recorded in decision 9.88.

## 0. Inputs
- **BRENDA JSON:** the owner uploaded `brenda_2026_1_json_tar.gz` on 26 October 2026. It is 83,199,555 bytes packed
  (sha256 `bb2549d02b7255de2272b35701c331493caad16b82eb38a41adb2e03bbb0d2e1`) and 709,658,292 bytes unpacked, both
  matching the 2026.1 row in `docs/data_sources.md`. Containers are reclaimed, so ask the owner to upload it again if it
  is not present.
- **Extractor needs `ijson`** (`pip install --break-system-packages ijson`). It runs in about 10 seconds.
- **UniProt for the mapping:** `ftp.ebi.ac.uk` is allowed by `CLAUDE.md`'s EBI FTP exception (the owner, 22 October:
  "don't refuse FTP from EBI"). The 403 from `rest.uniprot.org` on 26 October came from the container's proxy, not from
  UniProt, so the no-mirror rule does not apply. The FTP release is `.dat`, not the pinned REST TSV, so it needs a
  converter for the Entry and EC number columns plus a substitution note in `docs/data_sources.md`. If the rebuild
  already fetched the TSV, use that instead.

## 1. Owner ruling to record first
> "\"no effect\" should not have an activates edge ..." (the owner, 26 October 2026)

Recorded in decision 9.88 on 27 October 2026. When this was written, `regulation_rows` only **counted**
activating-compound notes that state no effect, and still wrote them as `activates` (note class "a note states no effect
(written as activates, as before)").

### 1a. First: investigate the wording context of the 47 notes (the owner's instruction, 26 October 2026)
Before writing any rule, read each of the 47 activating-compound notes in full, and the roughly 15 more that the widened
pattern below would add. Many comments in the extraction are cut at 300 characters, so read the whole comment from the
JSON. For each note, record:
- what the "no effect" is about: this enzyme, another isozyme or form, a mutant, another organism, cell line or
  condition, another substrate or activity, a concentration range, or another compound;
- whether activation of this human enzyme is stated in the same note;
- the relation the note supports: `activates`, `no_activation` or no row.

Put the table in a page the owner can review, and get the owner's sign-off on the classes before the rules are built
from them. **The first-pass reading below came from a 220-character skim of each note. It is a starting point, not a
result.**

**First-pass reading of the 47 notes.** Most seem to state activation and put the no-effect on something else:
- another isozyme or form: "activates cNII, no effect on cNI" (3.1.3.5); "No activation of other HDAC isoenzymes"
  (3.5.1.98, three ligands); heparin ATXalpha vs ATXbeta (3.1.4.39)
- another substrate or activity: "stimulation of ATPase activity, no effect on daunorubicin efflux" (7.6.2.2, four drugs)
- another cell line or condition (2.8.2.4, 2.7.11.20)
- concentration dependence: "stimulates at low concentrations, but has no effect at high concentrations" (2.8.2.4);
  retinoic acid at 0.001 vs 0.0001 mM (1.1.1.62)

Possible pure absences about the enzyme:
- pyrazole "no effect" (1.1.1.284)
- spermine "no effect at 0.02-0.2 mM" (3.1.3.48)
- GAP "no stimulation of GTP hydrolysis" (3.6.5.2)
- 2',5'-ADP and 5'-ADP "does not stimulate" (3.5.4.9)
- Ca2+/calmodulin "has no detectable effect on recombinant human NAD kinase" (2.7.1.23; the note's first sentence says
  it "regulates")

Odd one: phosphate on 2.7.6.1 is listed as an activating compound, but its note says "no inhibition up to 75 mM".

### 1b. Then implement, shaped by 1a
A likely shape, mirroring the inhibition fields (`relation_of_notes`):
- an absence about this enzyme with no activation stated for it: a `no_activation` negative row, never an edge;
- an absence scoped elsewhere only: no row;
- activation stated for this enzyme beside an absence: keep `activates`.

This likely needs:
- a `STATES_ACTIVATION` pattern: `\bactivat\w*` (the `\b` already excludes "inactivat"), `stimulat\w*`, `enhanc\w*`,
  `increas\w*`, "N-fold" and "% activation";
- an activator absence pattern that also catches "no activation" or "no stimulation", "not activated" or "not
  stimulated" and "does not activate" or "does not stimulate". Widening to these is an inference from the ruling, so
  **confirm with the owner**.

The existing scope patterns (`scope_elsewhere`) do not cover "another substrate or activity" or "another cell line". 1a
will show whether they need to.

In the mapping (`experiments/map_brenda_regulation_to_graph.py`), negatives are selected by
`relation_type == NO_INHIBITION_RELATION` (line ~187 when this was written). Extend that test so `no_activation` rows
reach a negative table and never the edges. Add tests beside `tests/test_brenda_no_inhibition.py`, using 1a's notes as
cases, and audit the near misses in `tests/test_regex_audit.py`. Neither `STATES_ACTIVATION` nor `no_activation` exists
in the code as of 27 October 2026.

## 2. Step 1, extraction: already run once, rerun after section 1
Run at `main` `0d4d62f`, before the activator change:
- 8,129 enzyme entries with a human protein; 150,173 rows (the previous derived table was built from 150,238)
- inhibits 137,209; no_inhibition 184; cofactor_of 7,261; activates 5,519
- 1,846 human accessions; 116,631 ligand names
- Output `brenda_regulation_records.csv` sha256 `2fac945a4b18d9309ab7f9dfb00dde1ffc11332cc3643196746952c836a488a5`,
  sent to the owner in chat as .gz. It becomes stale once section 1 is built.

How the notes were classed:
- **Comment format (an open 9.88 question, answered here):** all 176,313 inhibition-field comments in the JSON have no
  `#n#` protein markers. Each comment is therefore one note covering every protein in its record, and
  `notes_by_protein`'s per-protein reading only matters for the text release.
- **Notes of absence:** 179 inhibitor, 4 IC50 and 1 Ki became `no_inhibition`.
- **Kept `inhibits`:** 150, because inhibition is stated beside the absence.
- **No row:** 65, because the absence is scoped elsewhere.

## 3. Step 2, mapping: needs the rebuilt graph
```
cp configs/brenda_metabolite_enzyme_regulation.csv data/processed/brenda_metabolite_enzyme_regulation_before_9_88.csv
python experiments/extract_brenda_enzyme_regulation.py brenda_2026_1.json --output data/processed/brenda_regulation_records.csv
python experiments/map_brenda_regulation_to_graph.py --regulation-records data/processed/brenda_regulation_records.csv \
  --graph-dir <rebuilt split graph, e.g. graph_full_neuronal_split_binders_drugs_v5> \
  --output configs/brenda_metabolite_enzyme_regulation.csv --summary docs/brenda_regulation_mapping.json \
  --no-inhibition-output configs/brenda_metabolite_enzyme_no_inhibition.csv \
  --compare-with data/processed/brenda_metabolite_enzyme_regulation_before_9_88.csv
```
- `--graph-dir` defaults to v4. Pass the rebuilt graph explicitly and record which one was used.
- The mapping needs `nodes.parquet` with `uniprot_entry` (a split graph), UniProt reviewed human, `chebi_core.obo.gz`
  and Human-GEM 2.0.1 `metabolites.tsv`.
- Baseline: the current table has 4,143 pairs (inhibits 1,552; activates 482; cofactor_of 2,109).
- Report gains and losses per relation from `--compare-with`, the `no_inhibition` (and `no_activation`) pairs that also
  exist as edges, and the edge count `build_neuronal_graph_variant.py` takes from the new table.
- **Order:** the derived table feeds `build_neuronal_graph_variant.py`, so regenerating it changes the graph. Either
  regenerate it before the v5 rebuild's neuronal step, using the base or split graph from that same rebuild for the
  protein set, or rebuild the downstream variants afterwards.
- Then regenerate the generated pages and run `tests/test_documentation_process.py`.

## 4. Owner calls still open from 9.88
- set aside the 164 single-isoform Yang 2016 IntAct records?
- should a BRENDA no-inhibition (and now no-activation) observation lower a prior?
- confirm the widened activator absence pattern (section 1b)
- sign off on the 1a classification of the activator notes
