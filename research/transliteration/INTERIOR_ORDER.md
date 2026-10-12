# Exploratory interior notation-length order

The 2,165 common eligible P0 loci show **greater adjacent interior notation-length
association than an endpoint-fixed permutation control** in each ZL3b/IT2a and
split/join treatment. This is a representation-level constraint for future
text-generation hypotheses, not a reading or translation of the manuscript.
The uncentered statistic is negative in every treatment; the effect is its
departure above a more negative conditional expectation.

## Question, chronology, and method

The [analysis plan](INTERIOR_ORDER_PLAN.md) was committed at
`655e286d2f7f1d253cf18e879dc529a30a06371f` before manuscript execution.
Its source selection, cohort, endpoint handling, statistic, seed, 999-trial
range, two-sided tail, and decision convention were retained unchanged.
The earlier full-corpus coverage, repetition, and position reports had been
inspected. This is an exploratory analysis with recorded choices, not an
untouched evaluation or a registered decoding candidate.

Inputs are the CC0-published ZL3b and IT2a native Eva sources pinned in
[the source catalog](../../data/transliterations.json). The
[conservative adapter](TOKEN_ADAPTER.md) excludes entire ambiguous, unreadable,
extended, or malformed loci. Both treatments of uncertain spaces are retained;
no preferred ambiguous reading is selected. Length means the number of native
ASCII Eva letters, not manuscript glyphs, phonemes, or decoded characters.

The statistic uses only the interior tokens of a locus with at least five
tokens; neither endpoint participates in an adjacent pair. A control permutes
only the interior lengths, preserving their multiset and leaving endpoints
fixed. It moves nothing across loci, pages, or folio sides. The centered
association `C` subtracts the exact without-replacement expectation of the
normalized adjacent-product statistic `R`. The plan gives the formula and
its derivation. Average `C` with equal locus weight, retaining constant
interiors as zero contributions.

## Cohort and observations

| Selection stage, applied jointly to all four treatments | Loci |
| --- | ---: |
| Shared present P0 identities | 3,884 |
| Eligible under all conservative adapter treatments | 2,940 |
| Also free of drawing interruptions in every treatment | 2,505 |
| Also at least five tokens in every treatment | **2,165** |

The retained identities span 176 transcription page IDs, with inherited
source Currier metadata A for 549 loci, B for 1,598, and unset for 18.
These are source annotations, not inferred languages or independently checked
physical-page units. A P0 locus can differ from a physical line. The
[complete report](interior_length_order.json) lists every retained key, all
1,719 excluded keys with reasons, source and cohort hashes, and descriptive
per-page statistics. Exclusion reasons can overlap; stage counts partition
successive selection losses.

| Treatment | Interior tokens / adjacent pairs | Mean `R` | Exact null mean `R` | Mean `C` | Monte Carlo two-sided tail |
| --- | ---: | ---: | ---: | ---: | ---: |
| ZL3b split, primary | 15,878 / 13,713 | -0.100892 | -0.189954 | **0.089062** | 0.001 |
| ZL3b join | 14,437 / 12,272 | -0.156255 | -0.212929 | **0.056674** | 0.001 |
| IT2a split | 15,558 / 13,393 | -0.114311 | -0.193425 | **0.079114** | 0.001 |
| IT2a join | 15,558 / 13,393 | -0.114311 | -0.193425 | **0.079114** | 0.001 |

All 999 controls have smaller absolute centered statistics in each treatment.
The reported tail includes the observed ordering and has resolution 1/1,000;
it does not measure the exact tail below that resolution. The primary
treatment meets the plan's exploratory 0.01 convention, and the direction
persists across the paired sensitivity treatments. Joining uncertain spaces
reduces the centered effect by about 36%; preprocessing therefore matters even
when the direction survives. IT has no uncertain-space markers, so its two
numerical corpora and complete control arrays coincide and supply one
comparison, not two replications.

There are 13 constant interiors in each ZL treatment and 14 in each IT
treatment, retained in the 2,165-locus denominator. The report retains all
999 control statistics, their means and standard deviations, exact conditional
expectations, and cohort metadata. No page subset was selected after viewing
its result.

## Reproduce and validate

From the repository root, using Python's standard library:

```sh
python3 -m unittest discover -s tests -p 'test_interior_length_order.py' -v
python3 scripts/interior_length_order.py --check research/transliteration/interior_length_order.json
```

The full replay takes several minutes. Source hashes are checked by the
accepted reader. The draw stream reuses the
[versioned SHA-256 control algorithm](../token-controls/README.md), with the
length-corpus digest, scope, seed, trial, and locus identity specified in the
plan. Exhaustive synthetic permutations verify the exact centered expectation
for distinct, repeated, and constant lengths. Additional tests check equal
locus weight, endpoint isolation, common eligibility, multiset preservation,
unchanged inputs, deterministic controls, and all-trial tail accounting.

## Limits and next test

The result rejects only the stated exchangeability control on this selected
representation cohort. It does not distinguish neighboring-token dependence
from an interior position gradient, paragraph context, copying patterns,
transcription conventions, or clear-locus selection. Fixed endpoints remove
their direct contribution, but do not account for all interior position effects.
ZL/IT are paired representations with shared history, not independent
manuscript samples. Full-corpus prior exposure prevents a claim of unseen data.

A next experiment should specify a positional model before execution and
compare residual adjacency with controls that preserve the relevant interior
position profile. Later linguistic or cipher mechanisms also need documented
language and synthetic-encoding comparisons, an honest split, explicit rules,
and prospective evaluation under the
[decipherment protocol](../DECIPHERMENT_PROTOCOL.md). No glyph adjudication,
decipherment, or proposed English passage follows from this analysis.
