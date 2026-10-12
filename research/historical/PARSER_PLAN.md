# Historical parser plan, version 1

Question: what token stream follows from an explicit reading of Amancio et al.'s
Supporting Information S1, and which exclusion choices remain uncertain?

Freeze this plan before counting the processed corpus or fitting a repetition
statistic. It is an exploratory reconstruction on exposed source material, not
the authors' parser or a registered decipherment candidate. Do not adjust rules
to obtain the reported 37,762-token length. Preserve any discrepancy.

## Inputs and source support

Use H from the pinned LS16e6 archive and the native reader added in the
[intake](README.md). Verify archive and member hashes before processing. The
[paper supplement](https://doi.org/10.1371/journal.pone.0067310.s007), section
`Transcription of the Voynich Manuscript and parsing`, supplies the rules; its
inspected artifact hash is pinned in the [methods register](../literature/methods.json).
The exact 2010 download and processed sequence remain unproven.

Source-native unit comments support the following operational exclusions:

| Paper instruction | H selector | Source member evidence |
| --- | --- | --- |
| f49v column | f49v.L | Unit comment describes the left column of letters |
| f69r central six characters | f69r.W | Central-disk letter-label unit; six H records |
| f70r1 outermost ring | f70r1.C.1 | First of the three outer circular lines |
| f75 upper-right five characters | f75v.K | Loose letters near right corner; five H records |
| f76 letter column | f76r.L | Letter-label unit |

These are source-supported interpretations, not confirmation of the authors'
exact selectors. Save every excluded native locator and the original body hash.

## Two unresolved choices

The f57 instruction does not specify ring locators or the encoding unit for an
individual character. Run two declared interpretations: omit only f57v.R2 (the
ring described as a repeated character sequence), or omit single-character
**encoded tokens** throughout f57v.R1–R4 after spacing and filler handling. The
latter criterion does not identify manuscript glyphs; retain its limitation.

For f66r, compare excluding native M (letters/symbols) with excluding native L
(left-hand words). The [Yale scan](https://collections.library.yale.edu/catalog/2002046?child_oid=1006192)
shows words at the far left, a nearby column of isolated signs, and the main
text. The phrase about a first column resembling bullets does not resolve which
native unit the authors removed. Do not silently omit both.

Run the complete two-by-two matrix and retain all outputs. Give no variant the
status of a verified historical replication based on its count or statistic.

## Ordered transformations

1. Select native H records in archive order through the existing reader. Source
   line comments and page/unit headers are not text. No native line begins with
   percent; the supplement's percent-comment wording cannot be taken literally
   as the member's comment syntax.
2. Remove the one encoded fallback character immediately preceding a curly
   annotation whose complete code is in the supplement's special-character list.
   Retain an event ledger. This is an explicit interpretation of removing those
   characters; do not remove approximate multi-letter groups or unlisted codes.
3. Remove balanced curly comments, then exclamation and percent fillers. Replace
   comma, period, hyphen and equals with boundaries; collapse resulting spacing.
   Retain unreadable asterisks. Reject unsupported residual characters rather
   than guessing. Removing a character or comment may concatenate neighboring
   representation strings; record that chosen behavior.
4. Match each of the four published figure-label phrases only against a complete
   normalized H record. Record match locators and zero-match phrases; do not
   delete the same strings from larger text records or substitute similar words.
5. Apply the listed unit/line exclusions and both ambiguous choices. For the
   single-character ring treatment, record each removed token's original index.
   Preserve empty/excluded records as ledger entries, not artificial tokens.
6. Flatten surviving tokens in source order only for a requested whole-text
   export, preserving each token's native locator and original token index.
   Keep record breaks separately so future adjacency rules are explicit.

## Required report and validation

Pin the plan bytes, source identities, parser version and supplement identity.
Report every stage's record/token counts, all manual exclusions, special-code
events, label match counts, ring deletions, and exact output digests for all four
variants. Compare processed lengths with 37,762 as a diagnostic. Do not measure
B or sample a null in this contribution.

Test annotation/code ordering, fillers and separators, retention of unlisted
weirdoes and asterisks, exact label matching, native unit selection, both ring
policies, source order and token provenance, source-byte drift, and output replay
on small invented fixtures. Independently check the resulting exclusion ledger
against the cited member units. Preserve unmatched instructions and contradictory
counts; require an author-compatible corpus before claiming exact replication.

Prior exposure: the entire archive was structurally audited; relevant H snippets,
unit descriptions and code annotations were inspected, as was the f66r scan.
The paper's reported length was known before freezing this plan. These are not
untouched evaluation data or image-adjudicated glyph readings.
