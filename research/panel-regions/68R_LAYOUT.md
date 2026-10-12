# Provisional 68r writing layout

Question: how do the native `f68r1`, `f68r2`, and `f68r3` records relate to
the visible writing fields, without assuming that every page has P0 text or
that every crease defines a native-page boundary?

The [proposal](f68r-proposal.json) and [native-text checklist](f68r-p0-review.json)
remain provisional and **unusable as a verified corpus join**. They extend the
accepted [native-page convention note](../pilot/NATIVE_PAGE_CONVENTIONS.md) and
reuse the [67r review collector](README.md). No original source text is changed.

## Evidence and proposed rows

Inspected [Yale image 1006196, labeled 68r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006196)
on 12 October 2026 (America/New_York), using a
[2,400-pixel-bounded derivative](https://collections.library.yale.edu/iiif/2/1006196/full/!2400,2400/0/default.jpg).
The JSON retains its hash, dimensions, original image size, and manifest pin.
Only metadata and original observations are shared; image bytes stay local.

The [IVTFF specification](https://voynich.nu/software/ivtt/IVTFF_format.pdf),
issue 2.0.2, section 4.2 and appendix page 35, documents the recto numbering
direction and the three native names, with unqualified `f68r` as a placeholder.
The downloaded PDF hash matches the accepted convention note. Its relevant
table was visually inspected. Source counts and P0 texts were read before the
image, and this scan had already been exposed in the initial inventories.
This is not a blinded test or independent image/transcription reproduction.

| Proposed native field | Direct image observation | Present source records in each edition | Proposed P0 review |
| --- | --- | --- | --- |
| `f68r1`, left near binding | Three longer upper rows, followed by a short row near the left; a small upper drawing interrupts the writing area. | 37 total: 4 P0, 3 Pb, 29 Ls, 1 Cc. | Locations 1-4; check the drawing interruption at location 3. |
| `f68r2`, middle | Five upper rows above/alongside a small circular drawing, with scattered writing and star-like forms below. | 31 total: 5 P0, 2 Cc, 24 Ls. | Locations 1-5; check the drawing interruption at location 5. |
| `f68r3`, right | Large circular drawing with sector/circular writing and a crease passing through it. | 22 total: 2 Cc, 8 Ri, 11 Ls, 1 La; **zero P0**. | No P0 rows are assigned; a separate [non-paragraph packet and two radial attempts](F68R3_NONPARAGRAPH.md) now preserve this scope. |

A zero P0 count is a statement about the source's locus kinds. It does not mean
that the third page is absent, blank, or free of horizontal writing. The
checklist retains its required page header and all present-kind counts.
Its empty P0 list must not become an invented row or silently disappear.

The right-hand drawing crossing a visible crease also cautions against
equal-width crops or one-page-per-crease assumptions. The proposed fields are
textual locators, not exact masks. All three native names reference the same
leaf and canvas and must preserve that dependency.

## Source discrepancies and replay

Across the nine declared P0 locations, four native record texts are identical
between ZL3b and IT2a and five differ. This compares the reader's preserved
encoded text, including annotations; it is not a glyph-agreement score.
For example, `f68r1.4` has `okaiiin` in ZL and `okaiin` in IT, while
`f68r2.1` uses an uncertain comma in ZL where IT has a period. Image review
must preserve these alternatives rather than choose an edition by convenience.

The collector's default 67r output remains unchanged. The new 68r entry point
requires all three page headers and the exact declared P0 key sets, including
the empty set on `f68r3`. It checks pinned source bytes and retains native
text, source locators, page counts, and explicit pending glyph status.

```sh
python3 scripts/build_68r_review.py --check research/panel-regions/f68r-p0-review.json
python3 scripts/build_67r_review.py --check research/panel-regions/f67r-p0-review.json
python3 -m unittest tests.test_panel_review -v
```

Next, compare each proposed row with the original-resolution glyph sequence
and the drawing-interruption positions. Reject or revise mismatches, and
record precise reviewed regions before proposing a verified image/text join.
The [f68r3 non-paragraph follow-up](F68R3_NONPARAGRAPH.md) retains all 22 records
and proposes two compatible radial placements. Exact glyphs, boundaries and
independent review remain pending. No decipherment, translation, or
untouched-material claim follows from these packets.
