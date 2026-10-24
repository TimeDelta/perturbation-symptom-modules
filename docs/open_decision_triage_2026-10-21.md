# Open decisions in docs/open_decisions.md, classified (main at 2f21e2b, 21 October 2026)

> **Note added 21 October 2026, after the fact.** This triage was computed against `main` at `2f21e2b`. Commit
> `8764bb4` ("Decision log against the repository") has since acted on much of it: 8.11, 9.71 and 9.74 are struck,
> 9.68 and 9.69 record their merges, 1.2 states that it is decided and not built, the BRENDA rows no longer wait on a
> licence, and `docs/status.md` now counts the rows that owe nothing apart. The class counts below therefore describe
> the log as it stood before those changes, and the open count has moved from 77 to 74. The per-id evidence stands.


Read-only audit of TimeDelta/perturbation-symptom-modules. History unshallowed (657 commits); pull-request heads fetched as `refs/remotes/pr/*` only to compare with main. Nothing in the repository was edited.

## (a) The generator's rule

`experiments/generate_status.py` imports `read_history` from `experiments/generate_decision_history.py`, which uses two helpers in `mechanistic_pathway_learning/documentation.py`:

```python
# documentation.py:215 - every id in the log, struck or not
match = re.match(r"^\|\s*(~~)?(?P<id>\d+\.\d+[a-z]?)(~~)?\s*\|", line)
# documentation.py:221-222 - closed = struck through
def closed_decision_ids(text: str) -> set[str]:
    return {match.group("id") for match in re.finditer(r"^\|\s*~~(?P<id>\d+\.\d+[a-z]?)~~\s*\|", text.replace("\\n", "\n"), flags=re.MULTILINE)}
# generate_decision_history.py:90-91
if identifier in closed and timeline.closed_commit is None:
    timeline.closed_commit, timeline.closed_date = sha, day
# generate_decision_history.py:51-54
def status(self) -> str:
    if self.dropped_commit:
        return "dropped"
    return "closed" if self.closed_commit else "open"
# generate_status.py:108
open_ids = [timeline.identifier for timeline in timelines if timeline.status == "open"]
```

So an id is **open** when it begins a table row (`| 9.40 |`) in the current log, is still present, and has never appeared struck through (`| ~~9.40~~ |`) in any committed version. The text of the row ("decided", "built", "for the record", "no decision owed") is never read.

## (b) Classification

Classes: A awaiting an owner ruling; A? probably A, see note; B ruled (or registered/decided) but not struck, work owed by a session; C built/merged on main or a record with nothing to choose; D superseded by a later entry; E built behind a default-off flag or otherwise waiting on a measurement/run; F built in an open pull request; X waiting on a third party (added because 6.2 fits none of A-F). Where a row is partly done, the class is what remains.

