# Exact-slot loss support accounting: exposed-data plan v1

Publish this plan and a tested implementation before calculating the new support
partition. The complete native study and all known-process calibration results
are already exposed. This is an arithmetic diagnostic of the fixed estimator,
not independent evaluation, a model revision or a new preference test.

## Question and immutable inputs

How much of the native F1/F0 loss is contributed by a scoring previous/target
pair absent from its training exact-slot cell, versus an observed pair? Keep the
accepted #194 model, all four ZL3b/IT2a split/join treatments, all 2,165 loci,
86 dependency groups, five folds and every original transition. Use only the
already published native fitted tables and exact probability receipts, together
with the accepted coarse fitted tables. No raw transcription, image, refitting,
new sampler, selected folio or inferred glyph policy is needed.

The native producer is SHA-256
`f299d79d49555b312651658e71289b77c97f5e2aac9067fa6594bfd1a9e2632f`;
the lossless native report is
`7c17ddfe3f9826122b5a7a305af93d224ded94798f1cf2124b5e8424baa7ac64`.
The original coarse report is
`d271a627a4f37f4916f032fd5021cf6e14bcc9c0817337a6aeeccb1f29cc9810`.
Pin this plan, native plan/manifest/source/report, coarse report and exposed
calibration result/report. Verify all identities before parsing records.

## Exhaustive categories, fixed in this order

For each scored transition let n be the fine training cell total, nx the total
for its previous class x, ny the total for its target class y, and nxy their
joint count. Obtain these integers from the scoring fold's retained fine table,
with zero counts for absent cells. Partition using the first matching rule:

1. `unseen_fine`: n = 0.
2. `unseen_previous`: n > 0 and nx = 0.
3. `constant_previous`: exactly one previous class occurs in the training cell.
4. `unseen_target`: ny = 0 in a variable previous-class cell with nx > 0.
5. `unseen_pair`: nxy = 0 but ny > 0, in that same variable/seen-previous cell.
6. `seen_pair`: nxy > 0 in a variable/seen-previous cell.

These six categories include every transition once. Categories depend on the
scored class and training support; they are descriptive outcome partitions,
not prospectively identifiable scoring cohorts or causal groups.

The first four categories have F1 = F0 exactly. In `unseen_pair`, writing p for
the existing coarse prior, F0 = (ny + 10p)/(n+10) and F1 = 10p/(n+10).
Thus F1/F0 = 10p/(ny+10p) < 1 and the transition gain is strictly negative.
`seen_pair` permits either sign. These identities are exact fractions, not
inferences from observed gain signs. Verify them on every retained receipt.

## Complete accounting

Reconstruct both exact probabilities from the published fine and coarse tables
without calling the model's probability/fit/score API. Check table marginals,
all receipt supports, class/slot ranges, constant flags, fitted-table hashes,
fold exclusion/assignment metadata and native locus identities. Reproduce the
native F0/F1 losses and fixed aggregate gains within a declared floating-point
tolerance of absolute 1e-10 plus relative 1e-12; exact probability/support checks
allow no tolerance. Keep measured residuals.

For every category retain count, F0/F1 losses, gain sum, positive/zero/negative
transition counts and conditional gain per category transition (null when empty).
Also retain its additive contribution to the original whole-treatment pooled,
equal-locus and equal-group gains. The latter two divide each locus/group bucket
gain by that locus/group's original total transition count before averaging over
all original loci/groups. Never average only nonempty category groups or change
the original denominator. Retain all six buckets, including empty buckets, for
every locus, group, fold and complete treatment. Preserve closure against the
original total; a category may exceed the total loss when another offsets it.

No collection threshold, p-value, tuned support cut, model adoption or native
persistence estimate is added. Report all treatments and both beneficial and
adverse categories. In particular, do not presuppose that absent pairs account
for all or most of the losses.

## Validation and limits

Before execution test all six categories, exact equalities/strict-loss identity,
both signs for seen pairs, count/receipt corruption, empty buckets, unequal
group/locus denominators, complete closure, typed report drift, changed pins and
existing/initial/late input aliases. Use invented mathematical fixtures only.
Publish the tested implementation and manifest before native aggregation.

After calculation use a separate receipt-driven checker: independently look up
pair counts, classify all transitions and reconstruct the accounting, using the
saved exact probabilities rather than the producer's reconstructed formula.
Compare every output field and verify complete producer byte replay. Inspect
the exact outgoing contents, decompressed archive, links and commit metadata.

This partition explains where this estimator gains or loses on exposed encoded
classes. It cannot establish why native sequences have those supports, isolate
estimation variance causally, prove absence/presence of dependence, explain the
manuscript or override the calibration's moderate-persistence failure. All
representations, exposure and image/dependency limits of #194 remain. A later
model or causal claim needs its own registered, useful comparison.
