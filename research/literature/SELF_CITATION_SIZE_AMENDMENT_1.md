# Exact-size replay amendment 1: accepted parent integer serialization

The original [plan](SELF_CITATION_SIZE_PLAN.md), pre-measurement implementation
and first result remain immutable. This amendment adopts the accepted PR #137
repair that replaces process-wide integer conversion guard changes with local
large-decimal formatting/parsing. It changes software/provenance identities;
it changes no statistic, source, selection, count policy, size support, weighting,
seed, generation receipt, null range, effect or decision convention.

## Original evidence and accepted parent

The plan was published at `75c462c4e52866c05fde302934b85b2bfffa8476`, followed by
the tested implementation `8c9e3d7186d16ce600137ed779a491e2e7f489aa` before first
conditional measurements. The first reviewed result head is
`baf80300e21652cb920d6a81ab8862f9baa2eeac`.
The exact original 65c9... pin manifest and first parent/size reports are retained
in [inert snapshots](frozen/), with compressed and decompressed fingerprints in
the [transition record](self-citation-size-amendment-1.json). Original source
texts are retained for AST comparison, not executed as experiment producers.

PR #137 was reviewed at `bb15b5a35ef9404bd2556a8939d24e5bb0e74e93` and merged
as `8a08e771936e05fb3d8f7e283fe9e7a0cb206e89` under the
[recorded maintainer decision](https://github.com/tobrien6/voynich-manuscript-research/pull/137#issuecomment-6121262927).
Its effective producer SHA-256 is
`fa01c8d9f44527895b9242302ac6158a54958b97f41fc1617b287693247c878f`;
its complete effective report is
`113b4b407691c3765e949de5f8390703bf0fdd94cfa3d6d9a30ed05790ff6829`.
These are accepted identities, not a moving unreviewed branch.

## Exact allowed transitions

The original parent report has SHA-256
`f23c65bc2b7830522fe4e24f710c266d2f81ad0ef69d46636106c1a5cb9c7b8d`.
A complete scalar-type-preserving comparison with the effective accepted report
must differ **only** in `implementation_sha256`. Original/effective parent
source ASTs must preserve every pre-existing function except `packed`/`unpack`;
the only added functions are local decimal formatting/parsing. The independent
checker similarly preserves its scientific functions and replaces its parser.
No snapshot source text is executed for this comparison.

The exact first size report has SHA-256
`df4b1f52137311083e6da69814ec6f6fc6f2d86b81251ffebf86cea9f46faf61`.
Effective replay must differ only in four top-level provenance fields:
`input_pins`, `pin_manifest_sha256`, `implementation_sha256` and
`parent_report_sha256`. Every other scalar, count vector, missing-size entry,
cohort key, source weight, standardized seed score, exact endpoint/gap,
comparison flag and original generation receipt reference must remain identical.
The accepted parent/source/transition/snapshot identities are explicitly pinned
in a new effective manifest; the original manifest and plan are preserved.

## Validation and limits

Before publication, validate both archive hashes and decompressed bytes, AST
allowances, complete parent/result comparisons, all relevant tests and full
31-run native replay. Check the independently written literal/moment/weight
checker under the unchanged interpreter integer-string limit. Reject any
scientific or non-allowlisted provenance drift; do not silently repin or tune
results to match a revised implementation. Record effective manifest/producer/
report fingerprints and exact ready head with the completed checks.

This is maintenance after the original numerical result. It is not a new
pre-measurement timestamp, new evaluation, new generator execution or replacement
of the earlier exposure record. Full-cohort ranges remain undefined, and the
predeclared 1,426-key cohort retains its two inside-range and 22 above-range points.
The finite-range and encoded-unit limitations remain unchanged.
