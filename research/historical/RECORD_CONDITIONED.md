# Repeating types with native-record bags fixed

Question: how much do the historical global-null contrasts depend on pooling
tokens across native records, when input and measured edges are held fixed?

The [human plan](RECORD_CONDITIONED_PLAN.md) and [machine plan](record-conditioned-plan.json)
were committed before computing the new null. The [complete report](record-conditioned.json)
pins all dependencies and retains exact rational means, scope contributions,
input equality checks and all forty controls. It builds on the
[global assay](REPEATED_TYPES.md), whose observations were already exposed.
These approximate H streams remain unverified as the original authors' input.

## Matched observations and changed expectations

A counts overlapping equal adjacent-pair events; B counts distinct complete
types with at least one such event. The same four reconstructions, all retained
tokens and all N−1 flat-stream edges are measured, including native-record joins
and the singleton policy's normalized index-gap edges. Native records are not
established physical manuscript lines.

The conditional null independently shuffles each surviving native record's
complete token bag. Retained record lengths and position/provenance slots stay
fixed. The global null shuffles the complete text bag. Expected means below are
rounded for display; exact hexadecimal numerator/denominator records are retained.

| Ring treatment | f66r removed | N | A | Global E[A] | Conditional E[A] | B | Global E[B] | Conditional E[B] | B / conditional E[B] |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Omit R2 | M | 37,759 | 313 | 116.54 | 318.73 | 114 | 47.52 | 105.49 | 1.081 |
| Omit R2 | L | 37,776 | 314 | 116.56 | 319.73 | 115 | 47.56 | 106.49 | 1.080 |
| Remove ring singletons | M | 37,713 | 314 | 116.52 | 317.81 | 114 | 47.46 | 104.75 | 1.088 |
| Remove ring singletons | L | 37,730 | 315 | 116.53 | 318.81 | 115 | 47.50 | 105.75 | 1.087 |

With record bags fixed, B's exact mean rises by 57.29–58.93 types, leaving an
observed-minus-mean difference of 8.51 or 9.25. A's observed-minus-mean difference
changes sign: −5.73 or −3.81. The same fixed observations therefore give quite
different contrasts under the two declared nulls. This demonstrates sensitivity
to conditioning; it does not supply a causal allocation of the global contrast.

Conditional E[A] comprises 282.57 within-record plus 36.16/37.16 joining events
under R2 exclusion, or 281.68 plus 36.13/37.13 under singleton removal. Observed
within-record counts remain 304/305, while joining counts remain 9/10. Reporting
only within-record events would change the question and obscure those opposing
scope contrasts. B remains deduplicated across both scopes; their type counts
cannot simply be added. The original asterisk/boundary diagnostics remain identical.

All ten trials per variant are retained. Their B means are 107.1, 105.7, 103.9
and 105.9, and A means are 316.3, 314.3, 315.2 and 326.4 in table order. Trials
are keyed separately from the global controls; no common-random-number coupling
is claimed. Ten samples are descriptive, and no calibrated tail or significance
claim is computed. Exact conditional B variance is also absent.

## Exact mean on the complete edge path

The [plan](RECORD_CONDITIONED_PLAN.md) derives a per-type endpoint matrix for each
record: the joint probability of no internal self-repeat and specified first/
last occupancy. Transfer between consecutive nonempty records excludes a
type-equal joining edge. Summing the final states gives the probability of no
self-repeat anywhere in the measured text. Summing its complement by type gives
E[B] by linearity, without assuming types are independent.

Single-token records share their first/last position and have no internal edge.
Empty records add no position or edge and are skipped when finding the next
nonempty record. A nonempty record without the type resets the endpoint state;
sparse runs of records containing it can therefore be factored exactly. For A,
internal c(c−1)/m expectations and joining bag-overlap probabilities are summed
separately. No cyclic closing edge is added.

Fourteen focused tests pass. Before the source run, endpoint matrices were
checked against every occupancy subset for lengths 1–8, and whole-stream A/B
means against exhaustive independent permutations of eleven tiny-record cases.
Two further nontrivial separated-run cases were added afterward without changing
the metric implementation or results. The tests also verify single-record
reduction to the global formula, forced singleton joining, empty records,
case/relabel invariance, per-record bag preservation, deterministic replay,
source/global-input/observed-edge mismatches and protected-output failures.

The plan, core mathematical validation and guarded runner were committed
separately before the first manuscript measurement. All twelve frozen source/
global-study dependency pins remain unchanged. The runner requires the previous
global report's observed counts, boundary diagnostics, N, type count, variant
identity and both corpus hashes to match before computing the conditional mean.

## Reproduce

Python 3.10+, standard library only; recorded run used Python 3.14.3. From the
repository root at the reviewed study commit:

```sh
python3 scripts/historical_record_conditioned.py --output research/historical/record-conditioned.json
python3 scripts/historical_record_conditioned.py --check research/historical/record-conditioned.json
python3 -m unittest tests.test_record_conditioned_repeated_types tests.test_historical_record_conditioned -v
```

The complete report replays byte for byte. Source/plan/global-report drift fails
before reconstruction or measurement. Restore reviewed dependency versions when
needed; do not refresh frozen pins to make a changed checkout pass.

## Interpretation limits and next work

This matched comparison preserves input and edge population and changes the
null's conditioning. It allows record composition to remain while randomizing
order within records. It retains native-record order, finer position effects,
uncertain normalization, manually excluded material and the unresolved original
input identity. Any residual B contrast has no declared tail calibration here.

The [modern fixed-gap study](https://github.com/tobrien6/voynich-manuscript-research/pull/119)
uses different modern P0 inputs and eligible edges; it is not a matched replicate
of either historical assay. The four H variants share source material and are
not independent manuscript replications. Literal type identity does not resolve
glyphs or linguistic words. Neither null contrast identifies a language or
cipher, validates a decoding rule, or produces a translation.

Further position-conditioned controls or mechanism comparisons require a new
plan. Preserve this report, the global report, every variant and the prior
parsing/count/label discrepancies rather than tuning choices to remove or
amplify a contrast.
