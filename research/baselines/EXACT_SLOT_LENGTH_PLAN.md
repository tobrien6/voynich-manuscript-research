# Exact-slot grouped length prediction: exploratory plan v1

Publish this plan and a synthetic-tested implementation before fitting any new
fine-slot manuscript counts or calculating their scores. The parent corpus,
coarse predictor results and synthetic positional counterexample are exposed.
All folds retain prior exposure; excluding groups from a parameter fit creates
no untouched manuscript evaluation or decipherment evidence.

## Question and immutable cohort

Does previous interior count class improve prediction after conditioning on the
source Currier label, exact interior size and exact target slot, with a matched
shrinkage weight that cannot produce a gain for a constant previous class?

Use the same 2,165 conservative common P0 loci, four ZL3b/IT2a spacing variants,
native ASCII notation lengths, ten classes 1..9/10+, complete 86 image-dependency
components and five deterministic folds as the accepted grouped predictor.
Endpoints remain excluded; target slots j=1..m-1 include the crossing pair.
Reuse the exact original group assignments without balancing, seed changes,
resampling or new exclusions. Do not pool treatments or source labels.

Pin the accepted parent report to SHA-256
`d271a627a4f37f4916f032fd5021cf6e14bcc9c0817337a6aeeccb1f29cc9810`,
its producer (`10d090fa79506c41d0974b9a3b1c75ecaf2d8bcc6adee16093291fb63ff432fb`),
the parent full order report, image-dependency report, complete canvas index,
catalog, native ingestion, cohort/component helpers and this plan in a frozen
manifest. Recreate the complete cohort/exclusion ledger, source/count-vector
fingerprints and group manifest. Reproduce every original coarse fitted table,
fold/group/locus score and summary exactly before fitting the new models.
The original coarse Q0/Q1 comparison remains unchanged, including its failures.

## Fine features and matched shrinkage

The old coarse context c=(source label,target half) remains the backoff prior.
The new fine context f=(source label,m,j) records the original interior size m
and zero-based target slot j. Its coarse half is determined by j>=ceil(m/2).
No relative-position bucket, learned position boundary, paragraph marker or
image-width proxy is added. Different source annotations remain literal inputs.

From training transitions only, let N(c,y) be coarse target counts, N(f,y) fine
target counts, and N(f,x,y) fine previous/target counts. Let n=N(f) and n_x=N(f,x).
The fixed prior is the exact parent Q0 formula

```text
Qc(y|c) = (N(c,y)+1)/(N(c)+10).
w(f) = n/(n+10).
F0(y|f) = w(f)*N(f,y)/n + (1-w(f))*Qc(y|c).
F1(y|x,f) = w(f)*N(f,x,y)/n_x + (1-w(f))*Qc(y|c), when n_x>0.
```

If n=0, F0=Qc. If n_x=0, F1=F0, including a wholly unseen fine context.
The same weight w applies to every observed previous-class subcell in that
fine context. Its effective previous-cell prior strength is 10*n_x/n, rather
than a second fixed-strength smoothing pass toward F0. No strength is tuned.
Counts in the coarse empirical prior may include the same training fine cell;
this reuse remains within training data and supplies no calibrated prior.

For each training fine context with n>0,

```text
sum_x (n_x/n)*F1(y|x,f) = F0(y|f).
```

If all its training previous classes are equal, F1 equals F0 exactly for every
target and for every scored previous class (unseen classes use the backoff).
Verify these identities exactly, not through rounded probabilities. They
remove the particular constant-feature gain caused by changed smoothing;
they do not guarantee that a gain identifies direct neighbor dependence.

## Complete scoring and support

Fit solely on the other four folds. Retain both new models' full fine target
and previous-target tables, the parent coarse-table identity and all training/
scoring group declarations. Record every scored transition's identity, target
slot, class pair, fine/coarse training support and exact F0/F1 probabilities,
including every backoff and constant-previous-context case. No native token text
is published. Original classes/contexts and every locus remain included.

Retain per-locus and aggregate log losses for all four models: original Q0/Q1
and new F0/F1. New probabilities are exact rationals before converting to floats
for log2 loss. Old Q0/Q1 retain their published binary-float calculation order.
Use the same transition, equal-locus and equal-group denominators, with complete
fold/group/locus records. Report three fixed contrasts:

- F1 over F0: primary previous-class increment at fixed fine features/weight.
- F0 over Q0: descriptive independent-position model refinement.
- F1 over Q1: descriptive combined model difference; context and shrinkage both
  change, so do not attribute it to position alone.

Positive gain means lower loss for the first-named model. Apply the parent's
diagnostic preference convention **only to the primary F1/F0 contrast**: positive
transition-weighted and equal-group gains, plus at least four positive folds.
Primary treatment is ZL3b split; report all four outcomes and the all-treatment
conjunction regardless of result. The other contrasts have no new pass threshold.
Keep negative gains, sparse/unseen cells and identical IT views explicit.
These scores are predictive comparisons, not tails, causal proportions or a
decipherment test.

## Verification and publication

Before manuscript fits, check exact normalized probabilities, hand-computed
examples, unseen backoff, constant-previous equality and empirical previous-
frequency mixture equality across synthetic fine contexts. Check m/j/half
features, ten-class coarsening, train-only counts, group exclusion, all-fold/
locus/transition accounting, support states and probability positivity. Perturb
only an excluded fold's values/labels and prove its fitted tables unchanged.
Check input pin drift, scalar-type preservation and initial/late direct,
symbolic/hardlink and parent-directory redirect output aliases.

After generation, independently ingest/rebuild all selected counts, labels,
dependency assignments and fitted tables. Compute the probabilities with a
separate algebraic implementation, calling no production fine fitting/scoring
functions. Check all exact transition probabilities/supports and all complete
loss/contrast records, summaries and fixed decisions. Reproduce the saved report
completely. Retain exact fractions and deterministic lossless transport without
changing global interpreter or Decimal settings.

Protect native sources, catalog, code, settings, plans, dependency/index and parent
reports before calculation and again after serialization immediately before
exclusive creation. Refuse existing outputs. Inspect exact outgoing artifacts,
decompressed content and public commit metadata for private/sensitive data.
Submit a focused contributor PR; assigned maintainers retain upstream disposition.

## Limits and next question

Exact encoded slots are finer declared features, not a continuous physical
position or a known sufficient model of layout. Sparse cells and the shared
empirical prior limit this model's useful support. A loss change compares the
specified predictors, and may still reflect omitted structure, source conventions
or model estimation. Count classes, related editions, coarse dependency links,
unrecorded content relationships and full-corpus exposure remain limitations.

No empirical outcome here validates the synthetic gradient, direct dependence,
copying, glyph identity, language or translation. Any future feature, class or
smoothing revision needs a new version and exposure statement. Explicit mechanism
readings still require prospective, source-linked rules and evaluation under the
decipherment protocol; keep every negative/mixed baseline in the record.
