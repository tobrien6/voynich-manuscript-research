# Two opposite source-boundary cases on f102r1

The fixed corpus audit [PR #113](https://github.com/tobrien6/voynich-manuscript-research/pull/113)
identified literal encoded strings with different token boundaries. This
follow-up fixes one example in each direction and checks their provisional
image context. Both selections fall on adjacent native loci of the same foldout.

| Native key | ZL3b grouping | IT2a grouping | ZL / IT tokens | Encoded chain | Extra boundary |
| --- | --- | --- | ---: | ---: | --- |
| `f102r1.14` | `chos.s.or.oeeaiin` | `chos.sor.oeeaiin` | 11 / 10 | 47 ASCII letters | ZL, offset 38 |
| `f102r1.15` | `os.ykeeykam` | `os.ykeey.kam` | 9 / 10 | 42 ASCII letters | IT, offset 39 |

These are source-observed terminal groupings, not manuscript readings derived
from an independent glyph review. Each pair has an identical case-preserved
concatenated string under both comma policies. Neither locus has uncertain
commas, alternative readings, unreadability or drawing interruptions. The
extra period boundary persists under split and join. Source identifiers and
file lines, full original text, both token arrays, chains and offsets are
retained in the [review record](102r-boundary-pair-review.json).

## Selection before the new image inspection

The [frozen selection](102r-boundary-pair-selection.json) was committed at
`9d9d33ef1235eca9e760c987951cd760f1328af7` before retrieving and inspecting the
new target-specific carrier/block/detail images. Source text and the complete
corpus results were already exposed. This is a prospective record of this
image-review selection, not a prospective decipherment test or blind reading.

Starting from the exact report published at `5611563bf851320c93decd862976d3327f1e262a`:
require an identical-chain boundary disagreement under both spacing policies,
no drawing interruption in either edition, exactly one boundary offset unique
to the named source and none unique to the other, with the same unique offset
under both policies. Independently select the lexicographically first original
native key for ZL-only and IT-only boundaries. No image, folio, panel, region or
shape criterion participates in that choice.

There are **15 ZL-only** and **80 IT-only** eligible candidates under that rule.
The complete ordered candidate lists are preserved, including both selected
records under both policies. Lexicographic native-key order is not manuscript
reading order. The selection's report checksum is
`8c93d9cf1bb83e4f9690378d5fdd6100377e019bf17dede7e0f70de7a4df1bb6`.

## Foldout and provisional row context

The [IVTFF specification](https://voynich.nu/software/ivtt/IVTFF_format.pdf),
document issue 2.0.2 of 8 July 2025, section 4.2 and appendix printed p. 38,
lists `f102r` as a placeholder with written pages `f102r1` and `f102r2`.
Recto pages are numbered left to right away from the binding. It also records
that the `f101v1`/`f101v2` text is included in `f101v`. The inspected PDF's
SHA-256 is retained in the record; these source conventions do not define
precise text masks or imply equal-width panels.

The Yale carrier is [image 1006251](https://collections.library.yale.edu/catalog/2002046?child_oid=1006251),
labeled **101v (part) and 102r**, with native dimensions 8,176 by 3,864.
The accepted [coarse reference audit](../folio-alignment/IMAGE_COVERAGE.md)
keeps `f102r1`'s panel region unresolved and assigns dependency
`yale-leaves:100+101+102`. That metadata status remains intact.

Direct image observation: the shared scan has a left illustrated/written
surface, a middle illustrated surface beside the visible gutter, and a farther
unfolded right surface. The middle surface has three main horizontal text
blocks with four, four and five visible rows among plant-like and container-like
drawings. Both pinned native `f102r1` sources have 17 present loci: 13 P0 and
four short non-P0 inscriptions. Their P0 blocks likewise have lengths four,
four and five.

This source-informed structural agreement supports a **provisional** placement
of `f102r1` on the middle recto portion nearest the gutter, with selected
`.14` and `.15` at rows two and three of its lowest five-row block. It does not
verify the complete glyph sequence or precise row extent. `f102r2` retains 15
P0 loci in both sources but has 22 total present ZL loci versus 20 IT loci;
equal P0 counts do not certify complete annotation agreement. Neither edition
has a written `f102r` container header.

## Image observations and limits

Inspected on 12 October 2026 (America/New_York):

- [Complete carrier at 2,400 pixels wide](https://collections.library.yale.edu/iiif/2/1006251/full/2400,/0/default.jpg), returned 2,400 by 1,134.
- [Lowest middle-panel block](https://collections.library.yale.edu/iiif/2/1006251/3000,1850,2300,500/1500,/0/default.jpg), native viewing rectangle `(3000,1850,2300,500)`, returned 1,500 by 326.
- [Two provisional row endings](https://collections.library.yale.edu/iiif/2/1006251/4400,1990,800,300/full/0/default.jpg), native viewing rectangle `(4400,1990,800,300)`, returned 800 by 300.

The rectangles are inspection aids; neither is an adjudicated glyph/word mask
or exact locus extent. Neighboring rows and illustration strokes remain
visible. Hashes, byte sizes, dimensions and original-coordinate bounds are
retained; source pixels and the PDF remain local rather than redistributed.

For provisional `.14`, separate curved forms precede a longer sequence of oval
and upright strokes. Around the proposed `s/or` grouping, a blank gap is visible
without an apparent connecting ink stroke at this scale. For provisional `.15`,
the terminal group contains tall uprights, rounded marks and descenders. Ink
is crowded around the proposed internal `ykeey/kam` grouping, which appears
less isolated than the blank space to the left of the whole terminal group.
These descriptions depend on the provisional row association and known source
readings. They leave both glyph correspondence and linguistic word division
unresolved; no preferred source grouping or correction is assigned.

The cases have opposite source directions but share adjacent rows, one canvas,
and one conservative image dependency. They are not independent manuscript
samples or replications. The carrier was already in the project's inventories;
repeated inspection does not restore an untouched holdout. The record keeps
`apply_to_statistics` and `usable_as_verified_corpus_join` false, with independent
review pending.

## Replay and next test

Read the pinned corpus report and repeat the stated predicate for every
split/join disagreement pair. Check each complete ordered candidate list and
its first key against the frozen selection. The input report must match the
recorded checksum; if a later audit changes its implementation pins, use the
explicit public commit rather than silently rebinding the selection.

For each selected source locus, the accepted pin-checking loader and
`plain-eva-v1` tokenizer reproduce the native text, identifier/file line and
both token arrays. Recompute concatenated chains and cumulative offsets; the
set differences are exactly ZL-only `[38]` for `.14` and IT-only `[39]` for
`.15`. Original image bounds and byte/hash identities were checked against
the public derivatives, and the appendix naming table was visually inspected.
No executable or tokenizer is changed by this follow-up.

Next, have an independently assigned reader check the full carrier, proposed
row context and every glyph before proposing verified region or segmentation
records. Any candidate word-division rule needs frozen predictions on
exposure-valid material under the [evaluation protocol](../DECIPHERMENT_PROTOCOL.md).
Visible spacing alone does not recover a language or English translation.
