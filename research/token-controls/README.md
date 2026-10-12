# Reproducible token-order controls

Question: how can an order or line-position hypothesis be compared with shuffled tokens while preserving its stated sampling units?

The generator creates a documented control from a versioned JSON token-line corpus. This supports the [decipherment evaluation protocol](../DECIPHERMENT_PROTOCOL.md): a candidate's prediction must be compared with a relevant baseline on frozen inputs. The committed corpus and both outputs are **synthetic software fixtures**, with invented tokens and folio-side assignments. They contain no manuscript transcription or measured Voynich result.

## Two controls with different constraints

| Scope | Preserved | Changed by the control | A suitable comparison |
| --- | --- | --- | --- |
| `line` | Each line's complete token multiset; line/folio-side identities; line lengths | Token order within each line | A within-line order or position statistic, conditional on the tokens already assigned to each line |
| `folio-side` | Each side's complete token multiset; line/folio-side identities; line lengths | Order and allocation of tokens to lines within the same side | Line clustering or order statistics, conditional on the tokens and line lengths already assigned to each side |

No token crosses a folio-side boundary. Tokens with identical strings retain their multiplicities; empty lines remain empty. An unchanged permutation is a valid outcome and must not be discarded. The folio-side control can move a token out of a singleton line; the line control keeps it there.

Neither control tests a claim about the distribution of line lengths, because both preserve those lengths. Choose the control from the registered claim, not from which produces a favorable result. A shuffled resemblance or difference does not establish a language, decipherment, or translation.

## Input contract

The top-level fields are exactly the supported schema: `schema_version: 1`, `corpus_id`, `provenance`, and `lines`. Original input bytes are hashed and are never normalized by this tool.

`provenance` requires `kind` (`synthetic` or `transcription`) and a nonempty `tokenization` description. Synthetic input also needs a description. Transcription input requires `source_url`, `edition`, `version`, and the lowercase SHA-256 of the retrieved transcription bytes. That supplied transcription hash is recorded metadata; the generator can check the token-corpus input hash, but cannot verify an external source file it was not given.

Every line has:

- `folio_side`: an explicitly mapped canonical number-plus-`r/v` identifier, such as `70v`. An unresolved alias or panel identifier such as `67r1` requires a reviewed adapter before this input can be built.
- `line_id`: the original line identifier, unique within that side. Neither identifier may have surrounding whitespace.
- `tokens`: a list of opaque, nonempty strings without whitespace. An empty list is permitted for an empty line. Transcription ambiguity notation may remain inside a token; document its treatment before freezing the corpus.
- Optional `context`: text describing immutable line context, such as an image region. Token-position annotations and derived statistics are not accepted as extra line fields, because copying them after a shuffle would leave stale associations.

The generator treats strings as transcription tokens, not identified manuscript glyphs, linguistic words, or plaintext. It splits no strings and counts no characters. Existing `control` output is rejected as a new source, preventing accidental chained shuffles.

Identifier-format validation does not verify an image crosswalk or establish a physical folio alias. Review source mapping with the [folio alignment utility](../folio-alignment/README.md) before constructing a manuscript input.

## Run and reproduce

From the repository root with Python 3:

```sh
python3 scripts/shuffle_token_lines.py research/token-controls/synthetic-corpus.json \
  --scope line --seed 1729 --trial 0 --output /tmp/line-control.json
python3 scripts/shuffle_token_lines.py research/token-controls/synthetic-corpus.json \
  --scope folio-side --seed 1729 --trial 0 --output /tmp/side-control.json
cmp /tmp/line-control.json research/token-controls/example-line-control.json
cmp /tmp/side-control.json research/token-controls/example-folio-side-control.json
python3 -m unittest discover -s tests -p 'test_token_shuffles.py' -v
```

`--seed` and `--trial` are required nonnegative integers. Keep a fixed preregistered seed and use consecutive trial numbers to generate a declared set of controls. Do not choose or exclude trials after inspecting a statistic. Different parameters may still produce the same permutation, especially for short or repeated-token lines.

Add `--expected-sha256 DIGEST` to require the exact token-corpus input bytes. A mismatch fails before writing output. The output path must differ from the source path. Every result retains corpus provenance and includes algorithm version, scope, seed, trial, input hash, and unit/line/token counts. It records no wall-clock value, so the same inputs produce identical bytes.

The Python interface is `make_control(raw_corpus_bytes, scope, seed, trial)`. It returns the control corpus; it does not compute a test statistic, fit a candidate, select a split, or calculate a p-value.

## Fixed permutation algorithm

Python's [random-module reproducibility notes](https://docs.python.org/3/library/random.html#notes-on-reproducibility) distinguish a stable seeded `random()` sequence from other algorithms that may change across versions. This tool specifies its byte stream and swaps directly instead of relying on a runtime's `shuffle()` implementation.

Algorithm ID: `sha256-counter-fisher-yates-v1`.

1. For each sampling unit, serialize the ordered array `[algorithm_id, input_sha256, scope, seed, trial, unit_identifiers]` as UTF-8 JSON with `ensure_ascii=False` and separators `(',', ':')`. Hash those bytes with SHA-256 to obtain a 32-byte key. Unit identifiers are `[folio_side, line_id]` for line scope and `[folio_side]` for side scope.
2. Start a counter at zero. Each draw hashes the key followed by the counter encoded as 16 unsigned big-endian bytes, then increments the counter.
3. For bound `n`, take the first `max(1, ceil(bit_length(n-1)/8))` digest bytes as a big-endian integer. Let `space` be the number of possible integers of that byte width. Reject a value at or above `space - space % n`; otherwise return `value % n`. This avoids unequal residue counts from reducing the entire byte range modulo `n`. It treats hash outputs as pseudorandom draws, rather than claiming a source of true randomness.
4. Starting at the last token and moving down to index 1, swap it with the token at a draw below `index + 1`. For side scope, pool tokens in input line order and then refill the same lines with their original lengths.

Each unit has its own keyed stream. Input row order and serialization are part of the pinned input: even a whitespace-only change to the JSON changes the hash and may change all controls. Freeze the corpus bytes, not just a seed.

The implementation checks token multiset preservation for every shuffled unit. Six focused tests cover line and side constraints, exact committed-output reproduction, ambiguous/stale input rejection, rejection-draw behavior, and input/output preservation on CLI failure. These validate software behavior, not a manuscript hypothesis.

## Next experiment

After the transcription decision and folio crosswalk are reviewed, create the token corpus with explicit treatment of spaces, uncertain readings, comments, and line categories. Use only the material permitted by the recorded development/evaluation split; generating controls does not establish that a dataset is untouched. Freeze the corpus, statistic, trial range, tail definition, and failure condition before evaluating a candidate. Then report the observed statistic and every declared control result, including contradictory outcomes, and repeat across documented transcription variants.
