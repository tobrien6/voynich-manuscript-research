# Fixed generator interior order: all 24 target points miss the seed ranges

All **24** manuscript source/spacing/count-policy/centering points lie above
their corresponding ranges across the **31** fixed self-citation generator
seeds. This is an exploratory constraint on the accepted configuration under an
approximate encoded-row comparison. It does not reject every copying mechanism,
replicate a paper result, identify a language, or support a translation.

The [published plan](SELF_CITATION_INTERIOR_PLAN.md) preceded implementation and
new measurement. The [complete report](self-citation-interior.json) retains every
seed, eligibility exclusion, count-vector fingerprint, exact rational mean,
range endpoint and gap. No Java process, seed, configuration or permutation draw
was added or changed for this comparison.

## Fixed inputs and comparison units

This reuses all Java 17 seeds 1–31 from the accepted
[prefix diagnostic](SELF_CITATION_PREFIX_PROFILE.md), author source commit
`9e98c9122a0f490905e8b66f3911fc7ce095fd26`. The parent report is pinned to
SHA-256 `140731ba67ca1a9bd2bb35460a4f6a19b5cff671627c4020f9f76f9362191ca9`.
The separate Java 22/1,200-row seed census is not part of these inputs.

Before any new measurement, both complete output files for every seed matched
the parent hashes and each other. Both effective configurations and all recorded
stdout/stderr hashes matched, as did the observed ledger bytes. All **52,204**
observed ledger rows were checked against native file line numbers, byte
intervals, row hashes and space-delimited group counts. Exactly the first row
in each case is the initialized input. Context flags and counters remain
model provenance; they are not adjudicated manuscript paragraph annotations.

The complete parent manuscript selection and token/context digests reproduced:
1,683 joint clear regular P0 loci, native `L=B` in both ZL3b and IT2a, with no
recorded drawing interruptions. Requiring at least five original tokens in
**every** source/spacing variant retains **1,590** common keys and records all
**93** extra exclusions. Native L labels do not identify natural languages.

Each seed contains one initialized row and 1,683 newly generated rows. Excluding
initialization and fewer-than-five-group rows leaves **1,517–1,556** eligible rows
per seed: **47,566** of **52,173** newly generated rows across the fixed cases.
Every one of the **4,607** short generated rows remains in the exclusion audit.
Unsupported notation or a failed identity would block the whole comparison,
rather than being repaired or dropped.

Original source tokens and program-produced space-delimited groups are retained
without regrouping. Generator groups are neither internal GlyphGroup segments
nor verified manuscript words. A P0 locus is not necessarily a complete physical
line. Source/model physical line, paragraph and glyph correspondence remains
unverified. These are explicit encoded measurement units, with equal weight per
eligible locus or row and no length matching, balancing or reweighting.

## Exact statistic and operational counts

The three unchanged [count policies](../baselines/eva-unit-protocol.json) count
ASCII letters, listed bench sequences, and listed bench plus minim sequences.
They use case-sensitive longest matches within each original token, single-letter
fallback and exact source reconstruction. They are finite notation counts, not
adjudicated physical glyph counts. Only original interior tokens/groups enter
the statistic; the first and last remain excluded.

For interior lengths `x` of size `m >= 3`, set `d_i = m*x_i - sum(x)` and
`D = sum(d_i^2)`. The uncentered association is
`R = m*sum(d_i*d_(i+1))/((m-1)*D)`. Nonconstant unrestricted expectation is
`-1/(m-1)`. The half expectation is the exact mean under independent permutations
of the first `ceil(m/2)` and remaining slots, including their crossing pair.
Scores are `R - E[R]` for each scope. Constants contribute zero and stay in the
same denominator, including cases that become constant or variable under another
policy. Exact half-invariant identifiers and size counts remain in every profile.

All means use rational arithmetic; display rounding below does not determine
membership. For each target, its corresponding inclusive min/max range contains
all 31 fixed seed values. No range is a confidence interval, fitted acceptance
probability or permutation p-value. All comparisons are defined here; an undefined
fixed seed or target would have remained present and made the relevant ranges
and overall criterion undefined.

## All six profiles and all 24 target points

| Count policy | Centering | Fixed 31-seed range | ZL3b split | ZL3b join | IT2a split | IT2a join |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| ASCII letters | Unrestricted | [-0.022521, +0.007503] | +0.096916 | +0.060756 | +0.090315 | +0.090315 |
| ASCII letters | Half | [-0.018452, +0.007934] | +0.074597 | +0.049867 | +0.070791 | +0.070791 |
| Bench sequences | Unrestricted | [-0.022776, +0.019261] | +0.063895 | +0.031914 | +0.051930 | +0.051930 |
| Bench sequences | Half | [-0.019327, +0.021469] | +0.046787 | +0.025225 | +0.039694 | +0.039694 |
| Bench and minim sequences | Unrestricted | [-0.019016, +0.010572] | +0.103375 | +0.071230 | +0.097826 | +0.097826 |
| Bench and minim sequences | Half | [-0.017869, +0.012570] | +0.073368 | +0.050757 | +0.068826 | +0.068826 |

**0/24** target points are inside their corresponding ranges. The smallest
outside-range gap is **+0.0037562084**, for ZL3b join, bench sequences, half
centering. The exact rational endpoints and gaps, all 186 generator seed scores,
and all 24 target scores are retained. IT2a spacing treatments coincide on this
cohort; related editions and count policies are not independent replications.

Eligibility and group-count mixtures differ even with identical source keys:

