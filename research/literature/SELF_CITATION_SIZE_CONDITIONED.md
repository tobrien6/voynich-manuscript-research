# Exact-size comparison: missing full support and mixed supported results

The full 1,590-locus manuscript comparison is **undefined** after exact original
group-count standardization: some fixed generator seeds have no eligible rows
of required sizes. The predeclared secondary common cohort retains **1,426**
loci. Its ZL3b join bench-sequence points lie inside both standardized seed
ranges; the other **22/24** points lie above their ranges. Both results and every
unsupported cell are retained in the [complete report](self-citation-size-conditioned.json).

This follows the [parent interior diagnostic](SELF_CITATION_INTERIOR.md), PR #137,
which exposed different row-size mixtures and had all 24 unconditioned points
above their seed ranges. The [published plan](SELF_CITATION_SIZE_PLAN.md) froze
exact-size weighting, support failures and the count-only common-subset rule
before new conditional measurements. This is exploratory sensitivity analysis
on the same already exposed inputs, with an approximate encoded-row bridge.

## Exact conditioning and immutable generation evidence

All 31 Java 17 seeds 1–31, original control/observed outputs, configurations,
process/log/ledger identities, initialization exclusions and parent eligibility
are unchanged. No new Java processes, permutation draws, parameters, seed
replacement or grouping policies were used. Complete parent report replay
preceded new measurement. The original parent SHA-256 is
`f23c65bc2b7830522fe4e24f710c266d2f81ad0ef69d46636106c1a5cb9c7b8d`.
The separate Java 22 census and changed-rule ablations are separate experiments.

Size `k` is the number of **original** tokens or space-delimited generated groups,
not the number of segmented notation units. All eligible rows are partitioned
into exact-size cells across the complete observed grid **5–21**. Each cell keeps
all three accepted literal count policies, uncentered associations, exact full
and half expectations, centered means, counts/vector hashes and constant/half-
invariant diagnostics. Empty cells retain zero row counts and undefined means;
they are not merged, imputed, smoothed or replaced with another size.

For each variant, let `n_k` be its source row count of size `k` and `N=sum(n_k)`.
The standardized model mean for seed `s` is
`sum_k n_k * mean_model(s,k) / N`, separately for each count policy and centering.
The target is its equal-locus source mean using those same size frequencies.
Constants contribute zero and remain in their cells and source weight denominator.
All **35** source/model decompositions reassemble every parent's raw, null and
centered mean exactly, with unchanged denominators.

P0 loci and model rows remain approximate encoded units. Equal original group
counts do not establish physical line, word, paragraph or glyph equivalence.
Weights come from exposed manuscript counts; they do not create an untouched
split or establish model fitting. Native L labels remain source metadata.

## Primary: full parent cohort remains undefined

A seed value requires every size with positive target weight to have a nonempty
cell in that seed. A range requires all 31 fixed seed values. Missing sizes and
exact missing target weights are retained per seed/variant; no seed or source key
was removed from this primary analysis.

| Full target | Source loci | Seeds with all required sizes | Fully defined 31-seed comparisons |
| --- | ---: | ---: | ---: |
| ZL3b split | 1,590 | 3/31 | 0/6 |
| ZL3b join | 1,590 | 12/31 | 0/6 |
| IT2a split | 1,590 | 9/31 | 0/6 |
| IT2a join | 1,590 | 9/31 | 0/6 |

Sizes 5–12 occur in every seed; size 13 is missing in seeds 4 and 14, and further
required large sizes have additional support failures. Therefore all **24** full-
cohort ranges and the global compatibility criterion are **null**. Individual
fully supported seed values are retained. Missing support is a coverage
limitation, not numerical evidence of either a fit or a miss.

## Secondary: identical common keys supported by every seed

The frozen count-only rule first finds sizes present in every seed: **5–12**.
A parent source key survives only if all four source/spacing token counts lie
in that set. It retains **1,426/1,590 = 89.6855%** of keys and records every one
of the **164** exclusions with variant counts and missing-seed reasons. Source
keys stay identical across all four treatments. No conditional score influences
selection, and this smaller cohort does not repair the primary undefinedness.

The actual target frequencies define each variant's weights:

| Original size | ZL3b split | ZL3b join | IT2a split | IT2a join |
| ---: | ---: | ---: | ---: | ---: |
| 5 | 50 | 81 | 53 | 53 |
| 6 | 99 | 126 | 88 | 88 |
| 7 | 104 | 125 | 130 | 130 |
| 8 | 159 | 224 | 150 | 150 |
| 9 | 216 | 277 | 228 | 228 |
| 10 | 308 | 300 | 323 | 323 |
| 11 | 296 | 225 | 292 | 292 |
| 12 | 194 | 68 | 162 | 162 |

