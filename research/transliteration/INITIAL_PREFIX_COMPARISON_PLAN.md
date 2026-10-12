# Same-page initial-shape comparison plan

## Question and prior exposure

The initial-prefix image review leaves `f78r.21` unresolved between ZL's
`lchedy` and IT's `qchedy`. Do source-agreed initial `l` and `q` examples on the
same page provide useful shape comparisons? The full f78r image, the disputed
crop, and both transcriptions were already viewed. This targeted follow-up is
not blind or confirmatory, and agreement between related editions is not glyph
ground truth.

## Fixed comparison rule

- Use the pinned ZL3b and IT2a source bytes and the existing native tokenizer,
  retaining exact locus identifiers and source annotations.
- Restrict reference candidates to present regular P0 loci on `f78r` with a
  first token that is nonempty, readable, free of alternative readings, and
  plain case-preserved ASCII under both split and join spacing policies.
- Require both editions and both policies to have the identical first-token
  string, beginning with literal `l` or `q`. A later ambiguous token does not
  exclude a reference initial, but its source uncertainty must remain recorded.
  This reference rule differs explicitly from the whole-locus rule that
  selected the original two disputed cases.
- Sort by numeric locus and select the first qualifying `l` example and the
  first qualifying `q` example. Source screening identifies `f78r.43`
  (`lchedy`) and `f78r.4` (`qokeedy`) respectively. Do not replace a difficult
  reference after inspecting its image region.
- Inspect row contexts and beginnings at native pixel resolution, preserving
  neighbors to support a provisional row match. Compare loop/crossed-top form,
  stroke direction and extension below the neighboring low forms. Avoid
  numerical classifications without a reproducible segmentation rule.

## Record and limits

Link the exact Yale regions and record inspected bytes and dimensions. Retain
both source strings and file line numbers; publish original observations and
separate their interpretation. If either reference row cannot be aligned, keep
the disputed reading unresolved. A resemblance can support a provisional
preference but cannot certify a glyph-family boundary or correct the source.

This compares samples from one page, not independently established writing
hands or source accuracy. No inference about phonemes, language, plaintext or
translation follows. `may_apply_as_source_correction` remains false. Independent
region and shape review is required before any versioned correction.

Role: contributor under the continuing Voynich goal, using the isolated
voynich-prefix-reviewed checkout and verified `tobrien6` account. The separate
maintainer retains merge ownership. This extends draft PR #46 rather than
opening an equivalent contribution.
