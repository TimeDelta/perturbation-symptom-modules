# The documentation process: what is current, what is a record, and what checks it

Written 15 October 2026, after the audit the owner asked for ("audit and automate the documentation process in a
way that avoids any issues with stale information interfering with your or anyone else's understanding but still
maintains a valid research study log"). It extends the mechanism they settled for the registration the same day: a
frozen baseline, a living document free to be overwritten, and a history generated from the git log rather than
written by hand (`experiments/generate_amendment_history.py`). The practices it draws on are the ones research-record
and documentation standards agree on: a record is corrected by adding to it, never by overwriting it (NIH IRP notebook
guidance, 2024: "Correct documentation errors, do not remove them"; MHRA GxP data-integrity guidance, 2018: corrections
"without obscuring or overwriting the original record"); a decision that is reversed is kept and marked superseded
(Nygard, 2011); documents without a review date go stale (Winters, Manshreck and Wright, *Software Engineering at
Google*, 2020, ch. 10); and generated documents are regenerated and diffed in CI rather than trusted (`cog --check`).

## What the audit found (15 October 2026)

144 tracked Markdown documents. 93 are written by scripts, and almost none of them said when, from which data or at
which commit: their only date was the last commit that touched them, and the oldest (the mechanism cards, the Phase 2
baseline tables) describe runs from the first week of October that live on the disks of the containers that made
them (the owner keeps every container of this project), not in this repository. The README restated
release counts by hand, and two of them were wrong against the manifest (261,369 edges against the manifest's
255,367; an evidence table of 3,838 observations that had become 3,910 in the release and 5,604 in the rebuild).
Decisions were recorded in the log after they were taken (the owner's complaint of 13 October); the git history
shows 12 of 51 closed decisions recorded and closed in the same commit, one id used by two rows, two ids that
vanished (1.5 and 9.10, renumbered into 9.10a and 9.10b), and one line holding three rows behind literal `\n`. One
decision (9.47) and one operational document (`docs/job_harness.md`) describe a container or a session, which is true
on one machine and false on the next. Several generated tables exist in two to six versions as separate files with
nothing saying which is current.

## The classes

Every tracked Markdown document is in `configs/documentation_registry.json` with one of five classes. The class
decides what `tests/test_documentation_process.py` checks; an unregistered document fails the suite, and
`python experiments/register_documents.py --add-missing` adds a guessed entry that fails until a session confirms it.

| class | what it is | the rule | checked by |
| --- | --- | --- | --- |
| generated | written by a script from data, a run or the git log | names its script in the first lines; once regenerated after 16 October 2026 it carries the stamp `provenance_stamp` writes (script, date, commit, inputs); never edited by hand | stamp present; generator exists; paths it names exist |
| living | hand-written and kept current by overwriting | describes the repository, never a container or a session; `reviewed` and `as_of_commit` in the register say when it was last read against the repository | no session-state phrases; paths, decisions and items it names exist; review due after 60 days or when a named file changed |
| record | dated: a review, a reading of a source, a rebuild report, the decision log | written once; a correction is a dated addition; `append_only: true` means the committed text is a prefix of the working tree | append-only records unchanged at their committed prefix; the decision log keeps every id |
| frozen | byte-exact | SHA-256 pinned in the register; replaced by a new frozen copy, never edited | digest matches |
| draft | text for the owner to act on | no claim about the current state | registered only |

The study log is the set of records plus the two generated histories. `docs/open_decisions.md` is the decision log:
a row is added in the turn the decision is taken, edited only to close it (the id struck through) or to add a dated
correction, and ids are never dropped or renumbered. `docs/decision_history.md` is its chronology, read from the git
history of the log by `experiments/generate_decision_history.py`: the commit that first holds a row is the earliest
the decision can have been recorded, whatever date the row claims. `docs/amendment_history.md` is the same for the
registration, from `Amends:` trailers. `docs/data_layer_rebuild.md`, the readings under `docs/exposure_sources/` and
the other records the register marks `append_only: true` are append-only.

## Where documents live (20 November 2026)

The owner, 20 November 2026: "can you please start an agent to improve the organization of the docs directory? it's
become insanely bloated". Git tracked 279 files under `docs/` that day, 225 of them at its top level, so the documents
kept current were lost among the dated ones. Each file now goes where its class puts it, and the top of `docs/` holds
what is kept current:

| place | what goes there |
| --- | --- |
| `docs/` | every living document, the frozen baseline, and the exceptions below |
| `docs/generated/` | every page a script writes, every data file a script wrote, and the inputs a page's script reads, beside the page |
| `docs/records/<YYYY-MM>/` | every record, in the month of its `recorded` date in the register, with the data files it explains |
| `docs/drafts/` | every draft |
| `configs/` | a data file the graph or evidence build reads, beside the other build tables (phase 3 below) |

The owner settled the layout the same day, answering five questions about it in turn ("1 class / 2 yes / 3 yes / 4
sure / 5 either there or the readme"): folders by class rather than by topic; a session may change the three paths the
owner's Claude Docs study sheet names for files that move (`module_names.md`, `physiological_adherence_review.md`,
`curated_pathway_modules.csv`) in the doc and export it again; the build inputs move to `configs/` at the next
data-layer rebuild; the exploration queue and the study sheet join the reference list of the landing page,
`docs/README.md`; and the rule on where a new document goes is stated in this document and on the landing page (the
last point below).

- `expected_location` in `mechanistic_pathway_learning/documentation.py` is the rule. It is read from the register's
  class, so no file needs a judgement of its own. A file keeps its name when it moves, and a folder moves whole under
  its own name: `docs/mechanism_cards/<run>/` goes to `docs/generated/mechanism_cards/<run>/`, and
  `docs/exposure_sources/` into `docs/records/2026-10/`. A family of versions moves together, as do a data file and the
  document that explains it, and a script's inputs and its page. `docs/figures/` and `docs/study_sheet_figures/` stay
  where they are, because `figures.md` and `study_sheet.md` link into them relatively.
- The exceptions that stay at the top, each with its reason, are `TOP_LEVEL_EXCEPTIONS` in the same module: the six
  process pages (`README.md`, `status.md`, `file_index.md`, `decision_history.md`, `amendment_history.md`,
  `registered_core.md`), `graph_summary.md`, the decision log and the three other running logs
  (`label_source_review.md`, `development_sessions.md`, `data_layer_rebuild.md`), `alternative_sources.md` (the licence
  statement of the immutable release v0.4 names it), the owner's rulings draft of 13 November 2026 while it is open,
  and `references.bib`.
- `configs/moved_paths.json` lists the moves made, with the date, and the moves planned, with their phase. Phase 1 is
  every move that needs no edit to a file other work is changing. Phase 2 waits: for work in flight on another branch
  or in another checkout that changes a file the move must edit, until it lands, so that no branch meets a conflict;
  and for the owner where the move would change their rulings draft. Where a move changes one of the three paths the
  study sheet names (above), the session changes it in the doc first, then in the doc's Markdown copy, and exports the
  doc again: that is what the owner's answer of 20 November 2026 allowed, for those three paths. Phase 3 holds the
  build inputs, moved to `configs/` just before a data-layer rebuild and when no job is running, because a moved file
  has a new modification time on every checkout and `experiments/check_rebuild_inputs.py` would report the builds
  there as stale. What a planned move waits for is worked out on the day, not stored.
- `PYTHONPATH=. python experiments/move_documents.py --phase N` applies a phase, as a dry run until it is given
  `--apply`. It renames each file with `git mv`, rewrites the old path in code, scripts, tests, YAML configs, living
  documents, drafts and the bibliography, renames the register keys where they stand, and gives each generated page
  that names an old path an allowance in `names_absent_paths` until its script writes the page again. It then checks
  that every moved file is staged as a pure rename (git's R100) and that no record and no frozen file changed.
- Records, the decision log, the frozen baseline, the provenance columns of build tables and the quotations in
  `configs/registered_rules.json` keep the old paths they were written with, as records do. `docs/file_index.md` prints
  every move, old path, new path and date, so an old path leads to the file, and its unchanged name finds it as well.
- A move is not a change. The dates read from git follow a pure rename back to the last change to the text
  (`content_change_commits`), so a page generated before the stamp keeps its date, a record moved and edited in one
  commit is still compared with its old text, and `--review` does not call a living document due because a file it
  names moved.
- **Where a new document goes.** Where its class puts it, from the start: a living document at the top of `docs/`, a
  record in `docs/records/<YYYY-MM>/` for the month the register says it was recorded, a page or data file a script
  writes in `docs/generated/`, a draft in `docs/drafts/`, and a table the graph or evidence build reads in `configs/`.
  `python experiments/register_documents.py --add-missing` prints the place for a new Markdown document, and
  `tests/test_documentation_process.py` fails for a registered document outside it that is not a planned move, for a
  file left at the top of `docs/`, and for code or a YAML config that still names a moved path. Asked on 20 November
  2026 whether `CLAUDE.md` should say where a new document goes, the owner answered "either there or the readme", and
  on 21 November 2026, asked which of the two "the readme" meant, `docs/README.md` or the top-level `README.md`, they
  answered "Whichever makes more sense to you". It is the docs landing page, `docs/README.md`, because that is where a
  person goes to find or add a document; so the rule is stated there and here, and `CLAUDE.md` is not edited.

## What is current

`docs/status.md` is generated by `experiments/generate_status.py` from the release manifests,
`configs/registered_rules.json`, the git history of the decision log and the register. It is the one page that says
what is current: the releases and their counts, the registered rules and their amendments, the decisions open and
closed, which generated documents carry a stamp and which predate it, and when each living document was last
reviewed. Whether a review is due depends on today's date and on what changed after the reviewed commit, so that
diagnostic is printed by `python experiments/generate_status.py --review` and never committed, where it would be
stale by the next commit or the next day. The same script renders the release counts into the README between `<!-- generated:release_counts -->`
markers, so the README restates no number by hand; a test asserts that no release count appears in the README
prose outside that block. It also writes `docs/README.md`, the index of every registered document by topic, through
`experiments/generate_docs_index.py` (added 17 October 2026).

**Which member of a family of versions is current (20 November 2026).** Six families of generated documents exist in
several versions: the Phase 2 baseline tables, the label plasma binders, the drug administration routes, the leakage
group rules, the module health results and the rewiring null distribution. Asked which member of each is current, the
owner answered "6 yes" and then, asked which question 6, "Version families": the current member is the one generated
on the tables the registered model reads, v5. `"current": true` on that member's entry in
`configs/documentation_registry.json`, beside the `family` field that groups the members, names it, and
`experiments/generate_docs_index.py` prints it on the family's line of `docs/README.md`. A family with no v5 member
has no current member until one is regenerated, and its members are listed as history. None of the six has one: every
member was last written between 3 and 11 October 2026 (the dates `content_change_commits` reads through the renames),
before any v5 table existed - `evidence_full_v5` is first named in this repository on 16 October 2026 and
`graph_full_neuronal_split_binders_drugs_v5` on 17 October - and no member names a v5 table: the two leakage pages
name `data/processed/evidence_full_v3_max3_targets` and `data/processed/evidence_full_v2`, the two newest Phase 2
tables the v2 label selection, and the two rewiring pages `data/processed/graph` and `data/processed/evidence`.

What is deliberately absent from every living document: the state of a container, a session or a running job. That
state is on a machine's disk and is read there (`bash scripts/resume_jobs.sh --status`). A dated record may say
"the container of 15 October did not hold the rebuild" because the date scopes it; a living document may not.

## What a session does

- Before acting on a statement about the current state, read `docs/status.md` and the stamp or date of the document
  the statement is in. A generated document without a stamp was written before 16 October 2026 and describes the
  data of its last commit date at best.
- Record a decision in `docs/open_decisions.md` in the turn it is taken, with the date and the owner's words; close
  it by striking the id. Never remove or renumber an id. Write amendments to registered rules as `Amends:` trailers.
- After changing data, rules, the decision log or any document, run the generators from the checkout's root with
  `PYTHONPATH=.`: `experiments/generate_status.py` (which also writes `docs/README.md`),
  `experiments/generate_decision_history.py`, `experiments/generate_amendment_history.py`,
  `experiments/generate_registered_core.py` (one entry per registered rule, added 27 October 2026) and
  `experiments/generate_file_index.py` (every file under `docs/`, added 2 November 2026), then
  `pytest tests/test_documentation_process.py -q`, which fails on any of their pages left stale. The decision log and
  the pages generated from it go in two commits, the log first, because `docs/decision_history.md` records the hash of
  the commit that first holds each row (`CLAUDE.md`, Documents); the three generators that read the git log refuse a
  shallow clone unless given `--allow-shallow`. The `.claude/settings.json` hook runs that test file and
  `tests/test_amendment_history.py` after an edit to a Markdown file under `docs/`, to `README.md`, `CLAUDE.md`,
  `configs/documentation_registry.json` or `configs/registered_rules.json`, so a stale page is reported in the same
  turn that made it stale.
- When a generated document is regenerated, its generator writes the stamp; a generator that does not yet (most of
  the generated documents predate the stamp; `docs/status.md` counts them) is given it at its next change by calling
  `provenance_stamp` from `mechanistic_pathway_learning/documentation.py`.
- A new document is registered before it is committed, and is placed where its class puts it ("Where documents live"
  above). A document that is superseded gets `superseded_by` in the register and stays; nothing is deleted from the
  record.
- A living document that `docs/status.md` lists as due is read against the repository, corrected by overwriting, and
  its `reviewed` date and `as_of_commit` are updated in the register.
- The study sheet's diagrams are checked with the decisions and code they depict (the owner, 5 November 2026;
  `CLAUDE.md`, Documents). `configs/study_sheet_diagrams.json` lists each diagram of the owner's Claude Docs study sheet
  with the decision rows and code files it depicts and a SHA-256 of each, taken when a session last checked it;
  `tests/test_study_sheet_diagrams_current.py` fails while any of them has changed since. A commit that changes a
  depicted row or file therefore checks the diagram in the doc, corrects it there if it is wrong, and re-stamps it with
  `PYTHONPATH=. python experiments/check_study_sheet_diagrams.py --stamp <widget id>`. Each diagram shows the
  architecture as last built or as decided, with one of each where the two differ.

## Defects repaired, and what is left to the owner

Line 204 of the decision log (three rows behind literal `\n`) was split into its rows, and the opening row of 9.5 was
merged with the closing row that had been appended below it, so the id names one row (the owner, 15 October:
"Whatever you think is best for the 9.5 duplicate ... Just make it honest"); the tests fail on any literal `\n` or
on an id that names two rows. The six families of generated documents that exist in several versions are settled by
the owner's answer of 20 November 2026, under "What is current" above: the member generated on the v5 tables is the
current one, the register names it, and none of the six has such a member, so every version of each is history.
`docs/status.md` lists the oldest unstamped documents.
