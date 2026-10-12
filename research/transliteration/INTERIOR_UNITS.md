# Interior-order departure persists under the declared count policies

All three operational EVA count policies retain a positive centered interior-
order departure under both control scopes, in every source/spacing treatment.
Each of the **24** observed effects exceeds all 999 controls in absolute value,
giving the retained Monte Carlo tail **0.001**, its resolution floor. Grouping
listed bench sequences decreases the effect; adding the listed minim sequences
gives values near the original ASCII result. The latter paired changes have
nonsmall tails. This preserves a representation constraint while exposing
measurement sensitivity; it does not adjudicate glyphs or identify a mechanism.

## Frozen method, sources and exposure

The [plan](INTERIOR_UNITS_PLAN.md) was published at `e49f81f`, followed by the
synthetic-tested implementation at
**`b614b6ef71db0b118c09c1c2b9dcfe68f7628fe7`**. Both remote heads were verified
before applying grouped policies to the manuscript or generating these controls.
The generator, source/cohort, maps, seeds, trials and scoring rules were retained
unchanged after inspecting results.

Reuse the exact **2,165 common P0 loci** from the accepted
[unrestricted](INTERIOR_ORDER.md) and [half-control](INTERIOR_HALVES.md) studies.
There are 176 transcription page identifiers, with 15,878 interior tokens for
ZL split, 14,437 for ZL join and 15,558 for either IT spacing treatment. These
are source-record counts, not physical manuscript lines or independently
adjudicated glyph/token boundaries. The conservative source/spacing intersection,
drawing exclusion, five-token minimum and every original exclusion remain fixed.
No row is dropped because grouping makes its values constant.

