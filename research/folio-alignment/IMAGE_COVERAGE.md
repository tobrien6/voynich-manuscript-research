# Whole-corpus transcription image references

Question: which page identifiers in the pinned ZL3b/IT2a sources can be linked
to Yale's labels, and which source views require dependent sampling units?

This audit adds a documented IVTFF naming layer to the existing strict
[folio-side lookup](README.md). It preserves three different claims:

1. A plain folio request is supported by the strict lookup.
2. A transcription page has a documented **coarse side reference** with
   matching Yale label metadata.
3. The transcription's actual image/panel/text region has been verified.

The report establishes the first two types of metadata relationship where
stated. It establishes no relationship of the third type. Its root field
`image_text_alignment` is `not_reviewed`; numbered panels and `fRos` retain
`panel_region_status: unresolved`. These references support later image
inspection and dependency checks before decoding experiments.

## Naming convention and input identity

René Zandbergen's [IVTFF specification](https://voynich.nu/software/ivtt/IVTFF_format.pdf),
document issue 2.0.2 (8 July 2025), section 4.2 and Figures 1–2, printed
pages 11–12, explains the folio, side, and numbered-panel notation. It also
identifies `fRos` with 85v and 86r and documents the exceptional 86v panel names.

The implementation explicitly lists the numbered page names observed in the
[pinned ZL3b and IT2a sources](../../data/transliterations.json). Each keeps its
original identifier. A declared naming rule supplies a side reference; it does
not select a crop or silently truncate an arbitrary suffix. Unlisted names such
as `f67r3` and `f86v1` remain unsupported. A new source or page convention
requires a reviewed extension. Only ZL3b and IT2a enter the report, even when the
catalog includes additional alphabets or exports.

The Yale manifest must match the existing
[image-index snapshot](../image-index/audit.json): SHA-256
`317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309`.
The generator rebuilds both index CSVs and their audit byte for byte before
joining references. It checks pinned transcription bytes through the shared
source loader and records the canvas-CSV hash. A changed manifest, altered
index, or source-pin mismatch stops processing.

## Recorded coverage

Inspected 11 October 2026 (America/New_York). The complete, reproducible
[report](transcription-image-coverage.json) has one record per distinct page
identifier, with separate per-source locus counts and every matching canvas.
It retains empty headers and excludes source-declared nonexistent loci only
from the `present_loci` denominator. No token processing enters this audit.

| Measure | ZL3b | IT2a |
| --- | ---: | ---: |
| Page headers | 227 | 225 |
| All locus records | 5,385 | 5,215 |
| Present locus records | 5,385 | 5,214 |
| Supported plain folio requests | 184 | 183 |
| Strict lookup rejects panel/special identifiers | 43 | 42 |
| Documented side references with matching label metadata | 227 | 225 |
| Panel/special page regions still unresolved | 43 | 42 |

There are **227 distinct page identifiers** across the pair. ZL3b alone has
`fRos` (160 present loci) and `f116v` (one present non-P0 locus). This describes
edition coverage. It does not identify the terminal writing as a cipher key,
infer a missing IT page, or establish a historical `117v → 116v` alias.
The [legacy foliation decision](../folio-aliases/README.md) remains separate.

For `f70v1` and `f70v2`, both partial 70v canvases remain references for each
page; neither is assigned to an individual panel. For `fRos`, the single
canvas labeled `85v and 86r (foldout)` is retained once, with both requested
sides attached. Metadata coverage is not proof of complete visible text.

## Conservative dependencies

Treat sides and panels with the same declared leaf number as related. Connect
leaf numbers that share an explicitly labeled canvas, then take the **transitive
closure** over the whole pinned index, including intervening leaves outside an
eventual selected sample. These are conservative dependencies from labels;
they do not identify all shared content or prove a complete physical structure.

The 102 indexed leaf numbers form **94 components**. Six contain multiple leaves:

| Stable dependency group | Leaf numbers |
| --- | --- |
| `yale-leaves:69+70` | 69, 70 |
| `yale-leaves:71+72` | 71, 72 |
| `yale-leaves:85+86` | 85, 86 |
| `yale-leaves:88+89+90` | 88, 89, 90 |
| `yale-leaves:94+95` | 94, 95 |
| `yale-leaves:100+101+102` | 100, 101, 102 |

For example, scans connect 88v to 89r and 89v to 90r. Leaves 88 and 90
therefore belong to one component even without a single image naming both.
Grouping each scan independently would miss these chains. Opposite sides of
a leaf retain the same component too.

Before freezing a split, combine selected leaves from one component into one
sampling unit, retain the derived group ID, and declare all indexed canvas
references for those selected leaves. The optional `--split` gate checks these
requirements against freshly recomputed coverage. It rejects omitted groups,
missing canvas references, unsupported leaves, and components divided among
multiple units. Required canvases come from the complete rebuilt index through
`indexed_canvas_ids_by_leaf`, including sides absent from both source editions;
transcription-page support is checked separately. This last requirement is deliberately stricter than the base
split validator's allowance for several same-partition units sharing an
arbitrary dependency group: the image audit prevents inflating units connected
by the recorded scans. Review conservative exclusions before choosing a sample.

## Reproduce and check

Python 3.10 or later, standard library only. Images are linked, not downloaded
or redistributed. Download the public metadata once, then replay offline:

```sh
curl -fsSL https://collections.library.yale.edu/manifests/2002046 -o /tmp/voynich-manifest.json
python3 scripts/audit_transcription_images.py \
  --manifest /tmp/voynich-manifest.json \
  --check research/folio-alignment/transcription-image-coverage.json
python3 -m unittest tests.test_transcription_images -v
```

Use `--output PATH` to write a separate report. The writer rejects the manifest,
split, source catalog, cataloged input files, raw-data directory, and image-index
directory as destinations, including symlink and hardlink aliases of input
files. It checks the destination before computing the audit. This preserves
inputs for replay; it does not change source pins or the coverage method.
For an actual split declaration:

```sh
python3 scripts/audit_transcription_images.py \
  --manifest /tmp/voynich-manifest.json --split /tmp/candidate-split.json
python3 scripts/validate_evaluation_split.py /tmp/candidate-split.json \
  --input /tmp/candidate-input.json --require-frozen
```

The second command uses the split's actual pinned input bytes. The image gate
does not verify that input checksum or certify freeze history. Both gates must
pass for their respective claims, and neither certifies unseen material,
independent review, or correct image/text alignment. Existing full-corpus
analysis and inventory exposure still belong in the split declaration.

The image gate reads split files with the [same strict JSON loader](../evaluation/SPLIT_FORMAT.md)
as the base validator. Duplicate decoded object names and literal non-JSON
numeric constants fail before structural or image-dependency checks, preserving
one unambiguous declaration at both entry points. The coverage report and its
source/image pins are unaffected by this serialized-split check.

Tests exercise partial-view preservation, explicit convention rejection,
Rosettes deduplication, absent historical aliases, transitive grouping,
per-source/nonexistent denominators, pair isolation, source/index pin gates,
and refusal of incomplete dependency declarations. The recorded report was
also regenerated and compared in full.

Next, review the coarse references against images and specify text regions for
the chosen pilot pages. Use the dependency components when designing sampling
units, and record prior exposure before registering a candidate-specific test.
This contribution supplies metadata infrastructure, not a decipherment or
translation result.
