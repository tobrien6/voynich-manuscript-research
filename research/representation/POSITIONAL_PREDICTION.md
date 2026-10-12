# A positional carrier can raise bigram accuracy

A known reversible encoding produces a bigram advantage over a position-blind
unigram even though its underlying source letters are independent. A
position-only baseline matches or exceeds the bigram in every declared
treatment. This original synthetic control helps specify a stronger future
predictor comparison; it establishes no manuscript mechanism or reading.

The [published plan](POSITIONAL_PREDICTION_PLAN.md) was committed and pushed at
`4a478e0` before implementation execution. All expected fractions were derived
analytically before that plan; this checks exposed predictions rather than
reporting an unseen outcome. The [complete receipt](positional-prediction-demo.json)
retains all invented source words, shared assignments, fitted counts, thirty-six
fold/model records and eighteen exact aggregate records. The
[producer](../../scripts/positional_prediction_demo.py) uses only the standard
library and makes no network request.

## Population, reversible encoding and exclusions

Enumerate all sixteen words in `{a,b}^4` once. An ideal source choosing uniformly
from this population has four independent fair binary letters. The literal
carrier leaves words unchanged. The alternating carrier uppercases positions
2 and 4: for example, `abba` becomes `aBbA`. Its inverse validates the four
position-specific case/alphabet choices and lowercases them. No symbol is
inserted, removed or merged. This bijection preserves all sixteen complete-word
probabilities under the known inverse.

Assign folds by the parity of the number of `b` letters in each source word.
Use one fold's eight types for training and exclude the other eight types for
scoring, then swap roles. Keep these same source-word assignments in both
representations. The two folds each have four occurrences of each source letter
at every position and two occurrences of each source pair at each adjacent
position. The receipt records these complete low-order marginals.

Conditioning on parity imposes a four-letter constraint in each fold. The folds
are therefore not IID samples, even though the full source distribution is a
product. Their one-letter and adjacent-pair marginals remain balanced. This
small deterministic two-fold design is not the paper's ten-fold procedure,
a random-sample performance estimate or an untouched manuscript evaluation.

## Predictions and every declared result

Count each training word type once. The unigram pools character counts across
positions. The bigram uses the observed preceding character inside the word.
The position-only model predicts from a training count table for that position,
without reading preceding test characters. Every tied maximum chooses the
lowest Unicode codepoint. No model crosses word boundaries or uses a fitted
parameter. The beginning context is separate from the target alphabet.

The table gives pooled correct/scored counts and exact accuracy. Each fold has
the same accuracy, so its equal-weight mean equals the pooled value here; both
aggregations are retained separately in the receipt.

| Treatment | Model | Literal carrier | Alternating carrier |
| --- | --- | ---: | ---: |
| All characters, first unigram backoff | Unigram | 32/64 = 1/2 | 16/64 = 1/4 |
| All characters, first unigram backoff | Bigram | 32/64 = 1/2 | 24/64 = 3/8 |
| All characters, first unigram backoff | Position only | 32/64 = 1/2 | 32/64 = 1/2 |
| All characters, beginning context | Unigram | 32/64 = 1/2 | 16/64 = 1/4 |
| All characters, beginning context | Bigram | 32/64 = 1/2 | 32/64 = 1/2 |
| All characters, beginning context | Position only | 32/64 = 1/2 | 32/64 = 1/2 |
| Non-initial positions | Unigram | 24/48 = 1/2 | 16/48 = 1/3 |
| Non-initial positions | Bigram | 24/48 = 1/2 | 24/48 = 1/2 |
| Non-initial positions | Position only | 24/48 = 1/2 | 24/48 = 1/2 |

All scored decisions have tied training maxima. Primary bigrams have eight
first-position unigram backoffs per fold; other treatments have none. No
internal context is unseen. Non-initial scoring changes the positions and
denominators for every model, while retaining full training counts and folds.

In the alternating carrier, the pooled unigram chooses `A`, so it can be correct
only at positions 2 and 4. There are eight such correct predictions per fold,
giving 8/32 for all characters or 8/24 for non-initial positions. The first
position is lowercase and every primary first-position guess is wrong.
Each internal bigram's predecessor identifies the next letter's case class;
its two underlying-letter choices remain balanced. It gets four correct
predictions at each of the three internal positions, giving 12/32. A beginning
context adds four correct first predictions, giving 16/32. A position-only
table already knows the case class and gets four correct predictions at every
position. The improvement supplies positional-class information without
predicting the next underlying binary letter better than 1/2.

## Relation to manuscript prediction and next test

Reddy and Knight's [paper](https://aclanthology.org/W11-1511.pdf), Section 4.2,
printed page 81, describes most-likely-letter prediction using training word
types and preceding-letter contexts. The project's
[native-input operationalization, PR 147](https://github.com/tobrien6/voynich-manuscript-research/pull/147)
retains explicit first-position choices and a published discrepancy. This toy
example supplies neither its historical method nor an explanation of its
numerical discrepancy. No manuscript input or comparator language is fitted.
The [entropy representation example](ENTROPY_SANITY.md) asks a separate
measurement question; these accuracy fractions are not entropy in bits.

Bigram superiority to a position-blind unigram alone cannot distinguish this
constructed positional carrier from dependence in the underlying letters.
The example does not establish that Voynich notation uses such a carrier or
that any manuscript predictor gain is entirely positional. A later comparison
can predeclare a position-only baseline, comparable word-position/length
support and fallback rules, the same training exclusions, and matched scored
positions before fitting. Preserve unsupported positions and all treatments.
Any decoding claim still requires source-linked glyph units and predictions
under the [evaluation protocol](../DECIPHERMENT_PROTOCOL.md).

## Reproduction and validation

```sh
PYTHONPATH=tests python3 -m unittest test_positional_prediction_demo -v
python3 scripts/positional_prediction_demo.py --check
# Optional full regeneration into a new file:
python3 scripts/positional_prediction_demo.py --output NEW_RECORD.json
cmp NEW_RECORD.json research/representation/positional-prediction-demo.json
```

Python 3.14.3 produced the receipt. Six tests check complete inversion and
invalid carriers, balanced/disjoint parity folds, all predeclared score counts,
exact aggregation, word-local counting, the positional baseline's context
independence, and preservation of existing outputs and aliases. An independent
implementation imported no production functions: integer-bit enumeration and
analytical training tables reproduced all sixteen source words, four fits,
thirty-six complete score records and eighteen exact aggregates. Complete
report replay is byte-identical. The plan and producer hashes are in the receipt.
Only original invented data, code, counts and documentation are published.
