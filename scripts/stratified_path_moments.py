"""Exact anchored path moments under fixed interior stratum-position patterns.

Required edges form short directed chains, as in anchored_path_moments, but
their placements are counted in the actual slot pattern rather than contracted
into interchangeable free chains. At most two edges are needed for variance.
"""

from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
from math import factorial, prod


def validate_strata(strata):
    if not isinstance(strata, (list, tuple)) or not strata or any(
            type(label) is not int or label < 0 for label in strata):
        raise ValueError('strata must be a nonempty sequence of nonnegative integer labels')
    return tuple(strata)


def allowed_orders(strata):
    strata = validate_strata(strata)
    return prod(factorial(count) for count in Counter(strata[1:-1]).values())


@lru_cache(maxsize=100000)
def _probability(strata, edges):
    size = len(strata)
    successor, predecessor = {}, {}
    nodes = set()
    for left, right in edges:
        if left == right or right == 0 or left == size - 1:
            return Fraction()
        if left in successor or right in predecessor:
            return Fraction()
        successor[left], predecessor[right] = right, left
        nodes.update((left, right))
    chains, seen = [], set()
    for start in sorted(nodes - predecessor.keys()):
        chain, node = [], start
        while node is not None:
            chain.append(node)
            seen.add(node)
            node = successor.get(node)
        chains.append(chain)
    if seen != nodes:  # Cycle.
        return Fraction()
    if not chains:
        return Fraction(1)
    candidates = []
    for chain in chains:
        placements = []
        for start in range(size - len(chain) + 1):
            slots = tuple(range(start, start + len(chain)))
            valid = True
            for identity, slot in zip(chain, slots):
                if identity in (0, size - 1):
                    valid &= slot == identity
                else:
                    valid &= 0 < slot < size - 1 and strata[identity] == strata[slot]
            if valid:
                placements.append(slots)
        candidates.append(placements)
    assignments = sum(len(set().union(*map(set, placement))) == sum(map(len, placement))
                      for placement in product(*candidates))
    counts = Counter(strata[1:-1])
    required = Counter(strata[node] for node in nodes if 0 < node < size - 1)
    denominator = prod(prod(range(counts[label] - count + 1, counts[label] + 1))
                       for label, count in required.items())
    return Fraction(assignments, denominator)


def event_probability(strata, edges):
    strata = validate_strata(strata)
    requirements = set()
    for edge in edges:
        if len(edge) != 2 or any(type(i) is not int or not 0 <= i < len(strata) for i in edge):
            raise ValueError('edge identities must be original path indices')
        requirements.add(tuple(edge))
    if len(requirements) > 2:
        raise ValueError('single and two-edge events only')
    return _probability(strata, tuple(sorted(requirements)))


def weighted_moments(weights, strata):
    strata = validate_strata(strata)
    size = len(strata)
    if len(weights) != size or any(len(row) != size for row in weights):
        raise ValueError('weights must be a square matrix matching the strata')
    for a, row in enumerate(weights):
        for b, weight in enumerate(row):
            if (a == b and weight is not None) or (a != b and not isinstance(weight, Fraction)):
                raise ValueError('off-diagonal weights must be Fractions; self edges are null')
    probabilities = [[None if a == b else event_probability(strata, [(a, b)])
                      for b in range(size)] for a in range(size)]
    edges = [(a, b) for a in range(size) for b in range(size)
             if a != b and weights[a][b] and probabilities[a][b]]
    mean = sum((weights[a][b] * probabilities[a][b] for a, b in edges), Fraction())
    diagonal = sum((weights[a][b] ** 2 * probabilities[a][b] * (1 - probabilities[a][b])
                    for a, b in edges), Fraction())
    covariance = Fraction()
    zero = 0
    for left, right in combinations(edges, 2):
        joint = event_probability(strata, [left, right])
        covariance += (weights[left[0]][left[1]] * weights[right[0]][right[1]] *
                       (joint - probabilities[left[0]][left[1]] * probabilities[right[0]][right[1]]))
        zero += joint == 0
    count = len(edges) * (len(edges) - 1) // 2
    variance = diagonal + 2 * covariance
    observed = sum((weights[i][i + 1] for i in range(size - 1)), Fraction())
    if variance < 0 or (variance == 0 and observed != mean):
        raise ValueError('restricted moments contradict the allowed original path')
    return {'observed': observed, 'mean': mean, 'variance': variance,
            'diagonal_variance': diagonal, 'twice_covariance': 2 * covariance,
            'probabilities': probabilities, 'nonzero_weight_possible_edges': len(edges),
            'joint_events_evaluated': count, 'zero_joint_events': zero,
            'positive_joint_events': count - zero, 'possible_interior_orders': allowed_orders(strata),
            'invariant': variance == 0}
