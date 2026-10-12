"""Literal repeated-type counts and exact whole-stream multiset null means."""

from collections import Counter
from fractions import Fraction
import hashlib
import json
from math import comb
import re

try:
    from .shuffle_token_lines import ALGORITHM, HashDraws, shuffle
except ImportError:
    from shuffle_token_lines import ALGORITHM, HashDraws, shuffle


def validate_tokens(tokens):
    if not isinstance(tokens, (list, tuple)) or any(
            not isinstance(t, str) or not t or any(c.isspace() for c in t) for t in tokens):
        raise ValueError("provide complete nonempty opaque token strings without whitespace")


def counts(tokens):
    validate_tokens(tokens)
    equal = [left for left, right in zip(tokens, tokens[1:]) if left == right]
    repeated = set(equal)
    return {
        "equal_pair_events_A": len(equal), "distinct_repeating_types_B": len(repeated),
        "asterisk_bearing_pair_events": sum("*" in token for token in equal),
        "asterisk_bearing_repeating_types": sum("*" in token for token in repeated),
    }


def exact_means(tokens):
    """Marginal occurrence-position counting; no independence between types."""
    validate_tokens(tokens)
    n = len(tokens)
    classes = Counter(Counter(tokens).values())
    expected_b = Fraction(0)
    forced = 0
    for count, multiplicity in classes.items():
        if count < 2:
            continue
        if count > n - count + 1:
            probability = Fraction(1)
            forced += multiplicity
        else:
            probability = 1 - Fraction(comb(n - count + 1, count), comb(n, count))
        expected_b += multiplicity * probability
    expected_a = Fraction(sum(m * c * (c - 1) for c, m in classes.items()), n) if n else Fraction(0)
    return {
        "A": expected_a, "B": expected_b, "forced_repeating_types": forced,
        "frequency_classes": dict(sorted(classes.items())),
    }


def exact_record(value):
    value = Fraction(value)
    return {"numerator_hex": hex(value.numerator), "denominator_hex": hex(value.denominator),
            "decimal": float(value)}


def ratio(observed, expected):
    return float(Fraction(observed) / expected) if expected else None


def boundary_diagnostics(flat):
    if not isinstance(flat, list) or any(
            not isinstance(row, dict) or not isinstance(row.get("locator"), str)
            or not row["locator"] or type(row.get("original_token_index")) is not int
            or row["original_token_index"] < 0 for row in flat):
        raise ValueError("flat provenance requires native locators and normalized token indices")
    validate_tokens([r.get("token") for r in flat])
    within, joining = set(), set()
    within_events = joining_events = joining_edges = gap_edges = gap_events = 0
    for left, right in zip(flat, flat[1:]):
        same_record = left["locator"] == right["locator"]
        equal = left["token"] == right["token"]
        if same_record:
            if right["original_token_index"] <= left["original_token_index"]:
                raise ValueError("within-record normalized indices must increase")
            gap = right["original_token_index"] > left["original_token_index"] + 1
            gap_edges += gap
            gap_events += gap and equal
            if equal:
                within_events += 1
                within.add(left["token"])
        else:
            joining_edges += 1
            if equal:
                joining_events += 1
                joining.add(left["token"])
    return {
        "all_adjacent_edges": max(0, len(flat) - 1),
        "cross_record_joining_edges": joining_edges,
        "within_record_pair_events": within_events, "cross_record_pair_events": joining_events,
        "within_record_repeating_types": len(within), "cross_record_repeating_types": len(joining),
        "types_repeating_in_both_scopes": len(within & joining),
        "within_record_pre_manual_index_gap_edges": gap_edges,
        "equal_pair_events_on_index_gap_edges": gap_events,
    }


def whole_text_control(tokens, corpus_digest, ring_policy, column_unit, seed, trial):
    validate_tokens(tokens)
    if not isinstance(corpus_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", corpus_digest):
        raise ValueError("provide the pinned flat-corpus digest")
    if type(seed) is not int or seed < 0 or type(trial) is not int or trial < 0:
        raise ValueError("seed and trial must be nonnegative integers")
    frame = [ALGORITHM, corpus_digest, "historical-whole-text-v1", seed, trial,
             [ring_policy, column_unit]]
    key = hashlib.sha256(json.dumps(frame, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).digest()
    result = shuffle(tokens, HashDraws(key))
    if Counter(result) != Counter(tokens):
        raise ValueError("global control changed the token multiset")
    return result
