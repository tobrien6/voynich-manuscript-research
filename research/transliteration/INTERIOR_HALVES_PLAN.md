# Interior order with half-position constraints: exploratory plan, version 1

Record these choices before executing the half-position analysis. The original
[interior-order result](INTERIOR_ORDER.md) and its full-corpus inputs have already
been inspected. This is a targeted sensitivity follow-up to that result, not an
independent discovery, untouched evaluation, decoding candidate, or translation.
No parameter is fitted. No new source text or token representation is introduced.

## Question and fixed cohort

Does the original interior-order departure persist when the control preserves
each locus's early and late interior length distributions? This addresses one
coarse positional explanation while retaining the locus's overall multiset.
It cannot eliminate finer gradients or establish direct neighbor dependence.

Reuse the exact 2,165-locus common cohort and four ZL3b/IT2a split/join treatments
from [the original plan](INTERIOR_ORDER_PLAN.md). Recompute it through the shared
conservative adapter and require the same identity and length-corpus hashes as
the pinned parent report. Keep endpoints fixed and exclude their adjacent pairs.
Preserve drawing/ambiguity/short-locus exclusions and the constant-interior
convention. No cohort, source stratum, or page is selected from its result.

## Half-position permutation and exact expectation

For an interior length list of size `m >= 3`, split at `k = ceil(m/2)`.
The first `k` positions form the early block and the remaining positions the
late block. Independently permute lengths within each block, moving none
across the split, locus, page, or folio side. Thus every control preserves each
half's entire multiset, mean, and variance, as well as the full interior
multiset and both endpoint tokens. The crossing pair remains in the statistic.

Use the original integer deviations `d[i] = m*x[i] - sum(x)`, squared-deviation
sum `D`, adjacent product sum `A`, and normalized association
`R = m*A/((m-1)*D)`. For a block of size `n`, deviation sum `S`, and squared
sum `Q`, the expected sum of its internal adjacent products is `(S*S-Q)/n`.
This also yields zero for a singleton. The crossing pair's expectation is
the product of the two block means, because their permutations are independent.
Therefore, with subscripts `e` and `l` for the early and late blocks,

```
E_half[A] = (S_e*S_e-Q_e)/n_e + (S_l*S_l-Q_l)/n_l
            + S_e*S_l/(n_e*n_l)
E_half[R] = m*E_half[A]/((m-1)*D)
C_half = R - E_half[R]
```

Compute the expectation with exact rational arithmetic from integer lengths.
Constant interiors contribute zero to `R`, both null expectations, and both
centered statistics, and remain in the denominator. Mean `C_half` over the
same 2,165 loci with equal locus weight. Save mean `R`, the unrestricted and
half-constrained expectations, the original centered effect, the new centered
effect, and their difference. The expectation shift is descriptive; do not
label its ratio to the original effect as a causal fraction explained.

A locus is permutation-degenerate for this statistic if `D == 0`, or the
adjacent-product sum is invariant under every permitted permutation. Classify
this *exactly* from the permitted local permutations of distinct length values
for short interiors, or by an algebraic test of within-block swaps for longer
interiors. Report their count and retain them in the full denominator. If the
exact classification is not implemented and verified, report the narrower
count of constant-within-each-half loci and explicitly avoid asserting that
it captures all degenerate statistics.

## Controls, report, and interpretation

Use **999** trials, **0 through 998**, seed **20261011**, with the existing
SHA-256 counter and Fisher-Yates routines. Reuse the original compact length
corpus digest. Each block has a draw key obtained by SHA-256 of compact UTF-8
JSON with `ensure_ascii=False`, separators `(',', ':')`:

```
["sha256-counter-fisher-yates-v1", length_corpus_sha256,
 "locus-interior-half-blocks-v1", 20261011, trial,
 [page_id, locus_key, block_index]]
```

`block_index` is integer 0 for early and 1 for late. Identical numerical inputs
have identical controls, including IT's two spacing treatments. Save every
control mean `C_half`. Report the two-sided Monte Carlo tail
`(1 + count(abs(control) >= abs(observed) - 1e-12))/1000`, with the original
ZL split treatment primary and the other three dependent sensitivity checks.
Keep the earlier exploratory 0.01 convention without tuning. Disclose the
0.001 resolution floor and any contradictory direction or nonsmall tail.

Report the parent report hash, source and corpus pins, unchanged cohort hash,
interior/pair denominators, block-size distribution, constant and both-half-
constant counts, exact null expectations, all control arrays, and per-page
descriptive centered effects. Count pages as transcription IDs, not leaves.
For each treatment, require the original observed statistic and denominators
to match the parent report before running the new controls.

Before manuscript execution, test the expectation exhaustively over permitted
block permutations with distinct/repeated values and singleton blocks. Check
that an unpermutable interior yields a zero centered statistic, the split is
fixed for odd/even sizes, block multisets and endpoints are preserved, and the
parent-cohort checks fail on changed identifiers or source hashes. Replay the
complete report afterward. Keep the method and interpretation fixed on both
positive and negative results.

If a departure persists, state only that retaining each half's length
distribution does not remove it in this representation cohort. Remaining
explanations include finer interior position patterns, paragraph context,
copying, transcription conventions, and selection. A nonsmall tail limits the
original unconstrained conclusion; do not equate it with proof of randomness
or a successfully fitted gradient. New mechanisms still require explicit
rules, suitable language/synthetic controls, and prospective evaluation under
the [decipherment protocol](../DECIPHERMENT_PROTOCOL.md).