| id | subject | class | evidence |
| --- | --- | --- | --- |
| 1.1 | Held-out draw go-ahead and its leakage ceiling | A | "the owner's: the ceiling, before the draw." - Same ceiling question as 9.35; owner action, nothing built |
| 1.2 | v4 rebuild lifting the three-target limit | B | "registers no limit with orphenadrine set aside by the stated bridging rule" - Approved in struck 1.2c ("Rebuild package numbers seem acceptable"); rebuilds ran 15-16 Oct (d60815b, a7e46df) but scripts/rebuild_data_layer.sh still passes --max-drug-targets 3 |
| 4.1 | Magnitude of electrical-layer input at VM_c | B | "is re-measured at the rebuild before anything further is decided" - Procedural ruling (owner asked for re-measurement, per 9.11 and section 10); no re-measurement found on main |
| 4.3 | Class-specific routing lost under limiting-step rule | B | "the owner, 13 October: "4.3 should be quantified after the rebuild"" - Measurement owed by session; none found on main |
| 4.12b | Signed (two-channel) limiting-step bottleneck | B | "decided: option (a). Not yet built - I failed it three times." - No signed bottleneck code on main (49632eb reverted) |
| 5.2 | Whether P1 is primary | A? | "Whether P1 is primary at all, which needs the power simulation first" - Owner's eventually, but nothing to rule until 8.8's simulation exists |
| 6.1 | Send the CTD notice | A | "`docs/ctd_notice_draft.md` is written for the owner to send" - Owner action; "not sent" |
| 6.2 | Lombardo permission request | X | "sent, awaiting a reply" - Waits on a third party, not the owner |
| 8.1 | Occupancy input path (item 5c) | B | "calibration built 13 October, input path unbuilt" - Section 8 = decided; no model consumer of occupancy on main |
| 8.3 | Build of decision 4.12 (duplicate of 4.12b) | B | "blocked on 4.12b, a conflict with a registered property." - 4.12b says the conflict does not exist; build owed |
| 8.5 | Open Targets class into Dawid-Skene fit | C | "Built 14 October on option (a), which the owner chose after the measurement" - 016ff6a on main; open_targets_scoped_rows_path in assemble_evidence_table.py |
| 8.8 | Power simulation for 5.2 | B | "The power simulation of 5.2" - Registered work, unbuilt; no power-simulation script on main |
| 8.10 | Nosology readout of item 26 | E | "built, waiting on runs" - Not a flag: waits on trained checkpoints, not a ruling |
| 8.11 | Narrow ChEMBL complex targets to GtoPdb subunits | A? | "whether GtoPdb's additions enter is the owner's" - PR #4 landed on main 20 Oct (7ab325b..344d211); --narrow-complex-targets default on; only the additions question remains |
| 9.1 | Occupancy rule should cut on band, not role | C | "Not put to them, because they have not asked for one" - Record; "no longer a live defect" |
| 9.7 | Eighteen absent psychiatric drugs incl. lithium | D | "Lithium is the conspicuous one" - Superseded by struck 9.7a, 9.7b, 9.7c (closed 15 Oct) |
| 9.11 | Dead changes_membrane_potential edges | D | "not put to the owner as a decision, because 4.1 already holds the question" - Folded into 4.1 |
| 9.12 | Promiscuous receptor-to-G-alpha coupling | D | "the question is whether to re-source the coupling from Guide to PHARMACOLOGY" - Superseded by 9.23 (GPCRdb sourcing, filter built 37fbdef); residual measured in PR #8's 9.86 |
| 9.13 | No multi-gene perturbations; OLIDA as source | D | "not put to the owner as a decision, raised because they asked." - OLIDA dropped by struck 9.18 |
| 9.14 | Paring the orphan layer, held for BRENDA | B | "held pending the BRENDA download, which is the owner's licence acceptance to make" - Owner ruled "wait"; its condition was met (9.26, BRENDA in) |
| 9.15 | Sourcing G-alpha coupling from GtoPdb | D | "outstanding, not closed." - Superseded by 9.23 (GPCRdb route, no credentials) |
| 9.16 | Per-seed forward-cone divisor | F | "they reversed to per seed on 14 October" - Module on main (090cae9) unused by trainer; PR #8 (e9758bd) makes it the registered normalisation |
| 9.17 | Chloride remap and ChEBI charge guard | C | "the remap is what the owner's condition resolves to" - 090f001 on main: "Read every tracked ion's charge from the ChEBI term Reactome names" |
| 9.20 | Overexpression-derived coupling | D | "My weighting proposal was wrong" - Owner's objection resolved by the 9.23 admission rule (GtoPdb primary/secondary) |
| 9.21 | Drop unreferenced G-alpha rows | D | "Superseded by 9.23, which the owner approved" - Row itself says withdrawn |
| 9.22 | No family-level inferred couplings | B | "agreed in principle; the zero-coupling count is owed before anything is dropped" - Owner position quoted; session owes a count |
| 9.23 | GPCRdb/GtoPdb coupling filter | C | "the owner's, and their constraint is now satisfiable." - 37fbdef "Build the receptor-to-G-alpha coupling filter approved in decision 9.23"; 9.53: 282 edges dropped |
| 9.25 | BRENDA vs GPCRdb roles | C | "BRENDA still waits on the owner's licence acceptance; GPCRdb is downloaded" - Stale: 9.26 says licence accepted 14 Oct; bdb896c wired BRENDA |
| 9.26 | BRENDA metabolite-enzyme regulation | C | "the owner's to admit at the rebuild." - bdb896c "Wire BRENDA's enzyme regulation into the graph"; 9.43 calls 9.5 built |
| 9.28 | Item 31 documentation skew | B | "the owner has decided the rule" - "What remains is work rather than a decision" |
| 9.29 | Second agency for drugs blocked by rule (a) | D | "whether the Spanish route is acceptable at all" - Answered by 9.31 (owner: Spanish dropped, English agencies fine) |
| 9.31 | English-language second agency only | B | "any of the reputable English-released agency sources are fine though" - Ruled; remaining work is testing agencies (see 9.34) |
| 9.33 | Regex audit defects | C | "closed." - tests/test_regex_audit.py, UNBOUND_SUBJECT and ENDOGENOUS_CARRIER_LIGANDS on main |
| 9.34 | Archived Health Canada monographs usable | C | "corrects my own reading, not a decision of their" - Record |
| 9.35 | Non-arbitrary leakage ceiling | A | "the owner's. Proposed: the one-standard-error ceiling, first passing draw, registered channel list." - Unbuilt; same question as 1.1 |
| 9.35b | Leakage-only adversary measured | C | "no decision owed." - Record; docs/leakage_only_adversary.md |
| 9.36 | k=2 reached-node channel in the adversary | A | "the owner's: whether to add the k=2 reached-node channel to the adversary." - Unbuilt |
| 9.37 | Four stale registration passages corrected | C | "corrections, not decisions" - f300a8b on main; record |
| 9.38 | Effect-size reporting wording and floor rule | A | "the owner's: the wording." - Floor rule also open |
| 9.39 | Commit a Kp tier rule before rebuild, or defer | A? | "Needs the owner's call on whether to commit the rule before the rebuild or defer the whole tier question" - Possibly moot: rebuilds ran; guanfacine settled by 9.7b |
| 9.40 | B3DB logBB column | D | "DECIDED 15 October 2026, the owner: "Definitely a separate column with separate provenance etc."" - Form ruled; build-or-not re-asked as 9.41(c) |
| 9.41 | Kalvass 2007 derivation, eletriptan, B3DB | A | "Three things need the owner's call." - (a), (b), (c) unruled |
| 9.42 | Label-derived sources: collapse or model correlation | A | "Needs the owner's call on (1), which is a change to the current fit" - Gates 9.45 and 9.46 |
| 9.43 | Pre-rebuild checklist answer | D | "section 10's owner list is empty" - Status note; corrected by 9.44, 9.46, 9.47; its owner items are other rows |
| 9.44 | Drug additions gated by evidence table | D | "The 7 need the owner's decision" - Corrected to 12/6 by 9.46; second-source rule (9.45) answers it |
| 9.45 | Second source for the drugs without labels | A | "whether the three national-agency drugs are worth the pass" - Numbers corrected by 9.46 (two national-agency drugs); (i) is 9.42 |
| 9.46 | Flupentixol spelling; six truly absent | B | "Mine to build" - Under owner's 9.7b ruling; config still spells flupentixol; gated on 9.42 |
| 9.47 | File dates prove only local state | C | "The rule this establishes" - Record |
| 9.48 | Absence sources: which comparisons enter | A | "open: which comparisons enter (A, B or C)" - Decided (3) and built (9526785); residual sub-choice |
| 9.49 | Assembler class ranking | C | "none; recorded for the record" - 7e50913 on main |
| 9.50 | Soft priors secondary arm | E | "Soft priors are wired into training as a secondary arm, off by default" - Owner: grid "should run after finalization of the dev folds" |
| 9.51 | Physiology validation set and audits | C | "the rebuild" - Stale: docs/physiology_audit.md generated 17 Oct on rebuilt v4 |
| 9.52 | Technology audit findings | A | "owner's prioritisation" - Low stakes; nothing changes a result |
| 9.53 | Base graph rebuilt; v0.5 release cut | B | "the v0.5 release is cut before the first confirmatory run" - Ruled; cut not yet made (only data/releases/v0.4) |
| 9.54 | Allele perturbations: untyped default | A | "open: the untyped default for never-recessive pairs, and neomorph curation" - Decided (d) and built (8502cfc); residual |
| 9.55 | Absence sources break reliability fit | D | "the item grouping is the owner's" - Settled by 9.56's measurement |
| 9.56 | Joined evidence table; IMPC fitted apart | A | "the remainder of 9.55 is the owner's" - Owner's constraint on IMPC quoted; "still to be put to them" |
| 9.57 | Edge priors by evidence strength | E | "`--edge-prior-strength` is 0 by default" - Tier values wait on the 9.50 grid; gate reading moved to 9.62 |
| 9.58 | Fine symptom constructs | C | "built; the ID scale is 9.61" - ea0ccaa on main |
| 9.59 | Calibrated reliability regression | E | "built; read on the grid of 9.50" - Behind --soft-prior-probability calibrated (tier by default) |
| 9.60 | Trial outcome measures as relief source | C | "built" - 69290b0 on main |
| 9.61 | Intellectual disability's 734 genes | A | "the owner's: (a) to (d)" - No ruling quoted |
| 9.62 | Hard edge gates: closure reading, annealing | A | "open: how closures are read (by P(false) or E)" - Decided (e) and built (0dc6c93); residual sub-choices |
| 9.63 | Curated edges as labels: human-evidence threshold | A | "open: what counts as evidence from humans, and the transcription records" - Decided (b)+(c)+(d); (b),(c) built (8383a9e); residual |
| 9.64 | Post-experiment nosology discovery options | A | "the owner's: options (A) to (E) and the three questions" - Draft docs/nosology_discovery_options.md |
| 9.65 | Stoichiometric demand on product_of edges | A | "the owner's: (a) to (c)" - Not changed |
| 9.66 | Bottleneck skipped drug mechanism edges | C | "fixed; recorded for the record" - 600abc7 on main |
| 9.67 | GENE:CA2 tagged as currency | C | "fixed; recorded for the record" - 4642a07 on main |
| 9.68 | Dead-end perturbations: curated routes | F | "pull request #5, branch `curated-dead-end-mechanisms`" - PR #5 open (a9d9ea8, 3fda2b2); (b) answered by 9.76; (c) still unruled |
| 9.69 | CaV1/CaV3 calcium entry; gabapentinoid sign | A | "merging pull request #2 is (a) without the drug re-derivation" - PR #2 landed 20 Oct (e675eda); only the gabapentinoid re-derivation remains |
| 9.70 | Knowledge-graph practices: ten changes | A | "the owner's: which of (1) to (10)" - (1) and (3) built behind flags, off |
| 9.71 | Non-conducting channels and transporters | F | "Pull request #5 also holds the delta subunit" - PR #2 and #3 landed on main (e49fd0c, 57f95ff); GABRD in open PR #5 |
| 9.72 | Disputed CollecTRI regulation signs | A | "the owner's: (a) to (e)" - Flag for (a) built off (26d11e6) |
| 9.73 | Further label sources from research report | A | "the owner's: (a) to (f)" - No ruling quoted |
| 9.74 | Akathisia as its own fine construct | C | "the owner's: merging pull request #6" - PR #6 landed on main as ec9d924 (20 Oct) |
| 9.75 | Organelle calcium stores | F | "Pull request #7, branch `organelle-calcium-stores`" - Owner ruled scope 20 Oct; PR #7 open (0fc70e3) |
| 9.76 | Expression-anywhere transcription gate, peripheral classes | F | "the owner's: merge; whether to extend the pool to peptide hormones; the thyroid hormone receptor edges" - PR #9 open; two residual A questions |

