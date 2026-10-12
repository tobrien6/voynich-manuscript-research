# Initial-prefix image review plan

## Question

When the pinned ZL3b and IT2a editions disagree about a literal `q` or `y`
prefix at the first token of a regular P0 locus, what does the linked manuscript
region support? This is a small source-adjudication exercise, not a new
transcription, decipherment, or estimate of either edition's accuracy.

## Selection fixed before image inspection

- Verify the accepted source catalog and use `plain-eva-v1` with P0 only.
- Require the same locus key to be eligible with at least two tokens under both
  split and join policies in both ZL3b and IT2a. Require `@`, `+`, or `*` locators
  in all four records. No ambiguous, unreadable, extended, or ligature-bracket
  locus is admitted through a partial-token exclusion.
- Require the first-token `q`/`y` Boolean disagreement to be unchanged under
  split and join policies. Compare literal case-preserved ASCII prefixes;
  do not equate them to phonemes or plaintext.
- Restrict image targets to exact single-side Yale canvas labels without partial
  or combined markers, and exactly one such canvas per transcription page.
  Do not infer panel aliases or identify a physical region from a numeric locus
  identifier alone.
- Sort candidates by numeric folio, recto before verso, then numeric locus.
  Select the earliest candidate on each of the first three distinct eligible
  folio sides. Publish all candidate keys, exclusions and source/image-index
  hashes so the review is not selected by a favorable visual outcome.
- Inspect each whole image, then link explicit IIIF region coordinates for the
  proposed text row and its beginning. If the source-to-row match cannot be
  supported from neighboring text and layout, mark alignment unresolved and
  refrain from choosing a reading. Do not replace a difficult selected case.

## Record and review

Keep both editions' first-token strings, locus identifiers, file line numbers,
source hashes, exact canvas labels and links. Record inspected derivative URLs,
dimensions and byte hashes. Source images stay local; publish links and original
observations rather than pixels. Consult the publisher's Basic Eva shape table
as a notation reference, retaining uncertainty about handwriting variants.

Distinguish visible strokes, proposed row alignment, and a provisional
representation preference. Any preference is a single observer's judgment and
must not silently modify the source files or enter a decoding corpus as a
verified correction. Report contradictory or non-estimable cases explicitly.
The next step is a second image-based review with independently checked regions.

## Prior exposure and authority

Both complete transcriptions and their aggregate prefix statistics were already
exposed in this project. Existing folio inventories may also have viewed some
selected whole images. This exercise cannot create untouched evaluation data.

Role: contributor for the user's continuing Voynich contribution goal. GitHub
identity and upstream owner are `tobrien6`; verified permissions include
admin/maintain/push. Work uses this isolated checkout. The designated maintainer
retains merge ownership; no self-approval is used.
