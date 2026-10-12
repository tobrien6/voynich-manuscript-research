import unittest

from scripts.eva_token_adapter import adapt, build, tokenize
from scripts.ivtff import parse_ivtff


class TokenAdapterTests(unittest.TestCase):
    def test_uncertain_spacing_is_an_explicit_two_policy_choice(self):
        self.assertEqual(tokenize("ab,cd.ef", "split")["tokens"], ["ab", "cd", "ef"])
        self.assertEqual(tokenize("ab,cd.ef", "join")["tokens"], ["abcd", "ef"])
        with self.assertRaises(ValueError):
            tokenize("ab", "guess")

    def test_formatting_spaces_are_not_word_spaces_and_case_is_preserved(self):
        self.assertEqual(tokenize("a B . cd", "split")["tokens"], ["aB", "cd"])

    def test_drawing_gaps_are_boundaries_under_both_policies(self):
        for policy in ("split", "join"):
            result = tokenize("ab<->cd<~>ef", policy)
            self.assertEqual(result["tokens"], ["ab", "cd", "ef"])
            self.assertEqual(result["drawing_interruption_count"], 2)

    def test_comments_and_tags_do_not_create_ambiguity_or_tokens(self):
        result = tokenize("<%>a<! ?, @200; [x:y]>.b<@H=2><$>", "split")
        self.assertTrue(result["eligible"])
        self.assertEqual(result["tokens"], ["a", "b"])
        self.assertEqual(result["uncertain_space_count"], 0)

    def test_ambiguous_extended_and_unreadable_loci_are_retained_as_exclusions(self):
        for text, reason in (("a.[b:c]", "alternative_reading"), ("a.???", "unreadable"),
                             ("a.@200;", "high_ascii_escape"), ("a.{bc}", "ligature_braces")):
            with self.subTest(text=text):
                result = tokenize(text, "split")
                self.assertFalse(result["eligible"])
                self.assertIsNone(result["tokens"])
                self.assertIn(reason, result["exclusion_reasons"])

    def test_empty_and_unsupported_boundaries_are_not_silently_repaired(self):
        for text in ("a..b", ".a", "a.", "", "a'b", "a]", "a;"):
            with self.subTest(text=text):
                self.assertFalse(tokenize(text, "split")["eligible"])
        with self.assertRaises(ValueError):
            tokenize("a<! unclosed", "split")

    def test_join_cannot_hide_invalid_uncertain_or_drawing_boundaries(self):
        invalid = ("a,,b", ",ab", "ab,", "a.,b", "a,.b", "a.<->b", "a<->,b")
        for policy in ("split", "join"):
            for text in invalid:
                with self.subTest(policy=policy, text=text):
                    result = tokenize(text, policy)
                    self.assertFalse(result["eligible"])
                    self.assertIsNone(result["tokens"])
                    self.assertIn("empty_token_boundary", result["exclusion_reasons"])

    def test_identity_type_and_nonexistent_exclusions_remain_visible(self):
        doc = parse_ivtff("#=IVTFF Eva- 2.0 M\n<f67r1>\n"
                          "<f67r1.1,@P0> a,b\n<f67r1.2,+Cc> c.d\n<f67r1.3,!P0> e.f\n")
        records = adapt({"id": "fixture"}, doc, "join")
        self.assertEqual(records[0]["page_id"], "f67r1")
        self.assertEqual(records[0]["locus_key"], "f67r1.1")
        self.assertEqual(records[0]["tokens"], ["ab"])
        self.assertIn("unselected_locus_kind", records[1]["exclusion_reasons"])
        self.assertIn("nonexistent_locus", records[2]["exclusion_reasons"])

    def test_v101_cannot_be_mistaken_for_an_eva_length_measurement(self):
        doc = parse_ivtff("#=IVTFF v101 2.0 M\n<f1r>\n<f1r.1,@P0> a!b\n")
        with self.assertRaisesRegex(ValueError, "unsupported alphabet"):
            adapt({"id": "GC-fixture"}, doc, "split")

    def test_pinned_source_outputs_account_for_every_locus(self):
        for policy in ("split", "join"):
            result = build(policy)
            self.assertEqual({s["id"] for s in result["sources"]}, {"ZL3b", "IT2a"})
            self.assertEqual(result["summary"]["records"], 5385 + 5215)
            self.assertEqual(result["summary"]["eligible_records"] + result["summary"]["excluded_records"], 10600)
            for record in result["records"]:
                if record["eligible"]:
                    self.assertEqual(record["token_count"], len(record["tokens"]))
                    self.assertFalse(record["exclusion_reasons"])
                else:
                    self.assertIsNone(record["tokens"])


if __name__ == "__main__":
    unittest.main()
