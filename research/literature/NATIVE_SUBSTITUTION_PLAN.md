# Native B substitution scores under two fixed normalizations

Question: do the conditional-subset and whole-corpus entropy definitions give
the same positive maximizing replacement sets on the pinned native B input?
Compare all source characters and retain the four paper-associated gallows
symbols as a fixed descriptive focus. Do not select a normalization by its
agreement with a published interpretation.

This follows the [synthetic normalization control](SUBSTITUTION_NORMALIZATION.md)
in [PR #153](https://github.com/tobrien6/voynich-manuscript-research/pull/153).
It is a new explicit count comparison on exposed input, not authenticated
historical replication or a registered decipherment test.

## Fixed input and prior exposure

Use only `data/voy.b.paged.wds` at `sravanareddy/deciphervoynich` commit
`643b881b2937bae8193814d8ff5d6e99a48bf7c5`, 95,465 bytes and SHA-256
`723cb2746da37c8272005f71298917abfed60412b23597b2b8aecb95dc7a0ee4`.
Verify those bytes before UTF-8 decoding and whitespace splitting. Preserve
case, asterisks and every native character; retain all 17,597 occurrences,
3,920 word types and 35 codepoints. Weight word counts by occurrence frequency.
Use no source correction, symbol grouping, vocabulary filter or comparator
language. These supplied words/codepoints are notation units, not independently
reviewed physical glyphs or lexical words.

The publication, complete source/code intake and history, token populations,
letter-prediction results and the synthetic score reversal are already exposed.
The source's unigram word-entropy/substitution functions were statically read.
No B substitution score has been calculated for this contribution before
committing this plan. Commit the original producer and its synthetic tests,
publish/verify that branch, and only then calculate native pair scores.

Pin the parent measurement helper `scripts/substitution_entropy_control.py`
to SHA-256 `4bc4ed684c8f86ac4775e50d505d8e5f70b9aace6db7f4955d0123c85d677145`
and its toy report to SHA-256
`c3bfa5ae655f992da7d34602b6e47a0b98ec600c41cdb9a05fe7a78f219d4cbd`.
The helper's source-observation fingerprint is provenance, not execution of
author code. Reject dependency drift before reading native input.

## Complete pair scope and both metrics

Enumerate the 595 unordered pairs of all 35 native characters in Unicode
order. For a canonical pair `c < d`, replace every `c` by `d` inside words.
This gives the same count partitions and entropy decrease as `d`→`c`; use the
shared pair score when considering either character's replacement candidates.
Never cross word boundaries or delete a character.

For each pair retain affected occurrence count `T`, all occurrence count `N`,
before/after type counts, the complete multiset of merged-class frequency
vectors, and a digest of the hashed native class identities. No native word
strings will be published. Compute both `I/T` conditional-subset and `I/N`
whole-corpus entropy decreases from the same collision information numerator:
`I = sum_g(n_g log2 n_g - sum_i(n_i log2 n_i))`. Include singleton/zero-collision
pairs explicitly; their information numerator is exactly zero.

Represent `I` as an exact sum of integer prime exponents times `log2(prime)`:
factor each positive count, accumulating `n_g*v_p(n_g) - sum_i n_i*v_p(n_i)`.
Retain the complete nonzero exponent vector for every pair. Dividing that
vector by `T` or `N` yields an exact rational signature for the score. Unique
prime factorization identifies exact equality of two such scores even when
their original count expressions differ.

Evaluate numerical scores with standard-library Decimal logarithms at fixed
80-digit precision; display 20 digits after the decimal point. If unequal
exact signatures lie within `1e-60` bits of a candidate maximum, retain a
numerically unresolved possible-maximum set and make no forced ranking. This
fixed guard is a numerical rule, not a significance threshold. Exact signature
ties retain every tied candidate in Unicode order. A zero maximum is reported
as no positive optimum, rather than assigning a substitution by a tie rule.

## Recorded comparisons and limits

For each of the 35 source characters, consider all other 34 as candidates
under each metric. Publish every pair score and all 70 ranking records,
including exact ties, zero maxima and unresolved cases. Record whether the
two positive maximizing sets differ, with unresolved cases explicitly null.

The paper's Section 3.2 identifies native symbols `B`, `F`, `P`, `V` as gallows.
For exactly those four, preserve both maximizing sets and whether each
nonempty resolved set contains only another symbol from that fixed four-symbol
list. No physical case, null-symbol or phonetic inference follows from this
classification, and no numeric prediction is made for the result.

Keep contradictions and unchanged rankings. Do not replace a metric, choose
a subset, add a case rule or search new normalization after viewing results.
Report both definitions as explicit implementations, with original 2011
preprocessing/runtime/method still unresolved. Validate all 595 count records,
prime vectors and 70 ranking records independently from raw local bytes and
the published frequency vectors. No p-value, confidence interval, language,
glyph mapping, decipherment or translation is claimed. A decoding proposal
still requires prospective source-linked predictions under the project's
[evaluation protocol](../DECIPHERMENT_PROTOCOL.md).
