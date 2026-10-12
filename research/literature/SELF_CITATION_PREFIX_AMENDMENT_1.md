# Pre-measurement amendment 1

Recorded 2026-10-12 at 05:43:17 UTC. The original plan/protocol at commit
`586d4b50e155880cd5fb9c7f554c22b16b3dd046` remain in Git history; the
[original plan](SELF_CITATION_PREFIX_PLAN.md) stays byte-identical. No new target
or seed-ensemble prefix measurement had begun at this amendment. Prior manuscript,
source-code and seed-19 output/count exposure remains disclosed.

## Observer snapshot and adaptation

The [current protocol](self-citation-prefix-protocol.json) pins corrected
PR #100 head `d86cccdc0afd19ebeea8b4de3f3068294c87d05f` and both helper files.
The changes to those files add compiler-option filtering and producer/runtime
guards; the reused pure helpers' observation/configuration behavior is unchanged.
The superseded snapshot is retained in the protocol and original commit.

This experiment reuses only `instrument`, `trace_events`, `row_ledger`,
`configuration` and `canonical`. Its **own producer** explicitly targets Java
17.0.16, seeds 1-31 and the cohort-derived row count. It does not invoke or
generalize the parent `observe()`/`replay()` producers, whose guard contracts
remain Java 22.0.2, seed 19 and 1,200 rows. The minimal environment contains only
PATH, LANG, LC_ALL and TZ, so compiler/VM injection variables are not inherited.
The exact previously verified author-source manifest is also pinned before use.

## Undefined cases

If a target stratum or **any** matching seed-stratum is empty, that particular
comparison's range and compatibility status are undefined. All 31 seed cases
remain recorded; no undefined value is dropped to construct a smaller range.
Other comparison points remain available. The overall all-32 compatibility
criterion is undefined whenever one comparison is undefined. Execution coverage,
reporting coverage and numerical definability are separate report fields.

These are guard/provenance changes and an explicit treatment of the original
empty-stratum rule. Source selection, all generation properties/overrides, seed
list, statistic and finite-range membership criterion remain unchanged. This
amendment still establishes no untouched split or verified correspondence between
model contexts, native annotations, physical rows or manuscript glyphs.
