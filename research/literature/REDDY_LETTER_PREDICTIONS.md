# Native word-type letter prediction: three frozen boundary choices

Question: what does an explicit implementation of Reddy–Knight's letter
prediction comparison produce on the recovered B input, and how much do three
specified first-position choices change the result?

The primary [publication](https://aclanthology.org/W11-1511.pdf), Section 4.2
and Table 2, printed page 81, reports 14.65% unigram and 40.02% bigram
accuracy averaged over ten folds. The [source intake](REDDY_SOURCE_INTAKE.md)
recovered a later author-associated input with matching population counts,
but no original predictor or fold assignments. This contribution implements
the [committed plan](REDDY_LETTER_PREDICTION_PLAN.md), rather than claiming to
have recovered the historical procedure. The discrepancy remains in the
[complete result](reddy-letter-predictions.json).

## Input, folds and exposure

Use `data/voy.b.paged.wds` from `sravanareddy/deciphervoynich` commit
`643b881b2937bae8193814d8ff5d6e99a48bf7c5`: 95,465 bytes, SHA-256
`723cb2746da37c8272005f71298917abfed60412b23597b2b8aecb95dc7a0ee4`.
Whitespace splitting retains all 17,597 token occurrences and 3,920 distinct
types, including case, asterisks and the 35 native notation characters.
Training counts each distinct training type once; occurrence frequencies do
not weight the model. Characters are notation codepoints, not image-adjudicated
glyphs, and native word types are not validated lexical words.

The plan was committed in `ac133c0`. The original producer and
[hash/length/fold manifest](reddy-letter-folds.json) were committed in
`262fda0103a55f52f03005871b242ca33dc2f99c` before fitting the source input or
calculating its accuracies. Synthetic tests preceded that fit. All 3,920 unique
type hashes are assigned once, with 392 test types and 3,528 training types in
each of ten folds. The manifest pins the plan and producer; evaluation rejects
any changed assignment or identity. No type occurs in both training and test
within a fold.

The publication's values and recovered input counts were exposed before the
plan. Token inspection, fold construction and the complete input's results
are now exposed as well. These type exclusions are cross-validation of a
predictor on this input, not untouched physical folios or an exposure-valid
decipherment test. The native historical input and the separate modern-source
[grouped predictor proposal](https://github.com/tobrien6/voynich-manuscript-research/pull/123) have different
units, folds and preprocessing; their numerical scores are not interchangeable.

## All declared treatments

The unigram chooses the most frequent training character. The bigram chooses
the most frequent successor to the observed preceding test character,
without crossing word boundaries. Ties choose the lowest Unicode codepoint;
unseen contexts use the unigram. The beginning treatment adds a context
sentinel, never a predicted character. The non-initial treatment scores the
same positions for both models. These choices were fixed before the input fit.

| Boundary treatment | Model | Mean fold accuracy % | Pooled accuracy % | Pooled correct / scored | Mean minus published, percentage points |
| --- | --- | ---: | ---: | ---: | ---: |
| All characters, first unigram backoff (primary) | Unigram | 14.55555096 | 14.55623012 | 3,021 / 20,754 | −0.09444904 |
| All characters, first unigram backoff (primary) | Bigram | 29.17797401 | 29.17991712 | 6,056 / 20,754 | −10.84202599 |
| All characters, beginning context | Unigram | 14.55555096 | 14.55623012 | 3,021 / 20,754 | −0.09444904 |
| All characters, beginning context | Bigram | 32.96280659 | 32.96232052 | 6,841 / 20,754 | −7.05719341 |
| Matched non-initial positions | Unigram | 17.72405502 | 17.72603065 | 2,984 / 16,834 | +3.07405502 |
| Matched non-initial positions | Bigram | 35.75239389 | 35.75501960 | 6,019 / 16,834 | −4.26760611 |

Mean fold accuracy gives each fold equal weight; pooled accuracy gives each
scored character equal weight. Their exact rational values and all 60
fold/model records are retained. No fold is undefined. The non-initial
treatment retains all types in the manifest and explicitly records 17
one-character test types with zero scored positions. Removing first positions
changes both numerator and denominator; its higher percentage is not a
like-for-like gain over the primary all-character score.

Across folds, every bigram treatment has 18 tied-maximum decisions. There is
one unseen internal context. The primary treatment additionally records 3,920
first-position unigram backoffs, for 3,921 total; the beginning and non-initial
treatments each have one. Unigrams have no tied decisions or backoffs.

Every declared bigram result is below the published 40.02%. Beginning context
raises the all-character score, but none of these treatments recovers that
number. The primary unigram is close to, but differs from, 14.65%. Neither
proximity nor discrepancy establishes the original 2011 procedure. No further
normalization, seed search or choice of a nearest treatment follows this run.

## Reproduction and validation

Obtain the single pinned input locally with its native relative path; the
[intake manifest](reddy-source-manifest.json) records its upstream location.
The predictor makes no network request and verifies the exact input size and
hash before parsing. Existing outputs, including symlink and hardlink aliases,
are rejected rather than overwritten.

```sh
PYTHONPATH=tests python3 -m unittest test_reddy_letter_predictions -v
# Replay against the committed manifest into a new file:
python3 scripts/reddy_letter_predictions.py evaluate \
  --input LOCAL_REFERENCE/data/voy.b.paged.wds --output NEW_RESULT.json
cmp NEW_RESULT.json research/literature/reddy-letter-predictions.json
# Optional fold reconstruction into a separate new file:
python3 scripts/reddy_letter_predictions.py folds \
  --input LOCAL_REFERENCE/data/voy.b.paged.wds --output NEW_FOLDS.json
cmp NEW_FOLDS.json research/literature/reddy-letter-folds.json
```

Python 3.14.3 produced the result using only the standard library. Eight
synthetic tests cover disjoint balanced folds, within-word training, sentinel
handling, ties, unseen-context fallback, observed rather than predicted test
contexts, first-position denominators, exact aggregation, changed manifest
rejection and input preservation through existing output aliases. A separate implementation, importing no production predictor,
reconstructed the folds and all 60 correct/scored/tie/backoff/type records
from local bytes, and verified all six exact aggregate pairs and differences.
A second complete run reproduced the report bytes. Plan, producer and manifest
bytes agree with the pre-fit commit. Raw words, author code and PDF remain
local; this PR publishes original code and metadata only.

## Implication for decoding and the next test

This supplies a replayable notation-level prediction baseline and documents
an unresolved published comparison. It identifies neither plaintext nor a
language, cipher, phonetic value, physical glyph mapping or translation.
Accuracy is not entropy in bits. Closely related types can share substrings
across folds, and no comparator-language corpus was evaluated.

The next historical task is to recover the actual predictor, fold procedure
and preprocessing before assigning an explanation to the discrepancy. A
separate comparison on modern or independently reviewed glyph units must
freeze those units and exposure first. A decipherment candidate still needs
source-linked rules, predictions and validation under the project's
[evaluation protocol](../DECIPHERMENT_PROTOCOL.md).
