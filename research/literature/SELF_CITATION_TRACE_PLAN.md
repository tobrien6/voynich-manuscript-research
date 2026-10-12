# Observation-only generator row trace plan

The [source-build replay](SELF_CITATION_REPLAY.md) reproduces the supplied
release file, but that saved text omits the paragraph flags used by generation.
This follow-up records those flags before `generateLine` without drawing a
mechanism comparison or claiming a manuscript annotation. The source and
output are already exposed. Commit this plan before running instrumented code.

## Fixed program and cases

- Reuse author commit `9e98c9122a0f490905e8b66f3911fc7ce095fd26`, the full
  executable configuration, Java 22.0.2 and the preceding direct Java 8-target
  build settings. Do not alter any generation property or algorithm.
- Copy the source into a new local build directory. Require exactly one known
  insertion anchor in `SelfCitationTextGenerator.generateText`. Immediately
  before the call generating a row, print only its zero-based output index,
  `isParagraphInitial`, `isParagraphFinal`, and source page/paragraph counters
  to stderr with a versioned tab-separated prefix. Do not add random calls,
  mutate state, change accepted groups, or modify the generated text.
- Record original/instrumented source hashes, build/class identities, effective
  configuration, JVM settings, exit outcomes, and complete trace/log hashes.
- Run the 1,200-row seed-19 case twice in fresh JVM processes. Keep the same
  save-path/filename overrides and environment controls as the unmodified replay.
  Retain failures; do not select another seed or settings from the outcome.

## Acceptance criteria and row bridge

Accept a trace only when both processes finish with 1,200 output rows and both
complete output files exactly match the unmodified release-19 result and the
pinned supplied artifact. Require complete, ordered, unique events for every
newly generated row, and identical event/ledger content between repeats.
No output divergence may be repaired by removing headers or normalizing text.

Retain all 1,200 rows in a ledger bound to the complete output hash. The one
initialized row is input reuse, with unknown/null model paragraph flags rather
than an inferred annotation. The other 1,199 rows obtain flags directly from
the observed call arguments. Preserve native file-line numbers, byte offsets,
row hashes, and space-separated token counts. Validate the pinned plain ASCII
output shape; do not silently repair spacing or unreadable material.

The counters are the program's values after its boundary bookkeeping and
before generation, not independently reconstructed page/paragraph memberships.
All identifiers refer to generated output rows, not manuscript folios, IVTFF
P0 loci, physical lines, glyphs, languages or verified manuscript boundaries.

## Scope

Publish only the observer, identities, original metadata ledger and method.
Third-party source, instrumented source/classes and generated text stay local.
This proves neither a decoding rule nor a mechanism fit. Prefix/order statistics,
manuscript comparisons, seed distributions, glyph-unit equivalence and any
evaluation split require a separate specified experiment and exposure record.
