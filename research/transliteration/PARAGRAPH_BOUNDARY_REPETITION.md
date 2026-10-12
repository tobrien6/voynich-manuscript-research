# Exact repetition at encoded paragraph locus boundaries

There is **one exact token repeat across 652 consecutive encoded locus
boundaries** in the common paragraph corpus, in every source/spacing treatment.
The conditional within-locus permutation expectations are 4.68–5.74 repeats.
This selected corpus therefore shows no observed repeat excess at those
boundaries. No tail probability or candidate decision follows from the
SD-scaled descriptions below.

## Question, inputs and chronology

The [plan](PARAGRAPH_BOUNDARY_PLAN.md) asks whether the final native-Eva token
of one locus equals the first token of its next locus within an exact common
encoded paragraph. It was remotely published and verified at `9eeb0c1` before
measurement. The implementation and eleven passing synthetic tests were
published and verified at `19e4e38` before the first manuscript run. No
cohort, statistic, control, or decision criterion changed after the result.

The [common paragraph producer](PARAGRAPH_CORPUS.md), accepted in
[PR #95](https://github.com/tobrien6/voynich-manuscript-research/pull/95), replays
the accepted [membership audit](PARAGRAPH_MEMBERSHIP.md) from pinned CC0 ZL3b
and IT2a native-Eva sources. This analysis rebuilds that entire corpus and
checks every field in its committed coverage report before scoring boundaries.
It records the parent corpus's source, plan and implementation fingerprints,
its canonical digest, the coverage bytes, and this plan/implementation's hashes.
The complete [boundary report](paragraph_boundary_repetition.json) contains
metadata and moments, with no native token strings.

The parent review head changed from `43be569` to `aba7667` during execution.
That change integrated accepted main and changed no parent producer, source,
catalog, plan or coverage bytes. Integration preserved this analysis's exact
report and scientific inputs. The two source editions and their policies remain
dependent, and the manuscript/source material was already exposed.

## Cohort and observations

| Stage | Count |
| --- | ---: |
| Exact shared paragraph-membership candidates | 671 units / 3,647 loci |
| Whole units eligible in both editions and both spacing policies | 233 units / 885 loci |
| Whole-unit candidates excluded by the parent producer | 438 |
| Original consecutive boundaries within the retained units | 652 |
| Boundaries nonempty in all four variants | 652 |
| Retained units with no eligible boundary | 0 |

All present generic P subtypes are selected. No new drawing, locator, subtype,
section or length filter is applied. The synthetic tests retain singleton
paragraphs, but this actual retained cohort contains no singleton units.

| Treatment | Observed repeats | Exact conditional mean, decimal display | Conditional SD | Centered count / SD |
| --- | ---: | ---: | ---: | ---: |
| ZL3b split | 1 | 5.702162 | 2.345431 | -2.004818 |
| ZL3b join | 1 | 4.684708 | 2.126149 | -1.733043 |
| IT2a split | 1 | 5.738836 | 2.349368 | -2.017068 |
| IT2a join | 1 | 5.738836 | 2.349368 | -2.017068 |

The only observed repeat is between `f82r.3` and `f82r.4` in each variant.
Agreement at this identifier does not create four independent observations or
adjudicate its glyphs, segmentation, or image alignment. IT's spacing inputs
and all numerical results coincide.

The report preserves every original locus and boundary. Locator pairs are
60 `@ -> +`, 585 `+ -> +`, three `* -> +`, three `= -> =`, and one `+ -> =`.
Seventy-five boundaries touch at least one locus containing a drawing
interruption. These contexts remain included as declared; encoded consecutive
loci must not be promoted to verified adjacent physical words or lines.

## Control and exact covariance

Uniformly permute token **occurrences** independently within each original
locus, preserving its size and complete token multiset. Tokens never move
between loci or paragraphs. For each boundary, the repeat probability is the
overlap of the two loci's token-frequency distributions. The observed statistic
is the unweighted sum of exact equality indicators over the same boundaries.

Neighboring boundaries share a middle locus. Its first and final tokens are
distinct without-replacement draws when it has two or more tokens; when it has
one token, both boundaries use that same occurrence. The [plan](PARAGRAPH_BOUNDARY_PLAN.md)
gives both joint-probability formulas. Subtract the product of marginal
probabilities to obtain each covariance, and add twice the covariance to the
sum of individual Bernoulli variances. Nonadjacent boundaries use disjoint
loci and have zero covariance under the stipulated control.

Means, centered counts, variances, probabilities and covariances are retained
as exact numerator/denominator pairs for every boundary and paragraph.
Paragraph means and variances add under the control's independent-locus
assumption. No assumption of independent manuscript sampling is established.
Zero-variance controls have a null SD-scaled contrast, rather than infinity or
a fabricated probability. The control changes first/last positional roles,
so positional conventions are an immediate alternative explanation.

## Reproduce and verify

Python 3.10 or later; standard library only, on a checkout containing the parent
corpus contribution:

```sh
PYTHONPATH=tests python3 -m unittest test_paragraph_boundary_repetition -v
python3 scripts/paragraph_boundary_repetition.py --check research/transliteration/paragraph_boundary_repetition.json
python3 scripts/paragraph_boundary_repetition.py --output /tmp/paragraph-boundary-repetition.json
```

Eleven focused tests cover all 488 binary token assignments in five small
locus layouts, exhaustively enumerating 7,816 occurrence orderings. They verify
exact means and variances, singleton sharing, negative covariance and constant
controls, disjoint pairs, omitted coordinates, common boundary exclusions,
source metadata, input preservation, forged parent rejection, duplicate and
nonfinite JSON, typed cache tampering, and protected direct/hardlink outputs.

A separate occurrence-based calculation on the actual retained corpus verifies
all 2,608 source/policy boundary probabilities and 1,676 adjacent-boundary joint
probabilities, including every paragraph variance. It enumerates occurrence
pairs directly instead of using the production Counter overlap formula. The
complete report replays exactly after integration. Output guards run before
computation and protect source/catalog/code, both producer plans, parent reports,
the new plan and verification inputs, including resolved and hardlink aliases.

## Limits and next test

This is a narrow, heavily uncertainty-filtered corpus: only 233 of 671 matched
units survive the parent's whole-unit exclusions. It measures equality of
native transcription strings, not decoded words or independent glyph readings.
One observed repeat and an SD-scaled count cannot identify or reject a general
copying process, language, cipher, paragraph mechanism, or decipherment.

A later candidate-specific test needs a generator and controls that address
endpoint/position conventions, representation uncertainty and the selected
population. Preserving the exact endpoint tokens would make this particular
statistic invariant, so a revised statistic must state what information remains
testable. Any prospective evaluation also needs explicit dependency groups,
prior-exposure records and an honest frozen split. No translation is proposed.

The [anchored whole-locus order control](PARAGRAPH_ORDER_CONTROL.md) keeps every
locus's endpoint tokens intact while permuting interior locus identities within
the same paragraphs. Its expected repeat count is 0.83–1.03, with only four or
five variable units; all invariant units remain in the original denominator.
