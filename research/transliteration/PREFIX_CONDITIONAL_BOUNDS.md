# Conditional upper bounds for literal prefix contrasts

The [conservative common-cohort report](CONSERVATIVE_PREFIXES.md) retains only
199 shuffled assignments per contrast. Its Monte Carlo tail estimates therefore
have a 0.005 floor. This follow-up calculates conservative analytic upper bounds
for the same 96 binary-prefix contrasts. It changes no source, cohort, feature,
boundary, or conditional control. The [calculation plan](PREFIX_BOUND_PLAN.md)
was committed before this run; the prefix observations were already exposed.

## Inputs and conditional assumptions

Recompute from the pinned ZL3b/IT2a bytes through `plain-eva-v1`, using the exact
same 2,907 shared locations under both spacing policies. Check the selected-key
digest, source hashes, family identities, boundary denominators, and agreement
with the preceding report's means and exact conditional standard deviations.
The [JSON report](prefix_conditional_bounds.json) records its predecessor's byte
hash, exact rational moments, and all 96 comparisons, including loose bounds.

The ideal control assigns tokens uniformly within each locus, independently
across loci, conditional on its token multiset. Paragraph/Currier annotations
and the fixed cohort are conditioned on. This is a stipulated randomization
model: independence of actual manuscript loci is not established. The source
versions and split/join policies are also not independent manuscript samples.

## Derivation and numeric treatment

For one literal prefix, a locus has `m >= 2` tokens, `k` positive indicators,
and observed boundary indicator `x`. The existing boundary-minus-other-token
contrast is `D = (m*x - k)/(m - 1)`. A uniformly assigned boundary is positive
with probability `k/m`. Thus `E[D] = 0`, `|D| <= 1`, and
`Var(D) = k*(m-k)/(m-1)^2`. For `T = sum(D)` and `V = sum(Var(D))`, applying
the bounded-variable Bernstein inequality to each sign and adding the two
one-sided bounds gives

```text
P_control(|sum(D)| >= |T_observed|)
  <= min(1, 2*exp(-T_observed^2/(2*V + 2*abs(T_observed)/3))).
```

The [Stanford CS229T problem set, Question 12(c)](https://web.stanford.edu/class/cs229t/2017/problems.pdf)
states the one-sided inequality for independent, centered, bounded variables.
The binary moments and conversion from that inequality to this two-sided
sum bound are derived above. These are upper bounds, not exact tail
probabilities or Monte Carlo estimates.

Compute `T`, `V`, and the positive exponent as exact fractions. For decimal
evaluation, round the positive exponent downward at 60-digit precision,
evaluate its negative exponential, move to the next larger representable
decimal, and multiply with upward rounding. Python documents correctly rounded
[`Decimal.exp`](https://docs.python.org/3.14/library/decimal.html#decimal.Decimal.exp)
and [`next_plus`](https://docs.python.org/3.14/library/decimal.html#decimal.Decimal.next_plus).
This keeps reported bounds above the ideal expression, with positive decimal
strings instead of float underflow to zero. A zero observed contrast has bound
one; an empty cohort remains nonestimable and still belongs to the family.

The family-adjusted bound is `min(1, 96*upper)`. This Bonferroni/union-bound
adjustment permits dependence among the comparisons when their marginal
conditional models are valid. The family includes both sources, both spacing
policies, all three source labels including unset, both paragraph states,
both boundaries, and both prefixes. It accounts for this family only; other
exploration and model selection in the project are not accounted for.

## Observations

The primary split-policy first-boundary contrasts are reproduced below. The
two bound columns are **family-adjusted upper bounds**, displayed rounded
upward to four significant figures; use the complete decimal strings in JSON
for numerical decisions. A value of one is a loose bound, not evidence for
exchangeability or absence of an effect.

| Source | L label | Paragraph start | Loci | q contrast | y contrast | q bound | y bound |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| ZL3b | A | no | 929 | +0.06105 | +0.13004 | 2.918e-4 | 6.121e-26 |
| ZL3b | A | yes | 142 | -0.06718 | -0.03309 | 1 | 1 |
| ZL3b | B | no | 1,477 | -0.03524 | +0.14441 | 1 | 1.060e-67 |
| ZL3b | B | yes | 334 | -0.18035 | -0.00698 | 1.492e-8 | 1 |
| ZL3b | unset | no | 17 | -0.03207 | +0.10194 | 1 | 1 |
| ZL3b | unset | yes | 8 | -0.06409 | -0.11952 | 1 | 1 |
| IT2a | A | no | 927 | +0.06059 | +0.12802 | 4.306e-4 | 1.044e-24 |
| IT2a | A | yes | 144 | -0.06887 | -0.03402 | 1 | 1 |
| IT2a | B | no | 1,475 | -0.03585 | +0.14673 | 9.786e-1 | 3.390e-69 |
| IT2a | B | yes | 336 | -0.18495 | -0.00815 | 5.353e-9 | 1 |
| IT2a | unset | no | 17 | -0.03700 | +0.10126 | 1 | 1 |
| IT2a | unset | yes | 8 | -0.06584 | -0.12175 | 1 | 1 |

All 96 cases are estimable. Family-adjusted bounds below 0.05 occur in 6/24
ZL3b split, 8/24 ZL3b join, and 6/24 in each IT2a policy: 26/96 dependent
comparisons, not 26 independent findings. IT2a split/join values coincide on
these inputs. Several effects have small analytic bounds beyond the Monte
Carlo resolution; others remain loose or change their bound substantially
with spacing treatment. No effect sizes or directions have changed.

## Reproduction and limits

```sh
python3 scripts/prefix_conditional_bounds.py --output research/transliteration/prefix_conditional_bounds.json
python3 scripts/prefix_conditional_bounds.py --check research/transliteration/prefix_conditional_bounds.json
PYTHONPATH=tests python3 -m unittest test_prefix_conditional_bounds test_conservative_prefixes test_prefix_strata test_locus_positions -v
```

Tests compare exact binary moments and joint tails against exhaustively
enumerated small independent permutation spaces, check the variance addition
assumption, verify outward rounding against a higher-precision evaluation,
and exercise bounds far below ordinary float range. Full-data replay checks
the accepted cohort and preceding report before generating any bounds.

A small bound constrains the stated ideal exchangeability model. It does
not select a language, glyph mapping, cipher, or translation, and does not
repair annotation error, tokenization assumptions, source dependence, or
prior exposure. A large bound does not establish the null. The next
decipherment step remains a candidate-specific prediction with checked glyph
units, a disclosed exposure history, and a separately validated evaluation split.
