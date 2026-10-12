# Y-layout-prefix v1: exploratory representation diagnostic

## Claim and scope

A possible explanation of first-slot EVA `y` enrichment is that a leading `y`
is added at continuing P0 locus starts. This v1 candidate makes a narrower,
falsifiable representation prediction: removing exactly one leading literal
`y` should improve matches to a development-only internal-token vocabulary
more at original first slots than at other slots in comparable evaluation
page families. No language, phoneme, glyph identity, or translation is proposed.

This question is motivated by the exposed [position analysis](../../transliteration/POSITION_EFFECTS.md),
[prefix strata](../../transliteration/PREFIX_STRATA.md), and
[catalog-section analysis](../../transliteration/SECTION_STRATA.md). Those
full-corpus observations helped develop the candidate. **All selected material
has therefore already contributed to candidate development.** The diagnostic
partition below cannot qualify as an untouched or valid held-out candidate
evaluation under [the project protocol](../../DECIPHERMENT_PROTOCOL.md).
It separates dictionary fitting from scoring only. This is not the original
ten-folio pilot or a replacement for its unresolved mappings and 8/2 split.

## Fixed input and selection

- Exact ZL3b and IT2a pins from `data/transliterations.json`, with their original
  alphabet conventions, source credits, and CC0 licence. Use the accepted reader,
  source-pair guard, token policies, and original-slot representation.
- Select shared present P0 locations with locator `@`, `+`, or `*` in both
  sources. Then require absence of the source `<%>` start mark in both sources,
  outside free comments. Exclude source-start disagreements rather than picking
  a preferred annotation. Keep all excluded keys and selection digests.
- Run all eight source × split/join spacing × exclude/first-choice combinations.
  Restrict analysis to locus keys whose original first slot is retained and at
  least two retained tokens remain in every variant. First-slot values must be
  ASCII letters in every variant; other tokens enter the vocabulary/scoring only
  when they are ASCII letters. Case is preserved, and no ligature, escape,
  unreadable value, or phonetic identity is silently converted.
- For prefix-removal scoring, a candidate token must start with lower-case `y`
  and have at least two ASCII letters. Remove exactly that first character;
  preserve the remaining representation. Do not remove internal/final `y`,
  rewrite capitals, choose alternatives anew, or add exceptions after scoring.

## Partition fixed before dictionary construction

Use numeric source-page families, preserving every selected side/panel with
that number. Connect families through all transitive shared-scan components in
the accepted [image-reference audit](../../folio-alignment/IMAGE_COVERAGE.md).
Also connect families containing an exactly repeated P0 body in either source
after removing free comments, tags, paragraph marks and formatting whitespace.
Require at least two certain `.` boundaries and no `?` or alternative brackets
before calling such an exact-string repetition a dependency. Retain its hash
and source/folio provenance; do not equate it with a verified repeated passage.

Merge connected families into a single unit. Sort units by the SHA-256 of
`y-layout-prefix-v1-2026-10-11` plus the sorted family numbers. Assign the first
`max(1, floor(unit_count / 5))` units to diagnostic evaluation and the rest to
dictionary development. Require at least two units. Do not choose a partition
after inspecting vocabulary-match outcomes. Retain unit members, every indexed
canvas reference, dependency edges, source/input hashes, and both partition
digests in `partition.json`; commit it with this plan before fitting.

These are coarse source/image relationships, not adjudicated physical regions.
Unresolved panel localization remains explicit. Similar but non-identical
passages, unknown dependencies, and the earlier candidate-development exposure
prevent a strong generalization claim. This record deliberately does not use
the formal split validator's `frozen`/`unseen_material` status.

## Complete rule, fit, comparison, and decision

For each of the eight variants, fit one vocabulary: the set of ASCII tokens in
all retained **non-first slots** of common-eligible development loci. No evaluation
tokens or first-slot tokens enter it. Record vocabulary size, token count, and
digest; the data-dependent vocabulary is the sole fitted object. The strip rule,
selection, partition, and thresholds are fixed. One candidate version is tried;
the eight correlated source/preprocessing variants are sensitivity treatments.

For each eligible evaluation `y…` token, score
`I(stripped token in vocabulary) - I(original token in vocabulary)`, in {-1,0,1}.
Compute separate first-slot and other-slot mean gains within each unit. Compare
only evaluation units having both kinds of scorable tokens in **all eight**
variants. Keep all exclusions/denominators. Average unit means with equal unit
weight, then subtract other-slot mean gain from first-slot mean gain. This
controls for a general benefit of stripping `y` at any position. It is a lexical
lookup diagnostic, not evidence that matched forms are valid readings.

The candidate survives this v1 diagnostic only if the primary ZL split/exclude
first-slot gain is positive, its first-minus-other gain is at least **0.05**
(five percentage points), and all other seven variants have positive first-slot
and first-minus-other gains. Otherwise report `fails_v1_diagnostic`; if no common
evaluation units remain, report `indeterminate`. The 0.05 threshold is a fixed
decision convention, not a calibrated significance level. Do not replace this
rule after seeing outcomes or label a surviving result a validated decipherment.

Report every variant, unit, denominator, original/stripped match counts, gains,
selection/partition/source/vocabulary hashes, exclusions, and decision. Show
all before/after cases as aggregate counts; source bytes remain in the pinned
inputs. Do not publish invented plaintext or omit failures. No p-value or
confidence claim is made for this already explored corpus.

## Validation and next test

Synthetic cases must independently check known {-1,0,1} scores, original-slot
preservation, development-only vocabulary construction, equal unit weighting,
all-variant common eligibility, shared-scan and exact-string dependency closure,
deterministic partitioning, source-pin/partition drift rejection, empty groups,
and the fixed decision threshold. The complete report must replay offline.

Even a passing diagnostic would leave image-supported glyph/boundary review,
an exposure-valid evaluation corpus, model alternatives, and independent
reproduction unresolved. A failure rejects this particular lookup prediction,
not every possible role for `y`. Revise only as a new candidate version with
an explicit record of the failed v1 and newly exposed results.
