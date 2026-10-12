# Catalog-section paragraph-agreement sensitivity plan

Recorded on 2026-10-11 (America/New_York), before executing this follow-up.
The sources and section results in [PR #36](https://github.com/tobrien6/voynich-manuscript-research/pull/36)
are already exposed. This is a planned descriptive sensitivity analysis, not a
new held-out evaluation or candidate decipherment.

## Question

How much do first-slot q/y contrasts within catalog sections change when
locations with disagreeing source paragraph-start marks are removed?

## Fixed choices

- Start with the same pinned ZL3b/IT2a shared regular P0 locations and grouping
  rules as [SECTION_STRATA_PLAN.md](SECTION_STRATA_PLAN.md). Reuse its selection,
  tokenization, original-slot eligibility, paragraph detection, and equal-locus
  contrast functions; do not introduce a competing reader.
- Remove a selected location from both sources if their `<%>` presence differs
  outside free comments. Preserve both annotations and every excluded key.
  Do not remove an end-mark-only disagreement: this test concerns first slots
  and paragraph-start membership, not reconstruction of paragraph intervals.
- Keep the six numeric catalog parts plus the unassigned group and both
  paragraph states. Assignment remains source-label grouping without verified
  image-region alignment or a historical folio alias.
- Run every split/join uncertain-space and exclude/first-choice alternative
  combination. The agreed annotation cohort is common, but token exclusions
  may still produce different eligible sets. Do not call it fixed eligibility
  or treat annotation agreement as source correctness.
- Report each source/policy/section/paragraph feature before and after filtering,
  their difference, selected and eligible counts, removed counts, exact null
  expectation and SD, 199 shuffled contrasts, seed 20261011, and the exploratory
  two-sided tail. Reuse the accepted within-locus control; do not perform a new
  between-source or between-section significance test on these dependent data.
- Verify the complete unfiltered report against `section_strata.json` before
  comparing results. Pin that report's digest, source hashes, both selection
  digests, and all removed keys. Retain empty groups and all outcomes.
- Summarize the primary split/exclude results for both sources and the maximum
  absolute change across all declared cells. Report sign changes and small
  cohorts rather than choosing a favorable subset. Undefined effects stay null.

## Interpretation and next test

This isolates the impact of removing annotation-discordant locations under the
declared retention policies; it cannot tell which source's boundary is right or
separate annotation accuracy from content/layout correlated with exclusions.
The same data recur in multiple analyses, and same-leaf/panel dependence remains.
Independent image review and a frozen, exposure-aware candidate test remain
necessary before assigning meaning or claiming a decipherment.
