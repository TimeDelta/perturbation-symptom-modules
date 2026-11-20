# Reconstruction errata

Curation errors found in Human-GEM or its inherited Recon3D content, with what the build does about each. The build
records the same actions in the gitignored summaries (for example data/processed/graph_neuronal/neuronal_variant_summary.json);
this file is the committed, human-readable record.

## 5-hydroxy-L-tryptophan secreted as if it were a transmitter (Recon3D)

Human-GEM reactions MAR00052 ("5-Hydroxy-L-Tryptophan Secretion via Secretory Vesicle (ATP Driven)") and MAR07634
("transport of 5-hydroxy-L-tryptophan (cytosol to extracellular)"), both carrying the Recon3D identifier
`5HTRPVESSEC`, move 5-hydroxy-L-tryptophan (5-HTP) from the cytosol to the extracellular space and are gene-associated
to the vesicular monoamine transporters SLC18A1 and SLC18A2 (VMAT1, VMAT2).

This is a miscuration. 5-HTP is the amino-acid precursor of serotonin: aromatic L-amino acid decarboxylase (DDC/AADC)
decarboxylates it to serotonin inside the neuron, and it is serotonin, the monoamine, that VMAT2 loads into the
vesicle. 5-HTP still carries its carboxyl group and is not a VMAT substrate, so a VMAT-driven vesicular secretion of
5-HTP itself does not occur. The reaction appears to have been built by analogy to the genuine monoamine secretion
reactions without substituting the decarboxylated product.

Build action (experiments/build_neuronal_graph_variant.py): both reactions are in the set of vesicular cytosol-to-
extracellular shortcuts the neuronal variant deletes, so they are removed with every edge they carry when no
non-vesicular transporter also catalyses them. The correct route, cytosolic 5-HTP decarboxylated to serotonin and
serotonin loaded by VMAT2 (RCT_380586) then released, is present from Reactome. The deletion therefore removes a
spurious route rather than a real one; it is not a loss of coverage.

## beta-alanine secreted as if it were a transmitter (Recon3D)

MAR00087 ("B-Alanine Secretion via Secretory Vesicle (ATP Driven)") and MAR07736 ("transport of beta-alanine (cytosol
to extracellular)") move beta-alanine from the cytosol to the extracellular space, gene-associated to the vesicular
inhibitory amino acid transporter SLC32A1 (VGAT). beta-Alanine is a weak VGAT substrate in vitro, but a VGAT-driven
vesicular secretion of beta-alanine as a transmitter in the brain is not established, and these reactions have the same
"secretion via secretory vesicle" form as the dopamine and GABA reactions that are genuine. They are deleted with the
other vesicular shortcuts; if a vesicular beta-alanine role is wanted later it should be added as a curated reaction
with a citation, not inherited from this form.

## Why these are deleted rather than left with their catalysis dropped

Dropping only the gene-reaction association would leave an uncatalysed reaction that still moves the metabolite from the
cytosol to the extracellular space, and the linear-response and message-passing encoders both propagate
substrate -> reaction -> product whether or not a catalyst is attached. The reaction has to be removed entirely for the
vesicle to become the only exocytosis route (see the VMAT2 handling in docs/experiment_design.md, section 5.2).
## Human Phenotype Ontology annotation errata (added 21 October 2026)

Scope note: the three entries below are curation errors in HPO annotation rows rather than in Human-GEM or Recon3D.
They are recorded here because this is the committed record of source curation errors and what the build does about
each. Found while classifying the monogenic negative-report pairs
(`docs/monogenic_negative_report_pairs_2026-10-21.md`, decision 9.85), on the pinned HPO release v2026-09-01.

### POLG's "Dementia 0/35" is a cohort of patients with TYMP mutations

POLG reaches OMIM:603041 (mitochondrial neurogastrointestinal encephalomyopathy, MNGIE) only through
`mim2gene_medgen` in `genes_to_disease.txt`, not through a curated gene-disease assertion. The negative annotation on
that disease, Dementia at 0 of 35 patients, cites PMID 10852545, which is Nishino et al., "Mitochondrial
neurogastrointestinal encephalomyopathy: an autosomal recessive disorder due to thymidine phosphorylase mutations",
Ann Neurol 2000;47(6):792-800. That paper reports "21 probands (35 patients)" in whom "Homozygous or compound
heterozygous mutations were present in all patients tested" in the thymidine phosphorylase gene, that is TYMP. The
0-of-35 therefore describes TYMP carriers and says nothing about POLG.

Build action: none yet. The pair is a candidate for exclusion from the monogenic negatives; it is listed as an
erratum here and left in the table until the owner rules on decision 9.85, so that no count changes silently.

### CHCHD2's two negative annotations cite an unrelated paper

Both negative rows behind CHCHD2 cite PMID 12244316, which is Takashima et al., "Mutation of TDP1, encoding a
topoisomerase I-dependent DNA damage repair enzyme, in spinocerebellar ataxia with axonal neuropathy", Nat Genet
2002;32(2):267-72, doi:10.1038/ng987. That paper concerns TDP1 and SCAN1 and does not mention CHCHD2, so the
reference is probably wrong in the source. Both CHCHD2 records are among the 13 that are not labels, so nothing in
training reads them today.

Build action: none; recorded so that a later pass does not treat these as evidence of absence.

### The negative on MAPT parkinsonism rests on a susceptibility association

The negative comes from an Orphanet association typed "Major susceptibility factor", which is not a causal
gene-disease assertion. An absence of a phenotype in a susceptibility cohort is weaker than an absence in a
monogenic cohort, and the evidence model does not distinguish them.

Build action: none; it bears on decision 9.85 and on how the evidence classes treat Orphanet association types.
