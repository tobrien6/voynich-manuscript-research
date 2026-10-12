# Provisional f89v bottom-label context

The [inspection record](f89v-context.json) proposes Yale image **1006234** as
context for the historical native `f89v2` container. Its three illustration
bands and two intervening text blocks agree with the attributed source layout.
This is a single observer's provisional association. **No exact locus, glyph
reading, panel crosswalk or physical text-presence decision is verified.** It
cannot serve as a verified image/text join or statistical evaluation sample.

The [explicit nonexistent-locus note](../transcriptions/NONEXISTENT_LOCUS.md)
distinguishes IT2a/GC2a's `!` annotation at modern `f89v2.26` from omission of
that key in the other exports. This packet adds image context without deciding
which visible marks, if any, correspond to that modern locator.

## Source containers and images

The credited [Stolfi interlinear release](../../data/historical/interlinear-16e6.json)
describes its `f89v2` page as the two outer verso panels, `f89v3` and `f89v2`,
with paragraph lines crossing their fold. The member's page description starts
at source-file line 29983; the panel explanation is at lines 29995–29997.
The bottom label unit starts at line 30257 and reports five labels and four
plants at line 30261. These are historical source assertions, not an image
annotation made by this packet. The archive/member and catalog hashes are
retained in the JSON record.

