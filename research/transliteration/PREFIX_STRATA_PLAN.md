# Exploratory prefix-position stratification plan

Record these choices before running the stratified analysis. The preceding
position results have already exposed the full corpus; this is an exploratory
robustness check, not an untouched confirmation or a decipherment test.

## Question

Are literal EVA `q` and `y` boundary contrasts still visible when source-marked
paragraph starts and source Currier labels are separated, and same-line fragments
are excluded? This check focuses on prefixes; the separately developed
first-token-length experiment is outside its scope.

## Fixed choices

- Use the pinned ZL3b/IT2a pair and all four uncertainty policies from
  `POSITION_PLAN.md`; do not add RF as an independent replicate.
- Select locations present as P0 in both sources, with a locator in `@`, `+`,
  or `*` in **both**. This excludes `=` fragments. Preserve original identifiers
  and publish the selected-location digest and counts removed by this rule.
- Within each source/policy, partition by the effective source `L` metadata
  label, retaining unset and any other labels explicitly, and by presence or
  absence of the source `<%>` paragraph-start mark outside free comments.
- Report every combination of observed labels and both paragraph states,
  including empty or non-estimable cohorts. Do not choose a minimum sample
  threshold or drop unfavorable groups after inspecting results.
- Features are the literal `q` and `y` prefixes only. Retain case and ligature
  representation conventions. Do not infer glyph, phonetic, or semantic identity.
- Use original first and last retained boundary-slot eligibility, equal locus
  weighting, exact conditional expectation/variance, and 199 within-locus
  shuffles (seed 20261011), as in `POSITION_EFFECTS.md`.
- Publish denominators, exclusions, controls, all shuffled contrasts, source
  hashes, and two-sided exploratory tails. No comparison is multiplicity-adjusted
  or an independent replication of another treatment on the same data.

## Limits

Source `L` values are Currier labels, not identified natural languages. Source
paragraph annotations are not independent visual verification. The locator
restriction removes a known layout ambiguity but does not reconstruct physical
lines. Any remaining boundary pattern constrains the specified exchangeability
control; it does not establish a reading or translation.
