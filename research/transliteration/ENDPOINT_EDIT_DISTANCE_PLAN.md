# Native-string distance across encoded locus boundaries

## Question and exposure

Does the literal native-Eva edit distance between consecutive locus endpoints
depart from an anchored whole-locus order control on the same common paragraph
cohort? Does this broader statistic retain variation where exact-repeat counts
were mostly invariant?

Publish the fixed method and synthetic-tested implementation before measuring
the new manuscript distances or control moments. The complete native sources,
paragraph corpus, one-repeat boundary result, proposed anchored repeat control
in PR #105, and f82r source-image check in PR #142 are already exposed. This is
exploratory sensitivity on encoded strings, not a glyph mapping, language
comparison, untouched evaluation, fitted candidate or decipherment.

## Fixed input, cohort and measurement

- Rebuild the accepted common paragraph corpus and verify its complete coverage
  report from pinned ZL3b/IT2a bytes. Retain its all-member/all-four-variant
  eligibility, all present generic P subtypes, native case, source metadata,
  drawing handling and split/join comma treatments.
- Include every common eligible unit and every original consecutive boundary.
  Require every locus to have a nonempty token list in all four variants. If
  that condition fails, stop rather than silently filtering the cohort. Keep
  the original candidate/common/excluded denominators and all invariant units.
- For each boundary, use the last token of its left locus and the first token
  of its right locus. Levenshtein distance uses unit insertion, deletion and
  substitution costs on native case-preserved ASCII letters. No transposition,
  glyph grouping, case folding, prefix removal, synonym or pronunciation rule
  is added. Normalize by max(len(left),len(right)), giving an exact rational
  cost from zero to one. The metric is symmetric; identical strings cost zero.
- Sum normalized costs over all consecutive boundaries, with equal boundary
  weight. Report the sum and mean cost, conditional mean/variance and centered
  effect. Lower observed cost means greater literal string similarity relative
  to the stated control. No source, paragraph size, section, drawing, locator,
  token length or favorable-result subset is selected afterward.

## Anchored whole-locus control and exact moments

Preserve each locus's entire token sequence and identity/metadata. Fix the
first and last locus of each paragraph; uniformly permute only its interior
locus identities, independently between paragraphs. Move no token between
loci or units. Singletons and units with only one allowed order remain in the
denominator, with zero conditional variance. This preserves endpoint roles
while changing interior neighbors and fine positions.

For every distinct ordered pair of locus identities a,b, record its normalized
endpoint cost w(a,b) and probability of adjacency in the anchored path. Reuse
the compatible directed-chain counting formula explored in PR #105 as a
standalone weighted-path helper, with attribution and complete synthetic
verification; do not modify that pending producer or rely on its cached result.
Compatible edge requirements contract to chains, first/last chains are anchored,
and k remaining chains among m interiors admit k!/m! probability. Conflicting
successors/predecessors, cycles, incoming edges to the fixed first, outgoing
edges from the fixed last and premature anchor-joining chains are impossible.

With exact single/joint edge probabilities, compute
E[S]=sum w_e p_e and
Var(S)=sum w_e^2 p_e(1-p_e)+2 sum_(e<f) w_e w_f(P[e,f]-p_e p_f).
Include all edge-pair dependencies, not only neighboring original boundaries.
Use exact rational arithmetic for weights and all moments. Record the complete
weight/probability matrices, every unit's observation and moments, diagonal
and covariance variance components, and joint-event accounting. These inputs
must be sufficient to replay every pair; a huge repeated pair ledger is not
required. Sum unit moments under the stipulated independent-unit control.

Report invariant/varying unit counts separately in every variant. Exact zero
variance defines invariance and must agree with the observed cost. SD-scaled
effects are descriptive, with null values for zero variance. No tail, threshold,
model preference or mechanism decision is chosen; do not add one after viewing
the result. Preserve all four variants and their dependence.

## Verification, provenance and limits

Before execution, exhaust small synthetic anchored orders with arbitrary
rational edge weights and repeated endpoint payloads, checking exact mean,
variance, fixed anchors, identity multiplicity and input preservation. Check
edit distances independently on small strings, including case and empty helper
inputs; the actual corpus endpoints must be nonempty. A later independent
position-assignment calculation must verify real edge/joint probabilities and
aggregate moments without the production chain/moment functions.

Pin source/catalog/corpus/coverage/plan/implementation bytes, retain every unit
and original locus identity and all denominators, and commit no native token
payload. Complete report replay rejects altered provenance/data, duplicate JSON
keys and nonfinite constants. Output guards must run before computation and
after serialization immediately before writing, protecting sources, code,
plans, parent coverage and verification inputs, including symlinks/hardlinks.

Distance depends on arbitrary native letter segmentation and coding choices;
its costs are not adjudicated glyph, sound, plaintext-word or semantic distances.
Whole-unit exclusions strongly select this corpus. Encoded locus/paragraph
boundaries and reading routes around drawings remain source conventions with
incomplete image/glyph review. Edition/policy dependence and unrecorded content
dependencies persist. Conditional-control independence is not independent
manuscript sampling. Any mechanism claim needs frozen joint predictions,
comparable glyph/source representations and exposure-aware prospective data.

Use verified tobrien6 contribution authority and noreply author/committer
metadata. Inspect exact new outgoing objects for sensitive content. Preserve
existing history and submit a focused PR to the established maintainer workflow.
