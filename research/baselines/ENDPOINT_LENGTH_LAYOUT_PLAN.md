# Independent-token endpoint costs under fixed length layouts

Recorded 2026-10-12. Publish this plan and synthetic-tested implementation
before computing the complete new demonstration report. The accepted ASCII
endpoint result (#152), grouped sensitivity (#156), pending length conditioning
(#179), native sources and source/image observations are already exposed.
This is an exact synthetic counterexample, not manuscript fitting, realistic
language/copying simulation, power calibration or an untouched evaluation.

## Fixed question and construction

Can independent token draws produce a negative centered endpoint edit cost
solely because the original slot lengths are arranged in blocks, while the
unrestricted interior-order control moves those lengths? Does preserving the
length pattern remove that expected contrast under the same construction?

Each synthetic paragraph has six distinct locus identities, one token per
locus. Its first and last endpoint are therefore the same token. Each token's
letters are independent fair choices from the literal alphabet `a,b`, with no
state, previous-token reference or copy operation. Tokens can equal one another
by chance. Enumerate every token tuple with its exact uniform probability;
retain identity multiplicity, including repeated payloads. No native source
token, image, fitted corpus profile, parameter sweep or selected favorable
draw enters the experiment.

Use exactly these three length layouts in this order:

| Family | Original token lengths | Complete draw count |
| --- | --- | ---: |
| blocked_lengths | 1, 1, 1, 2, 2, 2 | 512 |
| alternating_lengths | 1, 2, 1, 2, 1, 2 | 512 |
| uniform_short | 1, 1, 1, 1, 1, 1 | 64 |

Original observations have five boundaries. Reuse the accepted case-preserved
ASCII unit-cost Levenshtein/max-length metric without transposition or glyph
grouping; pin its exact implementation bytes. Equal boundary weights remain.

## Two complete identity-order controls

1. Fix identities 0 and 5; enumerate all 24 interior identity orders uniformly.
2. Also preserve every original interior length label and enumerate only
   identity orders assigning tokens to slots of the same length. Blocked and
   alternating families have four orders; uniform_short has all 24. Anchors
   remain fixed even if their lengths match interiors.

Directly evaluate every complete allowed path for each token tuple. Use exact
Fractions for costs, uniform averages and population variances. Keep the same
original observation in both controls. No pending stratified helper/report
from #179 is imported or altered; this direct enumeration is separately
checkable and uses only the accepted metric.

## Predictions fixed before execution

Independently enumerate all pairs of fair binary tokens of lengths 1 or 2.
The expected normalized cost is 1/2 for either equal-length pair and 5/8 for
either cross-length direction. Thus each crossing adds expected cost 1/8
beyond the same-length expectation.

Blocked/alternating layouts have the same three short/three long identities,
fixed short first and long last. Their unrestricted reference has expected
crossing count 3: 1/2 at each anchor boundary and 2 among the three interior
boundaries. Original crossing counts are 1 and 5 respectively. Conditioning
on the original length pattern keeps that crossing count fixed. Predicted
complete-draw means of cost sums are:

| Family | Observed | Unrestricted expected | Length-fixed expected | Unrestricted centered | Length-fixed centered |
| --- | ---: | ---: | ---: | ---: | ---: |
| blocked_lengths | 21/8 | 23/8 | 21/8 | -1/4 | 0 |
| alternating_lengths | 25/8 | 23/8 | 25/8 | +1/4 | 0 |
| uniform_short | 5/2 | 5/2 | 5/2 | 0 | 0 |

Boundary-mean centered contrasts divide by five: -1/20, +1/20 and zero for the
unrestricted control, with zero in all length-fixed families. These are exact
population averages across independent token draws, not a claim that each
individual tuple has zero conditional contrast.

Report every tuple, original cost, each conditional mean/variance/centered
cost, possible-order count and invariant status. Aggregate exact expectations,
the full centered-sum histogram, negative/zero/positive counts and varying/
invariant draw counts for both controls. These sign counts have no chosen
significance threshold or false-positive/power interpretation. Preserve all
contradictions; if a prediction fails, stop for a documented diagnosis rather
than tune the construction or omit a family.

## Verification, provenance and limits

Before the full report, verify small metric pairs independently, exact draw
cardinalities/uniqueness/uniform product probabilities, anchor/stratum/order
rules, repeated identity payloads, input preservation, exact moments and zero
variance behavior on separate tiny examples. Compare direct path moments with
an independently assembled edge-probability/covariance calculation, including
signed weights. Verify typed JSON and early/late symlink/hardlink output guards.

After the first report, a separate verifier must reconstruct every synthetic
tuple, cost and complete control distribution without the production draw,
distance, order or moment functions. Verify all individual/aggregate fields,
histograms, invariance flags and analytical predictions, then replay the full
report. Pin the plan, accepted metric and own implementation. Protect source/
catalog/parent/plan/code/check inputs before computation and again immediately
after complete serialization, before writing. Publish only this original toy
data and analysis; keep all native/source artifacts unchanged.

This construction demonstrates non-identifiability of a negative endpoint
contrast as copying evidence. It does not show that length layout explains the
manuscript, validates #179's sparse conditioned cohort, estimates a realistic
effect, selects a language/mechanism or yields a translation. One-token loci,
a two-letter alphabet, prescribed lengths and short paths are deliberate toy
limits. Real mechanism tests still need justified representations, joint
predictions, useful reference variation and honestly prospective data.

Use verified `tobrien6`, matching upstream owner with admin/maintain/push
permissions, as owner/maintainer for the user-assigned focused contribution.
Inspect exact outgoing files/objects for sensitive data; use public GitHub
noreply metadata and the established final-review workflow. Do not modify
pending #179/#184 heads, self-approve or publish directly to main.
