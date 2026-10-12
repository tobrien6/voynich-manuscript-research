# Exact-slot count prediction: both refinements lose on excluded groups

The previous-class predictor with exact slot features **fails the fixed diagnostic
preference in all four treatments**. Relative to the matched slot-only predictor,
it loses **0.33692–0.39418 bits per transition**, and none of the five folds is
positive. The slot-only predictor also loses against the original coarse context
baseline by **0.03048–0.03095 bits per transition**. These are failures of the
fixed models, with every unfavorable group, fold and transition retained.

This extends the [accepted coarse comparison](GROUPED_LENGTH_RESULTS.md) on the
same **2,165** common conservative P0 loci, **86** recorded dependency components,
176 native page IDs and original five folds. Old Q0/Q1 tables, losses and failed
criteria reproduce completely and remain unchanged. The full corpus, old results
and synthetic positional counterexample were exposed before this follow-up.
Group exclusion applies to parameter fitting; every fold has prior exposure and
this supplies no untouched evaluation or decipherment evidence.

## Models and controls

The [published plan](EXACT_SLOT_LENGTH_PLAN.md) fixes ten native ASCII notation-
length classes, 1..9 and 10+, and scores the original interior adjacent transitions.
Both endpoint tokens remain excluded; the early/late crossing pair stays included.
All source/spacing treatments and ambiguity/exclusion rules remain unchanged.
These are encoded slots/count classes, not physical glyphs, words or image widths.

The old Q0 prior uses the source Currier annotation and target half. New fine
features are the same annotation, the exact interior size m, and zero-based
target slot j. They are retrospective conditional features on an observed encoded
locus, rather than an online prediction of unknown future row length. No source
labels, folds, sizes, slot buckets or prior strengths are learned by score tuning.

F0 combines the training fine-cell target frequencies with exact old Q0 using
weight w=n/(n+10). F1 combines previous-class conditional frequencies with the
same prior and **the same fine-cell weight**, backing off to F0 for unseen previous
classes. An unseen fine cell uses Q0. The complete formulas are in the plan.
The coarse empirical prior can reuse the same fine cell's training observations;
no scoring-fold observation enters any fitted count or prior.

The training previous-frequency mixture of F1 equals F0 exactly in every fine
context. With a constant training previous class, F1 equals F0 for every target
and scored previous class, including unseen previous-class backoff. These identities
prevent the specific constant-feature gain from an extra smoothing pass. They
neither optimize estimation nor establish that a remaining gain measures direct
neighbor dependence. The effective previous-cell prior strength is 10*n_x/n;
it can be small for rare previous classes. Sparsity and estimator variance remain
limitations, not explanations established by this calculation.

## Complete contrasts

Positive gain means lower loss for the first-named model. The primary F1/F0
criterion requires positive transition-weighted and equal-group gains and at
least four positive folds, as fixed before fitting. The other contrasts are
descriptive and carry no new pass threshold.

| Treatment | Transitions | F1 over F0, pooled | F1 over F0, equal groups | Positive folds | Positive groups | Primary criterion |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| ZL3b / split | 13,713 | -0.38559166 | -0.41884663 | 0 / 5 | 4 / 86 | Fails |
| ZL3b / join | 12,272 | -0.39418147 | -0.42909192 | 0 / 5 | 1 / 86 | Fails |
| IT2a / split | 13,393 | -0.33691752 | -0.39625434 | 0 / 5 | 4 / 86 | Fails |
| IT2a / join | 13,393 | -0.33691752 | -0.39625434 | 0 / 5 | 4 / 86 | Fails |

| Treatment | F0 over Q0, pooled | F0 over Q0, equal groups | F1 over Q1, pooled | F1 over Q1, equal groups |
| --- | ---: | ---: | ---: | ---: |
| ZL3b / split | -0.03086217 | -0.05188616 | -0.43071521 | -0.46709639 |
| ZL3b / join | -0.03094791 | -0.04332112 | -0.42319269 | -0.46211865 |
| IT2a / split | -0.03048412 | -0.04946690 | -0.37452206 | -0.43989012 |
| IT2a / join | -0.03048412 | -0.04946690 | -0.37452206 | -0.43989012 |

Units are bits per transition; equally weighted locus means and all fold/group
records are also retained. All five folds are negative for every displayed
contrast. F1 over Q1 changes both context and shrinkage, so that difference cannot
be attributed to position alone. Identical IT split/join results remain dependent
views, rather than independent replications.

## Support and complete receipts

| Treatment | Unseen fine cell | Seen fine cell, unseen previous class | Constant training previous class | Unseen coarse context |
| --- | ---: | ---: | ---: | ---: |
| ZL3b / split | 168 | 349 | 116 | 0 |
| ZL3b / join | 146 | 254 | 75 | 0 |
| IT2a / split | 155 | 287 | 84 | 0 |
| IT2a / join | 155 | 287 | 84 | 0 |

