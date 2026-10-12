# Exact covariance of paired interior count policies

The three operational count-policy statistics are positively correlated under
their shared ideal occurrence permutations. ASCII/bench correlations are
**0.700–0.718**, ASCII/bench-plus-minim correlations **0.613–0.640**, and bench/
bench-plus-minim correlations **0.734–0.757** across all four source/spacing
variants and both scopes. Treating these controls as independent would omit
positive covariance and overstate the variance of their paired differences.

This is an exact conditional-control calculation on the accepted **2,165**
common P0 loci. It clarifies the existing [paired unit sensitivity](INTERIOR_UNITS.md)
and extends the [ASCII half-moment audit](HALF_MOMENTS.md). Every old observed
effect, control array and tail is unchanged. It neither selects a physical glyph
policy nor creates a Gaussian test, confidence interval or decipherment result.
The [complete report](interior_unit_covariance.json) retains all eight ensembles,
all locus matrices, 72 expanded aggregate entries and 16 paired-change records.

## Paired ensemble and exact calculation

The three accepted finite [count policies](../baselines/EVA_UNIT_PROTOCOL.md)
retain source case, original token boundaries and the same interior slots.
First/last original tokens stay outside the statistic. Within each locus, every
policy receives the **same** original occurrence permutation. Unrestricted
controls permute all interior slots; half controls independently permute the
ceil(m/2) early and remaining late slots, including their crossing pair.
Constants and exact invariant cases stay in the denominator. These are notation
counts, not adjudicated physical glyphs or linguistic words.

For paired interior vectors x,y, set d_i=m*x_i-sum(x) and e_i=m*y_i-sum(y).
Each association has its accepted fixed normalization and policy-specific null
centering. Calculate covariance from E[Q_d*Q_e]-E[Q_d]*E[Q_e], where each Q is
its sum of adjacent products. Centering by a fixed expectation leaves covariance
unchanged. Zero squared-deviation sums retain the accepted zero convention.

All ordered chain-edge pairs are included: identical edges, shared vertices,
disjoint edges and crossing-half combinations. Distinct positions in a block
receive distinct **paired** original occurrences (d_i,e_i), even for repeated
values. Bivariate power sums and set-partition inclusion-exclusion calculate
these moments exactly. A partition block of size b contributes
(-1)^(b-1)*(b-1)!; its product of summed power products gives the injective-
assignment numerator. Divide by the block falling factorial. Separate block
moments multiply under the half control. Degree at most four is required.

Every per-locus and aggregate 3x3 covariance matrix has exact symmetry,
nonnegative diagonals and all nonnegative principal minors. Under the explicitly
stipulated **independent-locus ideal permutation ensemble**, covariance of the
equal-locus mean is sum(locus covariances)/2165^2. This mathematical assumption
does not make manuscript loci, scans, source editions or policies independent
observations. The accepted hash-generated 999 controls are a separate fixed
finite empirical measure; their population covariance uses their own array means
and denominator 999.

## Complete ideal control scales and correlations

SDs below are approximations in normalized association units, not physical glyph
uncertainties or sampling errors for a randomly selected manuscript population.

| Source / spaces | Scope | ASCII SD | Bench SD | Bench/minim SD | ASCII–bench corr. | ASCII–minim corr. | Bench–minim corr. |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ZL3b / split | unrestricted | 0.007104405 | 0.007213184 | 0.007176236 | 0.717512 | 0.636404 | 0.751113 |
| ZL3b / split | half | 0.005827849 | 0.005898397 | 0.005881720 | 0.716304 | 0.639674 | 0.757124 |
| ZL3b / join | unrestricted | 0.007217450 | 0.007321983 | 0.007250297 | 0.703506 | 0.617985 | 0.737074 |
| ZL3b / join | half | 0.005884180 | 0.005955930 | 0.005933864 | 0.710857 | 0.621024 | 0.741434 |
| IT2a / split | unrestricted | 0.007136933 | 0.007262039 | 0.007227024 | 0.700446 | 0.613435 | 0.733612 |
| IT2a / split | half | 0.005868071 | 0.005920103 | 0.005918448 | 0.700662 | 0.617564 | 0.738271 |
| IT2a / join | unrestricted | 0.007136933 | 0.007262039 | 0.007227024 | 0.700446 | 0.613435 | 0.733612 |
| IT2a / join | half | 0.005868071 | 0.005920103 | 0.005918448 | 0.700662 | 0.617564 | 0.738271 |

