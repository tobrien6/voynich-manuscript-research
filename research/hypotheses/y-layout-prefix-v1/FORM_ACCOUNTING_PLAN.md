# Literal-form accounting of the y-prefix lookup diagnostic

Record this plan before computing the form-level contributions. The parent
result, rules and implementation have already been read. This is an accounting
follow-up on exposed material, not a new candidate test or untouched evaluation.

## Fixed inputs and scope

Use the accepted parent report from PR #75 without changing its inputs, rules,
partition, vocabulary construction, eligibility or decision. Initial report
SHA-256 is `8944187811166c1ba687d4065b9afe7fa7c853e3ed46acacb56ae3a28ae1a6f1`;
its recorded producer SHA-256 is
`0c32a056a79a196a5987faf3ae202f0a7a83860f47476f492fe125a350a3edc3`.
The partition SHA-256 is
`354aace43b44b5158257c737fe81c64ccc27469026a4d3b69743e117c3e739ae`.
Require these exact identities and a complete parent replay before accounting.
Preserve the original pre-fit registration and its explicitly invalid holdout
claim. No original report or code is rewritten by this follow-up.

Reconstruct all eight source/uncertainty variants through the accepted helpers.
Check every original unit lookup cell, vocabulary size/digest and development
token count, the common locus count/digest, all evaluation-unit identities,
missing classes and the 15 common scoring units before computing new terms.
Use those same common units in every variant. The parent non-first class and
development vocabulary include eligible final slots; do not redefine them as
strictly interior slots or promote excluded positions to first position.

## Accounting identity

For a scorable literal representation `t` and the fixed vocabulary `V`, define

```
g(t) = I(t[1:] in V) - I(t in V)
```

The parent applies this same function in both position classes. It has no
position argument, and its value is fixed for a literal form within a variant.
It is a string lookup score, not correctness of a reading or glyph deletion.

Let `n[u,F,t]` and `n[u,O,t]` count occurrences of form `t` in the first and
other classes of common unit `u`; class totals are `N[u,F]` and `N[u,O]`.
For `M` common units, calculate exactly with rational arithmetic:

```
wF(t) = (1/M) * sum_u n[u,F,t] / N[u,F]
wO(t) = (1/M) * sum_u n[u,O,t] / N[u,O]
A(t) = wF(t) - wO(t)
C(t) = A(t) * g(t)
first_gain = sum_t wF(t) * g(t)
other_gain = sum_t wO(t) * g(t)
selective_gain = sum_t C(t)
```

Retain all forms occurring in either class, including zero-score and
zero-contribution forms. Require `sum(wF)=sum(wO)=1`, `sum(A)=0`, and exact
agreement with independently summed per-unit gains. Reproduce the parent's
rounded summaries and pooled lookup cells without substituting pooled rates
for its equal-unit statistic.

## Outputs and interpretation

Publish complete variant form tables: before/after membership and score,
pooled occurrence counts, exact class weights, exact weight difference and
signed contribution. Retain unit/class frequency ledgers, including every
excluded diagnostic unit and its missing class. Pin the parent files, relevant
helper bytes, this plan and the new producer; keep data representations literal.

For the readable note, list up to five largest positive and five most negative
primary contributions, ordered by signed value and literal form for ties. The
complete report remains authoritative; a short table must not suppress losses
or neutral forms. Record the other seven summaries and any failures. No new
threshold, p-value, confidence or causal fraction is introduced.

Equal-weight exact-form matching yields zero selectivity by construction because
`g(t)` is position-independent. Explain that this is an algebraic property,
not evidence refuting a mechanism that changes the strings themselves. The
unmatched parent contrast describes the composition of its sampled forms and
vocabulary scores. Lexical, morphological, orthographic, layout and transcription
interpretations still require actual matched controls and image evidence.

Before running manuscript accounting, test all four lookup cells, unequal
class/unit sizes, repeated forms, opposite scores, neutral forms, literal case,
frequency-composition examples, exact-form matching, malformed/empty classes,
parent drift and output/input alias refusal using synthetic fixtures. Protect
all pinned inputs and scripts, including symlink/hardlink aliases, and check
again immediately before writing. Replay the new report afterward. Disclose
the exposed corpus and related source/policy treatments throughout.
