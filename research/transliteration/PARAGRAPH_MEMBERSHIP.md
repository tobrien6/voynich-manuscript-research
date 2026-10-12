# Encoded paragraph-unit agreement

## Question and method

Paragraph-level experiments require a declared grouping of loci. Do the pinned
ZL3b and IT2a files define the same complete encoded paragraph units, even where
individual locus identifiers agree?

The [plan](PARAGRAPH_MEMBERSHIP_PLAN.md) was committed before computing this
report, after earlier source-annotation and image work had exposed the corpus.
This is a descriptive metadata analysis. It supplies source-specific units and
an exact common membership cohort for later experiments, rather than fitting
a decoding rule or claiming unseen evaluation material.

Use the accepted IVTFF reader and hash-verified
[ZL3b/IT2a pins](../../data/transliterations.json). Select present generic P
loci, including every P subtype, in each source's encoded page and locus order.
Detect dedicated `<%>` and `<$>` marks outside free comments. No token text,
glyph readings, spacing policies, or alphabet conversions enter this audit.

The publisher's [IVTFF definition](https://voynich.nu/software/ivtt/IVTFF_format.pdf),
document issue 2.0.2 (2025-07-08), section 6.9 (printed page 26), requires
alternating start/end marks on the same page and assigns paragraph boundaries
to the transcriber. The audit checks that limited pairing/order rule, including
one-locus units. It withholds assignments for an entire anomalous page and
retains unmarked leading/trailing loci. It does not check marker placement
relative to glyphs or certify full IVTFF conformance.

The [complete report](paragraph_membership.json) records source hashes,
all encoded pages, units and ordered member keys, unit digests, anomalies and
unassigned material, excluded records and counterpart metadata, every shared
locus's membership category, and exact matching unit identifiers.
Source credits and edition history remain in the
[transcription source register](../transcriptions/SOURCES.md).

## Source units and pairing checks

| Measure | ZL3b | IT2a |
| --- | ---: | ---: |
| Encoded pages containing present generic P loci | 207 | 206 |
| Present generic P loci | 4,130 | 4,118 |
| Pages passing the declared marker-order check | 207 | 206 |
| Pages with no marks / anomalous order | 0 / 0 | 0 / 0 |
| Complete encoded paragraph units | 740 | 772 |
| Loci assigned to complete units | 4,117 | 4,118 |
| Present P loci left unassigned | 13 | 0 |

No present non-P locus carries a paragraph mark in either pinned source.
Passing this limited check does not prove complete annotation coverage:
ZL leaves `f68r1.5–7` and `f84v.42–51` outside complete marked units, while
IT assigns those 13 shared loci. The report preserves each key. No missing
boundary is synthesized and no source is preferred.

Encoded page counts are not physical-leaf counts. Foldout panels and `fRos`
retain native source conventions and their dependencies. No new image join
or foliation alias is established by this analysis.

## Exact cross-source membership

There are **4,118 shared present generic P locus keys**. Every key is accounted
for exactly once:

| Membership relation | Shared loci |
| --- | ---: |
| Same ordered unit members in both sources | 3,647 |
| Both grouped, with different ordered members | 458 |
| Grouped only in ZL | 0 |
| Grouped only in IT | 13 |
| Ungrouped in both | 0 |
| Ineligible because of anomalous page annotations | 0 |
| **Total** | **4,118** |

The complete units have **671 exact membership matches**, covering those
3,647 loci. ZL has 69 unmatched complete units; IT has 101. The common cohort
is defined by the entire ordered member-key tuple, not just a shared start
marker, end marker, page identifier, or paragraph number.

Among the 458 different memberships, four shared loci (`f106r.27`, `.28`,
`.30`, `.31`) belong to a unit containing ZL's `f106r.29`, which is outside
the shared generic-P intersection. The other 454 different memberships contain
only shared keys, so their difference concerns grouping of the available loci.
These categories describe source coverage and membership; they are not
manuscript annotation error rates.

## Two traceable examples

On **f9r**, both files group loci 1–5 together. ZL groups 6–10 as another unit;
IT instead groups 6–9 together and makes locus 10 a one-locus unit. The
[image pilot](PARAGRAPH_IMAGE_PILOT.md) retains the paragraph division as
unresolved. Here the shared first unit counts once, while all five members
of the later unit have different cross-source membership.

On **f26v**, ZL's marks enclose loci 1–9 as one unit. IT's marks divide them
into 1–2, 3–4, 5–6, and 7–9. All nine loci therefore have different membership,
although the source end markers differ at only three positions. This shows
why a boundary-disagreement count does not count all affected sampling rows.
The [residual image work](https://github.com/tobrien6/voynich-manuscript-research/pull/53)
leaves the visual divisions unresolved; the units here remain encoded source
annotations.

## Reproduce and validate

Python 3.10 or later; standard library only:

```sh
python3 scripts/paragraph_membership.py --output research/transliteration/paragraph_membership.json
python3 scripts/paragraph_membership.py --check research/transliteration/paragraph_membership.json
PYTHONPATH=tests python3 -m unittest test_paragraph_membership -v
```

Synthetic tests cover all P subtypes, intervening non-P records, one-locus
units, page resets, repeated/orphan/dangling/reversed markers, withholding an
entire anomalous page, free comments, nonexistent records, leading/trailing
unmarked loci, grouping splits, coverage differences, and non-P markers.
Output guards protect raw inputs, the source catalog, source scripts, and the
pre-execution plan, including resolved aliases. Pinned integration checks
reproduce the complete report, retain the explicit ZL/IT pair when catalog
order changes, and account for every shared key and every source P locus.

## Limits and next test

These units follow source annotations and locus alignment, rather than
independently verified physical paragraphs. The same ordered members can have
different native text or tokenization; membership agreement does not establish
glyph or reading agreement. Adjacent units, shared panels, and the two related
source editions remain dependent observations.

A later paragraph-level statistic should either use the 671 explicitly matched
units or report separate source groupings and all cohort exclusions. It still
needs a declared token/glyph representation, appropriate controls, input pins,
and exposure history. Image and glyph-level review must separately adjudicate
any proposed source correction. This audit supplies reproducible grouping
denominators and makes no language, decoding, or translation claim.
