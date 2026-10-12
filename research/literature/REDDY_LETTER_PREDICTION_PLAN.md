# An explicit operationalization of the letter-prediction comparison

The [recovered input audit](REDDY_SOURCE_INTAKE.md) supplies a later
author-associated VMS B candidate matching reported population counts.
The original Table 2 predictor, fold assignments and preprocessing remain
unrecovered. This study freezes one explicit implementation and three boundary
treatments before new accuracy calculations. It is not authenticated historical
replication, a manuscript-wide split, or a registered decoding hypothesis.

## Source and development exposure

Use only `data/voy.b.paged.wds` at author repository commit
`643b881b2937bae8193814d8ff5d6e99a48bf7c5`, exactly 95,465 bytes and SHA-256
`723cb2746da37c8272005f71298917abfed60412b23597b2b8aecb95dc7a0ee4`.
Verify that pin before decoding UTF-8 and splitting on whitespace, following
the recovered constructor's token rule. Preserve case, asterisks and all
other source characters. Use all 3,920 distinct native token types; do not
weight training words by their 17,597 occurrence frequencies.

The primary [paper](https://aclanthology.org/W11-1511.pdf), Section 4.2 and
Table 2, printed page 81, defines most-likely-letter prediction from training
word types and averages accuracy over ten-fold cross-validation. It reports
14.65% unigram and 40.02% bigram accuracy for VMS B. Its stated description
does not resolve every first-position, tie, unseen-context or aggregation
choice. The publication, source association/population audit and these
reported numbers are already exposed; later token inspection and fold
construction must also be disclosed. No comparator-language file is selected.

## Frozen folds before fitting

Hash each distinct word's UTF-8 bytes with SHA-256. Sort the unique word types
by that digest, rejecting collisions, and distribute consecutive entries
round-robin over folds 0–9. This yields 392 held-out types per fold. The
non-test nine folds are training types. Publish a manifest of word hashes,
native character lengths and fold indices, without copying the raw word list.
Commit that manifest before fitting or calculating any prediction accuracy.
Use the same manifest for every treatment and both models.

## Models and three fixed first-position treatments

Train unigrams by counting every native notation character in each training
word type once. Train bigrams from observed adjacent characters inside each
training word; never concatenate words or cross a word boundary. Predict the
highest-count target character, with the lowest Unicode codepoint resolving
all ties. A bigram context absent in training backs off to the training
unigram prediction. Contexts in test words are observed characters, not the
model's previous predictions. No smoothing or fitted parameter is introduced.

1. **Primary, all characters with first-position unigram backoff:** score every
   test character; the first has no preceding character and uses the unigram
   prediction for both models.
2. **All characters with beginning-of-word context:** add a non-character
   beginning sentinel to bigram training/test context for first characters.
   Keep unigram training and all-character denominators unchanged.
3. **Matched non-initial positions:** score positions after the first for both
   models, using the same training unigram/internal-bigram tables. Retain
   one-character held-out words as explicit zero-scored types for this
   treatment, rather than changing the folds or pretending they were scored.

For each fold/model/treatment record correct predictions, scored characters,
held-out type counts, zero-scored type counts, ties and backoffs. Report the
unweighted arithmetic mean of the ten per-fold accuracies, and separately
the pooled character accuracy with its denominator. Preserve exact rational
values and display percentages. These two aggregations are not interchangeable.

## Comparisons and interpretation

Report all six model/treatment results and differences from the two published
values. Agreement is descriptive: do not select a treatment by proximity or
call matching accuracy proof of the original procedure. A discrepancy must
remain visible, not trigger outcome-dependent normalization or fold changes.
No statistical significance, entropy in bits, confidence interval, language,
phonetic mapping, cipher, plaintext or translation is inferred from accuracy.

Word types are model-training exclusions, not untouched physical folios.
Morphologically related types can share notation sequences across folds, and
the input/measurements are already exposed. Raw corpus, author code and PDF
stay local; only original code, hashes, counts, plans and results are published.
A stronger decipherment evaluation needs independently specified units,
source/glyph review, prior-exposure declarations and the project's
[evaluation protocol](../DECIPHERMENT_PROTOCOL.md).
