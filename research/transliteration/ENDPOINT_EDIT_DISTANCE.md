# Native endpoint distance with locus roles preserved

Consecutive encoded locus endpoints have a **slightly lower normalized native
string edit cost** than the anchored whole-locus order control in all four
treatments. The primary observed mean is 0.820318 versus 0.825519 expected,
a centered difference of -0.005201. This broader statistic varies in 99–101
paragraphs, while the earlier exact-repeat statistic varied in only four or
five. These are descriptive conditional comparisons on exposed, selected
transcription strings; no tail or candidate decision is supplied.

## Fixed method and chronology

The [plan](ENDPOINT_EDIT_DISTANCE_PLAN.md) was remotely published and verified
at `e647c6c`; the implementation and ten passing synthetic tests were published
and verified at `55a3cbc`, before computing the new manuscript measurements.
Source bytes, existing boundary results, the proposed
[anchored repeat control](https://github.com/tobrien6/voynich-manuscript-research/pull/105)
and f82r image check were already exposed. No metric, control, cohort, criterion
or favorable subset changed after these results.

Rebuild the [common paragraph corpus](PARAGRAPH_CORPUS.md) completely from the
pinned ZL3b/IT2a inputs and verify its coverage. Retain every common eligible
unit and consecutive boundary, all generic P subtypes, original case,
metadata and both split/join comma treatments. Empty endpoints would stop the
producer rather than silently filter it. The
[complete report](paragraph_endpoint_distance.json) retains all source/input,
plan and implementation fingerprints, original unit/locus identities, cost
and probability matrices, exact moments and variance components. Native token
payloads remain local.

For each boundary, compare the last native token of the left locus with the
first token of its successor. Levenshtein distance uses unit insertion,
deletion and substitution costs, divided by the maximum string length. There
is no transposition, case folding, prefix removal or glyph grouping. Costs
range from zero (identical strings) to one. Sum them with equal **boundary**
weight; the reported mean divides by the unchanged boundary count.

## Cohort and results

| Stage | Count |
| --- | ---: |
| Exact common paragraph-membership candidates | 671 units / 3,647 loci |
| Whole units eligible in both editions and both policies | 233 units / 885 loci |
| Whole-unit excluded candidates | 438 |
| Original boundaries retained in every treatment | 652 |
| Units with no interior-order choice | 130 |

| Treatment | Observed mean cost | Exact-control mean, decimal display | Centered mean cost | SD-scaled sum contrast | Invariant / varying units |
| --- | ---: | ---: | ---: | ---: | ---: |
| ZL3b split | 0.820318 | 0.825519 | -0.005201 | -1.184334 | 134 / 99 |
| ZL3b join | 0.808286 | 0.814575 | -0.006289 | -1.423312 | 134 / 99 |
| IT2a split | 0.818734 | 0.825055 | -0.006321 | -1.430017 | 132 / 101 |
| IT2a join | 0.818734 | 0.825055 | -0.006321 | -1.430017 | 132 / 101 |

Lower cost means greater literal string similarity under this metric. All
directions are negative relative to their control expectations, but the effect
is small on the zero-to-one cost scale. SD scaling has no stipulated normal
tail or significance interpretation. IT's two complete numerical records
coincide and remain one dependent source comparison.

Of the 103 units with multiple interior orders, four ZL and two IT units still
have invariant cost. All 233 units stay in the denominator. Greater permissible
variation than exact repeats does not establish calibrated power for a language
or mechanism test. Whole-unit annotation exclusions strongly restrict coverage.

## Exact weighted path control

Keep each original locus's entire token sequence and metadata intact. Fix the
first and last locus of each paragraph, and choose uniformly among its interior
identity orders, independently between units. Nothing moves across loci or
paragraphs. Identical payloads remain distinct identities with their proper
permutation multiplicities. This preserves within-locus endpoint roles while
changing interior neighbors and fine positions.

Each distinct directed identity pair has a fixed normalized endpoint cost.
The chain-count formula from the proposed repeat control is reproduced with
attribution in a standalone [weighted helper](../../scripts/anchored_path_moments.py).
It imports neither that pending producer nor its cached result. Compatible
required edges contract into chains; anchor chains are fixed, while k free
chains among m interiors admit probability k!/m!. Conflicting, cyclic and
premature anchor-joining requirements are impossible. Identity-isomorphic
events share a cached probability without sharing their weights or records.

The sum's mean is `sum(w*p)`. Its variance contains each weighted Bernoulli
variance and **every** distinct weighted edge-pair covariance, including
incompatible and shared-identity events. Exact rational arithmetic is used
throughout. The report separates diagonal variance and twice the covariance
sum, with complete matrices and joint-event accounting sufficient to replay
all terms. Unit means and variances add under the stipulated independent-unit
reference distribution. This is not an assertion of independent manuscript
sampling.

There are 2,152–2,153 nonzero-cost possible edges per treatment. Across all four
variants, 428,111 distinct joint events enter the variance calculation. Edges
with zero cost or zero probability have zero contribution; their complete
matrix entries remain visible. Exact zero variance defines an invariant unit
and must agree with its observed cost. These units receive null SD-scaled
contrasts and are retained.

## Reproduce and independent verification

Python 3.10 or later; standard library only:

```sh
PYTHONPATH=tests python3 -m unittest test_endpoint_distance -v
python3 scripts/paragraph_endpoint_distance.py --check research/transliteration/paragraph_endpoint_distance.json
python3 scripts/paragraph_endpoint_distance.py --output /tmp/paragraph-endpoint-distance.json
```

The ten pre-execution tests exhaust 225 small-string pairs with a separate
recursive edit program, single/double adjacency events through seven identities,
and 35 arbitrary rational-weight matrices against complete anchored identity
orders. They cover fixed anchors, cached identity isomorphism, positive/negative
weights, constant and row-only invariant costs, source case and metadata,
singletons, no silent endpoint filtering, forged coverage, strict typed JSON,
and initial/late symlink/hardlink output protection.

An eleventh test added after the first result reconstructs every actual cost
matrix with independent recursive string comparison. It counts event
probabilities by assigning positions directly to involved identities, with a
separately sorted identity canonicalization, instead of contracting chains.
It checks every probability matrix, all 428,111 evaluated joint events, every
unit observation/mean/variance/component/invariant flag and each exact aggregate.
No production edit, chain or moment function computes its expected values.
Complete deterministic replay also checks the recorded provenance and every
field. Output paths are checked before computation and after serialization
immediately before writing; source/catalog/code/plan/coverage and verification
aliases are protected.

## Interpretation and next test

This metric treats native ASCII letters as edit units. Those are encoding
choices, with no adjudicated glyph, sound, plaintext-word or semantic distance.
Different glyph grouping or source conventions could change these costs. The
selected clear-unit corpus and dependent editions/policies do not provide
independent or unseen evidence.

Encoded locus/paragraph boundaries and reading routes around drawings remain
incompletely reviewed. The control changes fine neighbor/position relationships
and preserves only its stated constraints. A small conditional cost departure
cannot isolate a copying process, linguistic order, language or decipherment.

A later mechanism comparison should freeze a justified representation and
joint predictions, show how much variation remains under its controls, preserve
all unfavorable/invariant cases, and evaluate on honestly prospective material
with explicit dependency and exposure records. No English reading is proposed.
