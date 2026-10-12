# Synthetic greedy-wrapping control protocol

Recorded 2026-10-12 before computing this synthetic sweep. The experiment is
motivated by the exposed [locus-initial length result](../baselines/LOCUS_POSITION_RESULTS.md).
It is an exploratory control construction, not a registered manuscript
decipherment hypothesis or an untouched test.

## Question and complete mechanism

Can one explicitly defined layout process produce a nonzero initial-minus-rest
length contrast when the incoming token lengths are independent and identically
distributed and no position-dependent encoding is applied?

An abstract integer is a token's width in **synthetic units**, not an EVA glyph
count or manuscript pixel width. For each declared law, incoming lengths are
uniform over its listed support. A row starts with one token and no leading
separator. Each later token consumes its width plus one separator unit. Append
it if the new total is at most the row capacity, including equality. Otherwise
close the current row and carry that *same* token unchanged to the next row.
Never split a token, redraw a rejected token, pad a row, add a prefix, or justify
spacing. Reject a token wider than the capacity. Reject analysis settings whose
capacity is less than twice the maximum length plus the separator: every
overflow-closed row must have at least two tokens.

The [parameters](parameters.json) fix two laws and five cases:

| Law | Uniform support | Capacities | Separator width |
| --- | --- | --- | --- |
| two-length | 2, 3 | 7, 8 | 1 |
| five-length | 2, 3, 4, 5, 6 | 18, 24, 30 | 1 |

The two-length cases are analytically derived checks, not blind predictions:
capacity 7 always closes two-token rows and has zero expected contrast. At
capacity 8, finite path enumeration gives row-start transition probabilities
`[[3/8, 5/8], [1/2, 1/2]]`, stationary start probabilities `[4/9, 5/9]`,
conditional mean contrasts `[-1/2, +1/2]`, and an equal-row mean of **1/18**.
Check these exact values rather than tuning them to a simulation. Report the
entire five-length sweep even if it is zero or has the opposite sign.

## Exact calculation and finite simulation

For each possible first length, enumerate bounded row-occupancy/token-count
states until an incoming token overflows. That determines the next row's first
length and the current row's contrast. Keep exact rational transition
probabilities and expected rewards, solve the finite stationary distribution,
and verify row sums, nonnegativity, normalization and stationarity exactly.
Publish every kernel, first-length conditional reward and stationary probability,
not only the final contrast. Use an independent recursive path enumeration of
the two-length finite case as an implementation check.

Generate exactly 100,000 lengths per law with the shared `HashDraws`/
`uniform_index` helper. The fixed seed and serialized context are in the JSON;
use the zero-based token index as the helper's replicate argument. Reuse the
same stream across capacities of the same law. Retain its full digest and
length frequencies, so it can be regenerated. This deterministic sampled
stream approximates the ideal IID model; an exact stationary result is not a
claim that a finite seeded stream is already stationary.

Retain all rows closed by overflow, including the first completed row. Exclude
the final row not closed by overflow **even if it happens to fill the capacity**;
record its lengths and counts. No outcome-dependent burn-in is allowed. The
finite run contains an initial transient, so report its discrepancy from the
asymptotic prediction descriptively without a fitted tolerance or confidence
claim.

For the same incoming stream, also divide into fixed token-count chunks of
3, 4 and 5. Retain complete chunks and record any trailing remainder. Every
fixed-count chunk has exact IID expected contrast zero. These controls have
different row occupancy; no matched manuscript geometry is asserted.

## Measurement, conditioning and reporting

The primary score is first length minus the mean of other lengths in a complete
row, averaged with **one equal vote per row**. Publish row counts, token-count
distribution, retained token counts and length frequencies, first-length
frequencies, and observed contrast. Rows are not weighted by their token count.
Only rows with at least two tokens can be scored.

For each finite row collection, report the shared baseline helper's exact
conditional standard deviation for uniformly choosing a first token inside
each fixed row. Its equal-row expected contrast is exactly zero. This conditions
on existing row bags and chooses positions independently; it is a different
process from generating a token stream and carrying overflows across rows.
Do not interpret this conditional variance as the sampling variance of the
greedy-wrapping simulation or use it for a generative significance test.

Keep all five cases, all fixed-count controls, exact fractions, finite outcomes,
implementation and parameter fingerprints, and the simulation/exact
discrepancies. A nonzero case is a counterexample to treating within-row
exchangeability as every possible text-production model; it does not explain
the manuscript's actual writing system. Zero and contrary cases are equally
part of the result.

## Source context and limits

[Reddy and Knight (2011)](https://aclanthology.org/W11-1511/), section 6.2 and
Figure 7, compare line-edge character distributions with within-line word
shuffles. This toy uses an explicitly specified length/layout process; it does
not reproduce their corpus, statistic, or numerical result.

No manuscript strings, natural-language text, fitted token law, observed line
capacity, drawing geometry, prefix rule, glyph adjudication, or claimed
translation enters this model. A real layout test would require reviewed
physical-line/image alignment and a predeclared width/spacing model tested on
material excluded from fitting. Existing manuscript loci cannot automatically
be treated as these synthetic rows. The toy establishes only what its own
declared mechanism produces.