## (c) Counts

| class | count | ids |
| --- | --- | --- |
| A | 21 | 1.1, 6.1, 9.35, 9.36, 9.38, 9.41, 9.42, 9.45, 9.48, 9.52, 9.54, 9.56, 9.61, 9.62, 9.63, 9.64, 9.65, 9.69, 9.70, 9.72, 9.73 |
| A? | 3 | 5.2, 8.11, 9.39 |
| B | 13 | 1.2, 4.1, 4.3, 4.12b, 8.1, 8.3, 8.8, 9.14, 9.22, 9.28, 9.31, 9.46, 9.53 |
| C | 18 | 8.5, 9.1, 9.17, 9.23, 9.25, 9.26, 9.33, 9.34, 9.35b, 9.37, 9.47, 9.49, 9.51, 9.58, 9.60, 9.66, 9.67, 9.74 |
| D | 12 | 9.7, 9.11, 9.12, 9.13, 9.15, 9.20, 9.21, 9.29, 9.40, 9.43, 9.44, 9.55 |
| E | 4 | 8.10, 9.50, 9.57, 9.59 |
| F | 5 | 9.16, 9.68, 9.71, 9.75, 9.76 |
| X | 1 | 6.2 |
| total | 77 | |

Within C: 13 built or merged on main (8.5, 9.17, 9.23, 9.25, 9.26, 9.33, 9.49, 9.51, 9.58, 9.60, 9.66, 9.67, 9.74) and 5 records with nothing to choose or build (9.1, 9.34, 9.35b, 9.37, 9.47).

