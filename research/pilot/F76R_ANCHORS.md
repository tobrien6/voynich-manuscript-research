# Provisional native-locus image anchors on f76r

All three frozen anchors have plausible row associations in Yale's f76r image.
This supplies review windows and both native source texts for a later comparison
interface. It does **not** establish an accepted glyph or physical-line mapping.
The first and median native readings still disagree between editions.

## Fixed selection and source identity

The [plan](F76R_ANCHOR_PLAN.md), [selector](../../scripts/select_f76r_anchors.py),
and [complete source selection](f76r-anchor-selection.json) were committed in
`54007c5479a49652c8233b841234eec4b337841f` before further image inspection.
There are 38 shared present P0 keys with regular `@`, `+`, or `*` locators.
Numerical ordering and the lower-median rule select ranks 0, 18, and 37:
`f76r.1`, `f76r.35`, and `f76r.56`. No agreement or readability filter was used.

The selection also retains all 18 excluded page keys, both source identifiers,
and each anchor's immediate native neighbors. Nine `L0` margin records and nine
`=P0` records account for those exclusions. They are not absent manuscript rows.
A locus number and the selected rank cannot be treated as a physical row number.

ZL3b (`Eva-`) and IT2a (`EvaT`) remain distinct, related editions with the exact
source bytes, versions, credits, and CC0 transliteration terms in the
[source catalog](../../data/transliterations.json). Native text below is the
accepted reader's logical locus text, including annotation and uncertainty;
the source-file layout and physical file line numbers remain traceable.

## Image review

The [Yale catalog image](https://collections.library.yale.edu/catalog/2002046?child_oid=1006210)
has image ID `1006210`, label `76r`, and a single-side canvas. The accepted
manifest/index and live image-service metadata both give 2793 by 3769 native
pixels. The [review JSON](f76r-anchor-review.json) records those identities, the
four inspected derivative fingerprints/dimensions, service metadata digest,
complete native contexts, observations, provisional association basis, and
remaining uncertainty.

Regions use `[x, y, width, height]` in native pixels, with origin at the upper
left. These are inspection windows including neighboring strokes or rows,
not verified glyph/token bounding boxes. The windows were chosen during image
inspection, after the native locus selections were frozen. Tool displays may
resize images; the coordinates refer to their original native-pixel requests.

| Frozen key | Proposed placement | Native review region | Status |
| --- | --- | --- | --- |
| f76r.1 | First main-text row with a large left flourish | [240, 120, 2200, 330] | Provisional |
| f76r.35 | Near the bottom of the upper dense block, between proposed f76r.34 and f76r.36 | [240, 1630, 2190, 210] | Provisional |
| f76r.56 | Short bottommost main-text row | [230, 2870, 2210, 220] | Provisional |

At the [first anchor](https://collections.library.yale.edu/iiif/2/1006210/240,120,2200,330/full/0/default.jpg),
the large raised left form, distributed tall forms, and low upright-rich group
near the right support the proposed row association. ZL begins `potchokor`
while IT begins `potchokar`; ZL ends `sain.as,y`, while IT ends `sain.?sy`.
These native reading and spacing differences remain unresolved.

At the [median anchor](https://collections.library.yale.edu/iiif/2/1006210/240,1630,2190,210/full/0/default.jpg),
the proposed row has an upright-rich beginning and two complex tall forms at
its far-right end. Those forms and the source-record order support association
with the shared ending `qol.chcthy.chckhy`. ZL starts `sain`, while IT starts
`saiin`; this review does not decide the visible stroke count. The neighboring
ZL `qok[a:o]l` alternative also remains native uncertainty.

At the [last anchor](https://collections.library.yale.edu/iiif/2/1006210/230,2870,2210,220/full/0/default.jpg),
the short bottom row leaves wide blank space to its right and below. Its
long-stem/upright-rich first group and alternating short/larger groups are
compatible with both editions' identical
`qokaiin.ol.shedy.qokeey.or.shdy<$>`. Agreement does not provide independent
glyph ground truth or certify all source word boundaries.

The native full/full endpoint returned HTTP 504. Inspection used the official
1334-by-1800 overview and the three native-resolution region derivatives.
Their actual bitmap dimensions were checked with macOS `sips`; the overview
digest matches the earlier inventory derivative. No full-resolution whole-page
inspection is claimed. Images remain local; only official Yale links and
provenance are committed.

## Verification and next review

From the repository root:

```sh
python3 scripts/select_f76r_anchors.py --check research/pilot/f76r-anchor-selection.json
python3 scripts/verify_f76r_review.py
python3 -m unittest discover -s tests -p 'test_f76r_*.py' -v
```

For optional byte verification, download the four URLs and `info.json` into a
local directory using the `local_filename` values recorded in the JSON, then
run `python3 scripts/verify_f76r_review.py --image-dir DIRECTORY`. Local pixels
are not required for the offline source/metadata check. The verifier checks
geometry declarations, byte digests, and optional local bitmap header dimensions
using the accepted prefix-review helper; it does not decode pixels or validate
visual judgments. The recorded pre-inspection commit is a chronology
reference for human review, not certification of an unexposed sample.

Thirteen focused tests cover deterministic selection, lower-median ordering,
source-specific exclusions, preserved native uncertainty/context, complete
anchor coverage, image identities and native bounds, changed local bytes/headers,
unsupported confirmation/correction claims, and retention of an unresolved
attempt. The current selection reproduces and all five local inspected files
(four bitmaps and service metadata) match their recorded digests.

This project already inspected f76r in its original inventory, and this chat
analyzed both whole-corpus sources before selecting these anchors. The current
image inspection adds exposure. The three anchors share one image and one
observer; they are not independent manuscript samples or untouched evaluation.
No source correction, glyph adjudication, decipherment, or translation follows.

A [second AI-assisted comparison](F76R_SECOND_ROW_CHECK.md) retains compatible
row-level outcomes for all three windows while preserving the initial/median
reading disagreements. It is non-blind and does not establish model independence,
human validation, accepted mappings, or untouched evaluation material.

Next, an independent observer should check each proposed region against both
complete native loci and their neighbors, record competing placements, and
evaluate every source disagreement before any accepted mapping. Other f76r
loci and all token-level boxes remain outside this pilot.
