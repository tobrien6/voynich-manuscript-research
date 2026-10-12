# Conditional interior order under IID greedy wrapping — protocol

This is an analytical follow-up to the accepted synthetic greedy-wrapping
control (PR #82) and the accepted full/half interior-order definitions. The
first-slot and manuscript interior outcomes are already known. The proposed
claim and verification fixtures below are known mathematical calibrations,
not blind predictions or a manuscript evaluation. No certificate calculations
have run. This protocol derives symmetry from the specified wrapping process
rather than assuming a permutation null or comparing a copying generator.

## Claim and assumptions

Take a finite-support IID law on positive integer widths, with positive rational
probabilities summing to one. Use a fixed nonnegative integer separator and a
fixed integer capacity at least the largest width. Append when the new occupied
width is at most capacity; close only on overflow and carry that same failed
token as the next first token. Do not redraw, reorder while wrapping, split
tokens or include a final row not closed by overflow, even when it exactly fills
capacity. No stationary start distribution or independence between rows is
assumed.

For a fixed generated row with at least two distinct token positions, condition
on its first width a, last width z and interior
multiset M, and optionally its next carried width b. Singleton rows are outside
this theorem: first and last would be the same occurrence. Row selection must
be invariant under the interior permutations being considered; our score rule
selects only overflow-closed rows with at least five tokens. Choosing rows
by an interior-order statistic adds unsupported conditioning. Require positive probability
for the conditioning event. With k interior tokens, total occupancy is
T = a + z + sum(M) + separator * (k + 1). Every interior ordering that has this
bag has the same IID product weight. Positive widths/nonnegative separators
make T <= capacity sufficient for every partial prefix to fit. Closing depends
only on T and b: T + separator + b > capacity. After summing over b, each unique
ordering has weight p(z) * product(p(x), x in M) * P(X + separator > capacity-T).
This is an unnormalized row-event weight conditional on the first width, not a
probability of an order conditional on endpoints, bag and completion. Divide by
the sum of these weights over distinct orders for that conditional probability.
Repeated values change the number of distinct orders, not their relative weights.

Thus interiors are uniform conditional on these quantities. Conditioning further
on fixed early/late bags gives uniform independent *permutation choices* within
those blocks; it does not assert independent manuscript rows. Permuting only
completed-row interiors in a finite input stream preserves its row boundaries,
carryovers, endpoints, completed-row count and unclosed final tail.

## Statistics and inclusion

Use the accepted interior definitions only on rows with at least five tokens
(at least three interior widths). Constants remain zero contributions. Report
the full centered normalized adjacent-product score and the half-centered score
with the early half of size ceil(k/2), including the crossing pair. Their exact
conditional means are zero under the stated IID model. An individual order or
finite realized stream need not have score zero. Do not report an unscorable or
zero-probability conditioning event as a successful zero result.

No law, capacity, row inclusion rule or statistic is fitted to manuscript data.
This theorem concerns the stipulated synthetic mechanism and synthetic width
units. Source-native loci are not certified physical lines; ASCII notation
lengths are not image widths or manuscript glyph counts.

## Fixed bounded certificates

Freeze these before enumeration; keep every attempt and explicit failure status.
The uniform five-width law is exactly {2,3,4,5,6}, separator 1. All listed
capacity cases come from the accepted parent unless marked fixture.

1. Capacity 18, endpoints 2/2, interior bag [2,2,3]: three distinct orders,
   selective overflow, repeated values and a nonzero individual centered score.
2. Capacity 24, endpoints 2/2, interior bag [2,3,4,5]: 24 orders and an even
   interior/half split.
3. Capacity 30, endpoints 2/2, interior bag [2,3,4,5,6]: 120 orders, an exactly
   full row, and an odd interior/half split.
4. Capacity 18, endpoints 2/2, interior bag [3,3,3]: a constant interior.
5. Unequal-law fixture: support [2,3,4,5] with probabilities [1/2,1/4,1/8,1/8],
   capacity 24, endpoints 2/2, interior bag [2,3,4,5]. This is an implementation
   check, not a sixth parent sweep case or a fitted distribution.
6. Accepted two-width law {2,3}, capacity 8, endpoints 2/3, empty interior:
   a positive-probability completed row excluded from the interior statistic.
7. Uniform five-width law, capacity 30, endpoints 2/2, interior [2,2,2]: it
   fits but has no possible closing overflow. Conditional mean is undefined.
8. Uniform five-width law, capacity 18, endpoints 3/6, interior [5,5,5]: it
   exceeds capacity. Conditional mean is undefined.

For each valid class, retain every unique ordered interior, exact per-order
probability, occupied width, allowed/disallowed overflow values and exact scores.
Also group by the two half bags and verify the exact half-centered mean in every
positive-probability group. Retain complete orbit hashes and declared input/code
identities. Compare a separately coded sequential append/overflow check against
the product/tail formula, including exact equality and rejected conditions.

Use one finite whole-stream fixture with capacity 18 and separator 1:
[2,2,2,3,2,4,2,3,2,2,2,2,2,3,5]. It has two overflow-closed five-token rows,
with three interior orders each, followed by an exactly full unclosed tail.
Check every one of the nine joint interior permutations. Verify unchanged
closure indices, carried tokens, endpoints and the final tail; retain the
nonzero original score and the exact zero conditional orbit means. This is a
calibration fixture, not an IID simulation or an independent manuscript sample.

## Evidence and publication

Commit the final protocol/settings and accepted parent/method Git-blob pins
before certificate calculation. Preserve original parent parameters, scientific
reports, selectors and sources. Use a focused contributor branch and PR with
public tobrien6 noreply commit metadata. Publish the proof and all fixed
certificates, including the short and impossible cases, plus a reproducible
standard-library checker and independent tests. Keep calculations bounded;
there is no new 100,000-token sweep, corpus fit, p-value, confidence claim,
glyph decision, decipherment or translation. First-slot bias and conditional
interior symmetry concern different sampling conditions. This result cannot
exclude every layout process or determine how manuscript lines were produced.
