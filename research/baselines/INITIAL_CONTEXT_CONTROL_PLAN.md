# Constructed constant-older-context predictor control

Question: can the fixed Q2/Q1 diagnostic convention be met even when the older
context label contains no extra information, because the hierarchy changes
shrinkage? This is an analytical counterexample about predictor interpretation,
not a manuscript experiment or a proposed decoding rule.

The reviewed [PR #123](https://github.com/tobrien6/voynich-manuscript-research/pull/123)
specification, head `7a4b7ae3ccd1196e1389f16247c77e9505a626fe`, is exposed and
not yet accepted when this plan is written. Its producer SHA-256 is
`b02e32a636b4f4b42c2798e5ce6f15128410d3eb97c9e3b14206b6cc4f1a4458`.
The review already established the initial-context smoothing identity. This
example was deliberately chosen after that review. Its positive outcome is
reasoned out analytically in advance, not an unexpected experimental finding.
No manuscript scores, sources, folds, model decisions or parent files change.

## Fixed synthetic population

Use five literal groups `toy-0` through `toy-4`, with one locus and one token
`a` per group. Assign `toy-i` to fold i, explicitly, for i=0..4. There is no
random seed, image group, hash-seed search or corpus selection. The assignments
differ from the manuscript's hash-fold procedure and are bookkeeping for this
constructed example. Fit on the other four groups and score the remaining one.

Each token emits the single unit `a` under all three accepted unit policies.
Its two prediction events are `(BOS,BOS,a)` and `(BOS,a,EOS)`. The older context
is therefore always BOS, including termination. Conditioning on it adds no
information to the immediately preceding context, in either training or
scoring. Every fit has four `a` targets and four EOS targets; every scoring
fold has two targets. Five scored tokens give ten targets overall.

Keep the accepted unit-protocol file and its SHA-256 fixed in the companion
JSON plan. Include all 52 ASCII letters, the policy's declared patterns and
EOS in the sorted target alphabet, as in the exposed specification. Report
all three alphabets, including unused types; these are dependent synthetic
variants, not three manuscript replications.

## Frozen equations and constructed predictions

Use root pseudocount 1/2 and context prior strength S=16. With training-only
counts, calculate the same hierarchy using exact rational arithmetic:

```
Q0(y) = (N(y)+1/2)/(N+K/2)
Q1(y|x) = (N(x,y)+16*Q0(y))/(N(x)+16)
Q2(y|w,x) = (N(w,x,y)+16*Q1(y|x))/(N(w,x)+16)
```

Here every observed x has only one older label, BOS, so its pair/triple counts
and totals are identical. Algebra gives an equivalent one-context estimator:

```
S_eff(x) = S*S / (N(x)+2*S)
Q1_eff(y|x) = (N(x,y)+S_eff(x)*Q0(y))/(N(x)+S_eff(x))
Q2(y|BOS,x) = Q1_eff(y|x)
```

For each observed context N(x)=4 and S_eff=64/9, smaller than 16. The expected
probabilities of either actual scoring target are fixed analytically:

| Alphabet size K | Q0 | Q1 | Q2 = Q1_eff |
| ---: | ---: | ---: | ---: |
| 53 | 3/23 | 7/23 | 51/115 |
| 65 | 1/9 | 13/45 | 97/225 |
| 77 | 3/31 | 43/155 | 327/775 |

Compute log2 losses only after the exact probabilities. Record all alphabet
probabilities, every fit's sparse counts, all fold/group/locus losses and
target totals. Compare Q2/Q1 under the exposed reporting convention: pooled
gain >=0.02 bits per target, positive equal-group gain and all five folds
positive. Expected: all three constructed variants meet it. Q2 versus Q1_eff
has exactly equal probabilities and equal loss by construction. Keep all
variants even if a stated prediction or accounting identity fails.

This does not tune a replacement manuscript model or estimate how much of
the real gain is caused by smoothing. The adjusted strength is derived from
the hierarchy, not fitted to outcomes. The example establishes possibility
and motivates separately specified controls; it does not invalidate the
published numerical scores or imply absence of real longer-context structure.

## Publication and validation

Commit and publish this plan before executing the synthetic report. Commit
and publish the producer and synthetic tests before that execution. Preserve
these analytical expectations and exposure declarations in the result note.
Use a standalone implementation; do not execute, copy or change PR #123's
producer. Pin the accepted unit-protocol bytes and the new plan/producer.
Output creation must be exclusive, including refusal of aliases appearing
during calculation. Complete replay must compare every field and byte.

Verify exact manual probabilities, normalized distributions over the full
alphabet, the general effective-strength identity across count cases, constant
older context, token reset/termination accounting, train/scoring separation,
all summary denominators, the exact criterion boundaries, literal alphabet
and policy pins, input drift, and early/late output alias refusal. A separate
closed-form check should verify every report probability and gain.
