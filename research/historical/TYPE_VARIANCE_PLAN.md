# Historical native-record B variance plan, version 1

Question: what is the exact variance of globally deduplicated repeating types B
under the accepted historical native-record bag null on the identical four
approximate H streams and all N−1 measured edges?

Commit this plan and synthetic mathematical validation before measuring the
new manuscript variances. The source/parser/global/conditional mean studies,
all forty existing controls, joining census results and figure are already
exposed. This is an exploratory moment extension of the fixed null, not an
untouched evaluation, original-author replication or registered decoding test.

## Unchanged input, units and null

Freeze all effective dependencies of the accepted
[conditional study](RECORD_CONDITIONED.md), its unchanged original plans,
explicit safety amendment, mathematical helper, producer and complete report.
Reconstruct all four variants unchanged; require exact parent report replay,
observed B, source/corpus identities, all within/join diagnostics and old means.
Retain all asterisks, empty/excluded records and normalized index gaps as the
parent does. No new permutation samples or variant selection are introduced.

B counts each complete representation type once if it has an equal adjacent
pair anywhere in the entire surviving flat stream. Native-record joining edges
remain scored. Conditional permutations are independent within each retained
native record's bag; those model assumptions do not establish physical-line or
manuscript sampling independence. A and all existing controls remain unchanged.

## Exact type indicators and joint endpoint transfer

Let Q_i be the probability that type i has no repeat anywhere under this null.
Reuse the accepted one-type endpoint/run probabilities and check that
sum_i(1−Q_i) equals the parent's exact E[B]. For two distinct types, compute
Q_ij, the probability of no self-repeat of either. Then:

```text
Cov(I_i,I_j) = Q_ij − Q_i Q_j
Var(B) = sum_i Q_i(1−Q_i) + 2 sum_{i<j} (Q_ij − Q_i Q_j)
```

The two-type record kernel has three endpoint categories: unmarked, type i,
type j. Count all categorical multiset arrangements with neither ii nor jj
internally, retaining their first/last category. Unmarked adjacency and ij/ji
are allowed. Divide endpoint counts by C(m,c_i)C(m−c_i,c_j). Other literal types
collapse to unmarked only for these two event indicators; all category placements
have the same number of assignments of the original other-type bag.

Propagate endpoint probabilities across consecutive nonempty records, rejecting
only an i/i or j/j joining edge. Initialize the previous endpoint as unmarked.
Singleton first/last endpoints share one position; empty records add no position
and are skipped. This kernel must preserve boundary state rather than resetting
at every record or copying a within-locus-only no-event probability.

## Exact sparse covariance calculation

Type i's event depends only on permutations of records containing i. Types with
disjoint record domains therefore have zero covariance under the stipulated
independent bag model. Indicators with Q=0 or Q=1 are constant and have zero
variance/covariance. Their exact contributions to E[B] and population counts
remain retained; excluding their zero variance terms is not a corpus filter.

For variable indicators, enumerate every type pair sharing a record. Each type's
single-type no-event probability factors over consecutive nonempty-record runs
containing it. Overlapping i/j runs form connected bipartite components; disjoint
run components are independent. Replace each overlapping component's product of
one-type no-event probabilities by its joint endpoint-transfer probability.
Multiplying these exact ratio corrections by Q_iQ_j gives Q_ij. Denominators
are nonzero because the pair indicators are variable. If either type's runs in
a component all have Q=1, the correction is exactly one and no joint kernel is
needed there. Validate this factorization against full-stream enumeration.

Retain signed covariance sums, twice-covariance adjustment, marginal variance,
their exact total, all type/population/support counts, candidate/positive/negative/
zero-covariance pair counts and mean agreement. Use exact Fractions and existing
hex integer serialization without changing Python's integer-string safety limit.

## Diagnostics, validation and limits

Report variance, SD and observed-minus-exact-mean in conditional SD units. These
are descriptive scale diagnostics: no normal approximation, confidence interval,
p-value, calibrated tail, decision threshold or mechanism probability is declared.
Use 50-digit Decimal arithmetic for square roots/scaling and retain decimal
strings. Optional binary floats must not turn positive underflow into an exact
zero. Zero variance gives undefined SD-normalized contrast; observed B must then
equal its constant expectation.

Before source measurement, enumerate small three-category strings to verify
every endpoint count, and exhaustively combine tiny record-bag permutations to
verify global B mean, variance and covariance accounting. Include positive and
negative covariance, shared but inactive runs, chained overlapping components,
disjoint supports, forced/singleton/empty cases, case/relabeling invariance,
invalid typed counts, underflow diagnostics, parent/dependency/input mismatches
and protected direct/symlink/hardlink output aliases before/during computation.

The [modern fixed-gap variance work](https://github.com/tobrien6/voynich-manuscript-research/pull/144)
is related background on deduplicated finite-bag indicators, with different
inputs/edges and no native-record joining state. This extension retains the
historical path and existing mean/control results. No decoded word/glyph identity,
language, cipher, physical-line interpretation, decipherment or translation is
established by the new moment or its standardized contrast.
