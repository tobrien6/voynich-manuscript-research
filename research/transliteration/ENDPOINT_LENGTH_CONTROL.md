# Endpoint length conditioning changes the small edit-cost contrast

Fixing the original endpoint-length pattern makes the centered native ASCII
edit cost **slightly positive in every treatment**, whereas the accepted
unrestricted interior-order control gave small negative contrasts. This
reversal comes with a large loss of variation: only 8–10 of the same 233 units
vary in cost, compared with 99–101 under the original control. It constrains
interpretation of the original contrast; it does not establish a length-based
production mechanism or supply a decisive language/copying test.

## Fixed question, inputs and chronology

The [plan](ENDPOINT_LENGTH_CONTROL_PLAN.md) was published and its remote head
verified at `1887894`. The implementation and eight passing synthetic tests
were published and verified at `1a0e383` before computing these measurements.
The native sources, complete corpus and accepted [ASCII result](ENDPOINT_EDIT_DISTANCE.md)
and [grouped-unit sensitivity](ENDPOINT_UNIT_SENSITIVITY.md) were already
exposed. The strata, two controls, cohort and metric were not revised after
the results. The ninth test was added afterward for independent verification
of every real result; the measured producer/helper remain unchanged.

The producer completely rebuilds the pinned ZL3b/IT2a corpus and ASCII parent,
then requires typed equality and unchanged input hashes. All 671 candidate
units / 3,647 member loci, 438 exclusions and 233 eligible units / 885 loci
remain represented in the inherited coverage. Every original boundary remains:
**652** in each of the four source/split-join treatments. Original observations,
case, identity membership and native endpoint cost matrices are unchanged.
The [complete report](endpoint_length_control.json) contains all 1,864
unit/variant/control records, length pairs/vectors, partitions, probabilities,
exact moments, order freedom and aggregate results. Native token payloads
remain local; the accepted source/corpus artifacts are unchanged.

## Conditional reference distributions

Preserve whole loci and fix first/last identities. At every interior slot keep
its original stratum label; uniformly permute identities within matching
strata. The original path is always allowed. Duplicate payloads remain separate
identities with their correct multiplicities. The two predeclared labels are:

- **Variant endpoint lengths:** ordered ASCII lengths of the first and last
  token, measured separately in that variant.
- **Common endpoint lengths:** the ordered vector of all four pairs in the
  parent's source/policy order. Each variant then shares the same allowed
  identity orders.

Every original boundary retains both endpoint lengths, its maximum-length
normalizing denominator and its unavoidable length-difference edit-cost lower
bound. Interior identities can change while the endpoint-length pattern stays
fixed. These are notation lengths, with no verified physical glyph counts.
The variant-specific controls have different allowed sets; their numerical
differences are not paired-source distributions.

For each stratum with n interior identities there are n! equally likely
assignments. Multiply these counts across strata and retain the exact fraction
of the parent's unrestricted (number of interiors)! orders. Anchors stay fixed
even when their labels match interiors. Nothing crosses a paragraph, and all
invariant units stay in the unchanged boundary denominator.

## Complete results

Costs are normalized native Levenshtein distances on a zero-to-one scale.
Centered means are observed minus conditional expected cost; positive values
mean less literal endpoint similarity than that reference distribution.
Displays are rounded; exact rational sums and variances are in the report.

| Treatment | Original centered mean | Variant-length centered mean | Common-length centered mean | Varying units, original / variant / common |
| --- | ---: | ---: | ---: | ---: |
| ZL3b split | -0.005201 | +0.002758 | +0.001838 | 99 / 8 / 8 |
| ZL3b join | -0.006289 | +0.003049 | +0.002095 | 99 / 10 / 8 |
| IT2a split | -0.006321 | +0.002204 | +0.001926 | 101 / 10 / 9 |
| IT2a join | -0.006321 | +0.002204 | +0.001926 | 101 / 10 / 9 |

