# Rosette surface: source names and missing paired coverage

Question: can the recovered historical archive fill the paired pilot's missing
rosette text, or is that absence merely a page-name mismatch?

The pinned historical archive contains rosette records under `f85v2`, but none
under its Takahashi code `H`. Modern IT2a has no `fRos` or any of the six
documented constituent-panel headers. Changing a name therefore supplies no H/IT
records in these exact inputs.
Other modern editions contain `fRos`, with different native coverage and
representation. This diagnostic narrows the pilot-corpus gap; it does not change
the [exact-page readiness gate](TRANSCRIPTION_READINESS.md).

## Source conventions and image context

The [1.6e6 publisher release](https://www.ic.unicamp.br/~stolfi/EXPORT/00-EXPORT/98-12-28-interln16e6/),
under its edition-change list, records the renaming of the nine-rosette page from
`f86r4` to `f85v2`. The pinned archive member's `f85v2` header is at physical
line 27,298. Its Identification comments (lines 27,302-27,317) describe a logical
page spanning the six panels named `85v2`, `86r4`, `86r6`, `85v1`, `86r3`, and
`86r5`. This is the historical source's convention, not a rule for truncating
every panel suffix or a verified locus crosswalk.

The [IVTFF specification](https://voynich.nu/software/ivtt/IVTFF_format.pdf),
document issue 2.0.2, section 4.2/Figure 2 on printed page 12, calls the shared
85v/86r drawing `fRos`. Its appendix on printed pages 36-37 lists the constituent
panel names separately and assigns their text to `fRos`. Both relevant rendered
pages were checked; the retrieved PDF matches the accepted SHA-256
`7ac9c4a82064763cac8767cca6f661cc4e1b4503ab9342acc03032ddb6939d49`.
This extends the [existing convention note](NATIVE_PAGE_CONVENTIONS.md) with
historical source coverage; it does not establish historical/modern record identity.

The pinned [Yale index](../image-index/canvases.csv) and original
[pilot inventory](inventory.json) retain image
[1006231, labeled 85v and 86r (foldout)](https://collections.library.yale.edu/catalog/2002046?child_oid=1006231).
The script checks their shared canvas, both explicit sides, and manifest identity.
This is the existing coarse carrier reference. No new image inspection, pixel
boundary, glyph adjudication, physical collation, or text-region mapping is added.
Keep both leaves and their related scans together in dependency review.

## Reproducible file observations

The [complete report](rosette-source-coverage.json) uses the accepted historical
and IVTFF readers after checking archive/member and modern-source byte pins.
It queries `fRos` and all six documented panel names **exactly**, preserving absent headers, nonexistent
records, native locus types, historical unit case/line suffixes, source order,
transcriber codes, and physical source-line references. No text normalization
or body-string matching is performed.

| Historical 1.6e6 native page | Records by code | Distinct unit/line keys across codes |
| --- | --- | ---: |
| `f85v2` | U: 99; V: 84; H: 0 | 117 |
| `f86r4`, `f86r6`, `f85v1`, `f86r3`, `f86r5` | No records under any of these names; H: 0 | 0 each |
| `fRos` | No records; H: 0 | 0 |

The 183 `f85v2` records are not 183 separate native locations: U and V share
66 exact unit/line keys, with 33 U-only and 18 V-only keys. The report retains
every locator and physical line. Shared keys do not establish equal readings,
independent authorship, or physical manuscript lines. Historical unit keys are
not mapped to modern locus numbers or kinds.

| Modern pinned edition | `fRos` header | Present native loci | Native kinds |
| --- | --- | ---: | --- |
| ZL3b | Present | 160 | 137 L0, 11 Cc, 11 Pb, 1 Ca |
| IT2a | Absent | 0 | None |
| GC2a | Present | 148 | 125 L0, 11 Cc, 11 Pb, 1 Ca |
| RF1b full | Present | 160 | 137 L0, 11 Cc, 11 Pb, 1 Ca |
| RF1b basic | Present | 160 | 137 L0, 11 Cc, 11 Pb, 1 Ca |

All five lack every exact constituent-panel header. None of the present modern
`fRos` loci is P0. The report includes all present/native-kind identifiers,
rather than silently taking only ordinary paragraph rows. It does not infer
that a count difference represents omitted manuscript glyphs or a transcription
error. GC's v101 representation and the Eva exports require separately declared
comparison rules. RF derives from ZL/GC, as recorded in the
[reference-variant audit](../transcriptions/REFERENCE_VARIANTS.md); those
agreements cannot supply independent confirmation.

## Reproduce, limits, and next test

From the repository root, Python 3.10 or later, standard library only:

```sh
python3 scripts/audit_rosette_coverage.py --check research/pilot/rosette-source-coverage.json
python3 scripts/audit_rosette_coverage.py --output /tmp/rosette-source-coverage.json
python3 -m unittest tests.test_rosette_coverage -v
```

The report pins its metadata and reader/implementation files, plus every source
identity. The CLI rejects writes over those inputs, including linked paths, and
does not replace an existing output when report verification fails. Synthetic
tests distinguish records from shared source keys, retain unit case and line
suffixes, isolate exact page names, preserve header/nonexistent-record distinctions,
and reject a changed or isolated carrier declaration.

This is an already exposed source-coverage diagnostic. It does not prove the
absence of a transcription elsewhere, equate these editions, authorize U/V as
Takahashi replacements, join historical and modern loci, or validate a reading.
The output keeps `apply_to_statistics: false` and a null verified crosswalk.
Source archives, credits, and permissions remain in the
[accepted historical catalog](../../data/historical/README.md); source PDF and
image bytes are linked, not redistributed by this contribution.

Next, select a documented rosette transcription and register native locus-to-image
region checks appropriate to circular text and labels. Compare ZL and GC only
under explicit representation/segmentation rules, preserve disagreements, and
review glyphs on the source image. A historical comparison additionally needs
an explicit locus correspondence. Resolve that work before changing the paired
pilot or freezing a decipherment candidate's input and evaluation units.
