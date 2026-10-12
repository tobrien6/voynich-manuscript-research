# Interior adjacent-edge components: exploratory plan v1

Publish this plan and the synthetic-tested implementation before calculating
new component measurements. The parent corpus, order effects, half controls,
count-policy sensitivity and covariance have already been inspected. This is
bookkeeping of previously exposed statistics, not an untouched prediction,
another rejection test, a physical-line assertion or a decipherment candidate.

## Question and complete family

How much of the accepted centered interior association lies in edges entirely
inside the early half, in the single edge crossing the early/late boundary,
and in edges entirely inside the late half? How does the change from unrestricted
to half centering distribute across those same three components?

Use all 2,165 accepted common conservative P0 loci, all four ZL3b/IT2a split/join
treatments, and all three accepted operational ASCII/bench/bench-plus-minim
counts. Preserve every constant, invariant, singleton-half and zero-component
case in the full equal-locus denominator. IT split/join remain dependent views.
No source, map, original token slot, cohort, normalization or old control changes.

Pin the accepted unit report (SHA-256
`1d7264718b561e13cc8c43d9f361a9b1503f2692837db6a15bdc3377ae8da097`)
and joint report (`b90b8811672192bc578695c0e5e9b4d003488c27e6100a214af21a19d886fef6`),
plus their required reports, settings, catalog, native reader, segmentation,
reconstruction and formatting helpers. Freeze a manifest including this plan.
Reconstruct the complete original eligibility ledger and all 12 vector/audit
fingerprints before measuring components. Do not use a moving PR dependency.

## Exact decomposition

For interior vector x of size m>=3, let d_i=m*x_i-sum(x), D=sum(d_i^2),
k=ceil(m/2), early=d[:k] and late=d[k:]. The accepted normalization is
A=m/((m-1)*D) when D>0. A=0 is the accepted constant-vector convention.

Define three adjacent-product sums:

- Q_early=sum(d_i*d_(i+1), i=0..k-2),
- Q_bridge=d_(k-1)*d_k,
- Q_late=sum(d_i*d_(i+1), i=k..m-2).

Their raw association contributions are A times each sum, and add exactly to
the accepted raw association. Their edge counts are k-1, 1 and m-k-1, including
zero late edges for m=3. These are artificial position partitions of encoded
interior slots; the bridge is not an observed paragraph or manuscript boundary.

Under unrestricted occurrence permutations every edge has expected product
-D/(m*(m-1)). Multiply by each component's edge count and A.

Under independent half occurrence permutations, write S_b=sum(d_i in b) and
T_b=sum(d_i^2 in b). Expected product sums are
(S_early^2-T_early)/k,
S_early*S_late/(k*(m-k)), and
(S_late^2-T_late)/(m-k), respectively. The within-block formula includes its
number of edges; for a singleton its numerator is zero. Multiply by A.

For each scope subtract these exact component expectations from the same raw
components. The three centered contributions sum to the accepted centered
association at every locus and under equal-locus averaging. The expectation
shift from unrestricted to half centering is componentwise arithmetic, not a
causal proportion explained by position or a fitted gradient.

## Reporting and checks

Retain each locus's identity, slot/edge counts, and all three exact raw,
unrestricted-expected and half-expected contributions for all policies. Record
aggregate exact raw/expected/centered triplets and centering shifts for all
12 treatments. Record grouped-minus-ASCII centered component differences for
both grouped policies and both scopes. Complete signed values are retained;
no contribution is selected by its sign or size. All three contributions use
the original whole-locus normalization and denominator, rather than separate
edgewise correlations or normalization by each component's number of edges.

Reassemble per-locus raw/null values exactly against the accepted full/half
formulas and all 51,960 accepted per-locus covariance-report null means.
Reassemble all 24 exact aggregate centered effects against the accepted joint
report and approximately against the unit report (tolerance 1e-12). Verify both
grouped-minus-ASCII totals and the full-to-half centering shifts. Retain old
total tails as attributed parent facts, without new component probabilities,
thresholds, Gaussian approximations, ratios of causal explanation or decisions.
Do not generate or rerun permutation draws, fit a model or execute a generator.

Before corpus measurement, use complete small occurrence permutations under
both scopes, including repeated values, constants, odd/even splits and singleton
halves, to check each component expectation. Test exact additivity, shift signs,
policy differences, equal-locus weights, malformed counts, complete families,
serialization without global settings changes, pin failures and output aliases.

After generation, a separate checker reconstructs every count vector with a
literal scanner and computes expected edge products directly from distinct
ordered occurrence pairs. It must call no production component, centering or
aggregation function. Check every locus component and all aggregate/policy
differences, then reproduce the complete saved report from frozen inputs.
Store exact small fractions as decimal pairs and large aggregate fractions with
explicit base-16 integer strings, without changing interpreter/Decimal settings.

Protect native source files, code, settings, plans and all accepted reports before
calculation and again after complete serialization immediately before exclusive
output creation. Inspect outgoing artifacts and metadata for secrets/private
data. Publish no raw third-party source/image payload or private local path.
Submit through a focused contributor PR; upstream disposition stays with the
assigned maintainers.

This decomposition can locate an existing encoded order effect and expose the
role of the included bridge. It cannot distinguish direct neighbor dependence
from finer positional structure, transcription conventions or another production
process. Operational count maps, physical-unit correspondence, exposure-valid
mechanism predictions and source-linked readings remain unresolved.