| Treatment | Original observed mean | Variant-length expected mean | Common-length expected mean | Multiple-order units, variant / common |
| --- | ---: | ---: | ---: | ---: |
| ZL3b split | 0.820318 | 0.817560 | 0.818481 | 10 / 10 |
| ZL3b join | 0.808286 | 0.805237 | 0.806191 | 12 / 10 |
| IT2a split | 0.818734 | 0.816530 | 0.816808 | 11 / 10 |
| IT2a join | 0.818734 | 0.816530 | 0.816808 | 11 / 10 |

All 103 originally multiple-order units lose some order freedom in both
controls; no other unit gains freedom. The common control leaves one order in
223 units, two in seven, four in one and six in two. For variant-specific
controls, 221–223 units have one order and the largest retained count is 48.
Order freedom is distinct from cost variation: some multiple-order units have
constant costs. Each report record preserves its exact count and fraction.

Newly invariant units number 91/89/91/91 under variant conditioning and
91/91/92/92 under common conditioning. IT split/join remain numerically equal
dependent treatments. Reported SD-scaled contrasts are descriptive only; no
normal tail, threshold, favorable subset or decision criterion is introduced.
Changes in expected cost and variance compare different reference distributions,
without assigning a paired random-variable variance to their difference.

## Probability method and verification

The [restricted-path helper](../../scripts/stratified_path_moments.py) retains
directed-edge covariance accounting from the accepted anchored helper, with a
different probability calculation. One/two required edges form compatible
chains. Count their nonoverlapping placements in the actual slot-label pattern,
respecting fixed anchors and stratum memberships. Divide by the product of
falling-factorial assignments of the involved interior identities. Impossible
predecessor/successor conflicts, cycles, self edges and anchor violations have
zero probability. This counts events without enumerating all complete orders.

Exact mean and variance include every weighted diagonal and distinct edge-pair
covariance. Across both controls and all four variants, **15,974 joint events**
enter the calculation; zero/impossible joints remain in the accounting.
Complete matrices allow every term to be reconstructed. Unit moments add under
the stipulated independent-unit reference, not an independent-manuscript claim.

All **33 focused tests** pass: nine new length-control tests, eleven accepted
endpoint tests and thirteen corpus tests. Before measurement, all small binary
slot patterns through seven identities were exhaustively checked for every
single/two-edge probability and three arbitrary signed rational matrices per
pattern. Tests retain interleaved strata, equal anchor/interior labels,
duplicate payloads, singleton strata, invariant costs, input preservation and
one-stratum equivalence to the accepted control.

The post-result test separately reconstructs every native cost with recursive
string edits, each length partition and freedom count, and every probability
by direct involved-identity position assignments. It also enumerates every
complete allowed real path (at most 48) for independent means/variances, checks
all 15,974 production joints, each variance component and all aggregates,
displays, transitions and fingerprints. Its expected values use no production
edit, chain, partition or moment function. Full deterministic typed replay
passes. Strict duplicate/nonfinite/type checks and initial/late symlink/hardlink
guards protect source/catalog/corpus/parent/plan/implementation/check inputs.

```sh
PYTHONPATH=tests python3 -m unittest test_endpoint_length_control test_endpoint_distance test_paragraph_token_corpus -v
python3 scripts/endpoint_length_control.py --check research/transliteration/endpoint_length_control.json
python3 scripts/endpoint_length_control.py --output /tmp/endpoint-length-control.json
```

## Interpretation and next test

The original small negative contrast is conditional on allowing endpoint-length
patterns to move. It does not persist under these two stricter, fixed controls.
Because they retain variation in very few units, the reversal cannot isolate
length as a causal explanation or refute a broad copying/linguistic mechanism.
It also does not validate the positive contrast as a new manuscript property.

Character composition, native segmentation, source annotation/reading routes,
selection and prior exposure remain unresolved. The unchanged clear-unit
eligibility excludes most candidate paragraphs. No physical glyph alignment,
sound, meaning, translation or source correction is inferred. A mechanism
comparison needs frozen joint predictions and justified representations, with
controls that retain useful variation and honestly prospective material.
