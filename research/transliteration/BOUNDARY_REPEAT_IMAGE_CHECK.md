# Image check of the f82r.3 / f82r.4 encoded repeat

The sole boundary repeat in the selected common corpus is native-Eva
`qokaiin` at the end of `f82r.3` and the start of `f82r.4`, in both editions and
both comma policies. Two candidate image groups have a similar sequence of
prominent shapes. Their row association and visual correspondence are
**provisional**; precise stroke grouping and glyph-to-Eva equivalence remain
unresolved pending independent qualified review. The original transcriptions
are preserved.

## Selection and source facts

This is a purposeful check selected after the [boundary result](PARAGRAPH_BOUNDARY_REPETITION.md),
not an independent sample or frequency estimate. The [local plan](BOUNDARY_REPEAT_IMAGE_PLAN.md)
was saved before image inspection; its original SHA-256 is
`b2c4dc17d13aa549549c1ea13af031728eb67536e99156ec1d85ae224ae383a7`.
It was neither committed nor remotely published before the inspection. The
public plan's workflow explanation was clarified afterward without changing
selection, procedure or limits; the record retains both plan fingerprints. Known
native readings and the expected repeat can bias this single assistant's
judgments. The entire f82r image has now been inspected; future exposure
records must retain that fact.

The [record](boundary_repeat_image_check.json) retains the exact common unit
`f82r.1` through `f82r.9`, all four endpoint/row records, source pins and the
two selected raw loci. It replays the complete corpus and parent report before
checking selection. ZL3b source-file lines are 4807/4808; IT2a lines are
3178/3179. These are physical **file** line numbers, not manuscript row numbers.
The [catalog](../../data/transliterations.json) records editions, credits and
reuse terms.

| Selected source locus | Native tokens after conservative adaptation | Drawing interruptions | Endpoint |
| --- | ---: | ---: | --- |
| `f82r.3,+P0` | 6 | 1 | Last token `qokaiin` |
| `f82r.4,+P0` | 8 | 1 | First token `qokaiin` |

Both selected raw source strings are identical across ZL/IT, and neither has
an uncertain comma. The four variants therefore share the same endpoint
reading here; they are dependent representations. The string also appears
elsewhere in this source unit, so an isolated similar-looking group is
insufficient to locate the selected row.

## Image identity and review windows

The live [Yale manifest](https://collections.library.yale.edu/manifests/2002046)
labels image 1006222 `82r`, with dimensions 2753 by 3745. Its exact response
hash matches the existing index snapshot:
`317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309`.
The [image information](https://collections.library.yale.edu/iiif/2/1006222/info.json),
JPEG header and displayed image agree on dimensions. The original JPEG hash
is `269cb42307824ab82764f80009429e58d98c649371d8efe10d2a1f54132a21ef`.
Retrieval date is 2026-10-12. These checks establish the technical source view,
not physical glyph interpretation.

The full-page display was resized to 2719 by 3700. Subsequent official service
regions were viewed at their returned native sizes. Coordinates below use
original-image pixels, with x/y measured from the upper-left corner; `full`
requests no scaling. [IIIF Image API 2.1](https://iiif.io/api/image/2.1/#region)

| Review window | Original x,y,width,height | Official source view |
| --- | --- | --- |
| Upper text-group context | 250,360,1840,700 | [Context](https://collections.library.yale.edu/iiif/2/1006222/250,360,1840,700/full/0/default.jpg) |
| Candidate `.3` terminal group, on the page's right | 1630,550,360,150 | [Right region](https://collections.library.yale.edu/iiif/2/1006222/1630,550,360,150/full/0/default.jpg) |
| Candidate `.4` initial group, on the page's left | 280,540,260,160 | [Left region](https://collections.library.yale.edu/iiif/2/1006222/280,540,260,160/full/0/default.jpg) |

These are review windows, not independently segmented glyph masks. Image
bytes remain in a local temporary cache; this contribution supplies source
links, coordinates and hashes.

## Observations and uncertainty

The upper text group has nine left-hand starts/row trajectories. Early text
wraps around a central banded illustration; its right-hand fragments have
offset/sloping baselines. A larger text group begins below an intervening
horizontal illustrated structure. Straight horizontal alignment alone does
not identify the source loci.

Under provisional source-guided grouping, candidate `.3` has three groups on
each side of the central illustration and `.4` has four. Several neighboring
anchors support the association together: `.3`'s `qokeey` opening and long
arch/ascender group precede its shorter left-terminal group, while the right
fragment has an extended opening group and an arched middle group before the
candidate endpoint. The next left fragment begins with the compared group,
followed by rounded/arched groups and a short terminal before the illustration.
Its right fragment starts with a rounded opening and tall/looped structure.
These are comparisons to known source readings, not a blind transcription.

The middle token group in each endpoint window has a 4-like opening with a
dark head/descending stroke, a small rounded loop, a tall looped ascender,
then a low angular/arched run with minim-like strokes and a curved terminal.
The order of these conspicuous features is similar. Width, slant, joins and
terminal curves differ. Precise minim count, connected-stroke grouping and
glyph-to-Eva mapping have not been independently adjudicated.

The two occurrences lie on opposite sides of the central illustration. Source
tags join the left/right fragments into each encoded locus. This check does
not adjudicate the manuscript's reading route around that structure or turn
encoded adjacency into verified consecutive physical words. Visual similarity
also supplies no decoded meaning, language or copying explanation.

## Replay and next review

Standard-library Python, with the pinned parent/corpus inputs present:

```sh
PYTHONPATH=tests python3 -m unittest test_boundary_repeat_image -v
python3 scripts/verify_boundary_repeat_image.py
python3 scripts/verify_boundary_repeat_image.py --image-dir /tmp/your-local-image-cache
```

The optional cache check needs the original `f82r.jpg`, `live-manifest.json`,
`info.json`, and the three region JPEGs with their recorded names. Six tests
check fresh source/endpoints, row types, missing variants, raw-text tampering,
source/image pins, required original byte pins, region URLs/bounds/dimensions,
typed coordinates, honest exposure declarations, unresolved glyph status,
and malformed JPEG headers. The actual original and region bytes match all
recorded hashes and dimensions.

The verifier checks source facts, declared metadata and byte identity. It
cannot certify a visual judgment, actual inspection chronology or a glyph
reading. A qualified reviewer should assess the contextual row associations
and both native-scale endpoint groups, preserving alternatives and the known
source-reading bias. Any source correction needs a separately reviewed record.

The initial inspection used parent report hash
`451c0859306ab591f0c9e287f147131aa3d94b34bf0998851d2b632fb74dcb99`.
After accepted writer repair [PR #112](https://github.com/tobrien6/voynich-manuscript-research/pull/112),
the record explicitly refreshes that input to
`265b7dd26dfe56f57b8b163f73e6e26cb01c2007b043752e441afd96092ec8ff`.
The parent report changes only its implementation fingerprint; its scientific
fields and syntax tree outside the CLI body remain identical. Selected source
facts, image bytes, original plan and visual conclusions are preserved. A
temporary replay against those accepted files passes all 68 focused
parent/child/source/image tests and both complete report and image-cache checks.
