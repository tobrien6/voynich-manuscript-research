# Positive Q2/Q1 gain with no additional older-context information

A constructed constant-older-context example meets the exposed grouped-symbol
predictor's reporting convention under all three declared alphabets. Yet its
older label is always BOS, so it supplies no extra information beyond the
immediately preceding label. The positive gain arises from the hierarchy's
changed smoothing. Q2 exactly equals a one-context estimator using the
algebraically equivalent smaller prior strength.

This is a possibility example with analytically predicted results. It does
not estimate the cause or size of any manuscript effect, tune a replacement
model, or dispute the reviewed numerical scores.

## Fixed construction and chronology

The [plan](INITIAL_CONTEXT_CONTROL_PLAN.md) and
[protocol](initial-context-control-plan.json) were committed and published at
[`f78e32a`](https://github.com/tobrien6/voynich-manuscript-research/commit/f78e32a).
The initial standalone producer and nine synthetic tests were committed and published
at [`dca9dc9`](https://github.com/tobrien6/voynich-manuscript-research/commit/dca9dc9bed25c8ff9e133a6bedd5c102bc94d31a)
before the saved report was constructed. These chronological records remain
declarations, not independent certification of execution history. The expected
fractions and positive outcome were reasoned out before publication and are
explicitly recorded in the plan.

After that saved construction, failure reporting was corrected to retain all
declared variants if an analytical prediction or equivalence fails, as the plan
requires. Those checks now have explicit status fields rather than aborting
the report. A tenth synthetic test simulates a normalized weaker second model
and confirms every failed variant and criterion remains visible. The actual
probabilities, counts, losses and gains are unchanged; the final report adds
status fields and updates producer and probability-table fingerprints. This reporting change was
made after the known result and is not claimed as a pre-result implementation.

The model equations and reporting convention come from the reviewed
[PR #123 specification](https://github.com/tobrien6/voynich-manuscript-research/blob/7a4b7ae3ccd1196e1389f16247c77e9505a626fe/scripts/grouped_symbol_prediction.py),
which was exposed and not yet accepted when this plan was written. This
control executes its own code, with no import or copy of that producer and no
manuscript fitting. The referenced SHA-256 and status remain explicit in the
protocol. The accepted [unit definitions](eva-unit-protocol.json) are byte-pinned.
No source, manuscript model, report, decision, grouping or fold is changed.

Five literal synthetic groups contain one token `a` each. Group `toy-i` is
assigned explicitly to fold i. Each fit uses the other four groups and scores
the remaining group. These are bookkeeping groups with repeated identical
content; they are not images, independently sampled observations, the
manuscript's hash-fold assignments or an unseen-content test.

Every token emits one `a` under each policy. Its two events are
`(BOS,BOS,a)` and `(BOS,a,EOS)`. The older context is always BOS in both
training and scoring, including termination. Each fit contains eight targets:
four `a` and four EOS. Each scoring group has two targets; the total scored
population has five tokens, five units and ten targets. EOS is a prediction
event, not a glyph.

## Exact smoothing identity

Use the exposed root pseudocount 1/2 and context prior strength S=16. When
every observed immediately preceding context x has only the older label BOS,
its pair and triple counts and totals are identical. For a target y, write
`n=N(x,y)` and `N=N(x)`:

```
Q1 = (n + S*Q0)/(N+S)
Q2 = (n + S*Q1)/(N+S)
S_eff = S*S/(N+2*S)
Q1_eff = (n + S_eff*Q0)/(N+S_eff)
Q2 = Q1_eff
```

Substituting Q1 into Q2 gives empirical-count weight
`1-(S/(N+S))^2` and root-prior weight `(S/(N+S))^2`. A one-context
estimator with strength S_eff has those same weights. It uses the same
information with different shrinkage. At N=4 here, **S_eff=64/9**, instead of
16. Exact equivalence holds for every target in the full alphabet, including
unobserved targets, not just the two observed scoring events.

## All constructed outcomes

Target alphabets retain all 52 native ASCII letters, the policy's patterns
and EOS. The token `a` is unchanged across policies. Larger alphabets change
unused prior mass; the three rows are dependent treatments of one constructed
population and do not compare manuscript glyph systems.

| Unit policy | Alphabet K | Observed-target Q0 | Q1 | Q2 = Q1_eff | Q2/Q1 gain, bits per target | Q2/Q1_eff gain |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `ascii_letters` | 53 | 3/23 | 7/23 | 51/115 | +0.54314233 | 0 |
| `bench_sequences` | 65 | 1/9 | 13/45 | 97/225 | +0.57754503 | 0 |
| `bench_and_minim_sequences` | 77 | 3/31 | 43/155 | 327/775 | +0.60495398 | 0 |

The probability shown in each row applies to either actual target, at its
corresponding context. Every alphabet probability is retained in
[the complete report](initial_context_shrinkage_control.json). Every fold's
training counts and group exclusions, scoring loss and target count remain
visible. Exact probabilities precede logarithmic floating-point presentation.

All five folds in every row have the same positive gain. Pooled-target and
equal-group gains agree up to floating-point presentation because every
scoring group has the same targets and scores. Each row meets the referenced
convention: pooled gain >=0.02 bits per target, positive equal-group gain and
five positive folds. Q2 and Q1_eff have exactly equal probabilities and losses;
their contrast is zero. This is an identity check, not a fitted new control
or a causal fraction explained.

## What the example constrains

A positive Q2/Q1 gain under this hierarchy compares two predictors whose
shrinkage differs as well as their context labels. It cannot, by itself,
isolate information carried by an additional preceding manuscript symbol.
The same issue applies to initial `(BOS,BOS)` events in the exposed predictor,
where the older context contains the same initial-position information as
the one-context BOS label. This example makes that distinction explicit.

It does not show that real manuscript higher-context gains are entirely due
to smoothing, or that older symbols lack predictive information. General
contexts can have several older labels; the one-context equivalence above
then need not hold. A substantive comparison requires separately specified
regularization controls and target-position breakdowns, followed by honest
prospective evaluation. The present deliberately chosen population supplies
no power, specificity, language/copying calibration or optimal prior choice.
No glyph function, reading, decipherment or translation is established.

## Reproduce and validation

Python 3.10+, standard library only. From the repository root:

```sh
PYTHONPATH=tests python3 -m unittest test_initial_context_shrinkage_control -v
python3 scripts/initial_context_shrinkage_control.py --check research/baselines/initial_context_shrinkage_control.json
# Use a new destination; existing files and aliases are rejected.
python3 scripts/initial_context_shrinkage_control.py --output /tmp/initial-context-control-replay.json
cmp research/baselines/initial_context_shrinkage_control.json /tmp/initial-context-control-replay.json
```

Ten tests check manual probabilities, exact whole-alphabet normalization,
the general strength identity over 460 count/prior cases, BOS/EOS reset and
target accounting, complete disjoint folds, an excluded-group perturbation,
criterion boundaries, immutable inputs, duplicate/nonfinite JSON refusal and
early/late output collisions, including symlink/hardlink aliases. Exclusive
creation prevents an input from being overwritten by a late alias.
The failure-retention test keeps all three variants and all five folds while
recording failed analytical and equivalence checks with a nonpositive gain.

Complete replay and a separate output replay match every field and byte.
A separate closed-form calculation verifies all 390 full-alphabet target
records, all 15 fitted count tables, every fold score and all denominators,
summaries and criteria. This is computational verification of the same
constructed case, not independent manuscript evidence. Plan, protocol,
unit-definition and producer fingerprints are retained in the report.
