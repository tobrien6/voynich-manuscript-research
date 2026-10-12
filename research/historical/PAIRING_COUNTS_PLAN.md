# Complete maximum index-pairing counts

Question: how many maximum order-preserving index pairings underlie the accepted
record-order ambiguity flags, and what fraction of those pairings contains each
possible pair? This measures encoded combinatorial ambiguity before any native
locator crosswalk. It adopts no physical row pairing or preferred source.

## Fixed inputs and complete scope

Use the accepted [record-order report](record-order.json), SHA-256
`0f053fd9a3bdeb2e92ae95da9d9c352cdf908b3a8be4aaec75b52c9a99211365`,
and its unchanged producer, SHA-256
`c0da851f03810696c7d72212130a76519bacc33173becd24dfbfcba7f32ba050`.
Verify the entire parent against its pinned historical H/modern IT2a sources,
plans and implementations before computing this follow-up. Retain the source
edition credits, reuse terms, original native orders, notation losses, empty
descriptors and excluded nonexistent modern envelope. Compare exact nonempty
projected strings before any digest serialization.

Keep all 211 equal-multiset pages: all 29 differing orders in detailed form,
182 equal-order identity controls, and the 16 excluded union pages separately.
Do not remove duplicates or ambiguous cases, tune a source order or select a
matching witness. Link each index pair to its immutable parent descriptors;
do not duplicate projected bodies or introduce page aliases.

## Exact count and support fraction

Create a DAG with one node for each equal-string index pair (i,j). An edge can
connect nodes only when both indices strictly increase. Each path is one unique
ordered list of index pairs. Count **longest paths**, not arbitrary skip routes
through a sequence-DP table: skip routes could count the same pairing repeatedly.
Use exact Python integers and retain zero-length synthetic cases as one empty
pairing. No random sampling, floating count approximation or tie breaking.

For every possible parent pair retain its matched rank, total maximum-pairing
count, number of maximum pairings containing it and reduced exact support
fraction. Counts through a node are the product of its longest-prefix and
longest-suffix path counts, provided it lies on a globally longest path. A pair
is mandatory precisely when that count equals the page's total maximum count.
At each matched rank, the counts through all possible pairs must sum to that
page total. Preserve the complete candidate inventory and the parent's L,
unmatched counts, mandatory flags, ranks and uniqueness.

Report all 29 per-page totals, the complete count histogram, unique/ambiguous
page counts and each ambiguous page's minimum/maximum nonmandatory support
fraction. Equal-order controls must have exactly one identity pairing. Do not
pool path counts across pages, construct a joint physical pairing distribution
or choose one of the possible pairings. A support fraction is a count ratio;
it is **not** a calibrated probability that two locators represent one row.
Uniform counting gives each distinct optimal index-pair sequence equal weight;
that explicitly chosen weighting supplies no prior over physical row identities.
Different index pairings of repeated projected strings remain observationally
indistinguishable and are not new manuscript observations.

## Validation and prior exposure

Verify all counts, support fractions, rank sums and mandatory/unique flags
against independent exhaustive index-subsequence alignment enumeration on small
synthetic sequences, including repeated strings, reversals, unequal lengths and
empty input. For the actual native report use a separate raw-envelope scanner
and a distinct rank-layer path-count calculation, importing no producer/reader
or projection routine. Verify every reported field, every source/plan/helper pin
and every guide table row. Keep typed full-report checks and protected-output
guards, with a final guard after serialization and exclusive fresh output
creation. Test failed checks and late aliases without modifying protected data.

The original sources, 211/182/29 split, all possible pairs/ranks and mandatory
flags are already exposed. During review of #167, this assistant's independent
DAG oracle **already computed native longest-path counts internally** to verify
uniqueness and mandatory status. This plan declares that prior computational
exposure; it does not preregister an untouched statistic or certify private
first-look timing. Publish this declared plan before the new count producer and
complete native count-summary assembly, retaining all outcomes.

This exposed-data diagnostic changes no source, glyph reading, physical row
mapping, historical attribution, language hypothesis or statistical eligibility.
Both verified-crosswalk and statistical-evaluation flags remain false. It
supplies no significance, likelihood, calibrated tail, decipherment or translation.
