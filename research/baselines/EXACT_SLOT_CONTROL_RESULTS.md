# Exact-slot predictor detects strong persistence but misses the quarter case

The fixed exact-slot previous-class model meets its original diagnostic preference
in **0/64 independent-uniform**, **0/64 quarter-persistence**, **64/64 strong-
persistence**, and **0/64 independent alternating-position** cases. The old
coarse model detects all quarter-persistence cases on those exact same datasets.
The stricter predictor's negative manuscript result therefore does not establish
absence of moderate dependence.

The slot-only model learns the constructed positional signal: F0 improves over
Q0 in all 64 alternating-position datasets under both pooled and equal-group
weighting. The old coarse previous-class model also meets its own criterion in
all 64 of these independent-position datasets. This derived comparison shows
that its earlier uniform-IID behavior was not a general independence guarantee.
The finer previous-class increment remains negative once those exact positions
are supplied. These are known-process diagnostics, not a fitted manuscript
explanation or probability/decipherment calibration.

## Fixed inputs and nominal laws

The [plan](EXACT_SLOT_CONTROL_PLAN.md) reuses the unchanged model from
[the exact-slot study](EXACT_SLOT_LENGTH_RESULTS.md): source label, exact interior
size/target slot, strength ten, shared context weight, unseen-class backoff and
original five-group-fold exclusion. No model was revised after its native losses.

The first 192 datasets are byte-identical regenerated class sequences from the
[accepted old benchmark](GROUPED_CONTROL_RESULTS.md), with all existing sequence
hashes, coarse fitted/scored records and oracles verified before fine fitting.
They have uniform classes 1..10, with direct retention probabilities 0, 1/4 or
3/4. Each innovation can repeat the previous class. The first class is uniform.
These abstract classes are not glyph widths, words or natural language.

The additional 64 datasets independently choose class 10 with probability 1/4
at even interior slots and 3/4 at odd slots, otherwise class 1. All ten predictor
classes remain; no model support was shrunk to the two generated categories.
Every slot consumes one prescribed sampler draw, with no previous-class input.
Separate case/replicate/locus SHA-256 streams retain seed 20261012 and all 64
indices. These deterministic finite streams implement the stated nominal laws;
no hash-uniformity or general independence certification is inferred.

All cases use the previously exposed primary ZL3b split metadata: **2,165** row
sizes/labels/identifiers, **86** groups, five original folds and **13,713** scored
transitions per dataset. Native classes, probabilities, gains, source bodies and
images are not used to generate values. It is a layout-specific diagnostic, with
no untouched source evidence and no new folio/text interpretation.

## All 256 results

Values below are means in bits per transition. The old coarse criterion is
reconstructed from the retained Q0/Q1 fold/group losses using its existing rule;
the [derived receipt](exact-slot-control-coarse-receipt.json) records every one
of those 256 arithmetic decisions. This display was added after scoring; it
introduces no new threshold or fitted values and leaves the frozen report intact.

| Process | Old coarse hits | Fine F1/F0 hits | Fine increment, pooled | Fine increment, equal groups | F0/Q0, pooled | F0/Q0, equal groups |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Independent uniform | 0 / 64 | 0 / 64 | -0.68854100 | -0.79632879 | -0.05183211 | -0.06598954 |
| Quarter persistence | 64 / 64 | 0 / 64 | -0.34848361 | -0.43030807 | -0.05130184 | -0.06402060 |
| Three-quarter persistence | 64 / 64 | 64 / 64 | +1.55501774 | +1.52916874 | -0.05020731 | -0.06368192 |
| Independent alternating positions | 64 / 64 | 0 / 64 | -0.00549538 | -0.00711512 | +0.17665582 | +0.16940723 |

Quarter-persistence fine pooled gains range from -0.40007921 to -0.30725665,
and equal-group gains from -0.53007412 to -0.33613976. Strong-persistence fine
pooled gains range from +1.51053107 to +1.62788895. On alternating positions,
all 64 F0/Q0 pooled gains are positive (+0.16428362 to +0.18864952), while all
64 fine previous-class increments are negative (-0.00884907 to -0.00286980).
The complete report retains every fold, group, backoff, contrast and adverse
case. There is no collection-level pass threshold or secondary decision rule.

The old coarse previous-class gain on alternating positions averages +0.05006119
pooled and meets its existing rule in all 64 datasets. Its prior independent-
uniform hit count remains 0/64. Changing positional marginals can make a
previous class informative about omitted position even under independent slot
draws. This constructed control supplies no quantitative fit to native text.

The shared fine weight prevents constant-feature smoothing gains, but does not
ensure reliable conditional estimation when previous subcells are small. Its
quarter-case losses show a concrete limitation under the specified law/layout;
they neither identify the cause of every native loss nor establish a universal
power boundary. F1 also loses against the old Q1 in all three uniform-marginal
processes, including strong persistence. Context and shrinkage both differ in
that contrast, so it is not a causal position decomposition.

## Known-process references

