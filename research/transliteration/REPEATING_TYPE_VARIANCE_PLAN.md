# Exact conditional spread of the repeating-type count

Freeze this follow-up before computing manuscript type variances. The accepted
source text, pair/distance measurements and repeating-type means/counts are
already exposed. This is an exploratory conditional-moment calculation, not
preregistration, a new held-out evaluation, or a fitted decoding candidate.

Question: what is the exact variance of the number of distinct representations
with any immediate self-repeat under the accepted fixed-gap within-locus
permutation control, accounting for dependence between type indicators?

Reuse all 3,884 shared present P0 loci and all eight source/uncertainty treatments
from REPEATING_TYPES.md. Rebuild and completely verify its parent mean report
before calculating variance. Preserve original excluded slots, entire-locus
token bags, source boundaries and global deduplication. Do not freeze token
allocations within retained runs, concatenate loci, change eligibility, or
rewrite accepted source/plan/producer/report/shuffle bytes.

Let J_t indicate no immediate repeat of type t anywhere in the cohort,
Q_t=E[J_t], and I_t=1-J_t. The accepted producer computes Q_t by multiplying
its per-locus no-event probabilities. Then:

```text
Var(I_t) = Q_t(1-Q_t)
Cov(I_a,I_b) = Q_ab - Q_a Q_b
Var(sum_t I_t) = sum_t Var(I_t) + 2 sum_(a<b) Cov(I_a,I_b)
```

For each locus and two distinct types with counts c_a and c_b, count assignments
of marked colors A/B and the remaining unmarked positions. Forbid AA and BB
on eligible adjacency edges; leave adjacency between unmarked positions
unconstrained. Reset previous-color state at fixed gaps. Track both marked
counts across every retained run, so assignments include allocation between
runs. Normalize by C(m,c_a) C(m-c_a,c_b). Every marked placement has the same
number of assignments of the other token representations, giving this ratio.

Multiply these joint no-event probabilities across independently permuted
loci. Pairs with no shared locus where both can repeat have zero covariance.
A type with exact Q_t=0 repeats deterministically under this control and has
zero variance/covariance; retain its observed/expected contribution. Use exact
fractions and signed covariance, including negative cases. Do not infer type
independence or sum per-locus distinct-type variances: global deduplication
changes the random variable.

Report every policy, parent count/mean/digest reconciliation, exact total
variance, marginal-variance sum, signed covariance adjustment, pair-accounting
counts, conditional SD and descriptive centered count/SD. Zero exact variance
has a null standardized contrast. Preserve exact fractions and decimal-scale
diagnostics when floating conversion would underflow or overflow. No normal
tail, confidence interval, calibrated significance, mechanism probability,
language, glyph reading or translation is requested.

Validate joint placement counts by direct original-coordinate three-color
enumeration with gaps. Validate corpus means and variances by exhaustive
independent locus permutations, including global deduplication, positive and
negative covariances, omitted edges, forced repeats and constants. Verify
single-locus bags with each frequency at most two against the accepted pair
moment helper. Test exact serialization and scale handling, protected outputs
on fully temporary input/code copies, strict caches, and complete report replay.

Record source/catalog, parent report/plan/engine, new plan/engine and exact
preprocessed-slot identities. The variance belongs to a stipulated conditional
reference distribution. Manuscript, source editions, policies, loci and physical
pages are not thereby established as independent observations. A mechanism or
paper comparison still needs matched input, statistic and control definitions.
