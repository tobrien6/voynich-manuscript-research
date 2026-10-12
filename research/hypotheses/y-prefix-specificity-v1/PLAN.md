# Prefix-specificity and vocabulary-opportunity controls v1

## Question and scope

The [y-layout v1 lookup prediction](../y-layout-prefix-v1/RESULTS.md) survived its
fixed diagnostic. Does its first-minus-other lookup gain remain distinctive
against other literal prefixes and after matching vocabulary opportunity?

Deleting a prefix can improve a match only when the original form is absent
from the reference vocabulary. An original already present can stay matched or
lose a match, but cannot improve. Different original-form frequencies and
representation lengths can therefore contribute to first/other comparisons.
This follow-up investigates that alternative; it does not change v1's rule,
threshold, decision or original result.

The v1 corpus and results have already developed this question. All material
remains previously exposed candidate-development data. No valid candidate
holdout, untouched evaluation, glyph meaning, language or translation is claimed.
These are descriptive controls with no new support/failure threshold or p-value.

## Fixed inputs and preprocessing

- Pin the corrected public parent at `1c6abb48776a6a59b527f502b50289edf9709191`.
  Use its unchanged plan, diagnostic partition, scientific report, ZL3b/IT2a
  source pins, shared-scan grouping and input metadata. Record their byte hashes
  in `inputs.json`, together with this plan, before new control scoring.
- Reconstruct the same 3,131 jointly non-start regular P0 locations and the same
  all-eight-variant common eligibility. Preserve original slots and source
  uncertainty policies. Verify all v1 vocabulary identities and every original
  y lookup cell/unit mean against the baseline before comparing controls.
- Construct the identical development-only internal ASCII-token vocabularies.
  Additionally count occurrences of each original representation among those
  development tokens, without using evaluation tokens to estimate frequency.
  Keep case, exclusions, source differences and word-space treatments intact.

## Comparison A: fixed other-prefix controls

Use the lower-case literal representation prefixes **y, q, and o**, fixed here
before scoring. q and o are comparison characters, not asserted glyph/phonetic
identities or an accuracy ranking. A scorable form has at least two ASCII
letters and starts with the specified character. Remove exactly that character.
Use the same vocabulary-membership gain in {-1,0,1} as v1.

For every diagnostic unit, source/policy and prefix, retain first and other-slot
candidate counts, all four original/stripped lookup cells, and mean gains,
including empty classes. Compare only units with both candidate classes for
**every prefix in all eight variants**. Average with equal unit weight. Report
all three first, other and selective gains, y-minus-q and y-minus-o selective
differences, every excluded unit/reason, and the y-only v1 result as context.
If no joint units remain, report undefined effects rather than invented zeroes.
Do not silently compare different unit cohorts or choose another control prefix.

## Comparison B: matched y opportunities

For y candidates, classify the original form using development-only frequency
bins **absent (0), singleton (1), repeated (2+)** and ASCII representation-length
bins **2–4, 5–7, 8+**. These are nine fixed cells; lengths are not manuscript
glyph counts. Keep all nine cells and both original-slot roles in each unit.

A matched cell is a unit × frequency × length cell with first and other y
candidates in **all eight variants**. Within each unit, average gain over its
matched cells with equal cell weight for each role, then average unit means
with equal unit weight. Use the same cells/units for every source/policy.
Report the standardized first-minus-other gain and the unstandardized y effect
on those **same units**, along with the difference. This separates composition
matching from changing the unit sample; it is not a causal decomposition.
If no common cells/units remain, retain undefined estimates and all exclusions.

Report original v1's broader 15-unit value separately. Matched cases remain
different strings/tokens, so this does not equate them to identical glyph regions
or certify correct annotation. Small or one-token cells remain visible. Exact
rational arithmetic determines means before eight-decimal presentation.

## Reporting and validation

Commit this plan and the byte-pinned inputs before computing q/o removal or
frequency/length-cell effects. Retain every treatment, unit, prefix/cell count,
source and vocabulary identity, selection hash, and undefined/excluded case.
Record the pre-control commit and execution chronology without calling Git
timestamps independent certification. No source token payload or manuscript
image needs to be redistributed.

Synthetic tests must verify all {-1,0,1} cells for each prefix, the deterministic
opportunity restriction, development-only frequency bins, length boundaries,
equal cell/unit weighting, all-prefix/all-variant common cohorts, empty cells,
unchanged v1 reconstruction, input/provenance drift refusal, and safe output
paths including symlink/hardlink aliases. The complete report must replay.

Interpret all outcomes as constraints on this dictionary diagnostic. Comparable
other-prefix gains or reduced matched y effects limit specificity; a residual
y difference still cannot choose an added layout marker over morphology,
spelling, segmentation or transcription. Stronger evidence needs independently
reviewed glyph regions, explicit generative alternatives and exposure-valid
candidate evaluation. Preserve the original v1 record and its limits.
