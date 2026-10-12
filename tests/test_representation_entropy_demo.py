import math
import unittest

from scripts.representation_entropy_demo import decode_fixed_width, empirical_entropy, encode, make_report


class RepresentationEntropyTests(unittest.TestCase):
    def test_hand_calculated_zero_and_uniform_entropy(self):
        self.assertEqual(empirical_entropy("aaaa"), 0.0)
        self.assertEqual(empirical_entropy("aabb"), 1.0)
        self.assertEqual(empirical_entropy("abcd"), 2.0)

    def test_conditional_entropy_of_a_deterministic_cycle(self):
        self.assertEqual(empirical_entropy("abababab", 1), 0.0)
        self.assertEqual(empirical_entropy("abcdabcd", 1), 0.0)

    def test_order_one_hand_calculation(self):
        # aa, ab, ba: after a the two next symbols are equally likely;
        # after b the next symbol is deterministic. Three transitions are scored.
        self.assertAlmostEqual(empirical_entropy("aaba", 1), 2 / 3)

    def test_reversible_maps_preserve_sequence_and_atom_measurements(self):
        result = make_report(16, 7)
        atom = result["atomic_empirical_bits_per_symbol"]
        for representation in result["representations"]:
            self.assertTrue(representation["round_trip_verified"])
            self.assertEqual(representation["decoded_bits_per_symbol"], atom)
        plain, escaped = result["representations"]
        self.assertEqual(escaped["ascii_character_count"], 5 * plain["ascii_character_count"])
        self.assertEqual(plain["ideal_uniform_block_bits_per_original_symbol"],
                         escaped["ideal_uniform_block_bits_per_original_symbol"])
        self.assertAlmostEqual(plain["ideal_uniform_block_bits_per_ascii_character"],
                               5 * escaped["ideal_uniform_block_bits_per_ascii_character"], places=9)
        self.assertLess(escaped["empirical_bits_per_ascii_character"]["1"], plain["empirical_bits_per_ascii_character"]["1"])

    def test_combinatorial_support_for_one_each_of_four_symbols(self):
        self.assertAlmostEqual(make_report(1)["log2_distinct_balanced_sequences"], math.log2(24), places=9)

    def test_invalid_or_partial_maps_cannot_be_silently_decoded(self):
        mapping = {"A": "@128;", "B": "@129;"}
        self.assertEqual(decode_fixed_width(encode(["A", "B", "A"], mapping), mapping), ["A", "B", "A"])
        for text in ("@128", "@999;"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                decode_fixed_width(text, mapping)
        for bad in ({"A": "x", "B": "x"}, {"A": "x", "B": "yy"}):
            with self.subTest(mapping=bad), self.assertRaises(ValueError):
                decode_fixed_width("x", bad)

    def test_empty_and_invalid_contexts_are_rejected(self):
        for sequence, order in (("", 0), ("a", 1), ("a", -1)):
            with self.subTest(sequence=sequence, order=order), self.assertRaises(ValueError):
                empirical_entropy(sequence, order)

    def test_unrecorded_randomness_and_boolean_counts_are_rejected(self):
        for arguments in ({"seed": None}, {"seed": True}, {"count_per_symbol": True}):
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                make_report(**arguments)


if __name__ == "__main__":
    unittest.main()