Every seed is standardized to each variant's own exact distribution. Ranges
therefore differ across variants. The following values are rounded for display;
exact rational membership and all standardized seed values are retained.

### Unrestricted centering

| Target | Count policy | Source mean | Standardized 31-seed range | Inside |
| --- | --- | ---: | --- | --- |
| ZL3b split | ASCII letters | +0.086901 | [-0.037095, +0.013878] | no |
| ZL3b split | Bench | +0.055522 | [-0.030433, +0.020544] | no |
| ZL3b split | Bench + minim | +0.094661 | [-0.039083, +0.006060] | no |
| ZL3b join | ASCII letters | +0.049958 | [-0.031967, +0.024518] | no |
| ZL3b join | Bench | +0.022022 | [-0.025731, +0.032761] | yes |
| ZL3b join | Bench + minim | +0.062655 | [-0.026721, +0.010533] | no |
| IT2a split | ASCII letters | +0.080275 | [-0.032996, +0.017119] | no |
| IT2a split | Bench | +0.042776 | [-0.028015, +0.023373] | no |
| IT2a split | Bench + minim | +0.090759 | [-0.035106, +0.005821] | no |
| IT2a join | ASCII letters | +0.080275 | [-0.032996, +0.017119] | no |
| IT2a join | Bench | +0.042776 | [-0.028015, +0.023373] | no |
| IT2a join | Bench + minim | +0.090759 | [-0.035106, +0.005821] | no |

### Half centering

| Target | Count policy | Source mean | Standardized 31-seed range | Inside |
| --- | --- | ---: | --- | --- |
| ZL3b split | ASCII letters | +0.067188 | [-0.029367, +0.006753] | no |
| ZL3b split | Bench | +0.039479 | [-0.027042, +0.019374] | no |
| ZL3b split | Bench + minim | +0.066418 | [-0.032150, +0.006984] | no |
| ZL3b join | ASCII letters | +0.043074 | [-0.026342, +0.013126] | no |
| ZL3b join | Bench | +0.017994 | [-0.023000, +0.028966] | yes |
| ZL3b join | Bench + minim | +0.044421 | [-0.024157, +0.012688] | no |
| IT2a split | ASCII letters | +0.063744 | [-0.027651, +0.010281] | no |
| IT2a split | Bench | +0.031787 | [-0.025346, +0.020672] | no |
| IT2a split | Bench + minim | +0.062477 | [-0.029984, +0.009704] | no |
| IT2a join | ASCII letters | +0.063744 | [-0.027651, +0.010281] | no |
| IT2a join | Bench | +0.031787 | [-0.025346, +0.020672] | no |
| IT2a join | Bench + minim | +0.062477 | [-0.029984, +0.009704] | no |

All 24 supported comparisons are defined. **2/24** points are inside and **22/24**
are above their ranges; the global supported-cohort criterion is false. The
smallest positive outside-range gap is **+0.0111154303**, for IT2a bench counts
under half centering (both spacing policies coincide). These related treatments
are not independent replications, and the fixed min/max range has no calibrated
probability coverage or p-value.

Both the target cohort and model weights differ from the parent comparison.
The two inside-range points cannot be attributed to reweighting alone. They do
not establish equivalence or validate the configuration. The remaining misses
limit this setup on the declared supported encoded units; they do not reject an
entire copying family or isolate a particular program rule.

## Publication, reproduction and verification

The plan was pushed and remote-verified at
`75c462c4e52866c05fde302934b85b2bfffa8476`. The synthetic-tested producer and
four-entry [manifest](self-citation-size-pins.json) were pushed and remote-verified
at `8c9e3d7186d16ce600137ed779a491e2e7f489aa` **before** new conditional measurements.
The original manifest pins the first parent report/producer/manifest and plan;
all 22 parent source/helper/artifact pins are also checked. The producer
reconstructs the parent report completely and validates every archived run
before measuring exact-size cells. Output aliases are rejected before calculation
and final exclusive writing; existing destinations are refused.

- Original pre-amendment producer SHA-256: `91ce99488c38d53afa27302103bb698c2d87020e51a3d805186f2eaa1f12f801`.
- Original pre-amendment manifest SHA-256: `65c9d900f34172c98a5ff38b780fc2612a7fed9c5412a91634859f4d3976e275`.
- First complete report SHA-256: `df4b1f52137311083e6da69814ec6f6fc6f2d86b81251ffebf86cea9f46faf61`.

Before measurement, **95** relevant tests passed, including **14** new producer
regressions. They verify original-size conditioning under all policies, exact
rational target weights, parent reassembly, constant retention, complete seed/
variant/policy families, missing support and zero-cohort nulls, count-only common
support, exact inclusive ranges/gaps, pin failures, scalar-type-preserving replay,
protected input aliases and final write protection.

