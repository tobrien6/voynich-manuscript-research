# Repeated-type assay plan, version 1

Question: how do adjacent-pair events and distinct types with a self-repeat
compare under one global frequency-preserving null on the four declared
historical reconstructions?

Freeze this plan before measuring either statistic on those streams. This is an
exploratory assay of approximate, exposed input, not a reconstruction of the
authors' exact experiment or a registered decoding hypothesis. Keep all variants,
all ten controls and negative results. Do not revise the parser to improve a
ratio or match a published count.

## Inputs and units

Reuse the accepted [parser](PARSING.md), recompute its export, and require exact
agreement with the committed parsing report and per-variant corpus digests.
Pin source/archive/catalog, native reader, parser/plan/report and shuffle-primitive
bytes in the machine plan. Use all four ring/column combinations unchanged.
Prior length discrepancies and unmatched-label findings remain unresolved.

Tokens are complete normalized representation strings, including retained
asterisks. Count **A**, all equal adjacent-pair events, and **B**, distinct token
types with at least one such event. B follows the definition in
[Amancio et al. (2013)](https://doi.org/10.1371/journal.pone.0067310), Methods p. 7.
Both statistics use all N−1 edges of the surviving flat stream, including joins
between different native records. Empty/excluded records supply no tokens.

Report within-record and cross-record joining events separately, with distinct
type counts and their overlap. Also count within-record edges crossing a gap in
the pre-manual normalized token indices and any equal events on those edges.
These diagnostics do not capture earlier syntactic changes. Native records are
not established physical lines. Also report observed events/types whose literal string contains `*`,
without dropping or reinterpreting those strings. No glyph or word meaning is
inferred from representation equality.

## Null and exact mean

Uniformly permute all surviving token positions while preserving their complete
frequency multiset. The null mixes pages, units and native records. It is not
the accepted conditional within-P0-locus control.

For a type with c occurrences in N slots, its occurrence-position set is uniform
over C(N,c) choices. Sets with no adjacent occurrence number C(N−c+1,c), taken
as zero when c>N−c+1. Therefore:

```text
E[B] = sum_types (1 − C(N−c+1,c) / C(N,c))
E[A] = sum_types c(c−1) / N
```

Use exact rational arithmetic and group equal frequency classes for computation.
Types' repeat indicators are dependent; linearity of expectation does not
provide a joint variance or tail probability. Empty/singleton streams have zero
events/types. Ratios with a zero expected or sampled mean are undefined, not
infinite. Retain exact rationals in hexadecimal integer form to avoid changing
Python's decimal-conversion safety limit; display decimal approximations too.

## Ten deterministic control trials

Use the accepted SHA-256 counter stream and Fisher–Yates primitive, with a new
declared whole-text frame; do not invent a folio/line identity. Required seed is
20261012, trials 0–9. Serialize the array

```text
[algorithm, flat_corpus_sha256, "historical-whole-text-v1", seed, trial,
 [ring_policy, f66r_column_unit]]
```

as UTF-8 JSON with `ensure_ascii=False` and separators `(',', ':')`; SHA-256 of
those bytes supplies the draw key. Each trial starts from the original flat
stream, not a previous shuffled output. Verify the token multiset after every
shuffle. Report A/B for every trial, their ten-control means and observed/mean
ratios separately from ratios to the exact expectations. Ten trials follow the
published normalization scale but do not recover its unknown seed/implementation.

## Validation and limits

Before the manuscript assay, verify both exact means against all distinct
permutations of small multisets. Test repeated triples, overlapping events,
singleton/empty streams, case-preserving type identity, bijective relabeling,
forced repeats, record joining/overlap, seeded replay/multiset preservation,
source/report drift and protected outputs. No significance threshold, p-value,
language comparison or decipherment claim is declared here.

Report input identity, frequency-class counts, analytic means, observed units,
boundary/asterisk diagnostics, all controls, undefined denominators and all four
sensitivity outcomes. Differences from a global null may reflect source/layout
clustering or token conventions. They cannot be compared numerically with the
modern conditional event baseline as though only one factor changed.

Prior exposure: full historical source intake, parsing and caption lookup,
published methods/target length and prior full-corpus exploratory results were
already inspected. These are not untouched evaluation data. Exact original
input/parser recovery remains a separate requirement.
