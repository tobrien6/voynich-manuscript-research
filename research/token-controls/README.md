# Reproducible token-order controls

Question: how can an order or line-position hypothesis be compared with shuffled tokens while preserving its stated sampling units?

The generator creates a documented control from a versioned JSON token-line corpus. This supports the [decipherment evaluation protocol](../DECIPHERMENT_PROTOCOL.md): a candidate's prediction must be compared with a relevant baseline on frozen inputs. The committed corpus and both outputs are **synthetic software fixtures**, with invented tokens and folio-side assignments. They contain no manuscript transcription or measured Voynich result.

## Two controls with different constraints

| Scope | Preserved | Changed by the control | A suitable comparison |
| --- | --- | --- | --- |
| `line` | Each line's eligible token multiset; line/folio-side identities; line lengths and excluded slots | Eligible token order within each line | A within-line order or position statistic, conditional on tokens and exclusions already assigned to each line |
| `folio-side` | Each side's eligible token multiset; line/folio-side identities; line lengths and excluded slots | Order and allocation of eligible tokens to lines within the same side | Line clustering or order statistics, conditional on tokens, line lengths, and exclusions already assigned to each side |

No token crosses a folio-side boundary. Tokens with identical strings retain their multiplicities; empty lines remain empty. A `null` slot marks a position excluded by the documented preprocessing, and stays fixed in both controls. Eligible strings move only among eligible positions. Do not delete excluded slots: that could create a new adjacency across unreadable material. An unchanged permutation is a valid outcome and must not be discarded. The folio-side control can move a token out of a singleton line; the line control keeps it there.

Neither control tests a claim about the distribution of line lengths, because both preserve those lengths. Choose the control from the registered claim, not from which produces a favorable result. A shuffled resemblance or difference does not establish a language, decipherment, or translation.

## Input contract

The top-level fields are exactly the supported schema: `schema_version: 1`, `corpus_id`, `provenance`, and `lines`. Original input bytes are hashed and are never normalized by this tool.

`provenance` requires `kind` (`synthetic` or `transcription`), a nonempty `tokenization` description, and a `unit_definition` explaining what each input row represents. Synthetic input also needs a description. Transcription input requires `source_url`, `edition`, `version`, and the lowercase SHA-256 of the retrieved transcription bytes. That supplied transcription hash is recorded metadata; the generator can check the token-corpus input hash, but cannot verify an external source file it was not given.

Every line has:

- `folio_side`: an explicitly mapped canonical number-plus-`r/v` identifier, such as `70v`. An unresolved alias or panel identifier such as `67r1` requires a reviewed adapter before this input can be built.
- `line_id`: the original line identifier, unique within that side. Neither identifier may have surrounding whitespace.
- `tokens`: a list of slots, each containing an opaque, nonempty string without whitespace or `null` for an excluded position. An empty list is permitted for an empty line. Transcription ambiguity notation may remain inside a string; document its treatment and the reason for exclusions before freezing the corpus.
- Optional `context`: text describing immutable line context, such as an image region. Token-position annotations and derived statistics are not accepted as extra line fields, because copying them after a shuffle would leave stale associations.

The generator treats strings as transcription tokens, not identified manuscript glyphs, linguistic words, or plaintext. It splits no strings and counts no characters. Existing `control` output is rejected as a new source, preventing accidental chained shuffles.

Identifier-format validation does not verify an image crosswalk or establish a physical folio alias. Review source mapping with the [folio alignment utility](../folio-alignment/README.md) before constructing a manuscript input.

An IVTFF locus is not automatically a complete physical line. State whether rows represent loci or reconstructed physical lines, how same-line fragments are handled, and which categories are included. The `line` scope permutes within supplied rows; `line_count` counts those rows. The program does not infer physical boundaries from a record identifier. See the [transliteration decision](../transliteration/DECISION.md) for this distinction.

## Run and reproduce

From the repository root with Python 3:

```sh
python3 scripts/write_token_control.py research/token-controls/synthetic-corpus.json \
  --scope line --seed 1729 --trial 0 --output /tmp/line-control.json
python3 scripts/write_token_control.py research/token-controls/synthetic-corpus.json \
  --scope folio-side --seed 1729 --trial 0 --output /tmp/side-control.json
cmp /tmp/line-control.json research/token-controls/example-line-control.json
cmp /tmp/side-control.json research/token-controls/example-folio-side-control.json
python3 -m unittest discover -s tests -p 'test_token_shuffles.py' -v
python3 -m unittest discover -s tests -p 'test_token_control_writer.py' -v
```

