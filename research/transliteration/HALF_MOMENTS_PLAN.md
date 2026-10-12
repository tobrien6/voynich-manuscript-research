# Exact half-control moments: plan v1

Question: what is the exact conditional variance of the accepted interior
association statistic under ideal independent uniform occurrence permutations
within its early and late halves? Can this independent calculation reproduce
every invariant identifier in the accepted swap-feasibility diagnostic?

This supplements the accepted [half-position controls](INTERIOR_HALVES.md) and
[invariance audit](HALF_DEGENERACY.md). The manuscript corpus, the original
effects, all 999 deterministic controls, and the invariant classifications are
already exposed. Publish this plan and validate the implementation using
synthetic inputs before calculating manuscript variances. This is a descriptive
mathematical audit, with no new candidate, criterion, null draw, tail probability,
normal approximation, or decipherment claim.

## Fixed inputs and comparisons

Keep all 2,165 original loci, all four ZL3b/IT2a split/join treatments, their
source and length-corpus digests, every exclusion, and equal locus weighting.
Use plain ASCII notation lengths and the original ceil(m/2) split. The first
and last source-token slots remain outside the interior statistic. Constant
and invariant loci remain in the original denominator.

Pin these accepted reports before deriving anything from source material:

| Report | SHA-256 |
| --- | --- |
| `interior_length_order.json` | `d3ada06de64c80f315ea6fa38f71f25158857cdf0d2a34728d1c6fc6ad7b6a6c` |
| `interior_half_controls.json` | `6b239d3a7b52018f6f71bffb07f40df9347bf3c1bf964387378e8c926ce94d6c` |
| `half_control_invariance.json` | `a3e598134b374c50f18b9e5b6027eb54436e7f142bb64a52f21b99c16392f36f` |

Verify the complete original selection and source identities before the new
calculation. Rebuild the length vectors through the accepted conservative
adapter. Record and verify imported helper and catalog bytes, and record this
plan and implementation fingerprints. Fail on any input, cohort, treatment, or
accepted invariant-identifier mismatch.

Report every locus's exact numerator mean and variance, exact normalized
association variance, and invariant status. Under the stipulated independent
locus permutation ensemble, report the exact variance of the equal-locus mean,
its approximate standard deviation, and the original 999-control empirical
standard deviation divided by that exact-ensemble standard deviation. Retain
all four comparisons regardless of their direction or size. Recalculate no
controls and change none of the accepted report bytes.

Store per-locus reduced fractions as decimal numerator/denominator strings.
Store the possibly long aggregate fraction as explicitly labelled hexadecimal
numerator/denominator strings plus a 60-significant-digit decimal presentation;
this avoids interpreter decimal-integer conversion limits without discarding
exactness. Display standard deviations and empirical ratios as approximations.

## Exact calculation

For interior lengths x of size m, set d[i] = m*x[i] - sum(x),
D = sum(d[i]^2), and Q = sum(d[i]*d[i+1]). The uncentered association is
m*Q / ((m-1)*D) when D is nonzero; use the accepted zero convention when D=0.
Half-centering subtracts a fixed expectation and does not change variance.

For k distinct positions in one permuted block with exponents r[1] through
r[k], compute E[product(d[position[j]]^r[j])] by summing over ordered assignments
of distinct original occurrences, divided by the falling factorial (n)_k.
At most four positions and total degree four are needed for Q squared.

Implement the assignment sum as a subset dynamic program. Start with weight
one at the empty assigned-position mask. For each original occurrence value a,
either leave it unused or assign it to one still-empty position j, multiplying
the old mask weight by a^r[j]. Update from the previous occurrence's states,
so one occurrence cannot fill two positions. The full-mask coefficient is the
ordered distinct-occurrence sum. Equal values remain separate occurrences.
Empty exponent sets have expectation one. Reject impossible requests for more
distinct positions than a block contains.

For every adjacent edge, group its endpoint exponents by early/late block.
The blocks are independently permuted, so multiply their exact block moments.
Sum these edge means to obtain E[Q]. For every ordered pair of edges, combine
exponents at shared positions, group them by block, multiply the block moments,
and sum to obtain E[Q^2]. Cache identical exponent patterns and their geometric
multiplicities. Then Var(Q) = E[Q^2] - E[Q]^2, and multiply by
(m / ((m-1)*D))^2 for the association variance. Use exact integer/Fraction
arithmetic throughout and reject a negative exact variance.

Check each exact association mean against the accepted half-expectation
formula. Zero exact variance is equivalent to constant Q on the finite
positive-weight permutation support. Compare its complete identifier set with
the independently derived accepted swap-feasibility set. This comparison must
not call the swap classifier from the moment algorithm.

If N is the unchanged locus count, independent locus permutations imply
Var(mean) = sum(Var(locus))/N^2, including zero-variance loci. This independence
describes a control ensemble, not independent manuscript observations, pages,
images, or transcription treatments. The exact ensemble also differs from the
finite empirical measure on 999 deterministic hash-generated controls.

## Synthetic validation and limits

Before manuscript measurement, compare exact first and second moments with
complete allowed occurrence permutations for every vector of sizes 3 through
7 over {1,2,3}. Separately check block moments against direct injective
assignment enumeration, including signed and zero deviations, repeated values,
singleton blocks, and fourth-degree patterns. Verify invariants, affine
invariance of normalized variance, fixed endpoints, input immutability, and
equal-locus weighting with zero-variance members. Reject malformed lengths,
duplicate identities, changed pins, and drift in committed output.

Protect the catalog, every native source, accepted reports, plan, implementation
and imported helpers from direct paths, symlinks and hardlinks used as output.
Check before calculation and immediately before the final write, including
aliases created during calculation, using temporary synthetic fixtures only.
Support script and package entry points with identical report bytes.

An exact conditional spread neither identifies a physical ordering mechanism
nor establishes that a normal tail is valid. No p-value is inferred from a
standard deviation. These already exposed, dependent representations supply
no untouched evaluation, glyph adjudication, language identification, reading,
or translation. The next separate test would require a prospectively specified
mechanism and exposure-valid evidence; it is outside this diagnostic.
