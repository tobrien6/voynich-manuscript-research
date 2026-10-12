# Independent position-dependent counts: synthetic plan v1

Publish this plan, fixed settings and synthetic-tested implementation before
enumerating the new process ensembles. Existing manuscript order effects,
half controls and component decomposition have been inspected. This is a
constructed counterexample/calibration, not a manuscript fit or untouched test.

## Question and fixed processes

Can mutually independent integer counts with position-dependent means have a
positive expected accepted full/half-centered interior association, including
positive early/late components under the half control?

For interior sizes m=3 through 10, enumerate all 2^m vectors of independent fair
Bernoulli bits B_i. The lower bound is the accepted statistic's domain; the upper
bound limits exact enumeration, not a fitted corpus coverage target. Position
indices start at zero, k=ceil(m/2), and no endpoint token enters the calculation.
Use the following four fixed families, retaining every outcome at weight 2^-m:

- Flat: X_i=2+B_i.
- Half-step: X_i=2+3*1[i>=k]+B_i.
- Increasing: X_i=2+i+B_i.
- Decreasing: X_i=2+(m-1-i)+B_i.

All counts are positive, and each slot has two possible values. The complete
joint law factorizes by construction; do not infer independence merely from
zero pairwise covariance. Verify each mean and the complete population count
covariance matrix (diagonal 1/4, off-diagonal zero) as a separate receipt.
The differing positional means are part of the specified process, rather than
parameters estimated from a realized vector. No sampling, random seed, native
transcription, manuscript image or generator output is used.

## Accepted scores, components and predictions

For each outcome let d_i=m*X_i-sum(X), D=sum(d_i^2), and
R=m*sum(d_i*d_(i+1))/((m-1)*D) when D>0; retain the accepted zero convention for
constant vectors. Full centering subtracts -1/(m-1) for nonconstant interiors.
Half centering subtracts the exact expectation under independent permutations
of the two observed half bags, including their crossing pair. It is not the
expectation under the new position-dependent process.

Partition the adjacent products into early, single crossing, and late edges.
Use the original whole-interior normalization on every component. Calculate
their raw/unrestricted/half expectations and centered values exactly; the three
components must add to the accepted total for each outcome. These definitions
follow the accepted full/half methods and the pending component supplement,
but require no unaccepted implementation or result dependency.

Known zero predictions: the flat family has ensemble mean zero under both
centerings. The half-step family has half-centered ensemble mean zero, because
its distributions are identical within each half. Their complete conditional
within-half ordering likelihoods are invariant; constants remain included.

The fixed primary counterexample is size m=8: predict strictly positive half-
centered ensemble means for the increasing and decreasing families, with
strictly positive early and late components as well. If any prediction fails,
retain the failure without changing the slope, noise, sizes, family or criterion.
For all other sizes record the complete signed values without additional pass
thresholds. This is a planned check of an intentionally constructed mechanism,
not a blind discovery or a claim about the manuscript's data-generating process.

For every size, decreasing outcome B has the same scores as increasing outcome
1-B, by the positive-count affine relation X_decreasing(B)=m+4-X_increasing(1-B).
Check this exact reversal-of-gradient symmetry, including odd splits. It does
not permute half membership and supplies no inference about writing direction.

## Complete report and verification

Retain all 8,160 outcome records across the four families/sizes. Each outcome
records its complete bit vector and exact raw/full/half totals plus all three
half-centered components; fixed settings recover its invented counts uniquely.
Declare column order explicitly. Record all exact ensemble component means,
population count means/covariances, constant counts, positive/zero/negative total
outcome masses, known-zero checks, symmetry checks and the fixed primary outcome.
Do not omit zero or negative cases or assign a probability to a manuscript tail.

Freeze plan/settings/reference identities and code before ensemble execution.
Beforehand, test local score formulas against complete occurrence permutations
on small synthetic vectors, the pinned accepted full/half functions, constants,
singleton late components, affine transformations, invalid sizes/counts/families,
exact serialization, pin drift and initial/late output aliases. Local mathematical
fixtures are permitted; do not run the declared process ensembles before freeze.

After generation, independently reconstruct all outcomes using integer bit masks
and a separate rational-centered direct-edge/ordered-pair calculation. Verify
every outcome score, weight, component, population covariance, aggregate and
declared pass/failure. The checker may use standard library fractions and frozen
settings but no production family, score, expectation or aggregation function.
Reproduce the complete report byte for byte.

Use exact fraction pairs for bounded outcome values and labelled base-16 integers
for aggregates. Do not change global integer-string or Decimal settings. Protect
plan/settings/code/reference inputs before calculation and again after complete
serialization; use exclusive creation and refuse existing destinations. Inspect
exact outgoing artifacts and public commit metadata for sensitive data. Submit
a focused contributor PR; upstream decisions stay with assigned maintainers.

## Interpretation and next test

The accepted IID greedy-wrapping theorem relies on exchangeable interior order
under its specified conditioning. These independent nonidentical slot laws
need not satisfy that condition. A positive score here would demonstrate that
independence alone does not imply zero under a position-permutation reference.
Sample-centered adjacency and position-conditioned population covariance are
different quantities.

No finite tail, glyph map, copying mechanism, physical line model, language,
decipherment or translation is calibrated or adopted. A future manuscript model
needs justified positional features, registered training exclusions and prediction
evaluation, and useful conditional variation. The present process is a known
synthetic counterexample, not an explanation fitted to exposed manuscript rows.
