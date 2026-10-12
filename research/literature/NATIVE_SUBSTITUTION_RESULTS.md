# Native B substitution rankings depend on normalization

Question: do conditional-subset and whole-corpus word-entropy decreases have
the same maximizing replacement sets on the fixed recovered B input?

They differ for 21 of 35 native symbols. For the four fixed paper-associated
gallows symbols, two specific targets change, while all four symbols retain
another member of that same four-symbol set under both definitions. Every
declared comparison remains in the [complete report](native-substitution-normalizations.json).
This is an explicit implementation on a later author-associated input, not
authenticated reproduction of the 2011 procedure or a physical case assignment.

## Source, freeze and method

The unchanged [plan](NATIVE_SUBSTITUTION_PLAN.md) was committed at
`9a708c9fe5d8c357c43fa931a8d58297fec63474`. The producer and its synthetic tests
were committed, pushed and remotely verified at
`ba60d4546cdd9f355dff0a0f64c58cb3e7d65534` before the first native pair-score
calculation. Both files' identities are retained in the result. This sequence
is an author declaration supported by the preserved Git records, not blind
registration or untouched evaluation material.

Use `data/voy.b.paged.wds` at `sravanareddy/deciphervoynich` commit
`643b881b2937bae8193814d8ff5d6e99a48bf7c5`: 95,465 bytes, SHA-256
`723cb2746da37c8272005f71298917abfed60412b23597b2b8aecb95dc7a0ee4`.
Exact input verification precedes UTF-8/whitespace parsing. All 17,597 token
occurrences, 3,920 native word types and 35 codepoints remain, including case
and asterisks. Word frequencies weight both metrics. These are supplied
notation units, with no image/glyph adjudication or lexical-word claim.

All 595 unordered character pairs are evaluated once in canonical Unicode
order. Replacing all occurrences of either character by the other induces
the same word-count equivalence classes, so the pair supplies both directional
candidate comparisons. Each source symbol has all 34 other symbols as
candidates under both metrics. No word boundary is crossed or character
deleted. Unaffected words cannot collide with affected words after this
replacement; their distributions remain unchanged.

The [synthetic normalization note](SUBSTITUTION_NORMALIZATION.md) derives the
identity `whole decrease = (affected occurrences / all occurrences) * subset
decrease`. The original parent helper supplies collision classes, but its
floating-point entropy scores are not used for rankings here. Integer prime
exponents represent each information numerator exactly; normalized rational
prime signatures identify exact score equality. Scores are evaluated with
80-digit Decimal logarithms. The fixed `1e-60` guard would preserve unequal
near-maximum candidates as unresolved; none occurs in this run.

The paper, source/code/population audit, prior letter predictions and synthetic
reversal were exposed before this run; these substitution results are now
exposed too. No comparator-language source was selected. The prior
[source intake](REDDY_SOURCE_INTAKE.md) does not authenticate historical
preprocessing, and the [history follow-up](https://github.com/tobrien6/voynich-manuscript-research/pull/151)
does not recover private or other-archive code. No author implementation is
executed or represented as ported runtime behavior.

## Complete scope and the fixed focus

There are 187 zero-collision pairs, retained with exactly zero information.
The 70 ranking records include 68 resolved positive maxima and two
no-positive-optimum records: native symbol `1` has zero decrease against
every other symbol under both definitions. Those records preserve all 34
zero-score candidates without assigning a positive replacement. There are
no positive maximizing ties or numerically unresolved rankings.

Twenty-one source symbols have different positive maximizing sets; fourteen
have unchanged sets, including `1`'s two empty positive sets. Every changed
and unchanged comparison is retained, rather than selecting only the four
focus symbols or only changes.

The [paper](https://aclanthology.org/W11-1511.pdf), Section 3.2, printed page 80,
associates `B`, `F`, `P`, `V` with gallows. That literal list was fixed in the
plan and is used only for descriptive category membership here.

| Source symbol | Subset maximizer | Subset decrease, bits | Affected occurrences | Whole maximizer | Whole decrease, bits | Affected occurrences |
| --- | --- | ---: | ---: | --- | ---: | ---: |
| `B` | `P` | 0.259678441725 | 3,304 | `F` | 0.052363489007 | 5,972 |
| `F` | `P` | 0.652430938326 | 7,816 | `P` | 0.289788044209 | 7,816 |
| `P` | `F` | 0.652430938326 | 7,816 | `F` | 0.289788044209 | 7,816 |
| `V` | `B` | 0.234719430249 | 864 | `F` | 0.013788844799 | 5,407 |

All full-population denominators are 17,597. Subset scores condition on the
listed, candidate-dependent masses. The same pair's whole score is its subset
score multiplied by that mass fraction; the table's different winner columns
must not be compared as if they were the same pair. For `B` and `V`, the
identity of the maximizing replacement changes. The four-symbol category
observation persists under both normalizations. This does not identify the
physical function of a glyph, establish a case relation, or prove the original
published method or its interpretation.

## Reproduction and validation

```sh
PYTHONPATH=tests python3 -m unittest test_native_substitution_normalizations test_substitution_entropy_control -v
python3 scripts/native_substitution_normalizations.py \
  --input LOCAL_REFERENCE/data/voy.b.paged.wds --check
# A separate new report; existing outputs and aliases cannot be overwritten:
python3 scripts/native_substitution_normalizations.py \
  --input LOCAL_REFERENCE/data/voy.b.paged.wds --output NEW_REPORT.json
cmp NEW_REPORT.json research/literature/native-substitution-normalizations.json
```

The standard-library producer checks both pinned parent artifacts before
reading native input and makes no network request. Python 3.14.3 was used.
All thirteen focused native/parent tests pass. Synthetic cases test known
entropy values, exact prime information, different-count-scale ties, zero
maxima, preserved numerical ambiguity, dependency/input drift and typed JSON
comparison. The complete report regenerates identically.

A separate implementation importing no production method reconstructed the
raw word frequencies, every pair's complete groups/counts/type changes and
class digest. Direct before/after entropy distributions agree with all 595
pair scores to better than `1e-70` bits and with every displayed 20-digit
score. Independent integer-product ratios verify all prime expressions.
All 70 ranking records, 35 normalization comparisons, four focus records,
input/parent identities and pre-score plan/producer Git bytes agree. Exact
mass ratios, counts and prime expressions are retained; Decimal displays are
approximations, not uncertainty intervals.

Published fields contain only symbol labels, counts, merged-class frequency
vectors, hashes, expressions and scores. No native word strings, corpus bytes,
author code, generated logs or private paths are copied. Complete frequency
vectors allow arithmetic checking without redistributing the underlying words.

This adds a normalization-sensitive constraint for future decoding proposals,
while preserving the limited gallows-category observation on this input. It
supplies neither a language nor a glyph mapping, decipherment or translation.
Broader case-function tests need source/image review and suitable comparator
data; a decoding rule still needs source-linked prospective predictions under
the project's [evaluation protocol](../DECIPHERMENT_PROTOCOL.md).
