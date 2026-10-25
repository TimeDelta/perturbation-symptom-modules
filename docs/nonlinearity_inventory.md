# Where linearity binds

Every place the physiology needs something the linear-response encoder cannot represent because it is linear, with
what the code does instead. Kept current for decision 9.81 (saturation inside the fixed point). The second question
9.81 was raised with, whether the message-passing encoder leaves the tested models, was settled on 22 October 2026 by
decisions 9.77 and 9.78: the encoder is a robustness reading under the registered rule `robustness_models`. Counts are
the repository's own, taken on `data/processed/graph_full_neuronal_split_binders_drugs_v4_enzymes` (49,796 nodes,
280,966 edges) on 21 October 2026 unless another source is named. Written 21 October 2026; read against the
repository at 7104489 on 25 October 2026.

## 1. The cases

Cases 1 to 6 are from `docs/physiological_adherence_review.md` (13 October 2026), whose section is named.

| # | Case | Section | Size | Status |
|---|---|---|---|---|
| 1 | Competition between drugs at a shared site | 12 | 1,184 of 9,908 (drug, drug, gene) triples share a site; 7,792 have a site unknown | Registered limit: "competition is saturable and so cannot be a relation inside a linear propagation" |
| 2 | Partial agonism, positive and negative allosteric modulators | 12 | 357 entry rows at +0.5, 19 at -0.5, over 41 drugs, 33 of which have no other kind of target | The fix is "scaling the endogenous ligand's state rather than adding to it", which "is not linear" |
| 3 | Conjunction of complex members in propagation | 10 | 542 entities need all members, 238 need any one; 147 two-member conjunctions, 1,202 member proteins, 201 perturbed genes | Open. "nothing in the graph tells them apart". A minimum over the signed field is ruled out (9.81: "better handled by a different control"); decision 4.2 already gates a complex by its limiting member's expression |
| 4 | Receptor adaptation: desensitisation, internalisation, downregulation, tolerance | 11 | Not represented in code or documents; the labels are largely chronic-dosing | "the largest unrepresented piece of pharmacology in the study". A state-dependent gain, so a product of two states |
| 5 | Knockout against inhibitor; occupancy | 11 | 154 of 222 drugs carry a total input of 1 | Occupancy is registered as an input (amendment item 29); occupancy itself saturates |
| 6 | Compartment pH ceiling | 5, 6 | 18,928 of 49,796 nodes take a weight; 25,741 have no compartment; 5,127 transport reactions take none | Applied after the fixed point; `calibrate_ph_sensitivity` is called by no trainer code |
| 7 | Dosage asymmetry | - | All gene perturbations | The response is positively homogeneous of degree one (the bottleneck's comment states it), so a knockout cannot saturate at zero activity while an overexpression does not |
| 8 | Multistability, hysteresis and sustained oscillation | - | The clock genes' CollecTRI edges are in the graph | A linear map has one fixed point or a continuum of them, and the contraction bound makes it unique |

**On this list as evidence.** Most entries were written in Claude sessions rather than observed independently. The
counts are measured and the code claims can be checked, so the list stands; the sense that the problem keeps
coming back is partly the same analysis being made again, which is why this document exists.

## 2. The linear encoder's nonlinearities, and where they sit

Fixed-point update: `state = (1 - damping) * state + damping * (relation_messages + node_major_input)`, damping 0.5,
the input added again every round, tolerance 1e-3, at most 60 rounds. Contraction: `|gain_r| <= 0.9` per relation and
channel, and every row of `sum_r |S_r|` sums to at most 1 over the edges that carry (the registered normalisation is
`forward_cone`, decision 9.16: the `total_in_degree` divisor read per seed over the edges whose source that seed can
reach; `experiments/run_main_model.py --normalisation`).

| Nonlinearity | Where | Default |
|---|---|---|
| Limiting-step bottleneck (`class_bottleneck`) | after the loop | on |
| Compartment pH weight (`compartment_ph_weight`) | after the loop | on in the registered configuration, never calibrated |
| `response_scale = "signed_log"` | after the loop | off |
| Edge gates | in the loop, computed once per call and read every round | off |
| `CrossRelationAggregator` | in the loop | off (`mean`) |

Every one that sits after the loop scales the settled state and carries nothing along a route. The review says it of
pH: "the pH weight carries nowhere: a collapse of lysosomal pH cannot change the field at any cytosolic node".

## 3. Why the mixture statistics are odd

The `MIXTURE_STATISTICS` comment: "A plain maximum is not odd and is worse than even, it is sign-biased: over
negative messages it returns the least negative, which at the first step is the zero of an untouched neighbour, so it
suppresses the whole falling branch of the response and a metabolite that should drop stays at exactly zero."

The comment also cited a gain/loss mirror property as a reason, until it was corrected on 21 October 2026. That
property was never agreed and was withdrawn on 13 October 2026 (the owner: "i never accepted that"), together with
item 22a's even pH form; the registered pH weight's log form is not even.

The sign bias needs a set of messages in which an untouched neighbour contributes exactly zero, so it constrains a
statistic taken across the messages into a node. A map applied pointwise to a node's own state chooses among nothing;
f(0) = 0 is what keeps the unperturbed field at zero there.

The mixture's weighting is sparsemax by default (exact zeros, so a node type's use of a statistic can be read off),
and entmax, built 21 October 2026, interpolates from softmax to sparsemax and can be annealed to it during training.
The command-line value `softmax_mixture` is a historical name. The mixture is not in the registered model.

