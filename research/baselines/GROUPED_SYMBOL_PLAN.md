# Grouped within-token symbol prediction: exploratory plan v1

Commit this plan, its input pins and synthetic-tested implementation before any
manuscript model is fitted or scored. Earlier whole-corpus analyses, including
the paired symbol entropy report, motivated this question. All material is
previously exposed. Excluding a dependency group from parameter fitting does
not create untouched evaluation material or register a decipherment candidate.

Question: does a second preceding notation unit improve within-token prediction
beyond one preceding unit, using a fixed smoothed predictor on complete
image-dependency groups excluded from its fit? Also report the one-unit versus
zero-unit comparison. These are representation baselines for later mechanisms,
not language identification, glyph readings or a text-production explanation.

## Inputs, cohort, groups and folds

Reproduce the entire accepted paired-symbol entropy report, including every
frequency table, source pin and selection reason. Use its 2,485 common clear
regular P0 loci with no drawing interruptions, unchanged ZL3b/IT2a split/join
tokens, native case, and three declared longest-match unit policies. Do not
select a subset from entropy values or change a source. All twelve treatments
use the same keys, groups and folds; IT spacing variants remain dependent.

Pin all parent artifacts, unit definitions, catalog, reader/adapter/segmenter,
image dependency report, full canvas CSV and imported repository helper files
in `grouped-symbol-plan.json`. Reconstruct transitive leaf components from the
entire CSV using the accepted dependency helper. Require all selected pages to
have matched supported side references in exactly one component, agreeing with
the pinned image report. Keep all leaves and indexed canvases of each selected
component together, even when a leaf has no selected locus. Abort on unsupported
references, duplicate declarations or any mismatch; do not discard a page.
These are coarse source references, not adjudicated glyph/image mappings, and
they do not capture every possible content dependency.

Assign each group to one of five folds by taking the unsigned big-endian
SHA-256 of compact UTF-8 JSON `["grouped-symbol-prediction-v1",20261012,group_id]`
modulo five. Use `ensure_ascii=False`, separators comma/colon. Abort if any fold
is empty; do not choose a replacement seed. Fit each model using only the other
four folds, and score each locus exactly once. Publish complete component,
leaf, page, canvas and locus declarations and their canonical digest.

## Three frozen predictors

Each native token is one separate sequence. Apply the parent's case-sensitive
longest-match segmenter inside that token and verify exact rejoining. Prefix
two reserved `<BOS>` context labels and score all emitted units followed by
one `<EOS>` target. Start again for every token. `<BOS>` is never a target;
`<EOS>` is never followed by a target. There are no cross-token or cross-locus
transitions. A one-unit token has two targets. No word-space unit is scored.

The target alphabet for each unit policy is fixed before fitting: all 52
uppercase/lowercase ASCII letters, all patterns listed by that policy, and
`<EOS>`, sorted lexically without duplicates. It is not an observed vocabulary.
Unobserved uppercase letters or patterns keep prior mass. Verify every emitted
unit belongs to this alphabet. Use no Currier, section or slot covariate.

From training tokens alone count `N(y)`, `N(x,y)`, and `N(w,x,y)` across the
same complete target population. With alphabet size `K`, fixed root
pseudocount **0.5** per target and prior strength **16** at each context order:

```text
Q0(y)       = (N(y) + 0.5) / (N + 0.5*K)
Q1(y|x)     = (N(x,y) + 16*Q0(y)) / (N(x) + 16)
Q2(y|w,x)   = (N(w,x,y) + 16*Q1(y|x)) / (N(w,x) + 16)
```

Use the immediately preceding training-only lower-order distribution as the
prior. Unseen contexts back off exactly. At first token position both context
labels are `<BOS>`; at second position only the older label is `<BOS>`. All
three predictors include initials and termination in the same denominator.
No smoothing, alphabet, segmentation, fold, threshold or context is tuned
after the corpus run. These are deliberately limited empirical predictors.

## Scores and declared diagnostic criterion

Retain three summed negative log2 losses and target/token/unit counts for every
locus, fold, group and whole treatment. Report gains `loss0-loss1` and
`loss1-loss2` per scored target under pooled target weighting, equal-locus
weighting and equal-group weighting. Also retain unseen-context target counts.
Do not compare absolute bits across unit policies as if their units or context
reach were equal. Termination is a model event, not an additional glyph.

The primary treatment is **ZL3b split, ascii_letters**. Call the fixed
second-order diagnostic preference consistent only when pooled gain over Q1
is at least **0.02 bits per target**, equal-group gain is positive, and all five
fold pooled gains are positive. Report the same criterion for every treatment
and whether all twelve meet it, including failures. Report the Q1/Q0 gains as
secondary descriptive results without another selection criterion. This is a
fixed reporting convention, not a calibrated test, confidence interval or
claim that order two is optimal. Trying other choices requires another version.

For each fitted fold retain target totals, observed one/two-unit context counts,
training/scoring group identities, and a digest of every sparse fitted count
table serialized in sorted canonical order. Complete source replay reconstructs
those tables. Retain all per-locus scores; publish no native token strings.

## Validation and limits

Before a real fit, test hand-computed probabilities and log losses, normalized
distributions, exact unseen-context backoff, BOS/EOS reset, fixed alphabet
coverage, input rejection, complete/disjoint fold accounting, a held-out token
perturbation that cannot change its excluded fold's fitted-count digest,
transitive scan grouping, deterministic count serialization, changed pins and
strict duplicate/nonfinite JSON rejection. Output files must be new and created
exclusively, so late symlink/hardlink aliases cannot overwrite inputs. Full
replay checks every report field and retained score, not only the summary.

The original cohort's restrictive exclusions remain visible through the parent
receipt. Known scans are not all dependencies; near-identical tokens or passages
can appear across groups. The models weight symbol and termination targets,
not words or folios equally, and model scores depend on declared notation units,
the alphabet prior and included token boundaries. Report every weighting and
negative outcome. A gain can reflect orthographic/notation conventions and does
not establish linguistic content, a causal copying mechanism, a glyph map,
general entropy rate, decipherment or translation. A loss constrains these
particular fixed predictors, not all possible mechanisms.

Later mechanism comparisons need stronger comparable controls and an honest
prospective split under the [decipherment protocol](../DECIPHERMENT_PROTOCOL.md).
This contribution freezes a modest predictive baseline on already exposed data.

Before the first manuscript fit, import inspection added pins for four
transitively imported helpers (`locus_position_baseline`,
`run_locus_position_baseline`, `shuffle_token_lines`, `repetition_moments`). Their
analysis functions are unused here; their module bytes are nevertheless part
of the reproducible import environment. This completes the input scope after
the initial plan commit and synthetic implementation, without changing any
model, fold, cohort, score or decision choice. The final pre-fit commit records
all twenty artifact/helper pins and an import-closure regression.
