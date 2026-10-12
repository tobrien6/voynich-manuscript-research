# Grouped notation-length prediction: exploratory plan v1

Commit this plan and the synthetic-verified implementation before fitting the
models or computing manuscript scores. The earlier whole-corpus interior-order
and position results motivated this comparison. **Every fold is previously
exposed material.** Group exclusion below applies to each parameter fit;
it does not create an untouched evaluation or satisfy the stronger claim in
the decipherment protocol. This is an exploratory predictive baseline, not a
registered decipherment candidate, glyph mapping, or translation.

## Question and fixed inputs

Does previous interior token length improve prediction beyond a source-defined
Currier label and a coarse early/late interior position profile when all loci
from a recorded image-dependency component are excluded from that model fit?

Reuse the 2,165 common P0 loci selected by the accepted
[interior-order plan](../transliteration/INTERIOR_ORDER_PLAN.md), with the same
conservative whole-locus exclusions, drawing exclusion, minimum five-token
rule, and four ZL3b/IT2a split/join treatments. Recreate every parent cohort,
source hash, length-corpus digest, and observation before fitting. Endpoints
do not enter these models or their scored transitions. These are native ASCII
Eva notation lengths, not manuscript glyph counts or decoded words.

Pin the parent report, accepted
[coarse image/dependency report](../folio-alignment/transcription-image-coverage.json),
and canvas CSV by exact SHA-256. Recompute dependency components from the whole
CSV with the accepted helper; compare them with the pinned report. Require
every selected page to have a supported side reference and one matching
component. Both sides/panels and transitive shared scans stay together. Do not
assign crops, validate text/image alignment, infer a historical alias, or
silently discard unsupported pages. Known shared scans are only part of the
possible content dependencies; repeated or related passages outside those
components may remain.

## Five deterministic folds

For each selected dependency group, serialize compact UTF-8 JSON
`["grouped-length-prediction-v1", 20261012, group_id]` with
`ensure_ascii=False` and separators `(',', ':')`. Convert its SHA-256 digest
to an unsigned big-endian integer and take modulo **5**. This assigns a fold
without inspecting scores. All four treatments use exactly the same groups
and folds. Refuse an empty fold; do not try a replacement seed.

For each fold, train solely on rows from the other four folds and score all
rows in the excluded fold. Each locus is scored once. Report the complete
group/leaf/page/fold declarations and training/scoring counts, retaining all
indexed canvas references for each selected complete dependency component.
This manifest is a cross-validation record with known prior exposure; it is
not presented as the project's eight/two frozen candidate split.

## Two fixed models

Map each positive ASCII token length to one of **10** classes:
`1,2,...,9,10+`, with `10+` including every length at least ten. This
coarsening is fixed before fitting and is not a glyph-unit conversion.

For an interior sequence of size `m`, define the early block as its first
`ceil(m/2)` slots. Score adjacent transitions to target slots `j=1,...,m-1`
(zero-based); target half is early when `j < ceil(m/2)`, late otherwise.
The crossing pair is included. A context `c` contains the row's original
source Currier label (missing -> `unset`) and the **target** half. Treat each
source/spacing combination separately; no counts are pooled across them.

From training transitions only, let `N(c,y)` count target class `y`,
`N(c,x,y)` count previous class `x` followed by `y`, and use their sums
`N(c)` and `N(c,x)`. Compare precisely two models:

```
Q0(y | c) = (N(c,y) + 1) / (N(c) + 10)
Q1(y | x,c) = (N(c,x,y) + 10*Q0(y | c)) / (N(c,x) + 10)
```

Q0 is a smoothed context-only model. Q1 adds previous length, shrinking toward
the training-only Q0 distribution with fixed strength **10**. An unseen
previous class backs off exactly to Q0; an unseen context is uniform.
No smoothing strength, class boundary, context, seed, or rule is selected by
cross-validation score. No model or fold is tuned after seeing results.

## Scores and fixed interpretation

For each scored transition record the log probability ratio
`log2(Q1/Q0)`. The primary aggregate is the arithmetic mean over all scored
transitions, in **bits per transition**. Also report each dependency group's
transition-weighted mean and their equally weighted average, and an
equally weighted locus mean. Retain Q0/Q1 log-loss totals and all per-fold,
per-group, and per-locus counts and gains so sign reversals remain visible.

The primary treatment is ZL3b split. Call its diagnostic preference consistent
only if (a) overall transition-weighted gain is positive, (b) equally weighted
group gain is positive, and (c) at least four of five fold transition-weighted
gains are positive. Report this convention even when it fails. Report all
four treatment outcomes and signs; a preference robust across these paired
treatments additionally requires the same convention in all four. Identical
IT spacing corpora are one comparison, not independent replications.

These are predictive scores, not permutation tails or calibrated confidence
in a decipherment. Q1 improvement supports only this representation-level
comparison with Q0. A negative/unstable gain limits the simple transition
model; it does not refute all sequence structure or prove randomness.

## Verification, limits, and next step

Use synthetic exact probability checks, normalized distributions, unseen
context/previous-class backoff, correct target-half assignment, coarsening,
train-only counts, disjoint groups, transitive dependency preservation,
complete fold accounting, and a held-out-value perturbation that cannot
change its fold's fitted parameters. Replay the complete committed report
from the pinned inputs. Preserve negative outcomes and the fixed choices.

The model does not preserve each locus's length multiset, identify a mechanism
of production, or distinguish fine position gradients from neighbor effects.
Source labels and coarse references are not independent adjudications. Full
corpus exposure and the choice of this question after earlier results limit
any confirmation claim. The score concerns parameter-fit exclusion on these
records, not new manuscript prediction. Future candidate mechanisms need
explicit glyph/segmentation rules, stronger controls and appropriate language
or synthetic-encoding comparisons, reviewed mappings, an honest preregistered
split, and prospective evaluation under the
[decipherment protocol](../DECIPHERMENT_PROTOCOL.md).