The three [accepted counting policies](../baselines/EVA_UNIT_PROTOCOL.md)
preserve native case and original token boundaries. They count ASCII letters,
listed bench segments, or listed bench plus minim segments with exact longest-
match precedence and single-letter fallback. Their finite lists remain analyst
definitions. The [alphabet reference](https://voynich.nu/hist/gabriel/eva2_reference.pdf)
was checked visually on pages 4 and 6–7, and its 170,416-byte PDF matches the
accepted `2f9a9c7e...` hash. Its notation examples motivate the policies without
settling a physical glyph inventory. No PDF or image copy is published here.

Use identical original token-index permutations in every count policy. Draw
keys retain the original ASCII vector digest, seed 20261011 and trials 0–998;
the grouped vector hashes identify values without changing the random stream.
Endpoints remain outside the statistic and permutations. Half controls preserve
the original early/late slot split and each half's entire mapped count multiset.
The crossing interior pair remains included. Every locus receives equal weight.
Each policy has its own exact centering and constant-zero convention.

The whole corpus, earlier effects and accepted maps were already exposed.
This is post-result sensitivity with paired conditional controls, not an
untouched evaluation, registered decipherment candidate or fitted explanation.
IT split/join vectors, audits and controls are identical and dependent.

## Complete effect comparison

Numbers are mean centered normalized associations under the named count policy,
not lengths in a common physical glyph unit. The raw association is centered on
the relevant exact permutation expectation; a positive departure is relative
to that expectation.

| Source / spacing | ASCII, unrestricted | Bench, unrestricted | Bench/minim, unrestricted |
| --- | ---: | ---: | ---: |
| ZL3b split, primary | +0.089062 | +0.063341 | +0.092942 |
| ZL3b join | +0.056674 | +0.033079 | +0.062152 |
| IT2a split | +0.079114 | +0.049213 | +0.084558 |
| IT2a join | +0.079114 | +0.049213 | +0.084558 |

| Source / spacing | ASCII, half controls | Bench, half controls | Bench/minim, half controls |
| --- | ---: | ---: | ---: |
| ZL3b split, primary | +0.067330 | +0.046359 | +0.065453 |
| ZL3b join | +0.044792 | +0.026490 | +0.044915 |
| IT2a split | +0.062378 | +0.037249 | +0.060643 |
| IT2a join | +0.062378 | +0.037249 | +0.060643 |

All 24 tails are 0.001 from 0/999 exceedances. This is an exposed-data
conditional comparison with a finite resolution; it is neither a zero p-value
nor calibrated decipherment confidence or family-level significance.

## Paired policy changes and constant cases

The primary treatment's changes use the same token-index order in each trial:

| Change from ASCII | Unrestricted change | Its paired tail | Half-centered change | Its paired tail |
| --- | ---: | ---: | ---: | ---: |
| Bench | -0.025721 | 0.001 | -0.020971 | 0.001 |
| Bench/minim | +0.003880 | 0.525 | -0.001877 | 0.702 |

Bench changes are negative in every treatment under both scopes, with paired
tails 0.001. Bench/minim unrestricted changes are positive in every treatment;
their paired tails are 0.525 for ZL split, 0.396 for ZL join and 0.390 for
either IT treatment. Half-centered bench/minim changes are negative for ZL
split and IT, but **positive +0.000123 for ZL join**, with tails 0.702, 0.735
and 0.981 respectively. Keep that sign exception and the nonsmall comparisons.
These outcomes do not establish equivalence or select a preferred unit map.
All 16 complete paired-difference arrays remain in the report.

Grouping can make formerly variable counts constant, and can distinguish tokens
with equal ASCII lengths. For primary bench counts, 11 loci become constant
while 10 formerly constant loci become variable, yielding 14 constants instead
of 13. Bench/minim counts have 17 newly constant and nine formerly constant
cases becoming variable, yielding 21 constants. These status changes affect
the representation's statistic, with all loci retained at their original weight.

Entries below give **constant interiors / exact half-invariant interiors**:

| Source / spacing | ASCII | Bench | Bench/minim |
| --- | ---: | ---: | ---: |
| ZL3b split | 13 / 55 | 14 / 63 | 21 / 66 |
| ZL3b join | 13 / 73 | 19 / 80 | 28 / 88 |
| IT2a split | 14 / 58 | 16 / 72 | 21 / 71 |
| IT2a join | 14 / 58 | 16 / 72 | 21 / 71 |

The accepted exact invariance classifier also retains the narrower both-halves-
constant count and every invariant identifier. Newly constant identifiers,
pattern hits, uppercase fallback and unlisted-example substring occurrences are
reported for selected interior tokens only. These audits preserve incomplete
map scope and partial matches; no unlisted form is added after seeing results.

## Reproduction and verification

[interior_unit_controls.json](interior_unit_controls.json) retains all 24
effects/expectations/control arrays, all 16 paired arrays, every per-page
description, exact mean half-expectation fractions, source/software/settings
pins, vector/cohort hashes, invariant identifiers and mapping audits.
Every original ASCII observed value, moment, denominator and all 999 draws
under each scope reproduces the accepted parent reports exactly.

```sh
python3 -m unittest tests.test_interior_unit_controls -v
python3 scripts/interior_unit_controls.py --check research/transliteration/interior_unit_controls.json
```

Twelve synthetic tests passed before execution. After observing the status
accounting, a thirteenth regression explicitly checked the reverse transition
from ASCII-constant to grouped-variable without changing the implementation
or experiment. Tests cover known segment counts and case/fallback, source
reconstruction and boundaries, shared index permutations and half multisets,
exhaustive rational centering, both constant transitions, unchanged denominators,
parent reproduction, paired changes, rejected pins/slots/seeds and direct,
symbolic, hardlink and during-calculation output aliases.

An independent left-to-right scanner reconstructed every one of the twelve
count-vector digests. Separate rational deviation and expectation calculations
verified all observed effects and expectations. An independent SHA-256 rejection
sampler, Fisher-Yates implementation and rational scorer checked 72 scalar
controls at trials 0, 31 and 998, and all 48 corresponding paired differences.
Those calculations reuse only source parsing/cohort selection, not production
segmentation, scoring, expectation or control functions. The complete report
also replays from the exact pinned inputs and recorded Python environment.

## Limits and next test

The sign of this interior-order constraint persists under these finite maps,
while magnitude and constant/invariant sets change. It is not solely an
ASCII-letter count result, and it is still a representation-level observation.
Grouping does not adjudicate glyphs; a nonsmall paired change is not proof of
equivalence. Normalization changes with each count vector, so differences are
not a causal fraction explained or a physical length change in one shared unit.

The conservative selection, source conventions, unreviewed line/region links,
finer positional profiles, copying and prior exposure remain limitations. The
controls preserve particular bags and halves rather than modeling manuscript
production. Future mechanisms need explicit comparable representations, suitable
language or synthetic controls and prospective predictions before readings or
translations are evaluated under the decipherment protocol.
