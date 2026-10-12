# Exact joint moments of paired interior count policies: exploratory plan v1

Publish this plan and the synthetic-tested implementation before any new
manuscript covariance calculation. Extend the accepted
[unit sensitivity](INTERIOR_UNITS.md), PR #116, and
[half-control moments](HALF_MOMENTS.md), PR #121, on their unchanged **2,165**
common conservative P0 loci, four source/spacing treatments and three finite
EVA count policies. Sources, mappings, all effects and 999-control arrays are
already exposed. This is a mathematical sensitivity audit, not untouched
prediction, physical glyph adjudication or a decipherment candidate.

## Question and immutable inputs

How strongly do the three count-policy statistics co-vary under their shared
original token-index permutations, and what exact null variation does this give
the already observed paired policy changes?

Pin the accepted unit report to SHA-256
`1d7264718b561e13cc8c43d9f361a9b1503f2692837db6a15bdc3377ae8da097`
and the accepted half-moment report to
`7f9548f4c8a8cc7fb980ed5cf12051b7f6feef9db1cc0881accedac54efb4b1c`.
The unit report differs from the original contribution only in its corrected
producer fingerprint; complete scientific fields and arrays are unchanged.
Also pin the original full/half reports, unit settings, source catalog, native
reader/adapter, segmentation/math helpers and this plan. Reconstruct every
source/count vector, exact parent cohort/exclusion rule, token count/audit,
vector fingerprint and reported observation before computing joint moments.
No native sources, count maps, endpoints, seeds, trials or old tails are altered.

Within a single source/spacing treatment, every policy uses the **same** original
occurrence permutation. Grouping occurs inside a token before permutation and
does not change original interior positions. Half controls independently shuffle
occurrences within the same ceil(m/2) early/late slots and retain the crossing
pair. Constant and invariant cases remain in the shared denominator. Do not
claim cross-source matched permutations or independent transcription evidence.

## Exact ideal ensemble and bivariate kernel

For interior count vectors x and y of equal size m>=3, use the accepted scaled
deviations d_i=m*x_i-sum(x), e_i=m*y_i-sum(y), squared sums and normalized adjacent
associations. Center each policy by its own exact unrestricted/half expectation;
constant counts give zero. Centering changes means but not covariance.

Compute E[Q_d], E[Q_e] and E[Q_d*Q_e], where Q is the sum over adjacent interior
products. Sum over all ordered pairs of chain edges, combining d/e factors at
shared positions. This includes identical, shared-vertex, disjoint and crossing-
half edge pairs. Distinct positions in each permutation block receive distinct
original occurrences, preserving the paired (d_i,e_i) values. Early/late block
independence permits multiplication of block moments.

The production kernel will use bivariate power sums and inclusion-exclusion
over set partitions of at most four labelled positions. A partition block of
size b contributes (-1)^(b-1)*(b-1)! times the corresponding summed power product.
Summing partition products gives the injective-assignment numerator; divide by
the block's falling factorial. This differs from the accepted univariate subset
implementation. All arithmetic is integer/Fraction; no Monte Carlo estimate or
Gaussian approximation enters the exact covariance.

Normalize Cov(Q_d,Q_e) by the two fixed association scales. Record all three-
policy per-locus covariance matrices under unrestricted and half scopes. Check
symmetry, nonnegative diagonals and positive semidefiniteness exactly, including
all principal minors. Affine-equivalent normalized statistics and invariant/
constant rows can produce zero paired variance; retain these cases explicitly.

Under the **stipulated independent-locus ideal permutation ensemble**, covariance
of equal-locus mean statistics is sum(locus covariances)/2165^2. This mathematical
independence does not make manuscript loci, folios, scans, editions or count
policies independent observations. Hash-generated controls are a separate
fixed deterministic finite empirical measure, not the ideal uniform ensemble.

## Reporting family and paired changes

For all four source/spacing treatments and both scopes, retain complete exact
3x3 ideal covariance matrices, diagonal variances, approximate standard
deviations/correlations and every per-locus matrix. Do not filter off-diagonal
signs or degenerate cases. The accepted ASCII half variance and every one of
its **8,660** per-locus records must equal PR #121 exactly; zero-variance
identifiers must agree with the accepted invariance audit for each mapped policy.

For bench-minus-ASCII and bench/minim-minus-ASCII, calculate exact ideal variance
V_grouped+V_ascii-2*Cov(grouped,ASCII), including every zero contribution and the
full denominator. Preserve the original observed differences and 999-control
paired tails. Record approximate observed-difference / ideal-SD ratios when
variance is positive, and explicitly distinguish zero-variance/zero-difference
from zero-variance/nonzero-difference cases. These ratios are scale diagnostics,
not z-test p-values, confidence levels, Gaussian tails or a new decision rule.

Descriptively compute each complete existing 999-array population covariance,
correlation and paired-difference variance with its original denominator and
finite-array mean. Compare its spread to the exact ideal scale, retaining all
cases whatever the agreement. Never add draws, select trials or replace the
accepted arrays/tails. IT's identical spacing treatments remain separately
reported but dependent. No numerical compatibility threshold is introduced.

Exact per-locus fractions use decimal strings where small; potentially large
aggregate fractions use explicitly labelled base-16 integer strings, with
separate approximate display values. Do not change global integer-string or
ambient Decimal settings merely to serialize a large aggregate.

## Verification and publication

Before manuscript calculation, verify signed bivariate block moments against
explicit injective assignments and joint covariances against complete occurrence
permutations on small vectors under both scopes. Include shared/disjoint/crossing
edges, repeated/constant values, affine transformations, symmetry/PSD, differing
mapped constant status, zero paired variance, equal-locus denominators, invalid
inputs, exact serialization under altered ambient contexts, complete policy/
source families, changed pins and input/output aliases. Publish the tested
kernel and source reconstruction before measuring new corpus moments.

After generation, independently reconstruct all selected count vectors and
covariances with a separate subset-of-labelled-positions injective dynamic
program and independent edge-pair enumeration, without production moment,
partition/signature or covariance functions. Check all per-locus and aggregate
entries, paired variances, observed effects and descriptive finite-control
summaries. Reproduce the complete saved report from pinned inputs. No new
permutation arrays or raw third-party source/image payloads are published.

Protect all pinned native sources, code, reports, settings, plan and optional
check file before calculation and after complete serialization, immediately
before exclusive output creation. Inspect exact outgoing files, metadata and
staged diffs for secrets/private data. Keep all accepted results and timestamps
intact, and submit the supplement through a focused contributor PR.

This audit clarifies the variation of paired operational count changes under
an explicit conditional ensemble. It does not choose a physical glyph policy,
isolate a text-production mechanism, calibrate a decipherment claim or supply
an exposure-valid evaluation/translation. Future mechanism comparisons still
require comparable units, prospective predictions and source-linked readings.
