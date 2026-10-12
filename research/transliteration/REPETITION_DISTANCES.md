# Equal-token recurrence at original-slot distances

Question: does the near-null adjacent-repetition result also describe equal
token representations separated by two, three, or four apparent-token slots?

This follows the [exploratory plan](REPETITION_DISTANCE_PLAN.md), committed as
`755dd58` before computing the new manuscript distance results. The source text
and earlier adjacent baseline were already exposed. This is exploratory
description, not preregistration, a reserved evaluation, or a decoding test.

## Sources and coordinates

Use the same **3,884 shared present P0 loci** and pinned ZL3b/IT2a bytes as the
[accepted baseline](BASELINES.md). Sources, cohort digest, preprocessed-slot
digests, plan digest, and calculation-file digests accompany all eight source
and policy treatments in [the complete report](repetition_distances.json).
No existing baseline fields or recorded shuffles are changed.

Apply the shared tokenizer and split/join uncertain-space and exclude/first
alternative policies. Equality compares preserved representations, not decoded
words or adjudicated glyphs. An excluded apparent-token slot remains `null`.
At distance `d`, an eligible pair has retained endpoints at original slots
`i` and `i+d` in the **same locus**. Interior slots may be excluded. For
`[a, null, a]`, the pair is at distance 2; there is no distance-1 edge.
The report counts pairs spanning excluded interior slots explicitly.

Distances refer to each treatment's apparent-token coordinates. Joining comma
spaces changes those coordinates. Denominators also change with distance and
source. This is not a fixed endpoint cohort across distances, and a locus is
not automatically a physical manuscript line. The accepted P0 cohort retains
fragment loci; this follow-up does not reconstruct or concatenate them.

## Exact conditional calculation

Within each locus, uniformly permute its retained token bag over the retained
positions, keeping exclusions fixed. Construct a simple graph for each distance
and reuse the [exact graph moment calculation](REPETITION_VARIANCE.md).
For different distances, the edge sets are disjoint. Thus:

```text
Cov(T_d, T_e) = [Var(T_d + T_e) - Var(T_d) - Var(T_e)] / 2
```

Compute the sum variance on the union graph. It includes both shared-endpoint
and disjoint-edge dependencies from sampling the same finite token bag without
replacement. Sum locus means and full covariance matrices under the stipulated
independent-locus permutation control. Physical manuscript independence is not
asserted. Exact fractions are preserved alongside eight-decimal diagnostics.

Counts at different distances are correlated. For the primary ZL split/exclude
treatment, the covariance between distances 1 and 2 is **-47.68734614**. The
full 4-by-4 matrices and their exact fractions remain in the report; the
distances and treatment variants must not be treated as independent tests.

## Results

Every distance-1 count, denominator, mean, variance, SD, and SD-scaled contrast
reproduces the accepted baseline exactly for all eight treatments. IT2a's four
policy results are identical, verified before collapsing them in this table.

