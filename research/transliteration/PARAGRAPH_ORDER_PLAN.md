# Boundary recurrence with locus endpoint roles preserved

## Question and exposure

Does the existing boundary-repeat count depart from a control that preserves
every locus's original token sequence and first/last token roles, while changing
only the order of interior loci in each common encoded paragraph?

Publish this plan and the synthetic-tested implementation before computing the
new manuscript control moments. The parent boundary result, source bytes,
paragraph corpus and earlier position findings are already exposed. The parent
has one repeat over 652 encoded boundaries in all four variants. This is a
declared exploratory sensitivity comparison, not a new unseen evaluation or
candidate decipherment test. The parent PR #102 is pending acceptance; resolve
its current producer/input revision before publishing this follow-up.

## Cohort and fixed control

- Rebuild the common paragraph corpus and the complete parent boundary report
  from pinned sources. Verify every parent field and provenance pin, not just
  its totals. Retain the same whole-unit eligibility and all four source/comma
  variants. Preserve all 233 retained units and their 885 member loci; do not
  select a source, section, locator, paragraph size or favorable subset.
- Require every locus in a retained unit to be nonempty in all variants, and
  every original consecutive boundary to be retained by the parent report.
  If this condition fails, stop rather than silently changing the cohort.
- Treat each locus's complete token sequence as an atomic record. Keep its
  identity, variables, kind, locator and drawing counts attached to that record.
  Do not permute tokens, relabel source records, join loci, remove fragments,
  infer glyphs, or create adjacency across excluded material.
- Fix the first and last locus of each unit. Permute all interior locus
  identities uniformly and independently within each paragraph. Singleton,
  two-locus and three-locus units have no order variation and remain in all
  denominators. Move nothing between units, pages, sources or comma variants.
- The statistic is unchanged: count exact last-left/first-right native-Eva
  token equality along consecutive loci. Report every unit's observed count,
  exact conditional moments, size, invariant status and original member IDs.
  Retain the parent within-locus-control summary for comparison.

## Exact control probabilities and variance

For a unit with N loci, let m=max(N-2,0) interior identities. Each of the m!
interior orders is equally weighted. A directed edge a->b denotes consecutive
whole-locus identities with equal endpoint token strings. Build all such edges
among distinct original identities; native strings remain local.

For any required directed-edge subset, check whether all edges can coexist in
a path with the declared first/last identities. A self-edge, incoming edge to
the fixed first identity, outgoing edge from the fixed last identity, conflicting
incoming/outgoing requirements, or directed cycle makes the event impossible.
Compatible requirements form directed chains, which can be contracted to
blocks. Chains attached to the first/last identities are anchored. If the two
anchors share a chain before all identities are included, no complete ordering
can satisfy it. If that chain includes every identity, exactly one ordering is
valid. Otherwise k unanchored chains can be arranged in k! ways, and event
probability is k!/m!.

Compute exact single-edge and two-edge probabilities by this chain count.
The total repeat mean is the sum of single-edge probabilities. Variance is
sum p(1-p) plus twice every distinct edge-pair covariance q-p_a p_b. This
includes incompatible, shared-identity and disjoint requirements. Sum unit
means and variances under the stipulated independent-unit control. Use exact
rational arithmetic throughout; decimals and SD scaling are descriptive.

Verify the chain probabilities by exhaustive small interior-order spaces,
including impossible/cyclic/anchored chains and no-interior cases. Independently
enumerate synthetic endpoint assignments and compare complete repeat-count
means/variances. Zero variance defines an invariant unit and must agree with
its observed count. Retain these units; null SD-scaled contrasts replace an
undefined division. No tail, threshold, fitted model or mechanism decision is
chosen, and no new criterion may be selected after observing the control.

## Reproducibility and limits

Record source/corpus/parent-report/plan/code fingerprints, all original unit
and locus IDs/metadata, every endpoint-match edge and its probability, all edge
pairs and joint probabilities/covariances, and exact aggregate moments. Commit
no native token strings. Complete replay rejects altered parent or result
content, duplicate JSON keys and nonfinite constants. Output protection covers
sources, implementation, plans, parent reports and verification inputs,
including resolved and hardlink aliases, before any computation or write.

Whole-unit uncertainty exclusions strongly select this corpus. Encoded loci
and paragraphs are not adjudicated physical words, lines or paragraphs.
Moving interior fragments or drawing-associated loci is a mathematical
sensitivity control, not a proposed physical manuscript process. This preserves
within-locus endpoint roles and terminal paragraph locus identities but not
all fine position, image, source-label or content dependencies. Editions and
policies remain dependent; conditional-control independence is not independent
manuscript sampling. Any mechanism claim needs its own frozen predictions,
representation and exposure-aware prospective evaluation.

Use verified tobrien6 contribution authority in the isolated checkout. Submit
a focused PR for the established maintainer workflow; do not self-approve or
make a competing disposition on the parent PR.
