# Independent positional means can preserve an interior-order departure

The fixed size-eight counterexample has mutually independent counts, yet its
expected accepted half-centered association is **+0.22840579**. The early,
crossing and late components are **+0.06526130**, **+0.09788318**, and
**+0.06526130**. All 256 equally likely outcomes have a positive half-centered
total. The process has slot-specific population covariance **zero** between
all distinct positions, including neighbors.

The [derivation](PROOF.md) explains the difference: independence does not imply
exchangeability when count distributions vary by position. The accepted statistic
centers each realized interior by its pooled mean and uses a conditional uniform
position-permutation reference. It does not subtract the process's different
slot means. This constructed counterexample limits a direct-neighbor interpretation
of the [existing half result](../../transliteration/INTERIOR_HALVES.md), including
positive contributions inside both halves. It supplies no empirical fit, line
geometry, physical glyph policy, language or decipherment.

## Fixed processes and complete enumeration

For each interior size 3 through 10, enumerate every vector of independent fair
Bernoulli bits B_i, with probability 2^-m, then add a known offset:

| Family | Count at slot i (zero based) | Conditional order property |
| --- | --- | --- |
| Flat | 2+B_i | Identical laws at all slots; whole/half order exchangeable |
| Half-step | 2+3*1[i>=ceil(m/2)]+B_i | Identical laws inside each half |
| Increasing | 2+i+B_i | Slot law varies within each half |
| Decreasing | 2+(m-1-i)+B_i | Slot law varies within each half |

The base, step, gradient, noise and sizes were fixed in the [settings](settings.json)
before process enumeration. The minimum is the accepted score domain; the maximum
bounds exact computation. Primary size eight gives four positions per half and
within-half edges that can vary. No parameter or noise level was fitted to native
text. These are invented positive counts; they are not glyph/image widths and
no endpoint token or row-wrapping process is modeled.

The complete [lossless report](results.json.gz) contains all **32** process
ensembles and **8,160** exact outcome records, including every zero/negative
score, constant and short-half component. The declared outcome columns preserve
the complete bit vector, raw/full/half totals and three half components; settings
recover every invented count vector. Every outcome has its exact process weight.
Both occurrence-permutation centering scopes include all interior adjacent edges.
Every component uses the same whole-locus normalization, rather than a separate
correlation or division by its edge count.

## Full and half ensemble means

All flat full/half means are exactly zero. All half-step half means, including
all three half components, are exactly zero. Full half-step and both gradient
means are positive throughout the bounded size family. Increasing and decreasing
families have exactly equal distributions under a bit-complement affine relation,
including odd splits; neither count direction is selected after inspection.

| Interior size | Flat full / half | Half-step full | Half-step half | Gradient full | Gradient half |
| --- | --- | ---: | ---: | ---: | ---: |
| 3 | 0 / 0 | +0.22939560 | 0 | +0.36607143 | +0.27455357 |
| 4 | 0 / 0 | +0.61334423 | 0 | +0.56806716 | +0.17030745 |
| 5 | 0 / 0 | +0.64566171 | 0 | +0.67735239 | +0.24437784 |
| 6 | 0 / 0 | +0.72948149 | 0 | +0.74462484 | +0.21271110 |
| 7 | 0 / 0 | +0.74405264 | 0 | +0.78991277 | +0.24353883 |
| 8 | 0 / 0 | +0.77854894 | 0 | +0.82227295 | +0.22840579 |
| 9 | 0 / 0 | +0.78719744 | 0 | +0.84642718 | +0.24485781 |
| 10 | 0 / 0 | +0.80566434 | 0 | +0.86507335 | +0.23592904 |

The gradient column applies to each of the two direction families. Exact fractions
and every component mean are retained in the report. For sizes three/four, both
within-half centered components are identically zero because neither block has
more than two positions. At size five only the early block has more than two.
These cases remain in the tables and receipts; the primary prediction concerns
size eight with positive early and late ensemble contributions.

At the primary size, the complete half-total sign counts are:

| Family | Negative | Zero | Positive | Exact half ensemble mean |
| --- | ---: | ---: | ---: | --- |
| Flat | 122 | 4 | 130 | 0 |
| Half-step | 123 | 4 | 129 | 0 |
| Increasing | 0 | 0 | 256 | +0.22840579 (rounded) |
| Decreasing | 0 | 0 | 256 | +0.22840579 (rounded) |

