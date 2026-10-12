# Fixed-seed census of native generated prefix effects

This is an exploratory software-output study using the
[released generator replay](SELF_CITATION_REPLAY.md) and
[output-preserving row observer](SELF_CITATION_ROW_TRACE.md). It tests neither
a manuscript decipherment nor a held-out corpus prediction. Source rules,
the full seed-19 output and short seed-20 output are already exposed. Commit
this plan before generating the new full seed grid; do not choose settings,
seeds, features or eligibility from their observed effects.

## Fixed program and seed schedule

- Retain author commit `9e98c9122a0f490905e8b66f3911fc7ce095fd26`, the full
  executable property file, Java 22.0.2 and the reviewed direct Java 8-target
  compiler/runtime/environment controls.
- Build unchanged and observer-instrumented source once each. Require the same
  code/configuration identities as the accepted replay/trace, apart from the
  declared seed property and save-path/filename overrides.
- Use **every integer seed from 1 through 20**, in that order. Request 1,200
  rows for each. Run one fresh unmodified JVM and one fresh observed JVM per
  seed: 40 processes, with the same settings within each pair.
- Retain all outcomes. Require complete byte equality within each pair,
  successful expected row counts and complete ordered generation-call events.
  Seed 19 must also match the supplied release artifact. Failures remain
  explicit and block an all-cases-valid claim; do not replace failed seeds.

The seed grid is a deterministic sensitivity schedule, not an independently
drawn sample with calibrated sampling probabilities. Every run reuses the
same manuscript-derived initialization input; no output is a new observation
of the manuscript or evidence of untouched evaluation material.

## Eight fixed measurements per seed

Exclude the initialized row from all measurements while retaining its identity.
Partition newly generated rows by the **observed paragraph-initial call flag**
only. Retain every row in the population counts and require at least two native
space-delimited tokens for a boundary-versus-others contrast. Record excluded
row indices/reasons. This eligibility set is common to both boundaries and
both features; no boundary token is promoted or selected after seeing a value.

For each flag state, both first/last boundaries and both literal q/y prefixes,
use the existing equal-row-weight binary contrast:

```text
m = native space-delimited token count, k = tokens beginning with the prefix
x = boundary prefix indicator
D = (m*x - k)/(m - 1)
reported contrast = sum(D)/number_of_eligible_rows
```

Retain exact rational sums/means, boundary-positive counts, average other-token
prefix rates and explicit denominators. The unit is a generated output row;
space-delimited groups, algorithmic glyph segments and actual manuscript
glyphs are different units. Model call flags are not source paragraph/Currier
annotations. No manuscript cohort or natural-language label is imported.

## Reporting and interpretation

Publish all 20 seeds × eight cells, including undefined/failed cases. Summarize
the range, arithmetic mean across seed means, and negative/zero/positive sign
counts for each cell. Those are descriptive properties of the chosen grid,
not p-values, confidence intervals, Monte Carlo tail probabilities or a
goodness-of-fit score. Do not select a winning seed or tune a parameter.

Bind results to source/build/configuration identities and complete per-process
output/trace/ledger fingerprints. Keep original and instrumented source,
classes, raw configurations/logs, ledgers and generated text local; publish
only the original method and measurement records. A manuscript comparison,
ablation, calibrated predictive test, glyph reading or translation requires
a separate specified experiment with compatible units and exposure records.
