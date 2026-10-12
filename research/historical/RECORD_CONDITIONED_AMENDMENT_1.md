# Amendment 1: output protection after the first measurement

The original [plan](RECORD_CONDITIONED_PLAN.md) and
[machine parameters](record-conditioned-plan.json) remain byte-identical to
their premeasurement commits. All first measurements remain in
[PR #131's initial head](https://github.com/tobrien6/voynich-manuscript-research/commit/e0a023f36fea7104769f5dc9cd7b044cd443f231).

The [review of prerequisite #126](https://github.com/tobrien6/voynich-manuscript-research/pull/126#issuecomment-6119372286)
identified an output-guard defect: comparing resolved names alone misses
hardlinks, and a check only before computation misses aliases introduced during
it. Both assay runners now reject direct/symlink/hardlink aliases to every
protected file, checking before computation and immediately before writing the
serialized result. This is a safety repair after results were exposed, not a
change of scientific input, measured edges, metrics, null or trial selection.

The prerequisite [repair commit](https://github.com/tobrien6/voynich-manuscript-research/commit/72e6871ad695dc3c32314d36f1ae9b34fef8e232)
changes the global runner bytes and only the global report's `runner_sha256`.
The global helper, original plan, all seven underlying dependency pins, every
observation, exact mean and all forty controls remain identical. Consequently,
two of the conditional study's twelve recorded dependency hashes need explicit
migration: `scripts/historical_repeated_types.py` and
`research/historical/repeated-types.json`.

The [machine amendment](record-conditioned-amendment-1.json) retains both
original/repaired hashes and binds to the unchanged original machine-plan hash.
Only those two replacements are accepted. It also pins the entire original
global report after removing only `runner_sha256`; the repaired report must
match that scientific/metadata payload before source reconstruction. The other
ten conditional dependency hashes remain unchanged. Future drift is not
automatically accepted.

The conditional report retains the original registered dependency hashes as
well as the effective amended ones and amendment identities. Its runner hash
changes and amendment metadata is added. All conditional variant observations,
exact means, scope contributions, residuals, ratios and forty controls are
compared to the first report and must remain identical. The mathematical helper
bytes remain unchanged. Preserve this amendment and the first-result commit
when reproducing or reviewing the study; never silently refresh frozen pins to
make a changed producer or report pass.