The flat family includes two constant outcomes among its 256 cases. A zero
ensemble mean does not require every realized score to be zero, or equal counts
of positive and negative scores. These are exact probabilities/counts under the
specified invented law, not manuscript significance levels or a calibrated
permutation tail. The half-step calibration shows what the coarse block control
removes in this particular independent process; the finer gradient survives it.

## Publication and verification

The [plan](PLAN.md) and settings were pushed and remote-verified at
`2c0c6637dce199691829824d0873adcdbb73b687`. The synthetic-tested producer was
pushed and remote-verified at `be428b1f16982591479a9488c1d36775ee1f878c` before
any declared process ensemble enumeration. **32 relevant tests** passed at that
point, including thirteen new local mathematical/reference/writer tests. Expected
zero cases and an intentionally positive counterexample were specified in advance;
this is a check of a constructed process, not blind discovery.

Three subsequent independent-oracle tests bring the relevant total to **35**.
Local score and expectation tests compare the pinned accepted full/half methods
and complete small occurrence permutations, including constants, repeated values,
singleton late components and positive/negative affine transformations. Other
checks cover family/count/noise/size guards, generic slot-centered covariance,
strict primary failures, frozen plan/settings and historical-reference drift,
initial/late aliases, exclusive creation, scalar-type byte drift and lossless
compression. A 9,001-digit aggregate encodes exactly without changing interpreter
or Decimal settings.

The [independent checker](../../../scripts/verify_independent_position_length.py)
uses integer bit masks, rational pooled deviations and direct sums over distinct
ordered occurrences. It computes population covariance from deviations about
separate slot means, rather than the producer's raw-second-moment subtraction.
It imports no production family, score, expectation or aggregation function.
Its complete typed reconstruction matches all **48,960** retained outcome score
values, all **480** aggregate component values, **1,520** count-covariance entries,
**2,040** directional outcome pairs, all weights/sign masses/constant counts,
known-zero checks and fixed primary predictions. Complete producer byte replay
also agrees. Neither producer nor checker reads manuscript tokens or images.

- Producer SHA-256: `990e121599596901f76a830895fa9339abfb49d0658fd8d992bb523f679a94f1`.
- Decompressed report SHA-256: `1fccb1fcbee481bd8f7aa80cef9d0e18d4ae5a39195b1c002438e6a424ee6250`.
- Gzip SHA-256: `f5fc77de97d32a8ab58550072eb793a0af705db903ce6251f38c5761a980a3e1`.

The 183,553-byte gzip preserves every byte of the 3,632,130-byte JSON; its mtime
is zero and no filename is embedded. Aggregate fractions use labelled base-16
integers plus a separate approximate float. Bounded outcome fractions use decimal
numerator/denominator pairs. The report binds historical accepted score definitions
at `45582ca72353d0c1edb78610f811ba50a78712c4`; those source blobs are hashed but
not executed by the standalone producer/checker. Local reference tests verify
current definition identities before importing their score functions.

For the recorded Python 3.14.3 runtime, standard library and the recorded Git
history only:

```sh
python3 scripts/independent_position_length.py \
  --check research/baselines/independent-position-length/results.json.gz
python3 scripts/verify_independent_position_length.py
python3 -m unittest tests.test_independent_position_length \
  tests.test_independent_position_oracle
```

Use `--new-report NEW_PATH.json` or `NEW_PATH.json.gz` for an exclusive output;
the latter uses deterministic lossless compression. Existing destinations are
refused before calculation, and input/source/code protection is rechecked after
complete serialization. The report contains only invented outcomes, derived
numbers and public reference fingerprints, with no private local path or native
source/image/generator payload.

## Interpretation and next test

The explicit factorized law proves independence; the zero covariance matrix is
an additional consistency receipt. A departure from a uniform conditional order
reference can reflect changing slot distributions, even where counts are mutually
independent. The [IID greedy-wrapping theorem](../../line-wrap/interior/PROOF.md)
retains its different assumptions and zero conditional interior expectation.
This counterexample neither contradicts that theorem nor models manuscript layout.

The size-eight gradient effect is larger than the observed manuscript effect.
No matching of magnitude, distribution, eligibility or exposure-valid predictions
was attempted. The example demonstrates an alternative class of explanations,
without adopting a fitted gradient or excluding actual dependence/copying. A
later manuscript position model needs justified features, predeclared training
exclusions, predictive evaluation and conditional controls with useful variation.
Physical row/glyph mapping and source uncertainty remain unresolved. No language,
plaintext, decipherment or translation follows from these constructed scores.
