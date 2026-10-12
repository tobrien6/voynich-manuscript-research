# Paragraph annotation differences across generic P loci

## Question and fixed scope

The [P0 audit](ANNOTATION_AGREEMENT.md) compares regular paragraph-text loci.
The [three-page image pilot](https://github.com/tobrien6/voynich-manuscript-research/pull/40)
showed why neighbouring P subtypes matter: an end-mark disagreement can precede
a centred line that the two sources group differently. How much annotation
context is outside P0, and how often does that specific encoded pattern occur?

The [plan](GENERIC_P_CONTEXT_PLAN.md) was committed before execution, after
the P0 audit and the three selected images were inspected. This is an exploratory
source-metadata follow-up. It does not provide new independent observations of
the manuscript or identify the intended paragraph divisions.

Use the hash-verified [ZL3b and IT2a files](../../data/transliterations.json),
the accepted IVTFF reader, and the P0 audit's annotation helper. Select shared
present loci with generic type P in both sources, including all subtypes.
Match by page name and locus number, without tokenizing or altering glyphs.
The [complete report](generic_p_context.json) preserves all exclusions,
zero cells, subtype pairs, source identities, and discordant records.

## Coverage and observations

ZL contains 4,130 present generic P loci; IT contains 4,118. All IT generic P keys
are shared. ZL's 12 excluded keys comprise `f106r.29` and 11 `fRos` loci; all are
listed in the report. The shared cohort contains **4,118 loci** with identical
subtypes, effective Currier labels, and locators in both sources.

| Shared subtype | Shared loci | Start-mark disagreements | End-mark disagreements |
| --- | ---: | ---: | ---: |
| P0 | 3,884 | 29 | 54 |
| P1 | 72 | 2 | 1 |
| Pb | 123 | 4 | 5 |
| Pc | 17 | 16 | 0 |
| Pr | 12 | 9 | 0 |
| Pt | 10 | 0 | 0 |
| **All generic P** | **4,118** | **60** | **60** |

Start/end disagreement sets overlap at one locus, giving **119 distinct
discordant loci**. The P0 audit contains 82 of these; this extension records
the 37 additional loci outside P0. Equal total counts of start/end differences
do not establish valid paragraph pairing or equal paragraph membership.

The publisher's [IVTFF definition](https://voynich.nu/software/ivtt/IVTFF_format.pdf),
Table 9 and section 6.9, defines P subtypes and source paragraph markers. The
observed subtype labels and marker counts are file metadata, not independent
visual verification. Source credit and edition history remain in the
[source register](../transcriptions/SOURCES.md).

## Immediate centred-line context

For each of the **54 shared P0 end-mark disagreements**, inspect only the next
present generic P locus on the same page in each source. Preserve null at page
end. Do not search further to find a preferred explanation.

The declared pattern requires the same next key, Pc in both sources, one end
mark in both next loci, and a start mark there only in the source that also
ends the preceding P0 locus. This describes one source making the centred line
a separate one-locus paragraph while the other retains it in the preceding
paragraph.

**16 of 54 cases** meet this exact context rule, all with the centred line
separate in IT2a. Zero meet the directional reverse with it separate in ZL3b.
The **38 other cases** remain individually listed with their next source
contexts. These counts account for every P0 end disagreement without inferring
an unmarked boundary or collapsing the residual cases into the centred-line
pattern.

The three image-pilot cases fall within those 16 metadata cases. The pilot's
paragraph divisions remain unresolved. The wider count is a file observation;
the other images have not been reviewed here, and a next encoded P locus need
not be the next physical line.

## Reproduce and validate

Python 3.10 or later; standard library only:

```sh
python3 scripts/paragraph_context_audit.py --output research/transliteration/generic_p_context.json
python3 scripts/paragraph_context_audit.py --check research/transliteration/generic_p_context.json
PYTHONPATH=tests python3 -m unittest test_paragraph_context_audit -v
```

Tests cover both marker-pattern directions, changed next identifiers and
subtypes, marker multiplicity, page-end nulls, refusal to skip an intervening
P locus, explicit subtype changes and intersection exclusions, and exact
report reproduction from the pinned pair as the source catalog grows.
The audit preserves source identifiers and physical file line numbers and
does not redistribute token text or images.

## Limits and next test

Source-order relationships inherit the publisher's locus alignment. The audit
does not validate complete IVTFF paragraph conformance, reconstruct paragraph
intervals, verify physical line associations, or prefer one source's grouping.
Other P0 end disagreements and all differences in P1, Pb, Pc, and Pr need their
own source-linked review.

A later analysis using paragraph boundaries should declare its eligible
subtypes and boundary convention and disclose which choices affect its cohort.
Image review needs an explicit paragraph definition and glyph-level alignment.
These exposed metadata results must remain separate from an untouched
decipherment evaluation or a translation claim.

The [residual image pilot](RESIDUAL_PARAGRAPH_IMAGE_PILOT.md) inspects every
residual end disagreement on the first three selected pages: 19v, 24v, and
26v. It distinguishes a right-aligned terminal-row context from divisions
within ordinary P0 text and keeps all five boundaries unresolved.
