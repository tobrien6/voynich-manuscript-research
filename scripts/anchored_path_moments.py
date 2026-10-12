"""Exact weighted anchored-path moments, with identity-preserving edge events.

The chain counter originates in PR #105's fixed paragraph-order control.
This standalone helper keeps that formula without importing the pending
producer or its cached manuscript result. Weights are exact Fractions.
"""

from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import factorial


def constraints_probability(size, edges):
    """Count fixed-anchor orders satisfying directed adjacency requirements."""
    if type(size) is not int or size < 1:
        raise ValueError('a paragraph must have at least one locus identity')
    requirements = set()
    for edge in edges:
        if len(edge) != 2 or any(type(i) is not int or not 0 <= i < size for i in edge):
            raise ValueError('edge identities must be original locus indices')
        requirements.add(tuple(edge))
    successor, predecessor = {}, {}
    for left, right in sorted(requirements):
        if left == right or right == 0 or left == size - 1:
            return Fraction()
        if left in successor or right in predecessor:
            return Fraction()
        successor[left], predecessor[right] = right, left
    chains, seen = [], set()
    for start in range(size):
        if start in predecessor:
            continue
        chain, node = [], start
        while node is not None:
            chain.append(node)
            seen.add(node)
            node = successor.get(node)
        chains.append(chain)
    if len(seen) != size:  # A directed cycle has no chain root.
        return Fraction()
    first = next(chain for chain in chains if 0 in chain)
    last = next(chain for chain in chains if size - 1 in chain)
    orders = factorial(max(size - 2, 0))
    if first == last:
        return Fraction(1, orders) if len(first) == size else Fraction()
    return Fraction(factorial(len(chains) - 2), orders)


@lru_cache(maxsize=None)
def _canonical_probability(size, edges):
    return constraints_probability(size, [(size - 1 if a == -1 else a,
                                           size - 1 if b == -1 else b) for a, b in edges])


def event_probability(size, edges):
    """Cache identity-isomorphic events; fixed anchors retain separate roles."""
    if type(size) is not int or size < 1:
        raise ValueError('a path must contain at least one identity')
    renamed, canonical = {}, []
    for edge in edges:
        if len(edge) != 2 or any(type(i) is not int or not 0 <= i < size for i in edge):
            raise ValueError('event indices must be original path identities')
        pair = []
        for node in edge:
            if node == 0:
                pair.append(0)
            elif node == size - 1:
                pair.append(-1)
            else:
                if node not in renamed:
                    renamed[node] = len(renamed) + 1
                pair.append(renamed[node])
        canonical.append(tuple(pair))
    return _canonical_probability(size, tuple(canonical))


def weighted_moments(weights):
    """Sum edge weights on a uniform interior-identity permutation path."""
    size = len(weights)
    if not size or any(len(row) != size for row in weights):
        raise ValueError('weights must be a nonempty square matrix')
    for a, row in enumerate(weights):
        for b, weight in enumerate(row):
            if (a == b and weight is not None) or (a != b and not isinstance(weight, Fraction)):
                raise ValueError('off-diagonal weights must be Fractions; self edges are null')
    probabilities = [[None if a == b else event_probability(size, [(a, b)])
                      for b in range(size)] for a in range(size)]
    edges = [(a, b) for a in range(size) for b in range(size)
             if a != b and weights[a][b] and probabilities[a][b]]
    mean = sum((weights[a][b] * probabilities[a][b] for a, b in edges), Fraction())
    diagonal = sum((weights[a][b] ** 2 * probabilities[a][b] * (1 - probabilities[a][b])
                    for a, b in edges), Fraction())
    covariance = Fraction()
    joint_count = zero_joints = 0
    for left, right in combinations(edges, 2):
        joint = event_probability(size, [left, right])
        pa, pb = probabilities[left[0]][left[1]], probabilities[right[0]][right[1]]
        covariance += weights[left[0]][left[1]] * weights[right[0]][right[1]] * (joint - pa * pb)
        joint_count += 1
        zero_joints += joint == 0
    variance = diagonal + 2 * covariance
    observed = sum((weights[i][i + 1] for i in range(size - 1)), Fraction())
    if variance < 0 or (variance == 0 and observed != mean):
        raise ValueError('weighted conditional moments contradict the observed allowed path')
    return {'observed': observed, 'mean': mean, 'variance': variance,
            'diagonal_variance': diagonal, 'twice_covariance': 2 * covariance,
            'probabilities': probabilities, 'nonzero_weight_possible_edges': len(edges),
            'joint_events_evaluated': joint_count, 'zero_joint_events': zero_joints,
            'positive_joint_events': joint_count - zero_joints,
            'possible_interior_orders': factorial(max(size - 2, 0)),
            'invariant': variance == 0}
