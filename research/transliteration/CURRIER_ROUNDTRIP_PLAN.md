# Exact round-trip language of a declared greedy model

## Question and exposure

Which strings over the 38 Currier rule codes survive concatenated Eva expansion
followed by per-position longest-match reversal, and how many such strings exist
at each source-code length? This is a finite-state property of a current primary
definition and one declared parser, with no manuscript input or fitted mapping.

The accepted [source intake](CURRIER_CONVERSION_SOURCE.md) has already exposed
the complete table metadata, thirteen proper-prefix pairs and all 1,444 ordered
two-code diagnostics, including twelve failures. The example `ID` becomes `in`
and returns `N`. The rule bytes and manual have been inspected. The H-only model
in PR #186 and its exact recovery observations are also exposed. This plan
does not reuse its data, adopt that pending PR, or claim untouched evaluation.
No longer-string primary-table language or state graph has yet been measured.

## Fixed inputs and semantics

Freeze the accepted source catalog and source guide by complete SHA-256. Require
all three local primary artifacts to match the catalog's complete bytes/hashes,
and verify all 38 physical rule rows, column hashes, unique codes and lengths.
Raw definitions/manual/README remain local; no author software runs.

Input symbols are the distinct one-codepoint left-column entries, labelled in
published metadata by physical rule lines 5–42. Encoding concatenates their
right-column strings. Reversal repeatedly selects the longest matching
right-column prefix at the current position and emits its one left code.
An unmatched character is a failure; none is repaired, deleted or case-folded.
There is no annotation, whitespace or separator context in these synthetic
strings. This model does not implement full Bitrans rule scheduling, rule blocks,
protected comments, headers or overlap priority.

## Complete finite-state construction

Delay decoding while the entire pending Eva buffer is a proper prefix of any
right-column entry: future input could change the longest match. Otherwise
commit its longest matching prefix. Compare that emitted rule identity with
the first still-pending source rule identity. Reject immediately if they differ
or no match exists; a mismatch cannot later restore exact source equality.
Continue until the buffer is empty or a proper prefix. At each input-code
boundary, the buffer is exactly the concatenation of the pending source codes'
definitions when every committed output has agreed. No raw buffer is published.

Each nonempty delayed buffer is a proper prefix of an entry of maximum length
four. Its length is at most three, and every source definition is nonempty.
The pending source queue therefore has at most three codes. Breadth-first
closure from the empty queue over every one of the 38 inputs yields the complete
reachable deterministic graph, with one absorbing rejection state. At EOF,
flush greedily without delaying and compare every remaining output. EOF success
does not require that a nonempty pending queue was already emitted.

Publish every state's pending rule-line queue, shortest reaching rule-line
sequence, EOF acceptance and all 38 transitions. State identities and intermediate
text use canonical hashes; the complete mapping payload is not redistributed.
Retain every rejecting transition and failed EOF case, without choosing a
successful subset. The proof above supplies the all-length bound; a finite
enumeration alone is not presented as an all-length proof.

## Counts and checks fixed before measurement

Count accepted/rejected source strings at lengths 0 through **12** by exact
integer transition dynamic programming. Retain total `38**n`, accepted and
rejected integers and a reduced rational accepted fraction at each length.
Uniform independent source-code draws are an artificial counting measure,
not a distribution inferred from the manuscript or language.

Independently enumerate all primary-table source strings of lengths 0–3 using
a whole-string longest-prefix reference decoder; require every automaton decision
and every count to agree. Require the length-two failure ledger to match all
twelve accepted intake cases by input physical rule-line sequence. Retain all
new counts even if every pair failure is already known.

Before primary measurements, test synthetic dictionaries with independent
whole-string decoding: all injective two- and three-code assignments to binary
strings of lengths one or two, every source string of lengths 0–5; additional
length-four dictionary cases; prefix-free, delayed EOF, straddling, mismatch and
invalid dictionary cases. Verify count accounting, shortest graph reachability,
strict JSON, source/catalog/plan mismatch failures and preservation of existing
output. Reject direct, symbolic and hard-link output aliases of all dependencies,
plans, producer and local references both before calculation and before write.

Commit/push this human/machine plan, then the synthetic-tested producer, before
running complete graph closure, longer-string counts or primary enumeration.
Publish complete results and replay instructions in a separate results commit.
This is a constraint on notation segmentation, without historical corpus
authentication, glyph equivalence, Bitrans conformance, decipherment or translation.
