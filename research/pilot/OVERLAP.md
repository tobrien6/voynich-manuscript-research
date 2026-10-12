# Initial pilot inventories: image and dependency overlap

Question: how many source views and conservative sampling components are
represented by the three initial ten-record inventories?

This reconciles the [section-beginning inventory](INVENTORY.md),
[boundary survey](../boundary-pilot/INVENTORY.md), and
[standalone-recto inventory](../PILOT_INVENTORY.md). It uses their recorded
references, not a new inspection of their images. The
[complete report](initial-inventory-overlap.json) pins each metadata file and
observation document by SHA-256, verifies image/canvas/label identity against
the rebuilt Yale index, and applies the
[transitive dependency components](../folio-alignment/IMAGE_COVERAGE.md).

## Recorded findings

The three inventories contain **30 records**, referencing **15 distinct Yale
canvases** and **14 conservative image-dependency components**. Each inventory
by itself contains ten distinct canvases and ten distinct components. The
components are metadata-based grouping hints, not independently validated
manuscript samples.

| Inventory pair | Same canvases | Same dependency components |
| --- | ---: | ---: |
| Section beginnings / boundary survey | 6 | 6 |
| Section beginnings / standalone rectos | 6 | 6 |
| Boundary survey / standalone rectos | 9 | 10 |

The last row matters: the standalone-recto rule selects 100r (image 1006248),
while the boundary survey selects 102r in the scan labeled `101v (part) and
102r` (image 1006251). They are distinct images within the same conservative
`yale-leaves:100+101+102` component. Thus these inventories offer different
views, while covering the same ten dependency components. Do not count that
change as an additional independent evaluation component.

The Rosettes scan, image 1006231, is also retained once in the union. Its three
inventory references preserve targets `85v`, `86r`, and the standalone
inventory's full compound label. The last inventory selects the whole canvas;
the report deliberately assigns it no invented single-side target. Different
target names do not turn one image into separate samples or establish panel
alignment.

The union's labels explicitly name 17 leaf numbers, including 101 within a
shared partial view. This does not mean 17 complete leaves were inspected.
Recorded image observations can support review of earlier descriptions, but
reused canvases do not add new manuscript material.

## Reproduce and validation

Python 3.10 or later, standard library only. Use the public manifest matching
the repository's recorded snapshot; images are not fetched or redistributed.

```sh
curl -fsSL https://collections.library.yale.edu/manifests/2002046 -o /tmp/voynich-manifest.json
python3 scripts/audit_pilot_overlap.py --manifest /tmp/voynich-manifest.json \
  --check research/pilot/initial-inventory-overlap.json
python3 -m unittest tests.test_pilot_overlap -v
```

Use `--output PATH` to regenerate the report. The loader requires all ten
declared records from each inventory and rejects repeated images within an
inventory, changed source/index identity, or targets not explicitly named by
the selected image's label. Tests verify the actual 30/15/14 reconciliation,
the 9-image/10-component distinction, compound-target preservation, and
refusal of shortened, duplicated, or misidentified inventories.

## Scope for later evaluation

This is an audit of three existing records, not a complete exposure ledger.
Later image work, transcription inspection, and candidate development require
their own exposure declarations. Shared components alone cannot prove every
relationship, actual viewing history, or the absence of previous exposure.

No development/evaluation partition or freeze is assigned. Before selecting
a candidate's units, preserve the original inventory references, combine
shared leaves/scans, and review text-region mappings. Declare relevant prior
exposure under the [split format](../evaluation/SPLIT_FORMAT.md), with the
claim's actual scope. Do not convert these previously documented inventories
into a claim of untouched material.
