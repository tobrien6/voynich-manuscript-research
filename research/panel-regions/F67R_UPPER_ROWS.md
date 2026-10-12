# Four upper 67r rows: source-informed image anchors

The four upper horizontal rows support the proposed placement of native
`f67r1.1`–`f67r1.4` in order through visible opening, middle and ending anchors.
The [inspection record](f67r-upper-row-inspection.json) retains all four outcomes,
all eight unmodified source readings, eleven response fingerprints and the
unresolved features. **These partial anchors do not verify every glyph or a
corpus join.** The original proposal/checklist and pinned sources remain unchanged.

## Selection and method

The [plan](F67R_UPPER_ROWS_PLAN.md) was published at
[`912bf87`](https://github.com/tobrien6/voynich-manuscript-research/commit/912bf8724db1c7f632ec61bc8fd1bf7f53b8c139)
and the remote head verified before this pass's first image view. All four P0
keys in the proposed left-panel upper block were fixed; none was replaced.
The native readings, prior layout and first-row boundary observation had already
been read. This is another source-informed, nonblind AI inspection, with no
untouched evaluation or independent manuscript-witness claim. The sequence is
a declared tool record, not independently certified chronology.

Inspected the [complete Yale scan 1006194](https://collections.library.yale.edu/iiif/2/1006194/full/!1800,1800/0/default.jpg),
whose bytes match the accepted proposal, then the preselected native-pixel
[upper band](https://collections.library.yale.edu/iiif/2/1006194/0,200,2486,900/full/0/default.jpg).
Its four rows sit above the large circular drawing. The complete view also
exposes the right-panel drawing and lower writing; these are the same leaf and
image dependency, rather than independent samples.

After the band, selected three overlapping native-pixel tiles across the whole
block, followed by four row-context windows. All requested windows were
retained; none required extension. The rectangles overlap neighboring strokes
and are context aids, not exact glyph/word masks. No image enhancement or
rotation was applied. The [Basic Eva forms](https://voynich.nu/img/extra/eva01.gif)
and [Table 3 explanation](https://voynich.nu/transcr.html) supplied shape context.
Its legacy punctuation examples were not used for parsing. Encoded letters,
glyphs and linguistic word divisions remain separate questions.

## All four row associations

The source strings below identify comparison context from the pinned editions;
they are not a fresh full-row transcription from the images. Direct shape
observations and each unresolved feature are separate fields in the record.

| Native target / proposed row | Source context compared | Visible placement anchors | Preserved uncertainty |
| --- | --- | --- | --- |
| `f67r1.1` / top row | `teeodaiin.shey`; `epairody.osaiin.yteeoey`; terminal `shey.epaiin` and `o`/short strokes | Tall paired-stem opening, later crossing/tall structures and minim-like clusters occur in the proposed order; a closed oval and short stroke cluster close the row. | The terminal visible gap preserves ZL `o.aiin` / IT `oaiin`; it does not adjudicate word division. |
| `f67r1.2` / second row | `daiir.okeody`; `sar.oeteody.oteey`; `keey.keo.keeoda` | Distinct loop/short-stroke opening, successive oval/tall clusters and a longer terminal cluster support the second row. | ZL `qoekeey` / IT `qoekshg` and final ZL `[l:?]` / IT `l` remain unresolved. |
| `f67r1.3` / third row | `ycheo.s`; `aiin.okesoe`; `shees.dalaiin.dam` | Descending opening, a later minim-like group before an oval/tall cluster, and two loop-initial closing clusters support the third row. | ZL `o,iim.[che:eee]os` / IT `o.g.cheos`, and ZL `ar.am` / IT `aram`, remain unresolved. |
| `f67r1.4` / lowest row | `cheodaiin`; middle short clusters; `cheey.dair.cthey` | Low roofed opening and a distinctive final tall benched structure support the lowest row, which ends earlier than those above. | ZL `[ch:a]`, explicit/uncertain boundaries and their IT groupings are preserved. |

All four associations are classified `supported_by_visible_anchors`. No
contradictory row-order anchor was identified at this scale. That statement
does not certify either source's complete glyph string or choose a preferred
edition. Related editions are comparison representations, not two independent
physical witnesses. The first-row gap adds full-row context to the accepted
[boundary case](67R_BOUNDARY_CASE.md) while retaining its segmentation question.

## Context windows and provenance

Native coordinates are `x,y,width,height` in the 4972 × 3738 image.

| Context | Native bounds | Returned pixels |
| --- | --- | --- |
| [Opening tile](https://collections.library.yale.edu/iiif/2/1006194/350,300,1000,500/full/0/default.jpg) | `350,300,1000,500` | 1000 × 500 |
| [Middle tile](https://collections.library.yale.edu/iiif/2/1006194/1050,300,1000,500/full/0/default.jpg) | `1050,300,1000,500` | 1000 × 500 |
| [Ending tile](https://collections.library.yale.edu/iiif/2/1006194/1650,300,800,500/full/0/default.jpg) | `1650,300,800,500` | 800 × 500 |
| [Row 1 context](https://collections.library.yale.edu/iiif/2/1006194/350,350,2000,190/full/0/default.jpg) | `350,350,2000,190` | 2000 × 190 |
| [Row 2 context](https://collections.library.yale.edu/iiif/2/1006194/350,430,2000,190/full/0/default.jpg) | `350,430,2000,190` | 2000 × 190 |
| [Row 3 context](https://collections.library.yale.edu/iiif/2/1006194/350,525,2000,175/full/0/default.jpg) | `350,525,2000,175` | 2000 × 175 |
| [Row 4 context](https://collections.library.yale.edu/iiif/2/1006194/350,600,2000,190/full/0/default.jpg) | `350,600,2000,190` | 2000 × 190 |

The JSON pins responses retrieved for every selected image/font URL and the
service info URL, including byte lengths and returned dimensions. The source catalog and original
checklist retain edition credits, reuse terms, alphabet labels and file-line
scope. Direct local retrieval of the reference HTML returned HTTP 406; its
Table 3 text was inspected through the web reader and has no invented raw-body
pin. Hashes identify this pass's response bytes, not permanent editions or
independent interpretations. Only text, source links and metadata are published.

## Reproduce the offline checks

From the repository root, standard-library Python:

```sh
python3 scripts/build_67r_review.py --check research/panel-regions/f67r-p0-review.json
python3 - <<'PY'
import hashlib, json
from pathlib import Path
from scripts.audit_transliterations import load_sources
p = json.loads(Path('research/panel-regions/f67r-upper-row-inspection.json').read_bytes())
for path, expected in p['input_sha256'].items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected
assert [r['locus_key'] for r in p['records']] == ['f67r1.1', 'f67r1.2', 'f67r1.3', 'f67r1.4']
sources = {s['id']: (s, d) for s, d in load_sources()}
windows = {w['id']: w for w in p['response_fingerprints']}
for index, row in enumerate(p['records'], 1):
    assert row['proposed_physical_row_top_to_bottom'] == index
    assert row['association_status'] == 'supported_by_visible_anchors'
    assert not row['every_glyph_verified'] and not row['word_divisions_adjudicated']
    assert not row['usable_as_verified_corpus_join'] and row['source_reading_preference'] is None
    assert [r['source_id'] for r in row['source_readings']] == ['ZL3b', 'IT2a']
    for reading in row['source_readings']:
        source, document = sources[reading['source_id']]
        expected_source = next(s for s in p['sources'] if s['source_id'] == source['id'])
        assert source['sha256'] == expected_source['sha256']
        locus = next(l for l in document.loci if l.key == row['locus_key'])
        assert locus.present and locus.kind == 'P0'
        assert (locus.identifier, locus.line_number, locus.text) == (reading['locus_identifier'], reading['source_file_line'], reading['native_text'])
    assert row['context_window_id'] in windows
for window in windows.values():
    if 'native_context_xywh' in window:
        x, y, w, h = window['native_context_xywh']
        assert x >= 0 and y >= 0 and w > 0 and h > 0 and x+w <= 4972 and y+h <= 3738
        assert window['returned_dimensions'] == [w, h]
assert not p['usable_as_verified_corpus_join'] and not p['usable_for_statistical_evaluation']
print('Four targets, eight literal readings, frozen inputs and provisional bounds reproduce.')
PY
```

For online checks, retrieve each exact fingerprint URL and compare its byte
length, SHA-256 and declared dimensions. A changed image needs fresh visual
review. Bounds/source reconstruction verifies metadata, not the interpretation.
Independent region/glyph review and an explicit crosswalk decision remain
necessary before any verified corpus join. The pilot's 67r mapping gap stays
open; these four rows supply no language, mechanism, decipherment or translation.
