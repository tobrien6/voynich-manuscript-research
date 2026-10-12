# Generic-P annotation context audit plan

## Question and exposure

The three-page image pilot in PR #40 found that each selected P0 end-mark
disagreement precedes a Pc locus marked as a separate paragraph only in IT.
How many paired annotation differences are outside P0, and how many of the 54
P0 end-mark disagreements have this same encoded context?

Commit these choices before running the broader audit. The P0 audit and the
three selected images have already been inspected; this is an exploratory
metadata follow-up motivated by those observations. It is not an independent
replication or a held-out experiment.

## Fixed choices

- Use exactly the pinned ZL3b/IT2a pair, hash-verified by the accepted loader.
  Use the shared IVTFF reader and the annotation helper from PR #34.
- Select the intersection of present loci whose generic type is P in both
  sources, matching page and locus number. Retain differing P subtypes and
  report their pairs. Publish per-source counts, intersection exclusions, and
  the sorted selection digest.
- Report the same start/end mark, effective Currier-label, and locator tables
  as the P0 audit, with zero Boolean cells retained. Publish every discordant
  locus, including those differing only in subtype or marker multiplicity.
- For each shared P0 end-mark disagreement, record the next present generic-P
  locus on the same page in each source, or explicit null at page end. Do not
  search beyond that next locus to find a matching pattern.
- Count the centred-line context only when the next key is identical in both
  sources, both next subtypes are Pc, both next loci have one end mark, and
  the source with one end mark on the current P0 locus has one start mark on
  the Pc locus while the other has neither of those marks. Count both
  directional versions of the pattern and report all other cases separately.
- Preserve source identifiers and physical file line numbers, and separate
  missing records or changed subtypes from paragraph-mark differences.
  No source marks are inferred or changed. Do not reconstruct paragraphs,
  validate marker-pair conformance, assign glyph readings, or select a preferred
  paragraph convention.

## Interpretation and next step

The next encoded generic-P locus is a source-order relation, not proof of an
adjacent physical line. The centred-line pattern describes annotations, not a
manuscript-wide visual result. Use the publisher's IVTFF Table 9 and section
6.9 for subtype/marker semantics and retain the original source credits.
Only later image review and an explicit paragraph definition can adjudicate
grouping. Every subgroup and residual case must remain visible.

Continue within the verified `tobrien6` owner/maintainer contribution scope,
using this isolated checkout and a linked topic PR. The existing maintainer
workflow handles merge decisions. This contribution depends on PR #34's helper
and does not modify the P0 report or the image pilot.
