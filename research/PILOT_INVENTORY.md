# Boundary observation record and standalone 100r comparison

## Question, sources, and method

This contribution addresses the inventory component of the decipherment pilot
in [the project brief](../99TOKENS.md). The [selection protocol](PILOT_SELECTION.md)
was committed before image downloads or inspection (protocol-only commit
`ef2ffda`, rebased from the original `56bd5b4`). Ten Yale canvases cover all
six catalog parts, with no substitutions after inspection. Each record is a
scan/surface, not necessarily one physical leaf or one text panel.

Nine canvases overlap the [section boundary survey](boundary-pilot/INVENTORY.md).
This record additionally inspects `100r`, the latest exactly labeled standalone
recto in Part V. The other survey includes the later composite labeled
`101v (part) and 102r`. These are different selection rules; neither substitutes
an image after seeing its contents. The nine shared scans are repeated source
material, not nine additional independent manuscript samples.

Section ranges and attributions are **reported claims** from S002; S001 calls
the bathing illustrations balneological, whereas S002 calls Part III
“Biological.” Neither label establishes the drawings' intended meaning.
Exact canvas labels, identifiers, dimensions, and image URLs come from S004.
Descriptions below and in the [CSV](data/pilot-folios.csv) are **direct
observations** of S003 images. Interpretations are recorded separately in the
CSV. See the [source register](SOURCES.md) for source URLs, access, and limitations.

All ten images were inspected on 2026-10-11 (America/New_York) as complete IIIF
JPEGs fitting within 1600 × 1600 pixels. No glyph transcription, token/line
counts, species identification, or decipherment was attempted. This is an
initial observation record made with AI assistance; independent verification
is pending.

The image identifiers and separation of section attribution from observed layout
provide a foundation for aligning a documented transcription to image regions
and choosing suitable baseline comparisons. They do not constitute a decoding
test. All ten images have been exposed through inspection; none is represented
as untouched held-out evaluation material. No development/evaluation split,
transcription recommendation, or decipherment candidate is submitted here.

## Inventory overview

Every link identifies the exact Yale scan. The CSV retains per-record
uncertainties, source IDs, full-resolution image and canvas URLs, inspection
URLs, and SHA-256 digests of the inspected JPEGs.

| Yale label and image | Catalog part (S002) | Text layout observed | Illustration forms observed |
| --- | --- | --- | --- |
| [1r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006076) | I — botanical | Four separated horizontal text blocks; enlarged opening glyphs and colored marks at the left of some blocks. | Red ornamental shapes and pale green patches; no clear standalone plant illustration. |
| [66r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006192) | I — botanical | Dense horizontal text groups with a narrow column of short forms at left; additional writing at the foot. | Small outlined human figure and small rounded/container-like forms at lower left; no large plant drawing. |
| [67r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006194) | II — astronomical/astrological | Short paragraph above the left circle; writing follows circular bands and sectors; short lines below the right circle. | Two side-by-side circular diagrams across a vertical fold; face-like center and colored rays at left, crescent/disc forms and a star-like center at right. |
| [73r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006206) | II — astronomical/astrological | Curved bands of writing around rings and short inscriptions beside figures. | Concentric arrangements of human figures with star-like forms; a dark quadruped at the center; additional figures above the rings. |
| [75r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006208) | III — “Biological” | Text wraps around a tall central drawing and a lower-right group; writing also occurs inside an outlined upper-left shape. | Human figures in a tall green channel/pool-like form with a broad upper structure; another green grouping at lower right. |
| [84r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006226) | III — “Biological” | Short inscriptions above the top band; larger text blocks between and below illustrated groups; lower text beside the bottom-left group. | Three groups of human figures, two in green horizontal enclosures and one in a pale blue lower enclosure; winding blue line at left. |
| [85v and 86r (foldout)](https://collections.library.yale.edu/catalog/2002046?child_oid=1006231) | IV — medallion/cosmological | Writing around and inside circular regions and along connecting bands; several physical creases cross the layout. | Nine prominent circular regions in a roughly three-by-three arrangement, with connecting forms, star-like marks, colored radial shapes, and small architectural-looking forms. |
| [87r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006232) | V — pharmaceutical | Two main text blocks at upper/middle left, with right edges limited by the plant drawing. | One large plant-like drawing with green leaf groups, blue-tipped upper forms, and branching reddish roots; no obvious jar on this surface. |
| [100r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006248) | V — pharmaceutical | Short inscriptions beside plant forms; a central horizontal text block and a larger block beneath the lower illustrations. | Rows of separate green plant/root forms and two red cylindrical container-like drawings at left. |
| [103r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006254) | VI — continuous text | Dense horizontal text grouped into entries with star-like markers down the left margin. | Red and unfilled star-like markers; a brown patch over upper-right text; no large plant or human illustration. |

## Result and limits

All ten selected scans were available for inspection. Two cautions follow:

- **A catalog range is not a uniform visual class.** Neither selected Part I
  surface shows a clear large botanical drawing. Part V's `87r` is a single
  large plant-like drawing, whereas `100r` shows smaller forms and containers.
  These observations qualify future use of section names as image-derived
  feature labels; they do not disprove the catalog grouping.
- **A simple folio label is not a panel count.** `67r` spans two visible diagram
  panels. `85v and 86r (foldout)` is one scan with multiple panels and creases.
  Canvas, folio side, text region, and physical leaf need separate identifiers
  before statistical sampling or transcription alignment.

Comparison with the boundary survey shows agreement on the broad layout
descriptions of the nine shared scans: text-heavy Part I boundaries, circular
diagrams, human/enclosure scenes, the multi-region foldout, the large plant on
`87r`, and marginal markers on `103r`. This is agreement between AI-assisted
descriptive records, not independent verification of glyph readings, exact
counts, or depicted meanings. The additional `100r` record provides a separately
linked plant/root and container layout without describing a composite
`101v`/`102r` scan as one isolated folio-side sample.

The sample deliberately favors boundary rectos. It is not random or
representative, and it cannot establish feature frequencies. It does not
include a typical interior botanical leaf. At this inspection scale, small
glyphs, faint marks, colors, and the foldout's fine details remain uncertain.
Plant/animal/human/container-like forms describe resemblance, not their intended
identity or function. Pale patches could arise from material condition or marks
on the reverse; their cause was not determined. No observation supplies evidence
for a translation or preferred explanation.

## Reproduce the check

From the repository root, using Python 3 and curl:

```sh
curl --fail --location 'https://collections.library.yale.edu/manifests/2002046' \
  --output /tmp/voynich-2002046-manifest.json
python3 tools/check_pilot.py /tmp/voynich-2002046-manifest.json
```

The checker resolves the selection rule and compares the CSV's ordered labels,
section assignments, canvas/image identifiers, dimensions, and URLs with that
manifest. It checks uniqueness and presence of observation fields. It does not
verify visual descriptions or live link availability. Optional
`--images DIRECTORY` checks local derivatives named `IMAGE_OID.jpg` against the
CSV's hashes. Download each `inspection_image_url` to obtain those derivatives.

The manifest retrieved on 2026-10-11 contained 213 canvases. Its SHA-256 was
`317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309`.
Metadata may change; a changed manifest digest alone does not invalidate an
identifier. Per-image digests identify the inspection bytes, although a server
may later recompress a JPEG. Images are linked, not committed.

## Next test

An independent observer should review each image and the CSV's uncertainties,
recording corrections and disagreements. Define an expanded sample containing
interior leaves and versos, with panel/line identifiers for foldouts. Document
a transcription edition before any glyph, token, or line-position statistics.
