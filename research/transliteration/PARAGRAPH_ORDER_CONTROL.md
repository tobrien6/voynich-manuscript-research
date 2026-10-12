# Boundary recurrence with intact loci and anchored paragraph ends

Keeping every locus's endpoint tokens intact changes the conditional expected
repeat count from **4.68–5.74 to 0.83–1.03**, while the observed count stays one.
Only four or five of the 233 selected paragraphs have a variable repeat count
under this new control; all 228–229 invariant units remain in the denominator.
The result shows sensitivity to the control's constraints and a severe lack of
variation for this statistic. It does not establish random paragraph order or
identify the cause of the earlier deficit.

## Question and fixed inputs

The [boundary study](PARAGRAPH_BOUNDARY_REPETITION.md), proposed in
[PR #102](https://github.com/tobrien6/voynich-manuscript-research/pull/102),
compares the observed boundary-repeat count against independent token
permutations within loci. Those permutations change first/last token roles.
This follow-up asks what happens when the complete locus sequences remain
intact and only interior locus order can change inside the same paragraphs.

The [plan](PARAGRAPH_ORDER_PLAN.md) was remotely published and verified at
`8dacaa8`; the implementation and twelve passing synthetic tests were published
and verified at `2cde96a`, before computing these manuscript control moments.
No control, cohort, statistic, tail or decision criterion changed afterward.
The complete [report](paragraph_order_control.json) pins the source/corpus,
parent boundary report and producer, new plan and implementation. All prior
source and statistical material is exposed; this is exploratory sensitivity,
not a prospective decipherment test or untouched split.

The producer replays every field of the parent report before calculation.
It retains exactly the [common corpus](PARAGRAPH_CORPUS.md): 233 whole units,
885 original loci and 652 boundaries, in all four ZL3b/IT2a split/join variants.
All retained loci are nonempty. If a parent boundary is omitted or an endpoint
locus becomes empty, the producer stops rather than silently restricting the
cohort. The original 671 matched candidates and 438 whole-unit uncertainty
exclusions stay explicit. Native token strings remain local.

## Observations and invariant units

| Treatment | Observed repeats | Parent within-locus mean | Anchored whole-locus mean | New SD | Centered count / SD | Invariant / varying units |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ZL3b split | 1 | 5.702162 | 1.026190 | 0.884404 | -0.029614 | 228 / 5 |
| ZL3b join | 1 | 4.684708 | 0.926190 | 0.831968 | +0.088717 | 229 / 4 |
| IT2a split | 1 | 5.738836 | 0.826190 | 0.788778 | +0.220353 | 229 / 4 |
| IT2a join | 1 | 5.738836 | 0.826190 | 0.788778 | +0.220353 | 229 / 4 |

The exact new means are 431/420, 389/420, and 347/420 for the two identical IT
variants. All sources retain the same sole observed repeat, `f82r.3` to
`f82r.4`. The complete original boundaries, fragment locators and drawing
contexts remain included as declared. Dependent editions and identical IT
policies do not provide independent replications.

There are 130 units with only one allowed interior order: at most three loci
when the first and last are fixed. The other 103 units have multiple orders,
but 98–99 of them still have a constant repeat count. Exact zero variance
defines invariance; a large factorial order space alone does not make a
statistic informative. The largest unit has 21 loci and 19! allowed identity
orders, all handled without enumerating that space.

Varying units are retained with complete IDs and edge events. The primary
variant's five are `f16r.5–9`, `f66r.70–81`, `f82r.1–9`, `f82v.5–10`, and
`f83r.18–24`. ZL join lacks the varying f66r unit; both IT variants lack the
varying f83r unit. These are reported consequences, not newly selected cohorts.
The unchanged 233-unit and 652-boundary denominators apply everywhere.

## Exact directed-chain control

Fix each unit's first and last locus, then choose uniformly among all orders
of its interior **identities**. Preserve every original token sequence,
endpoint, locus ID, kind, locator, inherited variables and drawing counts.
Identical payloads remain distinct identities and have their correct permutation
multiplicity. This is a mathematical relinking of atomic source records;
no source document or physical manuscript row is rewritten.

A directed edge identifies two locus records whose last/first tokens match.
Its event occurs if those records become consecutive in an allowed ordering.
Compatible required edges form chains. Contract them to blocks, anchor any
chain touching the fixed first/last record, and count arrangements of the
remaining blocks. If k unanchored blocks remain among m original interiors,
the event probability is k!/m!. Conflicting successors/predecessors, cycles,
incoming edges to the first record or outgoing edges from the last are
impossible. Joining both anchors before including every record is also
impossible. A chain covering the entire unit admits exactly one ordering.
The [plan](PARAGRAPH_ORDER_PLAN.md) states all edge cases, including singleton
units and duplicate event requirements.

The report records every endpoint-match edge, even an impossible event with
zero probability, and every pair of edges. Compute exact means and variances
from single/joint event probabilities, including incompatible and shared-node
requirements. Unit variances add under the stipulated independent-unit control.
All probabilities, covariances and moments are exact rational pairs; SD scaling
is descriptive and does not imply a normal distribution, tail or significance
threshold. Invariant units retain null SD-scaled contrasts.

## Reproduce and verify

Python 3.10 or later; standard library only, with the parent boundary/corpus
contributions present:

```sh
PYTHONPATH=tests python3 -m unittest test_paragraph_order_control -v
python3 scripts/paragraph_order_control.py --check research/transliteration/paragraph_order_control.json
python3 scripts/paragraph_order_control.py --output /tmp/paragraph-order-control.json
```

The twelve pre-execution synthetic tests include exhaustive single/double-edge
probabilities through eight identities: 204 single events and 4,284 edge pairs
over 875 complete allowed orders. Separate checks cover every binary endpoint
assignment through five loci: 1,364 matrices and 6,740 identity orderings.
They verify fixed anchors, cycles, full/partial chains, repeated payloads,
invariant units, atomic endpoint preservation, metadata, unchanged observations,
input protection, forged parent rejection, and complete typed/strict JSON replay.

A thirteenth test added after the first result independently verifies the actual
report by assigning positions directly to the identities involved in each
event, without using chain contraction or production moment functions. It
reconstructs all 25 source/policy endpoint-match edges and four edge pairs
from locally generated native tokens, then verifies every unit mean/variance,
invariant flag, observation and exact aggregate. All 60 focused tests pass;
the complete report replays exactly. Output aliases of sources, code, plans,
parent reports and verification inputs are rejected before computation or
writing, including hardlinks.

## Limits and next step

This result preserves locus endpoint roles and terminal paragraph locus
identities but changes interior neighbors and fine positions. Comparing two
conditional controls does not establish which real manuscript mechanism caused
their different expectations. With only four or five variable units, this
statistic gives little coverage for testing paragraph order. Neither close
control agreement nor invariant units validate a random-order model.

The corpus is strongly selected by whole-unit uncertainty exclusions. Encoded
loci, fragments, drawings and paragraphs remain unadjudicated physical units;
native strings are not glyph ground truth or decoded words. Source and image
dependencies persist, and conditional-control independence is not independent
manuscript sampling. No tail, model fit, candidate decision, copying explanation,
language identification, decipherment or translation is supplied.

A useful later paragraph test needs a statistic with demonstrable variation
under its declared constraints and a mechanism-specific prediction. Preserve
the unfavorable/invariant cases, address endpoint conventions and source/glyph
uncertainty, and declare dependency groups and exposure-aware prospective data
before treating a fit as evidence for a reading.
