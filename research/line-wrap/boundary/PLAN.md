# Width-conditioned boundary costs under labelled IID wrapping

## Question and source context

Can a width-only wrapping process change the mean edit cost between the last
label of a completed row and the first label of its completed successor,
relative to an unconditional incoming-pair reference? Does conditioning on
those two widths remove the generative centered expectation under this model?

The accepted [wrapping control](../RESULTS.md) demonstrates first-width bias,
while the [interior proof](../interior/PROOF.md) establishes a different
conditional symmetry. The accepted [native endpoint method](../../transliteration/ENDPOINT_EDIT_DISTANCE.md)
compares literal endpoint strings across consecutive encoded loci. Its
[pending length-pattern sensitivity](https://github.com/tobrien6/voynich-manuscript-research/pull/179)
uses anchored whole-locus permutations. The present known-law generator is a
different reference distribution; it neither reproduces that control nor
reinterprets its manuscript measurements as physical lines.

Seven actual reference blobs are pinned in [settings.json](settings.json) at
accepted main `4d5baddaf0c9d5b9fd7c323579ceafefe24f03d4`. They document the
rules/metric; no original result, source text or image enters the calculation.
Future live documentary edits must not silently replace these references.

## Fixed model and cases

Every incoming label is an independent draw from the specified categorical law.
Labels are fictitious ASCII strings. Width is their literal string length,
an artificial additive geometry with no manuscript glyph-width interpretation.
The labels and strictly positive probabilities are:

| Law | Labels and probabilities |
| --- | --- |
| Uniform three | `a`: 1/3, `bb`: 1/3, `bc`: 1/3 |
| Unequal three | `a`: 1/2, `bb`: 3/8, `bc`: 1/8 |
| Constant width | `bb`: 1/2, `bc`: 1/2 |

Every stream has exactly **seven** incoming labels. Enumerate the entire finite
Cartesian product with exact product probabilities, including the initial
transient. There is no stationary start law or sampled simulation. Separator
width is one. Append on equality; close only when the next label would overflow;
carry that same occurrence unchanged to the next row. Capacity is at least twice
the maximum label width plus separator, guaranteeing two or more tokens in
every overflow-closed row and exceeding the general maximum-width restriction.

Freeze all eight cases before calculating outcomes:

1. Uniform-three law, capacities 5, 6 and 7: three distinct cases.
2. Unequal-three law, capacities 5, 6 and 7: three distinct cases.
3. Constant-width law, capacity 5: a known zero contrast calibration.
4. Uniform-three law, capacity 20: a no-closed-pair calibration. Even the longest
   possible seven-token stream only fills capacity and receives no closing
   overflow. Its final tail remains unclosed.

These choices test a mathematical mechanism on known synthetic labels. The
conditional zero and constant-width/no-boundary cases are analytical
calibrations, not discoveries or untouched prospective predictions. The signs
and sizes of the other incoming-reference contrasts have no preference
criterion. Preserve all declared outcomes, including zeros and opposing signs.

## Boundary selection and exact costs

Retain an edge only between **two consecutive overflow-closed rows**. Do not
include the edge from the last closed row into the unclosed final tail. Exclude
that tail even if exactly full; keep its complete occurrence/width trace. A
case/stream with fewer than two completed rows has no eligible edge. It remains
in all probability and exclusion ledgers, with undefined mean rather than a
successful zero score. No singleton closed row is possible in these capacities.
The two endpoint occurrences are distinct even when their labels are equal.

Use unit insertion, deletion and substitution Levenshtein distance, divided by
the maximum nonempty label length. There is no transposition, folding, prefix
removal or glyph grouping. Retain every ordered label pair, including equal
labels. The incoming-pair expectation uses two independent draws from the
declared law. The width-pair expectation is

```text
mu(u,v) = sum p(a | width(a)=u) * p(b | width(b)=v) * d(a,b),
          over every ordered label pair in the two width bins.
```

Within-width probabilities are normalized from the **actual label law**;
unequal labels within the same width bin must not be made uniform. For a stream
with N eligible edges, record S=sum observed costs and M=sum mu(endpoint widths).
Its width-centered sum is S-M and its incoming-centered sum is S-N*mu_incoming.
Individual residuals can be nonzero even under the correct reference.

## Two distinct finite estimands

Keep both weighting definitions and their complete denominators:

- Pooled boundaries: E[S]/E[N], with matched reference E[M]/E[N].
- Equal eligible streams: E[S/N | N>0], with E[M/N | N>0].

The first uses expected boundary mass; the second first gives each eligible
stream a single mean and conditions on its exact probability mass. Do not
substitute one for the other or treat missing stream means as zero. When a
case has E[N]=0, both observed/reference/centered means are undefined; the
incoming law's own pair expectation remains a defined separate quantity.
Neither estimand is a stationary limit or manuscript sampling estimate.

Conditional on the complete width sequence, IID labels factor into their
within-width laws. Row construction, closure, eligibility, N and these weights
depend only on widths. Therefore every eligible edge has conditional expected
cost mu(u,v), giving exact zero width-centered expectation under both estimands
and within each positive-probability eligible width-sequence class. No label
independence between *rows* is inferred. Spelling/cost-dependent selection or
weights, dependent input labels or contextual widths fall outside this proof.
Distinct occurrences may carry equal labels. General lower-capacity models
can have a singleton middle row whose one occurrence is shared by two boundary
costs; conditional label factorization does not make those costs independent.
The fixed capacity guard excludes singleton closed rows here. No variance or
covariance claim is made; the mean argument uses linearity and the ledger
retains the actual endpoint occurrence indices.

## Record and independent checks

Publish every label stream, exact probability, completed-row start/end/carry
trace, unclosed tail, eligible boundary positions/widths, observed and reference
costs, per-stream sums/means and case probability/eligibility/count ledgers.
Retain the full input pair matrix and width-bin conditional matrices. Check
probability mass one and every stated zero with rational arithmetic. Report
positive/negative/zero individual residual masses without selecting examples
after seeing their signs. Keep complete records for the no-edge case.

Use a standalone standard-library producer. Independent tests must reconstruct
partition cut points by a separate maximal-fitting-prefix method, preserve
every occurrence and carry boundary, and use a separately coded recursive edit
oracle. Exhaust bounded paths for all cases, both estimands, eligibility and
width classes, including the unequal within-width law, repeated labels,
equality fit and censored tail. Test literal input/reference drift, deterministic
replay and preservation of existing/linked/late output collisions. Output must
be a new unlinked file, checked again immediately before exclusive writing.

Publish and verify the protocol/settings remote head **before stream outcome
calculations**. Record the implementation/test and first-calculation chronology
honestly. This is known calibration with prior exploratory motivation, not
independent exposure certification. Keep the research PR separate from a new
UI, empirical overlay, simulation, manuscript fit, p-value, glyph decision,
language hypothesis, decipherment or translation. Use `tobrien6` and public
noreply commit metadata; assigned maintainers retain final review/merge.
