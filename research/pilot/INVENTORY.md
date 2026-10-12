# Ten-folio visual pilot

Completed 2026-10-11 (America/New_York). This contribution answers the project's first inventory task, using Yale's manuscript images and catalog. It establishes a descriptive baseline, not a decipherment.

## Method and sources

The [selection protocol](SAMPLING.md) was fixed after reading catalog metadata and before image inspection. Ten target sides were allocated across the six catalog sections. Earliest available exactly labeled rectos were selected, with one explicit exception for the complete cosmological foldout. Each selected image was inspected at a maximum dimension of 1,800 pixels. No OCR, transcription, plant identification, or exact line counting was performed.

[S002, Yale's catalog](https://pre1600ms.beinecke.library.yale.edu/docs/pre1600.ms408.HTM), supplies section attribution. [S003, Yale's digital manuscript](https://collections.library.yale.edu/catalog/2002046), supplies the visual evidence. [S004, its manifest](https://collections.library.yale.edu/manifests/2002046), supplies exact labels and image identifiers. The inventory's observation columns describe the selected images; section names are reported catalog classifications. Words such as plant, star, and jar describe visible forms, not decoded meanings or established species/functions.

The [CSV inventory](inventory.csv) is the canonical row-level record. It includes full and inspected image URLs, canvas URIs, exact labels, section ranges, dimensions, source identifiers, and observation limitations. [Provenance](PROVENANCE.json) identifies the fetched manifest and locally inspected JPEG derivatives by checksum. Images are linked rather than republished.

## Inventory

| Target and Yale image | Catalog section (S002) | Direct observation: text layout | Direct observation: illustration forms | Uncertainty / scope |
| --- | --- | --- | --- | --- |
| [1r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006076) | I, botanical | Several horizontal text blocks separated by gaps; small marks along the margins. | Red decorative marks; diffuse green areas behind text. No clear outlined whole-plant drawing on this side. | Green areas may include show-through or transferred color; the image alone does not determine their origin. Catalog attribution does not establish a plant illustration here. |
| [2r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006078) | I, botanical | Short text blocks lie on either side of stems in upper and lower parts of the page. | One large plant-like drawing, with green lobed leaves, three flower-like heads, and a red-brown branching root. | No species identification; apparent spaces are not validated token boundaries. |
| [67r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006194) | II, astronomical / astrological | Writing follows circular bands and radial sectors, with horizontal text above the left diagram and below the right. | Two large circular diagrams across folded panels; central face-like forms, stars, colored rays, and small crescent-like forms. | Manifest label is simply `67r`, despite multiple panels. No panel suffixes or astronomical identities are inferred. |
| [68r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006196) | II, astronomical / astrological | Horizontal blocks at the top of the left and middle panels; short inscriptions by stars; circular and radial writing in the right panel. | Three visible panels: scattered stars and round face-like forms on the left/middle, and a large divided circular diagram on the right. | Associations with particular stars, constellations, or celestial bodies are untested. The canvas is not split into independent samples. |
| [75r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006208) | III, biological (balneological in S001) | Dense horizontal text wraps around large drawings; additional writing occupies a narrow enclosed region near the upper center. | Human figures within or beside green pool/channel-like areas; blue outlines link parts of the drawing. | Fluids, anatomy, and depicted actions cannot be established from visual resemblance alone. |
| [76r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006210) | III, biological (balneological in S001) | A broad text column in several blocks, with enlarged initial signs and isolated left-margin marks. | No large figurative or pool-like illustration visible on the selected side. | Retained as a text-only observation within the catalog's biological range; adjacent imagery is outside this row. |
| [85v](https://collections.library.yale.edu/catalog/2002046?child_oid=1006231), shared scan labeled `85v and 86r (foldout)` | IV, cosmological | Writing follows circular rims and connecting structures; scattered inscriptions occur between diagrams. | Nine large circular medallions in a three-by-three arrangement, joined by elaborate bands; stars and blue/green details. | The whole shared scan is described. Features are not assigned to 85v versus 86r or given semantic interpretations. Fine inscriptions are small at the inspected resolution. |
| [87r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006232) | V, pharmaceutical | Two main text blocks to the left of a large drawing, with their right edges constrained by it. | One large plant-like form with broad green leaves, blue-tipped flower-like clusters, and a branching brown root; no visible jar-like forms. | A whole plant within the pharmaceutical range; medicinal use and species are not inferred. |
| [88r](https://collections.library.yale.edu/catalog/2002046?child_oid=1037112) | V, pharmaceutical | Horizontal text blocks alternate with rows of drawings; short inscriptions occur beside individual forms. | Stacked decorated vessel-like forms along the left, and multiple separate root/leaf-like specimens across the page. | Vessel function and whether short inscriptions name the adjacent forms remain unestablished. |
| [103r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006254) | VI, continuous text / possible recipes | Dense horizontal text divided into short blocks; star-like marks run down the left margin. | Red-filled and unfilled star-like marginal forms; no large central drawing. | A dark upper-right stain reduces contrast. Recipe content and the semantic role of the marginal marks are unverified. |

## Result and limitations

All ten preselected image canvases were available and inspected; no target was substituted. Coverage is 2 botanical, 2 astronomical/astrological, 2 biological/balneological, 1 cosmological, 2 pharmaceutical, and 1 final-text target. These are **catalog section counts**, not counts of observed motif types. The foldout target includes contextual material labeled 86r and is counted once.

The sample captures horizontal prose-like blocks, text constrained by drawings, inscriptions beside individual forms, and circular/radial writing. Two useful boundary cases are [76r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006210), with no large illustration in the biological range, and [87r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006232), with a whole plant and no visible jars in the pharmaceutical range. Therefore a future dataset should keep **catalog section** and **observed motif/layout** as separate variables. This is a proposed recording practice grounded in these examples, not a statistical association.

Selection is purposive and biased toward section beginnings and rectos. Each observation was made by one AI-assisted reviewer and needs independent checking. Image scale limits fine detail, especially on foldouts; pigmentation and show-through can obscure shapes. The ten canvases do not represent ten complete physical leaves or ten equally sized text samples. Nothing here validates a translation, botanical identification, reading order, tokenization, or manuscript-wide frequency estimate.

## Next test

Have a second reviewer check each image without seeing the observation fields first, then compare descriptions and record disagreements. Extend the inventory using a fixed selection of section-interior sides and versos. Define foldout panel identifiers against a chosen transcription before joining text and image records. Only then select transcription conventions and design frequency or line-position analyses.

## Recheck identifiers and provenance

The validator uses Python's standard library and performs no network requests. To check the recorded metadata against a fresh public manifest and inspect the same derivatives locally:

```sh
curl -fL https://collections.library.yale.edu/manifests/2002046 -o /tmp/voynich-manifest.json
python3 scripts/validate_pilot.py --manifest /tmp/voynich-manifest.json
```

A changed manifest checksum is reported separately from a label/identifier mismatch. JPEG hashes identify the exact inspected bytes; an image server may later recompress a derivative without changing the artwork. Optional `--images DIRECTORY` verifies locally held files named `IMAGE_OID.jpg`. The validator checks metadata consistency, not the correctness of the visual descriptions.
