# Exploratory locus-position effects

## Question and prior work

Do the first and last apparent tokens in source-assigned P0 loci differ from
the other tokens within the same loci, after conditioning on their token bags?

**LP-RK2011:** Sravana Reddy and Kevin Knight,
[What We Know About The Voynich Manuscript](https://aclanthology.org/W11-1511/),
2011, section 6.2 and Figure 7 (pp. 83–85), reports line-edge character patterns
using a Currier-based source. Our test uses EVA representations and locus slots,
so its numeric results are not a replication of their line/glyph measurements.
The paper motivates this exploratory question; it does not establish our results.

The [analysis choices](POSITION_PLAN.md) were committed before running this
analysis. The data were already exposed in the source audit and repetition
baselines. This is neither an untouched evaluation nor a decipherment claim.

## Inputs and analysis units

Use the exact [ZL3b and IT2a pins](../../data/transliterations.json), restricted
to their 3,884 shared present P0 locations. Additional catalogue entries do not
enter the paired analysis. The selection digest matches
[the token baselines](BASELINES.md).

Run split/join uncertain spaces and exclude/first-choice alternatives. Retain
original token slots, leaving unreadable, excluded, or empty selections as gaps.
For each boundary test, require that the original boundary slot is retained and
at least one other token remains. An excluded first token is not replaced by
the second. Source and policy differences can change eligible-locus sets.

Features are **literal representation prefixes** `q` and `y`, plus
**EVA notation-unit length**, defined in BASELINES.md. Ligature braces and case
are preserved: a representation beginning with `{` is not silently rewritten
to a bare prefix. These are not phonetic features or validated manuscript glyph
identities.

For each eligible locus, compute boundary feature minus the mean feature among
its other retained tokens. Average these differences with equal weight per
locus. Reported "other" rates are averages of within-locus means, not a pooled
rate over all interior tokens. A single long locus cannot dominate the contrast.

## Conditional control

Uniformly permute retained tokens over retained slots within each locus, keeping
the token bag, exclusions, and locus boundary. For scalar values `x_1 ... x_m`,
the contrast for a randomly selected boundary token `X` is:

```text
D = X - (sum(x_i) - X) / (m - 1)
E[D] = 0
Var(D) = (m / (m - 1))² × mean((x_i - mean(x_i))²)
```

For the mean over `N` eligible loci, sum these variances and divide by `N²`.
The report records the exact conditional standard deviation and 199 shuffled
mean contrasts, seed 20261011. The two-sided exploratory tail is
`(1 + count(abs(shuffled) >= abs(observed))) / 200`, with a `1e-12` tolerance
for floating-point ties. It is unadjusted for multiple, dependent comparisons.
The minimum reported tail is 0.005; a value at that floor does not mean a zero
probability or estimate a much smaller probability.

## Observations

Primary ZL3b split/exclude results:

| Boundary | Eligible loci | Feature | Boundary mean | Mean of locus others | Paired difference | Exact null SD |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| first | 3,778 | literal q prefix | 0.13155 | 0.15108 | -0.01953 | 0.00609 |
| first | 3,778 | literal y prefix | 0.14293 | 0.03581 | +0.10712 | 0.00385 |
| first | 3,778 | notation units | 5.45236 | 5.00715 | +0.44521 | 0.03044 |
| last | 3,740 | literal q prefix | 0.08663 | 0.15890 | -0.07227 | 0.00610 |
| last | 3,740 | literal y prefix | 0.03717 | 0.05353 | -0.01637 | 0.00384 |
| last | 3,740 | notation units | 4.75936 | 5.08322 | -0.32387 | 0.03055 |

The direction of all six contrasts is unchanged across the four ZL treatments
and IT's equivalent treatments. First-slot y-prefix enrichment ranges from
0.10681 to 0.10844 in ZL and is 0.10681 in IT. Last-slot notation-length
differences are more sensitive: ZL ranges from -0.32387 to -0.16136, while IT
gives -0.44807. Treat these as representation- and eligibility-dependent
measurements, not directly comparable glyph-length effects.

Every reported two-sided shuffle tail is at the 0.005 resolution floor. Summary
fields rounded to eight decimal places, all shuffled differences, eligibility
reasons, paragraph-start counts, source Currier labels, and locator counts are in
[locus_positions.json](locus_positions.json). The prefix/length structure is
incompatible with simple exchangeability under this particular within-locus
control; it does not identify the mechanism producing that structure.

## Reproduce and validate

Python 3.10 or later, standard library only. The recorded run used Python 3.14.3.

```sh
python3 scripts/locus_positions.py --output research/transliteration/locus_positions.json
python3 scripts/locus_positions.py --check research/transliteration/locus_positions.json
PYTHONPATH=tests python3 -m unittest test_locus_positions test_token_baselines test_ivtff test_source_audit -v
```

The exact variance is checked against exhaustive small permutations. Tests also
verify equal locus weighting, boundary-gap handling, exclusion of lone retained
tokens, and isolation of the declared EVA pair as other alphabets are added.
Check mode compares the complete report, including the shuffle sequence.

## Limitations and next test

P0 is a source-assigned locus type, not a reconstructed physical line. Both
source files include 36 P0 records with locator `=`, which denotes an item on
the same line as a preceding item. Paragraph boundaries and excluded readings
also differ. The report's eligibility and metadata counts expose these choices;
they do not correct or independently verify the annotations.

Next, test whether the contrasts persist after separating source-marked
paragraph starts and excluding same-line fragments. Use source Currier labels
as documented strata, without equating them to identified natural languages.
Candidate mechanisms should then make additional preregistered predictions
with the separate evaluation-split workflow and recorded prior exposure.
