# Fixed comparison of historical terminal photographs and Yale's final pair

## Question and scope

Does the visible layout in the photographic reproductions on Newbold/Kent
1928 Plates X and XV correspond to the ordinary Yale image labeled `116v`,
and what is absent, different or unresolved because of the reproductions'
crop and quality? Inspect Yale's adjacent `116r` as a fixed context comparison.
This concerns selected visible surface features. It cannot establish what
the legacy catalog's `117v` meant, authenticate the historical photograph,
adjudicate glyphs or validate Newbold's proposed key/readings.

This plan is recorded before new detailed comparison views in this task.
Prior exposure is substantial: all fourteen S009 source/context pages,
including Plates X and XV, were already inspected for the source record;
Yale `116v` was inspected in the original foliation work and MSI intake.
Prior pixel exposure to `116r` is not established. No blind, independent-human,
qualified-reader, previously unseen or untouched evaluation is claimed.
The fixed selections arise from the accepted historical-source locators and
the pinned manifest's final numbered pair, not an image search for agreement.

## Fixed inputs

- Accepted source-context base: `7c66607262721717fa6049dec61c8fdf31dfad24`.
- S009 hosted PDF: [Newbold/Kent 1928](https://oncle-dom.fr/biblio/1928-Newbold-The%20Cipher%20of%20Roger%20Bacon.pdf), 46,842,963 bytes, 297 pages, SHA-256 `69e9f37fbafe3b76c96bae9fba5b6c459f639e97824f7f9bb9e9cf4504a9c891`.
- Primary historical photograph: **Plate X, PDF page 119**. Secondary historical representation: **Plate XV, PDF page 159**, separating its photograph from the hand and printed transcripts. View both complete PDF pages, including captions. Neither plate's caption supplies a numeric folio label. Their dependence on a common photograph or source surface is not resolved; do not count them as independent evidence samples.
- S003/S004 Yale target: label **116v**, image/canvas **1006277**, [catalog image](https://collections.library.yale.edu/catalog/2002046?child_oid=1006277), [ordinary full JPEG](https://collections.library.yale.edu/iiif/2/1006277/full/full/0/default.jpg). Accepted intake pin: 1,994,539 bytes, 2,686 × 3,697, SHA-256 `0f2e8691a66f255159b28f3fc2984633016f96c30c6d4d89cff6396708e5bb17`; decoded stored RGB `12baa0075cf7a996813707a412fa67505e6ce75422b74ed3c9353c38aa3185b5`.
- Fixed adjacent context: label **116r**, image/canvas **1006276**, [catalog image](https://collections.library.yale.edu/catalog/2002046?child_oid=1006276), [ordinary full JPEG](https://collections.library.yale.edu/iiif/2/1006276/full/full/0/default.jpg). Record its actual retrieved bytes, dimensions and hash before viewing; no prior asset pin is asserted.
- Pinned [manifest](https://collections.library.yale.edu/manifests/2002046): SHA-256 `317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309`. Verify the cached response and exact labels/IDs against the index; no global folio shift or inference from display order.
- Existing `newbold-terminal-source.json`: SHA-256 `0e25099797f7055204eb945abdc4dfaf36bf1cb2c4a6aa3d314d43aface9ba4d`.
- Existing `canvases.csv`: SHA-256 `a0b03f8f012331e61a1e89b65f6462be0f1d28f896a068a8cc2cd0f63a255b0f`; `audit.json`: `812032c85bbbb8e3d196bdd9bfb5eef075a0569d842c2935fec8e861cf684ddc`.
- Existing `multispectral-intake.json`: SHA-256 `d3414bca64c2b71378cda05402b6a8271c99c2e993d3ccdacecd083e05c917e0`. It supplies the ordinary Yale JPEG pin only; no processed MSI image is selected here.
- Existing alias registry: SHA-256 `627ae452e40b2ea176ac50a641c1fb31c58fcbbcfa5fffddd4ed87415995dfc8`, unresolved legacy lookup with false mapping permission and null target.

## Observation procedure

1. Verify source bytes and metadata before viewing. Render both complete PDF pages with Poppler and inspect the ordinary whole Yale images. Preserve captions, plate margins and the separate photograph/transcript boundaries.
2. Describe visible extent and orientation first. A cropped historical photograph must not be treated as a full modern leaf surface or as evidence that a modern feature outside its frame was absent historically.
3. Record the following fixed feature classes for each historical photograph against the target and adjacent context: **visible text-row arrangement; relative starts/ends and broad cluster spacing; cross-shaped marks and their ordinal positions; marginal drawings; blank-area/edge/damage coverage**. For every class retain correspondence, difference, outside-frame and unresolved outcomes. Do not discard an unhelpful feature or add a replacement image after seeing the result.
4. Use ordinary zoom only. Newbold's printed/hand transcripts remain separate objects and cannot supply missing photographic glyphs. No OCR reading, enhancement, filtering, geometric fitting, automatic image matching, physical registration, quantitative similarity score or letter/word transcription is performed.
5. Report the candidate surface association as a bounded nonblind AI observation, with all discrepancies and crop limits. Comparing an adjacent recto is not a search of the whole manuscript and does not establish uniqueness or a calibrated false-match probability.

## Publication and validation

Record the published plan commit, unchanged plan hash, source pins, complete-page
locators, observations and exposure in a follow-up JSON ledger and note. Keep
PDFs, full JPEGs and renders local; publish selected original descriptions,
links and fingerprints only. Reuse cautions from S003/S009 remain in force.
Preserve all existing source ledgers, registry, checker/tests and statistical
inputs. Run the existing alias tests, registry validation and actual blocked
lookup; these check retained behavior, not the visual association's truth.
No change to issue #13's closure gate follows from a candidate match.
