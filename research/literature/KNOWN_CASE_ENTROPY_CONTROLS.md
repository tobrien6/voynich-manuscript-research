# Entropy maximization need not recover a known case relationship

Question: when an uppercase/lowercase relationship is independently known
from a data generator, must an entropy-maximizing replacement recover it?

No. Two original generated examples preserve an explicit `A`→`a` case rule,
yet the largest whole-corpus entropy decrease chooses `b` in both. The
conditional-subset score recovers `a` in one example and chooses `b` in the
other. This limits a logical inference from substitution scores; it does not
estimate their error rate on natural text or determine a manuscript symbol's
case function.

## Independently specified case rule

The generator begins with lowercase base lexemes `a`, `b`, `xb`. It capitalizes
only the declared number of occurrences of `a`, yielding `A`; all other
occurrences remain unchanged. Lowercasing the generated words restores every
base lexeme's count exactly. Thus `A`→`a` is the known inverse of the case
operation, specified independently of the entropy ranking.

| Constructed regime | Base `a` count | Capitalized as `A` | Base `b` count | Base `xb` count | Total |
| --- | ---: | ---: | ---: | ---: | ---: |
| Balanced rare case | 2 | 1 | 99 | 99 | 200 |
| Skewed common case | 100 | 99 | 99 | 99 | 298 |

These are abstract synthetic lexemes and deliberately chosen frequencies,
with no natural-language population or manuscript glyph correspondence.
The three replacement candidates are exactly `a`, `b`, `x`, the lowercase
alphabet of the base lexemes. Every candidate is scored in both regimes.
Replacing `A` with `b` merges occurrences of different base lexemes and does
not invert the declared case rule.

## Both scores and all candidates

For each candidate, replace every `A` inside words without deleting a symbol
or crossing a word boundary. Whole-corpus entropy uses all occurrences before
and after replacement. The subset calculation selects occurrences containing
either `A` or the candidate and renormalizes both distributions on that set.
All affected counts, exact mass fractions and transformed synthetic counts
remain in the [complete report](known-case-entropy-controls.json).

| Regime | Candidate | Subset decrease, bits | Whole-corpus decrease, bits |
| --- | --- | ---: | ---: |
| Balanced rare case | `a` (known inverse) | 1.000000000000 | 0.010000000000 |
| Balanced rare case | `b` | 0.040599565777 | 0.040396567948 |
| Balanced rare case | `x` | 0.000000000000 | 0.000000000000 |
| Skewed common case | `a` (known inverse) | 0.080793135896 | 0.027111790569 |
| Skewed common case | `b` | 0.666666666667 | 0.664429530201 |
| Skewed common case | `x` | 0.000000000000 | 0.000000000000 |

All four rankings have a unique positive maximum. In the first regime,
two equally frequent case variants merge perfectly inside their rare subset;
that subset's small mass reduces the whole-corpus gain. In the second,
case variants occur at counts 99 and 1, while the incorrect `A`/`b` merge
combines two 99-count forms. Both normalizations then favor the incorrect
candidate. This is the information-loss behavior of these word distributions,
not evidence that the independently specified case rule changed.

The [normalization control in PR #153](https://github.com/tobrien6/voynich-manuscript-research/pull/153)
derives the affected-mass identity; the first example here gives it a separately
known case relation and retains the zero-gain third candidate. The second
adds a failure under both definitions. The
[native comparison in PR #158](https://github.com/tobrien6/voynich-manuscript-research/pull/158)
is a separate exposed-input measurement; its scores are not refitted here.

Reddy–Knight's [paper](https://aclanthology.org/W11-1511.pdf), Section 3.2,
printed page 80, motivates using substitution entropy to consider case.
These original examples do not reproduce its language corpora or refute a
particular reported mapping. They show that a non-case entropy maximizer
does not logically exclude a known case relationship without further
assumptions about the word distributions.

## Reproduction and validation

```sh
PYTHONPATH=tests python3 -m unittest test_known_case_entropy_controls -v
python3 scripts/known_case_entropy_controls.py --check
# Original fixed synthetic inputs only; existing outputs cannot be replaced:
python3 scripts/known_case_entropy_controls.py --output NEW_REPORT.json
cmp NEW_REPORT.json research/literature/known-case-entropy-controls.json
```

The original standard-library producer accepts no corpus input and has no
network or author-code dependency. Python 3.14.3 was used. Four focused tests
pass: lowercasing recovers all base counts, including zero/all-capital boundary
cases; an independent merged-class information formula verifies all six
candidate records under both definitions; all four rankings retain their
known-case outcomes; invalid generation parameters fail. Complete report
replay, producer identity, strict typed JSON, relative links and whitespace
pass. Counts and mass ratios are exact; displayed entropy values are numerical
approximations rounded to twelve decimals.

The examples were constructed after source/method inspection to demonstrate
possible failures. Their frequencies and apparent success/failure counts are
not a sampled distribution, calibrated likelihood or benchmark error rate.
Only original code, synthetic strings/counts and public references are
published; no manuscript or comparator corpus is processed.

A source-linked glyph/case hypothesis therefore needs independent shape,
context or reading predictions and controlled comparisons. A replacement
ranking alone supplies no language, phonetic mapping, case adjudication,
decipherment or translation. The project's
[evaluation protocol](../DECIPHERMENT_PROTOCOL.md) remains necessary for a
proposed decoding rule.
