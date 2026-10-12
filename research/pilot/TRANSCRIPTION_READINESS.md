# Pilot transcription and image-link readiness

## Question and method

Which of the ten selected [inventory targets](inventory.json) have exact page
identifiers in both pinned ZL3b and IT2a, and which need an explicit mapping
before they can become a source-linked decipherment corpus?

The offline [audit](../../scripts/audit_pilot_transcriptions.py) uses the accepted
IVTFF reader, [source pins](../../data/transliterations.json), and
[Yale canvas index](../image-index/README.md). It verifies source bytes, compares
the inventory's manifest identity with the index audit, and checks each selected
canvas's label, image identifier, and explicitly named sides. The
[complete report](transcription-readiness.json) records hashes of all five
metadata inputs as well as both transcription editions.

The audit requires the original ten targets fixed in `SAMPLING.md`. Empty,
truncated, duplicated, or substituted samples are rejected before checking
coverage. Removing an unresolved target cannot make the completeness gate pass.

An `exact_page_metadata_link` requires the exact `f`-prefixed target identifier
and at least one present locus in both editions, with no shared canvas or
panel-identifier ambiguity. This status is a metadata correspondence requiring
image review; it does not validate glyphs, regions, or physical leaf identity.
Panel identifiers found by exact side-prefix plus a single 1–6 suffix are
reported as **unmapped lexical candidates**. They are never truncated or
included in exact-page counts. No foliation alias is applied.

## Recorded observations

| Inventory target | ZL3b exact-page present loci | IT2a exact-page present loci | Shared present locations | Metadata status |
| --- | ---: | ---: | ---: | --- |
| 1r | 28 | 28 | 28 | Exact page link |
| 2r | 15 | 13 | 13 | Exact page link; two ZL-only locations |
| 67r | 0 | 0 | 0 | Unmapped `f67r1`, `f67r2` candidates |
| 68r | 0 | 0 | 0 | Unmapped `f68r1`, `f68r2`, `f68r3` candidates |
| 75r | 53 | 53 | 53 | Exact page link |
| 76r | 56 | 56 | 56 | Exact page link |
| 85v | 0 | 0 | 0 | Shared 85v/86r canvas; exact page absent |
| 87r | 16 | 16 | 16 | Exact page link |
| 88r | 31 | 31 | 31 | Exact page link |
| 103r | 54 | 54 | 54 | Exact page link |

**Seven targets have exact metadata links, containing 253 ZL3b loci, 251 IT2a
loci, and 251 shared present locations. Three targets remain blocked.** Counts
include every present locus kind, preserving explicit nonexistent records,
edition-only locations, and shared locations whose kind or locator differs.
A shared location is identified by page and locus number; matching identifiers
do not prove equal glyph readings or independent observations.

The ZL3b page header `fRos` has 160 present loci. IT2a has no `fRos` header.
The report retains this special identifier separately with no assigned pilot
mapping. It does not substitute `fRos` for `85v` or conclude that the physical
manuscript lacks text. A documented convention and image-region review must
establish any correspondence before those loci enter the selected corpus.

## Reproduce and validate

Python 3.10 or later; standard library only; no downloads or image inspection
are performed. Source material and credits remain in the existing pinned files.

```sh
python3 scripts/audit_pilot_transcriptions.py --output research/pilot/transcription-readiness.json
python3 scripts/audit_pilot_transcriptions.py --check research/pilot/transcription-readiness.json
python3 scripts/audit_pilot_transcriptions.py --check research/pilot/transcription-readiness.json --require-complete
python3 -m unittest discover -s tests -p 'test_pilot_transcriptions.py'
```

The first two commands succeed. The third returns **2** because the three
blocked targets remain in the report. Recomputing this audit successfully is
different from having a complete mapped corpus. Invalid input or a changed
committed report returns 1. The default permits an incomplete diagnostic
report; consumers requiring full coverage must request `--require-complete`.

Synthetic tests cover differing locus kinds/locators, nonexistent and missing
records, empty page headers, panel-candidate isolation, shared scans, duplicate
targets, changed sampling targets, CLI failure distinctions, and inconsistent
image metadata. The committed real report can be
reproduced offline against the exact recorded input hashes.

## Limits and next test

This audit advances the pilot-corpus milestone by identifying the exact work
needed before joining images to text or freezing a split. It chooses no
development/evaluation partition and tests no decoding mechanism. The original
inventory inspected every selected image, and accepted full-corpus baselines
already explored public text. Those exposures must remain disclosed; the
seven exact links are not untouched evaluation material.

Next, review documented edition conventions against the 67r, 68r, and shared
85v/86r images, retain source page identifiers and every relevant canvas, and
record the region/panel mappings explicitly. Include opposite sides and related
foldout panels in dependency review before a real split. Do not obtain a
nominally complete pilot by dropping the three blocked targets: that would
omit the selected astronomical diagrams and cosmological foldout and change
the original six-section sampling rule.

The follow-up [native page convention record](NATIVE_PAGE_CONVENTIONS.md) now
documents the publisher's container/panel distinction and the `fRos` name for
the shared surface. It supplies an initial source/image cross-check, with
independent review and precise text regions still pending. It does not change
this audit's exact-identifier rule or fill IT2a's absent `fRos` page.
