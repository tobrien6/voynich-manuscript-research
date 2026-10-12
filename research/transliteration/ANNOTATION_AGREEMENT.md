# Paragraph-annotation agreement between ZL3b and IT2a

## Question and method

Source-marked paragraph boundaries define groups in positional analyses.
Are those groups the same in the pinned transcriptions?

The [audit plan](ANNOTATION_AGREEMENT_PLAN.md) was committed before execution.
This is a descriptive comparison of exposed public data, with no tokenization,
decoding, or held-out evaluation. The script reuses the accepted IVTFF reader,
hash-verified [source catalog](../../data/transliterations.json), and explicit
ZL3b/IT2a source selection. Source credits and edition history remain in the
[transcription decision](DECISION.md) and [source register](../transcriptions/SOURCES.md).

Match present P0 records by page name and locus number. Detect literal `<%>`
and `<$>` outside free comments; compare their presence, their counts, effective
`L` metadata, and locators. Effective metadata includes inherited text tags.
Missing `L` remains JSON null. No disagreement is resolved automatically.

The publisher's [IVTFF definition](https://voynich.nu/software/ivtt/IVTFF_format.pdf),
document issue 2.0.2 (2025-07-08), section 6.9 (printed page 26), defines paragraph
start/end marks and explicitly assigns paragraph divisions to the transcriber.
Section 6.8 defines text-tag inheritance; Tables 6 and 8 define `L` and locators.
Agreement here measures matching annotations, not independently verified layout.

## Cohort and observations

ZL3b has 3,885 present P0 loci and IT2a has 3,884. Their intersection has
**3,884**; ZL's `f106r.29` is excluded because it is not present as P0 in IT.
Requiring locators `@`, `+`, or `*` in both sources removes 36 shared same-line
fragments and leaves **3,848** loci. The excluded keys and both cohort digests
are recorded in [annotation_agreement.json](annotation_agreement.json).

Paragraph-mark presence in the **3,848 regular shared P0 loci**:

| ZL3b annotation | IT2a annotation | Start-mark loci | End-mark loci |
| --- | --- | ---: | ---: |
| absent | absent | 3,131 | 3,146 |
| absent | present | 19 | 44 |
| present | absent | 10 | 10 |
| present | present | 688 | 648 |
| **Disagreements** | | **29 / 3,848** | **54 / 3,848** |

All 29 start-mark disagreements and all 54 end-mark disagreements are also in
the full 3,884-locus cohort. The locator restriction removes no discordant locus.
The start and end disagreement sets overlap at one locus, so **82 distinct
loci** differ on at least one field. Neither source repeats a start or end mark
within a selected locus.

The effective `L` labels agree for every selected locus. In the regular cohort,
there are 1,497 matching A labels, 2,316 matching B labels, and 35 pairs with the
label absent in both sources. All locators also agree: 224 `@`, 3,606 `+`, and
18 `*` in the regular cohort. Matching labels can share inherited conventions;
they do not constitute independent evidence of underlying natural languages.

The JSON retains complete categorical tables, including zero cells, source
hashes and paths, denominators, all exclusions, and every discordant locus with
both source identifiers and physical file line numbers. It contains no token
payload and makes no choice of a preferred annotation.

## Consequence for positional comparisons

Using each source's own paragraph marks partitions some matched loci differently.
A difference between source-specific paragraph strata therefore need not arise
solely from different glyph readings or spacing. This audit identifies the
annotation component; it does not measure its effect on a token statistic.

P0 is a locus subtype, not the entire population of paragraph text. Paragraph
endings can occur in other P subtypes, including centred, right-aligned, or title
loci. The unequal start/end totals within this P0 subset do not demonstrate
unbalanced paragraphs or format errors. This audit does not reconstruct
paragraph intervals, certify marker placement, or identify physical lines.

## Reproduce and validate

Python 3.10 or later; standard library only. The run uses the committed source
files and verifies their exact hashes before analysis.

```sh
python3 scripts/annotation_agreement.py --output research/transliteration/annotation_agreement.json
python3 scripts/annotation_agreement.py --check research/transliteration/annotation_agreement.json
PYTHONPATH=tests python3 -m unittest test_annotation_agreement -v
```

Synthetic tests exercise directional disagreement tables, zero cells, marker
exclusion inside free comments, repeated markers, metadata inheritance and page
resets, absent and unexpected labels, joint source selection, explicit missing
and nonexistent-locus exclusions, duplicate-key rejection, and an empty regular
cohort. The pinned-data test reproduces the full committed audit and confirms
that unrelated source editions do not change it.

## Limits and next test

Matching locus keys inherit the publisher's alignment conventions; their text
regions have not been independently checked against all images. Mark absence
is a source observation, not a verified claim that a boundary is absent.
Counts describe these two exact editions and this declared subset; they are
not manuscript-wide error rates or independent replications.

Review the 82 discordant loci against source images, using the repository's
folio mapping and preserving unresolved foldouts. Record adjudications
separately with evidence. A later positional sensitivity test can compare
source-specific strata with a declared common annotation cohort. Neither step
should relabel the already explored corpus as previously unseen material.

The [generic-P context extension](GENERIC_P_CONTEXT.md) includes neighbouring
paragraph subtypes and records all source-marker disagreements outside P0.
Its exact centred-line pattern covers 16 of the 54 P0 end disagreements;
the 38 remaining contexts are retained separately.