These are transition counts, using each treatment's full denominator above.
The constant-context flag can overlap the unseen-previous flag; these columns
are not a partition. No backoff or invariant feature case is dropped.

The [complete lossless report](exact-slot-length-prediction.json.gz) retains all
20 fitted fine-table sets, **4,598** fitted contexts, **8,660** scored locus records,
**52,771** transition receipts and **105,542** exact F0/F1 probabilities. Every
receipt includes target slot, current/previous classes, training support and
constant-context state. All four model losses, three contrasts, fold/group/locus
weights, signs and decisions remain present. No native token text is included.
The original whole-locus counts are coarsened only by the already fixed ten-class
rule; old source/count-vector fingerprints and cohort/exclusion ledgers agree.

## Freeze and independent verification

The plan was pushed and remote-verified at
`0fabd754ee60e36b08589a56ac9f9506d73b2e86`. The synthetic-tested producer and
[18-entry manifest](exact-slot-length-pins.json) were pushed and remote-verified
at `7d07e42a704d7e93c4e25e9986818d4641b80923` before new native fine fits.
**46 relevant tests**, including fourteen new regressions, passed before fitting.
No model, feature, strength, class, cohort, fold or criterion was revised after
these negative results. Each treatment's complete coarse fitted/scored records
are checked before its fine fits. A separate whole-parent typed replay also
verifies all original metadata and scientific fields.

Three additional independent-checker regressions bring the relevant total to
**49**. Exact hand cases and normalization cover matched-weight mixtures,
variable-target/constant-previous equality, unseen backoffs and corrupted count
marginals. Synthetic folds cover every-locus/transition accounting, unchanged old
losses, source/slot features and an excluded-fold values/labels/size perturbation
that leaves its fitted tables unchanged. Tests also cover partial families,
changed pins, typed cache drift, lossless transport, existing outputs and initial/
serialization-time native/source/plan/catalog/manifest/code aliases and redirects.

The [independent checker](../../scripts/verify_exact_slot_length_prediction.py)
uses the accepted native adapter only for ingestion. Separate eligibility
accounting reproduces all **2,165** retained and **1,719** excluded loci. A union-
find calculation rebuilds the complete canvas dependency graph and selected
86-component/five-fold manifest. Direct slot iteration and integer arrays rebuild
all coarse/fine fitted tables. New probabilities use a separate weighted-mixture
formula, with no production fine feature, fitting, probability or scoring function.
It verifies every exact probability/support receipt, **34,640** locus/model losses,
all tables, old losses, complete summaries and fixed decisions. Full typed report
reconstruction and complete producer byte replay agree.

- Producer SHA-256: `f299d79d49555b312651658e71289b77c97f5e2aac9067fa6594bfd1a9e2632f`.
- Manifest SHA-256: `3c31d97b437e3f0b37be9dbc2ca19d8189945e72c71618eb1bb997574940305f`.
- Expanded JSON SHA-256: `647fa9879141b5b3d9101c8f24e168722360a73aab2a035ccfb35548de6d2b40`.
- Gzip SHA-256: `7c17ddfe3f9826122b5a7a305af93d224ded94798f1cf2124b5e8424baa7ac64`.

The deterministic 1,883,991-byte gzip preserves every byte of the 44,607,824-byte
JSON, with zero mtime and no embedded filename. The frozen producer can create
or check either plain JSON or gzip; no global numeric setting is changed.
For the recorded Python 3.14.3 runtime, standard library only:

```sh
python3 scripts/exact_slot_length_prediction.py \
  --check research/baselines/exact-slot-length-prediction.json.gz
python3 scripts/verify_exact_slot_length_prediction.py
python3 -m unittest tests.test_exact_slot_length_prediction \
  tests.test_independent_exact_slot_prediction
```

Use `--new-report NEW_PATH.json.gz` for an exclusive new output. Source/catalog/
code/plan/manifest/parent/index inputs are protected before calculation and again
after full serialization; existing destinations are refused. Outgoing archive
contents, code, links and public commit metadata are inspected before publication.
The contribution includes no source image, raw transcription, credential or
private local path.

## Interpretation and next test

The new models lose on all four exposed treatments and all folds; the original
coarse predictor's mixed gains and failed criterion remain unchanged. This limits
the stated exact-slot/matched-weight predictors. It does not show that counts
are independent, refute smooth positional structure, validate the toy gradient,
or exclude sequence information under other models. The categorical exact-slot
features and common shrinkage weight can be poor estimators; revision requires
another registered version, rather than changing this result.

Prior exposure, ten-class coarsening, related editions, source annotations,
coarse/unverified image links and unrecorded content dependencies remain limits.
Exact encoded slots are not established physical positions. A future mechanism
needs justified representation/features, useful control variation, honest fit/
evaluation exclusions and prospective source-linked predictions under the
[decipherment protocol](../DECIPHERMENT_PROTOCOL.md). No glyph policy, copying
mechanism, language, decipherment or translation is adopted.
