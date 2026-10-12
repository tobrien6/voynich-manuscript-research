import json
import unittest

from scripts.audit_transcription_comparators import ROOT, annotation_counts, audit, profile
from scripts.ivtff import parse_ivtff


class ComparatorTests(unittest.TestCase):
    def test_comment_punctuation_is_not_manuscript_annotation(self):
        counts, runs = annotation_counts("<%>ab,cd<->ef.[x:y]{gh}@200;?<$><! note [?] . , @201;>")
        self.assertEqual(counts["uncertain_space_comma"], 1)
        self.assertEqual(counts["apparent_space_period"], 1)
        self.assertEqual(counts["alternative_group"], 1)
        self.assertEqual(counts["high_ascii_escape"], 1)
        self.assertEqual(counts["drawing_interruption"], 1)
        self.assertEqual(runs, {"1": 1})

    def test_v101_punctuation_is_not_stripped_as_comments(self):
        counts, _ = annotation_counts("a!b#c+d(e)")
        self.assertEqual(counts["free_inline_comment"], 0)
        self.assertEqual(counts["alternative_group"], 0)

    def test_nonexistent_record_does_not_enter_annotation_denominator(self):
        document = parse_ivtff("#=IVTFF v101 2.0 M\n<f1r>\n"
                               "<f1r.1,@P0> a!b\n<f1r.2,!Lf> x,y.[z:q]?\n")
        result = profile({"id": "X", "sha256": "synthetic", "bytes": 0}, document)
        self.assertEqual(result["all_locus_record_count"], 2)
        self.assertEqual(result["present_locus_record_count"], 1)
        self.assertEqual(result["annotation_occurrences_in_present_records"]["uncertain_space_comma"], 0)
        self.assertEqual(result["generic_locus_counts_in_present_records"], {"P": 1})

    def test_unclosed_inline_annotation_fails(self):
        with self.assertRaisesRegex(ValueError, "malformed"):
            annotation_counts("ab<! unclosed")

    def test_all_pinned_exports_reproduce_the_committed_profile(self):
        result = audit()
        expected = json.loads((ROOT / "research/transliteration/comparator_profiles.json").read_text())
        self.assertEqual(result, expected)
        full, basic = result["profiles"]["RF1b-full"], result["profiles"]["RF1b-basic"]
        self.assertEqual(full["header"], basic["header"])
        self.assertNotEqual(full["sha256"], basic["sha256"])
        self.assertGreater(full["annotation_occurrences_in_present_records"]["high_ascii_escape"], 0)
        self.assertEqual(basic["annotation_occurrences_in_present_records"]["high_ascii_escape"], 0)


if __name__ == "__main__":
    unittest.main()
