# Native prefix comparison: row and opportunity weights

The accepted [twenty-seed census](SELF_CITATION_PREFIX_SEEDS.md) uses equal
native-row weights. Its complete results and selected raw rows were exposed
during review. This follow-up is an exploratory measurement-sensitivity audit,
not an untouched test, model intervention, manuscript comparison or decipherment.
Commit and publish this plan before computing the new weighted outcomes.

## Frozen family and inputs

Use only the accepted default census, SHA-256
`8a770fcd41340960b985e5e035c1b135f91137b2d0aa4acffdd6c075fc2d47a0`,
all seeds 1–20 and its eight first/last q/y cells stratified by the observed
model paragraph-initial Boolean. Read the already validated original/observed
native outputs and row ledgers, checking every frozen case fingerprint. Do not
execute a new generator, introduce ablated cases, change source/RNG/configuration,
select seeds, or compare these encoded flags with manuscript paragraph labels.

Preserve exactly the default eligibility: exclude initialization and native rows
with fewer than two space-delimited tokens. Verify each existing equal-row mean,
population, eligible denominator, boundary count and other-prefix rate before
using the case. If an input/case contract fails, reject the complete computation;
do not publish a result based on a substituted or silently reduced family.

## Two explicit estimands

For an eligible row with n tokens, let e be its boundary q/y indicator and k
the number of other tokens with that prefix. Its contrast is d = e − k/(n−1).
The accepted measure averages d with equal row weights.

The alternative uses weight w = n−1. It averages all boundary-versus-other-token
comparison opportunities: sum(w e − k) / sum(w). Thus the boundary indicator is
weighted too. It is not the unweighted boundary rate minus a separately pooled
other-token rate, or a replacement for the default measure.

For every seed/cell retain N, total opportunities, both component counts,
both exact contrasts, their difference, mean weight and the exact identity

    opportunity-weighted mean − equal-row mean = Cov(w, d) / mean(w)

where Cov uses population divisor N, not N−1. The same eligible rows contribute
to both measures. This decomposition is arithmetic, not causal attribution.

## All outcomes, validation and limits

Retain all 160 cells and every sign change or zero. Summarize each cell family
with equal weight across the twenty seed-specific means under both estimands;
report exact mean changes, sign counts and ranges. Do not pool seeds by their
number of rows/opportunities or select a success threshold after exposure.
There is no directional prediction or inferential pass/fail criterion.

Use exact rational arithmetic. Check the formulas independently by enumerating
boundary-versus-other-token pairs in bounded synthetic fixtures, including
unequal lengths with a sign reversal, constant weights and zero contrasts.
Separately reconstruct all real-input counts/means from the raw rows. Publish
original code, tests and token-free measurements; keep raw generated text,
source/classes/configuration/logs and ledgers local.

This audits a prerequisite for compatible mechanism comparisons: changing
weights changes what a descriptor averages. It does not identify manuscript
glyphs/words, authenticate a language, fit a generation mechanism, assign
calibrated seed probabilities, establish significance, decipher or translate.
