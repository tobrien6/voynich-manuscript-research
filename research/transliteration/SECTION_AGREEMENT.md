# Catalog-section prefixes on agreed paragraph-start cohorts

## Question and declared sensitivity

How much does excluding source paragraph-start disagreements change the
[catalog-section first-slot contrasts](SECTION_STRATA.md)?

The [plan](SECTION_AGREEMENT_PLAN.md) was committed before execution at `fdce37d`.
The same public inputs and earlier results are already exposed. This is a
descriptive robustness check, not independent manuscript replication or a
held-out decipherment test. It complements the [paragraph-annotation audit,
PR #34](https://github.com/tobrien6/voynich-manuscript-research/pull/34), which
compares annotations without estimating token effects.

The script first recomputes and verifies the **complete unfiltered section
report**, then pins its byte digest in [section_agreement.json](section_agreement.json).
It reuses the accepted source reader, explicit ZL3b/IT2a pair, shared regular P0
selection, tokenizer, catalog grouping, paragraph detection, and conditional
position routines. Refactoring the shared section summarizer leaves the
unfiltered report unchanged.

Remove each of the **29 paragraph-start disagreements from both sources**.
This leaves **3,819 of 3,848** selected locations. Exact excluded keys and both
source start annotations, source hashes, and selection digests remain in the
report. Comment-only marks do not define starts. End-mark-only disagreements
remain eligible because this test concerns first slots and start membership,
not complete paragraph reconstruction. Neither source is chosen as ground truth.

Within each source, retain all four uncertainty policies, all six numeric catalog
parts plus unassigned, and both paragraph states. The agreed annotation cohorts
now contain matching selected locations. Token-level exclusions can still yield
different eligible sets across sources and policies; **eligibility is not fixed**.
No image boundary is adjudicated and no folio alias is inferred.

## Statistic and controls

For each retained eligible locus, measure the first-slot literal q/y feature
minus the mean feature of its other retained tokens, with equal locus weight.
Keep original boundary slots and their exclusions. These features concern EVA
representations, not phonetic or independently validated manuscript glyphs.

Publish before/after effects and their differences, selected and eligible counts,
removed counts, exact conditional null expectation/SD, and all 199 within-locus
shuffle contrasts, seed 20261011. Differences are computed from the report's
eight-decimal effects and rounded to eight decimals. Every declared cell remains
visible, including empty groups; no new between-section/source significance
test is performed. The controls are conditional on each retained token bag,
dependent, exploratory, coarse, and unadjusted for multiple comparisons.

## Observations

Primary split/exclude changes, **after minus before**, in rate units:

| Part | Paragraph start | ZL eligible before → after | IT eligible before → after | ZL q change | IT q change | ZL y change | IT y change |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| I | no | 1,206 → 1,200 | 1,237 → 1,236 | +0.00092 | +0.00029 | +0.00002 | +0.00010 |
| I | yes | 225 → 224 | 234 → 228 | +0.00099 | +0.00196 | -0.00020 | -0.00424 |
| II | no | 22 → 22 | 22 → 22 | +0.00000 | +0.00000 | +0.00000 | +0.00000 |
| II | yes | 7 → 7 | 7 → 7 | +0.00000 | +0.00000 | +0.00000 | +0.00000 |
| III | no | 617 → 615 | 630 → 628 | +0.00120 | -0.00041 | +0.00025 | +0.00037 |
| III | yes | 80 → 78 | 82 → 80 | -0.00749 | +0.00423 | +0.00056 | -0.00040 |
| IV | no | 107 → 106 | 106 → 106 | -0.00036 | +0.00000 | +0.00104 | +0.00000 |
| IV | yes | 21 → 21 | 22 → 21 | +0.00000 | -0.00824 | +0.00000 | -0.00225 |
| V | no | 338 → 335 | 340 → 340 | +0.00096 | +0.00000 | +0.00151 | +0.00000 |
| V | yes | 69 → 69 | 74 → 71 | +0.00000 | +0.00104 | +0.00000 | -0.00118 |
| VI | no | 774 → 768 | 792 → 785 | +0.00151 | +0.00127 | +0.00161 | +0.00088 |
| VI | yes | 278 → 271 | 285 → 278 | +0.00116 | +0.00135 | -0.00321 | +0.00029 |

The largest absolute change across all 192 estimable declared cells is
**0.00824260** (0.82426 percentage points), for the IT Part IV paragraph-start q
contrast under all four equivalent IT treatments. That cohort loses one of its
22 eligible loci. The complete report retains all 224 declared cells, including
32 empty unassigned-group cells.

The positive non-paragraph-start y contrasts persist in all six parts and all
declared treatments. The non-start q contrasts remain positive in I/III and
negative in the other parts, and every paragraph-start q contrast remains
negative. Part II loses no records, so its small-cohort results remain unchanged.

The only numerical sign changes occur in Part VI's ZL paragraph-start y contrasts,
under all four treatments. The primary value changes from +0.00067972 to
-0.00253151; IT changes from -0.00144072 to -0.00114999. All filtered Part VI
paragraph-start y effects range from -0.00256384 to -0.00114999. These small
negative values do not establish a stable enrichment/depletion mechanism:
the primary conditional null SDs are 0.00817730 and 0.00766909, with exploratory
shuffle tails 0.670 and 0.895 for ZL and IT. Retain the sign sensitivity without
treating a near-zero sign as a substantive decoding result.

## Reproduce and validate

Python 3.10 or later; standard library only. Recorded run: Python 3.14.3.

```sh
python3 scripts/section_agreement.py --output research/transliteration/section_agreement.json
python3 scripts/section_agreement.py --check research/transliteration/section_agreement.json
python3 -m unittest discover -s tests
```

Check mode verifies source bytes, the full section baseline, its digest, and the
complete sensitivity report. Synthetic tests cover paired exclusion and exact
effect changes, comment/end-mark-only differences, continued token-eligibility
differences, complete exclusion with undefined effects, and stale-baseline
rejection. Existing section tests cover ranges, unresolved labels, partitions,
and duplicate source records. Shared position tests validate the exact variance
against exhaustive small permutations.

## Limits and next test

This estimates the impact of a declared exclusion on these measurements, not
an annotation error rate. Agreement is not correctness; discordant material may
have different text/layout, and removing it may change the sample systematically.
Shared folios and panels remain dependent, and P0 loci remain source-assigned
units rather than reconstructed physical lines. Matching start membership does
not resolve paragraph ends, token segmentation, or manuscript image alignment.

Independent image review of discordant boundaries should record adjudications
separately, preserving both source annotations. A later candidate needs a frozen
unit definition, exposure-aware evaluation split, additional predictions, and
reported failures. This check supplies no plaintext, language identification,
translation, or validated decipherment.
