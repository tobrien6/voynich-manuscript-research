import unittest

from scripts.audit_historical_interlinear import HistoricalRecord
from scripts.audit_historical_label_phrases import audit, literal_string, lookup


def record(line, transcriber, body, page="f1r", unit="X"):
    return HistoricalRecord(f"{page}.{unit}.{line};{transcriber}", page, unit, line,
                            transcriber, body, 1)


class HistoricalLabelLookupTests(unittest.TestCase):
    def test_formatter_preserves_readings_case_and_coded_fallbacks(self):
        self.assertEqual(literal_string("a!b,{comment}cd-ef=G*{&138}%"), "ab cd ef G*")
        self.assertEqual(literal_string("a{&F}b="), "ab")
        with self.assertRaises(ValueError):
            literal_string("a{bad")

    def test_only_complete_exact_records_match(self):
        records = [record("1", "H", "a.b="), record("2", "F", "x.a.b="),
                   record("3", "U", "A.b="), record("4", "V", "a.b*=")]
        result = lookup(records, ["a b", "missing"])
        self.assertEqual([r["locator"] for r in result["matches"][0]["records"]], ["f1r.X.1;H"])
        self.assertEqual(result["matches"][1]["records"], [])

    def test_all_transcribers_and_repeated_strings_keep_their_identifiers(self):
        records = [record("1", "F", "a.b="), record("1", "H", "a.c="),
                   record("2", "H", "a.b=", page="f2r")]
        result = lookup(records, ["a b"])
        self.assertEqual(result["native_records_searched"], 3)
        self.assertEqual(result["matches"][0]["matches_by_transcriber"], {"F": 1, "H": 1})
        self.assertEqual(len(result["native_key_readings"]), 2)
        first = result["native_key_readings"][0]
        self.assertEqual([r["literal_string"] for r in first["readings"]], ["a b", "a c"])

    def test_native_key_grouping_does_not_merge_other_units_or_line_suffixes(self):
        records = [record("1", "F", "a.b="), record("1a", "H", "a.c="),
                   record("1", "H", "a.c=", unit="Y")]
        result = lookup(records, ["a b"])
        self.assertEqual(len(result["native_key_readings"]), 1)
        self.assertEqual(len(result["native_key_readings"][0]["readings"]), 1)

    def test_bad_queries_and_duplicate_locators_fail(self):
        for phrases in ([], ["a", "a"], [" a"], ["a  b"], [""], "word", [{}]):
            with self.subTest(phrases=phrases), self.assertRaises(ValueError):
                lookup([], phrases)
        with self.assertRaises(ValueError):
            lookup([record("1", "H", "a="), record("1", "H", "b=")], ["a"])

    def test_recovered_archive_search_covers_every_native_record(self):
        result = audit()
        self.assertEqual(result["native_records_searched"], 17357)
        queries = {m["phrase"]: m for m in result["matches"]}
        self.assertNotIn("H", queries["dar alocfhy"]["matches_by_transcriber"])
        self.assertNotIn("H", queries["otarodl shy orory"]["matches_by_transcriber"])
        self.assertEqual(queries["otarodl shy orory"]["matches_by_transcriber"], {"F": 1})


if __name__ == "__main__":
    unittest.main()
