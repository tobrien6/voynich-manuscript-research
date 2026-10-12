# Greedy round-trip language tool: implementation status

The [frozen plan](CURRIER_ROUNDTRIP_PLAN.md), [machine parameters](currier-roundtrip-plan.json)
and [producer](../../scripts/currier_roundtrip_language.py) preserve the work from
`codex/currier-roundtrip-language`. This contribution publishes the implementation
and its synthetic validation. The primary-table graph, longer-string counts and
results report have **not been measured or published**. Adoption of this tool
does not complete that planned study.

The producer constructs a bounded-delay graph for the declared concatenation
and greedy reversal model. Its exact integer counting and separate whole-string
reference decoder can check each other's decisions. It does not implement all
Bitrans scheduling semantics or use manuscript text. The frozen source catalog
retains artifact identities, credit and reuse limitations; raw definitions,
manual and README stay local, and author programs are not executed.

Run its synthetic checks from the repository root:

```sh
python3 -m unittest tests.test_currier_roundtrip_language -v
```

All 12 tests pass, including 45,570 exhaustively enumerated source strings across
150 invented dictionaries, additional length-four/delayed-EOF cases, shortest
state reachability, exact count mass and strict JSON. Local source-identity
checks, when their cache is available, inspect the declared primary bytes but do
not calculate the primary graph or longer-string counts.

The cleanup review also repaired output safeguards: serialization completes
before the final alias check, and entry-time/current resolved protected names
are retained even after removal or symlink retargeting. Two regressions failed
before the repair and pass afterward, including serialization failure preserving
existing output. These are pre-write checks, not atomic filesystem transactions.
Both frozen plans and the original calculation remain unchanged.

A later explicitly undertaken study can supply the pinned local references to
`--reference` and write a report with `--output`, then verify it with `--check`.
It must publish complete outcomes and keep the source restrictions and declared
exposure. No language, glyph correspondence, historical conversion or translation
result follows from the implementation or its synthetic tests.
