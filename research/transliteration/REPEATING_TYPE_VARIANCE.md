# Conditional spread of the distinct repeating-type count

The primary ZL split/exclude result has **exact conditional variance 33.4164**
and **SD 5.7807**. Its 103 observed repeating representations, against mean
93.9073, are 1.573 conditional SD above that mean. This adds spread to the
[accepted type-count description](REPEATING_TYPES.md), with every original
count, mean, policy and slot digest preserved. SD scaling is descriptive;
no normal tail, confidence interval, mechanism probability or decipherment
follows from this result.

## Fixed scope and chronology

The [plan](REPEATING_TYPE_VARIANCE_PLAN.md) was committed at `a7a0f46` before
new manuscript variance calculations. Implementation and 30 passing targeted
tests were committed at `b9e1068` before the first variance run. Source text,
earlier pair/distance results and repeating-type counts/means were already
exposed. These local chronology records establish no independent preregistration
or untouched evaluation.

Use the same **3,884 shared present P0 loci**, native source byte pins and all
eight source/uncertainty policies. The producer completely rebuilds and verifies
the accepted mean report before calculating variance. It preserves whole-locus
bags and fixed excluded slots; tokens can move between retained runs of the
same locus. No source, mean report, earlier producer, plan or shuffle is changed.

## Joint no-event probabilities and signed covariance

For representation `t`, let `J_t` indicate that it has no immediate self-repeat
anywhere in the cohort, and set `I_t=1-J_t`. Its global no-event probability
`Q_t` is already supplied by the accepted locus-product calculation. Then:

```text
Var(I_t) = Q_t(1-Q_t)
Cov(I_a,I_b) = Q_ab - Q_a Q_b
Var(sum_t I_t) = sum_t Q_t(1-Q_t) + 2 sum_(a<b) Cov(I_a,I_b)
```

For two distinct representations in one locus, mark their occurrences A/B;
the remaining retained positions are unmarked. An integer transfer counter
tracks both marked counts and the previous position's marked color. Forbid
AA and BB, leave unmarked adjacency unrestricted, and reset previous-color
state at a fixed gap. Counts remain cumulative across retained runs, so the
method includes allocation of marked positions between runs.

Divide the valid marked placements by `C(m,c_a) C(m-c_a,c_b)`. Every placement
has the same number of assignments of the other token representations, so
this is the joint no-repeat probability under the original multiset shuffle.
Multiply it across independently permuted loci to obtain `Q_ab`.

Pairs with no shared locus where both can repeat have zero covariance under
this control. Exact forced-repeat indicators have zero variance/covariance
and retain their count/mean contributions. For the remaining pairs, start
from the product of global marginal no-event probabilities and correct the
local factors in shared repetition-opportunity loci. All arithmetic remains
rational. The report records marginal variance, signed covariance adjustment
and the complete total variance, with pair-accounting counts.

Global deduplication prevents summing per-locus type variances. Two synthetic
`a a b` loci have type-count variance **8/81**, rather than the sum of their
separate 2/9 variances. Covariance also need not be positive: a full `a a b b`
path gives type-pair covariance **1/12**, while the fixed-gap slots
`[a,a,null,b,null,b]` give **-1/36**. Both cases remain in validation.

## Results on the accepted cohort

[The complete report](repeating_type_variance.json) retains every policy and
exact fraction. IT2a's full policy results are identical apart from labels,
verified before collapsing this table.

| Source / spaces / alternatives | Observed types | Mean | Exact variance, decimal display | Conditional SD | Centered count / SD | Shared variable type pairs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ZL / split / exclude | 103 | 93.9073 | 33.4164 | 5.7807 | 1.5730 | 158 |
| ZL / split / first | 104 | 94.8820 | 33.4225 | 5.7812 | 1.5772 | 161 |
| ZL / join / exclude | 97 | 84.7705 | 30.7209 | 5.5426 | 2.2064 | 103 |
| ZL / join / first | 98 | 85.9505 | 31.1778 | 5.5837 | 2.1580 | 104 |
| IT / all policies | 106 | 93.3767 | 33.5127 | 5.7890 | 2.1806 | 142 |

All actual shared-pair covariances are positive, and no actual indicator is
forced. Those are observations of this cohort, not assumptions in the method.
The primary covariance adjustment is approximately 0.0673 added to the sum
of marginal indicator variances. Keeping signed terms is necessary for the
general fixed-gap control, as the negative synthetic cases demonstrate.
Joining uncertain spaces changes the descriptive contrast appreciably. The
dependent policies and source editions are not independent replications.

## Reproduce and validate

Python 3.10 or later, standard library only; recorded Python 3.14.3. Obtain
the [pinned sources](DECISION.md) and run:

```sh
PYTHONPATH=tests python3 -m unittest \
  test_repeating_type_variance test_repeating_types \
  test_repetition_moments test_token_baselines
python3 scripts/repeating_type_variance.py \
  --check research/transliteration/repeating_type_variance.json
python3 scripts/repeating_type_variance.py --output /tmp/repeating-type-variance.json
```

Seven new test methods cover 255 original retention layouts, 21,845 direct
three-color assignments and 2,816 marked-count cases; exhaustive independent
locus permutations; global deduplication; signed and forced-indicator cases;
and all 64 masks of a double-occurrence bag against the accepted pair moments.
Complete synthetic-source CLI tests protect copied mean/plan/code/raw inputs,
reject a changed parent mean and typed variance cache, and replay both policies.
The parent and accepted moment/tokenizer suites bring the targeted total to 30.

A separate original-coordinate recursive counter, without retained-component
convolution or ratio corrections, verifies every actual variant's global
no-event mean, marginal variance, covariance sum and total variance exactly.
It directly multiplies joint probabilities over the union of each pair's
repetition-opportunity loci, using 262 distinct mask/marked-count configurations.
All prior variant fields and earlier report/producer bytes remain unchanged.

Exact fractions use the parent's large-integer-safe text representation. SD
and standardized contrasts are decimal approximations at 50 digits under an
explicit local context; no decimal rounding enters variance itself. A synthetic
3,884-locus case has positive exact variance below binary floating range but
a representable positive SD. Tests retain that distinction and also verify
decimal diagnostics when SD or contrast is outside binary floating range.
Corresponding float fields are null, and exact-zero flags use rational values.

Check mode compares the entire typed report after complete parent replay.
Source/catalog, parent mean/plan/engine, new plan/engine and preprocessed-slot
fingerprints are retained. Output guards run before calculation and before
writing, protecting the parent inputs, accepted mean, new plan and producer.
The committed result contains no native token strings or pair identities.

## Interpretation and next test

The independent-locus permutation is a conditional reference distribution,
without establishing physical-line, manuscript or sampling independence.
Counts compare preserved representations; glyph readings and word boundaries
remain unadjudicated. Correlation between type indicators is now accounted for,
but these two moments do not determine a tail probability or confidence level.

A future distribution or generator comparison must match the same statistic,
input, gaps and control, disclose prior exposure, and keep failed predictions.
The historical paper's whole-text normalization remains a separate question.
No language, cipher, copying mechanism, decoding or translation is identified.
