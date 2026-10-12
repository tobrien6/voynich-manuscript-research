"""A synthetic, reversible encoding check for entropy measurement units.

This uses no manuscript data and proposes no Voynich glyph mapping. The seeded
shuffle is one realization; the combinatorial support size describes an ideal
uniform ensemble, not the entropy of a known seed or a deterministic output.
"""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import platform
import random


SYMBOLS = ("A", "B", "C", "D")
PLAIN = dict(zip(SYMBOLS, "abcd"))
ESCAPED = dict(zip(SYMBOLS, ("@128;", "@129;", "@130;", "@131;")))


def empirical_entropy(sequence, order=0):
    """Plugin conditional entropy in bits per next unit, with stated context."""
    if type(order) is not int or order < 0:
        raise ValueError("context order must be a nonnegative integer")
    if len(sequence) <= order:
        raise ValueError("sequence has no scored unit at this context order")
    joint = Counter((tuple(sequence[index - order:index]), sequence[index])
                    for index in range(order, len(sequence)))
    contexts = Counter()
    for (context, _), count in joint.items():
        contexts[context] += count
    denominator = len(sequence) - order
    return -sum(count / denominator * math.log2(count / contexts[context])
                for (context, _), count in joint.items())


def encode(sequence, mapping):
    return "".join(mapping[symbol] for symbol in sequence)


def decode_fixed_width(text, mapping):
    widths = {len(value) for value in mapping.values()}
    if len(widths) != 1 or len(set(mapping.values())) != len(mapping):
        raise ValueError("decoder requires a fixed-width one-to-one map")
    width = next(iter(widths))
    if not width or len(text) % width:
        raise ValueError("encoded length is not a whole number of codewords")
    reverse = {value: key for key, value in mapping.items()}
    try:
        return [reverse[text[index:index + width]] for index in range(0, len(text), width)]
    except KeyError as error:
        raise ValueError("unknown codeword") from error


def make_report(count_per_symbol=1024, seed=20261011):
    if type(count_per_symbol) is not int or count_per_symbol < 1:
        raise ValueError("count per symbol must be a positive integer")
    if type(seed) is not int:
        raise ValueError("a recorded integer seed is required for a reproducible realization")
    symbols = [symbol for symbol in SYMBOLS for _ in range(count_per_symbol)]
    random.Random(seed).shuffle(symbols)
    total = len(symbols)
    support_size, remaining = 1, total
    for _ in SYMBOLS:
        support_size *= math.comb(remaining, count_per_symbol)
        remaining -= count_per_symbol
    log2_support = math.log2(support_size)
    representations = []
    for name, mapping in (("single_ascii", PLAIN), ("escaped_ascii", ESCAPED)):
        carrier = encode(symbols, mapping)
        recovered = decode_fixed_width(carrier, mapping)
        if recovered != symbols:
            raise ValueError("encoding failed the exact round-trip check")
        representations.append({
            "name": name, "mapping": mapping, "round_trip_verified": True,
            "ascii_character_count": len(carrier), "characters_per_symbol": len(carrier) / len(symbols),
            "serialized_sha256": hashlib.sha256(carrier.encode("ascii")).hexdigest(),
            "ideal_uniform_block_bits_per_original_symbol": round(log2_support / total, 12),
            "ideal_uniform_block_bits_per_ascii_character": round(log2_support / len(carrier), 12),
            "empirical_bits_per_ascii_character": {
                str(order): round(empirical_entropy(carrier, order), 12) for order in (0, 1, 2)
            },
            "decoded_bits_per_symbol": {
                str(order): round(empirical_entropy(recovered, order), 12) for order in (0, 1, 2)
            },
        })
    return {
        "schema_version": 1,
        "scope": "Synthetic measurement-unit sanity check; no manuscript observations or glyph mapping",
        "generator": {"method": "seeded shuffle of a fixed balanced multiset", "seed": seed,
                      "count_per_symbol": count_per_symbol, "symbol_count": total,
                      "python": platform.python_version()},
        "source_sequence_sha256": hashlib.sha256("".join(symbols).encode("ascii")).hexdigest(),
        "log2_distinct_balanced_sequences": round(log2_support, 10),
        "support_interpretation": "If chosen uniformly from all distinct balanced sequences, this is the ensemble entropy in bits; conditioning on the recorded seed makes this realization deterministic.",
        "atomic_empirical_bits_per_symbol": {
            str(order): round(empirical_entropy(symbols, order), 12) for order in (0, 1, 2)
        },
        "representations": representations,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    report = make_report()
    if args.check:
        if report != json.loads(args.check.read_text()):
            parser.exit(1, "Synthetic report differs; check the recorded interpreter and method before updating it.\n")
        print("Synthetic encodings round-trip and the entropy report reproduces.")
    elif args.output:
        args.output.write_text(json.dumps(report, indent=2) + "\n")
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
