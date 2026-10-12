# Processed 1r views retain ambiguity around the selected repeat

The three fixed processed 1r JPEGs make broad writing strokes more distinct
than the ordinary reference in this nonblind inspection, but also emphasize
large leaf-like background forms across the proposed repeat neighborhood.
Low caps, rounded marks and curving endings remain visible; their small
contours are not cleanly separable from every intersecting form or colored
spot. **Exact glyph equality remains unresolved.** No source preference,
physical word boundary or transcription correction follows.

This follows the accepted [immediate-repeat image case](IMMEDIATE_REPEAT_IMAGES.md)
at `f1r.15` and the accepted [MSI source intake](../image-index/MULTISPECTRAL_INTAKE.md).
It advances the practical source/glyph review question without introducing a
new statistic, independent sample, decipherment or translation.

## Fixed target, sources and exposure

The [plan](MSI_FIRST_REPEAT_PLAN.md) was published and its remote head verified
at `a67530863b38a4f98b3bbd72429d1da96d6fc012` before these new detailed views.
It fixes the already selected paired-agreement case and **all three selected
processed 1r JPEGs**, plus the accepted full Yale 1r reference. The TIFFs, raw
band archive, other folios and complete release are outside this inspection.
No favorable source or case was substituted after looking.

Native readings, repeat classifications, previous notes, the release article,
Read Me and full images were already exposed. One AI assistant inspected these
views on 12 October 2026; this is not independent human paleography or untouched
evaluation. Encoded repeat coordinates stay **ZL 7–8 / IT 6–7**, with all eight
original source/policy vectors unchanged in the pinned selection. They do not
identify physical glyph boxes or reconcile earlier segmentation differences.

The [observation ledger](msi_first_repeat_review.json) retains seven exact
source/selection/review/viewer/plan fingerprints, all four original file
identities/metadata, sixteen viewport windows, each view's observations and
limits, and false/null review/correction flags. Exact provider filenames and
processing strings remain in the source record and ledger.

