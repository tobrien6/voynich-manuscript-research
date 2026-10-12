# Exact half-control invariance audit: plan v1

Question: which locus statistics are unchanged under every allowed early/late
half permutation in the [interior sensitivity proposal](https://github.com/tobrien6/voynich-manuscript-research/pull/47)?
That proposal explicitly records only the narrower count of individually
constant halves. This supplement will classify the remaining invariant cases
without changing its cohort, statistic, denominator, controls or interpretation.

This is an exploratory diagnostic on already exposed ZL3b/IT2a material, not a
decoding candidate or an unseen evaluation. Commit this plan and verify the
algorithm on synthetic fixtures before inspecting manuscript classifications.

## Fixed inputs and output

Use the pinned sources and unchanged 2,165-locus cohort from
[the original interior analysis](INTERIOR_ORDER.md), including all four
source/spacing treatments. Verify the exact parent report SHA-256, cohort
selection, length-corpus digests, source pins and treatment denominators before
classification. Keep the fixed ceil(m/2) early/late split and both endpoints
outside the statistic. Preserve every locus, including constants.

Publish a separate diagnostic with method/plan/source/parent identities,
all invariant locus identifiers, the narrower both-half-constant count,
and the additional invariant identifiers. Report only classification counts
and source notation lengths; run no new null draws, change no statistic or
p-value, and create no raw transcription or image payload.

## Exact decision rule

For interior lengths x, let m be their count and d[i] = m*x[i] - sum(x).
The squared-deviation sum and normalization of the original statistic remain
fixed under allowed permutations. Its varying numerator is therefore
A = sum(d[i]*d[i+1]). Constants are invariant by definition.

Adjacent swaps within each block generate every permitted permutation.
Swapping adjacent unequal deviations a and b changes A by
(b-a)*(left-right), with an absent chain neighbor represented by zero.
Consequently A is invariant if and only if every feasible adjacent swap,
in every possible block arrangement, has zero change.

Check this without enumerating full permutations: for each within-block pair
position and each pair of distinct supported deviation values, remove their
occurrences from that block's multiset. Enumerate the possible left and right
neighbor values from their respective blocks, or the absent-neighbor zero.
If both neighbors occupy the same block, enforce remaining multiplicities so
the same occurrence cannot fill both positions. A feasible pair with unequal
neighbor values is a nonzero-change witness. Any unused occurrences can fill
the remaining slots, so this local feasibility test is sufficient as well as
necessary. If no witness exists, classify the locus as invariant.

Verify every constructed witness by evaluating the complete original statistic
on the two permitted arrangements. Keep the witness calculation internal; the
published diagnostic needs only identifiers and aggregate counts.

## Synthetic validation and limits

Compare classifications against exhaustive allowed permutations for every
integer vector of sizes 3 through 6 with values in {1,2,3}. Include repeated
values, singleton halves, all constants, two constant halves with different
values, and nonconstant examples such as [1,3,2], [1,3,2,2] and [2,2,2,1,3].
Check that a repeated occurrence cannot be reused as two neighbors, both blocks
retain their multisets, positive integer lengths are required, and translating
or positively scaling every length leaves the classification unchanged.
Protect source, plan and parent-report files from output overwrites. Replay the
complete supplemental diagnostic after generation.

An invariant statistic is a property of the permitted controls and this
representation. It does not establish constant manuscript glyphs, independent
sampling, exchangeability, direct neighbor dependence, a language or a reading.
Retain all loci in the accepted effect denominator; do not discard invariants
or reinterpret a control rejection as a decipherment.
