"""Exact moments of equal-pair counts under a uniform token-bag permutation."""

from collections import Counter
from fractions import Fraction


def falling(number, order):
    result = 1
    for offset in range(order):
        result *= number - offset
    return result if number >= order else 0


def conditional_moments(values, edges):
    """Return exact mean/variance for a simple graph on retained token positions.

    Edges should come from a documented adjacency rule. Excluded original slots
    are represented by absent edges, not by missing values becoming adjacent.
    Values are eligible opaque representations, not decoded words or glyphs.
    """
    if not isinstance(values, (list, tuple)):
        raise ValueError("Supply a sequence of token strings, not a single character string")
    if any(not isinstance(value, str) or not value for value in values):
        raise ValueError("Supply nonempty eligible token strings; represent exclusions in the edge selection")
    count = len(values)
    seen = set()
    degree = Counter()
    for edge in edges:
        if not isinstance(edge, (tuple, list)) or len(edge) != 2:
            raise ValueError("Each edge must have two retained-position indices")
        left, right = edge
        if any(type(index) is not int or not 0 <= index < count for index in edge) or left == right:
            raise ValueError("Edge indices must be distinct integers within the retained positions")
        pair = tuple(sorted(edge))
        if pair in seen:
            raise ValueError("Duplicate undirected edge")
        seen.add(pair)
        degree.update(pair)
    edge_count = len(seen)
    shared = sum(value * (value - 1) // 2 for value in degree.values())
    disjoint = edge_count * (edge_count - 1) // 2 - shared
    frequencies = list(Counter(values).values())
    second = sum(falling(value, 2) for value in frequencies)
    pair_probability = Fraction(second, falling(count, 2)) if count >= 2 else Fraction(0)
    triple_probability = Fraction(sum(falling(value, 3) for value in frequencies), falling(count, 3)) if count >= 3 else Fraction(0)
    fourth = sum(falling(value, 4) for value in frequencies)
    distinct_pairs = second ** 2 - sum(falling(value, 2) ** 2 for value in frequencies)
    disjoint_probability = Fraction(fourth + distinct_pairs, falling(count, 4)) if count >= 4 else Fraction(0)
    expected = edge_count * pair_probability
    variance = (edge_count * pair_probability * (1 - pair_probability)
                + 2 * shared * (triple_probability - pair_probability ** 2)
                + 2 * disjoint * (disjoint_probability - pair_probability ** 2))
    if variance < 0:
        raise ValueError("Internal error: negative exact variance")
    return {
        "expected": expected,
        "variance": variance,
        "eligible_edges": edge_count,
        "shared_edge_pairs": shared,
        "disjoint_edge_pairs": disjoint,
    }