## 4. Decision 4.2 and the conjunction question

Decision 4.2 (closed and built 13 October 2026) gives a complex its limiting member's expression, per class, at the
complex node itself. The minimum is taken over non-negative expression, where it is the conjunction of the members
and has no sign to be biased by. 1,523 of 1,681 complexes carry a gate, median 0.150. The count of 413 complexes in
the adherence review reproduces under no reading; the three readings that do give 343, 387 and 499
(`docs/complex_limiting_member_weight.md`).

What 4.2 does not give is conjunction in the propagation itself (case 3). The message-passing encoder takes a minimum
over the signed field for `member_of`; the owner ruled that a signed AND is "better handled by a different control"
(9.81).

## 5. The two encoders side by side

- No common base class; shared code is `descriptor_treatments.py` and `edge_gates.py`.
- Duplicated rather than shared: `present_nodes`, `reset_flip_collection`, `flip_effect_estimates`,
  `perturbation_difference_field`, `descriptor_parameters`.
- Normalisation differs in substance: the linear encoder divides by the sum of the weights feeding a destination,
  over all relations together (decision 4.11), counted per seed over the edges the seed can reach (`forward_cone`,
  decision 9.16); the message-passing encoder divides by edge counts, per relation.
- Readouts differ: `channel_expansion` with `output_gate` and `descriptor_gate`, against `base_node_state` with
  `feature_projection` and `descriptor_projection`.
- The message-passing encoder has a fixed-point mode, off by default, allowed only with `shared_low_rank` weights.

## 6. Registration

`tested_models` in `configs/registered_rules.json` names one model, the noisy-OR configuration of the linear-response
encoder (`confirmatory_v2_linear_response_noisy_or`); `robustness_models` holds the message-passing noisy-OR
configuration, read and reported outside the tested family and spending no alpha (decision 9.77, 22 October 2026).
Until 22 October 2026 `tested_models` named the noisy-OR configurations of both encoders. The owner ruled on
21 October 2026 that changing them goes through an amendment (9.81), and the registered value changed that way.

## 7. Rulings that bear on the cases

- The version closest to physiology is used, and a choice made on numerical grounds is justified where it is made
  (CLAUDE.md, Modelling).
- 9.68's VAMP1 membership is related to 9.81 and decided apart from it.
- Findings 5, 13 and 14 of the slice pilot are not evidence about the current model (9.82).

## 8. Open in 9.81

1. For each case, whether its saturation goes inside the fixed point, acts on throughput after it, or stays a
   disclosed limit.
2. How conjunction is controlled for the 542 obligate complexes, given that the graph does not yet tell them from the
   238 alternatives.
3. Whether the pH ceiling is read at the right node: cytosolic H+ (`MAM02039c`) has 2,048 incoming and 1,281 outgoing
   edges, so one perturbed reaction moves it by about 1/4,096 of its own change.

Settled since the inventory was written: whether the message-passing encoder leaves the tested models. It left them on
22 October 2026 (decision 9.77) and stays as a robustness reading under `robustness_models`, not as a tested model
and not removed; the one-sided level returned to 0.05 with it (decision 9.78).
