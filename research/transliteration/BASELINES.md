# Exploratory token and repetition baselines

## Question

How much do uncertainty choices change token statistics, and do adjacent equal
tokens exceed the expectation from each locus's own token frequencies?

This is exploratory analysis of already available text, not a preregistered
decipherment test. There is no fitted decoding rule or translation in this result.

## Data, selection, and method

Explicitly select ZL3b and IT2a from the [pinned source catalog](../../data/transliterations.json) as specified in
[DECISION.md](DECISION.md). Select the intersection of their present loci whose
source-assigned kind is `P0`: **3,884 locations**. The sorted location-list digest,
source digests, all eight variants, and every shuffle result are recorded in
[token_baselines.json](token_baselines.json).

Other pinned comparator exports do not enter this paired analysis. Adding a
different alphabet or export to the catalog must not silently change its sample
or tokenization assumptions.

Each source is processed under four combinations:

- Split or join uncertain comma spaces. Periods and drawing intrusions always
  separate apparent tokens; formatting whitespace does not.
- Exclude tokens containing bracketed alternatives, or choose the first listed
  reading. The latter is a sensitivity treatment, not an adjudication.

Unreadable tokens and empty selected readings are excluded in every variant.
Their original slots remain gaps, so exclusion cannot make separated words
adjacent. Ligature notation, case, and rare-code identities are preserved in
token representations. Lengths count **EVA notation units**: each literal letter
or apostrophe counts once, `@nnn;` counts once, and ligature braces do not count.
For example, `ch` counts as two notation units. These lengths are neither
manuscript glyph counts nor phonetic measurements.

For repetition, count equal adjacent retained tokens within each locus. The
control uniformly shuffles that locus's retained representations over its
retained slots, preserving token multiplicities and excluded positions. It never
mixes loci or crosses their boundaries. With `m` retained tokens, counts `c_i`,
and `e` eligible adjacent edges, its exact expected equal-pair count is:

```text
e × sum(c_i × (c_i - 1)) / (m × (m - 1))
```

Sum this expectation across loci. In addition, run 199 shuffles with seed
20261011. The exploratory upper tail is `(1 + shuffles >= observed) / 200`.
The variants share input material and are not independent tests. These tails
are not adjusted for exploratory comparisons and have coarse Monte Carlo
resolution; use the effect sizes and complete distributions, not a significance label.

## Observations from the pinned inputs

| Source | Uncertain spaces | Alternatives | Retained tokens | Distinct representations | Mean notation units | Equal adjacent pairs | Conditional expectation |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| ZL3b | split | exclude | 33,299 | 6,742 | 4.9915 | 272 | 270.77 |
| ZL3b | split | first | 33,874 | 6,998 | 4.9947 | 274 | 274.37 |
| ZL3b | join | exclude | 30,908 | 7,647 | 5.3680 | 241 | 219.23 |
| ZL3b | join | first | 31,483 | 7,927 | 5.3730 | 242 | 222.18 |
| IT2a | either | either | 33,383 | 6,892 | 5.0668 | 282 | 264.73 |

IT2a has no uncertain commas or bracketed alternatives in these locations,
so its four treatments are identical. Its representations still differ from
ZL's conventions; distinct-type counts are representation-specific.

In the primary ZL split/exclude treatment, 272 of 29,013 eligible adjacent pairs
are equal (0.9375%), versus 270.77 expected (0.9333%). The exploratory shuffle
upper tail is 0.555. Under the join treatments it is 0.070; IT's is 0.075.
These results provide no clear excess in this analysis under the chosen conditional
control. Joining uncertain spaces changes the retained token count and vocabulary
substantially, so a single preprocessing choice would hide material sensitivity.

## Reproduce

Python 3.10 or later, standard library only. The recorded run used Python 3.14.3.
Random shuffles use `random.Random`; exact expectations do not depend on random
sampling. To generate or check the complete report:

```sh
python3 scripts/token_baselines.py --output research/transliteration/token_baselines.json
python3 scripts/token_baselines.py --check research/transliteration/token_baselines.json
python3 -m unittest discover -s tests -v
```

Check mode compares parsed report content, including the shuffle counts. A changed
source hash fails before analysis. Record interpreter changes if a shuffle replay
differs; do not silently replace the committed results.

## Limits and next test

The control asks whether ordering adds repetition beyond each locus's token bag.
It does not test a particular language, cipher, grammatical structure, or text
generation mechanism. A candidate could be compatible with this result without
being supported by it. `P0` loci are analysis units; we have not reconstructed
physical manuscript lines or verified the source labels against every image.

Further tests should study locus-position effects and representation choices
with explicit controls, then register candidate-specific predictions on an
evaluation set whose prior exposure is recorded. This full-corpus exploration
must not be relabeled as an untouched held-out evaluation.
