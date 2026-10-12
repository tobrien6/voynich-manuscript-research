# Matched other-prefix lookup control: exploratory plan v1

## Question and exposure

The [parent diagnostic](RESULTS.md) found that removing one leading literal
EVA `y` improves development-vocabulary lookup more at continuing-locus first
slots than at other slots. Does that difference remain after subtracting lookup
gains from deleting other leading letters at the same positions, matched on
encoded token length and development frequency?

The parent results, full paired corpora, source/annotation audits, and proposed
alternatives have already been inspected. This is a targeted post-result
exploratory control. It creates no valid held-out candidate evaluation or unseen
material. The original v1 rule, decision, partition and report remain unchanged.
Commit and publish this plan before new control gains are measured. Commit the
synthetic-tested implementation and exact protocol before manuscript execution.

## Inputs and fixed frame

Reuse the pinned ZL3b/IT2a sources, all eight source/spacing/alternative variants,
and the parent's original-slot tokenization. Recreate its jointly eligible
3,002 native locus keys, development-only internal vocabulary, source/partition
pins, and entire scientific report before scoring controls. Do not retokenize,
adjudicate glyphs, promote an excluded boundary, change the partition, or refit
on evaluation tokens.

The evaluation frame is exactly the parent's 15 all-variant units with both
original `y` candidate classes. The three other diagnostic units stay excluded
by the parent's joint rule, rather than being admitted through control coverage.
Compute development frequency as the occurrence count of each complete ASCII
token in retained non-first slots of common-eligible development loci. Its
support, token total and set digest must reproduce the parent vocabulary.
Record an additional sorted token/count digest. Case is preserved.

## Complete matching and score rule

A target starts with lower-case `y`, contains at least two ASCII letters, and
otherwise follows the parent's scorable rule. A control is likewise at least
two ASCII letters, with a lower-case first letter other than `y`. All such
letters are pooled; no letter is selected by its observed gain. Remove exactly
one leading character from either kind of token and score
`I(stripped in development vocabulary) - I(original in vocabulary)` in {-1,0,1}.

Match controls to each target on:

- The same source/spacing/alternative variant and evaluation unit.
- The same position class: original first slot or retained other slot.
- Exact ASCII token length.
- Complete-original-token development frequency bin: 0, 1, 2–3, 4–7, 8–15,
  and successive powers of two. For positive count c, the integer bin is
  `c.bit_length()`; count zero has bin 0. These bins are a declared coarse
  conditioning choice, rather than a calibrated model of word frequency.

Use **every control occurrence** in the matching pool with equal occurrence
weight. There is no random draw, nearest-neighbor fallback, replacement letter,
bin widening, or after-result matching revision. A pool may be reused by several
targets in its stratum; disclose this dependence and retain its size and prefix
composition. A target with no control pool is unmatched and receives no adjusted
score. Retain all unmatched counts and strata.

For each matched target, subtract its matching pool's mean gain from its own
gain. Average matched target gains and their corresponding control means within
each position class and unit. Each target occurrence has equal weight there.
Then average unit means with equal unit weight. The adjusted selective gain is
the adjusted first-slot mean minus the adjusted other-slot mean.

Require both matched position classes in every variant before including a unit
in the final comparison. Keep all 15 frame units, all missing-class reasons and
every variant's coverage in the report. Also report the unadjusted `y` gains on
the exact matched subset; this separates changed coverage from control subtraction.
Retain the original full-frame parent values as context, without reclassifying
the parent's decision or treating different denominators as equivalent.

## Fixed outcome and retained evidence

Use exact rational arithmetic for pool and unit averages and the sign decision.
If no joint units remain, report `indeterminate_matching_coverage`. Otherwise
report `positive_adjusted_selectivity_in_all_variants` only if the adjusted
first-minus-other gain is strictly positive in all eight variants; report
`mixed_or_nonpositive_adjusted_selectivity` otherwise. This is an exploratory
sign diagnostic with no p-value, confidence interval or calibrated threshold.
It is not the parent's 0.05 criterion or a new decipherment validation.

Retain all eight treatments, all unit/position/length/frequency strata, lookup
cells, target coverage, control occurrence/prefix counts, exact rational means,
joint-unit exclusions, source/input/implementation/plan/protocol hashes, and
parent/cohort/vocabulary identities. Publish no invented plaintext. Keep target
and control selection fixed on positive, mixed, negative and sparse outcomes.

Before manuscript execution, test all four lookup cells, frequency-bin edges,
matching by each required dimension, control occurrence weighting, pool reuse,
missing pools/classes, original-slot exclusions, development-only frequency
construction, equal unit weights, all-variant joint coverage, exact signs, and
refusal after parent/plan/protocol/implementation drift. Protect inputs and
code against both resolved and inode-alias output collisions. Replay the complete
report and independently reconcile its rational summaries.

## Limits and next test

Length means ASCII encoding length, rather than image-verified glyph count.
Frequency matching is coarse, and control prefix composition can vary by unit
and stratum. Unmatched targets and joint-unit selection may limit coverage.
Repeated controls, related editions and shared manuscript material are dependent.
A surviving difference could still reflect lexical/morphological conventions,
transcription, internal-vocabulary construction or other position effects.
It cannot identify an added layout marker, language, cipher or translation.

Any later candidate revision must preserve this record and obtain an
exposure-valid evaluation, image-supported glyph/line review, and separately
specified alternatives. Role: contributor under the user's continuing Voynich
goal, using `tobrien6`; the designated maintainer owns merge decisions.
