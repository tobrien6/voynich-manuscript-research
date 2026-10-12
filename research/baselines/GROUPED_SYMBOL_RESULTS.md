# Group-excluded within-token notation prediction

A fixed two-predecessor predictor reduces loss relative to a one-predecessor
predictor in all twelve source/spacing/unit treatments. On the primary ZL3b
split ASCII treatment, the pooled gain is **0.210108 bits per scored target**;
the equal-group gain is **0.220859**. All five fold gains are positive.
This meets the pre-fit reporting criterion on previously exposed data. It
establishes a modest notation prediction baseline, with no decoding rule or
language/mechanism identification inferred from the gain.

The [plan](GROUPED_SYMBOL_PLAN.md) was committed at
[`64cb5e9`](https://github.com/tobrien6/voynich-manuscript-research/commit/64cb5e94ce8468c0daed94dd584c2994d9d1da71).
The synthetic-tested implementation followed at
[`e0b1eea`](https://github.com/tobrien6/voynich-manuscript-research/commit/e0b1eea137a465d6fb0e651f28e016a0a633acbc).
Before the first manuscript fit, the final
[`6c6f902`](https://github.com/tobrien6/voynich-manuscript-research/commit/6c6f90251c781c030bb9953b56730e86a85cf001)
commit completed all twenty artifact/helper pins and twelve synthetic tests.
That full commit was remotely published and its branch identity verified before
fitting. The final pin addition and its chronology are disclosed in the plan.
No model, fold, score or preference choice changed after this run.

## Population and scoring rules

The entire accepted [paired-entropy receipt](../representation/PAIRED_ENTROPY.md)
is regenerated before fitting, including all frequency tables and exclusions.
The common cohort retains 2,485 of 3,884 shared present P0 loci on 195 native
source pages; 1,399 exclusions and the source-only f106r.29 remain bound through
the parent receipt. Native case, uncertain-space policies and all three
case-sensitive longest-match unit policies are unchanged.

Complete transitive image-dependency components give **91 groups**, assigned
to five fixed hash folds containing **18, 15, 16, 21 and 21 groups**. The
[full report](grouped-symbol-prediction.json) declares every selected locus,
page, leaf and indexed canvas. Other leaves in a component stay in its group
although they may have no selected locus. Every locus is scored once using
parameters fitted on the other four folds. These are coarse dependency
references and fit exclusions, with known whole-corpus exposure; they are not
an untouched decipherment evaluation or reviewed physical text/image mapping.

Every native token resets two reserved BOS context labels. Score its emitted
units and one EOS target, with no edge across tokens or loci. The fixed target
alphabet contains all 52 ASCII letters, the policy's declared patterns, and
EOS, including unobserved types. Root pseudocount is 0.5 per type; both context
orders shrink toward the training-only lower order with strength 16. The
[plan](GROUPED_SYMBOL_PLAN.md) supplies complete formulas.

Primary targets number **129,151**: 107,808 notation units plus 21,343 termination
events. Mean losses for orders zero/one/two are **3.871452 / 2.058956 / 1.848848**
bits per target. These smoothed fit-excluded scores include initial units and
termination; their target population differs from the parent's empirical
adjacent-edge conditional entropy. EOS is an accounting event, not a glyph.

## Complete paired sensitivity outcomes

Gains are loss of the lower order minus loss of the higher order, divided by
scored targets. Equal-group gains average each component's target-weighted gain.
All twelve pass the same fixed second-order criterion: pooled gain at least
0.02, positive equal-group gain, and all five fold gains positive. Q1/Q0 gains
are secondary descriptive results without another selection criterion.

| Source/spacing | Declared unit policy | Q1 over Q0, pooled | Q2 over Q1, pooled | Q2 over Q1, equal group | Nonpositive groups |
| --- | --- | ---: | ---: | ---: | ---: |
| ZL3b split | `ascii_letters` | 1.812497 | 0.210108 | 0.220859 | 0 |
| ZL3b split | `bench_sequences` | 1.666867 | 0.165052 | 0.172683 | 0 |
| ZL3b split | `bench_and_minim_sequences` | 1.521809 | 0.153866 | 0.151902 | 1 |
| ZL3b join | `ascii_letters` | 1.811683 | 0.215860 | 0.227233 | 0 |
| ZL3b join | `bench_sequences` | 1.666121 | 0.171110 | 0.180824 | 0 |
| ZL3b join | `bench_and_minim_sequences` | 1.520299 | 0.160424 | 0.160827 | 1 |
| IT2a split | `ascii_letters` | 1.810815 | 0.220909 | 0.227140 | 1 |
| IT2a split | `bench_sequences` | 1.667564 | 0.176742 | 0.181209 | 0 |
| IT2a split | `bench_and_minim_sequences` | 1.523046 | 0.166702 | 0.161123 | 1 |
| IT2a join | `ascii_letters` | 1.810815 | 0.220909 | 0.227140 | 1 |
| IT2a join | `bench_sequences` | 1.667564 | 0.176742 | 0.181209 | 0 |
| IT2a join | `bench_and_minim_sequences` | 1.523046 | 0.166702 | 0.161123 | 1 |

All scores are bits per the treatment's declared target. The token units and
context reach differ across policies, so these columns do not select a glyph
alphabet or establish that one representation is better. IT split/join arrays,
fit counts and scores are identical; they are paired dependent treatments.
ZL and IT are also related representations of the same manuscript.

Aggregate preference does not mean universal improvement. `yale-leaves:38`
loses under ZL's bench/minim policy: split -0.126424 (20 targets), join -0.036885
(19 targets). IT loses under ASCII (-0.043449; 28 targets) and bench/minim
(-0.141834; 20 targets), identically across its spacing policies. These small
component reversals, every locus score, unseen-context counts, all group/fold
losses and complete target denominators remain in the report.

## Verification and next comparison

```sh
PYTHONPATH=tests python3 -m unittest test_grouped_symbol_prediction -v
python3 scripts/grouped_symbol_prediction.py --check research/baselines/grouped-symbol-prediction.json
# A new destination is required; existing files and aliases are rejected.
python3 scripts/grouped_symbol_prediction.py --output NEW_REPORT.json
```

Twelve synthetic tests cover manual Fraction probabilities and log losses,
normalization/backoff, BOS/EOS reset, fixed alphabet mass, train/scoring group
separation and held-out perturbation, unselected transitive leaves, unequal
weighting and exact criterion boundaries, typed pins/strict JSON, parent drift,
complete repository import closure and late alias rejection by exclusive
creation. A separate post-result scanner and flat-counter calculation, without
calling the production fit or score functions, independently reconstruct all
60 sparse fitted-count hashes and every one of 29,820 locus scores using exact
rational probabilities. Largest locus-loss difference is 5.69e-14 bits; all
counts, pooled/macro gains and decisions agree. This checks computation on the
same inputs, not independent manuscript evidence.

The restrictive clear-locus cohort, repeated tokens/passages across components,
known prior exposure, fixed prior mass and notation-defined units limit the
interpretation. These scores do not measure a general entropy rate, establish
linguistic content or copying, reproduce a paper, identify glyph readings, or
support a translation. The next mechanism comparison should match units and
boundary opportunities against stronger production/language controls, and use
an honest prospective split under the
[decipherment protocol](../DECIPHERMENT_PROTOCOL.md).
