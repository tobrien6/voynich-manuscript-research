# Ten-folio pilot: selection protocol

Protocol fixed on 2026-10-11, after reading Yale's catalog and image manifest and before inspecting the selected manuscript images.

## Question and sampling unit

Can a small source-linked inventory capture the different visible text layouts across all six illustrated groups in Yale's description, while keeping observation separate from interpretation?

The sampling unit is a **target folio side**, represented by one Yale image canvas. This is not a census of both sides of ten physical leaves. Foldouts and shared images require additional identifiers.

## Rule fixed before image inspection

Use the six section ranges in [Yale's catalog, S002](https://pre1600ms.beinecke.library.yale.edu/docs/pre1600.ms408.HTM), in manuscript order. Allocate 2, 2, 2, 1, 2, and 1 targets to Parts I–VI respectively. The four extra targets go to sections with separately labeled rectos, leaving one target for the cosmological folding leaf and one for the final text section.

For Parts I, II, III, V, and VI, choose the earliest available exactly labeled recto canvas in the section; where allocated two, choose the next such recto. For Part IV, choose the canvas labeled `85v and 86r (foldout)`, which is the complete shared foldout view rather than the three separately labeled partial views of its other side. Record `85v` as the target and retain the entire shared label; `86r` is additional context, not an eleventh independently sampled target. This choice uses labels, not observed artwork.

The fixed targets are **1r, 2r, 67r, 68r, 75r, 76r, 85v, 87r, 88r, and 103r**. Preserve Yale's labels and image identifiers in the inventory. Do not silently replace targets because their imagery differs from the catalog's section description.

## Observation procedure

1. Resolve labels against [Yale's IIIF manifest, S004](https://collections.library.yale.edu/manifests/2002046).
2. Inspect each selected image at a maximum dimension of 1,800 pixels. Record descriptive text layout, illustration forms, and uncertainties; do not infer a translation, plant species, or biological function.
3. Keep catalog section attribution in a separate field. A catalog range does not establish the subject of every drawing within it.
4. Record persistent catalog links with `child_oid`, exact canvas URIs, full image URLs, inspected-image URLs, and image dimensions. Store inspection checksums so the inspected derivatives can be identified without redistributing them.
5. Report coverage and deviations explicitly. Exact glyph counts, line counts, and image segmentation are outside this pilot.

## Limits fixed in advance

This is a purposive sample biased toward section beginnings and rectos. It is not random, representative, or suitable for population-frequency estimates. The foldout is one shared scan, not independent evidence from two folio sides. Catalog section names are conventional descriptions; no content reading is established by them. A later sample should include versos, section interiors, boundary cases, and missing-leaf documentation.

## Clarification after inspection

The standalone labels `67r` and `68r` resolve to scans with multiple drawn panels. An exact recto label therefore does not guarantee a single isolated panel. The original targets remain unchanged; descriptions retain all visible panels as context within one canvas record. Panel-to-transcription mapping is pending. See the [completed inventory](INVENTORY.md).

The [verification and CSV guide](UTILITIES.md) describes metadata checks,
optional local inspection-image checksums and export of the canonical records.
