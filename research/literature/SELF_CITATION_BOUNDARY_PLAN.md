# Source-state audit of the accepted generator trace

Question: do the recorded call flags and counters obey the pinned generator's
boundary transitions, and which algorithmic segments can they support?

The [accepted row trace](SELF_CITATION_ROW_TRACE.md) is already exposed, including
the 231 initial and 232 final call flags. This is an offline software audit of
that one known output, not a new simulation, manuscript hypothesis, prefix
measurement, independent sample or untouched evaluation. Publish this plan
and synthetic-tested implementation before deriving the segment/page ledger.

## Fixed evidence and scope

Use all 1,200 rows of the accepted trace at merge
`0e4e99834e472a49fe9429e5f3fcaf81293665b1`. Require the complete trace,
unmodified replay receipt and both producer fingerprints below. Do not alter
the observer, source, configuration, seed, row count, text or annotations.

| Repository input | SHA-256 |
| --- | --- |
| `self-citation-row-trace.json` | `66ee19b89c3acba54112cc8a012cc3767ef0c2752a69cfd9a84e76d55e11fc91` |
| `self-citation-repeatability.json` | `a31bd822bc93546274a49db3a0fa144907c8aebf6864abf4f2230bd02d6c337e` |
| `scripts/trace_self_citation_rows.py` | `a078447279d7557d243fdce925a66749747d5c665cb69c97923a69328cf4b778` |
| `scripts/replay_self_citation.py` | `4579f7caaf75ec124a8ffcbfd53b2e173f1ea117bdf7a7ee24761e53d2ee225f` |

The source evidence is author release
`9e98c9122a0f490905e8b66f3911fc7ce095fd26`: `generateText` in
`SelfCitationTextGenerator.java`, `newLine/newPage/newParagraph` in
`StatisticHelper.java`, configuration parsing in `Config.java`, and the
`rand(100)` implementation in `PseudoRandomNumberGenerator.java`.
The pinned executable configuration sets `text.lines_per_page=29` and
`text.lines_to_create=1200`, with one initialized row. Verify all five file
identities against the accepted replay inventory. Keep source bytes local.

## Transition checks and derivation

Initialize both counters to the initialized output-row count. For every newly
generated row, preserve this exact order:

1. Read the initial flag from whether the previous paragraph counter is zero.
2. Increment both counters for the impending row.
3. A page-length match **or** the terminal output index forces the final flag
   and resets both counters before generation. Retain both conditions when
   they coincide; a terminal reset need not close a full page-length block.
4. Otherwise a final flag can occur only when the incremented page counter is
   below `pageLength-2`, the paragraph counter exceeds three, and the output
   index is below `totalRows-2`. It then resets only the paragraph counter.
   The pinned pseudo generator uses `Random.nextInt(100)` (integers 0–99), so
   an eligible paragraph counter of at least ten requires closure. This is
   the source's threshold branch, not a recovered random value.
5. Match the recorded initial/final flags and post-bookkeeping counters exactly.
   Reject any discrepancy, gap, duplicate index, wrong type or invented flag
   for initialized input. Do not repair or drop rows.

Close an algorithmic segment at each final call and a page-length/terminal
block at each forced reset. Retain all segment/block start and end indices,
row counts, initialized-row counts, closure conditions and segment membership.
Report complete count and length distributions, including zero categories.
The first segment contains initialized input with an unknown initial-call flag;
do not manufacture an event for it. No segment may cross an observed page reset.

## Validation and limits

Synthetic cases will cover normal page closure, partial terminal closure,
coincident page/terminal closure, threshold eligibility/saturation, initial-and-final calls,
wrong flags/counters, malformed/gapped indices and initialized-input metadata.
The report writer must create a new file exclusively, preserving existing
files and aliases. Check the complete report by deterministic regeneration.
Independently reconstruct all boundaries from source conditions and the trace
without using the production segmentation routine.

Publish original code and metadata only. This groups source-program output
rows; it does not infer physical manuscript pages, paragraphs, glyphs or words.
The state audit cannot establish comparable manuscript units, a copying-model
fit, seed distribution, paper-result replication, decipherment or translation.
Those remain separate experiments with their own controls and exposure records.
