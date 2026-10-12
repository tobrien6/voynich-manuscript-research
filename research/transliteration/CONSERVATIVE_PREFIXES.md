# Prefix controls on a conservative common cohort

## Question and selection-policy comparison

Do the paragraph/source-group prefix patterns persist after removing entire
loci containing ambiguity or extended notation, rather than excluding individual
tokens? The [plan](CONSERVATIVE_PREFIX_PLAN.md) was committed before this run.
The preceding [stratified prefix analysis](PREFIX_STRATA.md) had already exposed
the data, so this is exploratory sensitivity analysis.

This cohort uses `plain-eva-v1` whole-locus eligibility. It is distinct from
the earlier tokenizer's boundary-specific matched cohorts and from the separate
first-token-length experiment. Its conditions are P0, regular locators, and at
least two tokens in every source/spacing case. Only literal q/y prefixes are
reported; no length hypothesis is tested here.

## Exact sources and one fixed cohort

Use the pinned [ZL3b and IT2a sources](../../data/transliterations.json) through
the accepted [conservative adapter](TOKEN_ADAPTER.md). Verify its schema/version,
analysis unit, processing policies, and source IDs/hashes before selection.
Require eligibility with at least two plain-Eva tokens and a locator in `@`,
`+`, or `*` under **all four** combinations of the two sources and split/join
uncertain spaces. No cohort is fitted separately to a feature or boundary result.

This retains **2,907 of 3,884** shared present P0 locations. First and last-slot
tests, in both sources and under both spacing policies, use this same global
location list. Source paragraph annotations still define separate partitions;
matching locations does not mean matching annotations.

| Source | Spacing | Candidate P0 records | Excluded by adapter | Eligible, regular, at least two tokens |
| --- | --- | ---: | ---: | ---: |
| ZL3b | split | 3,884 | 930 | 2,922 |
| ZL3b | join | 3,884 | 930 | 2,921 |
| IT2a | split | 3,884 | 60 | 3,785 |
| IT2a | join | 3,884 | 60 | 3,785 |

The final 2,907-key intersection is smaller than each source-policy eligibility
set. Counts removed by adapter eligibility, token count, and locator conditions
can overlap; the report preserves reasons per excluded key and source/policy.
Neither per-source totals nor the four cases are independent manuscript samples.

## Method and observations

Use the accepted equal-locus-weight first/last boundary contrast, conditional
within-locus shuffles, exact null mean/variance, 199 permutations, and seed
20261011. Partition by each source's effective Currier `L` label and its own
paragraph-start mark. The unit is a source locus, not a reconstructed physical
line. Details of the [control](POSITION_EFFECTS.md) and the earlier
[source strata](PREFIX_STRATA.md) remain applicable.

First-slot split-policy observations on the fixed cohort:

| Source | L label | Paragraph start | Loci | q contrast | y contrast |
| --- | --- | --- | ---: | ---: | ---: |
| ZL3b | A | no | 929 | +0.06105 | +0.13004 |
| ZL3b | A | yes | 142 | -0.06718 | -0.03309 |
| ZL3b | B | no | 1,477 | -0.03524 | +0.14441 |
| ZL3b | B | yes | 334 | -0.18035 | -0.00698 |
| ZL3b | unset | no | 17 | -0.03207 | +0.10194 |
| ZL3b | unset | yes | 8 | -0.06409 | -0.11952 |
| IT2a | A | no | 927 | +0.06059 | +0.12802 |
| IT2a | A | yes | 144 | -0.06887 | -0.03402 |
| IT2a | B | no | 1,475 | -0.03585 | +0.14673 |
| IT2a | B | yes | 336 | -0.18495 | -0.00815 |
| IT2a | unset | no | 17 | -0.03700 | +0.10126 |
| IT2a | unset | yes | 8 | -0.06584 | -0.12175 |

The non-paragraph-start y enrichment and the differing A/B q directions remain
visible under the stricter selection. Paragraph-start y contrasts are negative
in both A and B in these split-policy results. Source-defined partition counts
differ even on the identical location list, so no label is transferred between
editions. Small unset cohorts remain descriptive.

The [complete report](conservative_prefixes.json) contains the selected keys and
digest, all excluded-key reasons, source-policy counts, source hashes, every
source/spacing/stratum/boundary result, controls, and shuffle contrasts. These
96 feature contrasts are dependent, exploratory, unadjusted for multiplicity,
and have a minimum Monte Carlo tail resolution of 0.005.

The [source-specific figures](figures/CONSERVATIVE_PREFIXES.md) display both
spacing policies, source partition sizes, observed contrasts, and conditional
shuffle reference ranges, with machine-readable plotted values and input digests.

## Reproduce and validate

Python 3.10 or later; standard library only. Recorded run: Python 3.14.3.

```sh
python3 scripts/conservative_prefixes.py --output research/transliteration/conservative_prefixes.json
python3 scripts/conservative_prefixes.py --check research/transliteration/conservative_prefixes.json
PYTHONPATH=tests python3 -m unittest test_conservative_prefixes test_prefix_strata test_locus_positions test_token_baselines test_ivtff test_source_audit -v
```

Tests verify that a failure in one source/policy removes the key from every
case; ambiguity and same-line failures remain explicit. Missing candidate
records, duplicate records/policies, source-hash drift, incompatible adapter
versions, inconsistent token counts, and non-plain eligible tokens fail the
selection gate. Existing controls and source/token tests remain in use.

## Limits and next test

Whole-locus exclusions can systematically change the represented sections,
hands, and text shapes. Clean ASCII notation is not evidence of correct glyph
identification or readability. Currier labels and paragraph marks remain source
annotations, and none of the source versions or treatments is an independent
replication.

The result constrains models that ignore the observed context-conditioned
structure. It establishes no language, phonetic mapping, cipher, plaintext, or
translation. Next, connect candidate-specific predictions to an independently
checked glyph-unit scheme and the separately validated split/leakage workflow,
with all prior exposure recorded.