All **8,660** ASCII half per-locus means/variances and all four aggregate
variances match the accepted independent moment audit exactly. For the mapped
half statistics, exact zero-variance identifiers equal their accepted swap
invariance classifications:

| Source / spaces | ASCII | Bench | Bench/minim |
| --- | ---: | ---: | ---: |
| ZL3b / split | 55 | 63 | 66 |
| ZL3b / join | 73 | 80 | 88 |
| IT2a / split | 58 | 72 | 71 |
| IT2a / join | 58 | 72 | 71 |

These counts include nonconstant invariant rows. No zero is dropped, and changes
in constant/invariant status under grouping remain explicit. IT split/join
vectors and results coincide; related treatments are not independent replications.

## Paired-change variation and retained tails

For grouped-minus-ASCII, exact ideal variance is
V_grouped+V_ASCII-2*Cov(grouped,ASCII). The observed-change/ideal-SD ratio is a
scale diagnostic only. It supplies no Gaussian probability, new tail, threshold
or decision rule. The finite/ideal SD ratio describes the unchanged control
arrays; it neither certifies uniform hash draws nor gives an uncertainty interval
for that ratio. All 16 such ratios lie between **0.97969 and 1.02817**.

| Source / spaces | Scope | Change | Observed change | Ideal paired SD | Observed / SD | Finite / ideal SD | Retained paired tail |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| ZL3b / split | unrestricted | Bench − ASCII | -0.025720663 | 0.005381843 | -4.779155 | 0.989863 | 0.001 |
| ZL3b / split | unrestricted | Bench/minim − ASCII | +0.003880374 | 0.006089294 | +0.637245 | 0.979690 | 0.525 |
| ZL3b / split | half | Bench − ASCII | -0.020970683 | 0.004416902 | -4.747826 | 0.997984 | 0.001 |
| ZL3b / split | half | Bench/minim − ASCII | -0.001876804 | 0.004970434 | -0.377594 | 1.028171 | 0.702 |
| ZL3b / join | unrestricted | Bench − ASCII | -0.023595819 | 0.005598930 | -4.214344 | 1.012648 | 0.001 |
| ZL3b / join | unrestricted | Bench/minim − ASCII | +0.005477256 | 0.006323110 | +0.866228 | 1.018726 | 0.396 |
| ZL3b / join | half | Bench − ASCII | -0.018302143 | 0.004502403 | -4.064972 | 0.998571 | 0.001 |
| ZL3b / join | half | Bench/minim − ASCII | +0.000123395 | 0.005144615 | +0.023985 | 1.010970 | 0.981 |
| IT2a / split | unrestricted | Bench − ASCII | -0.029901004 | 0.005573744 | -5.364617 | 1.010819 | 0.001 |
| IT2a / split | unrestricted | Bench/minim − ASCII | +0.005443668 | 0.006315474 | +0.861957 | 0.997429 | 0.390 |
| IT2a / split | half | Bench − ASCII | -0.025129236 | 0.004560751 | -5.509890 | 1.022891 | 0.001 |
| IT2a / split | half | Bench/minim − ASCII | -0.001734992 | 0.005154266 | -0.336613 | 1.010154 | 0.735 |
| IT2a / join | unrestricted | Bench − ASCII | -0.029901004 | 0.005573744 | -5.364617 | 1.010819 | 0.001 |
| IT2a / join | unrestricted | Bench/minim − ASCII | +0.005443668 | 0.006315474 | +0.861957 | 0.997429 | 0.390 |
| IT2a / join | half | Bench − ASCII | -0.025129236 | 0.004560751 | -5.509890 | 1.022891 | 0.001 |
| IT2a / join | half | Bench/minim − ASCII | -0.001734992 | 0.005154266 | -0.336613 | 1.010154 | 0.735 |

