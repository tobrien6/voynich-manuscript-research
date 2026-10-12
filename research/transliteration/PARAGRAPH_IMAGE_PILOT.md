# Image pilot for three discordant paragraph endings

## Question and fixed selection

Can image layout settle paragraph-end disagreements in the
[paired annotation audit](ANNOTATION_AGREEMENT.md)? The
[selection plan](PARAGRAPH_IMAGE_PILOT_PLAN.md) was committed before image
inspection. Sort discordant page identifiers by numeric folio, then literal
identifier, and take the first three: 9r, 16r, 18r. Each has one discordant P0
locus. All three remain unresolved after this initial image inspection.

The [machine-readable record](paragraph_image_pilot.json) separates direct
observations, source annotations, provisional row associations, and interpretation.
It records source hashes, canvas references, inspected derivative URLs and image
hashes, exposure, and every source context. The images are linked rather than
redistributed. Observations are AI-assisted and await independent human review.

## Source observations

| Yale image | Discordant P0 locus | Following locus, both sources | ZL marks at the two loci | IT marks at the two loci |
| --- | --- | --- | --- | --- |
| [9r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006092) | `f9r.9,+P0` | `f9r.10,+Pc` | no end at .9; end at .10, no start there | end at .9; start and end at .10 |
| [16r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006104) | `f16r.3,+P0` | `f16r.4,+Pc` | no end at .3; end at .4, no start there | end at .3; start and end at .4 |
| [18r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006108) | `f18r.13,+P0` | `f18r.14,+Pc` | no end at .13; end at .14, no start there | end at .13; start and end at .14 |

Both sources classify the following locus as centred paragraph text (`Pc`).
ZL's marks retain that locus in the preceding paragraph. IT's marks make it a
one-locus paragraph. This is an interpretation of their explicit markers,
without asserting which convention matches the manuscript's intended structure.

The P0-only audit records the preceding end-mark disagreement but omits the
start-mark disagreement on the following Pc locus. Context across generic P
subtypes is necessary when evaluating complete paragraph divisions. This
three-page observation does not estimate how often the pattern occurs elsewhere.

The [IVTFF format definition](https://voynich.nu/software/ivtt/IVTFF_format.pdf),
Table 9 (printed page 22), defines P subtypes including Pc; section 6.9 (printed
page 26) defines the paragraph markers. The pinned source credits and edition
history are in the [source register](../transcriptions/SOURCES.md).

## Direct image observations and association limits

On **9r**, ten ordered horizontal writing rows occupy the upper part of the
page. The plant separates left and right fragments in many rows. The tenth row
is short and indented within the left writing area, directly beneath the
preceding row. The image shows no clear blank band isolating it as a paragraph.
Both sources have ten present generic P loci, and drawing-interruption markers
occur in the first nine. The candidate is provisionally associated with the
ninth row, above the short final row of the lower text group.

On **16r**, thirteen ordered rows lie beside the plant. The fourth is short
and indented relative to the first three and the row below. There is no clear
vertical separator above it. Both sources have thirteen present generic P loci.
The candidate is provisionally associated with the third row above that short
fourth row; the fifth row resumes the left margin, consistent with the shared
`*` locator. Drawing-interrupted text appears in the upper rows.

On **18r**, fourteen ordered rows lie near the upper left, with some fragments
to the right of the plant. The last row is short and indented. Its gap from the
preceding row looks comparable to nearby spacing. Both sources have fourteen
present generic P loci. The candidate is provisionally associated with the
thirteenth row above the short last row. Both sources annotate drawing
interruptions, but they differ on one additional interruption elsewhere.

These associations use ordered layout, shared locator conventions, and complete
generic P counts, including Pc. They are provisional: individual glyph strings
have not been independently aligned to image regions. Horizontally interrupted
writing must not be mistaken for multiple additional source loci. No glyphs
were transcribed and no meanings assigned.

## Disposition and next test

**All three paragraph divisions remain unresolved.** The short indented rows
are visible, but indentation and short length alone do not distinguish a
terminal line from a separate paragraph. None supplies the clear block
separation required by the pre-inspection rule for an adjudication.

Retain both source conventions. The next review should check the glyph-level
alignment and use an explicit, consistently applied paragraph definition across
all relevant P subtypes. This negative pilot identifies a concrete limitation
of the P0-only comparison; it does not correct transcriptions, evaluate a
decoding hypothesis, or establish a translation. The sample is purposive, and
all inspected pages must be disclosed as exposed in later evaluation splits.

## Reproduce the provenance checks

Python 3.10 or later; standard library only:

```sh
python3 scripts/verify_paragraph_image_pilot.py
PYTHONPATH=tests python3 -m unittest test_paragraph_image_pilot -v
```

The checker recomputes the paired audit, verifies both input fingerprints, the
fixed page selection, exact standalone image references, source contexts, and
required uncertainty declarations. It does not certify visual judgments.
For locally retrieved derivatives named `f9r.jpg`, `f16r.jpg`, and `f18r.jpg`,
add `--image-dir /path/to/local/images` to verify their bytes against the record.
Each image was bounded to 2,200 pixels in height; inspected widths were 1,584,
1,556, and 1,557 pixels respectively, checked separately from the offline script.
