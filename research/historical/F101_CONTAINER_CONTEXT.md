# f101 file containers and their shared scan references

The modern IVTFF convention groups `f101r1`/`f101r2` text under `f101r`, and
`f101v1`/`f101v2` text under `f101v`. Its file-use recommendation explains how
these modern names can differ from the historical names retained in the
[fixed four-pair comparison](F101_RECORD_CANDIDATES.md). Physical panel/locus
correspondence remains unresolved. All original identifiers and the parent's
223 exact-page comparisons remain intact.

## Publisher convention

René Zandbergen's [IVTFF specification](https://voynich.nu/software/ivtt/IVTFF_format.pdf)
was checked as document issue 2.0.2, dated 8 July 2025, describing file format
2.0.1. The pinned 39-page copy has SHA-256
`7ac9c4a82064763cac8767cca6f661cc4e1b4503ab9342acc03032ddb6939d49`.
Printed pages 32 and 38 were rendered and visually read: page 32 supplies the
column legend, and page 38 contains all six f101 entries. The current publisher
PDF text agrees with those entries; a new raw-download identity is not claimed.

| Page name | Publisher file-use entry | Text collected under | Petersen page-number column |
| --- | --- | --- | --- |
| `f101r` | Y | — | 205 |
| `f101r1` | NO | `f101r` | 205 |
| `f101r2` | NO | `f101r` | 205 |
| `f101v` | Y | — | Blank |
| `f101v2` | NO | `f101v` | 206 |
| `f101v1` | NO | `f101v` | 207 |

The column is headed **Use in file?**. A NO entry leaves physical writing
presence undetermined; the comments describe collection under another page
name. Petersen's page numbers occupy a separate column. They do not supply
Yale canvas indices or a general foliation offset.

This is a modern-format convention. The historical 1.6e6 H source retains
`f101r1` and `f101v2` as native record-bearing names. Its `R1`/`R2` unit names
inside `f101v2` are another identifier field, without an assigned physical-panel
mapping. The accepted comparison's 10 and 28 ordered lossy matches remain
source evidence with their original limits; full native bodies and glyphs
have not been adjudicated here.

## All pinned Yale references

The accepted [whole-corpus side-reference audit](../folio-alignment/IMAGE_COVERAGE.md)
links modern `f101r` to one composite scan and `f101v` to two partial scans.
The [record](f101-container-context.json) preserves those complete audit entries,
including both editions' existing counts and every partial/composite flag.
The labels come from the existing pinned manifest index, rather than a new
manifest download or image inspection.

| Modern source side | Exact pinned Yale label | Stable image reference |
| --- | --- | --- |
| `f101r` | 100v and 101r | [1006249](https://collections.library.yale.edu/catalog/2002046?child_oid=1006249) |
| `f101v` | 101v (part) | [1006250](https://collections.library.yale.edu/catalog/2002046?child_oid=1006250) |
| `f101v` | 101v (part) and 102r | [1006251](https://collections.library.yale.edu/catalog/2002046?child_oid=1006251) |

Both source sides retain the audit's shared dependency group
`yale-leaves:100+101+102` and panel-region status `not_assessed`. Keep all three
references and related leaves when planning corpus dependencies. This record
chooses no preferred scan, mask, crop or alignment. The earlier
[f102r1 context](../panel-regions/102R_BOUNDARY_PAIR.md) had already examined the
shared 1006251 scan; this contribution makes no additional manuscript image
observation or independent/blinded verification claim.

## Verify and next work

The record pins the accepted f101 comparison, whole-corpus coverage, label
index and both source catalogs. Reproduce its metadata bindings from the
repository root with the standard library:

```sh
python3 - <<'PY'
from pathlib import Path
import hashlib, json
r = json.loads(Path('research/historical/f101-container-context.json').read_bytes())
for path, expected in r['input_sha256'].items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == expected
coverage = json.loads(Path('research/folio-alignment/transcription-image-coverage.json').read_bytes())
assert r['modern_side_references'] == [p for p in coverage['pages'] if p['page_id'] in {'f101r', 'f101v'}]
labels = json.loads(Path('research/source-audit/manifest-labels.json').read_bytes())
index = {c['id']: c['label']['none'][0] for c in labels['items']}
for page in r['modern_side_references']:
    for canvas in page['canvas_matches']:
        assert index[canvas['canvas_uri']] == canvas['yale_label']
assert r['aliases_applied'] == [] and r['apply_to_statistics'] is False
assert r['physical_regions_verified'] is False and r['new_manuscript_image_observation'] is False
print('Convention-context pins and all three inherited scan references verified.')
PY
```

Documentary entries were checked against the rendered PDF; metadata/code/data
bindings were checked without changing prior reports, source bytes or selection.
The next physical review must retain original native bodies, the related panels
and all partial scans, with exact region and glyph evidence. Every alias,
physical-region and statistical-use decision remains unassigned. Existing
[source credits and reuse notes](../../data/historical/README.md) remain in force;
PDF/manuscript pixels are linked and kept outside the contribution. No language,
decipherment, translation or untouched evaluation follows.
