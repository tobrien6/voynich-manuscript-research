# Fixed grouped predictor: synthetic control plan v1

Commit and publish this plan and its synthetic-tested implementation before
generating the benchmark results. The already observed mixed results in
[grouped prediction](GROUPED_LENGTH_RESULTS.md) motivate this diagnostic.
Do not change the estimator, criterion, generator, cases or seeds after seeing
the benchmark. This is simulation of specified class sequences, not a
decipherment candidate or an untouched manuscript evaluation.

## Question and layout

Can the fixed Q0/Q1 estimator avoid a consistent preference on independent
uniform classes and detect two specified levels of direct persistence when
it uses the primary analysis's group sizes, row sizes, source labels and folds?

Pin the complete grouped-prediction report to SHA-256
`d271a627a4f37f4916f032fd5021cf6e14bcc9c0817337a6aeeccb1f29cc9810`.
Use only its **ZL3b split** locus keys, page/group identifiers, source labels,
folds and transition counts. Each simulated interior has one more class than
that row's transition count. Retain the 2,165 loci, 86 groups, five original
folds and their complete membership. Do not use the observed length classes,
fitted manuscript probabilities, losses, or gains to generate sequences.
The layout and labels are previously exposed metadata.

Pin `scripts/grouped_length_prediction.py` to
`3a987a939fb389d25a75dfaf6494b5c3a97467f0bf5fcf846edca7d3eca69fd3`,
`scripts/shuffle_token_lines.py` to
`917b590cde2d190207464ce7a12cfd5e647f4b105cd7648ef57fce5afe957c4f`,
and `scripts/interior_length_order.py` to
`729e8a774a889b6370196ab09b56d228f7b3fe4c747f169a5217488453d28c3a`.
The pending parent PR #76 supplies the estimator; this contribution depends
on its reviewed implementation and preserves its negative manuscript result.

## Three fixed generating processes

Generate classes 1 through 10; class 10 is a synthetic category and does not
encode a particular token length. Each locus starts with an independent
uniform class. For every subsequent slot, draw an independent integer `u`
uniformly from 0 through 3, then an independent candidate uniformly from
1 through 10. Retain the previous class when `u < k`, otherwise use the
candidate. Use precisely these cases:

| Case | k | Persistence probability rho |
| --- | ---: | ---: |
| independent_uniform | 0 | 0 |
| persistence_quarter | 1 | 1/4 |
| persistence_three_quarters | 3 | 3/4 |

Even k=0 consumes both draws. Conditional transition probabilities are
`d = rho + (1-rho)/10` on the diagonal and `o = (1-rho)/10` off it. Every
case has a stationary uniform marginal. Draw streams are separate per case,
replicate and locus; loci have independent stream keys.

Use the accepted SHA-256 rejection sampler `HashDraws`. Its key is SHA-256
of compact UTF-8 JSON
`["grouped-predictor-synthetic-controls-v1", 20261012, replicate, case, locus_key]`
with the parent compact serializer. Replicates are **0 through 63**, inclusive.
Do not select seeds or remove a replicate. Cases share layout but do not use
common random draws; comparisons across cases are simulation diagnostics.

## Unchanged estimator and full reporting

For each of the 192 datasets, run exactly the parent's five-fold `evaluate`
function, assigning every generated row to its original group/fold and using
its original source label. Q0/Q1 classes, target half, smoothing and fixed
preference criterion remain unchanged. All fitted probabilities use only the
other four folds. Generated values are new simulation data; the criterion is
already known and the layout is already exposed.

Retain each replicate's sequence digest, both fitted-model loss totals, pooled,
equal-group and equal-locus gains, positive fold/group counts, criterion flag,
every fold's gains and counts, every group's gains and counts, and fitted-count
hashes. Report each case's mean, minimum and maximum pooled and equal-group
gains, and the number of replicates meeting the fixed criterion. Do not discard
unfavorable simulations. Raw synthetic sequences and full fitted counts can
be regenerated deterministically; their exact digests bind the summaries.

Also score every transition under the **known generating probabilities**:
uniform Q0 and the specified diagonal/off-diagonal Q1. Retain each replicate's
realized oracle gain. The ideal stationary mean gain is
`d*log2(10*d) + 9*o*log2(10*o)` bits/transition. This is zero for independence;
it is positive for both persistence cases. The oracle is a process diagnostic,
not a model fitted on the scored data and not a manuscript prediction.

Report outcomes without a new pass/fail cutoff for the collection of
replicates. The original per-dataset criterion remains a descriptive rule;
simulation hit counts are not calibrated manuscript p-values, proof of
type-I control, or confidence in a decipherment. Do not infer detection power
for natural languages or other encoding mechanisms from these cases.

## Verification and limits

Before the benchmark, test deterministic stream replay, case/replicate/locus
separation, exact small-sequence oracle calculations, boundary-case draws,
unchanged layout/fold accounting, source label preservation, invalid layout
rejection, complete replicate aggregation and input/output protection.
After generation, replay the entire report, independently recompute selected
oracle scores, and reconcile all 192 datasets' group/fold counts and losses.

Uniform class marginals are deliberately simple. The benchmark preserves
sample-size/context sparsity but not manuscript class frequencies, within-line
position profiles, glyphs, words, copying, source uncertainty or hidden content
dependencies. It cannot explain the manuscript's mixed gains or establish a
mechanism. Its contribution is an auditable finite-sample behavior check for
this fixed estimator under known absence and presence of direct persistence.
