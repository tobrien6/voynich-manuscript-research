# Fixed exact-slot predictors: known-process performance plan v1

Publish this plan and a synthetic-tested calibration program before calculating
new fine-model benchmark scores. The native exact-slot losses and old coarse
benchmark data/results are already exposed. This is a fixed performance
diagnostic, not blind discovery, probability calibration or a manuscript test.

## Question and immutable models

How do the unchanged exact-slot F0/F1 models behave under known absence/presence
of previous-class persistence, and can F0 learn a known independent position
profile? Do these cases limit interpreting the negative native comparison?

Use precisely the model API published for PR #194: exact-slot producer SHA-256
`f299d79d49555b312651658e71289b77c97f5e2aac9067fa6594bfd1a9e2632f`.
Keep its ten classes, exact m/j/source-label features, empirical coarse Q0 prior,
strength ten, common fine-context weight, backoffs, five-fold exclusion and
primary F1/F0 criterion unchanged. Q0/Q1 remain reference models. No smoothing,
context, case, seed or criterion is tuned to this diagnostic. PR #194 is pending;
use a stacked branch, then reconcile explicitly with its accepted implementation
before retargeting. Never silently replace the first model fingerprint.

## Fixed exposed layout and four processes

Reuse only the accepted old benchmark's primary ZL3b split metadata layout:
2,165 locus IDs/labels/pages, 86 groups, five original folds and 13,713 scored
transitions. Each row size is its declared transition count plus one. Verify
the layout against both pinned parent records. Native classes, fitted native
parameters/losses/gains, images and source bodies do not generate any values.

The first three processes are the **exact 192 already published datasets** in
the old benchmark, SHA-256
`c89b5fbc1bbe06d005eca566c2ea44d4751943f34eb5648e5c0198f3c0e5d1bc`:
independent uniform, quarter persistence, and three-quarter persistence, each
at replicates 0..63 with seed 20261012. Use the original generator and streams
without modification. Before a new fine evaluation, match every old sequence
digest, oracle and complete stored coarse record exactly. The accepted coarse
CLI compatibility verifier must validate its original inert source snapshot
and unchanged scientific AST; current coarse producer identity remains explicit.
No archived source text is imported or executed.

Add exactly **64 independent alternating-position datasets**, replicates 0..63.
For each original interior slot i (zero based), independently draw u below four.
Emit class 10 when u<1 for even i and u<3 for odd i; otherwise emit class 1.
Thus P(X_i=10) is 1/4 or 3/4, with no dependence on previous class. Every slot
consumes one draw. Class 10 is a synthetic category, not an asserted physical
length or glyph width. Other eight classes stay in the fixed predictor model.

For this new process, key the accepted SHA-256 rejection sampler by compact
UTF-8 JSON `["exact-slot-known-process-controls-v1",20261012,replicate,
"independent_alternating_positions",locus_key]`, ensure_ascii=False and separators
(',',':'). Every locus/case/replicate has its own stream. Old cases keep their
original namespace. Across-case comparisons do not use paired draws.
Deterministic keyed streams implement the declared nominal sampling laws;
no general hash-uniformity or independence certification is supplied.

## Known-process references and reporting

For the first three processes retain the exact old oracle: uniform ten-class
marginal versus the known diagonal/off-diagonal persistence probabilities.
For the alternating case use uniform **binary** support {1,10} as its declared
oracle reference, versus the known positional probabilities. Its ideal oracle
gain is 1-H_binary(1/4) bits/transition; realized gain sums log2(2*p_i(X_i)).
This reference differs from the fitted source-label/half Q0, and its support
differs from the ten-class persistence reference. Do not interpret differences
between their oracle gains as a causal decomposition or model-fit advantage.

Run all **256** datasets. Retain per-replicate sequence digest, known-process
oracle, original coarse-record identity where applicable, all four model losses,
all three contrasts, every fold/group summary, support counts, fine/coarse fitted-
table hashes and the canonical complete-evaluation digest. The latter binds all
scored locus losses, exact transition probabilities and fine tables, which are
regenerated rather than repeated across 256 outputs. Declare the canonical
digest as sorted-key compact UTF-8 JSON with allow_nan=False. Keep full layout
templates once. No dataset, fold, backoff or adverse outcome is removed.

For each case/contrast record mean/min/max pooled, equal-group and equal-locus
gains, plus positive pooled/equal-group replicate counts. Retain the unchanged
primary F1/F0 diagnostic criterion and report its hit count out of 64. There
is no new collection-level pass threshold or secondary criterion. All outcome
signs remain visible. These finite hit counts/ranges are descriptive; they are
not manuscript p-values, type-I guarantees or natural-language detection power.

## Verification and publication

Before benchmark execution, check new generator draw boundaries/consumption,
stream replay/separation, exact local oracle probabilities, metadata-only layout,
old-record mismatch guards, unchanged estimator binding, complete-case/replicate
accounting, adverse summaries, complete-evaluation digest/scalar types and
initial/late output aliases. Local invented fixtures may exercise the APIs;
do not score any declared full benchmark dataset before code publication.

After generation independently reconstruct every dataset's classes with a
separate byte-stream implementation, matching all old 192 digests. Rebuild fine
counts/probabilities/losses with the separate exact-slot checker, calling no
production fine fitting, probability or scoring function. Verify all 256 full
evaluation digests and retained records/aggregates. Reproduce the complete
saved report from frozen inputs. Neither route reads a raw manuscript corpus.

Freeze actual plan, source/API, parent/control/layout, compatibility receipt and
inert-snapshot identities. Guard them before calculation and after complete
serialization immediately before exclusive creation. If a native catalog is
present, protect its source paths too; existing outputs are refused regardless.
Use deterministic lossless compression, no global numeric-setting changes,
and inspect every outgoing file plus decompressed content/public commit metadata.
Leave final upstream disposition to the assigned maintainers.

The benchmark measures this fixed estimator at an exposed primary layout under
specified abstract class laws. It does not fit manuscript class marginals,
physical geometry, glyphs, copying or hidden content dependencies. Even known-
process success would not validate native independence, a positional mechanism,
language or decipherment. Preserve the native negative result and every failed
synthetic case; a model revision needs its own version and exposure statement.
