"""Exploratory, equal-locus ASCII token-length comparison against token-order nulls.

This is encoding-level analysis, not glyph counting or decipherment validation.
The manuscript adapter is supplied separately; the statistic accepts explicit
token sequences and never tokenizes or modifies a transliteration itself.
"""

from collections import Counter
import json
import math
import re

try:
    from .shuffle_token_lines import HashDraws
except ImportError:
    from shuffle_token_lines import HashDraws


def contrast(lengths):
    if len(lengths) < 2 or any(type(n) is not int or n < 1 for n in lengths):
        raise ValueError("Require at least two positive integer token lengths")
    return lengths[0] - sum(lengths[1:]) / (len(lengths) - 1)


def null_variance(lengths):
    """Finite variance when each token is equally likely to occupy first place."""
    contrast(lengths)
    count, total = len(lengths), sum(lengths)
    return sum(((count * length - total) / (count - 1)) ** 2
               for length in lengths) / count


def uniform_index(count, context, replicate):
    """Use the shared SHA-256 counter stream to select a first-token index."""
    if (type(count) is not int or not 1 <= count <= (1 << 256)
            or type(replicate) is not int or not 0 <= replicate < (1 << 128)):
        raise ValueError("Invalid token count or replicate index")
    key = context + b"\0" + replicate.to_bytes(16, "big")
    return HashDraws(key).below(count)


def quantile(values, probability):
    if not values or not 0 <= probability <= 1:
        raise ValueError("Invalid quantile input")
    values = sorted(values)
    position = probability * (len(values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    fraction = position - lower
    return values[lower] * (1 - fraction) + values[upper] * fraction


def analyze_tokens(tokens_by_locus, source_id, spacing_policy, *, replicates, seed):
    """Analyze a previously fixed cohort, preserving locus and token identities."""
    if (not isinstance(tokens_by_locus, dict) or not tokens_by_locus
            or type(replicates) is not int or replicates < 2):
        raise ValueError("Require a nonempty cohort and at least two null replicates")
    if not all(isinstance(key, str) and key for key in tokens_by_locus):
        raise ValueError("Locus keys must be nonempty strings")
    if not all(isinstance(value, str) and value for value in (source_id, spacing_policy, seed)):
        raise ValueError("Source, policy, and seed must be named")
    rows, token_counts, lengths_histogram = [], Counter(), Counter()
    for key in sorted(tokens_by_locus):
        if not isinstance(key, str) or not key:
            raise ValueError("Locus keys must be nonempty strings")
        tokens = tokens_by_locus[key]
        if (not isinstance(tokens, (list, tuple)) or len(tokens) < 2 or
                any(not isinstance(token, str) or not re.fullmatch(r"[A-Za-z]+", token)
                    for token in tokens)):
            raise ValueError(f"Unsupported encoded token sequence at {key}")
        lengths = [len(token) for token in tokens]
        token_counts.update(tokens)
        lengths_histogram.update(lengths)
        context = json.dumps([seed, source_id, spacing_policy, key],
                             ensure_ascii=True, separators=(",", ":")).encode("ascii")
        n, total = len(lengths), sum(lengths)
        alternatives = [(n * length - total) / (n - 1) for length in lengths]
        rows.append((lengths, alternatives, context))
    count = len(rows)
    observed = sum(contrast(lengths) for lengths, _, _ in rows) / count
    variance = sum(null_variance(lengths) for lengths, _, _ in rows) / count ** 2
    draws = []
    for replicate in range(replicates):
        total = 0.0
        for lengths, alternatives, context in rows:
            n = len(lengths)
            index = uniform_index(n, context, replicate)
            total += alternatives[index]
        draws.append(total / count)
    lower, upper = quantile(draws, 0.025), quantile(draws, 0.975)
    return {
        "source_id": source_id,
        "spacing_policy": spacing_policy,
        "cohort_locus_count": count,
        "encoded_token_count": sum(token_counts.values()),
        "distinct_token_string_count": len(token_counts),
        "hapax_token_string_count": sum(amount == 1 for amount in token_counts.values()),
        "ascii_length_histogram": {str(length): amount for length, amount
                                    in sorted(lengths_histogram.items())},
        "most_frequent_encoded_strings": [{"string": token, "count": amount}
            for token, amount in sorted(token_counts.items(), key=lambda item: (-item[1], item[0]))[:20]],
        "observed_equal_locus_mean_contrast": round(observed, 12),
        "exact_conditional_null_expectation": 0.0,
        "exact_conditional_null_standard_deviation": round(math.sqrt(variance), 12),
        "null_replicates": replicates,
        "null_seed": seed,
        "empirical_null_mean": round(sum(draws) / replicates, 12),
        "conditional_null_draws": [round(value, 12) for value in draws],
        "empirical_null_interval": {"quantiles": [0.025, 0.975],
                                    "lower": round(lower, 12), "upper": round(upper, 12)},
        "observed_outside_conditional_null_interval": observed < lower or observed > upper,
        "interpretation_limit": "Conditioned encoded-token order reference; not a confirmatory p-value or evidence of decipherment",
    }