| Encoded target | Eligible loci | Interior groups | Interior pairs | Mean original tokens per locus |
| --- | ---: | ---: | ---: | ---: |
| ZL3b split | 1,590 | 12,467 | 10,877 | 9.840881 |
| ZL3b join | 1,590 | 11,358 | 9,768 | 9.143396 |
| IT2a split | 1,590 | 12,255 | 10,665 | 9.707547 |
| IT2a join | 1,590 | 12,255 | 10,665 | 9.707547 |

Generated eligible rows have seed-specific mean group counts of **9.361039–9.966452**.
All generated pre/post-eligibility and source post-eligibility histograms are retained. Equal-row averaging does not
control these mixtures or finer position/context profiles. The manuscript subset
here also differs from the earlier 2,165-locus interior-order analyses; these
values must not be relabeled as a replay of those broader cohorts.

## Publication and verification

The plan was published and remote-verified at
`48424b1b1dd978698e69b390b499b2bcc68b10a2`. The synthetic-tested implementation
and its 22-entry [input/helper manifest](self-citation-interior-pins.json) were
published and remote-verified at `296650621a595830e1dd982e795db8a5f063f8cd`
**before** this new measurement. Their SHA-256 fingerprints are:

- Original producer: `63628dcbe5aaa1fe16f2ee01b2150eed6717eff19fa0c27eb96d8398d6447ac8`.
- Pin manifest: `8d1b9e97d61ce0052b6e0d15e764f5e46007652ef81fa05d22f1f347d10a9d6e`.
- Original complete report: `f23c65bc2b7830522fe4e24f710c266d2f81ad0ef69d46636106c1a5cb9c7b8d`.

During maintainer review, importing either arithmetic module was found to disable
Python's process-wide integer conversion digit limit. Both now convert the long
decimal fraction strings in small local chunks and leave that limit unchanged.
The selection, counting, statistical and receipt functions are unchanged, as are
the original plan and all 22 input pins. The complete report differs only in its
producer fingerprint; every fraction string, display value and other field is
preserved. The maintained producer is
`fa01c8d9f44527895b9242302ac6158a54958b97f41fc1617b287693247c878f`;
the maintained report is
`113b4b407691c3765e949de5f8390703bf0fdd94cfa3d6d9a30ed05790ff6829`.
Two added regressions exercise signed 9,001-digit fractions, invalid decimal
strings, the minimum supported digit limit and fresh-process imports. All 20
focused producer/checker tests pass after this maintenance repair. Final maintainer
integration with main `76df1248eca12db976a36c626867f335e26005d3` passes all 846 repository tests.
Both the full package replay and the separate maintainer arithmetic audit also
match the preserved report after integration.

The producer validates the manifest itself, all accepted source/helper/artifact
hashes, and every fixed run before measuring. It protects supplied run artifacts,
native sources, catalog, plan and code before analysis and again before exclusive
report creation. A saved-report replay preserves JSON scalar types, preventing
booleans or floats from substituting for recorded integer counts.

Fifteen new synthetic tests and 63 relevant existing tests passed before
measurement. They cover complete row accounting and typed identities, all-source
eligibility, literal case/boundary handling, both constant status transitions,
exact small exhaustive half ensembles, equal-row means, all fixed seeds,
inclusive ranges/gaps, undefined cases, changed pins, complete run receipt
failures and protected output aliases.

After adding the separate arithmetic checker and integrating current main,
all **81** relevant tests passed: the 78 above plus three checker regressions
for literal longest matches, exhaustively enumerated full/half expectations,
and refusal of incomplete policy profiles. The frozen experiment producer and
complete scientific report remained byte-identical.

An independently written [literal scanner and expanded-product rational scorer](../../scripts/verify_self_citation_interior_math.py),
using the established native token-packet reader only for source ingestion,
reconstructed all **105** source/model count vectors, **525** exact raw/null/centered
means, all **31** generated eligibility audits, and all **24** range memberships
and gaps. It used no production scoring or segmentation functions. A complete
saved-report replay from the independently archived 31-run dataset also matched
every field, including generation receipts and invariance diagnostics. This is
computational verification on the same exposed inputs, not independent evidence
for a mechanism or unseen-material evaluation.

For Python 3.10 or later, supply matching local output directories from the
[parent reproduction procedure](SELF_CITATION_PREFIX_PROFILE.md#reproduction-and-verification).
Third-party source/output/config/log payloads and private local paths are not
included in this contribution. The producer reads archived outputs without starting Java.

```sh
python3 scripts/self_citation_interior.py \
  --runs PATH_TO_MATCHING_31_RUN_DIRECTORY \
  --check research/literature/self-citation-interior.json
python3 scripts/verify_self_citation_interior_math.py \
  --runs PATH_TO_MATCHING_31_RUN_DIRECTORY
python3 -m unittest tests.test_self_citation_interior
```

Use `--new-report PATH_TO_NEW_REPORT.json` instead of `--check` to save a new
report. Existing destinations are refused. Complete receipt equality includes
the recorded Python version; changed helper/source hashes require an explicitly
versioned analysis instead of silently updating pins.

## Interpretation and next test

The fixed configuration's previously exposed prefix failures now have an
additional interior-order mismatch under all three declared count policies and
both centering scopes. These aggregate measurements constrain this setup on
the selected encoded units. They do not isolate a causal deficiency, exclude a
copying family, validate a glyph mapping, or establish meaning.

Reused manuscript initialization, corpus/output exposure, source-dependent
eligibility, uncertain unit correspondence, differing group-count mixtures and
finer position/context structure remain limitations. A revised mechanism needs
a new version and a prospectively declared comparison of comparable units,
including explicit size/context conditioning and calibrated controls, before
claims about decoding or translation.
