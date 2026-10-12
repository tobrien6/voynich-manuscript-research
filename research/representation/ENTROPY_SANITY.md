# Entropy measurements depend on the representation and unit

This synthetic check supports the project's requirement to define transcription
units before measuring glyph or character entropy. It uses invented symbols and
known reversible encodings. It establishes no manuscript statistic or glyph map.

The separate [finite-edge accounting check](ENTROPY_EDGES.md) holds atomic
units fixed and compares marginal counting populations. Together the two
examples distinguish representation effects from finite-boundary estimator
differences; neither is a manuscript entropy result.

## Method fixed by the example

Create 1,024 instances of each atomic label A, B, C, and D. Shuffle that balanced
multiset with seed 20261011. Represent the same 4,096-label sequence in two ways:

| Atomic label | Single-character carrier | Five-character escape carrier |
| --- | --- | --- |
| A | a | @128; |
| B | b | @129; |
| C | c | @130; |
| D | d | @131; |

Both dictionaries are one-to-one and fixed width, so decoding is unambiguous.
The escape shape is taken from the [IVTFF format specification](https://voynich.nu/software/ivtt/IVTFF_format.pdf),
section 6.6: an extended character code occupies five ASCII characters. These toy
code assignments identify invented labels; they are not Voynich glyph readings.

Compute empirical conditional entropy for context orders 0, 1, and 2. The
scored unit is the **next element of the supplied sequence**, and the context
contains the preceding `m` elements. For order `m`, score `N - m` positions:

```text
H_m = -sum over (context, next):
      count(context, next) / (N - m)
      * log2(count(context, next) / count(context))
```

For `m = 0`, the context is empty and this is the ordinary empirical frequency
entropy. The estimator is unsmoothed and has finite-sample bias. It is not a
language classifier or an estimate of recoverable plaintext.
H1 and H2 here are finite-context empirical estimates, not general entropy-rate
estimates. This finite balanced sequence also has a fixed-count constraint.

## Result of the fixed realization

The exact report, dictionaries, interpreter, seed, and sequence digests are in
[entropy_sanity.json](entropy_sanity.json).

| Representation supplied to estimator | Sequence length | H0 | H1 | H2 |
| --- | ---: | ---: | ---: | ---: |
| Atomic labels | 4,096 labels | 2.000000 | 1.999450 | 1.991383 |
| Single-character carrier | 4,096 ASCII characters | 2.000000 | 1.999450 | 1.991383 |
| Escape carrier | 20,480 ASCII characters | 2.741446 | 0.580510 | 0.400039 |

The first row's units are bits per next **label**. The carrier rows' units are
bits per next **ASCII character**. Context orders also refer to those different
units. Adding predictable characters to the escape carrier raises its H0 while
lowering its short-context conditional entropies. The underlying label sequence
is unchanged.

Decode either carrier and recompute the label-unit estimates: all three values
return exactly to the atomic row. This is verified by round-trip and entropy
checks. Multiplying a character entropy by the expansion factor alone is not a
general fix, because two characters of history and two labels of history are
different contexts. Define equivalent units and contexts before comparing.

There are `4096! / (1024!)^4` distinct balanced label sequences. Both reversible
carriers represent exactly the same number of possible messages; its base-2
logarithm is **8,174.0223155302 bits**. If an ideal source chooses uniformly from
that set, this is the ensemble entropy of its full sequence. The recorded seed
selects one reproducible, deterministic realization; the support calculation
does not claim entropy in a known seed or in that fixed output.

Under that ideal uniform block model, the block entropy per original label is
the same for both encodings. Dividing it by the encoded character count changes
the denominator by five in the escape carrier. The report records both values
separately from the empirical H0/H1/H2 estimates. For any distribution over
complete label sequences, a bijection preserves each complete message's
probability and hence its joint entropy; a plug-in H1 comparison is not the
argument for this preservation.

## Consequence for manuscript work

Every entropy result should identify the transcription edition, preprocessing,
atomic unit, context definition/order, sample selection, and denominator. Literal
ASCII codes, extended-code atoms, native notation units, and proposed manuscript
glyph units answer different questions. The [input decision](../transliteration/DECISION.md)
and [comparator audit](../transliteration/COMPARATORS.md) preserve the relevant
representation differences.

This example demonstrates a measurement effect of a **known** representation.
It does not select a Voynich segmentation, prove a natural-language or cipher
mechanism, or explain a published manuscript entropy value. A later corpus
comparison needs a sourced unit definition and controls encoded with comparable
rules. Preserve uncertainty and distinguish a representation effect from a
candidate-specific prediction under the [evaluation protocol](../DECIPHERMENT_PROTOCOL.md).

## Reproduce and validate

The [reversible row-marker demonstration](PREFIX_FORMATTING.md) supplies a
separate synthetic check of prefix/length contrasts and prefix-removal lookup
gains. It preserves a complete source matrix while adding known positional
formatting; its ideal source model and conditional control remain distinct.

Python 3.14.3 was used for the committed realization; standard library only:

```sh
python3 scripts/representation_entropy_demo.py --check research/representation/entropy_sanity.json
python3 -m unittest tests.test_representation_entropy_demo -v
```

To write a separate replay, use `--output /tmp/entropy-sanity.json`. Check mode
requires the recorded interpreter, digests, and numeric report to agree; inspect
runtime changes before updating a result. The seed and generator are specified,
but random-library or floating-point changes can affect exact report replay.

Tests cover hand-calculated H0 values, deterministic transition contexts, a
nontrivial H1 denominator, exact reversible recovery, invariant decoded estimates,
the four-symbol support count, and rejection of partial/non-bijective maps or
undefined context measurements.
