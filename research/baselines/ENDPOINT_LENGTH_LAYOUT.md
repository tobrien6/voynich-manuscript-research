# Independent tokens can have a negative endpoint-cost contrast

Independent token draws with blocked lengths have an exact mean centered
endpoint edit cost of **−0.05 per boundary** under the unrestricted anchored
order control. Alternating the same short/long counts gives **+0.05**, and a
uniform-length comparison gives zero. Preserving the original length pattern
makes all three population means zero. All fixed analytical predictions hold
across the complete **1,088** synthetic token tuples.

This supplies a concrete counterexample to identifying neighbor copying from
a negative endpoint-cost contrast alone. It does not show that this toy length
layout explains the manuscript, estimate realistic power, select a mechanism
or produce a reading/translation.

## Fixed construction and chronology

The [plan](ENDPOINT_LENGTH_LAYOUT_PLAN.md) was remotely published and verified
at `19b1e40`; the implementation and eight passing small-example tests were
published and verified at `6060acc` before the complete report was computed.
The ninth test was added after that first result to verify every record
independently. The measured producer remains byte-identical to the published
pre-report implementation. No layout, alphabet, metric, family, prediction or
favorable subset was changed after execution.

Each paragraph has six distinct locus identities, with one token per locus.
Every letter is an independent fair `a/b` choice, conditional on the fixed
token length. Generation never refers to previous tokens; equal payloads can
occur by chance and retain their distinct identity multiplicity. There are
five original boundaries. The two heterogeneous layouts each contain three
one-letter and three two-letter tokens, with a short first and long last token.
All tuple draws have equal probability within their family: 1/512 or 1/64.

| Family | Original lengths | Original cross-length boundaries | Draws |
| --- | --- | ---: | ---: |
| Blocked | 1, 1, 1, 2, 2, 2 | 1 | 512 |
| Alternating | 1, 2, 1, 2, 1, 2 | 5 | 512 |
| Uniform short | 1, 1, 1, 1, 1, 1 | 0 | 64 |

The metric is the accepted [ASCII endpoint distance](../transliteration/ENDPOINT_EDIT_DISTANCE.md):
unit insertion/deletion/substitution Levenshtein cost divided by maximum
string length, with no transposition, case folding or glyph grouping. Its
exact implementation hash is pinned. No native source tokens, images, corpus
profiles, seed selection or fitted parameters enter this demonstration.
The pending [length-conditioning study #179](https://github.com/tobrien6/voynich-manuscript-research/pull/179)
is context, not an imported code/report dependency or an accepted result claim.

## Complete identity-order controls

Both controls fix the first/last identities and preserve complete tokens.
The unrestricted control uniformly enumerates all **24** interior identity
orders. The length-fixed control assigns interior identities only to slots
with their original length: **four** orders for blocked/alternating layouts,
and the same 24 for uniform-short. The original order always remains allowed.
Repeated payloads do not collapse identities or change probabilities.

Every path is scored directly, with exact rational population mean/variance.
The [complete report](endpoint_length_layout.json) retains all 1,088 tuples,
their uniform probabilities and observations, both control distributions and
moments, each path-cost histogram, invariance and all aggregate sign histograms.
The literal strings in that file are original `a/b` toy data, not native
transcriptions. No pending stratified helper or manuscript report is used.

## Why the predictions follow

Enumerating all short/long binary token pairs gives expected normalized cost
**1/2** for either equal-length pair and **5/8** in either cross-length
direction. A cross-length boundary therefore adds an expected **1/8** to
the equal-length expectation. Independent generation does not remove this
length dependence from the normalized edit metric.

In the heterogeneous families, the unrestricted control has three expected
crossings: one-half at each fixed-anchor boundary, plus two among the three
interior boundaries. Its expected sum is therefore `5/2 + 3/8 = 23/8`.
The blocked original has one crossing and the alternating original has five.
The length-fixed reference retains those respective crossing counts.

| Family | Mean observed sum | Mean unrestricted reference | Mean length-fixed reference | Mean centered cost per boundary, unrestricted / length-fixed |
| --- | ---: | ---: | ---: | ---: |
| Blocked | 21/8 | 23/8 | 21/8 | −0.05 / 0 |
| Alternating | 25/8 | 23/8 | 25/8 | +0.05 / 0 |
| Uniform short | 5/2 | 5/2 | 5/2 | 0 / 0 |

These are expectations across complete independent token draws. An individual
tuple can have a nonzero length-fixed centered cost; zero population expectation
does not mean every draw has zero contrast. Complete sign accounting is:

| Family | Control | Negative / zero / positive draws | Invariant / varying draws |
| --- | --- | ---: | ---: |
| Blocked | Unrestricted | 332 / 32 / 148 | 0 / 512 |
| Blocked | Length-fixed | 188 / 120 / 204 | 112 / 400 |
| Alternating | Unrestricted | 156 / 48 / 308 | 0 / 512 |
| Alternating | Length-fixed | 144 / 224 / 144 | 216 / 296 |
| Uniform short | Unrestricted | 16 / 24 / 24 | 16 / 48 |
| Uniform short | Length-fixed | 16 / 24 / 24 | 16 / 48 |

Negative and positive counts need not match when their magnitudes balance.
Zero contrast is also distinct from zero conditional variance. All exact
centered-value histograms and mean within-draw conditional variances are
retained in the report. Sign counts have no chosen rejection threshold,
false-positive-rate interpretation or manuscript power claim.

## Verification and reproduction

All **20 focused tests** pass: nine new demonstration tests and eleven accepted
endpoint tests. The eight pre-report tests check independent recursive
edit costs, all draw cardinalities/uniqueness and product marginals, every
binary length pattern through seven identities against a separate partition
order generator, and signed moments via an independently assembled directed
edge-probability/covariance calculation. They retain repeated payloads,
invariant/telescoping weights, input preservation, invalid types/shapes, changed
metric bytes, typed replay and initial/late symlink/hardlink protection of
source/catalog/metric/plan/code/test/check inputs.

The post-result verifier reconstructs each tuple from integer bit patterns,
each distance by recursive edits and each allowed path through within-stratum
partition products. No production draw, distance, order or moment function
computes its expected values. It checks all **31,744** complete path scores,
every tuple probability/observation/control mean/variance/histogram/invariance,
all aggregate expectations/sign counts/freedom counts, each analytical
prediction and all fingerprints. Full deterministic typed report replay passes.

```sh
PYTHONPATH=tests python3 -m unittest test_endpoint_length_layout -v
python3 scripts/endpoint_length_layout.py --check research/baselines/endpoint_length_layout.json
python3 scripts/endpoint_length_layout.py --output /tmp/endpoint-length-layout.json
```

All report content is serialized before the final output-path guard directly
preceding a write. Source/catalog, metric, plan, implementation, test and check
aliases are protected. Inputs and existing manuscript statistics remain
unchanged. The complete report is original synthetic data, with no downloaded
source binary, screenshot or native-token export.

## Interpretation and next evidence

A negative conditional contrast can arise under independent token generation
because the reference moves a prescribed length pattern. This counterexample
limits copying interpretations of that statistic; it does not refute copying,
prove a manuscript layout rule or validate a sparse length-conditioned test.

Six identities, one-token loci, a two-letter alphabet and lengths 1/2 are toy
choices. Real multi-token endpoint roles, character composition, transcription
uncertainty, paragraph exclusions and reading routes are not modeled. A serious
mechanism comparison still needs frozen joint predictions, justified glyph/
source representations, useful reference variation and honestly prospective
data. No language preference, decoded glyph or English translation follows.
