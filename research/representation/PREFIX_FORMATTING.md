# A reversible row marker creates prefix and length contrasts

A fixed formatting rule can produce a strong first-slot prefix contrast and
a prefix-removal lookup gain while preserving every source token exactly.
This synthetic example tests the interpretation of those measurements. Its
source is an invented vocabulary, with supplied row boundaries; manuscript
bytes, glyphs, images and candidate rules are not inputs.

The [fixed plan](PREFIX_FORMATTING_PLAN.md) was committed at `c327460`, and
the implementation with seven synthetic tests at `a1cb7ae`, before running the
256-row realization. The project’s manuscript prefix observations and earlier
[representation/entropy check](ENTROPY_SANITY.md) were already exposed.

## Source and codec

The vocabulary contains all 64 three-letter strings over `abcd`. The ideal
source ensemble makes independent uniform token choices. One deterministic
SHA-256-counter realization supplies 256 rows of eight tokens each, using the
key recipe and seed in the [complete report](prefix_formatting_demo.json).

Prepend `y` to the first token of every row. Keep the other tokens and all
boundaries unchanged. For example, an invented row beginning `abc, bcd, aaa`
becomes `yabc, bcd, aaa`. Decoding removes exactly that marker and checks every
recovered token against the source vocabulary. The marker is outside the
source alphabet. The codec is bijective on complete matrices with their row
boundaries, and the recorded source and recovered matrix digests agree.

## Measurements

Apply the accepted [boundary-minus-other-token contrast and conditional
variance functions](../../scripts/locus_positions.py), with equal toy-row
weight. The two features are literal y-prefix membership and ASCII token
length. Length and prefix indicators are perfectly linked in this example:
they reflect one formatting operation, rather than independent evidence.

| Matrix | First-slot y contrast | First-slot length contrast | Last-slot y contrast | Last-slot length contrast |
| --- | ---: | ---: | ---: | ---: |
| Original | 0 | 0 | 0 | 0 |
| Marked | +1 | +1 character | -1/7 | -1/7 character |

These effects hold for every source token choice in the declared vocabulary.
The conditional variance of each marked mean is `1/1792` under independent
uniform token assignment within each row. With one marked token among eight,
the observed first-slot contrast +1 occurs only when all 256 markers land in
the first slot. The opposite extreme has magnitude only `1/7`. Thus the exact
two-sided tail for this fixed contrast is **`8^-256 = 2^-768`**. The report
stores a positive rational rather than a float that could underflow to zero.
This probability belongs to the stipulated token-order control, not the
source-generating ensemble or a manuscript hypothesis.

Construct a dictionary once from encoded non-first slots, then reuse it before
and after removing one leading y. In the fixed realization it contains all
64 base types. All 256 original first-slot tokens match. None of the marked
first-slot tokens match; all 256 match after removing the marker. The gain is
**100 percentage points** at first slots and zero at the 1,792 other slots.
Smaller realizations can miss vocabulary entries; the program retains that
coverage and never chooses a dictionary to force a successful gain.

## Information and interpretation

All 2,048 tokens and their order are recovered. Under the ideal independent
uniform source model there are `64^2048` possible complete messages, with
12,288 bits of joint entropy in either representation. The original carrier
has 6,144 ASCII characters; marking adds 256 characters, giving 6,400. The
joint-entropy denominators therefore give 2 bits per original character and
`48/25 = 1.92` bits per encoded character. These are ensemble quantities;
the known seed determines one realization and supplies no stochastic entropy.
No plug-in or finite-context entropy estimate is calculated.

The order test correctly detects a known marker’s positional structure.
The lookup correctly reverses that marker against the unchanged dictionary.
Both observations coexist with an exactly preserved source message and an
independent-token source ensemble. A manuscript interpretation needs additional
predictions that distinguish a formatting/coding convention from other causes.
The illustrative all-first/no-other marker rule has fixed prevalences; it
explains no manuscript prevalence, glyph shape, paragraph annotation, interior
order, language, or translation.

## Reproduce

Standard library only, from the repository root:

```sh
python3 -m unittest tests.test_prefix_formatting_demo -v
python3 scripts/prefix_formatting_demo.py --check research/representation/prefix_formatting_demo.json
python3 scripts/prefix_formatting_demo.py --output /tmp/prefix-formatting-replay.json
```

The report pins its plan, generator, and three implementation files and retains
source/encoded/recovered digests, exact moments/tail, dictionary identity,
denominators and ensemble qualifications. Tests cover exact recovery, invalid
codewords, accepted measurement agreement, exhaustive small assignment tails,
the special two-slot symmetry, dictionary reuse, deterministic generation and
input protection. No original measurement implementation is changed. The next
manuscript step remains a candidate-specific prediction with checked units and
prospective evaluation under the [decipherment protocol](../DECIPHERMENT_PROTOCOL.md).
