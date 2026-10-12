# Terminal-folio source and image intake plan

## Question and fixed scope

What can be established about the final numbered recto/verso and adjacent
flyleaf without silently resolving the legacy catalog's `117v` label?

Use the fixed Yale labels `116r`, `116v`, and `[Back flyleaf recto]` from the
accepted image index. Preserve their exact canvas identifiers and require one
matching index record per label. The flyleaf is a distinct image reference; do
not assign it a numbered transcription page or a `117` foliation alias.

## Source intake

- Verify the five accepted source pins: ZL3b, IT2a, GC2a, RF1b-full and
  RF1b-basic. Preserve their alphabets and the RF derivation relationship;
  do not treat five file versions as five independent manuscript samples.
- For the exact native page IDs `f116r` and `f116v`, distinguish absent headers,
  headers with no present loci, and pages with present records. Report every
  present/nonexistent locus identifier, file line number and subtype.
- Keep the source `Lx` record apart from ordinary P0/P1 paragraph selection.
  Record native payload outside free comments for `f116v` only, with the source
  comment-presence flag. A stored locus is not automatically one physical row
  or a complete transcription of the writing visible on a page.
- Include an exact `f117v` lookup as an absent-label control. Absence in a
  transcription does not prove loss of a physical leaf. Do not apply a numeric
  offset, infer an alias or supply a translation.

## Image observations

Inspect the three full images and source-linked native-pixel regions for the
recto's folio numeral and the verso's upper writing. Record image dimensions,
hashes and region coordinates. Report visible layout, apparent horizontal
writing rows, and uncertainty separately from source statements.

The legacy Yale catalog describes a three-line presumed key at `117v`; the
publisher describes four writing rows at `f116v`, with one marginal row and
three in the ordinary text frame. Compare these limited descriptions without
using a row count to prove or refute an alias, reinterpret a catalog subset, or
validate a claimed key. No new glyph reading is required by this audit.

## Exposure, role and next test

Both source files and existing terminal-image observations have already been
exposed in this project. The source coverage and publisher description were
inspected before this image pass. This is not blind independent validation.

Role: contributor for the user's continuing Voynich contribution goal, using
verified `tobrien6` and an isolated checkout. The account matches the upstream
owner and has admin/maintain/push permissions; the separate maintainer retains
merge ownership. Submit a focused PR and leave the alias registry unresolved.

The next step is an explicit documentary correspondence or independent
scholarly review of the legacy reference. Source/header coverage and a matching
visual description cannot silently promote an unresolved alias.
