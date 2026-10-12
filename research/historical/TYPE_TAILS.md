# A fixed new block of historical B controls

Question: how often does the accepted native-record bag control produce B at
least as large, or at least as far from its exact mean, as observed?

The [plan](TYPE_TAILS_PLAN.md), [parameters](type-tails-plan.json) and
synthetic-tested producer were published at
[`660b151`](https://github.com/tobrien6/voynich-manuscript-research/commit/660b151ff410be6fc495bc39facccb8e168b4150)
before the first new source controls. All original source/mean/control, census,
figure and variance outcomes were already exposed. The [complete report](type-tails.json)
retains 1,000 new trials per variant, IDs 10–1009, with seed 20261012 and the
unchanged `historical-native-record-v1` SHA-counter/Fisher–Yates frame. All
original controls, IDs 0–9, remain separate and byte-equivalent to the parent.

## All four finite-sample outcomes

B counts distinct complete representation types with at least one equal pair
over the entire N−1 flat-stream edge path. All native-record joins and normalized
index-gap edges remain scored. Every record's retained token bag, length and
provenance slots remain fixed under the declared control. No corpus/policy
selection or new parsing is performed.

Both tail rules include ties. The upper rule is `B_control >= B_observed`.
The centered rule is `abs(B_control−mu) >= abs(B_observed−mu)`, with the parent's
exact rational mean mu. It is not obtained by doubling an upper-tail frequency.

| Ring treatment | f66r removed | Observed B | Upper exceedances / 1,000 | Upper ties | Upper plus-one score | Centered exceedances / 1,000 | Centered ties | Centered plus-one score |
| --- | --- | ---: | --- | ---: | ---: | --- | ---: | ---: |
| Omit R2 | M | 114 | 109 / 1,000 | 27 | 110 / 1,001 = 0.109890 | 179 / 1,000 | 27 | 180 / 1,001 = 0.179820 |
| Omit R2 | L | 115 | 93 / 1,000 | 13 | 94 / 1,001 = 0.093906 | 158 / 1,000 | 13 | 159 / 1,001 = 0.158841 |
| Remove ring singletons | M | 114 | 89 / 1,000 | 31 | 90 / 1,001 = 0.089910 | 169 / 1,000 | 31 | 170 / 1,001 = 0.169830 |
| Remove ring singletons | L | 115 | 75 / 1,000 | 22 | 76 / 1,001 = 0.075924 | 152 / 1,000 | 22 | 153 / 1,001 = 0.152847 |

The corresponding centered lower-count cutoffs are B≤96, B≤97, B≤95 and B≤96
in table order. The exact means place no integer control on the lower equality
boundary, so the reported centered ties here coincide with upper ties. These
cutoffs are derived from exact source rationals, not rounded display means.

Every case completed its entire fixed block. No additional trial was chosen,
discarded, repeated or stopped because of its tail outcome. Repeated statistics
are retained. All four cases happened to have 1,000 distinct flat-control hashes;
this is an observed diagnostic, not a sampling-without-replacement rule.

## Raw estimates, ranks and model assumptions

The raw exceedance frequency k/1000 estimates a tail of the stipulated control.
It is stored separately from the score `(k+1)/1001`, which includes the observed
statistic once and has minimum 1/1001. Full exact ratios and 50-digit half-even
display strings are retained. Display precision does not increase simulation
precision, and no confidence interval or decision threshold is supplied.

With ideal independent uniform draws from the within-record permutation group,
identity-inclusive ranks with conservative ties have a valid randomization
interpretation. [Hemerik and Goeman](https://doi.org/10.1007/s11749-017-0571-1)
give the group/draw assumptions; [Phipson and Smyth](https://doi.org/10.2202/1544-6115.1585)
discuss nonzero Monte Carlo/permutation conventions. The actual run uses a fixed
deterministic SHA stream keyed in part by original source bytes. It does not
prove ideal draw independence or uniformity, exhaustively enumerate the whole
permutation tail, or create an exposure-valid discovery test.

These are model-conditional exploratory simulation/rank diagnostics. They are
not a probability that a language/cipher is true, a manuscript-level significance
finding, an independent confirmation by multiple variants, or a reject/accept
decision. Both tail definitions and all four related inputs are retained.

## New control moments and immutable parent

| Ring treatment | f66r removed | Parent exact E[B], displayed | New control mean B | New unbiased sample variance B |
| --- | --- | ---: | ---: | ---: |
| Omit R2 | M | 105.494573 | 105.717 | 39.532443 |
| Omit R2 | L | 106.494573 | 106.499 | 38.314313 |
| Remove ring singletons | M | 104.754878 | 104.644 | 41.138402 |
| Remove ring singletons | L | 105.754878 | 105.743 | 39.456407 |

These empirical moments and the full B histograms describe the new controls;
they do not replace the exact parent mean or [exact variance](TYPE_VARIANCE.md).
The new sampling code depends on the accepted mean/control study and its nineteen
frozen dependencies, independently of the separately reviewed variance code.
All old observations, both corpus hashes, boundary/type-overlap diagnostics,
registered plans/amendment and forty original control rows remain unchanged.

## Validation and reproduce

Eleven focused tests pass. They verify inclusive ties, two distinct score
transforms, zero-exceedance minimum rank, constant controls, exact fractional
thresholds that binary rounding would misclassify, complete trial/hash retention,
strict inputs, identical serial/four-worker synthetic outputs and source/parent
failure preservation. Exhaustive small ideal IID nulls with ties verify both
plus-one score transforms' conservative rank property. That mathematical check
does not certify the fixed SHA stream or the observed manuscript's null model.

One hundred ten temporary direct/symlink/hardlink alias cases cover every frozen
source, parent, plan and producer, before and during computation. Failed checks
preserve prior output; duplicate JSON keys and numeric/boolean type substitutions
are rejected. Output protection is rechecked immediately before writing.

The complete 4,000-trial report replays byte for byte. A separate recount verifies
every trial ID and hash, exact inclusive tail count, histogram total and original
control row without using the producer's summary function. Four process workers
are independent computation jobs; their completion order changes neither keys
nor matrix output order. They are not new manuscript replications.

Python 3.10+, standard library only; recorded run used Python 3.14.3:

```sh
python3 scripts/historical_type_tails.py --output research/historical/type-tails.json
python3 scripts/historical_type_tails.py --check research/historical/type-tails.json
python3 -m unittest tests.test_historical_type_tails -v
```

The report retains source credits/reuse terms, exact accepted source/method/plan
and corpus identities, the new producer identity, every A/B/asterisk trial count,
and the SHA-256 of each encoded flat control token vector. It republishes no raw
control text or image payload.

Original-author input/parser/count/label discrepancies, physical line/glyph/word
adjudication and prior exposure remain unresolved. Finer controls, alternative
mechanisms and decoding predictions need separate plans and appropriate data;
these frequencies/ranks supply no language identity, decipherment or translation.