Bench changes remain negative with retained tails 0.001. Bench/minim changes have
nonsmall retained tails; their half change is positive for ZL join and negative
elsewhere. Similar scalar effects do not imply identical controls or equivalent
glyph maps. The exact joint variation and every sign exception remain recorded.
No old Monte Carlo array or probability is replaced by an analytic tail.

## Publication and verification

The [plan](INTERIOR_COVARIANCE_PLAN.md) was pushed and remote-verified at
`651877c4c35cc0110322caef47861bf263b73372`. The synthetic-tested producer/kernel
and [20-entry manifest](interior-covariance-pins.json) were pushed and remote-
verified at `1905ed3ee20180bdd8a31d6e7cf7913a60844681` **before** new corpus joint
moments. The accepted unit report differs from the original contribution only
in its corrected producer fingerprint; all scientific fields/arrays match.

- Driver SHA-256: `d744ec07d1c71d053810d069d6dac164a43bf4708102d4e2459fec41d500dd41`.
- Kernel SHA-256: `026f64ca8d40c266723569e431a396480ebe9fcc54de1f1ab8030fb9b63b5690`.
- Manifest SHA-256: `0dfd611f66f54be079ff4eb0069b2ff943e05b4de655de7a88d8b75d529782c9`.
- Report SHA-256: `b90b8811672192bc578695c0e5e9b4d003488c27e6100a214af21a19d886fef6`.

Before measurement, **92** relevant tests passed, including 15 new kernel/driver
regressions. They compare signed block products with explicit injective assignments,
all 729 length-three trinary vector pairs under both scopes with complete
occurrence permutations, larger shared/disjoint/crossing fixtures, affine and
constant cases, covariance symmetry/PSD, equal-locus weights, finite population
covariance, invalid families/inputs, zero-variance states, large serialization,
pin failures and direct/symlink/hardlink aliases introduced during calculation
or serialization. No global integer-string or ambient Decimal setting changes.

A separately written [checker](../../scripts/verify_interior_covariance.py)
reconstructs all 12 literal count vectors, then uses an injective subset dynamic
program and direct ordered edge-pair enumeration. It calls no production moment,
partition, signature or covariance function. It verifies **103,920** unique
per-locus covariance entries, all raw null means, **72** expanded aggregate entries,
all 16 paired variances/effects, zero-variance identifiers and complete descriptive
finite-control summaries. Three additional checker regressions bring the relevant
test total to **95**. Complete saved-report replay matches every field.

The report stores per-locus fractions as pairs of decimal integer strings and
six upper-triangle entries in declared index order; symmetry restores the full
3x3 matrix without dropping entries. Large aggregate fractions use labelled
base-16 integer strings with a separately rounded 60-significant-digit decimal.
These formats preserve exact arithmetic, including a tested 9,001-digit integer,
without changing interpreter limits or ambient rounding contexts.

For the recorded Python 3.14.3 runtime, standard library only:

```sh
python3 scripts/interior_unit_covariance.py \
  --check research/transliteration/interior_unit_covariance.json
python3 scripts/verify_interior_covariance.py
python3 -m unittest tests.test_paired_interior_moments \
  tests.test_interior_unit_covariance tests.test_independent_interior_covariance
```

Use `--new-report PATH_TO_NEW_REPORT.json` for a new exclusive output. Frozen
source/report/helper identities are validated before calculation; complete
serialization finishes before the final output-alias guard. Native source/code/
settings/plan/report inputs and optional check-file aliases stay protected.
Existing destinations are refused. No raw manuscript tokens/images, third-party
generator payloads or private local paths are included in this supplement.

## Limits and next question

The ensemble conditions on mapped interior count vectors and original slots.
It does not model glyph-reading error, manuscript population uncertainty, source
selection, physical line correspondence, or a causal text-production process.
All material and maps were previously exposed. Correlated operational policies
remain sensitivity views, not replicated linguistic evidence or a preferred map.

Future mechanism comparisons can use these exact paired scales while retaining
physical unit ambiguity, prospective predictions and exposure-valid source-linked
readings. A stronger effect or a large scale ratio alone cannot support decoding
or translation.
