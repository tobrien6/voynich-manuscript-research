# Fixed self-citation prefix profile: exploratory diagnostic plan

Commit this plan and the [protocol](self-citation-prefix-protocol.json) before
calculating new target or simulated prefix values. Previous manuscript prefix
results, author source code and seed-19 release bytes/counts are already exposed.
This is a diagnostic of a fixed encoded-text profile, not untouched manuscript
validation, paper replication or a decipherment.

## Inputs and selection

- Reuse the pinned ZL3b/IT2a editions, accepted `plain-eva-v1` adapter and
  [conservative common cohort](../transliteration/CONSERVATIVE_PREFIXES.md).
  Retain its P0/regular-locator/at-least-two-token rule under all four
  source/spacing cases. From those keys require effective `L=B` in both native
  sources and zero drawing interruptions in every case. Preserve all selection
  counts, excluded keys/reasons and source hashes. No new row filter may depend
  on a q/y measurement or model outcome.
- Keep each source's own paragraph-start mark outside free comments. Source
  labels are not languages, and those marks are not independently verified
  physical boundaries. Do not transfer an annotation between editions.
- Reuse author commit `9e98c9122a0f490905e8b66f3911fc7ce095fd26` and its full
  pinned executable configuration. Its starting line is manuscript-derived.
  Fix seeds to integers 1 through 31, inclusive. Generate exactly the selected
  manuscript-key count plus one initialization row for each seed. Change only
  line count, seed and relative save directory/name; fit no generation parameter.
- Compile unchanged and observed source copies on Zulu OpenJDK/javac 17.0.16,
  with Java 8 target, UTF-8, annotation processing disabled and an empty external
  classpath. Use fresh directories/JVMs, en/US locale, UTC, a minimal environment,
  a 256 MiB heap and 60-second cap per process. Do not run Maven or a packaged JAR.
- The only observed-source change is PR #100's pinned pre-call stderr insertion.
  Inspect it, verify exact input/helper identities, and require all other source
  bytes to remain unchanged. For **every** seed run unchanged and observed
  programs; require identical complete output bytes before using observed flags.

## Units, statistic and all outcomes

Discard the one initialized written row from measurements, preserving its
unknown context and full input dependency. Require a complete ordered unique
trace for every newly generated row and retain native offsets/hashes. Check
strict lowercase ASCII and literal spaces. Retain generated rows with at least
two groups; preserve all shorter-row exclusions and denominators.

Partition by the directly observed `isParagraphInitial` call argument, not
inferred page counters. For each false/true group compute first and last
literal q/y prefix contrasts: the boundary indicator minus the mean indicator
over every other group in that same row, then average rows equally. Compute
the same statistic on each source's own false/true paragraph cohort under both
spacing policies. These are 32 dependent manuscript target comparisons, not
32 independent replications. An empty stratum is undefined and must stay so.

The fixed descriptive compatibility criterion asks whether each target point
falls in the inclusive min-to-max range of its matching statistic across all
31 fixed seeds. Publish every target, seed outcome, range and outside-range gap.
This range is **not** a calibrated confidence interval or predictive probability;
do not assign a p-value or accept the entire mechanism from it. A point outside
the range fails this specific finite-profile criterion, not every parameter
choice or every copying mechanism. No shuffle tail is a generator fit score.

Any failed process, timeout, missing/duplicate/out-of-order event, unexpected row
count, unsupported notation or changed complete observed output makes the full
planned comparison unavailable. Retain every failed case; do not quietly choose
another seed, repair text or report only successful simulations. Keep all
configuration, build, process, output and trace identities. Original program
artifacts and generated text stay local; publish original summaries, row/context
metadata and fingerprints.

## Interpretation limits

Source loci and generated writing rows are different units; the common contrast
is an explicitly chosen encoded-string bridge. Glyph identity, physical line
alignment and equivalence of source paragraph annotations with model flags are
unverified. Whole-locus exclusions may bias the represented manuscript. Different
row lengths and contextual mixtures remain visible, and related source/policy
results cannot create independent witnesses. The implementation includes learned
layout/frequency rules and a reused initial line, so this is not a fit of pure
copying alone. No plaintext, language, translation or paper-sample identity follows.

This creates no real evaluation split and does not relabel exposed material as
held out. A stronger candidate test needs independently checked units, complete
candidate rules, compatible controls/ablations and a separately frozen exposure-
aware split under the [evaluation protocol](../DECIPHERMENT_PROTOCOL.md).

Role: contributor using verified `tobrien6` under the continuing Voynich goal;
the account matches upstream owner and repository permissions. The assigned
maintainer owns the merge decision. Submit this diagnostic through a focused PR
with complete negative/positive outcomes, without self-approval or direct main
updates.
