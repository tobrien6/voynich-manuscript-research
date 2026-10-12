# Y-layout-prefix v1: lookup prediction survives an exploratory diagnostic

## Question, registration, and exposure

Does deleting exactly one leading literal EVA `y` improve internal-vocabulary
matches more at continuing-locus first slots than at other slots?

The [complete rule and decision criterion](PLAN.md) and
[dependency-aware dictionary partition](partition.json) were committed and
pushed before fitting at
[`0ea2416`](https://github.com/tobrien6/voynich-manuscript-research/commit/0ea2416d47aa6134e5ecf2127a96f88ecefbd915).
The recorded commit time is 2026-10-11 23:56:08 EDT; dictionary fitting began
2026-10-12 00:02:35 EDT. These Git/run timestamps are evidence to inspect, not
independent certification of honest history. Full-corpus position results
already motivated this candidate, so **every unit had contributed to candidate
development**. This is an exploratory dictionary fit/scoring partition, not a
valid held-out candidate evaluation, an unseen corpus, or the original pilot's
unresolved 8/2 split.

Exact source, metadata, partition, implementation, and vocabulary hashes, all
denominators and exclusions, and every unit's before/after counts are in
[results.json](results.json). Inputs remain the licensed pinned ZL3b/IT2a
editions, using the existing reader and uncertainty policies. No source text
payload, manuscript image, decoded reading, or translation is added.

## Method and analysis units

The fixed source selection has 3,131 shared regular P0 locations with no
paragraph-start mark in either edition. Requiring retained ASCII first slots
and another retained token in all eight variants leaves **3,002 common eligible
locations**; the 129 excluded keys are retained in the report. Other retained
ASCII tokens contribute to the dictionary and scoring without promoting an
excluded boundary or converting ligatures/rare notation into letters.

Numeric source-page families are grouped through the accepted shared-scan
components. The exact-long-string dependency check finds no cross-family
repeated eligible body under its declared rule. This does not establish that
there are no similar/repeated passages or missing dependencies. The pre-fit
hash-ranked partition has **74 development units and 18 diagnostic units**.
It preserves sides, panels, and every indexed canvas reference without claiming
reviewed text-region alignment.

For each variant, fit a set of ASCII representations from development **non-first
slots only**. Evaluation values and all first slots are excluded from vocabulary
construction. A scorable token starts with lower-case `y` and has at least two
ASCII letters. Its match gain is `I(stripped form in vocabulary) - I(original
form in vocabulary)`, in {-1,0,1}. This is string lookup, not reading accuracy.

Each diagnostic unit needs both first-slot and other-slot scorable tokens in
every variant. **15 common units remain**. Families 5 and 7 lack a scorable
class in every variant; family 13 has both classes only under the ZL join
treatments and therefore fails the joint rule. All 18 units remain in the
record, with missing classes explicit. First/interior candidate tokens need not
be identical across sources or spacing policies even on common locus/unit keys.

Average first-slot and other-slot gains separately within each common unit,
then give those units equal weight. Subtract other-slot gain from first-slot
gain. The rule set before scoring requires primary first gain > 0 and selective
gain >= 0.05, plus positive first and selective gains in all seven sensitivities.
The threshold is a decision convention, not a calibrated significance level.

## Complete variant summary

All gains below are fractions, averaged with equal unit weight:

| Source | Spaces | Alternatives | Vocabulary entries | First gain | Other gain | First minus other |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| ZL3b | split | exclude | 3,487 | +0.48112922 | +0.05222222 | +0.42890700 |
| ZL3b | split | first | 3,602 | +0.48112922 | +0.05222222 | +0.42890700 |
| ZL3b | join | exclude | 3,968 | +0.39957115 | +0.05777778 | +0.34179337 |
| ZL3b | join | first | 4,093 | +0.39957115 | +0.05777778 | +0.34179337 |
| IT2a | split | exclude | 3,755 | +0.42004734 | +0.08444444 | +0.33560290 |
| IT2a | split | first | 3,755 | +0.42004734 | +0.08444444 | +0.33560290 |
| IT2a | join | exclude | 3,755 | +0.42004734 | +0.08444444 | +0.33560290 |
| IT2a | join | first | 3,755 | +0.42004734 | +0.08444444 | +0.33560290 |

The recorded decision is **`survives_v1_diagnostic`**. The primary selective gain
is +0.42890700, exceeding the fixed +0.05 convention; first and selective gains
stay positive in every sensitivity treatment. IT's repeated rows reflect its
unchanged notation under these policies, not four independent replications.

For the primary treatment, the common units contain **85 first-slot candidates**:
35 originals and 71 stripped forms match the development vocabulary. Of the
85, 34 match both ways, 37 improve, one loses a match, and 13 match neither way.
The **82 other-slot candidates** have 67 original and 70 stripped matches:
66 match both ways, four improve, one loses a match, and 11 match neither way.
Losses and unresolved lookups are retained. These pooled counts give different
rates from the equal-unit statistic and are not its denominator.

Some units have only **one** candidate in a class, so unit means can be extreme.
The 15-unit diagnostic selection is small and eligibility-dependent. No p-value,
confidence interval, calibrated confidence, or population accuracy is claimed.

## Interpretation and alternatives

The fixed lookup prediction survives this exploratory test. The representation
pattern is consistent with some first-slot `y…` forms sharing a remaining string
with internal forms. It does not show that the manuscript writer inserted a
layout marker, or that deleting a glyph recovers a word. Lexical/morphological
prefixes, positional spelling conventions, transcription choices, and the
reference dictionary's exclusion of first slots could also contribute.

The sources and treatments are related, the corpus informed the hypothesis,
coarse image references remain unadjudicated, and EVA letters are not validated
phonetic/glyph units. The result selects no language, meaning, cipher, or English
translation. It cannot satisfy the project's independently reproduced
decipherment standard or convert the original pilot into a complete corpus.

## Reproduce and validate

Python 3.10 or later, standard library, and Git with the pre-fit commit available.
The recorded run used Python 3.14.3. From the repository root:

```sh
python3 scripts/y_layout_prefix.py --check research/hypotheses/y-layout-prefix-v1/results.json
PYTHONPATH=tests python3 -m unittest test_y_layout_prefix -v
```

The checker rebuilds the pinned image report and deterministic partition,
verifies the committed rule/partition bytes and chronological declarations,
reconstructs development-only vocabularies, and compares the complete report.
For a shallow checkout lacking the historical commit, fetch the public
pre-fit commit before replaying: `git fetch origin 0ea2416d47aa6134e5ecf2127a96f88ecefbd915`.
An archive without Git history cannot verify this chronology gate.

Synthetic tests independently check the four lookup cells and known gains,
development-only vocabulary construction, equal unit weighting, original-slot
exclusions, all-variant eligibility, deterministic dependency grouping,
empty/indeterminate cases, the exact rational threshold, sensitivity failure,
and refusal to fit after partition/rule drift or a post-fit registration.
Inherited source-pin tests reject changed source bytes before processing.

Next, preregister matched controls for deleting other prefixes and conditioning
on original form frequency/length. Review the relevant first-slot glyph regions
independently against images. Any stronger candidate test needs new exposure-valid
material and a reviewed unit/split definition. Preserve this v1 and its limits
when revising the proposed mechanism.
