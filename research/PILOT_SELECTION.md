# Pilot selection protocol

Recorded on 2026-10-11, after reading source descriptions and Yale's IIIF
manifest labels, but before inspecting any selected manuscript image.

## Question and unit

Can a small, explicitly selected set support a checkable inventory of image
identifiers, text layouts, illustration descriptions, and uncertainties across
the six illustrated/text sections in [S001 and S002](SOURCES.md)?

The unit is a **digitized surface**, identified by one Yale IIIF canvas. Ten
records do not imply ten independent physical leaves: a foldout canvas can
contain more than one folio side. Preserve Yale's complete image label rather
than inventing panel numbers or treating a composite as a single ordinary leaf.

## Selection rule

Use the catalog's Part I (1–66), II (67–73), III (75–84), IV (85–86),
V (87–102), and VI (103–117) ranges. These are reported catalog groupings,
not classifications inferred from the images.

1. In Parts I, II, III, and V, select the lowest and highest numbered canvases
   whose complete label is a standalone recto (`^[0-9]+r$`). This selects eight
   surfaces. Exclude composite/partial labels from this boundary rule even when
   they contain a later recto.
2. For Part IV, select the canvas labeled `85v and 86r (foldout)`, corresponding
   to the side associated with the catalog's nine-medallion description. Retain
   this selection even if image inspection complicates that description.
3. For Part VI, select the lowest numbered standalone recto.
4. Stop with those ten canvases. Do not replace a selected surface because its
   contents appear atypical. Record missing or inaccessible images explicitly.

The manifest labels resolve to: `1r`, `66r`, `67r`, `73r`, `75r`, `84r`,
`85v and 86r (foldout)`, `87r`, `100r`, and `103r`. Part V's latest standalone
recto is `100r`; `102r` occurs within a composite label and is excluded by rule.

## Observation method

Inspect each full surface in a Yale IIIF JPEG scaled to fit within 1600 × 1600
pixels. Describe visible text placement and illustration forms qualitatively.
Do not transcribe glyphs, assign plant species, count tokens, or infer a
translation. Record small or unclear details as uncertainties. Keep direct
image observations separate from section names reported by the catalog and
interpretive possibilities.

For each record retain the exact label, canvas and image identifiers, stable
catalog image link, full-size image URL, inspection image URL, source identifiers,
inspection date, text layout, illustration description, and uncertainties.
Images are inspected temporarily; the contribution redistributes links and
observations, not Yale's image files.

## Coverage and limitations

This purposive boundary sample gives Parts I, II, III, and V two records each,
and Parts IV and VI one each. It tests the inventory procedure and section
boundaries, rather than estimating the prevalence of features. It favors
rectos and endpoints, excludes most versos and partial/composite scans, and
does not cover every layout within a section. Catalog ranges need not be
visually homogeneous. The cosmological composite is one record, with dependent
panels; it must not be counted as multiple independent observations.

## Next test

Have another observer independently verify labels, source links, and descriptions
before choosing a broader sample. For transcription work, define panel/line
identifiers separately and compare the handling of foldouts and uncertain glyphs
across documented editions before calculating statistics.
