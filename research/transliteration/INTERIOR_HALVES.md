# Interior order with early/late position constraints

Preserving each locus's early and late interior length distributions reduces
the original order departure, but does not remove it in any of the four
ZL3b/IT2a spacing treatments. In the primary ZL split treatment, the centered
association changes from **0.089062** under unrestricted interior permutations
to **0.067330** under independent within-half permutations. This limits one
coarse positional explanation; finer gradients and other production or
transcription mechanisms remain possible.

## Scope and chronology

This is a sensitivity follow-up to [the interior-order exploration](INTERIOR_ORDER.md)
in [PR #38](https://github.com/tobrien6/voynich-manuscript-research/pull/38).
The parent result and full corpus were already inspected. The
[new plan](INTERIOR_HALVES_PLAN.md) was committed at
`20ae3e9` and its synthetic-verified implementation at `bfcbea4` before executing
the new manuscript controls. No fitted model, unseen evaluation set,
independent replication, decipherment, or translation is claimed.

The exact pinned parent report has SHA-256
`d3ada06de64c80f315ea6fa38f71f25158857cdf0d2a34728d1c6fc6ad7b6a6c`.
The program recreates its 2,165-locus cohort and all four length-corpus hashes,
checks source identities and original observations, and then runs the new
controls. The cohort, whole-locus ambiguity exclusions, drawing exclusions,
minimum five-token rule, ASCII Eva representation, and equal locus weights
are unchanged. Its 176 transcription page IDs remain distinct from a count
of physical leaves or independently aligned image regions.

## Method

Fix the first and last token and use only the original interior adjacent
pairs. Split an interior of size `m` after `ceil(m/2)` positions. Permute the
early and late blocks independently, preserving each half's complete length
multiset, mean, variance, and number of positions. The crossing pair is still
included, and nothing moves between halves, loci, pages, or folio sides.

The observed uncentered normalized adjacent-product statistic `R` is identical
to the parent analysis. Its null expectation changes with the permitted
permutations. The new centered statistic is `R - E_half[R]`, averaged equally
over the same loci. The plan derives `E_half[R]` from exact rational block
moments, including the crossing pair and singleton halves. Constants contribute
zero and remain in the denominator. This is a conditional sensitivity test,
not a fitted position model.

## Observations

| Treatment | Observed mean `R` | Unrestricted null mean | Half-constrained null mean | Original centered effect | Half-centered effect | Two-sided tail |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ZL3b split, primary | -0.100892 | -0.189954 | -0.168221 | 0.089062 | **0.067330** | 0.001 |
| ZL3b join | -0.156255 | -0.212929 | -0.201047 | 0.056674 | **0.044792** | 0.001 |
| IT2a split | -0.114311 | -0.193425 | -0.176690 | 0.079114 | **0.062378** | 0.001 |
| IT2a join | -0.114311 | -0.193425 | -0.176690 | 0.079114 | **0.062378** | 0.001 |

In each treatment, zero of the 999 controls have an absolute half-centered
statistic as large as the observed one. The inclusive Monte Carlo tail is
0.001, its resolution floor, not zero or an estimate of the exact tail below
that floor. All directions remain positive relative to their null expectations;
the raw uncentered associations remain negative. The primary result meets
the fixed exploratory 0.01 convention. IT's two spacing treatments produce
identical length inputs and controls and count as one dependent comparison.

The null expectation shifts upward by 0.021732 in ZL split, 0.011882 in ZL
join, and 0.016736 in IT. These shifts describe the change in the permitted
permutation set on the observed multiset. They are not causal fractions
explained by a gradient and do not validate a fitted text-production mechanism.

The four treatments retain, respectively, 15,878 / 13,713, 14,437 / 12,272,
and twice 15,558 / 13,393 interior tokens / adjacent pairs. There are 41,
54, and twice 45 loci with a constant length within each half. They remain
in the full denominator and cannot change under the control. This is a
**narrow count**, not a complete classification of permutation-degenerate
statistics: for example, the interior `[1, 3, 2]` has a nonconstant early
half but the same adjacent-product statistic under both permitted orders.
The original fully constant-interior counts remain 13, 13, 14, and 14.

The [separate exact invariance diagnostic](HALF_DEGENERACY.md) identifies 55,
73, 58, and 58 loci whose statistic cannot vary under any permitted half
permutation, including the narrower counts above. It preserves the full
2,165-locus denominator and changes no accepted statistic, control or tail.

The [complete report](interior_half_controls.json) retains the parent/source/plan
pins, unchanged cohort, each treatment's block-size distribution, all 999
control statistics, exact expectations, control means and deviations, and
descriptive per-page effects. No page subset was selected after inspection.
Source Currier labels remain source annotations rather than inferred languages.

## Reproduce and validate

From the repository root, using Python's standard library:

```sh
python3 -m unittest discover -s tests -p 'test_interior_half_controls.py' -v
python3 scripts/interior_half_controls.py --check research/transliteration/interior_half_controls.json
```

The full replay takes several minutes. Exact exhaustive tests cover permitted
block permutations with distinct/repeated values, singleton halves, constant
interiors, and other invariant statistics. Tests also check odd/even splits,
block-multiset preservation, unchanged inputs/endpoints, deterministic controls,
equal locus weights, full denominators, parent identity/source/length/statistic
guards, all-trial tail accounting, and protection against overwriting the
parent report or source data. Controls use the
[existing SHA-256 counter algorithm](../token-controls/README.md), with separate
block keys and the fixed seed/trials specified in the plan.

## Limits and next test

The early/late multiset constraint accounts for coarse positional differences,
while leaving finer within-half position patterns exchangeable. The surviving
departure therefore does not establish direct neighbor dependence. Paragraph
context, copying, transcription conventions, uncertainty treatment, clear-locus
selection, and representation-unit choices also remain possible explanations.
The exposed paired sources provide sensitivity evidence, not independent
manuscript validation or out-of-sample prediction.

The [fixed independent-position counterexample](../baselines/independent-position-length/RESULTS.md)
supplies a concrete finer-position alternative: independent counts with a linear
slot mean have positive half-centered ensemble association, including early/late
components. Flat and half-step controls retain their exact zero expectations.
These invented laws are not fitted manuscript explanations or glyph/line models.

A further experiment should register a justified finer position model and
its controls before execution, with enough permissible variation to assess
its power. An explicit language or cipher mechanism additionally needs
documented reference and synthetic-encoding comparisons and prospective
evaluation under the [decipherment protocol](../DECIPHERMENT_PROTOCOL.md).
Do not promote a sequence of exploratory control rejections into a validated
reading of the manuscript.

## Exact variance supplement

The [exact-moment audit](HALF_MOMENTS.md) supplies ideal occurrence-permutation
variances on this unchanged cohort, reproduces every accepted invariant
identifier, and compares the existing finite-control SD with its ideal ensemble
scale. All controls, effects and recorded tails in this study remain unchanged.