The first three oracles retain the old uniform ten-class marginal and known
persistence transition probabilities. Their ideal gains are zero, approximately
0.272493 and 1.839502 bits/transition. The alternating oracle compares its known
slot probabilities with **uniform binary support {1,10}**, yielding ideal gain
1-H_binary(1/4), approximately 0.188722. Its realized mean is 0.18801214.
These references differ in support and conditioning; oracle differences do
not isolate a causal source of model gain. Oracles are known-law calculations,
not parameters fitted on the scoring data or manuscript tail probabilities.

## Freeze, artifacts and reproduction

The plan was pushed and remote-verified at
`e4ac9bf459e8c8e4c3e806effea33e5011c25ab6`. The tested runner and
[23-entry manifest](exact-slot-control-pins.json) were pushed and remote-verified
at `e1c47e8ccde43e9ba16798950124b9df14f7f949` before any declared full benchmark
score. **33 relevant tests**, including eleven new regressions, passed before
execution. Four independent-checker/receipt regressions bring the total to
**37**. Local invented fixtures used before publication are explicit mathematical
checks, not declared full benchmark datasets.

The [lossless report](exact-slot-predictor-controls.json.gz) contains all 256
records and all original layout templates. Each record binds its entire coarse
and fine evaluation—including full fitted tables, scored locus losses and exact
transition/support receipts—by sorted-key compact JSON SHA-256. Tables/receipts
are deterministically regenerated rather than repeated in the report. All model
losses and three contrasts, every fold/group summary, support counts, hashes,
criterion flags, signs and known-process references remain present.

- Runner SHA-256: `999659bec8888f11afaeb720d7eaf36f18a7e8229f4d7912dd65b387468a5073`.
- Fine model SHA-256: `f299d79d49555b312651658e71289b77c97f5e2aac9067fa6594bfd1a9e2632f`.
- Manifest SHA-256: `f927c977aeeae4892505cd3b3b97223786e8358d33c48eab8b77ec55ba302660`.
- Expanded report SHA-256: `bd4214cb41cb66b2edc94962eaa3cf9e2ad186651e7925b535dde619d476699e`.
- Gzip SHA-256: `b5dff3382cc7e958ecc32b0fa3f5a9833c43460d2491a650ca225998997f021d`.

The 4,493,674-byte gzip preserves every byte of the 38,720,154-byte JSON, with
zero mtime and no embedded filename. The original coarse source 3a987a93 and
current repaired source 10d090fa remain separate identities. The accepted AST
compatibility verifier confirms unchanged scientific functions outside the
specific reviewed CLI/output guard; inert snapshots are parsed, never executed.
The accepted #194 parent preserves its original fine source/report bytes.

The [separate checker](../../scripts/verify_exact_slot_predictor_controls.py)
rebuilds every stream with an independent byte/rejection implementation and uses
the separate exact-slot integer-array/weighted-mixture engine. It calls no
production fine fit, probability or score function. It checks every complete
fine-evaluation digest, every retained field/aggregate, all old 192 dataset
records, all 3,510,528 scored transitions and 7,021,056 exact fine probabilities.
The derived coarse receipt passed a separate full arithmetic replay. Complete
producer replay reproduced the report bytes for all 256 datasets. Both full
routes passed before these results were submitted for review.

Tests cover draw boundaries/consumption, binary versus ten-class oracles,
stream separation, unchanged old generation, explicit original/current source
binding, local end-to-end fitting, coarse mismatch before fine fit, canonical
full digests/scalar types, all-replicate accounting/adverse summaries, changed
inputs before API imports, lossless compression and existing/late input aliases.
A reduced exact-input bundle without Git, source catalog or raw corpus passes
input verification and local invented five-group API scoring. This is a bounded
portability check, not a claimed complete 256-dataset replay in that bundle.

For Python 3.14.3, standard library only:

```sh
python3 scripts/exact_slot_predictor_controls.py \
  --check research/baselines/exact-slot-predictor-controls.json.gz
python3 scripts/verify_exact_slot_predictor_controls.py
python3 -m unittest tests.test_exact_slot_predictor_controls \
  tests.test_independent_exact_slot_controls
```

Both full routes recalculate all 256 datasets and take several minutes.
Use `--new-report NEW_PATH.json.gz` for an exclusive output. Source/API/plan/
parent/snapshot identities are protected before calculation and after complete
serialization. If a source catalog exists, its native paths are also protected.
Existing outputs are refused. Exact outgoing contents, archive headers, links
and public commit metadata are inspected; no private path, source image, native
token body or credential is included.

## Interpretation

The fixed model can detect the specified strong persistence and learn the
specified alternating position profile. It misses every moderate-persistence
case that the coarse model detects. This performance asymmetry limits using its
negative native preference as evidence about absence of dependence. The old
coarse model's preference on independent positional data likewise limits a
direct-neighbor interpretation of that preference.

These laws omit actual manuscript class marginals, glyph structure, geometry,
source disagreements and unrecorded content dependencies. No native persistence
rate, language, copying mechanism, physical glyph policy, decipherment or
translation is estimated or adopted. A model revision needs another registered
version and honest exposure/evaluation; preserve these failures and the original
native negative study rather than tune either after seeing the calibration.
