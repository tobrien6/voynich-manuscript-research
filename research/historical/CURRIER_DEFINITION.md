# Native H coverage under one primary-table parser

The independently supplied Currier/Eva table fully defines 37,420 of 37,919
native H tokens under the declared longest-match parser. The other **499
tokens retain all 637 unmatched characters**. The resulting partial notation
has 160,602 codepoints versus 191,825 in the input, while all 8,151 token types
and every immediate-repeat equality flag are preserved. No Reddy corpus is
read or compared in this H-only audit.

## Fixed inputs, procedure and exposure

The [primary source intake](../transliteration/CURRIER_CONVERSION_SOURCE.md),
[catalog](../transliteration/currier-conversion-source.json) and
[PR #181](https://github.com/tobrien6/voynich-manuscript-research/pull/181) at
`a03ac3589bb138be98a701666a481d9d4b1174e6` pin the author-hosted definition,
version 1.5 manual and README. That prerequisite is now accepted at corrected
head `410d4107e3bc775cf1fe9f6efeabd2ede919d10b`, merge
`c30f7dd9eb1ead3ae8e7c8f1386db494a4f9db25`. The
[source amendment](CURRIER_DEFINITION_SOURCE_AMENDMENT_1.md) records its
three added inspected-page entries and preserves the complete first evidence.
All three raw artifacts remain local. The
definition is SHA-256
`31105cb66e966bc7532c58178a867bf5b090c0473f047a3fdd30ee84bd339d32`.
The current 2025 definition is not authenticated as a historical 2011
preprocessing step.

Use the [native 1.6e6 catalog](../../data/historical/interlinear-16e6.json)
and all selected H records from its pinned publisher ZIP/member. The unchanged
accepted normalizer uses an empty listed-code set, retaining coded fallbacks
before all manual exclusions. No exclusion, code deletion, case folding,
alphabet fit, source pairing or uncertainty-symbol removal occurs.

The [human plan](CURRIER_DEFINITION_PLAN.md) and
[machine parameters](currier-definition-plan.json) were committed at
[`1c15348`](https://github.com/tobrien6/voynich-manuscript-research/commit/1c15348).
The synthetic-tested producer was committed at
[`678502d`](https://github.com/tobrien6/voynich-manuscript-research/commit/678502d).
Both were pushed before new H coverage/length measurements. Full source,
inventory/parsing, approximate assays, pending envelope/type results, primary
definition and synthetic string limits were already exposed. This descriptive
whole-source calculation is not untouched evaluation.

The producer checks eight dependency hashes, all three source artifact
identities, every rule-row/column identity, complete structural/synthetic
catalog diagnostics, and full accepted native-intake/parsing report replay.
It executes no author program.

At each original normalized-token offset, choose the longest matching Eva
right-column definition and emit its single Currier left-column code once.
Advance past the matched substring without rescanning output. If no rule
matches, copy one original character opaquely and flag its token-local offset.
This is one specified parser model, not full Bitrans program conformance.
Bitrans's larger-group scheduling and equal-length overlap/file-order behavior
are separate from this model's per-position longest match. Its IVTFF-header
rewriting exception also does not enter isolated normalized-token processing.
Output with unmatched symbols is **partial definition-based notation**, not
certified complete Currier transliteration or verified manuscript glyph units.

## Complete coverage and notation counts

The [complete report](currier-definition.json) retains all 5,214 native records,
their descriptors/file lines/body and vector hashes, every one of 637 unmatched
events, all 38 rule-use counts including zero use, all 8,151 type-pair/frequency
rows, character/length distributions and source/output repeat scopes.
Raw tokens, corpus bodies and the author's complete rule payload are absent.

| Measure | Count |
| --- | ---: |
| Native H records / normalized-empty records | 5,214 / 1 |
| Tokens fully covered / with unmatched symbols | 37,420 / 499 |
| Types fully covered / with unmatched symbols | 7,760 / 391 |
| Nonempty records fully covered / with unmatched symbols | 4,802 / 411 |
| Input notation codepoints | 191,825 |
| Matched input codepoints | 191,188 |
| Matched rule uses / emitted definition codes | 159,965 |
| Opaque unmatched codepoints | 637 |
| Partial-output codepoints | 160,602 |
| Input / partial-output notation-character types | 23 / 41 |

Input accounting is `191,188 + 637 = 191,825`; output accounting is
`159,965 + 637 = 160,602`. Group substitution removes 31,223 notation
codepoints, without removing any token, unmatched symbol or source record.
Thirty-seven definition rules occur; file line 12 has zero use. The output's
41 character types include the opaque unmatched symbols, so this count is not
an inferred manuscript alphabet size.

| Unmatched original codepoint | Occurrences |
| --- | ---: |
| `U+002A` (asterisk) | 280 |
| `U+0063` (c) | 157 |
| `U+0068` (h) | 198 |
| `U+007A` (z) | 2 |
| Total | 637 |

Every event supplies selected-H ordinal, local token index and original
normalized-token character offset. These are source-notation offsets after
comment/filler/separator normalization, not raw body byte positions or physical
glyph coordinates. The unmatched policy remains unchanged after observation.
The record ledger distinguishes the naturally empty record from nonempty
records with incomplete coverage.

## Recovery, type equality and repeats

The decoder expands known single Currier codes through the definition and
copies all other output characters unchanged. Every one of the 37,919 output
tokens recovers its original exactly. The complete type relation is bijective:
8,151 input types and 8,151 output types, with no source-type split or collapse.

This is also explained by the checked alphabet condition. Every permitted
input character that is a Currier output code has a single-character Eva rule,
so it cannot pass through as an unmatched character that the decoder would
reinterpret. Unique single output codes then decode each matched group back
to that group, while unmatched characters decode to themselves. Concatenating
these recoveries proves injectivity for this declared input alphabet and parser.
It does not guarantee the opposite round trip for arbitrary Currier strings;
the source intake's twelve synthetic failures remain unchanged.

| Repeat measure | H input | Partial output |
| --- | ---: | ---: |
| A: equal neighboring edges, complete flattened stream | 323 | 323 |
| Within-record A | 311 | 311 |
| Joining A | 12 | 12 |
| B: distinct repeated types, complete flattened stream | 118 | 118 |
| Within-record B | 115 | 115 |
| Joining B | 9 | 9 |
| B overlap between scopes | 6 | 6 |

There are 32,706 within-record opportunities and 5,212 flattened joins, totaling
37,918 noncyclic edges. The join from H ordinal 4,421 to 4,423 spans the empty
ordinal 4,422; both equality flags are false. Empty source boundaries remain
explicit, and joins do not assert physical manuscript adjacency. Type-equality
preservation follows from this invertible model and is not evidence of correct
glyph identification, semantic wordhood or language.

## Reproduce and validation

Python 3.10 or later, standard library only. Retrieve the three exact reference
URLs from the primary source catalog into a local directory, without executing
the author's program. Run from the repository root:

```sh
python3 -m unittest tests.test_historical_currier_definition -v
python3 scripts/historical_currier_definition.py --reference /path/to/local/reference --check research/historical/currier-definition.json
python3 scripts/historical_currier_definition.py --reference /path/to/local/reference --output /tmp/currier-definition.json
cmp /tmp/currier-definition.json research/historical/currier-definition.json
```

Fourteen focused tests cover greedy spans, noncumulative output, opaque offsets,
asterisks, exact character accounting, decoder conditions, malformed/ambiguous
definitions, source identity/order, all pins, both complete-parent failures and
existing-output preservation. All 20,439 allowed tokens of lengths one through
three decode and remain distinct under a fictional synthetic definition; this
test republishes no full author mapping. A separate trie generates a fictional
38-rule catalog's complete 1,444-case diagnostics, which the parser verifies.
Ninety-five temporary early/late direct/symlink/hardlink alias cases preserve all
nineteen protected files. Added transition tests bind the original plans,
source/producer/report artifacts and exact permitted catalog change, and reject
any changed source-derived result or boolean/integer substitution.

The report replays byte for byte. An independent raw ZIP scanner with a comment
walker and prefix trie imports none of the accepted readers/normalizer or new
producer. It checks all 5,214 record ledgers, all 37,919 token recoveries and
8,151 type pairs, all unmatched events and rule-use counts, all character/
length distributions, both flat vector hashes, complete repeat sets/scopes and
every one of 37,918 equality-edge flags. Report SHA-256:
`9f022fd41b7b227296dca88869b249f15a1904019d5c726926e50b2fc69b403a`
identifies the preserved first report. The accepted-source replay retains every
observation, original plan/hash map and source vector exactly; only the producer
fingerprint changes and two provenance fields are added. The runtime compares
that complete normalized payload to the first report before writing. The
amendment supplies original/effective source fingerprints and accepted chronology.
Current amended report SHA-256:
`c13357ab0c1a618084a6a52655fb46680d3fe85f770c2207a317500bf22d3d7d`.

## Rights and next work

Native H credits Jorge Stolfi, Gabriel Landini, Jim Reeds, Takeshi Takahashi and
the transcribers in the unmodified member. Its publisher permits copying, use,
modification and republication with due credit and without additional
conditions/copyrights; the repository MIT license does not replace those terms.
The primary rule/manual/README raw copies remain local under their intake's
separate reuse limitation. This contribution publishes original code and
metadata only.

The experiment separates notation compression from information loss and
quantifies the definition's incomplete source coverage. It supplies a fixed
input for a later independently frozen comparison, whose unmatched-symbol and
annotation choices must remain explicit. It establishes neither a historical
conversion, Reddy input identity, complete Currier edition, physical glyph
mapping, calibrated statistical tail, language, decipherment nor translation.
