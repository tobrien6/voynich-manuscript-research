# Exploratory catalog-section prefix analysis plan

Recorded on 2026-10-11 (America/New_York), before executing this section analysis.
The sources and pooled position results are already exposed. This is an
exploratory robustness check, not a held-out decipherment experiment.

## Question and scope

Do literal EVA first-slot `q` and `y` contrasts have the same direction across
Yale's six catalog ranges, after separating source-marked paragraph starts?
This extends the [pooled position analysis](POSITION_EFFECTS.md) and complements
[PR #28](https://github.com/tobrien6/voynich-manuscript-research/pull/28), which
stratifies by source Currier labels and paragraph marks. Section ranges and
source Currier labels are distinct classifications; neither identifies a
language, semantic topic for every locus, or causal text-production mechanism.

## Fixed choices

- Use the pinned ZL3b and IT2a files, with the accepted reader and token policies.
- Select shared present P0 locations with a locator in `@`, `+`, or `*` in both
  sources. Exclude same-line fragments jointly; report every excluded key.
- Assign numeric source page names, retaining recto/verso and panel suffixes,
  to the six ranges reported in [Yale's catalog, S002](https://pre1600ms.beinecke.library.yale.edu/docs/pre1600.ms408.HTM):
  I: 1–66; II: 67–73; III: 75–84; IV: 85–86; V: 87–102; VI: 103–117.
  This is a source-label grouping, not a verified image-region alignment.
  Non-numeric `fRos`, foliation gaps, and out-of-range labels remain unassigned.
  Do not infer an alias for `fRos` or legacy 117v. Retain exact page names and
  unassigned reasons in the report. Do not invent records for missing leaves.
- Within each source, divide each catalog group by presence/absence of `<%>`
  outside free comments. Paragraph assignments may differ between sources.
  Retain all seven groups and both paragraph states, including empty cohorts.
- Run split/join uncertain spaces and exclude/first-choice alternatives.
  Preserve original slots; exclude unreadable or empty readings. A first-slot
  contrast requires a retained original first slot and another retained token.
- Features: literal representation prefixes `q` and `y`, preserving case,
  ligatures, and high-ASCII notation. No glyph or phonetic identity is inferred.
- Reuse the accepted equal-locus-weight contrast and within-locus permutation
  routines: first-slot feature minus the mean feature of the other retained
  tokens. Report exact conditional expectation/SD and 199 shuffle differences
  per feature, seed 20261011. These are conditional exchangeability controls,
  not independent-folio sampling errors. Report every cohort and policy; tails
  are exploratory, dependent, coarse (minimum 0.005), and multiplicity-unadjusted.
- Summarize the primary split/exclude contrasts for both sources. Retain the
  full reports, eligible counts, page-name counts, source Currier labels, source
  paragraph counts, selection digest, and source hashes. Report disagreements
  and small/empty cohorts without promoting a favorable subset.

## Limits and next test

Numerical foliation does not establish the catalog's subject attribution for
individual drawings or text. Panels and repeated loci on a shared leaf do not
constitute independent manuscripts. Catalog Part VI's 117v endpoint remains
inconsistent with the digital manifest's 116v endpoint; this analysis does not
resolve it. A section/paragraph contrast cannot distinguish annotation,
scribal, layout, or linguistic mechanisms. Subsequent candidate testing needs
an image-supported unit definition, recorded exposure, and a frozen evaluation
split before fitting or claiming a reading.
