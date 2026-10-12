# Exact B spread on the historical full edge path

Question: how much can globally deduplicated repeating types B vary under the
accepted native-record bag null on the same four approximate H inputs?

The [plan](TYPE_VARIANCE_PLAN.md), [machine parameters](type-variance-plan.json),
synthetic mathematical validation and guarded producer were published at
[`77a9028`](https://github.com/tobrien6/voynich-manuscript-research/commit/77a9028)
before the first new manuscript variance calculation. All source, mean and
existing-control results were already exposed. This is a moment extension of
the [accepted conditional study](RECORD_CONDITIONED.md), not a new null, corpus
filter, untouched evaluation or original-author replication.

The [complete report](type-variance.json) preserves exact mean, marginal and
signed covariance contributions, variance, all four support/population ledgers,
fifty-digit scale diagnostics and every prior control's B value. All nineteen
frozen parent/source/method/report dependencies remain unchanged.

## Four retained outcomes

B counts distinct complete representation types having an equal adjacent pair
anywhere in the surviving flat stream. All N−1 edges, including native-record
joins and normalized index-gap edges, remain measured. Permutations are
independent within every retained native-record token bag. That is a stipulated
control model, not an assertion that physical manuscript lines are independent.

| Ring treatment | f66r removed | Observed B | Exact E[B], displayed | Var(B), displayed | Conditional SD | (B−E[B]) / SD |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Omit R2 | M | 114 | 105.494573 | 38.324132 | 6.190649 | 1.373915 |
| Omit R2 | L | 115 | 106.494573 | 38.324132 | 6.190649 | 1.373915 |
| Remove ring singletons | M | 114 | 104.754878 | 37.977597 | 6.162597 | 1.500199 |
| Remove ring singletons | L | 115 | 105.754878 | 37.977597 | 6.162597 | 1.500199 |

These are descriptive units of conditional spread. No Gaussian approximation,
confidence interval, decision threshold, p-value, calibrated tail or mechanism
probability is computed. An SD-scaled contrast is not a significance conclusion
and does not validate or reject a language/cipher explanation.

At each fixed ring treatment, M/L choices change observed B and E[B] by one,
while their exact variance and covariance totals are identical. The forced-type
count changes from one to two. This agrees with the singleton source contexts
in [the joining census](https://github.com/tobrien6/voynich-manuscript-research/pull/141),
without assigning physical or linguistic meanings to those native labels.

## Signed covariance and complete support accounting

Let Q_i be the probability of no self-repeat of type i and Q_ij the probability
of no self-repeat of either type i or j. Then `Cov(I_i,I_j)=Q_ij−Q_iQ_j`, and
the exact variance is `sum Q_i(1−Q_i) + 2 sum Cov(I_i,I_j)`. Type indicators are
globally deduplicated; they are not assumed independent, and per-record type
variances are not simply added.

| Ring treatment, both M/L | Marginal variance sum | Signed pair covariance sum | Twice-covariance adjustment | Positive / negative / zero shared-pair counts |
| --- | ---: | ---: | ---: | --- |
| Omit R2 | 38.246857 | +0.038638 | +0.077276 | 1,267 / 225 / 17,104 |
| Remove ring singletons | 37.904412 | +0.036593 | +0.073186 | 1,213 / 216 / 17,074 |

Both signs contribute to the retained exact net term. A small net adjustment
does not establish independence of every indicator. The report retains every
exact rational and the positive/negative/zero pair counts.

There are 354 variable indicators under R2 exclusion and 351 under singleton
removal. The respective 18,596/18,503 shared-record variable pairs are all
evaluated or assigned an exact inactive-component zero. Another 43,885/42,922
variable pairs have disjoint record domains and are exactly independent under
the declared bag model. All other literal types remain in the population
ledger: they have zero repeat probability or are forced repeats under this
particular null. Their omission from zero variance terms is not a corpus filter
or a claim that they cannot repeat under a different mechanism.

## Endpoint transfer and sparse factorization

The three endpoint categories are unmarked, target i and target j. An integer
record kernel counts categorical arrangements with neither ii nor jj internally,
retaining first and last categories. Unmarked adjacency and ij/ji are allowed.
All categorical placements have the same number of assignments of the original
other-type multiset. Division by the full categorical multiset denominator gives
the exact endpoint probabilities.

Joining transfer forbids only i/i and j/j between consecutive nonempty records.
Singletons share their first/last position. Empty records add no positions.
This keeps the same entire path as the accepted mean; resetting at every native
record would silently remove measured joining events.

Single-type no-event probabilities factor over contiguous native-record runs
containing that type. Overlapping i/j runs form bipartite components; components
with disjoint record domains are independent. The joint probability replaces
each interacting component's product of one-type probabilities by its joint
transfer probability, retaining exact ratio corrections. If one side of a
component has no possible repeat, its correction is exactly one. The mean and
all constant indicators remain checked against the parent report.

## Validation and reproduce

Fifteen focused tests pass. Endpoint matrices match 3,279 directly enumerated
three-category strings at lengths 1–7, spanning 119 count cases. Complete B
mean/variance matches exhaustive independent permutations of all 7,421 declared
tiny bag configurations (45,958 combined assignments), plus larger chained
overlap fixtures. Positive, negative, forced, inactive-shared and disjoint-domain
covariances, case/relabeling, typed/cache failures and Decimal underflow/constant
diagnostics are covered.

A separate bond inclusion-exclusion calculation, without the producer's state
recurrence, matches all 583 local matrix configurations covering every native
record/count pair in all four actual variants, including retained length 51.
The complete report replays byte for byte. The complete parent mean/control
report is also required to replay before any new variance calculation; all old
means, observations, corpus identities, diagnostics and forty controls remain
unchanged. No new random trials are generated.

One hundred fifteen temporary direct/symlink/hardlink alias cases cover every
protected dependency, parent, plan, runner and helper, before and during
computation. Failed checks preserve prior output and reject duplicate JSON keys
and scalar type changes. The producer rechecks protected paths immediately
before writing the serialized report.

Python 3.10+, standard library only; recorded run used Python 3.14.3:

```sh
python3 scripts/historical_type_variance.py --output research/historical/type-variance.json
python3 scripts/historical_type_variance.py --check research/historical/type-variance.json
python3 -m unittest tests.test_record_repeated_type_variance tests.test_historical_type_variance -v
```

Exact Fractions are retained as hex integers without changing Python's decimal
integer-string safety limit. SD/scaling uses 50-digit Decimal arithmetic and
keeps decimal strings; an optional binary-float underflow is absent rather than
misreported as exact zero. Zero variance gives an undefined SD-normalized contrast
and requires observed B to equal its constant expectation.

## Comparison limits and next work

The [modern fixed-gap variance study](https://github.com/tobrien6/voynich-manuscript-research/pull/144)
uses different P0 inputs and edge populations. Its numerical spread is not a
matched historical replicate. Here the four related, exposed H reconstructions
retain all source/parser/count/label discrepancies and unverified word/glyph or
physical-line interpretations. Source credit and publisher reuse terms remain
in the report.

This extension measures variation under one declared control, without a
language, cipher, historical-author input recovery, decipherment or translation.
Any tail calibration, finer position control or mechanism comparison needs a
separate plan; none follows automatically from these moment diagnostics.
