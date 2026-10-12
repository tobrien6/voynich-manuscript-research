# Exact token recurrence across encoded paragraph locus boundaries

## Question and exposure

Do literal native-Eva tokens repeat at consecutive encoded locus boundaries
within the exact common paragraph corpus more often than under independently
uniform token permutations within each original locus?

Commit this method before inspecting boundary repeat counts or control moments.
The sources, paragraph grouping, adapter exclusions, and earlier within-locus
repetition results are already exposed. This is exploratory representation-level
evidence, not an untouched evaluation, proposed glyph mapping, or decipherment.
The paragraph corpus producer is proposed in PR #95; preserve its complete
replay and provenance, and resolve any producer revision before publication.

## Fixed cohort and statistic

- Rebuild and verify the complete common paragraph corpus and its committed
  token-free coverage report. Use its all-member/all-four-variant eligibility
  rule, all generic P subtypes, native case, and split/join comma policies.
- Keep every common eligible paragraph in the report. A boundary is between
  each consecutive pair of original member loci, never between paragraphs.
  Do not merge same-line fragments, reconstruct physical rows, or bridge an
  empty locus. Retain locators, kinds, drawing counts, variables and source IDs.
- Score a boundary only if both endpoint loci contain at least one token in
  every source/policy variant. Retain every omitted boundary and reason.
  Apply no additional length, drawing, locator, subtype, section, or position
  filter. This measures encoded token adjacency; drawings and fragment locators
  limit any inference about physical word adjacency.
- For each retained boundary, score one if the left locus's final token equals
  the right locus's first token exactly, otherwise zero. Sum without weights
  over boundaries within a paragraph and over all paragraphs. Report complete
  boundary and paragraph denominators, observations and source/policy differences.
  Do not emit native token strings in the committed result.

## Exact conditional control

Permute token occurrences uniformly and independently inside each original
locus; preserve its size and token multiplicities. Move nothing between loci,
paragraphs, pages, or sources. This stipulated control changes endpoint roles;
an excess can reflect positional effects or annotation conventions as well as
sequence dependence. It does not isolate a copying mechanism.

Let p_i(t) be token t's frequency divided by locus i's size n_i. For boundary
i to i+1, the repeat probability is sum_t p_i(t) p_(i+1)(t). Its variance is
p(1-p). Two nonadjacent boundaries use disjoint loci and have zero covariance
under this control. For adjacent retained boundaries around middle locus M:

- If n_M >= 2, its first and final tokens are separate without-replacement
  draws. Their joint repeat probability is
  sum_(a,b) p_L(a) p_R(b) c_M(a)(c_M(b)-1[a=b]) / (n_M(n_M-1)).
- If n_M = 1, both boundaries use the same token occurrence. Their joint
  probability is sum_a p_L(a) p_M(a) p_R(a).
- Subtract the product of the two boundary probabilities for covariance.
  Include covariance only for original adjacent boundary indices; omitted
  boundaries never create a new neighbor. Total variance is the sum of
  Bernoulli variances plus twice every adjacent covariance.

Use exact rational arithmetic for probabilities, means, variances and centered
counts. Verify every formula by exhaustive small synthetic permutation spaces,
including repeats, singleton middle loci, missing boundaries and constants.
Report SD and centered-count/SD only as descriptive scales; zero variance has
null SD-scaled contrast. No Gaussian tail, Monte Carlo tail, significance
threshold, candidate decision or model fit is specified.

## Reproducibility and limits

Record source/corpus/coverage/plan/implementation fingerprints, every eligible
paragraph and original boundary, exclusion reasons, and all four variant
summaries. Complete deterministic replay must reject altered inputs or results.
Protect sources, code, both plans, parent reports and verification inputs from
output writes, including resolved and hardlink aliases.

The common corpus is heavily selected by conservative whole-unit exclusions.
Units and tokens remain encoded source annotations, not adjudicated physical
paragraphs, glyphs, decoded words, translations or independent observations.
Source editions and comma policies are dependent. The control's independence
assumptions describe a conditional reference distribution, not independent
manuscript sampling. A later mechanism claim requires an explicit generator,
position-sensitive controls and exposure-aware prospective evaluation.

Work as verified tobrien6 in the isolated contribution checkout, submit a
focused PR, and leave acceptance to the established maintainer workflow.
