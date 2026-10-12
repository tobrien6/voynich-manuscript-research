# Which literal forms contribute to the y-prefix lookup contrast?

The accepted [parent diagnostic](RESULTS.md) has a primary first-minus-other
lookup gain of **+0.42890700**. This follow-up reproduces that score exactly as
the sum of fixed literal-form scores multiplied by differences in their
unit-weighted frequencies. It identifies the strings and weights contributing
to the reported contrast. It does not estimate a causal share explained or
change the parent's `survives_v1_diagnostic` decision.

## Fixed inputs and chronology

The [accounting plan](FORM_ACCOUNTING_PLAN.md) was committed before computing
these terms at
[`9643286`](https://github.com/tobrien6/voynich-manuscript-research/commit/9643286bb9c145b529d669c4c90948ef3c8de0fb).
The implementation, input pins and 14 synthetic tests were committed before
manuscript accounting at
[`8bacdc4`](https://github.com/tobrien6/voynich-manuscript-research/commit/8bacdc415a0a625df8974139552ca83c234b2fd5).
These are inspectable chronological records, not independent certification of
execution history. The parent results, rule and source material were already
exposed; this is neither a valid candidate holdout nor previously unseen data.

[The input manifest](form-accounting-inputs.json) fixes the parent producer,
report, partition, both plans and all ten project helper files in the import
closure. Its SHA-256 is
`3e9f400e1727f50e242d51f0fbcbe044346f1c13cfd2606159c801a3b90a6f64`.
The accepted parent is [PR #75](https://github.com/tobrien6/voynich-manuscript-research/pull/75),
with report SHA-256
`8944187811166c1ba687d4065b9afe7fa7c853e3ed46acacb56ae3a28ae1a6f1`.
No parent producer, plan, partition or report bytes are changed.

The complete parent report is replayed first. The accounting then checks all
eight vocabulary identities and development token totals, original unit lookup
cells, missing classes, the 3,002 common eligible locus keys and the 15 common
scoring units. Selection remains shared regular non-paragraph-start P0 loci in
pinned ZL3b/IT2a, split/join uncertain spaces and exclude/first alternatives.
The 74 development / 18 diagnostic partition is preserved. The vocabulary and
other-slot class include retained final slots. Excluded original first slots
are never promoted to a later retained token.

## Exact identity and weights

Within a variant, a scorable form `t` starts with lower-case literal EVA `y`
and has at least two ASCII letters. Its fixed score is
`g(t) = I(t[1:] in V) - I(t in V)`, where `V` contains only retained ASCII
non-first development tokens on the common locus cohort. Case is preserved;
exactly one initial character is removed. The same form receives the same
lookup score in either position class. This is membership in a transcription
dictionary, not reading correctness.

For each common unit `u`, divide a form's class occurrence count by that unit's
class total. Average those proportions across the same 15 units to obtain
`wF(t)` and `wO(t)`. The contribution is
`C(t) = (wF(t) - wO(t)) * g(t)`. Therefore:

```
first_gain = sum_t wF(t) * g(t)
other_gain = sum_t wO(t) * g(t)
first_minus_other = sum_t C(t)
```

Every calculation uses exact rational arithmetic. In every variant, both class
weight sums are exactly one, their difference sums to zero, and the form sums
equal independently summed per-unit gains. Pooled occurrence counts below
describe the sample; they are not the denominator of this equal-unit statistic.
The primary exact contrast is **757943/1767150**.

## All eight variants

All rows use the same 15 common units. First/other counts include only their
scorable candidates; form counts are distinct literal strings in either class.

| Source | Spaces | Alternatives | Forms | First n | Other n | First gain | Other gain | First minus other |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ZL3b | split | exclude | 99 | 85 | 82 | +0.48112922 | +0.05222222 | +0.42890700 |
| ZL3b | split | first | 100 | 85 | 84 | +0.48112922 | +0.05222222 | +0.42890700 |
| ZL3b | join | exclude | 111 | 93 | 84 | +0.39957115 | +0.05777778 | +0.34179337 |
| ZL3b | join | first | 111 | 93 | 85 | +0.39957115 | +0.05777778 | +0.34179337 |
| IT2a | split | exclude | 112 | 91 | 93 | +0.42004734 | +0.08444444 | +0.33560290 |
| IT2a | split | first | 112 | 91 | 93 | +0.42004734 | +0.08444444 | +0.33560290 |
| IT2a | join | exclude | 112 | 91 | 93 | +0.42004734 | +0.08444444 | +0.33560290 |
| IT2a | join | first | 112 | 91 | 93 | +0.42004734 | +0.08444444 | +0.33560290 |

Identical gains do not imply identical populations. ZL split/first adds one
other-slot `yog` and another `ytol` relative to split/exclude; both have zero
lookup score. Their frequencies and class denominators remain in the complete
record even though the summary gains coincide. The repeated IT rows reflect
unchanged representations under these policies, not independent replications.

## Primary contributions, losses and neutral forms

Following the plan, these are the five largest positive signed contributions
and all four negative contributions, ordered by value then literal form. All
nine forms have lookup score +1. The counts are pooled, while the exact
contribution uses the unit-weighted frequency difference above.

| Literal form | First n | Other n | Exact contribution | Rounded contribution |
| --- | ---: | ---: | ---: | ---: |
| `ychor` | 5 | 0 | 2147/18900 | +0.11359788 |
| `yshol` | 1 | 0 | 1/15 | +0.06666667 |
| `yshedy` | 2 | 0 | 8/225 | +0.03555556 |
| `ycheol` | 4 | 0 | 328/11475 | +0.02858388 |
| `ychain` | 1 | 0 | 1/45 | +0.02222222 |
| `ylchdy` | 0 | 1 | -1/30 | -0.03333333 |
| `yckhy` | 0 | 1 | -1/75 | -0.01333333 |
| `ykeodaiin` | 0 | 1 | -1/165 | -0.00606061 |
| `ykchom` | 0 | 1 | -1/180 | -0.00555556 |

One occurrence need not receive weight 1/85. Source family 42 has one first
candidate, `yshol`, and one other candidate, `ykchy`; the former gains a match
and the latter matches both ways. Each unit receives 1/15 weight, so that single
`yshol` occurrence contributes 1/15. Sparse class denominators can have large
effects under the parent's declared statistic.

A negative contribution is different from a lost lookup. The sole primary
form with score -1 is `yteeey`: it occurs once in each class, with first weight
1/255 and other weight 1/165. Its frequency difference is -2/935, producing a
**positive** contribution of 2/935. Deletion loses its match in both classes;
the more heavily weighted other-class loss raises first-minus-other gain.
The 99 primary forms have 28 positive contributions, four negative
contributions and 67 zero contributions. The complete report retains this loss
and every neutral score and zero term,
alongside all 18 diagnostic units and their exclusions. A ranked excerpt is
not a complete list of evidence for the proposed mechanism.

## Interpretation and adjacent controls

This is an accounting identity of the accepted score. Exact-form matching at
identical class weights would produce zero by construction because `g(t)` has
no position argument. That identity does not falsify a mechanism that changes
the strings themselves. Conversely, the positive unmatched contrast cannot
establish such a mechanism. Lexical, morphological, spelling, layout and
transcription accounts still need discriminating evidence.

The accepted [prefix-specificity controls](../y-prefix-specificity-v1/RESULTS.md)
in [PR #109](https://github.com/tobrien6/voynich-manuscript-research/pull/109)
measure two different quantities: y/q/o contrasts on 13 common units, and y-only
frequency/length standardization on 21 common cells across a different 13-unit
cohort. The latter gives cells equal weight within units, then units equal
weight. Neither denominator is this report's 15-unit frame, so their values
must not be substituted for terms in this identity.

The separately published
[matched other-prefix plan](https://github.com/tobrien6/voynich-manuscript-research/blob/e170810/research/hypotheses/y-layout-prefix-v1/MATCHED_CONTROL_PLAN.md)
uses pooled non-y controls in the same unit, position, exact ASCII length and
log2 development-frequency stratum. Its pools and targets receive occurrence
weights before unit averaging, and missing pools can change coverage. This
accounting does not implement that contrast or assign an outcome to it. During
preparation of this note, the separate plan and accepted #109 results were
inspected. This adjacent-study exposure supplements the already disclosed
parent-result and corpus exposure.

All three follow-ups use related editions and already exposed manuscript
material. Form length is encoding length, and EVA strings are not independently
validated glyphs or words. No language, glyph function, decipherment,
translation, p-value, confidence interval or causal fraction is established.
Image-supported glyph comparisons and an exposure-valid evaluation remain
necessary for stronger claims.

## Reproduce

Python 3.10+, standard library, and Git history containing the parent's pre-fit
registration commit are required. From the repository root:

```sh
PYTHONPATH=tests python3 -m unittest test_y_prefix_form_accounting test_y_layout_prefix
python3 scripts/y_prefix_form_accounting.py --check research/hypotheses/y-layout-prefix-v1/form_accounting.json
python3 scripts/y_prefix_form_accounting.py --check research/hypotheses/y-layout-prefix-v1/form_accounting.json --output /tmp/y-prefix-accounting-replay.json
cmp research/hypotheses/y-layout-prefix-v1/form_accounting.json /tmp/y-prefix-accounting-replay.json
```

[The complete report](form_accounting.json) includes exact rational terms,
per-unit frequency ledgers, parent/source pins and the producer hash. The
checker requires a complete parent replay and every accounting field to agree;
the separate output replay is byte-identical. It refuses changed pinned helpers
rather than silently updating a historical scientific record. Direct, symlink
and hardlink output aliases of protected inputs, code or the check report are
rejected before analysis and immediately before writing. Synthetic tests cover
all lookup cells, unequal class/unit sizes, literal case, neutral and opposite
scores, missing classes, parent/input drift, unpromoted first slots, final-slot
inclusion, development-only vocabulary construction and output protection.
