# Yale image-to-folio crosswalk and foliation audit

Question: which Yale image views correspond to each explicitly labeled folio side, and where would a one-image-per-side assumption lose or duplicate evidence?

This contribution indexes the complete public [Yale IIIF manifest for object 2002046](https://collections.library.yale.edu/manifests/2002046), retrieved 2026-10-11 (America/New_York), and compares its numbered labels with the [MS 408 catalog's collation and section ranges](https://pre1600ms.beinecke.library.yale.edu/docs/pre1600.ms408.HTM). It does not transcribe the script or resolve physical foldout panels.

## Files and units

- [canvases.csv](canvases.csv): one row per Yale canvas, including its exact label, zero-based manifest index, one-based viewer position, canvas URI, image identifier, catalog image link, full image URL, image service, and source dimensions.
- [folio-sides.csv](folio-sides.csv): one row per explicitly labeled numbered side, with **every matching canvas** retained. Semicolon-separated lists of indices, image identifiers, canvas URIs, and links have corresponding positions. This is the reverse lookup for locating source views before transcription.
- [audit.json](audit.json): calculated counts, repeated mappings, numbering gaps, the catalog comparison, access date, and SHA-256 of the exact input response.
- [index_yale_manifest.py](../../scripts/index_yale_manifest.py): an offline generator using Python's standard library; it downloads no images.

The [IIIF Presentation specification](https://iiif.io/api/presentation/3.0/#canvas) defines a canvas as a view/container. Here a canvas may show a folded panel, partial side, shared spread, or non-numbered cover/binding view. Neither canvas count nor an exact single-side label establishes physical completeness. Panel subdivision requires separate image work.

## Method

Preserve labels verbatim. Extract only explicit number-plus-side strings such as `85r` or `86v`, with alphanumeric boundaries. Deduplicate repeated mentions **within a label**, while retaining separate canvases carrying the same label. A parenthetical numeric range such as `85-86` does not introduce sides that the label does not name.

Classify labels as exact single-side labels, compound/partial labels, or non-numbered views. Mark `(part)` and multiple explicit sides separately. These are properties of the **labels**, not observations of the artwork. A plain label such as `67r` can still describe a multi-panel image.

The generator requires Yale object 2002046's identifier and the observed single-image canvas arrangement. It stops for changed language maps, duplicate canvas IDs, multiple painting annotations, non-image bodies, unexpected image services, or invalid image dimensions, so those cases receive review instead of being silently reduced to one image.

## Result for the recorded response

| Measure | Count |
| --- | ---: |
| Yale canvases | 213 |
| Exact single-side labels | 183 |
| Compound or partial labels | 21 |
| Non-numbered views | 9 |
| Distinct explicit numbered folio sides | 204 |
| Distinct explicit folio numbers | 102 |
| Sides associated with multiple canvases | 9 |

These are computed from the response identified by `317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309`; the full result is in [audit.json](audit.json). Every numbered folio represented in the labels has both an explicit recto and an explicit verso association. This is a metadata finding, not proof that every surface is fully visible.

The repeated side associations are **70v, 72v, 85r, 86v, 89v, 90r, 95v, 101v, and 102v**. For example:

| Folio-side lookup | Yale source views | Consequence for research |
| --- | --- | --- |
| 70v | Two canvases both labeled `70v (part)`: [1006200](https://collections.library.yale.edu/catalog/2002046?child_oid=1006200), [1006201](https://collections.library.yale.edu/catalog/2002046?child_oid=1006201) | Do not collapse duplicate labels into one image. |
| 85r / 86v | [1006228](https://collections.library.yale.edu/catalog/2002046?child_oid=1006228) labels part of 85r; [1006229](https://collections.library.yale.edu/catalog/2002046?child_oid=1006229) labels parts of both; [1006230](https://collections.library.yale.edu/catalog/2002046?child_oid=1006230) labels part of 86v. | Preserve both partial and shared associations. |
| 85v / 86r | One shared view, [1006231](https://collections.library.yale.edu/catalog/2002046?child_oid=1006231), labeled `85v and 86r (foldout)`. | The same artwork cannot be counted as two independent image samples. |
| 90r | A shared view [1006235](https://collections.library.yale.edu/catalog/2002046?child_oid=1006235) and an exact-side view [1006236](https://collections.library.yale.edu/catalog/2002046?child_oid=1006236). | Preserve alternatives until coverage/overlap is inspected. |
| 102r | [1006251](https://collections.library.yale.edu/catalog/2002046?child_oid=1006251) labels `101v (part) and 102r`. | An exact-label-only lookup would omit 102r. |

Within the observed numbered span **1–116**, the unrepresented numbers are **12, 59–64, 74, 91–92, 97–98, and 109–110**. They match the missing leaf numbers reported in the [catalog's collation](https://pre1600ms.beinecke.library.yale.edu/docs/pre1600.ms408.HTM). Agreement supports using these labels for an initial crosswalk; it does not establish all foliation conventions.

The catalog gives the last section as **103r–117v**, while the manifest's last explicit numbered side is **116v** ([1006277](https://collections.library.yale.edu/catalog/2002046?child_oid=1006277)). Neither 117r nor 117v appears explicitly in the labels. This discrepancy is unresolved: the index **does not invent a missing 117th leaf, rename 116v, or assign the back flyleaf to 117**.

## Reproduce and verify

From the repository root, using Python 3:

```sh
curl -fsSL https://collections.library.yale.edu/manifests/2002046 -o /tmp/voynich-manifest.json
python3 scripts/index_yale_manifest.py --manifest /tmp/voynich-manifest.json --access-date 2026-10-11 --output-dir research/image-index --check
python3 -m unittest discover -s tests -p 'test_yale_image_index.py' -v
```

The first date is the retrieval date of the published snapshot. For a **new snapshot**, pass its actual retrieval date and omit `--check` to write reviewed outputs. `--check` changes no files and compares the two CSV indexes and audit byte-for-byte. A changed manifest response, access date, or selected metadata causes a mismatch; compare the checksum and row changes before replacing the snapshot.

Six focused tests cover shared foldouts, repeated partial labels, false side extraction from numeric ranges, preservation of alternate views, duplicate/multiple-painting rejection, and changed object/label conventions. The full recorded response was also regenerated byte-for-byte and its forward/reverse associations checked independently. These checks establish metadata consistency, not correct manuscript interpretation.

## Limits, rights, and next test

The manifest is live and can change. Links and indices are recorded evidence; indices are positions, while canvas/image identifiers identify the views. The parser deliberately handles the current Yale format and requires review when that structure changes. A label association does not specify which pixels belong to which side, how partial views overlap, or whether a transcription uses the same panel names.

Yale's [digital record](https://collections.library.yale.edu/catalog/2002046) grants public access and provides a copyright/other-rights caveat. No explicit open image license was found in the inspected record. This contribution contains technical identifiers, original analysis, and links; no image binaries or complete source manifest are republished.

Next test: independently inspect all nine repeated mappings and the shared foldout labels, recording panel boundaries and overlap before joining image observations to a transcription. Check the 116v/117v discrepancy against another documented foliation source, while retaining both source statements. No decipherment claim follows from this crosswalk.
