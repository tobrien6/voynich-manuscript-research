# Prefix-position patterns across source strata

## Question and fixed analysis choices

Does the pooled q/y boundary pattern persist when paragraph starts and source
Currier labels are separated, and same-line fragments are excluded?

The [plan](PREFIX_STRATA_PLAN.md) was committed before this run, after the full
corpus had already been explored in [POSITION_EFFECTS.md](POSITION_EFFECTS.md).
This is a robustness check on exposed data, not a held-out confirmation.
It studies only literal EVA `q` and `y` prefixes, rather than the separately
developed first-token-length experiment.

## Sources, cohort, and method

Use the exact [ZL3b and IT2a pins](../../data/transliterations.json). Require a
present P0 locus and a locator in `@`, `+`, or `*` in **both** sources. This retains
**3,848 of 3,884** shared P0 locations and excludes 36 same-line fragments.
The excluded identifiers and selected-location digest are in
[prefix_strata.json](prefix_strata.json).

Within each source and uncertainty treatment, partition by effective source
`L` metadata (A, B, or unset here) and by the source `<%>` paragraph-start mark.
The paragraph mark is read outside free comments; its accuracy has not been
verified against every source image. ZL and IT assign some paragraph starts
differently. Every cohort, including unset and empty cases, is retained.

Run all split/join and exclude/first-choice uncertainty combinations. Preserve
original token slots and exclude unreadable or empty readings. A boundary is
eligible only if its original slot remains and at least one other token is
retained. Compute boundary feature minus mean of other retained tokens within
each locus, giving loci equal weight. The [conditional control](POSITION_EFFECTS.md)
preserves each locus's token bag and exclusions, with exact mean/variance and
199 shuffled contrasts, seed 20261011.

## Observations

Primary split/exclude **first-slot** contrasts, expressed as fractions:

| Source | Source L label | Paragraph start | Eligible loci | q contrast | y contrast |
| --- | --- | --- | ---: | ---: | ---: |
| ZL3b | A | no | 1,223 | +0.06209 | +0.12396 |
| ZL3b | A | yes | 222 | -0.05995 | -0.03437 |
| ZL3b | B | no | 1,815 | -0.03564 | +0.14623 |
| ZL3b | B | yes | 449 | -0.17274 | -0.01542 |
| ZL3b | unset | no | 26 | -0.02647 | +0.10383 |
| ZL3b | unset | yes | 9 | -0.05697 | -0.15069 |
| IT2a | A | no | 1,250 | +0.06483 | +0.12222 |
| IT2a | A | yes | 233 | -0.06755 | -0.03277 |
| IT2a | B | no | 1,851 | -0.03459 | +0.14765 |
| IT2a | B | yes | 462 | -0.17504 | -0.01685 |
| IT2a | unset | no | 26 | -0.02625 | +0.10614 |
| IT2a | unset | yes | 9 | -0.07704 | -0.14526 |

The first-slot y enrichment in the pooled result is concentrated in
non-paragraph-start loci. In both A and B, source-marked paragraph-start cohorts
instead have negative y contrasts in the primary treatments. Among
non-paragraph-start loci, the primary q contrast is positive in A and negative
in B in both sources. A pooled q rate therefore hides different group patterns.
The complete report contains all other policies and the last-slot results;
the table is a readable summary of the declared primary treatment.

The unset cohorts are small and their estimates should remain descriptive.
Report denominators and the complete controls rather than ranking isolated
tails. The 192 feature contrasts are exploratory, dependent, unadjusted for
multiple comparisons, and use a coarse minimum shuffle tail of 0.005.
No equality between source groups and identified natural languages is asserted.

## Reproduce and validate

Python 3.10 or later; standard library only. Recorded run: Python 3.14.3.

```sh
python3 scripts/prefix_strata.py --output research/transliteration/prefix_strata.json
python3 scripts/prefix_strata.py --check research/transliteration/prefix_strata.json
PYTHONPATH=tests python3 -m unittest test_prefix_strata test_locus_positions test_token_baselines test_ivtff test_source_audit -v
```

The script reuses the accepted source reader, paired-source guard, token policies,
and conditional position routines. It never pools unrelated alphabets or infers
unwritten boundary readings. Tests check the joint locator restriction,
comment/paragraph separation, complete partitioning, retention of unset and
empty cohorts, and original boundary eligibility. The full committed report
can be replayed with its source hashes, selection digest, all exclusions and
metadata, and every shuffle contrast.

## Limits and next test

The source labels and paragraph marks are annotations, not independent evidence
for languages or causal scribal roles. The locator filter removes one ambiguity
without reconstructing physical lines. The same sources, rows, and policies
recur across these tests and the pooled analysis, so they cannot be counted as
new independent samples.

Candidate mechanisms should account for these conditional contrasts and make
additional predictions beyond restating them. A next test can distinguish
representation artifacts from image-supported prefix structure, using a
documented glyph-unit scheme and independently checked source regions before
assigning any plaintext or semantic role.

The [conservative common-cohort check](CONSERVATIVE_PREFIXES.md) now applies the
accepted whole-locus adapter to the same prefix question, with one location list
eligible under all source/spacing cases and source-defined paragraph partitions.
