# What the generator's boundary counters mean

All **1,199 generated-row transitions** in the accepted seed-19 trace agree
with the pinned source's bookkeeping. The 1,200 saved rows form **232
algorithmic segments** within **42 source page blocks**: 41 blocks of 29 rows
and one terminal block of 11 rows. These are program-defined units, including
one initialized input row, not manuscript paragraph or page annotations.

This closes a metadata interpretation gap in the
[output-preserving trace](SELF_CITATION_ROW_TRACE.md). Later comparisons can
use actual call flags and explicit source-defined grouping without treating a
zero counter as a physical position or a final-row flag as a complete page.
It does not establish that these units match manuscript loci, words or glyphs.

## Evidence, exposure and chronology

The [fixed plan](SELF_CITATION_BOUNDARY_PLAN.md) and offline implementation,
with nine synthetic tests, were published at
[`fab14ee`](https://github.com/tobrien6/voynich-manuscript-research/commit/fab14ee8c98b20427fea0fe4e3e52df4f2c3de24)
in PR #108 before deriving this ledger. The complete source, output and trace
were already exposed, including their 231 initial and 232 final flags. This
is a descriptive software audit of one known model sample. No Java process,
new seed, prefix statistic or manuscript measurement is introduced.

The [complete report](self-citation-boundary-state.json) pins the accepted
trace/control/producer bytes and the five author source/configuration files
used for interpretation. Author release
`9e98c9122a0f490905e8b66f3911fc7ce095fd26` supplies:

- [`generateText`](https://github.com/TorstenTimm/SelfCitationTextgenerator/blob/9e98c9122a0f490905e8b66f3911fc7ce095fd26/source/src/main/java/de/voynich/text/SelfCitationTextGenerator.java): read the initial flag, increment counters, apply boundary rules, then generate the row.
- [`StatisticHelper`](https://github.com/TorstenTimm/SelfCitationTextgenerator/blob/9e98c9122a0f490905e8b66f3911fc7ce095fd26/source/src/main/java/de/voynich/text/StatisticHelper.java): a page reset clears both counters and page-specific group/usage collections; a paragraph reset clears only its paragraph counter.
- [`Config`](https://github.com/TorstenTimm/SelfCitationTextgenerator/blob/9e98c9122a0f490905e8b66f3911fc7ce095fd26/source/src/main/java/de/voynich/text/util/Config.java) and the [executable configuration](https://github.com/TorstenTimm/SelfCitationTextgenerator/blob/9e98c9122a0f490905e8b66f3911fc7ce095fd26/executable/conf.properties): 1,200 output rows, a 29-row page-length setting, one initialized row and the pseudo random generator.
- [`PseudoRandomNumberGenerator`](https://github.com/TorstenTimm/SelfCitationTextgenerator/blob/9e98c9122a0f490905e8b66f3911fc7ce095fd26/source/src/main/java/de/voynich/text/util/random/PseudoRandomNumberGenerator.java): `rand(100)` delegates to `Random.nextInt(100)`, whose [API contract](https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/Random.html#nextInt(int)) yields integers from zero through 99.

Source bytes were checked locally against the accepted replay inventory.
Third-party source, configurations, generated text and raw logs remain local.

## Every transition and closure is retained

The initial flag reads the previous paragraph counter before incrementing it.
The final flag and recorded counters are determined after incrementing and
potentially resetting the state, before the actual generation call. Thus the
final row belongs to the block it closes even when both recorded counters are
already zero. The terminal output index forces that reset regardless of block
length. Flags on the initialized row remain null because it has no call event.

| Closure condition | Count | Counter treatment before generation |
| --- | ---: | --- |
| Page length reached, nonterminal | 41 | Page and paragraph counters reset |
| Terminal row without page-length match | 1 | Page and paragraph counters reset |
| Page length and terminal coincide | 0 | Both conditions would be retained |
| Eligible threshold branch | 190 | Only paragraph counter resets |
| All segment closures | 232 | Every final call closes one segment |

There are 411 eligible threshold calls: 190 close a segment and 221 do not.
No eligible call reaches a saturated threshold of at least 100 in this trace;
the validator would require closure there. A threshold closure identifies the
source branch from its conditions and observed final flag, without recovering
the random draw or claiming a whole-program random-call sequence.

The complete segment length distribution is retained:

| Saved rows in segment | Segments |
| ---: | ---: |
| 3 | 5 |
| 4 | 80 |
| 5 | 60 |
| 6 | 55 |
| 7 | 23 |
| 8 | 7 |
| 9 | 2 |

These 232 counts sum to 1,200 rows after weighting by segment length. The first
segment is indices 0–4 and contains the initialized row plus four newly
generated rows. Its first-row initial-call flag is unknown. The other 231
segments start with observed initial calls, explaining the initial/final flag
count difference without inventing an initialization event. No segment crosses
a source page reset.

For example, row 4 closes the first segment with page counter 5 and paragraph
counter 0; row 5 starts the next segment with counters 6 and 1. Row 28 closes
the first 29-row block with both counters 0. The terminal row 1,199 likewise
has counters 0 and 0, although it is only the eleventh row of the final block
(indices 1,189–1,199). Native row indices remain zero-based throughout.

## Reproduction, validation and next use

```sh
python3 scripts/audit_self_citation_boundaries.py --check
PYTHONPATH=tests python3 -m unittest test_self_citation_boundaries test_self_citation_trace test_self_citation_replay -v
# Optional new output; existing files and symlink/hardlink aliases are rejected:
python3 scripts/audit_self_citation_boundaries.py --output NEW_REPORT.json
```

All 23 focused tests pass. Nine pre-derivation synthetic tests cover complete,
partial and coincident terminal/page closures, threshold eligibility/saturation,
an initial-and-final call, wrong flags/counters, typed row coverage, unknown
input metadata, fingerprint drift and exclusive output creation. A tenth test,
added after derivation, independently reconstructs all 1,199 transitions from
previous-closure distances and modulo page positions, then verifies every
segment, block, closure count, length distribution and coverage sum without the
production state walk. Complete report regeneration and input identities pass.

The recorded segments belong to the program's boundary convention and known
input-dependent output. They do not validate physical manuscript paragraphs,
page lengths, glyph units, a seed distribution or a copying mechanism. A future
comparison must specify compatible units, initialization treatment, settings,
exposure and controls separately. Decipherment and translation remain the
project's objective, with no reading or meaning inferred from this audit.
