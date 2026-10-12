# Prefix controls: y differs from q/o, while opportunity matching reduces its contrast

Deleting leading literal EVA y has a larger first-versus-other lookup gain than
deleting q or o on their common diagnostic units. Conditioning the y comparison
on development frequency and representation length substantially reduces its
contrast in every treatment. A positive residual remains, with sparse cells.
These are descriptive controls on previously exposed representations; they
identify no glyph function, language, decipherment, or translation.

## Fixed plan, inputs, and exposure

The [plan](PLAN.md) and [input identities](inputs.json) were committed and pushed
before scoring these controls at
[`7c9ef00`](https://github.com/tobrien6/voynich-manuscript-research/commit/7c9ef000cf5873682486c4c921dfe58bc4eb921a).
Its recorded time is 2026-10-12 01:40:23 EDT; control execution began at
01:49:50.819499 EDT. Git/run timestamps are chronological declarations, not
independent certification of execution history. The parent is the accepted
[y-layout-prefix v1 diagnostic](../y-layout-prefix-v1/RESULTS.md), exact version
`1c6abb48776a6a59b527f502b50289edf9709191`, including its output-protection fix.
Every pinned parent file remains byte-identical. The original study and decision
are preserved; this version declares no new pass/fail or significance criterion.

Full-corpus results already helped develop the candidate. The retained 74/18
dictionary-development/diagnostic page-family partition is **not a valid
candidate holdout or an unseen sample**, and does not resolve the pilot's 8/2
evaluation split. Sources remain pinned ZL3b and IT2a, with split/join uncertain
spaces and exclude/first alternatives. Coarse source families and shared scans
are the parent study's dependency units, not independently aligned glyph regions.

The same 3,131 jointly non-start regular P0 locations yield the same **3,002
all-eight-variant eligible loci**. Each vocabulary contains only retained ASCII
tokens from development non-first slots. This implementation independently
counts those tokens, reproduces all vocabulary sizes and sorted-string hashes,
and reproduces all original y lookup cells and the full v1 scientific report.
Evaluation tokens contribute neither vocabulary entries nor development counts.

For a candidate with at least two ASCII letters beginning in the specified
lower-case character, remove exactly that character. Gain remains
`I(stripped in vocabulary) - I(original in vocabulary)`, in {-1,0,1}. String
membership is not reading accuracy. The [complete report](results.json) retains
every unit, role, prefix, opportunity cell, loss, empty class, exclusion reason,
input hash, and original v1 summary; it adds no source token payload or image.

## A. Fixed y, q, and o controls on common units

Require both first and other candidate classes for **all three prefixes in all
eight treatments**, then give each retained unit equal weight. Thirteen of the
18 diagnostic units qualify: source families 15, 17, 19, 42, 44, 45, 66, 80, 81,
82, 99, 104, and 114. These form a smaller cohort than v1's 15 y-only units.

The five excluded families are 5, 7, 13, 67, and 96. Families 5 and 7 lack first
y candidates; family 13 has both y roles only in the ZL join treatments. Family
67 lacks first q and o candidates in the primary treatment, and family 96 lacks
first q candidates. Per-treatment missing roles, including exclusions caused
only by another treatment, remain explicit in the report.

Selectivity means first gain minus other gain. All entries are fractions:

| Source | Spaces | Alternatives | y selectivity | q selectivity | o selectivity | y minus q | y minus o |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| ZL3b | split | exclude | +0.47950807 | -0.01081797 | +0.09800711 | +0.49032604 | +0.38150096 |
| ZL3b | split | first | +0.47950807 | -0.00988026 | +0.09762834 | +0.48938834 | +0.38187973 |
| ZL3b | join | exclude | +0.37899235 | -0.02079339 | +0.13073394 | +0.39978574 | +0.24825841 |
| ZL3b | join | first | +0.37899235 | -0.01964898 | +0.13442278 | +0.39864134 | +0.24456957 |
| IT2a | split | exclude | +0.39749052 | -0.05048289 | +0.13025081 | +0.44797342 | +0.26723971 |
| IT2a | split | first | +0.39749052 | -0.05048289 | +0.13025081 | +0.44797342 | +0.26723971 |
| IT2a | join | exclude | +0.39749052 | -0.05048289 | +0.13025081 | +0.44797342 | +0.26723971 |
| IT2a | join | first | +0.39749052 | -0.05048289 | +0.13025081 | +0.44797342 | +0.26723971 |

For the primary treatment, first/other gains are y **+0.53976448/+0.06025641**,
q **+0.01127182/+0.02208979**, and o **+0.12887198/+0.03086487**. All eight
treatments give larger y selectivity than q or o. This comparison fixes the
unit sample; it does not match the three prefixes' frequency, length, spelling,
or vocabulary composition, and does not make them equivalent linguistic controls.

## B. y frequency/length opportunities on common cells

Classify each original y form by its development-only frequency **0, 1, or 2+**
and ASCII representation length **2–4, 5–7, or 8+**. A common cell must contain
both candidate roles in all eight treatments. Give common cells equal weight
within a unit, then give units equal weight. Compare with unconditioned y gains
on those **same units**, separating matching from a change in the unit sample.

Twenty-one of the 162 declared unit × frequency × length cells qualify, across
13 units: families 15, 17, 19, 44, 45, 66, 67, 80, 81, 96, 99, 104, and 114.
Families 5, 7, 13, 42, and 82 have no common cell. This sample differs from A's
13 units. Every absent role and cross-treatment exclusion is recorded, including
cells retained in one treatment but missing a role elsewhere.

| Source | Spaces | Alternatives | Matched first gain | Matched other gain | Matched selectivity | Unmatched on same units | Matched minus unmatched |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| ZL3b | split | exclude | +0.17051282 | +0.06410256 | +0.10641026 | +0.39232859 | -0.28591833 |
| ZL3b | split | first | +0.17051282 | +0.06410256 | +0.10641026 | +0.39232859 | -0.28591833 |
| ZL3b | join | exclude | +0.16208791 | +0.03846154 | +0.12362637 | +0.31745389 | -0.19382752 |
| ZL3b | join | first | +0.16208791 | +0.03846154 | +0.12362637 | +0.31745389 | -0.19382752 |
| IT2a | split | exclude | +0.16346154 | +0.06623932 | +0.09722222 | +0.31031103 | -0.21308881 |
| IT2a | split | first | +0.16346154 | +0.06623932 | +0.09722222 | +0.31031103 | -0.21308881 |
| IT2a | join | exclude | +0.16346154 | +0.06623932 | +0.09722222 | +0.31031103 | -0.21308881 |
| IT2a | join | first | +0.16346154 | +0.06623932 | +0.09722222 | +0.31031103 | -0.21308881 |

The primary reduction is **0.28591833**, about 28.59 percentage points in this
gain contrast. It compares weighting/cohort compositions, not a causal share
explained. The parent's broader 15-unit y selectivity was **+0.42890700**;
using that as B's unmatched comparator would mix matching with unit selection.

The primary common cells contain **46 first and 49 other y candidates**.
Seventeen of their 42 role-specific cells contain a single token. These pooled
counts are not the equal-cell/equal-unit statistic's denominator. Primary cell
counts and gains are below; all eight treatments are in JSON.

| Family | Development frequency | Length | First n | Other n | First gain | Other gain |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| 104 | 0 | 5–7 | 5 | 2 | +1.00000000 | 0.00000000 |
| 104 | 0 | 8+ | 5 | 1 | +0.40000000 | 0.00000000 |
| 104 | 2+ | 5–7 | 2 | 5 | 0.00000000 | 0.00000000 |
| 114 | 0 | 8+ | 3 | 2 | 0.00000000 | +0.50000000 |
| 114 | 1 | 5–7 | 1 | 2 | 0.00000000 | -0.50000000 |
| 114 | 2+ | 5–7 | 4 | 4 | 0.00000000 | 0.00000000 |
| 15 | 2+ | 5–7 | 1 | 1 | 0.00000000 | 0.00000000 |
| 17 | 2+ | 5–7 | 3 | 1 | 0.00000000 | 0.00000000 |
| 19 | 1 | 5–7 | 1 | 1 | 0.00000000 | 0.00000000 |
| 44 | 1 | 5–7 | 1 | 2 | 0.00000000 | 0.00000000 |
| 44 | 2+ | 5–7 | 1 | 3 | 0.00000000 | 0.00000000 |
| 45 | 0 | 5–7 | 1 | 3 | +1.00000000 | +0.33333333 |
| 66 | 0 | 5–7 | 4 | 3 | +0.50000000 | 0.00000000 |
| 66 | 2+ | 5–7 | 2 | 3 | 0.00000000 | 0.00000000 |
| 67 | 1 | 5–7 | 2 | 2 | 0.00000000 | 0.00000000 |
| 80 | 2+ | 5–7 | 1 | 1 | 0.00000000 | 0.00000000 |
| 81 | 2+ | 2–4 | 2 | 1 | 0.00000000 | 0.00000000 |
| 81 | 2+ | 5–7 | 1 | 8 | 0.00000000 | 0.00000000 |
| 96 | 2+ | 5–7 | 2 | 1 | 0.00000000 | 0.00000000 |
| 99 | 0 | 5–7 | 3 | 1 | +1.00000000 | +1.00000000 |
| 99 | 2+ | 5–7 | 1 | 2 | 0.00000000 | 0.00000000 |

Original vocabulary membership restricts possible gains mechanically: absent
originals can gain or remain unmatched; present originals can retain or lose a
match. Comparing these opportunity compositions matters. Coarse bins still
contain different strings and different repeated counts, and exclude 141
noncommon cells. Matching these properties does not match true glyphs, words,
annotation quality, or generative mechanisms. The retained positive residual
cannot select a layout marker over morphology, spelling, segmentation, or
transcription. Repeated IT rows are identical treatments, not independent
replications. No p-value, confidence interval, accuracy, or new support verdict
is assigned to either control.

## Reproduce and next evidence

Python 3.10+, standard library, and Git with the pre-control and parent histories
available. From the repository root:

```sh
python3 -m unittest tests.test_y_prefix_specificity tests.test_y_layout_prefix
python3 scripts/y_layout_prefix.py --check research/hypotheses/y-layout-prefix-v1/results.json
python3 scripts/y_prefix_specificity.py --check research/hypotheses/y-prefix-specificity-v1/results.json
```

Twelve new synthetic tests and 20 parent diagnostic tests pass. Known lookup cells,
fixed frequency/length boundaries, development-only frequency, equal cell/unit
weights, all-prefix/all-treatment eligibility, empty classes, unpromoted excluded
first slots, altered v1 records, pin/chronology drift, and direct/symlink/hardlink
input-output aliases, including an alias introduced during analysis, are checked.
Complete replay checks the parent reconstruction
and every field of this report. Exact rational arithmetic precedes presentation.

The q/o contrast constrains a generic representation-prefix account; the
reduction after opportunity matching limits the raw y contrast's specificity.
Stronger evidence requires independently reviewed glyph regions, explicit
generative alternatives with comparable diagnostics, and an exposure-valid
evaluation design. The accepted [reversible row-marker demonstration](../../representation/PREFIX_FORMATTING.md)
provides a synthetic caution: strong lookup recovery can arise without decoding
a language. It is neither a manuscript fit nor a mechanism adjudication.
