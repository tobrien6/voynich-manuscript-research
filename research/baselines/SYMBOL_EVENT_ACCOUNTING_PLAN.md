# Event-role accounting of the fixed grouped symbol predictors

Commit and publish this plan before calculating role-specific manuscript
losses. The complete model/result and corpus have already been inspected.
This is descriptive accounting on exposed material, not a new candidate test,
untouched evaluation, causal decomposition or additional fitted model.

## Question and fixed reference

Where does the fixed Q2/Q1 gain occur: initial units, second units, later
units or token termination? The reviewed
[PR #123](https://github.com/tobrien6/voynich-manuscript-research/pull/123)
report is exposed and unaccepted at planning. It has SHA-256
`9afa08f7073188be5930191110517bb3bd88a2ef61c681931489782aeff4dc3c` and
producer SHA-256
`b02e32a636b4f4b42c2798e5ce6f15128410d3eb97c9e3b14206b6cc4f1a4458`.
The [input manifest](symbol-event-accounting-inputs.json) preserves all twenty
original artifact/helper pins. Do not copy its producer or change its report,
model, vocabulary, grouping, folds, source choices or decision. Receive the
pinned numeric reference as a separate local input, without republishing its
Git history or source payloads.

The related [constructed constant-context control](https://github.com/tobrien6/voynich-manuscript-research/pull/139)
already motivated this question. It showed that additional smoothing changes
predictions even when an older context adds no information. This study has
that prior analytical/result exposure and does not calibrate its example or
estimate how much of the real gain is caused by smoothing.

Recreate the accepted reader/cohort, declared unit policies and full transitive
canvas components. Require the same 2,485 clear regular P0 keys, 91 complete
groups, five fixed hash folds, all twelve source/spacing/unit treatments and
all sixty fitted-count digests. Reconstruct counts and rational probabilities
independently using the already inspected accepted helpers for source reading
and cohort definition. Verify every original per-locus count, group/fold,
unseen-context count and loss, all summary weightings and the original
criterion before publishing accounting. The original floating-point loss
presentation may differ from exact-rational probability conversion; use fixed
absolute tolerance 1e-10 bits for that computational comparison and report
the observed maximum discrepancy. This is a numerical tolerance, not a
statistical significance threshold.

## Event classes and scope

For each native token, use the fixed case-sensitive longest-match unit policy
and reset two BOS context labels. Every emitted unit and one EOS target is
scored. Partition these events into four exhaustive, disjoint classes:

1. `initial_unit`: emitted unit at zero-based token-unit index 0.
2. `second_unit`: emitted unit at index 1, when present.
3. `later_unit`: emitted units at index 2 or greater.
4. `termination`: the one EOS target, irrespective of token length.

One-unit tokens have initial and termination events only. No BOS target,
cross-token edge, promoted coordinate or separate space event is added.
Positions are declared notation-unit positions, not image-verified glyphs,
phonetic units, words, or equivalent context reach across policies. Preserve
each treatment's existing target alphabet and root/context priors.

Initial Q2 uses `(BOS,BOS)` while Q1 uses BOS. Its initial count table contains
the same information, with changed hierarchical shrinkage. At second units,
an older BOS label can distinguish initial-position predecessors from the
same literal predecessor elsewhere. Later units and termination have other
context/boundary opportunities. Role-specific prediction gains remain
descriptive and cannot choose a language or generative mechanism.

## Complete accounting identities

For event e let loss j be `L_j(e) = -log2(Q_j(e))` for j=0,1,2.
Let `D_r` sum `L_1-L_2` for events in role r, and let `N_r` count them.
With total targets N:

```
class_mean_gain[r] = D_r/N_r       (null when N_r=0)
pooled_contribution[r] = D_r/N
sum_r N_r = N
sum_r pooled_contribution[r] = original_pooled_Q2_over_Q1_gain
```

For original group g with total N_g, retain all G=91 groups and compute:

```
equal_group_contribution[r] = (1/G) * sum_g D[g,r]/N_g
sum_r equal_group_contribution[r] = original_equal_group_gain
```

Empty roles contribute zero through the original N_g denominator. Do not
drop such groups, use N[g,r] in that term or average only groups containing
the role. Preserve per-locus, group, fold and overall counts and all three
loss sums by role. Require initial count = termination count = token count;
all emitted-unit roles sum to unit count; every role sum recovers the original
target population and each model's losses. Check direct event-gain sums and
loss-difference sums with the same declared numerical tolerance.

Publish all twelve variant summaries and a readable table of primary class
means and both contribution weightings, retaining negative means/terms and
empty classes. The contribution is part of a score-sum identity, not a causal
fraction explained. No new reporting criterion, p-value or confidence is
introduced; preserve the original preference only as reference metadata.

## Artifacts and validation

Retain the full per-locus role ledger, every group/fold breakdown, all input,
cohort, count-table, implementation and reference-report identities. A
deterministic lossless gzip container with no filename or timestamp may hold
the full report; preserve its uncompressed SHA-256 and document how to inspect
it. Keep native token strings and image pixels out of the artifact. It is
derived numerical accounting, not a new transcription or source correction.

Publish the synthetic-tested implementation before role-specific manuscript
calculation. Tests must check one/two/longer-token role assignment, exact
initial/termination counts, manual probabilities/losses, unequal role/group
denominators, empty roles with groups retained, source/reference drift,
original fit/scoring exclusion, complete role-sum identities, strict JSON,
full reference comparison and early/late output alias refusal. Output files
must be new and created exclusively; do not overwrite the reference, plans,
helper code, source catalog/raw inputs or a check report.

Replay the complete report afterward. Independently verify every retained
role count and score aggregate, including all sparse/negative cases. Verify
the compressed output round-trip and its metadata. State which existing
helpers were reused, which reconstruction was independent and the limits of
the original coarse group references and full prior exposure. A stronger
mechanism comparison needs separately specified controls and prospective
evaluation under the project's decipherment protocol.
