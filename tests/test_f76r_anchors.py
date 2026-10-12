"""Selection choices and native uncertainty are independent of image review."""

import unittest
from scripts.ivtff import Document, Locus
from scripts.select_f76r_anchors import select


def locus(number, locator="+", kind="P0", text="a.[b:c],d<!note>"):
    return Locus("f76r", number, locator, kind, None, text, 100+number, {})


def documents(left, right=None):
    return {ident: Document("synthetic", "Eva-", {}, tuple(rows))
            for ident, rows in [("ZL3b", left), ("IT2a", left if right is None else right)]}


class AnchorTests(unittest.TestCase):
    def test_numeric_order_and_lower_median_for_even_count(self):
        result = select(documents([locus(n) for n in [20, 3, 11, 1]]))
        self.assertEqual(result["eligible_keys_in_numeric_order"],
                         ["f76r.1", "f76r.3", "f76r.11", "f76r.20"])
        self.assertEqual([(a["key"], a["eligible_rank_zero_based"]) for a in result["anchors"]],
                         [("f76r.1", 0), ("f76r.3", 1), ("f76r.20", 3)])

    def test_either_source_can_exclude_a_key_without_readability_filter(self):
        left = [locus(n) for n in range(1, 8)]
        right = [locus(1), locus(2, "="), locus(3, "!"), locus(4, kind="P1"),
                 locus(6, text="???"), locus(7)]
        result = select(documents(left, right))
        self.assertEqual(result["eligible_keys_in_numeric_order"], ["f76r.1", "f76r.6", "f76r.7"])
        self.assertEqual([item["reasons"] for item in result["excluded_page_keys"]],
                         [["IT2a:not_regular_P0"], ["IT2a:nonexistent"],
                          ["IT2a:not_regular_P0"], ["IT2a:absent"]])

    def test_adjacent_same_line_fragment_and_native_annotations_are_preserved(self):
        rows = [locus(1), locus(2, "="), locus(3), locus(4)]
        first = select(documents(rows))["anchors"][0]["sources"]["ZL3b"]
        self.assertEqual(first["locus"]["native_text"], "a.[b:c],d<!note>")
        self.assertEqual(first["locus"]["source_file_line"], 101)
        self.assertEqual(first["following"]["identifier"], "f76r.2,=P0")
        self.assertIsNone(first["preceding"])

    def test_missing_editions_duplicate_keys_and_small_samples_fail(self):
        for value in [{"ZL3b": documents([])["ZL3b"]},
                      documents([locus(1), locus(1), locus(2), locus(3)]),
                      documents([locus(1), locus(2)])]:
            with self.assertRaises(ValueError):
                select(value)

    def test_other_pages_do_not_change_selection(self):
        rows = [locus(n) for n in [1, 2, 3]]
        rows.append(Locus("f75r", 99, "+", "P0", None, "a.b", 999, {}))
        self.assertEqual(select(documents(rows)), select(documents(rows[:3])))


if __name__ == "__main__":
    unittest.main()
