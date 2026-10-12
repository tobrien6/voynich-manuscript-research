from fractions import Fraction
import importlib.util
import itertools
from pathlib import Path
import unittest


SPEC = importlib.util.spec_from_file_location(
    "repetition_moments", Path(__file__).resolve().parents[1] / "scripts" / "repetition_moments.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def enumerate_moments(values, edges):
    permutations = set(itertools.permutations(values))
    counts = [sum(order[left] == order[right] for left, right in edges) for order in permutations]
    mean = Fraction(sum(counts), len(counts))
    variance = sum((Fraction(count) - mean) ** 2 for count in counts) / len(counts)
    return mean, variance


class ConditionalMomentTests(unittest.TestCase):
    def test_all_path_edge_subsets_match_exhaustive_permutations(self):
        cases = [[], ["a"], list("aa"), list("ab"), list("aab"), list("aabb"), list("aaabb"), list("abcde"), list("aabbcd")]
        for values in cases:
            candidates = [(index, index + 1) for index in range(len(values) - 1)]
            for mask in range(1 << len(candidates)):
                edges = [edge for index, edge in enumerate(candidates) if mask & (1 << index)]
                with self.subTest(values=values, edges=edges):
                    actual = MODULE.conditional_moments(values, edges)
                    mean, variance = enumerate_moments(values, edges)
                    self.assertEqual(actual["expected"], mean)
                    self.assertEqual(actual["variance"], variance)

    def test_shared_and_disjoint_edge_covariances_are_both_needed(self):
        shared = MODULE.conditional_moments(list("aab"), [(0, 1), (1, 2)])
        self.assertEqual(shared["expected"], Fraction(2, 3))
        self.assertEqual(shared["variance"], Fraction(2, 9))
        self.assertEqual(shared["shared_edge_pairs"], 1)
        disjoint = MODULE.conditional_moments(list("aabb"), [(0, 1), (2, 3)])
        self.assertEqual(disjoint["expected"], Fraction(2, 3))
        self.assertEqual(disjoint["variance"], Fraction(8, 9))
        self.assertEqual(disjoint["disjoint_edge_pairs"], 1)

    def test_general_simple_graph_matches_enumeration(self):
        values = list("aabc")
        edges = [(0, 1), (0, 2), (1, 2), (2, 3)]
        mean, variance = enumerate_moments(values, edges)
        actual = MODULE.conditional_moments(values, edges)
        self.assertEqual(actual["expected"], mean)
        self.assertEqual(actual["variance"], variance)

    def test_invalid_edges_or_excluded_values_are_rejected(self):
        for edges in [[(0, 0)], [(0, 2)], [(0, 1), (1, 0)], [(True, 1)], [(0,)]]:
            with self.subTest(edges=edges), self.assertRaises(ValueError):
                MODULE.conditional_moments(["a", "b"], edges)
        with self.assertRaises(ValueError):
            MODULE.conditional_moments(["a", None], [])
        with self.assertRaises(ValueError):
            MODULE.conditional_moments("aab", [])


if __name__ == "__main__":
    unittest.main()
