# Endpoint similarity under the existing segment policies

The small negative centered endpoint-distance departure persists under all
three declared EVA unit policies. On the primary ZL split treatment, the mean
departures are **-0.005201 ASCII, -0.005014 bench and -0.005282 bench/minim**.
Grouping changes costs and some invariant-unit identities. The paired changes
differ by source and spacing policy; none supplies a reason to prefer a
grouping or identify a manuscript mechanism.

## Fixed experiment and exposure

The [plan](ENDPOINT_UNIT_SENSITIVITY_PLAN.md) was published and its remote head
verified at `47acbf99eae4438a90473286b5ebba5e3ffd527d`. The implementation and
nine passing synthetic tests were published and verified at
`01832a212862f33e8df7520cd513f1370588f7af` before computing grouped manuscript
costs. The implementation is unchanged after measurement. A tenth, independent
whole-result verification test was added afterward.

This is a sensitivity follow-up to the exposed ASCII result in
[PR #152](https://github.com/tobrien6/voynich-manuscript-research/pull/152), using
its [method](ENDPOINT_EDIT_DISTANCE.md), pinned report and weighted path helper.
The corpus, earlier grouping experiments and f82r image check were already
exposed. No representation, source, cohort, control, statistic or favorable
subset changed after these results. No untouched evaluation, registered
decipherment or English reading is claimed.

Rebuild the complete ASCII parent and [common corpus](PARAGRAPH_CORPUS.md) from
pinned ZL3b/IT2a bytes. Retain **671 candidate units / 3,647 loci**, their
**233 common eligible units / 885 loci**, **438 whole-unit exclusions** and
every **652 original consecutive boundary**. All generic P subtypes, native
case, metadata, drawings and split/join comma policies remain. Empty endpoints
stop the producer. The 130 units with no interior-order choice and all other
invariant units remain included.

## Measurement and complete policy comparison

Use the three existing [accepted policies](../baselines/EVA_UNIT_PROTOCOL.md)
and exact [map/reference record](../baselines/eva-unit-protocol.json): ASCII
letters, listed bench segments, and listed bench plus minim segments. The
earlier alphabet-reference observations motivate these finite lists; this study
makes no new paleographic adjudication.

Scan each token left to right, longest match first, with lexical ties and
one-letter fallback. Segment labels retain exact native spelling and case;
joining them reconstructs the original token. Never cross token boundaries.
Unlisted forms can contain listed substrings, but no extra pattern is inferred.
These analyst-defined segments are not verified manuscript glyphs.

The statistic is unit-cost Levenshtein insertion/deletion/substitution on the
**sequence of segment labels**, divided by the maximum endpoint segment count.
For example, `ch` versus `sh` costs one under the bench map, compared with one
half as two ASCII-letter strings. No transposition or edit inside a grouped
label is allowed. Zero cost retains exact native token equality. Every boundary
has equal weight, and displayed means divide cost sums by 652. Grouping changes
both edit operations and normalization; costs are not physical distances.

| Source / spacing | ASCII centered mean | Bench centered mean | Bench/minim centered mean |
| --- | ---: | ---: | ---: |
| ZL3b split | -0.005201 | -0.005014 | -0.005282 |
| ZL3b join | -0.006289 | -0.006798 | -0.006331 |
| IT2a split | -0.006321 | -0.005858 | -0.004836 |
| IT2a join | -0.006321 | -0.005858 | -0.004836 |

| Source / spacing | ASCII observed mean | Bench observed mean | Bench/minim observed mean |
| --- | ---: | ---: | ---: |
| ZL3b split | 0.820318 | 0.824081 | 0.817729 |
| ZL3b join | 0.808286 | 0.810588 | 0.805898 |
| IT2a split | 0.818734 | 0.822474 | 0.817983 |
| IT2a join | 0.818734 | 0.822474 | 0.817983 |

Lower centered cost means more literal segment-sequence similarity than the
stated conditional order expectation. IT's two complete numerical treatments
coincide and are dependent. Bench/minim slightly strengthens the departure in
ZL but weakens it in IT; this direction difference is retained. Preserving the
sign under finite maps does not establish a correct glyph inventory or
calibration against a language or copying process.

## Paired changes and invariant units

All representations use the **same allowed identity order**: fix first/last
loci and uniformly permute interior identities, retaining all whole-locus
content and identity multiplicities. Nothing moves across loci or paragraphs.
For grouped-minus-ASCII changes, subtract the complete edge cost matrices and
compute moments of that signed-weight path statistic. This includes covariance
between representations. Adding/subtracting marginal variances would give the
wrong paired variance. Every weighted single/joint adjacency event is accounted
for with exact rational arithmetic. Unit moments add under the stipulated
independent-unit control without asserting independent manuscript sampling.

| Source / spacing | Bench centered change | Its SD-scaled contrast | Bench/minim centered change | Its SD-scaled contrast |
| --- | ---: | ---: | ---: | ---: |
| ZL3b split | +0.000187 | +0.122188 | -0.000081 | -0.041174 |
| ZL3b join | -0.000510 | -0.313858 | -0.000042 | -0.020364 |
| IT2a split | +0.000463 | +0.309669 | +0.001485 | +0.743297 |
| IT2a join | +0.000463 | +0.309669 | +0.001485 | +0.743297 |

SD scaling describes conditional variation, with no normal tail, threshold,
equivalence decision, map preference or mechanism claim. A small paired
departure is not proof that representations are equivalent. The changes are
not a causal fraction explained in a common physical unit.

| Source / spacing | ASCII varying | Bench varying | Bench/minim varying | Bench paired varying | Bench/minim paired varying |
| --- | ---: | ---: | ---: | ---: | ---: |
| ZL3b split | 99 | 98 | 99 | 84 | 96 |
| ZL3b join | 99 | 100 | 100 | 93 | 99 |
| IT2a split | 101 | 99 | 100 | 85 | 96 |
| IT2a join | 101 | 99 | 100 | 85 | 96 |

All counts are out of 233 units. In ZL split, bench grouping makes three
previously varying units invariant and two previously invariant units varying.
Bench/minim makes two transitions in each direction, so its unchanged total
conceals a changed set. Every identity/transition is retained. A paired change
can be invariant even when both marginal costs vary.

## Scope audit and verification

The audit counts **1,304 original boundary endpoint roles** per source/spacing
treatment. A token used in two roles counts twice, without implying two
independently sampled manuscript words.

| Source / spacing | Native ASCII letters | Bench segments | Bench/minim segments |
| --- | ---: | ---: | ---: |
| ZL3b split | 6,420 | 5,898 | 5,451 |
| ZL3b join | 7,116 | 6,520 | 6,025 |
| IT2a split | 6,459 | 5,924 | 5,487 |
| IT2a join | 6,459 | 5,924 | 5,487 |

Uppercase singleton fallback counts in this population are zero. The listed
unlisted example `ith` occurs once in either IT treatment; all other listed
example counts are zero. These restricted audits do not enlarge the maps or
establish completeness.

The [complete report](endpoint_unit_distance.json) pins the parent, maps,
segmenter, plan, helpers and corpus provenance. It retains every unit/member
identity, both grouped cost matrices, all locus initial/terminal segment counts,
exact unit/aggregate moments and variance components, **1,390,744** evaluated
joint calculations across policies and paired changes, invariant sets/transitions
and audits. ASCII matrices and common probability matrices remain in the pinned
parent; signed matrices are exactly reconstructible. Ordered segmentation
digests preserve payload identity without publishing the native corpus.

Python 3.10 or later; standard library only:

```sh
PYTHONPATH=tests python3 -m unittest test_endpoint_unit_distance test_endpoint_distance test_paragraph_token_corpus test_eva_unit_sensitivity -v
python3 scripts/endpoint_unit_distance.py --check research/transliteration/endpoint_unit_distance.json
python3 scripts/endpoint_unit_distance.py --output /tmp/endpoint-unit-distance.json
```

All **43 focused tests** pass. Nine pre-execution tests compare a separate regex
scanner on 351 tokens per policy, recursive edit costs on 225 segment-sequence
pairs, and 105 synthetic marginal/paired matrices against all anchored orders
through seven identities. They also check case/precedence/partial fallback,
cohort/metadata retention, signed and invariant changes, changed/forged parent
rejection, strict JSON scalar types and initial/late symlink/hardlink aliases.

The post-result tenth test independently reconstructs every real segment vector
and cost matrix. Direct assignments of identities to positions verify every
single/joint probability without the production chain counter or moment
function. It checks all 1,390,744 joint calculations, every unit/aggregate exact
moment and decimal display, variance component, invariant transition, segment
count and audit/digest. Complete deterministic report replay also passes.
The writer serializes in memory, repeats protected-path checks, then writes
those bytes; source, code, plan, parent and verification aliases are protected.
No image binary or native corpus payload is added.

## Limits and next test

This finite sensitivity concerns encoded segment sequences under specified
order controls. It does not validate segmentation, glyph function, physical
reading routes or a manuscript-generating mechanism. Source/policy dependence,
severe whole-unit selection and complete prior exposure remain. Fine position
gradients and other content dependencies remain possible explanations for the
small departure.

A mechanism needs a justified representation and frozen joint predictions,
available conditional variation disclosed, and prospective evidence under the
[decipherment protocol](../DECIPHERMENT_PROTOCOL.md). Image/glyph review and a
traceable translation remain pending.
