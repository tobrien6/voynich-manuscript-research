#!/usr/bin/env python3
"""Create a versioned token-order control without crossing folio-side boundaries."""

import argparse
from collections import Counter, defaultdict
import copy
import hashlib
import json
from pathlib import Path
import re


ALGORITHM = "sha256-counter-fisher-yates-v1"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(corpus):
    require(isinstance(corpus, dict) and type(corpus.get("schema_version")) is int and corpus["schema_version"] == 1,
            "Expected token-line corpus schema_version 1")
    require("control" not in corpus, "Supply the original corpus, not an existing shuffled control")
    require(set(corpus) <= {"schema_version", "corpus_id", "provenance", "lines"},
            "Unexpected corpus fields; do not carry derived results into a shuffled control")
    require(isinstance(corpus.get("corpus_id"), str) and corpus["corpus_id"].strip(), "corpus_id is required")
    provenance = corpus.get("provenance")
    require(isinstance(provenance, dict), "provenance is required")
    require(provenance.get("kind") in ("synthetic", "transcription"), "Record synthetic or transcription provenance")
    require(isinstance(provenance.get("tokenization"), str) and provenance["tokenization"].strip(),
            "Record tokenization and treatment of ambiguity")
    if provenance["kind"] == "synthetic":
        require(isinstance(provenance.get("description"), str) and provenance["description"].strip(),
                "Describe the synthetic fixture")
    else:
        for field in ("source_url", "edition", "version"):
            require(isinstance(provenance.get(field), str) and provenance[field].strip(), f"Record transcription {field}")
        require(isinstance(provenance.get("sha256"), str) and re.fullmatch(r"[0-9a-f]{64}", provenance["sha256"]),
                "Record the exact transcription's lowercase SHA-256")
    lines = corpus.get("lines")
    require(isinstance(lines, list) and lines, "Provide a nonempty lines array")
    seen = set()
    for line in lines:
        require(isinstance(line, dict), "Each line must be an object")
        require(set(line) <= {"folio_side", "line_id", "tokens", "context"},
                "Unexpected line fields; token-aligned annotations require a separate documented adapter")
        for field in ("folio_side", "line_id"):
            require(isinstance(line.get(field), str) and line[field].strip(), f"Each line requires {field}")
            require(line[field] == line[field].strip(), f"Remove surrounding whitespace from {field} explicitly")
        require(re.fullmatch(r"[1-9]\d*[rv]", line["folio_side"]),
                "folio_side requires a canonical number+r/v identifier; resolve panel/alias conventions explicitly")
        require("context" not in line or isinstance(line["context"], str), "Optional context must be immutable line-context text")
        identity = (line["folio_side"], line["line_id"])
        require(identity not in seen, f"Duplicate line identity: {identity}")
        seen.add(identity)
        tokens = line.get("tokens")
        require(isinstance(tokens, list), f"Tokens must be a list at {identity}")
        require(all(isinstance(token, str) and token and not any(c.isspace() for c in token) for token in tokens),
                f"Each token must be a nonempty string without whitespace at {identity}")


class HashDraws:
    """A fixed byte-stream definition with rejection to avoid modulo bias."""

    def __init__(self, key):
        self.key = key
        self.counter = 0

    def below(self, bound):
        require(type(bound) is int and 1 <= bound <= 2 ** 256, "Invalid draw bound")
        width = max(1, ((bound - 1).bit_length() + 7) // 8)
        space = 1 << (8 * width)
        limit = space - space % bound
        while True:
            digest = hashlib.sha256(self.key + self.counter.to_bytes(16, "big")).digest()
            self.counter += 1
            value = int.from_bytes(digest[:width], "big")
            if value < limit:
                return value % bound


def shuffle(values, draws):
    result = list(values)
    for index in range(len(result) - 1, 0, -1):
        other = draws.below(index + 1)
        result[index], result[other] = result[other], result[index]
    return result


def make_control(raw, scope, seed, trial):
    require(scope in ("line", "folio-side"), "Scope must be line or folio-side")
    require(type(seed) is int and seed >= 0 and type(trial) is int and trial >= 0,
            "Seed and trial must be nonnegative integers")
    corpus = json.loads(raw)
    validate(corpus)
    digest = hashlib.sha256(raw).hexdigest()
    result = copy.deepcopy(corpus)
    groups = defaultdict(list)
    for index, line in enumerate(corpus["lines"]):
        unit = (line["folio_side"], line["line_id"]) if scope == "line" else (line["folio_side"],)
        groups[unit].append(index)
    for unit, indices in groups.items():
        parameters = [ALGORITHM, digest, scope, seed, trial, list(unit)]
        encoded = json.dumps(parameters, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        draws = HashDraws(hashlib.sha256(encoded).digest())
        original = [token for index in indices for token in corpus["lines"][index]["tokens"]]
        permuted = shuffle(original, draws)
        require(Counter(original) == Counter(permuted), "Internal error: permutation changed the token multiset")
        offset = 0
        for index in indices:
            count = len(corpus["lines"][index]["tokens"])
            result["lines"][index]["tokens"] = permuted[offset:offset + count]
            offset += count
    result["control"] = {
        "algorithm": ALGORITHM,
        "scope": scope,
        "seed": seed,
        "trial": trial,
        "input_sha256": digest,
        "line_count": len(corpus["lines"]),
        "token_count": sum(len(line["tokens"]) for line in corpus["lines"]),
        "unit_count": len(groups),
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("corpus", type=Path)
    parser.add_argument("--scope", choices=("line", "folio-side"), required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--trial", type=int, required=True)
    parser.add_argument("--expected-sha256")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        require(args.output.resolve() != args.corpus.resolve(), "Control output must not replace its original corpus")
        raw = args.corpus.read_bytes()
        if args.expected_sha256:
            require(hashlib.sha256(raw).hexdigest() == args.expected_sha256.lower(), "Input bytes do not match --expected-sha256")
        result = make_control(raw, args.scope, args.seed, args.trial)
        encoded = (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        args.output.write_bytes(encoded)
    except (ValueError, TypeError, KeyError, OSError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
