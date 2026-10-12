# Residual paragraph-end image pilot plan

## Question and prior exposure

The generic-P context audit retains 38 P0 end-mark disagreements outside its
exact centred-line pattern. What visible layout evidence bears on the first
three discordant pages in that residual set?

The earlier three-page pilot covered 9r, 16r, and 18r, all within the centred-line
pattern. This sample broadens image inspection to the residual contexts. The
source metadata have already been explored, and the samples are purposive.
Neither is independent confirmation of a decipherment or a new untouched
evaluation set.

## Fixed selection before opening images

Use the exact `generic_p_context.json` report from PR #45. Select contexts whose
`following_centered_locus_is_separate_paragraph_in` is null. Sort their distinct
page identifiers by numeric folio, then literal identifier, and select the
first three: `f19v`, `f24v`, and `f26v`. Review every residual end-disagreement
key on those pages: `f19v.13`, `f24v.11`, and `f26v.2`, `.4`, `.6`.

Use only unique exact standalone Yale labels in the accepted image index.
Keep unsupported or ambiguous mappings unresolved without replacing a selected
page. Download 2,200-pixel-bounded derivatives, retain stable source links, and
record local byte fingerprints and dimensions. Images stay local.

## Observation and disposition rule

Retain source context across all present generic P subtypes, the original mark
differences, and the immediate next encoded locus in each source. Count and
order visible writing rows separately from source-locus counts. State drawing
interruptions, block separation, short or indented rows, and any obstacles to
associating source loci with physical rows.

Record direct observations separately from inferred grouping. A supported
visual boundary requires an unambiguous source-row association and clear block
separation; otherwise retain the division as unresolved. A short line alone
does not settle it. Do not infer absent text, correct the pinned sources,
transcribe glyphs, or assign semantic readings. These are AI-assisted initial
observations, with independent human review and glyph-level alignment pending.

## Provenance and scope

Record the generic-P audit and image-index fingerprints, source identities,
selection-plan commit, all five selected contexts, image exposures, uncertainty,
and explicit dispositions. A checker verifies source metadata and local image
fingerprints only; it cannot validate visual judgments. No manuscript-wide
annotation accuracy or paragraph interpretation follows from this sample.

Use the verified `tobrien6` owner/maintainer contribution scope and isolated
checkout. This follow-up depends on PR #45; preserve its original analysis
choices and report, and submit a distinct topic PR. The established maintainer
workflow handles merge decisions.
