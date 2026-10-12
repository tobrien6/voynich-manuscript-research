# Matched-edge native-record control plan, version 1

Question: how do the four historical H repeated-type contrasts change when
conditioning on every surviving native record's token bag, while retaining the
identical observed tokens and all N−1 flat-stream edges?

Freeze this plan before computing this new null on any manuscript variant.
The [global assay](REPEATED_TYPES.md) is already exposed: B is 114–115 against
E[B] about 47.5, and A is 313–315 against E[A] about 116.5. This follow-up is
exploratory sensitivity work on known approximate inputs, not untouched
evaluation, original-author replication or a decoding hypothesis.

## Matched input and measured edges

Reuse all four accepted approximate H reconstructions unchanged. Verify the
frozen parser report, record/flat corpus hashes and global report inputs. A
counts equal adjacent-pair events; B counts distinct complete representation
types with one or more equal adjacent pairs, once over the entire flat stream.
Retain asterisks and case. Native-record joins and within-record edges crossing
pre-manual normalized index gaps remain measured, exactly as in the global
assay. Do not filter, fill or reinterpret them.

Keep empty/excluded records in the reconstruction, but they contribute no
positions. Consecutive nonempty records supply a joining edge even if empty
records intervene. Native records are source-defined units, not verified
physical manuscript lines. The identical observed A/B, boundary diagnostics,
N, distinct types and both corpus hashes must match the global report.

## Conditional null and exact means

Permute the retained tokens independently within each native record, preserving
every record length and complete token-frequency bag. The original retained
position/provenance slots remain fixed, including index gaps. No token crosses
a record boundary, but the concatenated control retains all observed edge
locations, including the joins. Conditioned means are not a within-record-only
statistic.

For one type with c tokens in a record of m positions, let T[a,b] be the
probability of no internal self-repeat with its first/last occupancy bits a,b.
For m≥2:

```text
T[a,b] = C(m−c−1,c−a−b) / C(m,c)
```

An impossible binomial choice is zero. For m=1,c=0, T[0,0]=1; for m=1,c=1,
T[1,1]=1. Other entries are zero. These cases share one endpoint position and
have no internal edge. Empty records are skipped.

Transfer the probability vector for the previous record's last occupancy bit
to the next record, disallowing previous-end=1/current-start=1 on a joining
edge. Initialize it as [1,0]. Summing the final vector gives P(no self-repeat)
for that type on the entire measured stream. Sum 1−P(no self-repeat) by type
for exact E[B], using linearity of expectation. Types are dependent. Absent-type
nonempty records reset the endpoint state; sparse consecutive runs of records
containing the type may be factored to compute the same probability efficiently.

For A, sum internal expectations c(c−1)/m over record/type pairs and joining
expectations c_left*c_right/(m_left*m_right) over adjacent nonempty records/type
pairs. Report within/join contributions separately and their exact total.
Use exact Fractions and hex integer serialization as in the global assay.
Zero expected/sample means give undefined ratios. No B variance, tail or
significance threshold is declared.

## Deterministic controls and comparison

Retain ten trials 0–9 with seed 20261012. Use the accepted SHA-256 counter and
Fisher–Yates primitive. For each retained record independently, hash UTF-8 JSON
with `ensure_ascii=False`, separators `(',', ':')`, frame:

```text
[algorithm, record_corpus_sha256, "historical-native-record-v1", seed, trial,
 [ring_policy, f66r_column_unit], native_locator]
```

Each trial starts from the original tokens in every record. Verify each record
bag, the whole bag and retained lengths. Record A/B for every trial, control
means, exact means, observed/mean ratios and exact global/conditioned mean
differences. The global control values remain as recorded; this is not a shared
random-number coupling between nulls.

## Validation, interpretation and next work

Before measuring this null on the manuscript, enumerate small occupancy subsets
to validate every endpoint matrix, and exhaustively combine distinct tiny-record
permutations to validate full-edge E[A]/E[B]. Include empty/singleton records,
forced internal/join repeats, nonconsecutive type runs, overlapping pair events,
case/relabel invariance, deterministic replay, per-record bag preservation and
failed source/hash/output guards. Check that a single record reduces to the
global mean. Then retain every four-variant outcome and all forty controls.

This comparison changes only null conditioning on the fixed approximate input
and fixed edge population. It tests sensitivity to within-record token
composition and confines order changes to those records. It does not establish
a causal decomposition, prove that a record is a physical line, remove glyph
uncertainty or identify a language/cipher. Any residual contrast can reflect
finer position structure, native-record ordering or encoding conventions.

Keep parser/count discrepancies and unmatched labels unresolved. Further
mechanism comparisons or finer position-conditioned controls require new plans;
do not tune this null or select a variant after observing the results.