After measurement, the separately written
[arithmetic checker](../../scripts/verify_self_citation_size_math.py) reused the
prior independent literal scanner/moment expansion, with separate support,
selection, weight and range calculations. It verified **1,989** count vectors
including empty cells, **768** target/model standardized policy profiles,
**3,840** weighted mean fields including undefined values, all **48** range
comparisons and **35** exact parent reassemblies. It uses no production selection,
scoring, segmentation or standardization functions. The established native
packet reader remains its source ingestion dependency. Three additional checker
tests give **98** passing relevant tests. Complete producer replay from the
second archived 31-run dataset matched every saved field, including diagnostics,
missing-support records and provenance. Producer/report bytes stayed unchanged.

## Accepted parent maintenance and exact preservation

[Amendment 1](SELF_CITATION_SIZE_AMENDMENT_1.md) adopts the accepted parent
serialization repair after PR #137 merge `8a08e771`. Local integer conversion
preserves the interpreter guard. The original plan, original manifest, first
parent/size reports and source texts remain in hashed inert snapshots, with an
explicit [transition record](self-citation-size-amendment-1.json). No original
pre-measurement timestamp or pin is silently replaced.

The effective parent report is
`113b4b407691c3765e949de5f8390703bf0fdd94cfa3d6d9a30ed05790ff6829`.
Only its producer fingerprint differs from the original. Every original numeric,
selection, cell, weight, comparison, support and reporting function AST in this
producer remains identical. The effective size report changes **only** four
provenance fields: `input_pins`, `pin_manifest_sha256`, `implementation_sha256`
and `parent_report_sha256`. Complete typed equality preserves every other field,
including all 24 primary nulls and the two supported inside-range points.

Current replay fingerprints are:

- Effective producer: `e1a420948591eaaa4571cc4ab2ed60d9c6cd930dcd40168128f647c8b036ec2c`.
- Effective 15-entry manifest: `7bb5faefbe8b6a7d2b2c3a6f678b973319175def3d4e4fabcc83d8b44b2276c0`.
- Effective complete report: `2610917f3946dc757d2d68a5839cb9be64c1d38b2567449c218bc4a1c6ad0522`.

The amendment/snapshots were published at `b55d41e` before effective replay;
the tested transition guard and effective producer at `f710f6a`. The guard checks
archive/decompressed hashes, accepted parent identities, unchanged protected
ASTs and exact report field allowances without executing any snapshot source.
Full native replay and the separate arithmetic checker pass under the unchanged
integer-string guard. All **106** relevant tests pass, including six new migration
regressions. The separate checker again verifies 1,989 vectors, 768 standardized
profiles, 3,840 weighted mean fields and 48 comparisons from the independent
archive. [Completed validation](self-citation-size-amendment-1-validation.json)
records the exact four-field transition. These are post-result maintenance
identities, not new untouched evaluation or pre-measurement claims.

Supply a matching archive from the
[parent reproduction procedure](SELF_CITATION_PREFIX_PROFILE.md#reproduction-and-verification).
Exact receipt replay uses the recorded **Python 3.14.3** runtime and frozen helper
bytes. A different Python version changes provenance and requires an explicitly
versioned parent/result record, even if its numerical calculation agrees.

```sh
python3 scripts/self_citation_size_conditioned.py \
  --runs PATH_TO_MATCHING_31_RUN_DIRECTORY \
  --check research/literature/self-citation-size-conditioned.json
python3 scripts/verify_self_citation_size_math.py \
  --runs PATH_TO_MATCHING_31_RUN_DIRECTORY
python3 -m unittest tests.test_self_citation_size_conditioned tests.test_self_citation_size_math
```

Use `--new-report PATH_TO_NEW_REPORT.json` instead of `--check` to create a new
report. Complete receipt equality includes the recorded Python version. No
third-party raw source/output/config/log/ledger payloads or private local paths
are included. Changed frozen identities require explicit versioning, rather
than silent pin updates.

## Limits and next research question

Exact original-size weighting addresses one mixture dimension. Within-size
notation-length distributions, position gradients, paragraph/context mixtures,
small conditional cells, reused manuscript initialization, whole-corpus/output
exposure and unverified physical correspondence remain. The supported cohort
also excludes 10.3145% of parent keys. These results neither remove those limits
nor identify a glyph, language, causal encoding mechanism or translation.

The fixed configuration still fails the declared supported-cohort aggregate
criterion, with two compatible points retained and full-cohort inference limited
by missing support. A revised model or further context conditioning needs a new
version, explicit comparable units, complete support accounting and prospective
controls. Claims about decipherment require separate evaluation of predicted
readings and source-linked passages.