| View | Original file identity | Observation in this inspection |
| --- | --- | --- |
| A | [1rBOSvrVJfpEKbLVsr85ijN26bwsQCHbp](https://drive.google.com/file/d/1rBOSvrVJfpEKbLVsr85ijN26bwsQCHbp/view) | Strong blue/dark strokes on a yellow-grey textured field; broad caps and curves remain visible, while an oblique leaf-like band intersects the proposed neighborhood. Small strokes merge with some background edges. |
| B | [1nmibtm1NpKHHwZ9oCQtByGj-btBu0pt9](https://drive.google.com/file/d/1nmibtm1NpKHHwZ9oCQtByGj-btBu0pt9/view) | Blue-violet strokes, green/grey mottling and maroon/purple broad forms. Low caps and ends can be followed, but small-edge separation is less bright in places; the intersecting form persists. |
| C | [1J8Z2kaTZgLJ972hoAKIcTuEhEmqWIMXt](https://drive.google.com/file/d/1J8Z2kaTZgLJ972hoAKIcTuEhEmqWIMXt/view) | Blue writing with colored fringes and spots on a yellow/green textured field. Broad outlines persist; a colored edge or isolated spot cannot be accepted as a separately attributable extra glyph stroke. |
| Ordinary Yale | [1r, image 1006076](https://collections.library.yale.edu/catalog/2002046?child_oid=1006076) | Uneven brown writing, fading and green/brown background marks. The neighboring low capped groups have broad correspondence with differing small contours, retaining the accepted case's uncertainty. |

Colors describe these display outputs, not original ink. The processing
differences are not an objective visibility ranking. The three processed views
are dependent representations of one surface; the ordinary image is a separate
reference capture of that same surface.

## Context and provisional correspondence

Full-frame context precedes the detail views. The third main writing block,
its row sequence and neighboring level patterns allow a provisional association
with the accepted `f1r.15` proposal. The preceding proposed `f1r.14` level has
a different opening/right-hand sequence; the following proposed `f1r.16` has
a taller central sequence and a different opening. Broad low capped/rounded
forms at the target are compatible with the known repeat.

This does not uniquely assign every small trace to either encoded slot. The
large oblique leaf-like form crosses portions of the terminal neighborhood
in all three processings. No new claim attributes those pixels to a particular
side, original pigment, restored letter or physical word. Fine contours,
possible touching/extra strokes and segmentation remain uncertain. Matching
dimensions and similar framing do not establish capture registration.

## Reproduce the recorded windows

Use the accepted [local viewer](../image-index/msi-viewer/README.md) with its
complete verified packet. No viewer code, file bytes or image enhancement was
changed. Choose **Stored array**. All processed sources have EXIF 1; the Yale
reference has no orientation tag. The observed canvas was **565×540 CSS pixels**.
Each recorded rectangle encloses the visible source pixels and is clipped to
its own original dimensions, with upper-left origin. These are viewport
envelopes, not glyph/word masks or a cross-capture transform.

| Source and view | Zoom | Center indices x,y | Stored-pixel rectangle x,y,width,height |
| --- | ---: | --- | --- |
| Yale full frame | 1 | 1485.5, 1882.5 | 0, 0, 2972, 3766 |
| Yale row context | 1.75 | 1500, 1850 | 374, 774, 2253, 2153 |
| Yale wide detail | 5 | 1850, 1900 | 1456, 1523, 789, 755 |
| Yale fine detail | 7.5 | 1850, 1900 | 1587, 1649, 527, 503 |
| Each MSI full frame | 1 | 3065.5, 4087.5 | 0, 0, 6132, 8176 |
| Each MSI row context | 2 | 2200, 4000 | 61, 1956, 4279, 4089 |
| Each MSI wide detail | 5 | 3400, 4075 | 2545, 3257, 1711, 1637 |
| Each MSI fine detail | 10 | 3100, 4075 | 2672, 3666, 857, 819 |

The same numerical windows were chosen separately after inspecting each MSI
frame. They are not independently verified pixel correspondences. Viewport
sizes affect the visible envelope; use the ledger's source rectangles when
reviewing on a different screen. Browser decoding, resampling and color
management are display conditions, not calibrated multispectral measurements.

The envelope uses the fit scale multiplied by zoom and a continuous pixel
center of `center_index + 0.5`; floor lower bounds, ceil upper bounds, and clip
to the original image. Preliminary wider/narrower pan attempts were inspected
while locating context, and no exposure is hidden. The table retains the final
overview/context/wide/fine sequence used for all fixed views. Numeric center
values were followed by an actual zoom redraw before retaining captures.

## Verification and remaining review

Complete original-cache/packet checks pass before inspection and again after
the observations. Every ledger source identity, original byte hash/length,
dimension/orientation and URL agrees with the accepted source record. All
sixteen windows are within their own image bounds and reproduce the recorded
viewport envelope. Every pinned input is unchanged. The accepted repeat
selection and review still verify; source/slot vectors and statistical inputs
are unchanged. No new tests or statistical producer are needed for this
documentation/observation addition.

```sh
python3 scripts/check_msi_intake.py --cache /path/to/original-cache
python3 scripts/build_msi_viewer.py --cache /path/to/original-cache --check /path/to/local-packet
python3 scripts/select_immediate_repeat_images.py --check research/transliteration/immediate_repeat_image_selection.json
python3 scripts/verify_immediate_repeat_images.py
```

For the new ledger's pins, source metadata and sixteen viewport envelopes:

```sh
python3 - <<'PY'
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as F
from math import floor, ceil
from scripts.paragraph_token_corpus import strict_json
from scripts.audit_eva_token_coverage import encoded
r = strict_json(Path('research/transliteration/msi_first_repeat_review.json').read_bytes())
for name, expected in r['input_sha256'].items():
    assert sha256(Path(name).read_bytes()).hexdigest() == expected
s = strict_json(Path('research/image-index/multispectral-intake.json').read_bytes())
expected = {x['file_id']: (x['metadata'], x['view_url'], x['local_filename'])
            for x in s['selected_images'] if x['source_side'] == '1r'}
y = next(x for x in s['yale_references'] if x['side'] == '1r')
expected['yale-1r'] = (y['metadata'], y['index_row']['catalog_image_url'], y['local_filename'])
assert len(r['views']) == 4 and {x['id'] for x in r['views']} == set(expected)
count = 0
for view in r['views']:
    metadata, url, filename = expected[view['id']]
    assert encoded(view['original_metadata']) == encoded(metadata)
    assert (view['source_url'], view['local_filename']) == (url, filename)
    w, h = metadata['header_dimensions']
    assert len(view['review_windows']) == 4
    for window in view['review_windows']:
        cw, ch = window['canvas_css_pixels']
        cx, cy = (F(str(x)) for x in window['center_pixel_indices'])
        scale = min(F(cw, w), F(ch, h)) * F(str(window['zoom']))
        x = max(0, floor(cx + F(1, 2) - F(cw, 2) / scale))
        y = max(0, floor(cy + F(1, 2) - F(ch, 2) / scale))
        right = min(w, ceil(cx + F(1, 2) + F(cw, 2) / scale))
        bottom = min(h, ceil(cy + F(1, 2) + F(ch, 2) / scale))
        assert window['visible_native_rectangle'] == [x, y, right-x, bottom-y]
        assert 0 <= x < right <= w and 0 <= y < bottom <= h
        count += 1
print('Verified pins, source metadata and', count, 'viewport envelopes.')
PY
```

These checks establish byte identity and structural/bounds consistency, not
visual truth. Original JPEGs, full source responses, generated packet and
inspection screenshots remain local. The ledger is a manual observation
record, with exact inputs/windows for another observer to inspect.

Next, qualified independent examination should compare the complete row and
neighbors across all fixed processings, retain competing boundaries/readings,
and assess original capture/processing provenance. Strong contrast alone does
not certify ink-side attribution or glyph equality. No source correction,
statistical use, foliation alias, decipherment or English reading is accepted.
