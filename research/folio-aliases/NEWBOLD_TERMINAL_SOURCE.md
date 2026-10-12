# Newbold's original terminal-material contexts and changing readings

The credited Newbold 1928 passages can now be inspected in a pinned
[hosted scan](https://oncle-dom.fr/biblio/1928-Newbold-The%20Cipher%20of%20Roger%20Bacon.pdf).
Printed p. 73 contains the early opening interpretation; printed p. 108 begins
Chapter IX, while the longer displayed transcript is on **printed p. 109**.
The editor explicitly describes that chapter as assembled from differently
dated papers and drafts. These are historical proposed readings, not accepted
glyph values or a decipherment.

This follows the two source credits recorded in pending
[PR #164](https://github.com/tobrien6/voynich-manuscript-research/pull/164).
Its reviewed head and files remain unchanged. This original-source note stands
separately and does not depend on acceptance of that PR or its interpretations.

## Source and exact locators

The title/copyright pages visibly give 1928, Newbold as author and Roland Grubb
Kent as editor. [Penn Press's record](https://www.pennpress.org/9781512813340/the-cipher-of-roger-bacon/)
corroborates the publication identity, while distinguishing its later offered
ebook. The inspected third-party file is **297 PDF pages / 46,842,963 bytes**,
SHA-256 `69e9f37fbafe3b76c96bae9fba5b6c459f639e97824f7f9bb9e9cf4504a9c891`.
Its Google/Michigan watermarks display Hathi item `mdp.39015004978535`; the
linked item could not be retrieved here, and identity with a current custodial
file is not asserted. No original physical copy is authenticated.

| Complete page inspected | Bounded source observation |
| --- | --- |
| Printed 44 / PDF 78, Chapter III opening and editor note 1 | Reports final folio number 116 and calls the final material a key. Credits the chapter to a 1921 lecture, pp. 461-474; that original lecture remains uninspected. |
| Printed 45 / PDF 81, Part V table | Retains folio ranges 103-108 and 111-116, separately from its equivalent-page totals. |
| Printed 73 / PDF 117 | Proposes a Latin interpretation after explicit omissions and a presumed spelling correction. The project accepts neither that reading nor its key claim. |
| Printed 74 / PDF 118, editor note 3 | Refers readers to Chapter IX for a final reading of closing letters. |
| Printed 108 / PDF 157, Chapter IX opening and editor note 1 | Introduces the transcript and identifies a compilation from varying drafts/dates. |
| Printed 109 / PDF 158 | Displays the longer proposed transcript and interpretive alphabet assignments. |
| Plate X / PDF 119 | Photographic terminal-material reproduction, credited to Wilfrid M. Voynich; no numerical folio label in the caption. |
| Plate XV / PDF 159 | Reproduction beside a separate hand transcript and printed rendering, with the same credit; no numerical folio label in its caption. |

Printed/PDF offsets differ because the representation includes inserted plates
and other pages. Each cited locator was checked visually; a global numeric
offset was not applied. The [ledger](newbold-terminal-source.json) retains the
individual correspondences, inspection scope, provenance limits and unchanged
registry fingerprint. Complete title/copyright, plate-list, context and cited
pages were inspected, including footnotes, captions and footers.

## What this changes and what remains open

The historical reading trail includes editorial redirection, differing draft
contexts, omissions and interpretation choices. These should remain explicit
if that proposal is evaluated under the [project protocol](../DECIPHERMENT_PROTOCOL.md).
The printed renderings are separate objects from manuscript pixels. No new
manuscript glyph transcription or comparison with present Yale images is
performed here, and no quoted translation is adopted.

The physical-description passage supplies a lead for the earlier
[publisher-preview quotation](CATALOG_EDITORIAL_FLAG.md). Its actual reference
7 remains uninspected; matching subject matter does not identify that endnote.
The claimed final number 116 and terminal photographs do not explain the
legacy Yale `117v` or establish its correspondence to current `116v`.
[Issue #13](https://github.com/tobrien6/voynich-manuscript-research/issues/13)
therefore remains open, with `mapping_allowed: false`, null verified target
and no statistical use. The source-numbering and editorial-marker ledgers
and all native/statistical inputs are unchanged.

## Extraction, access and verification limits

There is a concrete extraction discrepancy: the title page visibly prints
**1928**, while the local `pdftotext -layout` result reads **1918** at that
occurrence. Text extraction was navigation only; no date or whole-file
absence conclusion rests on it. Complete relevant pages were rendered with
Poppler and visually checked. An anonymously retrieved publisher front-matter
URL returned zero bytes, so no comparison of those PDF contents is claimed.

The source PDF, full extraction and fourteen rendered pages remain local.
Only brief source observations, selected identifier fields, links and
fingerprints are published. The alias registry's exact hash remains
`627ae452e40b2ea176ac50a641c1fb31c58fcbbcfa5fffddd4ed87415995dfc8`.
Existing alias tests and the actual blocked lookup are checked; this
documentation addition introduces no new checker or tests, and structural
verification does not validate the historical reading or physical alias.

```sh
python3 -m unittest discover -s tests -p 'test_folio_aliases.py' -v
python3 scripts/check_folio_aliases.py
python3 scripts/check_folio_aliases.py --lookup yale_legacy_ms408_catalog 117v
```

The final command should exit 1 with an unresolved decision and null target.
Next inspect the original 1921 lecture, the actual Kennedy/Churchill reference
7, and an explicit catalog-to-surface correspondence or custodial correction.
Keep source schemes and changing historical rules separate from verified
foliation, glyph interpretation and source-linked translation.
