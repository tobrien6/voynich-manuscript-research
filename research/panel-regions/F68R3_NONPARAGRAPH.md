# Non-paragraph writing on f68r3 and two provisional radial anchors

The right 68r field has a complete 22-location source packet even though it
has no P0 records. Two fixed radial locations have compatible candidate image
placements; exact glyphs and word boundaries remain unresolved. This extends
the [existing 68r review](68R_LAYOUT.md) into its previously omitted
non-paragraph scope without making the pilot a verified image/transcription join.

The [plan](F68R3_NONPARAGRAPH_PLAN.md), collector/tests and
[native packet](f68r3-native-review.json) were published at
`2bce08873c0cf8bb24661190c1b1ec18634b1ede` before this contribution's manuscript
pixel inspection. The [observation record](f68r3-image-review.json) retains all
request identities, native coordinates, both attempts and twenty other locations
whose glyph associations remain unreviewed. Both source sets/comments and the
accepted layout were read first. The carrier was already exposed in project
inventories; this is a non-blind AI-assisted development review.

## Complete native scope

Both source page headers are present. All 22 locations are present in each
edition, with matching native kinds and relative locators. The packet preserves
the distinct `Eva-` and `EvaT` alphabet headers, source hashes/URLs, source-file
line numbers, full native strings, free comments and extended/uncertain notation.
Nothing is converted or corrected.

| Native kind | Location numbers | Records in each edition | Identical/different native texts |
| --- | --- | ---: | ---: |
| Cc | 1, 22 | 2 | 0 / 2 |
| Ri | 2–9 | 8 | 1 / 7 |
| Ls | 10, 11, 13–21 | 11 | 5 / 6 |
| La | 12 | 1 | 1 / 0 |
| P0 | none | 0 | not applicable |

Seven native strings are identical and fifteen differ across the full packet.
These are literal encoded-text comparisons, not glyph-agreement scores or
independent witnesses. Eleven Ls records do not establish eleven separate
physical words, label objects or stars.

The publisher's [IVTFF specification](https://voynich.nu/software/ivtt/IVTFF_format.pdf),
issue 2.0.2, printed Table 9 on page 22, defines Cc as clockwise circular text,
Ri as inward radial text, Ls as star labels and La as another astronomical or
cosmological drawing-element label. Table 8 on page 21 describes relative
locator codes. Those categories are source annotations; their meanings do not
verify particular image glyphs, reading directions or semantic content. Both
pages were rendered and visually inspected; the PDF SHA-256 matches the accepted
[page-convention record](../pilot/NATIVE_PAGE_CONVENTIONS.md).

ZL's source comments locate the radial sequence's beginning near 10:30 and refer
to ThP ordering. Its two circular strings contain 09:30 free comments. This
review preserves those source claims. It does not inspect the ThP diagram,
assign clock angles to the remaining numbered records, or adjudicate where the
circle texts begin. Relative locators also do not automatically join successive
records into one label or semantic unit.

## Image context and the fixed attempts

