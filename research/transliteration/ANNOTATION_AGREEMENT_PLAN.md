# Paired paragraph-annotation audit plan

Record these choices before producing the audit. Existing full-corpus analyses
have exposed these public sources; this is a descriptive source-agreement audit,
not a held-out experiment or a decipherment candidate.

## Question

Do the pinned ZL3b and IT2a files place paragraph-start and paragraph-end marks
on the same shared P0 loci? Do their effective Currier labels and locators agree?
Source-specific paragraph strata need these denominators before they can be
treated as comparable cohorts.

## Fixed choices

- Use the accepted IVTFF reader and hash-verified source catalog. Select exactly
  ZL3b and IT2a, keeping other editions outside this paired audit.
- Match by page name and locus number. Require present P0 loci in both sources;
  report each source's P0 count and identifiers excluded by this intersection.
- Report both the full shared P0 cohort and its subset with locators `@`, `+`,
  or `*` in both files. Preserve excluded identifiers. This subset removes
  same-line fragments without claiming to reconstruct physical lines.
- Detect `<%>` and `<$>` after removing free comments, with no tokenization,
  case conversion, spacing policy, glyph interpretation, or inferred marks.
  Retain marker counts as well as presence; report repeated marks explicitly.
- Compare effective `L` metadata supplied by the shared reader, including
  inherited text-tag changes. Preserve absent values as JSON null and retain
  any other literal labels rather than mapping them to A or B.
- Publish complete categorical tables, agreement/disagreement counts and
  denominators, sorted cohort digests, and every discordant locus with both
  source identifiers and physical file line numbers. Include all Boolean cells,
  including zero counts. Do not infer that an absent mark means a visually
  verified non-boundary.
- Produce no significance test, confidence estimate, token-position effect,
  corrected transcription, image alias, or claim that one source is right.

## Evidence and next step

The publisher's IVTFF format definition, document issue 2.0.2 dated 2025-07-08,
section 6.9, assigns paragraph definitions to the transcriber and permits
differences between files. Section 6.8 defines metadata inheritance; Table 6
defines `L`; Table 8 defines locators. Use the exact source hashes and existing
source credits. Image review of discordant loci is the next step, with both
annotations retained until separately adjudicated.

## Role and scope

Role: owner/maintainer for this focused contribution. The user requested work on
this project; the authenticated GitHub login and upstream owner are `tobrien6`,
and the repository API reports admin/maintain/push permission. Submit through a
topic branch and PR, allowing the existing maintainer workflow to handle merge
decisions. Use only `tobrien6` for GitHub activity. This checkout is isolated
from the other active research contributions.