The [IVTFF specification](https://www.voynich.nu/software/ivtt/IVTFF_format.pdf),
issue 2.0.2, section 4.2 (printed pages 11–12), numbers verso panels away from
the binding, right to left. It also allows continuous writing to cross a
crease without creating a separate transcription page. That convention helps
explain the container, but does not independently verify this image mapping.

Every canvas in the pinned [Yale index](../image-index/canvases.csv) whose label
explicitly names `89v` was selected before the first image view. Both were
inspected, including the composite image that also exposes `90r`:

| Yale image | Pinned label | Native dimensions | Single-observer full-view observation |
| --- | --- | --- | --- |
| [1006234](https://collections.library.yale.edu/catalog/2002046?child_oid=1006234) | `89v (part)` | 4204 × 3809 | Three illustration bands and two text blocks; three container-like drawings near the left of the main field. The bottom band has four separated plant-like assemblages beside a blue container. |
| [1006235](https://collections.library.yale.edu/catalog/2002046?child_oid=1006235) | `89v (part) and 90r` | 7796 × 3761 | A composite opening: container/fragment bands and intervening writing toward the left; larger plant-like drawings and writing toward the center and right. |

The coarse catalog labels do not assign individual transcription panels. The
three-band match favors 1006234 as a context candidate; it does not locate
every `f89v2` line or prove the boundaries of the two reported physical panels.

## Bottom group and faint traces

The historical bottom unit has six H and six U envelopes (`0`, `1`, `2`, `3a`,
`3b`, `4`), four L envelopes (`0`, `1`, `2`, `3b`) and four V envelopes (`0`,
`1`, `2`, `4`). The native locators are retained without flattening `3a`/`3b`
or manufacturing aliases to modern numbers. Source-file line 30289, immediately
before H/U `3a`, suggests possible writing showing through from the other side.
That attributed suggestion remains unconfirmed.

After viewing both full derivatives, the observer inspected the historical
page descriptions and that comment, then selected these context windows on
1006234. Coordinates are native image pixels, `x,y,width,height`:

| Window | Native bounds | Inspected derivative |
| --- | --- | --- |
| [Bottom-band context](https://collections.library.yale.edu/iiif/2/1006234/200,2200,3950,1609/!1800,1800/0/default.jpg) | `200,2200,3950,1609` | 1800 × 733 |
| [Native-pixel context](https://collections.library.yale.edu/iiif/2/1006234/1800,2600,1300,1000/full/0/default.jpg) | `1800,2600,1300,1000` | 1300 × 1000 |

Clearer brown writing patches and much fainter traces are visible among the
illustrated fragments. Their origin and correspondence to historical `3a`/`3b`
or modern `26` are unresolved. Neither window is an exact locus box. The
native-pixel window preserves retrieved image resolution, without sharpening,
contrast changes, invented marks or a glyph transcription.

The [JSON record](f89v-context.json) pins the manifest, index, info responses,
full derivatives and both windows. The JPEGs and format PDF remain local;
this contribution publishes source links, metadata and original observations.
Hashes identify the retrieved bytes, not an independent reading, permanent
image edition or reuse license.

A [2026-10-12 recheck](https://github.com/tobrien6/voynich-manuscript-research/pull/129#pullrequestreview-5487471227)
observed a second 887-byte response for `1006235/info.json`, with SHA-256
`7086ed9f93a1b124c724481d5d2fcecd22c15c97d32da0dad20696c40184b83a`.
Comparing the saved responses shows only a change in the profile's format-list
order, from `tif,jpg,gif,png` to `jpg,tif,gif,png`; all other parsed JSON matches.
The original response and its recorded pin remain preserved, and the maintainer
also retrieved bytes matching that original pin. All four image derivatives
still match their recorded hashes and dimensions. The JSON retains both
metadata identities; this variation establishes no changed pixels or stronger
panel/locus mapping.

## Exposure, dependencies and review

Before image inspection, this observer had seen the modern source statuses,
the historical H payload, the bottom-unit label/plant count and coarse canvas
metadata. The later crops were selected after source-informed full views.
This is nonblind exploration with no untouched evaluation claim and no
independent observer. Both crops are derivatives of one canvas. The two full
views expose portions of the same folio; the composite also exposes neighboring
`90r`. Carry all this exposure into any later image-dependency or holdout audit.

An independent reviewer should first confirm panel/container placement, then
assign separate precise regions to the historical envelopes using full native
records and both sides where available. Record ambiguity or reject the proposed
association if layout, order or glyphs disagree. Only a separately reviewed
crosswalk may establish whether a modern locator corresponds to any region;
this packet supplies no physical absence/presence or word-division verdict.

## Reproduce the source and bounds checks

From the repository root, standard-library Python:

```sh
python3 - <<'PY'
import csv, hashlib, json
from pathlib import Path
from scripts.audit_historical_interlinear import read_pinned_archive, parse_historical
p = json.loads(Path('research/panel-regions/f89v-context.json').read_text())
c = json.loads(Path('data/historical/interlinear-16e6.json').read_text())
assert hashlib.sha256(Path('data/historical/interlinear-16e6.json').read_bytes()).hexdigest() == p['provenance']['historical_catalog_sha256']
assert hashlib.sha256(Path('research/image-index/canvases.csv').read_bytes()).hexdigest() == p['provenance']['canvas_index_sha256']
member = read_pinned_archive(Path(c['path']).read_bytes(), c)
records, _ = parse_historical(member)
for code, expected in p['source_context']['historical_native_locators_by_transcriber'].items():
    actual = [r.locator for r in records if r.page == 'f89v2' and r.unit == 'L3' and r.transcriber == code]
    assert actual == expected
rows = list(csv.DictReader(Path('research/image-index/canvases.csv').open()))
selected = {r['image_oid']: r for r in rows if '89v' in r['explicit_folio_sides'].split(';')}
assert set(selected) == {r['image_oid'] for r in p['images']}
for image in p['images']:
    row = selected[image['image_oid']]
    assert row['yale_label'] == image['pinned_yale_label']
    assert [int(row['image_width']), int(row['image_height'])] == image['native_dimensions']
for window in p['context_windows']:
    width, height = next(i['native_dimensions'] for i in p['images'] if i['image_oid'] == window['image_oid'])
    x, y, w, h = window['native_xywh']
    assert x >= 0 and y >= 0 and w > 0 and h > 0 and x+w <= width and y+h <= height
assert not p['usable_as_verified_image_text_join'] and not p['usable_for_statistical_evaluation']
assert p['exact_locus_mapping'] is None and not p['verified_panel_mapping']
print('Historical locators, both coarse 89v canvases and provisional bounds verified.')
PY
```

For online byte checks, retrieve the exact URLs in the JSON record locally
and compare SHA-256 and dimensions. A changed derivative requires a fresh
inspection; a matching hash alone does not validate a visual interpretation.
