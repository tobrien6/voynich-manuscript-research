# Native page conventions for the three blocked pilot targets

## Question and source evidence

The [exact-page readiness audit](TRANSCRIPTION_READINESS.md) leaves 67r, 68r,
and the shared 85v/86r scan unresolved. What naming conventions does the
transliteration publisher document for these surfaces?

The accepted [whole-corpus image-reference audit](../folio-alignment/IMAGE_COVERAGE.md)
already establishes their coarse side references. This follow-up adds a pinned
copy identity for the convention source and initial image/orientation checks.
Every native identifier cross-references that audit and retains its unresolved
panel-region status.

R. Zandbergen's [IVTFF specification](https://voynich.nu/software/ivtt/IVTFF_format.pdf),
document issue 2.0.2 dated 8 July 2025, defines recto foldout numbering away
from the binding, from left to right. Section 4.2 and the appendix distinguish
67r/68r containers from their numbered pages. They explicitly name the shared
85v/86r surface `fRos`. Printed pages 11, 12, 35, 36, and 37 were inspected,
including both numbering diagrams. The retrieved PDF SHA-256 is
`7ac9c4a82064763cac8767cca6f661cc4e1b4503ab9342acc03032ddb6939d49`.

| Yale carrier | Native identifiers in documented order | Source locator |
| --- | --- | --- |
| [67r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006194) | `f67r1` at left, `f67r2` at right | Section 4.2; appendix p. 35 |
| [68r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006196) | `f68r1`, `f68r2`, `f68r3` from left to right | Section 4.2; appendix p. 35 |
| [85v and 86r (foldout)](https://collections.library.yale.edu/catalog/2002046?child_oid=1006231) | `fRos` for the entire shared surface | Section 4.2, Figure 2; appendix pp. 36-37 |

These are containment relationships, not interchangeable page identifiers.
The [machine-readable record](native-page-conventions.json) retains the original
inventory target, exact Yale label/canvas, native identifiers, source locations,
edition presence, and the limits of the initial image cross-check. It applies
no mapping to an analysis and supplies no pixel boundaries.

## Direct image observations and corpus checks

The three existing 1,800-pixel-bounded derivatives were inspected again. All
three SHA-256 values match the [original inventory](inventory.json). The
67r/68r scans show binding context at left and layouts consistent with the
documented ordering. The shared scan shows connected circular forms across
the full unfolded surface. The record stores these descriptive observations
separately from the publisher's numbering convention. This is an AI-assisted
initial cross-check; independent review remains pending.
Source conventions and native metadata were read before this inspection, and
the pilot images had already been exposed. This is not a blinded replication.

The existing IVTFF reader verifies native page presence in the pinned inputs:

| Native page | Present ZL3b loci | Present IT2a loci |
| --- | ---: | ---: |
| `f67r1` | 19 | 19 |
| `f67r2` | 74 | 74 |
| `f68r1` | 37 | 37 |
| `f68r2` | 31 | 31 |
| `f68r3` | 22 | 22 |
| `fRos` | 160 | 0; header absent |

Counts include all present locus kinds, rather than only horizontal paragraph
text. Equal counts do not establish equal readings or independent evidence.
The native source comments and identifiers remain unchanged in the original
pinned files. The PDF and Yale images are linked, not redistributed.

## Validation and next test

The record pins the inventory, canvas index, image-index audit, source catalog,
and accepted whole-corpus report by SHA-256. Each referenced canvas/label, native page presence, kind
count, and source digest was checked against those inputs. Source publication
facts and image observations can be reviewed independently through the links
above; copying or cropping the illustrations is unnecessary.

From the repository root, reproduce the native-page presence/count checks with
the existing pinned-source reader:

```sh
python3 - <<'PY'
import hashlib, json
from pathlib import Path
from scripts.audit_transliterations import load_sources
from scripts.audit_pilot_transcriptions import page_summary
record = json.loads(Path('research/pilot/native-page-conventions.json').read_text())
for path, digest in record['input_pins'].items():
    assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest
sources = {source['id']: (source, doc) for source, doc in load_sources()}
for carrier in record['records']:
    for page in carrier['native_pages']:
        for edition, expected in page['edition_presence'].items():
            source, doc = sources[edition]
            actual = page_summary(doc, page['page_id'])
            assert source['sha256'] == expected['source_sha256']
            assert all(actual[key] == expected[key] for key in
                       ('header_present', 'present_loci', 'present_loci_by_kind'))
print('Pinned metadata and all six native page-presence records verified.')
PY
```

This evidence answers the naming-convention question. It does not establish
precise text regions, physical leaf dependencies, glyph agreement, or a complete
paired pilot corpus. In particular, a documented `fRos` correspondence cannot
supply the absent IT2a page. The original exact-page audit retains its three
blockers because its stricter exact-identifier rule has not changed.

Next, independently review the carrier and orientation records, then link
native locus identifiers to actual text regions while preserving shared-image
and cross-panel dependencies. Keep this record's `apply_to_statistics` false
until a separately reviewed corpus selection declares how it uses the
conventions. Do not turn panel order into equal-width crops or presume that
creases separate all writing. No decoding or translation is tested here.

The separate [provisional 67r row proposal](https://github.com/tobrien6/voynich-manuscript-research/pull/44)
tests correspondence between encoded loci and particular image rows. Its scope
is distinct from this naming-convention record. Repeated inspection of the
same public image does not supply independent manuscript evidence.
