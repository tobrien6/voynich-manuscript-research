# Grouped notation-length prediction: mixed gains and a failed criterion

The fixed previous-length model **fails the declared diagnostic preference
criterion in all four treatments**. On the primary ZL split treatment it
improves transition-weighted loss by 0.014261 bits per transition, while
equally weighted dependency groups lose 0.003636 bits per transition. Joining
ZL's uncertain spaces loses under both weightings. IT also has mixed gains.
The earlier permutation departures therefore do not establish a consistent
predictive benefit for this particular smoothed transition model.

## Scope, choices, and chronology

The [plan](GROUPED_LENGTH_PLAN.md) was locally committed at `c208c13` and the
synthetic-verified implementation at `17c1c26`, before fitting manuscript data.
The first attempt to publish that branch failed; its later remote publication
is not an independent pre-fit timestamp. The rule choices and decision
convention were not changed after observing scores.

This question was motivated by already inspected whole-corpus results.
**Every fold has prior exposure.** Groups are excluded from each parameter fit,
and each locus is scored once, but this is exploratory cross-validation, not
an untouched candidate evaluation or new manuscript prediction. No glyph
mapping, decipherment, language identification, or translation is proposed.

Reuse the 2,165 common conservative P0 loci from
[the accepted interior-order analysis](../transliteration/INTERIOR_ORDER.md).
Require the same original source hashes, length vectors, exclusions and
observations. All four ZL3b/IT2a split/join treatments use the same keys and
fold assignments. Length means native ASCII Eva notation length, coarsened
into fixed classes 1–9 and 10+; it is not a manuscript glyph measure.

## Models and group exclusion

The scored transitions are the adjacent interior pairs, including the pair
crossing the early/late split, and excluding both original endpoint tokens.
Q0 predicts target class from the source Currier label and target half.
Q1 also uses the previous class, with fixed shrinkage toward the training-only
Q0 distribution. The plan supplies complete formulas: Q0 adds one count to
each of ten target classes, and Q1 has prior strength ten. An unseen previous
class backs off exactly to Q0. Source labels are given annotations, not
languages inferred by this study.

The [accepted image-reference audit](../folio-alignment/IMAGE_COVERAGE.md)
supplies coarse dependency components. Recompute their transitive closure
over the complete pinned canvas index, retaining both sides, panels and
related scans. The selected cohort occupies **86 components** and 176
transcription page IDs. Neither number is an independently verified physical
sample count or an assertion of locus-to-image alignment.

Hash each component's identifier with the plan's fixed method/seed and assign
it to one of five folds. The component counts are 11, 23, 15, 18 and 19;
their scored locus counts are 371, 532, 326, 547 and 389. Fold sizes were
not balanced after inspection. Each model fit uses only the other four
folds. The manifest retains all component leaf references, source page IDs,
cohort keys and every indexed canvas for each complete component.

## Results

Positive gain means Q1 has lower conditional log-loss than Q0.

| Treatment | Scored transitions | Transition-weighted gain, bits/transition | Equal-group gain, bits/transition | Positive folds | Positive groups | Fixed criterion |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| ZL3b split, primary | 13,713 | +0.014261 | -0.003636 | 4 / 5 | 46 / 86 | **Fails** |
| ZL3b join | 12,272 | -0.001937 | -0.010294 | 1 / 5 | 38 / 86 | **Fails** |
| IT2a split | 13,393 | +0.007120 | -0.005831 | 3 / 5 | 42 / 86 | **Fails** |
| IT2a join | 13,393 | +0.007120 | -0.005831 | 3 / 5 | 42 / 86 | **Fails** |

The criterion requires positive pooled and equal-group gains plus at least
four positive fold gains. Primary ZL split satisfies only two of these three
conditions. IT's two spacing corpora coincide and are one paired comparison,
not independent replications.

The complete [recorded report](grouped-length-prediction.json) includes all
fitted count tables and hashes, both models' losses, training/scoring group
declarations, every fold, every group, and every scored locus. An equally
weighted locus mean is also retained. No unfavorable fold or group is removed.
The primary fold gains are +0.020083, +0.031978, +0.001354, +0.011532 and
-0.004380 bits per transition. Aggregate improvement alone hides this
heterogeneity and the adverse equal-group average.

## Reproduction and verification

From the repository root with Python's standard library:

```sh
python3 -m unittest discover -s tests -p 'test_grouped_length_prediction.py' -v
python3 scripts/grouped_length_prediction.py --check research/baselines/grouped-length-prediction.json
```

The program verifies the three exact parent/metadata/index pins and the
original source/cohort/length digests before fitting. Twelve synthetic tests
cover hand-computed probabilities and normalization, target-half/crossing
selection, coarsening, backoff, separate source contexts, complete fold
accounting, disjoint group fits, transitive dependencies and full canvas
references, invalid/empty folds, duplicate/unsupported rows, loss denominators,
and input protection. Changing only an excluded fold's values and labels leaves
that fold's fitted counts and fingerprint identical. The full report replays
exactly in the recorded Python environment. A separate Counter-based
calculation, without calling the production fitting or scoring functions,
also verified all 8,660 scored locus gains and the four aggregate gain totals.

A post-result maintainer correction rejects output hardlinks to native sources,
the catalog, plan, and all three pinned report/index inputs, before fitting and
again before writing. A thirteenth regression uses temporary synthetic inputs,
checks all six input classes byte for byte, and confirms that ordinary new and
existing outputs still work. This guard-only revision preserves the frozen
rules, chronology, fitted values and complete scientific report bytes.

## Interpretation and next step

The [registered exact-slot follow-up](EXACT_SLOT_LENGTH_RESULTS.md) retains the
same cohort and group folds, with exact interior size/target-slot features and
a matched previous-class weight. Both new refinements lose on every fold and
treatment; the primary previous-class comparison fails its criterion throughout.
All old coarse fitted/scored records remain unchanged. The follow-up is another
exposed-data predictive comparison, with no direct-dependence or decipherment claim.

This fixed model is limited by the observed results; the study does not refute
all sequence structure or show that the text is random. The previous
permutation questions conditioned on locus multisets, whereas this predictor
learns distributions across other groups. Those are different comparisons.
Fine position patterns, source conventions, arbitrary notation classes,
imbalance between groups, sparse contexts, and unrecorded related passages
remain alternatives. The folds exclude only recorded dependency groups from
each fit; the historical source labels and whole corpus remain exposed.

Any revised context, representation or smoothing rule needs a new version
and a new exposure statement. Before advancing an explicit mechanism, define
its rules and objective predictions, reviewed inputs and appropriate language
or synthetic-encoding controls, then apply prospective evaluation under the
[decipherment protocol](../DECIPHERMENT_PROTOCOL.md). Keep this negative and
mixed baseline in the research record.
