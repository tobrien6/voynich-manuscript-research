# Endpoint edit distance with endpoint-length patterns fixed

Recorded 2026-10-12. Publish this plan and a synthetic-tested implementation
before computing the new manuscript control distributions. The native sources,
common paragraph corpus, accepted ASCII endpoint-distance result (#152) and
grouped-unit sensitivity (#156) are already exposed. This is an exploratory
conditional sensitivity check, with no untouched evaluation or decipherment.

## Question and unchanged measurement

The accepted anchored-order control preserves whole loci and their endpoint
roles, but moves endpoint lengths between interior positions. Does its small
negative centered ASCII edit cost persist when the original endpoint-length
pattern is preserved? How much identity-order freedom and cost variation does
that conditioning remove?

Rebuild the entire pinned common paragraph corpus and accepted ASCII distance
report, requiring exact typed equality. Retain all 233 eligible units, 885 loci,
652 boundaries and all 438 excluded candidates in the inherited coverage.
These counts describe the accepted source-defined corpus, not verified physical
paragraphs. Stop on changed eligibility, identities, source/policy order or
empty endpoints; select no favorable subset. Retain all four native source and
split/join variants and every invariant unit.

Reuse the parent's exact cost matrix: unit-cost Levenshtein over case-preserved
native ASCII, divided by the maximum endpoint string length. Equal boundary
weights, original order and original observed cost remain unchanged. No glyph
grouping, token-count matching, case folding, prefix removal, new source reading
or grouped-policy result is added to this focused ASCII control.

## Two fixed conditioning scopes

Keep first/last locus identities fixed. At each interior position keep its
original stratum label, and uniformly permute whole locus identities only among
positions with the same label, independently by stratum and by paragraph.
Identical endpoint payloads remain distinct identities; multiplicities count.

1. **Variant endpoint lengths:** the stratum is the ordered pair of ASCII
   lengths (first token, last token) in that variant. Allowed identity orders
   may differ between editions/policies; no paired-source distribution or
   source preference is inferred from their differences.
2. **Common endpoint lengths:** the stratum is the ordered vector of those
   four pairs, in the parent's exact source/policy order. This fixes endpoint
   lengths simultaneously in all four variants and provides the same allowed
   identity orders for each variant. It may remove most order freedom; retain
   that result without relaxing or merging strata after measurement.

Lengths refer to notation strings, not physical glyph counts. Anchors are
always fixed even when their labels match interiors. The original order is
always allowed. For interior stratum sizes n_s, the number of identity orders
is the product of n_s!, compared with the parent's (n-2)! (or one for n<2).
Report all per-locus pairs, common vectors, stratum memberships, possible-order
counts and exact retained-order fractions. Do not count these dependent
controls as independent manuscript samples.

## Exact probability and variance method

For every distinct directed identity edge, compute its adjacency probability
under the restricted position assignments. For every two weighted possible
edges compute the joint probability, including zero/impossible events.
Compatible required edges form one or two directed chains. Enumerate their
placements in the fixed slot pattern, reject overlaps and anchor/stratum
violations, and divide by the number of possible assignments of the involved
interior identities: product_s (n_s falling k_s). This differs from counting
all complete interior orders and must be independently checked. Conflicting
predecessors/successors, self edges, cycles and reversed anchors are impossible.

Use exact Fractions for costs, probabilities, means and all variance terms:
E[S] = sum(w_e p_e), and Var(S) includes weighted Bernoulli diagonal terms and
every distinct edge-pair covariance. Retain complete probability matrices,
diagonal/twice-covariance components and joint-event counts so all terms can
be replayed. Sum paragraph moments under the stipulated independent-unit
reference distribution. Report exact and decimal displays, centered mean cost,
SD-scaled descriptive contrast, invariant/varying counts and unit identities.
No normal tail, threshold, preference criterion or copying/language claim is
introduced. A zero-variance unit must have observed cost equal to its mean.

Compare each conditioned expected cost and variance with the unchanged parent.
Report newly invariant units and the change in centered mean cost, explicitly
as a difference between reference distributions rather than a paired random
variable with an invented variance. No post-result length bins, alternative
strata, excluded units or favorable folios may be selected.

## Verification and publication

Before new measurements, exhaust small synthetic restricted identity orders,
including interleaved strata, matching anchor/interior labels, duplicate
payloads, singleton strata, impossible chains, arbitrary signed rational
weights and unconditioned one-stratum equivalence. Compare every single/joint
probability and moment with direct full-order enumeration. Verify complete
synthetic source/corpus integration and no mutation or silent filtering.

After measurement independently enumerate assignments of involved identities
to their permitted slots, without the production chain/probability/moment
functions. Verify every real single/joint probability, each cost/moment,
aggregate, partition and freedom count. Rebuild and compare the full report.

Pin accepted parent report, native corpus/source dependencies, plan and
implementation bytes. Commit no native token payload. Strict typed JSON and
complete replay reject forged data/provenance, duplicates and nonfinite values.
Guard output paths before computation and after complete serialization directly
before writing, protecting source/catalog/corpus/parent/plan/code/check inputs
and hardlink/symlink aliases. Inspect exact outgoing files and Git objects for
sensitive data. Submit through a focused PR as verified `tobrien6`, upstream
owner with admin/maintain/push permission, with GitHub noreply metadata; the
established maintainer workflow retains final review/disposition.

Conditioning can eliminate the signal together with most available variation;
that does not establish that length explains manuscript production. Any
remaining departure also retains character-composition, annotation, route,
selection and exposure confounds. The two editions/policies are dependent.
The next mechanism test needs explicit joint predictions, justified glyph
representation, comparable controls and honestly prospective material. No
translation or verified glyph reading follows from this statistic.