`--seed` and `--trial` are required nonnegative integers. Keep a fixed preregistered seed and use consecutive trial numbers to generate a declared set of controls. Do not choose or exclude trials after inspecting a statistic. Different parameters may still produce the same permutation, especially for short or repeated-token lines.

Add `--expected-sha256 DIGEST` to require the exact token-corpus input bytes. A mismatch fails before writing output. The guarded companion rejects direct, resolved-path, symlink, and existing hardlink aliases of its supplied corpus and writer/generator code, before calculation and again before writing. An ordinary new or existing unrelated output is permitted. Every result retains corpus provenance and includes algorithm version, scope, seed, trial, input hash, and unit/line/eligible-token/slot/exclusion counts. It records no wall-clock value, so the same inputs produce identical bytes. A line with no eligible tokens is retained as a degenerate control; a downstream statistic must handle its denominator explicitly.

The historical `shuffle_token_lines.py` remains byte-identical because accepted
locus-position and greedy-wrapping reports pin its producer hash. Its original
direct CLI checks resolved input/output paths but does not reject hardlinks.
On a disposable synthetic corpus, an output hardlinked to the input returned
success and replaced the input bytes with the control output. Use
`write_token_control.py` for generated writes. Its protection does not change
the historical direct writer or the `make_control` algorithm. No manuscript
source, frozen report, or committed fixture was modified by the reproducer.

Five companion tests exercise actual CLI aliases of copied input and code files,
both direct and package entry points, both committed scope outputs, unrelated
existing output, byte-preserving refusal on invalid/hash-mismatched input, and
a hardlink created during calculation. Temporary fixtures contain no manuscript
text. Both committed outputs reproduce byte-for-byte with the guarded writer.

The Python interface is `make_control(raw_corpus_bytes, scope, seed, trial)`. It returns the control corpus; it does not compute a test statistic, fit a candidate, select a split, or calculate a p-value.

## Fixed permutation algorithm

Python's [random-module reproducibility notes](https://docs.python.org/3/library/random.html#notes-on-reproducibility) distinguish a stable seeded `random()` sequence from other algorithms that may change across versions. This tool specifies its byte stream and swaps directly instead of relying on a runtime's `shuffle()` implementation.

Algorithm ID: `sha256-counter-fisher-yates-v1`.

1. For each sampling unit, serialize the ordered array `[algorithm_id, input_sha256, scope, seed, trial, unit_identifiers]` as UTF-8 JSON with `ensure_ascii=False` and separators `(',', ':')`. Hash those bytes with SHA-256 to obtain a 32-byte key. Unit identifiers are `[folio_side, line_id]` for line scope and `[folio_side]` for side scope.
2. Start a counter at zero. Each draw hashes the key followed by the counter encoded as 16 unsigned big-endian bytes, then increments the counter.
3. For bound `n`, take the first `max(1, ceil(bit_length(n-1)/8))` digest bytes as a big-endian integer. Let `space` be the number of possible integers of that byte width. Reject a value at or above `space - space % n`; otherwise return `value % n`. This avoids unequal residue counts from reducing the entire byte range modulo `n`. It treats hash outputs as pseudorandom draws, rather than claiming a source of true randomness.
4. Pool only eligible strings in input slot order. Starting at the last eligible token and moving down to index 1, swap it with the token at a draw below `index + 1`. Refill only eligible slots, preserving every excluded slot. Side scope pools across the side's lines in input order; line scope handles each line separately.

Each unit has its own keyed stream. Input row order and serialization are part of the pinned input: even a whitespace-only change to the JSON changes the hash and may change all controls. Freeze the corpus bytes, not just a seed.

The implementation checks eligible-token multiset preservation for every shuffled unit. Seven focused tests cover line and side constraints, fixed excluded positions, exact committed-output reproduction, ambiguous/stale input rejection, rejection-draw behavior, and input/output preservation on CLI failure. These validate software behavior, not a manuscript hypothesis.

## Next experiment

After the transcription decision and folio crosswalk are reviewed, create the token corpus with explicit treatment of spaces, uncertain readings, comments, and line categories. Use only the material permitted by the recorded development/evaluation split; generating controls does not establish that a dataset is untouched. Freeze the corpus, statistic, trial range, tail definition, and failure condition before evaluating a candidate. Then report the observed statistic and every declared control result, including contradictory outcomes, and repeat across documented transcription variants.
