# First-slot prefixes across catalog sections

## Question and sources

Does the pooled first-slot q/y pattern persist across Yale's six catalog ranges,
after separating source-marked paragraph starts?

The [analysis choices](SECTION_STRATA_PLAN.md) were committed before this run at
`c9123ad`. This extends the [pooled position analysis](POSITION_EFFECTS.md) and
the [paragraph/Currier analysis](PREFIX_STRATA.md) using already exposed inputs.
It is an exploratory constraint on text-production explanations, not a frozen
candidate test, glyph adjudication, or decipherment.

Use the exact [ZL3b and IT2a pins](../../data/transliterations.json), the accepted
reader/tokenizer, and the paragraph analysis's joint locator restriction.
There are **3,848 shared regular P0 locations**, after removing 36 same-line
fragments from the 3,884 shared present P0 locations. Exact source hashes,
selection digest, excluded keys, and all results are in
[section_strata.json](section_strata.json).

[Yale's catalog, S002](https://pre1600ms.beinecke.library.yale.edu/docs/pre1600.ms408.HTM),
inspected 2026-10-11 (America/New_York), supplies the grouping:

| Catalog part | Numeric source folios | Selected loci in either source |
| --- | --- | ---: |
| I | 1–66 | 1,484 |
| II | 67–73 | 29 |
| III | 75–84 | 712 |
| IV | 85–86 | 128 |
| V | 87–102 | 416 |
| VI | 103–117 | 1,079 |
| Unassigned | Non-numeric, gap, or outside these ranges | 0 |

Classify the number in each exact source page name, preserving side and panel
suffix. The report records 202 distinct page names; they are neither 202 physical
leaves nor independent samples. This grouping does not assert each locus's
subject or verify a source-page-to-image-region alignment. Non-numeric `fRos`
stays unassigned if it enters a future selection. No legacy 117v alias is
inferred; the catalog/digital endpoint discrepancy remains unresolved.

## Method and comparability

Partition each catalog part separately within each source by the `<%>` mark
outside free comments. **29 selected locations have different paragraph-start
annotations between ZL and IT**; their keys are retained in the report. A source
comparison of a paragraph-specific cohort therefore need not compare identical
locations. Retention policies can further change eligibility. Neither source's
annotation is treated as ground truth. Catalog parts remain distinct from the
source `L`/Currier labels, whose eligible counts are also retained.

Run all four split/join and exclude/first-choice uncertainty treatments. Preserve
original token slots and require a retained original first token plus at least
one other retained token. Do not replace an excluded boundary with a later token.
Use literal case-sensitive `q` and `y` representation prefixes, preserving
ligatures and high-ASCII notation. These are not phonetic or validated glyph units.

For each eligible locus, subtract the mean prefix feature of its other retained
tokens from the first token's feature; average with equal weight per locus.
Reuse the accepted [conditional control](POSITION_EFFECTS.md): retained tokens
are exchangeable within their own locus under the null, with exact expectation
zero and exact conditional SD. Record 199 within-locus shuffle contrasts per
feature, seed 20261011. Their SD is a conditional randomization quantity, not
uncertainty from independent sampling of folios or sections.

All 224 declared source/policy/section/paragraph/feature cells remain in the
report. Of these, 32 are empty unassigned-group cells and 192 are estimable.
Two-sided tails are exploratory, dependent, unadjusted for multiple comparisons,
and have a minimum resolution of 0.005. Small cohorts remain descriptive; a
direction is not itself evidence against the conditional null or a difference
between sections. No between-section significance test is performed.

## Observations

Primary split/exclude first-slot differences, as fractions:

| Catalog part | Paragraph start | ZL eligible | IT eligible | ZL q | IT q | ZL y | IT y |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| I | no | 1,206 | 1,237 | +0.07281 | +0.07535 | +0.11803 | +0.11775 |
| I | yes | 225 | 234 | -0.06319 | -0.07005 | -0.04585 | -0.04678 |
| II | no | 22 | 22 | -0.07024 | -0.06998 | +0.11286 | +0.11071 |
| II | yes | 7 | 7 | -0.05284 | -0.05483 | -0.13660 | -0.13915 |
| III | no | 617 | 630 | +0.03592 | +0.03851 | +0.07588 | +0.07510 |
| III | yes | 80 | 82 | -0.15867 | -0.16424 | -0.01977 | -0.01583 |
| IV | no | 107 | 106 | -0.03846 | -0.04413 | +0.11010 | +0.11189 |
| IV | yes | 21 | 22 | -0.17493 | -0.17309 | -0.05651 | -0.04728 |
| V | no | 338 | 340 | -0.05000 | -0.04381 | +0.16886 | +0.17123 |
| V | yes | 69 | 74 | -0.11226 | -0.11618 | -0.02984 | -0.02782 |
| VI | no | 774 | 792 | -0.09931 | -0.10105 | +0.20569 | +0.20626 |
| VI | yes | 278 | 285 | -0.18949 | -0.19177 | +0.00068 | -0.00144 |

The non-paragraph-start y contrast is positive in all six parts under both
sources and all four policies, ranging from +0.07510 to +0.20688. Parts I–V have
negative paragraph-start y contrasts across these treatments. Part VI instead
has near-zero paragraph-start contrasts, ranging from -0.00144 to +0.00113,
with a sign disagreement between sources. Retain that disagreement; the pooled
negative paragraph-start result does not describe every section alike.

For non-paragraph-start loci, q contrasts are positive in I and III and negative
in II, IV, V, and VI across the declared treatments. All paragraph-start q
contrasts are negative. These patterns are compatible with several interacting
source, layout, and production differences. They do not establish a causal
section effect or identify a language, cipher, or meaning.

Part II has only 22 non-start and 7 paragraph-start eligible loci. For example,
its primary y shuffle tails are 0.085/0.060 at non-starts and 0.515/0.510 at
paragraph starts (ZL/IT). The complete report retains the other non-floor tails
and all null distributions. Broadly matching contrast signs must not be called
equally strong evidence across differently sized sections.

## Reproduce and validate

Python 3.10 or later; standard library only. The recorded run used Python 3.14.3.

```sh
python3 scripts/section_strata.py --output research/transliteration/section_strata.json
python3 scripts/section_strata.py --check research/transliteration/section_strata.json
python3 -m unittest discover -s tests
```

Check mode verifies source bytes and compares the complete report, including
all cohort metadata and shuffle sequences. Synthetic tests cover every range
endpoint, side/panel preservation, unassigned labels and gaps, source-specific
paragraph membership, the joint locator restriction, complete partitions,
empty cohorts, boundary exclusions, and rejection of duplicate transcriber
records that would otherwise gain extra locus weight. Shared tests check the
exact conditional variance against exhaustive small permutations.

## Limits and next test

These are source-assigned P0 loci, not reconstructed physical lines. Repeated
locations and panel views on a shared leaf remain dependent material. The same
public inputs and loci recur across earlier analyses; this contribution adds
a grouping check, not independent manuscript observations. No reserved
evaluation set, candidate decoding rule, plaintext, or translation is produced.

The [paragraph-agreement sensitivity check](SECTION_AGREEMENT.md) now reports
how excluding the 29 annotation disagreements changes the contrasts, while
retaining both sources and their uncertainty treatments. Image review is
needed to adjudicate paragraph boundaries and glyph-unit definitions. Any
candidate mechanism then needs additional frozen predictions and an evaluation
split with explicit prior exposure, rather than fitting a story to these tables.