| Source / spaces / alternatives | Distance | Eligible pairs | Equal pairs | Conditional expectation | Conditional SD | Excess in SD |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ZL / split / exclude | 1 | 29,013 | 272 | 270.77 | 14.208 | 0.087 |
| ZL / split / exclude | 2 | 25,275 | 297 | 237.16 | 13.605 | 4.399 |
| ZL / split / exclude | 3 | 21,539 | 230 | 203.25 | 12.819 | 2.086 |
| ZL / split / exclude | 4 | 17,910 | 188 | 170.44 | 11.904 | 1.475 |
| ZL / split / first | 1 | 29,930 | 274 | 274.37 | 14.295 | -0.026 |
| ZL / split / first | 2 | 26,073 | 300 | 240.16 | 13.681 | 4.374 |
| ZL / split / first | 3 | 22,235 | 232 | 205.90 | 12.899 | 2.024 |
| ZL / split / first | 4 | 18,498 | 192 | 172.60 | 11.977 | 1.620 |
| ZL / join / exclude | 1 | 26,641 | 241 | 219.23 | 12.671 | 1.718 |
| ZL / join / exclude | 2 | 22,903 | 234 | 189.65 | 12.096 | 3.666 |
| ZL / join / exclude | 3 | 19,186 | 176 | 159.68 | 11.329 | 1.441 |
| ZL / join / exclude | 4 | 15,621 | 147 | 130.49 | 10.412 | 1.586 |
| ZL / join / first | 1 | 27,543 | 242 | 222.18 | 12.738 | 1.556 |
| ZL / join / first | 2 | 23,687 | 238 | 191.85 | 12.156 | 3.797 |
| ZL / join / first | 3 | 19,859 | 178 | 161.43 | 11.387 | 1.455 |
| ZL / join / first | 4 | 16,172 | 150 | 132.00 | 10.469 | 1.719 |
| IT / all policies | 1 | 29,454 | 282 | 264.73 | 13.997 | 1.234 |
| IT / all policies | 2 | 25,579 | 277 | 230.67 | 13.380 | 3.463 |
| IT / all policies | 3 | 21,737 | 227 | 196.67 | 12.592 | 2.409 |
| IT / all policies | 4 | 18,002 | 187 | 163.68 | 11.653 | 2.001 |

Distance 2 has a positive observed-minus-expected count in every treatment.
The primary result is 59.84 pairs above its conditional expectation, or 4.399
conditional SD. Its 25,275 eligible pairs include 388 spanning excluded
interior slots; the corresponding IT count is 35 of 25,579. The complete
report preserves these counts for every distance and policy. The result
distinguishes this exposed corpus's short-distance recurrence profile from
its adjacent-only summary under the specified conditional control.

SD scaling is descriptive. No normal tail, significance label, multiple-test
calibration, or probability of a copying mechanism is supplied. All distances
are reported. Their eligibility populations differ, so comparing standardized
values does not isolate distance as a causal effect. A token-bag departure
cannot identify a language, cipher, glyph reading, or translation.

## Reproduce and validate

Python 3.10 or later, standard library only; the recorded run used Python 3.14.3.
Obtain the exact raw sources using
the [source decision](DECISION.md); source hashes are verified before analysis.

```sh
PYTHONPATH=tests python3 -m unittest \
  test_repetition_distances test_repetition_moments test_token_baselines
python3 scripts/repetition_distances.py \
  --check research/transliteration/repetition_distances.json
python3 scripts/repetition_distances.py --output /tmp/repetition-distances.json
```

Seven new test methods include exhaustive unique permutations for all 64
exclusion masks of a six-slot synthetic example. They check the full mean and
covariance matrices, original-slot coordinates, negative covariance, zero
variance and empty denominators, independent-locus addition, source-specific
uncertainty policies, and invalid input. Temporary direct/symlink/hardlink
output probes verify that the CLI preserves calculation inputs. These tests
contain no manuscript readings. The two accepted helper/tokenizer suites bring
the targeted total to 22 passing tests.

Check mode recomputes the complete report, including exact fractions and pins.
The preprocessed digest hashes ASCII compact JSON of sorted
`[locus_key, original_slots]` rows, preserving null exclusions. The output guard
protects raw sources, source catalog, plan, calculation files, and the accepted
baseline. It does not execute candidate code or change the earlier report.

## Next test and limits

The conditional model fixes each locus's bag but does not preserve token
position roles, local transitions, paragraph structure, or differences between
folio sections. Those can create a recurrence profile without a particular
copying mechanism. Image localization and source-label review remain pending.

A subsequent fixed protocol should assess page/paragraph strata and token
position roles, account for differing distance eligibility, and compare an
explicit generator's predicted joint recurrence profile with this observation.
Preserve exposed-corpus status and failed predictions. A future decipherment
candidate still needs frozen rules, reviewed inputs, a disclosed exposure
record, and independent source-linked evaluation.
