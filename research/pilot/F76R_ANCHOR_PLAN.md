# Three native-locus image anchors on f76r

Recorded 2026-10-12.

Record this plan and the source selector before further f76r image inspection.
This is a small, purposive alignment pilot, chosen after the source-readiness
and whole-corpus statistical work. It is not an untouched evaluation set.

## Fixed selection

Use the pinned ZL3b and IT2a sources through the accepted IVTFF reader. Retain
their native text, case, punctuation, alternatives, tags, locus identifiers,
physical source-file line numbers, and alphabet names. Do not tokenize, resolve
readings, or normalize either edition.

Restrict to page `f76r`, present `P0` loci with regular locators `@`, `+`, or `*`
in **both** editions. Intersect keys, sort by integer locus number, and select
the first, lower median, and last. For N eligible keys, their zero-based ranks
are `0`, `(N - 1) // 2`, and `N - 1`. Require at least three distinct keys.
No readability or text-agreement filter is applied. Report all excluded page
keys with both source identifiers and reasons. Include immediately adjacent
source loci for each anchor; an `=` locus can be another fragment of a physical
line and must not be mistaken for another line by counting key numbers.

The frozen source computation has 38 shared regular P0 keys and selects
`f76r.1`, `f76r.35`, and `f76r.56` at ranks 0, 18, and 37. The native first
readings differ in both the first and median anchors; preserve those differences
rather than selecting an edition by agreement with the image.

## Image identity and inspection

The accepted inventory/index identify Yale image `1006210`, label `76r`, a
single-side canvas of 2793 by 3769 native pixels. Preserve its exact manifest,
canvas, image-service and catalog identities in the selection record. Verify
derivative dimensions and byte digests for every inspected file. Reference
regions in **native image pixels**, origin at the upper-left, x increasing
rightward and y downward, `[x, y, width, height]`. Display scaling does not change
that coordinate system. Crops may be chosen during inspection to locate the
frozen anchors; this is not prospective region selection.

For each of the three anchors, attempt to associate a visible writing row with
the complete native source locus. Use page order and multiple visible shape/
spacing anchors. Separate the direct image observation from the proposed
source-row correspondence. Record the preceding/following context and any
competing row/region. If association fails or remains ambiguous, retain the
anchor, mark it unresolved, and explain why. Do not invent a successful match.

End at **provisional row alignment**. These observations cannot adjudicate
glyph identities, exact word segmentation, paragraph markers, source accuracy,
or an authoritative physical-line mapping. No source correction, new parser,
unit policy, statistical rerun, or proposed reading/translation is in scope.

## Exposure and deliverable

The project's original inventory already inspected f76r. This chat has also
inspected other manuscript images and analyzed both whole-corpus text sources.
The current anchor selection reads native f76r text before image inspection.
Disclose the later image inspection and its derivatives as further exposure.
Neither the three anchors nor other rows on this page become untouched
evaluation material.

Publish the fixed selection, small source-linked review JSON, readable result,
and an offline metadata verifier. Keep image pixels local and publish Yale
links. The verifier checks selection, source/image identities, native text,
region bounds, fingerprints, complete anchor coverage, and provisional-only
status; it cannot validate visual judgments. A later comparison UI can consume
the source text and image-region links without treating the matches as settled.

Independent review of all three proposed regions, including contradictory
readings and neighboring rows, is the next test before an accepted mapping.
