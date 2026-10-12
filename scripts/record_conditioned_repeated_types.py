"""Exact all-flat-edge repeat means under independent native-record bag shuffles."""

from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from math import comb
import re

try:
    from .global_repeated_types import validate_tokens
    from .shuffle_token_lines import ALGORITHM, HashDraws, shuffle
except ImportError:
    from global_repeated_types import validate_tokens
    from shuffle_token_lines import ALGORITHM, HashDraws, shuffle


def validate_rows(rows):
    if not isinstance(rows, (list, tuple)):
        raise ValueError("provide a sequence of native-record token sequences")
    for row in rows:
        validate_tokens(row)


def choose(n, k):
    return comb(n, k) if 0 <= k <= n else 0


@lru_cache(maxsize=4096, typed=True)
def endpoint_matrix(m, c):
    """Joint no-internal-repeat/end-occupancy probabilities for one type."""
    if type(m) is not int or type(c) is not int or m < 1 or not 0 <= c <= m:
        raise ValueError("endpoint matrices require integer m>=1 and 0<=c<=m")
    if m == 1:
        return ((Fraction(c == 0), Fraction(0)), (Fraction(0), Fraction(c == 1)))
    denominator = comb(m, c)
    return tuple(tuple(Fraction(choose(m - c - 1, c - a - b), denominator)
                       for b in (0, 1)) for a in (0, 1))


@lru_cache(maxsize=8192)
def run_no_repeat(run):
    """Consecutive nonempty records containing the type; joining edges included."""
    previous = (Fraction(1), Fraction(0))
    for m, c in run:
        matrix = endpoint_matrix(m, c)
        previous = tuple(sum(previous[s] * matrix[a][b]
                             for s in (0, 1) for a in (0, 1) if not (s == a == 1))
                         for b in (0, 1))
        if not any(previous):
            return Fraction(0)
    return sum(previous, Fraction(0))


def exact_record_means(rows):
    validate_rows(rows)
    nonempty = [Counter(row) for row in rows if row]
    lengths = [sum(bag.values()) for bag in nonempty]
    expected_internal = sum((Fraction(sum(c * (c - 1) for c in bag.values()), m)
                             for bag, m in zip(nonempty, lengths)), Fraction(0))
    expected_joining = sum((Fraction(sum(c * right.get(t, 0) for t, c in left.items()), ml * mr)
                            for left, right, ml, mr in zip(nonempty, nonempty[1:], lengths, lengths[1:])),
                           Fraction(0))
    occurrences = defaultdict(list)
    for index, (bag, m) in enumerate(zip(nonempty, lengths)):
        for token, c in bag.items():
            occurrences[token].append((index, m, c))
    expected_b = Fraction(0)
    forced = 0
    for entries in occurrences.values():
        no_repeat = Fraction(1)
        run = []
        last_index = -2
        for index, m, c in entries:
            if index != last_index + 1 and run:
                no_repeat *= run_no_repeat(tuple(run))
                run = []
            run.append((m, c))
            last_index = index
        no_repeat *= run_no_repeat(tuple(run))
        expected_b += 1 - no_repeat
        forced += no_repeat == 0
    return {"A": expected_internal + expected_joining, "B": expected_b,
            "A_within_record": expected_internal, "A_cross_record": expected_joining,
            "forced_repeating_types": forced, "nonempty_records": len(nonempty),
            "type_record_incidence": sum(len(v) for v in occurrences.values())}


def record_controls(rows, locators, corpus_digest, ring_policy, column_unit, seed, trial):
    validate_rows(rows)
    if (not isinstance(locators, (list, tuple)) or len(locators) != len(rows)
            or any(not isinstance(v, str) or not v for v in locators)
            or len(set(locators)) != len(locators)):
        raise ValueError("provide one unique native locator per record")
    if not isinstance(corpus_digest, str) or not re.fullmatch(r"[0-9a-f]{64}", corpus_digest):
        raise ValueError("provide the pinned record-corpus digest")
    if type(seed) is not int or seed < 0 or type(trial) is not int or trial < 0:
        raise ValueError("seed and trial must be nonnegative integers")
    output = []
    for tokens, locator in zip(rows, locators, strict=True):
        frame = [ALGORITHM, corpus_digest, "historical-native-record-v1", seed, trial,
                 [ring_policy, column_unit], locator]
        key = hashlib.sha256(json.dumps(frame, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).digest()
        control = shuffle(tokens, HashDraws(key))
        if len(control) != len(tokens) or Counter(control) != Counter(tokens):
            raise ValueError("record control changed a retained record length or token bag")
        output.append(control)
    if Counter(t for row in output for t in row) != Counter(t for row in rows for t in row):
        raise ValueError("record controls changed the complete token bag")
    return output
