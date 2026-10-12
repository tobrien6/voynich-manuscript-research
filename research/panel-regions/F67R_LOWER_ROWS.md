# Three lower 67r rows: source-informed context

Visible opening, middle and ending structures give partial support to the
proposed top-to-bottom placement of `f67r2.72`, `.73`, `.74` below the right-panel
drawing in Yale scan 1006194. The [complete record](f67r-lower-row-inspection.json)
retains all three outcomes, six literal source readings, nine fresh response
receipts, every context window and all unresolved features. **None of these
associations is a verified corpus/image join or full glyph transcription.**

## Selection, method and prior exposure

The [plan](F67R_LOWER_ROWS_PLAN.md) was published at
[`e3726cf`](https://github.com/tobrien6/voynich-manuscript-research/commit/e3726cf0da68530cb18f380bde77b205a1fe4376)
and its remote head verified before the new native-detail pass. All three are
the proposed right-panel P0 targets in both pinned sources; none was replaced.
The six source readings, layout, checklist and accepted
[upper-row inspection](F67R_UPPER_ROWS.md) were already known. The full scan
had already exposed both panels and the entire lower block during upper-row
review. The sequence is a declared tool record, not independently certified
chronology or an untouched evaluation.

Freshly retrieved the [complete bounded scan](https://collections.library.yale.edu/iiif/2/1006194/full/!1800,1800/0/default.jpg),
verified its unchanged accepted bytes, and viewed it again. Then inspected the
preselected native-pixel [right-panel band](https://collections.library.yale.edu/iiif/2/1006194/2486,2550,2486,800/full/0/default.jpg).
After that view, selected three overlapping tiles covering the openings,
middles and endings of all rows. After the tiles, selected and inspected three
complete row contexts. Every requested view is retained; no context extension
was necessary. Native pixels were not enhanced, sharpened or rotated.

Reused and viewed the previously retrieved [Basic Eva reference](https://voynich.nu/img/extra/eva01.gif)
after verifying its cached response hash. The record distinguishes this cached
view from the nine newly retrieved responses. Its [Table 3 explanation](https://voynich.nu/transcr.html)
had been read through the web reader during upper-row review; no new raw HTML
body or hash is claimed. The reference supplies shape context; its legacy
punctuation is not a parser specification.

## All three row associations

The source strings identify comparison context from credited pinned editions,
not a new complete image transcription. Ordinals refer to this lower horizontal
block, rather than a whole-sheet row numbering scheme.

| Target / proposed lower-block row | Visible partial anchors | Preserved source uncertainty |
| --- | --- | --- |
| `f67r2.72` / first | Small loop/short-stroke opening, later descending and tall looped structures, then prominent tall forms and shorter rounded groups near the fore-edge support the common sequence's order. | Both native bodies are identical, but pale strokes, exact minim counts, glyph values and word divisions remain unverified. |
| `f67r2.73` / middle | The red row has low hooked opening groups, a long crossing stem, two adjacent similarly shaped tall/roofed clusters, then a longer crossing cluster and short terminal groups. | Preserve ZL `sy,shees` / IT `syshees` and the complete ZL `okol.ar.olar` / IT `okalar.ol` terminal difference. Similar middle shapes do not certify repeated identical glyph strings. |
| `f67r2.74` / last | A faint low opening precedes a clearer long downward/tall structure; low curves, short-stroke groups, further tall forms and a loop-initial ending support the proposed lowest row. | Preserve ZL `odain` / IT `odaiin` and ZL `ar.air.ay` / IT `ar.oirsg`. Pale opening/ending details do not settle minim counts or the full terminal sequence. |

All three outcomes are `supported_by_visible_anchors`; no contrary row-order
anchor was identified at the inspected scale. This is partial, source-informed
support. It does not select an edition or certify its complete letters, glyphs,
word divisions or paragraph structure. Exact source-body agreement at `.72`
is agreement between dependent representations, not two independent witnesses.

ZL's physical source-file line 2943 says the following single line is in red
ink, immediately before `.73`. That publisher annotation was known before
this pass. The visibly red middle writing is consistent with it, but the two
are not independent glyph evidence. No chemical ink claim or function of color
is inferred. The full scan, both panels and all derivatives share
`yale-leaves:67`; neighboring drawing/text/margins remain exposed.

## Native contexts and response identity

Coordinates are `x,y,width,height` in the 4972 × 3738 image. Rectangles overlap
neighboring strokes and are inspection aids, rather than exact locus/glyph masks.

| Context | Native bounds / returned pixels |
| --- | --- |
| [Opening tile](https://collections.library.yale.edu/iiif/2/1006194/2670,2600,950,500/full/0/default.jpg) | `2670,2600,950,500` / 950 × 500 |
| [Middle tile](https://collections.library.yale.edu/iiif/2/1006194/3420,2600,950,500/full/0/default.jpg) | `3420,2600,950,500` / 950 × 500 |
| [Ending tile](https://collections.library.yale.edu/iiif/2/1006194/4170,2600,760,500/full/0/default.jpg) | `4170,2600,760,500` / 760 × 500 |
| [Row `.72` context](https://collections.library.yale.edu/iiif/2/1006194/2630,2655,2300,180/full/0/default.jpg) | `2630,2655,2300,180` / 2300 × 180 |
| [Row `.73` context](https://collections.library.yale.edu/iiif/2/1006194/2630,2760,2300,205/full/0/default.jpg) | `2630,2760,2300,205` / 2300 × 205 |
| [Row `.74` context](https://collections.library.yale.edu/iiif/2/1006194/2630,2870,2300,200/full/0/default.jpg) | `2630,2870,2300,200` / 2300 × 200 |

The current service-info response differs from the upper-row receipt only in
the ordering of advertised formats: `jpg,tif,gif,png` became `tif,jpg,gif,png`.
Both 887-byte bodies are available locally for comparison; swapping precisely
that substring reconstructs the new response. All other parsed metadata and
native dimensions are equal, and the complete scan bytes are unchanged. Both
actual response hashes are retained without rewriting the prior receipt.
Fingerprints identify retrieved bytes, rather than permanent service editions.
Only links, source context, metadata and original observations are published.

## Reproduce the metadata checks

From the repository root, standard-library Python:

```sh
python3 scripts/build_67r_review.py --check research/panel-regions/f67r-p0-review.json
python3 - <<'PY'
import hashlib, json
from pathlib import Path
from scripts.audit_transliterations import load_sources
p = json.loads(Path('research/panel-regions/f67r-lower-row-inspection.json').read_bytes())
for path, expected in p['input_sha256'].items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected
assert [r['locus_key'] for r in p['records']] == ['f67r2.72', 'f67r2.73', 'f67r2.74']
sources = {s['id']: (s, d) for s, d in load_sources()}
windows = {w['id']: w for w in p['response_fingerprints']}
for index, row in enumerate(p['records'], 1):
    assert row['proposed_physical_row_top_to_bottom'] == index
    assert row['association_status'] == 'supported_by_visible_anchors'
    for flag in ['every_glyph_verified', 'word_divisions_adjudicated', 'usable_as_verified_corpus_join']:
        assert row[flag] is False
    assert row['source_reading_preference'] is None
    assert [r['source_id'] for r in row['source_readings']] == ['ZL3b', 'IT2a']
    for reading in row['source_readings']:
        source, document = sources[reading['source_id']]
        pin = next(s for s in p['sources'] if s['source_id'] == source['id'])
        assert (source['sha256'], source['alphabet'], source['url']) == (pin['sha256'], pin['alphabet'], pin['url'])
        locus = next(l for l in document.loci if l.key == row['locus_key'])
        assert locus.present and locus.kind == 'P0'
        assert (locus.identifier, locus.line_number, locus.text) == (reading['locus_identifier'], reading['source_file_line'], reading['native_text'])
    assert row['context_window_id'] in windows
for window in windows.values():
    if 'native_context_xywh' in window:
        x, y, w, h = window['native_context_xywh']
        assert x >= 0 and y >= 0 and w > 0 and h > 0 and x+w <= 4972 and y+h <= 3738
        assert window['returned_dimensions'] == [w, h]
assert p['usable_as_verified_corpus_join'] is False and p['usable_for_statistical_evaluation'] is False
print('Three targets, six literal readings, frozen inputs and provisional bounds reproduce.')
PY
```

Online verification retrieves each exact response URL and compares bytes,
SHA-256 and returned dimensions. A changed image needs fresh visual review.
Metadata reconstruction verifies bounds/source identity rather than the shape
interpretation. All seven proposed horizontal rows now have context across two
passes; an independent region/glyph review and explicit crosswalk decision remain
necessary. The pilot 67r mapping gap stays open. No preferred source, glyph
meaning, language, mechanism, decipherment or translation is established.