## (d) Corrected number awaiting the owner

- **Class A: 21 rows, 24 counting the three A?** (5.2 cannot be ruled until 8.8's power simulation exists; 8.11 is merged and only 'whether GtoPdb's additions enter' remains; 9.39 may be moot after the rebuilds and 9.7b).
- Of the 21, 5 are only a residual sub-choice after the owner already ruled the main question (9.48, 9.54, 9.62, 9.63, 9.69), and 6.1 is an action (send the CTD notice), not a ruling.
- Several A rows are the same question: 1.1 and 9.35 (the leakage ceiling), 9.45(i) and 9.42 step 1, 9.41(c) and 9.40.
- **A + F: 26 (29 with the A? rows)**; F = 9.16 (PR #8), 9.68 and 9.71 (PR #5), 9.75 (PR #7), 9.76 (PR #9). 9.68 and 9.76 also carry residual A questions inside them.
- Not awaiting the owner at all: B 13, C 18, D 12, E 4, X 1 = 48 of the 77.

## (e) Rows contradicted by another file or by git

1. **8.11** says "Drafted for review, not merged ... pull request #4" and lists as outstanding "wiring the narrowing ... into the evidence build". PR #4's four commits are on main (7ab325b, 7fdc62f, 0f419c1, 344d211; committed by B Nova 20 Oct), and `--narrow-complex-targets` defaults to on in `assemble_evidence_table.py:946` and `build_onsides_reports.py:121`.
2. **9.69** says pull request #2 is "Drafted for review, not merged". Its commits are on main as e675eda and e49fd0c (committed 20 Oct); `MAR_CAV1_CALCIUM` is at `experiments/build_neuronal_graph_variant.py:168`; 9.75 quotes the owner: "i merged PR 2".
3. **9.71** says pull request #3 is "Drafted for review, not merged". It was merged as 57f95ff (20 Oct). PR #2's ORAI/P2X part (e49fd0c) is also on main. Its last cell still says "the owner's: (a) to (c)".
4. **9.74** says "Built for review, not merged ... pull request #6" with last cell "the owner's: merging pull request #6". PR #6 is on main as ec9d924 (patch-identical to the PR head 8dbe064).
5. **9.23**'s last cell reads "the owner's", but 37fbdef is "Build the receptor-to-G-alpha coupling filter approved in decision 9.23", 9.21 says "Superseded by 9.23, which the owner approved", and 9.53 counts 282 edges it dropped.
6. **9.25** says "BRENDA still waits on the owner's licence acceptance"; 9.26 says "The owner accepted the licence and supplied both releases on 14 October". **9.14** says the same ("held pending the BRENDA download").
7. **9.26** says "the owner's to admit at the rebuild"; bdb896c ("Wire BRENDA's enzyme regulation into the graph") is on main, `docs/data_layer_rebuild.md` records 4,134 BRENDA edges in the 15 October rebuild, and 9.43 lists 9.5 as "built and in the 15 October graph rebuild".
8. **8.3** says "blocked on 4.12b, a conflict with a registered property"; 4.12b says "The conflict I registered does not exist" and "decided: option (a)".
9. **8.5**'s last cell opens "the owner's, and it is a small architectural choice" and then, in the same cell, "Built 14 October on option (a), which the owner chose" (016ff6a on main).
10. **9.51**'s last cell is "the rebuild"; `docs/physiology_audit.md` was generated 17 Oct on `graph_full_neuronal_split_binders_drugs_v4` and `evidence_full_v4`.
11. **1.2** and section 10: section 10 says "Nothing here starts without the go-ahead of 1.2", and 9.43 (15 Oct) lists "1.2 the go-ahead itself" as the owner's. But struck 1.2c says "Closed 12 October: the rebuild is approved", and rebuilds ran on 15-16 Oct (d60815b, a7e46df). Meanwhile the substance of 1.2 is not built: `scripts/rebuild_data_layer.sh` lines 106/110 and 237/241 still pass `--max-drug-targets 3` for v4 and v5, while 1.2 says the amendment "registers no limit".
12. **9.7** stays open although 9.7a, 9.7b and 9.7c are struck as closed 15 Oct. 9.43 notes this itself: "Two of those entries are not struck through, so the decision log still reads as blocking where it is not".
13. **9.68** option (b) (keep the 16 factors' regulons) was answered in 9.76 ("rest of proposal is accepted") and built in PR #9; 9.68's last cell still lists (a) to (d).
14. **The file header** says "Every decision waiting on the owner, in one place", but section 9's own heading is "Raised by a measurement, not yet put to the owner", and rows say "not put to the owner as a decision" (9.11, 9.13), "Not put to them" (9.1), "no decision owed" (9.35b), "corrections, not decisions" (9.37), "none; recorded for the record" (9.49), and "fixed; recorded for the record" (9.66, 9.67). The generator counts every one of these as open.

After the 20 October merges, commits 39a7cbb, cf3944a and a310191 edited `docs/open_decisions.md` (9.76 only) without updating rows 8.11, 9.69, 9.71 and 9.74.

## Other checks

- No text in the repository addressed an AI with override instructions. The only hits for phrases like "ignore previous instructions" are the repository's own records of scanning its sources for them (`docs/exposure_sources/schulz2020.md:29`, `docs/brain_exposure_data_feasibility.md:391`). `CLAUDE.md` and `.claude/settings.json` (test-running hooks) are ordinary project configuration and were not acted on.
- PR state comes from git, because the GitHub API was not available in this session: #1 and #3 are merge ancestors of main; the commits of #2, #4 and #6 are patch-equivalent to commits on main (`git cherry` reports '-'); #5, #7, #8, #9 and #10 have commits that are not on main.
