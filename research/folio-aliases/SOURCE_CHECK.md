# Terminal folio reference: source-numbering check

The sources inspected here do **not** establish a verified alias from the
legacy Yale catalog's `117v` to the current canvas label `116v`. They do
establish a separate issue: historical **folio identifiers and page counters
must retain their source schemes**. A counter discrepancy cannot authorize a
one-folio shift in manuscript references.

This check follows [issue #13](https://github.com/tobrien6/voynich-manuscript-research/issues/13)
and the existing [unresolved registry entry](decisions.json). Source descriptions
and earlier endpoint observations were already exposed. No new manuscript
glyph inspection, reading, collation, or decoding is claimed.

## Recorded evidence

| Source and inspected locator | Recorded identifier fields | Scope |
| --- | --- | --- |
| [Legacy Yale MS 408 catalog](https://pre1600ms.beinecke.library.yale.edu/docs/pre1600.ms408.HTM), Part VI | `117v` for a short presumed key | Catalog statement; its interpretation is not validated. |
| [Pinned Yale canvas index](../image-index/canvases.csv), final numbered pair | `116r`, `116v`; image IDs 1006276, 1006277 | Digital metadata; not a correction of the legacy label. |
| [Currier Table A, hosted PDF](https://voynich.nu/extra/img/curr_tabA.pdf), single page, rightmost block, row 116 and column legend | Folio field `116`; page fields `235`, `236` | Direct table observation. The legend distinguishes folio and page columns; no automatic recto/verso or Yale-canvas join is supplied here. |
| [Jim Reeds, checklist, 11 Sep 1995](https://www.ic.unicamp.br/~stolfi/voynich/mirror/gillogly/checklist), opening explanation and final rows | `116r → 234`, `116v → 235` in the Petersen-page column | Reeds's recorded scheme, with a warning about Currier's counter discrepancies. |
| [Stolfi's f116v note](https://www.ic.unicamp.br/~stolfi/voynich/Notes/040/html/f116v.htm), Identification | `f116v = p234 (Stolfi)` | Explicit source-specific page label; its origin is not inferred from the other counters. |

The [description by René Zandbergen](https://voynich.nu/descr.html#folios)
separates foliation `1–116` from Petersen photo-page numbering `1–236`.
Its note 17, following Reeds, flags inconsistencies in Currier page-number
ranges `167–179` and `206–236`. That warning concerns page counters;
it does not explicitly identify Yale `117v` as current `116v`.

The [machine-readable observations](source-numbering-observations.json)
retain each scheme, raw field, locator, and the PDF fingerprint. They are a
manual source extract, not a verified crosswalk. The selected table row is
recorded without copying the entire table or historical contact details.

## Inspection and identity

The hosted Currier table was downloaded from the linked publisher endpoint:
9,421 bytes, one PDF page, SHA-256
`3be46a0016a61e17d27e6d9d7086236c1a363f3c09927535ce9de525fdca54d3`.
The page was rendered with Poppler and visually checked, including the legend,
folio 116 row, and both page fields. Extracted text was a secondary check.
The hash identifies this hosted digital representation, not an authenticated
original seminar print or a verified historical edition. The source register
records [S005/S006 and their limits](../SOURCES.md).

PDF and render bytes remain local. Only links, the fingerprint, selected
identifier observations, and original analysis are added to the repository.
D'Imperio's *An Elegant Enigma* PDF was located through its NSA link, but
retrieval did not complete; no claim in this check relies on its contents.

## Result and next test

The three recorded page-number conventions cannot be pooled by numeric value.
Even if a page-counter offset is corroborated, it does not resolve a label in
a different foliation scheme. This check neither proves a lost folio 117 nor
declares a catalog error. The registry retains `status: unresolved`, null
review/verified-target fields, and `mapping_allowed: false` on lookup.

To settle the legacy reference, seek a custodial correction, documented
facsimile convention, or a source that explicitly connects that catalog entry
to the current surface. Check the final recto/verso and the basis for the
catalog's description. Record that evidence and scholarly review before
changing the alias gate. Historical counter normalization must be a separately
versioned decision with its own source-specific support.
