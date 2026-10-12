# An output-preserving bridge to generator paragraph flags

Two fresh instrumented runs preserved the complete supplied 1,200-row
self-citation output byte-for-byte while exposing all **1,199 generation-call
events**. Their events and row ledgers also match exactly. This provides model
context metadata for later measurements; it does not compare the mechanism
with manuscript data or supply a decoding or translation.

The [trace plan](SELF_CITATION_TRACE_PLAN.md) was committed before execution.
The source and saved output had already been exposed in the
[source-build replay](SELF_CITATION_REPLAY.md), so this is a software observation
follow-up, not a registered manuscript hypothesis or untouched evaluation.
The [complete record and ledger](self-citation-row-trace.json) preserve the
two runs, every output row, source/build identities and acceptance checks.

Review corrected the parent replay's compiler-option filtering. The initial
[trace record](https://github.com/tobrien6/voynich-manuscript-research/blob/b71d705cfefc8ffc2cc214a1908d7f1ed62ec0bc/research/literature/self-citation-row-trace.json)
remains available. This observer now uses that corrected shared environment
helper, pins its bytes to the control producer, and rejects changed build/JVM
options or locale declarations. Two fresh reruns preserved every ledger entry,
count, source/class/configuration identity and output byte. The current record
refreshes observer/helper/control-report and local-log provenance. All four
traced executions, across this validation update, matched the same supplied file;
no generation parameter or comparison was changed from an observed outcome.

## Observer and control

Copy author release commit `9e98c9122a0f490905e8b66f3911fc7ce095fd26` into a
new local source directory after verifying the original checkout. Insert one
`System.err.println` immediately before `generateLine` in
[`generateText`](https://github.com/TorstenTimm/SelfCitationTextgenerator/blob/9e98c9122a0f490905e8b66f3911fc7ce095fd26/source/src/main/java/de/voynich/text/SelfCitationTextGenerator.java).
It prints the output index, the actual paragraph-initial/final arguments, and
the source page/paragraph counters. It does not add random calls, change
variables, alter accepted groups, or transform output strings.

The observer requires exactly one insertion anchor and verifies that all
other copied source bytes remain unchanged. It records both source hashes;
the original main file has SHA-256
`7afa236373a997d2e2ccef9a8e7ee799c5766b63ddf161bab8b72ce0f3bbf1e9`,
and the instrumented file has SHA-256
`d37385c0340cf6c4faa94382ff4b1dc3ea2138c553a65769461d1e6fd45977cc`.
Only `SelfCitationTextGenerator.class` differs in the compiled inventory.
Third-party source, instrumented code/classes, traces, logs and generated
text stay local; this repository contains the original observer and metadata.

Use the preceding full-case configuration and exact Java/compiler binary
fingerprints and version outputs, with the same Java 8-target build settings,
JVM options and locale. Both processes exited zero without timeout. Their
complete output SHA-256 remains
`a9f8237c9d7428ed148718d5aef2563a220b0df3fbc137eea197751af8ce2956`,
equal to the unmodified runs and supplied artifact. Equality includes comment
headers; no projection or text repair was needed. The original checkout
remained unchanged after both runs.

## Ledger contract and observations

The ledger uses zero-based generated-row indices and one-based native
file-line numbers. Each record includes the byte interval of the row excluding
its line ending, its SHA-256, and a native single-space-delimited token count.
The parser accepts the pinned lowercase ASCII output shape and rejects
unsupported notation/spacing rather than normalizing it.

| Ledger population | Count | Context treatment |
| --- | ---: | --- |
| Initialized input row | 1 | No generation call; model paragraph flags and counters are null |
| Newly generated rows | 1,199 | Complete ordered unique call events supply flags and counters |
| Total saved rows | 1,200 | Every native row, offset and hash is retained |
| Calls with paragraph-initial argument true | 231 | Source-program argument, not a manuscript annotation |
| Calls with paragraph-final argument true | 232 | Source-program argument, not a reconstructed paragraph count |

The initialized row is the source's trimmed manuscript-derived input attributed
to `f103v.P.9`. It must remain input reuse with unknown flags; do not infer a
paragraph-start value for it from its location in the output. The two repeated
runs produce one identical model sample, not independent manuscript evidence.

Counters are captured **after** the generator's boundary bookkeeping and
**before** the row-generation call. For example, a final call may have counters
reset to zero. These values must not be reinterpreted as physical page positions
or complete paragraph memberships without reviewing the source state machine.
Generated rows, source-defined algorithmic segments, IVTFF P0 loci, actual
manuscript lines and glyphs remain different units.

Both event sequences have canonical SHA-256
`25192bc288a4ee0de0060591eb7c59070cd6774a8ff3f2bba9ec8706403682a2`;
both ledgers have canonical SHA-256
`973fe5642975181ec5570d76b5f8406a34d343bc9ae0f73334f55c1542904680`.
Canonical serialization is UTF-8 JSON with sorted keys, compact separators and
one final LF. Process stderr contains 1,199 versioned events and no additional
diagnostic lines in either run; full log fingerprints remain in the record.

## Reproduction and next use

The observer uses the accepted source-build report as its control and an
unchanged local author release checkout. Supply the same Java installation
used by that report and new output/work paths:

```sh
python3 scripts/trace_self_citation_rows.py \
  --reference PATH_TO_PINNED_RELEASE \
  --java-home PATH_TO_RECORDED_JAVA \
  --work PATH_TO_NEW_TRACE_DIRECTORY \
  --output PATH_TO_NEW_TRACE_RECORD.json
PYTHONPATH=tests python3 -m unittest test_self_citation_trace test_self_citation_replay -v
```

Thirteen focused tests passed. Synthetic fixtures verify a single reversible
insertion, missing/duplicate anchors, event coverage/order, literal booleans,
nonnegative counters, native byte offsets, unknown initialization flags,
unsupported spacing and missing rows. Existing configuration/projection and
failure-retention tests remain in use, with corrected compiler/VM environment
filtering, exact version tokens and control-producer/executable-option guards.
The two final actual Java runs establish
the stated byte-preservation and repeated-event result on this runtime.

This is an observation bridge, with no new prefix/order scores, seed
distribution, model fit, source-label transfer, glyph equivalence or evaluation
split. A later candidate comparison must specify compatible measurements and
units, initialization exclusions, settings/seeds, exposure, controls and failure
criteria separately, following the [comparison requirements](COPYING_MECHANISM.md)
and [decipherment protocol](../DECIPHERMENT_PROTOCOL.md).
