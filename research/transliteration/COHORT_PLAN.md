# Exploratory fixed-cohort transcription comparison

Recorded before computing this comparison on already exposed public data.
This extends POSITION_PLAN.md; it is not a held-out evaluation or an
independent preregistration.

Question: how do the existing locus-position contrasts change when every
transcription/uncertainty variant is evaluated on exactly the same locus keys?

Fixed choices:

- Use only the pinned ZL3b and IT2a sources and their shared present P0 keys.
  Reject duplicate selected keys rather than silently selecting a transcriber.
- Reuse the accepted tokenizer, retention policies, feature definitions and
  original boundary-slot eligibility from scripts/locus_positions.py.
- Prepare all eight source × split/join × exclude/first variants. For first
  and last boundaries separately, intersect their eligible key sets. Do not
  require a locus to qualify at both boundaries.
- For each feature and variant, report the equal-locus-weight contrast on its
  own eligible set and on the common set. Report the common-minus-own shift.
- On the common set, pair each variant's per-locus contrast with the primary
  ZL3b split/exclude contrast. Report the mean signed and absolute differences
  and the number of differing loci. Treat differences below 1e-12 as numeric
  ties only for the differing-locus count.
- Record source hashes, selection/cohort digests, ineligible keys by variant,
  and common-cohort locator counts. Use null statistics for an empty cohort.
- Report all three features and both boundaries. No new shuffle significance
  test is needed: this is a descriptive sensitivity comparison, not a test of
  independent edition samples or a causal decomposition of source differences.

The fixed locus keys do not fix retained tokens, segmentation, notation,
paragraph marks or locator annotations. They do not establish physical-line
alignment. Prior exposure includes the complete coverage, repetition and
position reports. No candidate decoding rule is fitted or evaluated.
