# Exploratory interior notation-length order, version 1

These choices are recorded before executing this analysis on manuscript data.
This is a structural exploration, not a registered decoding candidate or an
untouched evaluation. The full-corpus coverage, token/repetition, and boundary
position reports were already inspected. No rule is fitted and no development /
evaluation split is asserted. Record the plan commit in the result note.

## Question and inputs

Do neighboring interior tokens have related **native Eva ASCII notation
lengths**, beyond what follows from each locus's own length multiset? This
measures a constraint a future text-generation or decoding mechanism might need
to explain; it does not identify glyphs, words, sounds, language, or meaning.

Use only the pinned ZL3b and IT2a inputs in
[the source catalog](../../data/transliterations.json). Reuse the accepted
[conservative adapter](TOKEN_ADAPTER.md) with P0 loci only. Evaluate split and
join treatments of uncertain spaces. Keep the two sources paired, not pooled
as independent replicates. GC's alphabet and the derived RF inputs are outside
this question. All notation lengths are `len(token)` on plain ASCII letters;
case is retained and does not change this measure.

Take the intersection of present P0 locus keys in both sources, sorted
lexicographically. Require eligibility under all four source / spacing
treatments. Exclude a locus in all treatments if any treatment has a drawing
interruption or fewer than five tokens. Entire ambiguous, unreadable, extended,
or malformed loci are excluded by the adapter. Report exclusion counts at each
stage and reason counts (which can overlap), all retained identities, source
hashes, and the cohort identity hash. Do not infer panel or image boundaries
from an IVTFF page identifier. A P0 locus is not necessarily a physical line.

## Statistic and conditional control

For each retained locus, fix the original first and last tokens. Use only the
interior tokens, omitting pairs that touch a fixed endpoint. This prevents
the previously observed first/last-token differences from directly supplying
the new statistic. The control preserves interior token multiplicities and
locus length, and moves nothing between loci or folio sides. It does not
preserve a possible gradient or other positional structure *within* the
interior; those remain alternative explanations of an order effect.

Let the interior lengths be `x[1] ... x[m]`, with `m >= 3`, their sum `s`,
integer deviations `d[i] = m*x[i] - s`, squared-deviation sum `D`, and adjacent
product sum `A = sum(d[i]*d[i+1])`. For `D > 0`, use

```
R = m*A / ((m-1)*D)
C = R + 1/(m-1)
```

`R` is adjacent mean centered product divided by the interior population
variance. Under a uniform permutation of this fixed multiset, any neighboring
pair has expected centered product `-variance/(m-1)`, because distinct draws
are negatively associated without replacement. Therefore the exact conditional
expectation of `R` is `-1/(m-1)`, and that of `C` is zero. The correction matters
for short loci. For constant interiors (`D == 0`), define `R = C = 0`, retain
the locus in the denominator, and report constant-locus counts separately.

The corpus statistic is the arithmetic mean of `C` across retained loci:
each locus has equal weight. Also report the mean `R`, its exact conditional
expectation (constant loci contribute zero), token/pair denominators, source
Currier metadata, and per-page observed statistics. Page identifiers remain
transcription units; their counts are not physical-leaf counts. Per-page values
are descriptive only; do not search them for a selected significant subset.

Generate **999** controls with seed **20261011**, trials **0 through 998**,
using the accepted `HashDraws` and Fisher-Yates routines. Shuffle integer
notation lengths, which is equivalent for this statistic to shuffling the
corresponding tokens. For each source/treatment, pin a compact UTF-8 JSON list
of `[page_id, locus_key, interior_lengths]` (separators `(',', ':')`) and hash it.
Each locus's draw key is SHA-256 of compact UTF-8 JSON:

```
["sha256-counter-fisher-yates-v1", length_corpus_sha256,
 "locus-interior-notation-lengths-v1", 20261011, trial,
 [page_id, locus_key]]
```

Identical length corpora use identical controls, including IT's two spacing
policies if they coincide. Save every corpus control statistic. Report the
two-sided Monte Carlo tail `(1 + count(abs(control) >= abs(observed))) / 1000`,
with numerical comparisons allowing `1e-12` for floating-point equality.
The primary treatment is ZL3b split. Report the other three as paired
sensitivity checks without selecting the smallest tail. A primary tail at or
below 0.01 will be described as a departure from this conditional
exchangeability control. A robust direction additionally requires the same
sign in all treatments; report any contradictory sign or nonsmall tail.
This decision convention is exploratory and supplies no calibrated
decipherment confidence or generalization claim.

## Verification and limits

Before manuscript execution, use synthetic exhaustive permutations to check
the expectation, repeated/constant values, endpoint isolation, and equal locus
weighting. Test cohort exclusions and deterministic control invariants. Do not
tune the statistic, cohort, seed, trial range, or tail after seeing the result.
Replay the full report from pinned inputs and retain negative findings.

Even a small tail distinguishes only this narrow control. Interior position
gradients, paragraph context, copying, transcription conventions, or selection
of clear loci could explain it. ZL/IT agreement is sensitivity evidence, not
independent manuscript verification. No synthetic-cipher or documented-language
comparison is included, so this cannot distinguish linguistic text from other
production mechanisms. A later candidate needs a recorded split, explicit
rules, appropriate controls, and new prospective evaluation.

Source context: [publisher's transliteration account](https://voynich.nu/transcr.html)
distinguishes representation from proposed readings and documents differing
alphabet units; [the source decision](DECISION.md) and
[shuffle method](../token-controls/README.md) retain input and control provenance.