On 12 October 2026 (America/New_York), inspected Yale
[image 1006196, labeled 68r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006196).
The [whole-carrier overview](https://collections.library.yale.edu/iiif/2/1006196/full/!2400,2400/0/default.jpg)
matches the accepted parent image byte for byte. The native image is 7,993 ×
3,828 pixels. A single
[right-drawing window](https://collections.library.yale.edu/iiif/2/1006196/4490,380,2890,2820/full/0/default.jpg)
uses `(4490, 380, 2890, 2820)`, selected after the overview to contain the whole
circular drawing and surrounding writing. It is an inspection rectangle, not
an accepted panel boundary or exact writing mask. The viewing tool resized the
large displays; coordinates remain native source-image coordinates.

Direct observation: a face-bearing round center has a narrow writing band,
while a larger writing band encloses the whole drawing. Oriented rows extend
between the bands, with pointed yellow/brown forms in intervening sectors.
A vertical crease crosses the drawing rather than separating the entire right
field. This supports the broad native field proposal without equal-width panels
or a one-crease/one-page rule.

The two attempts were selected as the first and last native Ri records before
viewing pixels. No text-agreement/readability condition or replacement locus
was used. Each has one native-resolution detail; all requests succeeded, and
no extra detail or rotated derivative was inspected.

| Fixed native key | Candidate placement | Detail rectangle | Outcome |
| --- | --- | --- | --- |
| f68r3.2 | Upper-left inward diagonal row, near the source-described 10:30 area | `(5040, 770, 780, 900)` | Provisional compatible; uncertain spacing unresolved |
| f68r3.9 | Nearly horizontal row west of the center | `(4730, 1660, 1000, 350)` | Provisional compatible; exact glyphs/boundaries unresolved |

In the [first detail](https://collections.library.yale.edu/iiif/2/1006196/5040,770,780,900/full/0/default.jpg),
the diagonal writing descends rightward toward the central band. Its outer end
begins with an elevated looped form followed by lower curved strokes, with
larger gaps between later stretches. The native start-location comment and
broad shape/order cues support this candidate. ZL `ykeo,she` versus IT `ykeoshe`
remains in the packet; visible spacing alone does not decide that division.
No complete glyph-by-glyph comparison or exhaustive alternative placement
review was made.

In the [last detail](https://collections.library.yale.edu/iiif/2/1006196/4730,1660,1000,350/full/0/default.jpg),
five broad clusters lie on the horizontal stretch. The second has a conspicuous
descending stroke and elevated looped form; the last has another elevated looped
form. Pointed forms lie below the writing. These cues are compatible with both
sources' `dchey.qokeey.dcheey.daiir.otchal`. Five visible clusters are not a
linguistic word-count assertion, and source equality does not certify a reading.
The placement was not inferred from an assumed sequence of clock angles.

## Verification and remaining work

The metadata verifier reconstructs the complete source packet, checks immutable
plan/packet Git bytes, preserves both attempts and all twenty unreviewed keys,
enforces provisional scope, and validates service identities, URLs and native
window bounds. With the local directory it additionally checks every downloaded
file and rendered specification page by size, SHA-256 and bitmap dimensions.
The maintainer's 12 October recheck also retained a second 887-byte service
response, SHA-256 `9b1050cc0be3e33ca6c441d352a12f9c448bd5d78e681593dcaa60334ab1ff38`.
Only the profile format-list order differs (`jpg,tif,gif,png` versus
`tif,jpg,gif,png`); all other parsed metadata agrees and all four image
derivatives match exactly. The JSON preserves the original inspected response
pin and the dated alternate receipt. This variation does not strengthen the
image association or indicate changed pixels.
The PNG header check supplements the existing JPEG/GIF helper; all actual
local bindings pass. These checks establish metadata/provenance consistency,
not the correctness of a visual judgment or independent exposure history.

```sh
python3 scripts/build_f68r3_review.py --check research/panel-regions/f68r3-native-review.json
python3 scripts/verify_f68r3_review.py
python3 scripts/verify_f68r3_review.py --local-directory PATH_TO_RETAINED_LOCAL_FILES
PYTHONPATH=tests python3 -m unittest test_f68r3_review
python3 scripts/build_68r_review.py --check research/panel-regions/f68r-p0-review.json
```

Eight focused tests pass for complete source scope, zero P0 preservation,
missing/extra/duplicate/reordered/nonexistent records, required editions/headers,
native kind/locator and verbatim annotation retention, attempt/coverage loss,
false verification promotion, image request geometry/identity and PNG headers.
The accepted nine-record P0 checklist remains unchanged and reproduces.
All 760 tests pass after accepted-main integration: 751 standard tests,
including the eight focused cases, plus nine script tests. A separate extraction
from physical source-file lines also matches all 44 complete native readings,
kinds, locators and source-file references. Frozen plan/packet bytes remain
unchanged, and all local image/specification bindings verify.

All three native panel names preserve the same `yale-leaves:68` carrier
dependency. The source packet and compatible proposals supply review context;
they do not resolve the pilot-readiness blocker, enter statistics, create
untouched evaluation material or validate a decoding rule. A specialist should
check the complete anchor rows, alternatives and uncertain spaces, then the
remaining circular/radial/label records. Preserve unresolved glyphs and exact
region/topology dependencies before defining a candidate-specific corpus.
Images, rendered PDF pages and the specification bytes stay local. No source
correction, language identification or translation is proposed.
