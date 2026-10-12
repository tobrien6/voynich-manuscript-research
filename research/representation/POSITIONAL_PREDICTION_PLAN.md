# A fixed positional encoding control for letter prediction

Question: can a known reversible positional encoding raise a within-word
bigram's accuracy over a position-blind unigram when the underlying source
has independent letters? Compare a position-only predictor to distinguish
this constructed effect from information supplied by a preceding source letter.

This is an original exhaustive synthetic example. Its expected results below
were derived analytically before this plan, and the complete example is exposed.
Publishing the plan before executing the implementation records the calculation
choices; it does not make the expected result an unseen discovery. No manuscript
input, historical author code or comparator-language corpus is used.

## Fixed population and the two training exclusions

The ideal source chooses each of the sixteen four-letter words in `{a,b}^4`
with equal probability. Its four letters are independent fair binary choices.
The finite example enumerates every word once, without occurrence weighting.
Assign a word to fold `count(b) mod 2`. In each of two evaluations, exclude one
fold's eight types from training and score those eight types once. Preserve this
same underlying-word assignment in both representations; never repartition by
the encoded word's digest or choose a favorable split.

Conditioning on either parity introduces a four-letter constraint. Therefore
each training/test fold is not an IID sample, despite the full population's
product distribution. Every one-letter and adjacent two-letter marginal in
either fold is exactly balanced; verify this directly. This deliberately small
balanced split is not the historical paper's ten-fold procedure or an untouched
physical-manuscript split.

## Two reversible representations

1. Literal: leave every `a` or `b` unchanged.
2. Alternating case: leave one-based positions 1 and 3 lowercase, and uppercase
   positions 2 and 4. Decode by lowercasing after validating length four and the
   declared case/alphabet at each position. No symbol is inserted or removed.

The alternating carrier's previous character identifies the next position's
case class. It does not reveal the next underlying fair binary letter. The
encoding is a bijection on this sixteen-word population and preserves the
complete-word probability distribution under the known inverse.

## Fixed predictors, treatments and denominators

Train each word type once. The unigram counts all training characters together.
The bigram counts only adjacent within-word pairs, and uses the observed
preceding test character, never its own prior guess. The position-only predictor
counts training characters separately at each one-based position and does not
read preceding test characters. All winners choose the highest count, breaking
ties by the lowest Unicode codepoint. No smoothing or fitted parameter is used.

Keep all three first-position choices explicit:

- Primary: score all characters; the bigram's first position uses the unigram.
- Beginning context: train a separate non-character beginning context and score
  all characters. The sentinel is neither a scored target nor a unigram member.
- Non-initial: score only positions 2 through 4 for every predictor, retaining
  the same full training counts and the same excluded types.

An absent bigram context would back off to the unigram and must be counted.
For each representation, treatment, model and fold, retain training/test types,
correct/scored counts, ties, backoffs and exact rational accuracy. Retain the
equal-weight mean of the two fold accuracies separately from pooled accuracy.
Publish all thirty-six fold/model records and eighteen aggregate model records.

## Analytically specified expected results and next use

Literal unigrams, bigrams and position-only predictors all score exactly 1/2
in every treatment. In the alternating carrier, unigram accuracy is 1/4 for
all-character treatments and 1/3 for the non-initial treatment. Bigram accuracy
is 3/8 with first-position unigram backoff and 1/2 with either beginning context
or non-initial scoring. The position-only predictor is always 1/2. Per fold,
all-character and non-initial denominators are respectively 32 and 24.
Check every count and exact fraction against those expectations; preserve any
disagreement instead of changing the population, split or encoding.

Reddy and Knight's [paper](https://aclanthology.org/W11-1511.pdf), Section 4.2,
printed page 81, describes within-word letter prediction from training word
types. The separate [native-input operationalization, PR 147](https://github.com/tobrien6/voynich-manuscript-research/pull/147)
retains three explicit first-position choices and an unresolved published
discrepancy. This toy control neither explains that discrepancy nor recovers
the historical predictor. It complements the existing
[entropy representation control](ENTROPY_SANITY.md), using prediction accuracy
and an explicit position-only comparator rather than entropy estimates.

The next manuscript comparison could freeze a position-only baseline on the
same units, excluded groups and scored positions before fitting. That would
test an additional alternative explanation, without assigning a language,
cipher, glyph map, plaintext or translation to predictive accuracy. Follow the
[evaluation protocol](../DECIPHERMENT_PROTOCOL.md) for any decoding claim.
