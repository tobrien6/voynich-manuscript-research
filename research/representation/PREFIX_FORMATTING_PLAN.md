# Reversible row-marker demonstration: fixed plan, version 1

Question: can known row formatting alone create literal first-slot prefix and
notation-length contrasts, and a first-slot prefix-removal lookup gain, while
preserving the source message exactly?

This is a synthetic measurement check, separate from manuscript analysis,
greedy wrapping, language comparison, copying models and candidate fitting.
The manuscript prefix results and existing entropy demonstration were already
exposed. No source image, transcription bytes or manuscript split are inputs.

## Source ensemble and fixed realization

The vocabulary is all 64 length-three strings over `abcd`, in lexicographic
order. The ideal source model chooses each token independently and uniformly.
Arrange 256 rows of eight tokens; row boundaries are supplied metadata, not
inferred manuscript lines. The ideal ensemble has `64^(256*8)` messages.

For one reproducible illustration, use the existing SHA-256 counter draw
algorithm, keyed by SHA-256 of ASCII `prefix-formatting-demo-v1:20261012`.
Consume one `below(64)` draw per token in row order. The recorded seed fixes a
deterministic realization; neither that seed nor this single realization is
claimed to have stochastic entropy or to prove empirical independence.

## Contextual codec fixed before execution

Copy every token and prepend literal `y` only to the first token of each row.
The original vocabulary contains no `y`. Decoding requires that marker at the
first slot, removes exactly one character there, and validates every recovered
token against the vocabulary. Preserve row boundaries, all token positions and
token counts. Reject malformed codewords rather than repairing them.

This mapping is bijective on complete row matrices, including their supplied
boundaries. Thus it preserves the ideal complete-message support and joint
entropy. It need not preserve token-type counts or bits per encoded character.
It is an illustrative known codec, not a proposed Voynich glyph reading.

## Measurements and predictions

Use the accepted `locus_positions.contrast` and `conditional_variance` on
literal y indicators and ASCII token lengths, with equal row weights. Retain
both first and last slots. Original tokens have length three and no y prefix;
their two contrasts are zero. Encoding makes both first-slot contrasts +1 and
both last-slot contrasts `-1/7`, irrespective of the generated token choices.

Condition on each encoded row's token multiset and independently assign a
uniform boundary token. Each row contains exactly one y-marked/longer token.
The observed first-slot mean +1 is the maximum. With eight slots, the exact
two-sided tail at that threshold is `(1/8)^256`; the negative extreme has
magnitude only `1/7`. Save this as a positive exact rational, without float
underflow or a Monte Carlo estimate. For a general two-slot synthetic test,
both extremes attain the same absolute threshold and the tail has factor two.
Validate the formula by exhaustive small assignment spaces before the main run.

For the lookup check, form a fixed dictionary from the encoded non-first
slots, preserving the same dictionary before/after removing one leading y.
Report first/other-slot counts, matches and gains for original and encoded
matrices. No dictionary or sample is selected from the gain. First marked
tokens cannot match this dictionary; after removal their matches equal the
original first-token matches. Other slots remain unchanged. Do not require
full vocabulary coverage or a 100% empirical gain from an arbitrary small run.

Record source/encoded/decoded matrix digests, exact recovery, all denominators,
the codec, generator, implementation and plan identities, both boundary
contrasts/conditional variances, lookup counts, and ideal ensemble information
with source-token and ASCII-character denominators kept distinct.

## Interpretation and validation

Round-trip all tokens and rows exactly. Test domain rejection, preserved
boundaries/counts, constant first/last contrasts, exact small tails, dictionary
reuse, deterministic generation, output/input protection and report replay.

Rejecting within-row exchangeability here detects a known formatting marker.
It cannot by itself establish dependencies among source tokens or identify
linguistic content. The marker rule intentionally has fixed first/other-slot
prevalences; it explains no manuscript prevalence, image shape, paragraph
annotation, interior order or decoding mechanism. A manuscript candidate still
needs distinct predictions and prospective evaluation under the existing
[decipherment protocol](../DECIPHERMENT_PROTOCOL.md).
