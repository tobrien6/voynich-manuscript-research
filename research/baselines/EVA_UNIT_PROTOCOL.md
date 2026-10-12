# Fixed-cohort encoding-unit sensitivity protocol

Recorded 2026-10-11 before computing these grouping results. This follow-up is
motivated by the observed ASCII-length result in [PR #30](https://github.com/tobrien6/voynich-manuscript-research/pull/30).
It is explicitly **post-result exploratory sensitivity**, not an independent or
confirmatory test. Commit these measurement choices before applying them.

## Question and fixed inputs

How much does the locus-initial length contrast change when native EVA letter
sequences are counted using declared grouping policies? Retain PR #30's exact
2,964-locus cohort, original token boundaries, case, source/spacing variants,
and deterministic token-index draws. The
[protocol JSON](eva-unit-protocol.json) pins the parent result, cohort, mappings,
and alphabet-reference fingerprints. Do not add exclusions or retokenize text
to improve a particular policy's result.

## Source and scope

Gabriel Landini's [EVA Alphabet Font Version 2 Reference](https://voynich.nu/hist/gabriel/eva2_reference.pdf)
was visually inspected on pages 4 and 6–7. Page 4 documents connected spellings
and capitalized variants; pages 6–7 compare multi-letter EVA representations
with historical alphabets. The PDF's own final page says it was updated in
July 2004. Its older punctuation/annotation table is **not** used to parse the
current IVTFF files; parsing stays with the accepted modern reader and adapter.

Those tables motivate a measurement sensitivity check. They do not establish
which connected shapes are single manuscript glyphs or semantic units. This
is a finite, analyst-declared grouping experiment, not an authoritative glyph
segmentation or a complete conversion to Currier or another alphabet.

## Three policies fixed in advance

1. **ASCII letters:** every original letter is one unit, reproducing the parent.
2. **Bench sequences:** group only the exact, case-sensitive patterns
   `ch`, `Ch`, `sh`, `Sh`, `cth`, `cTh`, `ckh`, `cKh`, `cph`, `cPh`, `cfh`, `cFh`.
3. **Bench and minim sequences:** use the bench list plus
   `in`, `iin`, `iiin`, `il`, `iil`, `iiil`, `ir`, `iir`, `iiir`, `im`, `iim`, `iiim`.

Scan left to right, using the longest matching pattern at each position.
Break equal-length ties lexically; unmatched ASCII letters remain single units.
Never lowercase text or match across an original token boundary. A returned
segment retains its exact original substring: concatenating segments must
reconstruct the original token. Grouped counts alone cannot reconstruct text;
the original tokens and mappings remain available through pinned inputs.

Overlapping strings such as `in`, `iin`, and `iiin` follow this explicit
precedence. Longer runs outside the list are not inferred as new single units.
Connected/capitalized examples outside the selected policies, including `cTHh`,
`cthh`, `ITh`, `ith`, `Ao`, `Yk`, `Ee`, `Oy`, and `Qo`, are not automatically
grouped. Ordinary fallback segmentation may still match a listed substring
inside an unlisted example. Report their occurrence and uppercase single-letter
fallback counts so incomplete scope is visible. Connectivity alone is not the
criterion for adding another grouping after viewing results.

## Measures and paired controls

Count emitted segments per original token and apply the parent's equal-locus
initial-minus-remaining-token mean contrast. For each source/spacing variant,
use the same 2,000 uniformly selected first-token indices under every unit
policy. Report all policy contrasts, exact conditional null standard deviations,
empirical conditional intervals, and full draws.

For each grouped policy, also report its observed contrast minus the ASCII
contrast and the **paired** null difference from those identical index draws.
Retain token/locus counts, cohort/source hashes, matching-pattern counts,
fallback scope, and parent/input/mapping/implementation fingerprints. Confirm
that the ASCII outputs reproduce the parent before interpreting grouped ones.

## Interpretation fixed before results

Report all three policies, including sign changes, small differences, or
contradictory results. Do not select a preferred policy based on which gives
the strongest effect. A changed contrast demonstrates representation
sensitivity under the declared experiment, not a correct glyph inventory,
language, mechanism, or translation.

The cohort retains the parent's conservative exclusions and whole-corpus
exposure. This creates no untouched evaluation set. Independent paleographic
review and fuller treatment of connected forms remain necessary before a
claim about manuscript glyph length or physical line position.
