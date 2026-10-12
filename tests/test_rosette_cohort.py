import copy
import json
from pathlib import Path
import unittest

from scripts.rosette_cohort import check


ROOT = Path(__file__).resolve().parents[1]


def source(sid, identifiers, header=True):
    from collections import Counter
    return {"id": sid, "pages": [{"page_id": "fRos", "header_present": header,
        "present_loci": len(identifiers), "present_locus_identifiers": identifiers,
        "present_loci_by_kind": dict(Counter(identifier.split(",")[1][1:3] for identifier in identifiers))}]}


class RosetteCohortTests(unittest.TestCase):
    def test_committed_audit_exposes_the_actual_partial_and_absent_cohorts(self):
        report = json.loads((ROOT / "research/pilot/rosette-source-coverage.json").read_text())
        result = check(report, "ZL3b", "GC2a")
        self.assertEqual(result["shared_key_count"], 148)
        self.assertEqual(result["left_only_keys"], ["fRos.1", "fRos.3", "fRos.4", "fRos.5", "fRos.6", "fRos.7",
            "fRos.8", "fRos.9", "fRos.10", "fRos.18", "fRos.33", "fRos.135"])
        self.assertEqual(result["right_only_keys"], [])
        self.assertTrue(result["errors"])
        absent = check(report, "ZL3b", "IT2a")
        self.assertTrue(any("absent exact" in error for error in absent["errors"]))
        self.assertEqual(len(absent["left_only_keys"]), 160)
        self.assertEqual(check(report, "ZL3b", "RF1b-full")["errors"], [])
        self.assertIsNone(report["verified_locus_crosswalk"])
        self.assertIs(report["apply_to_statistics"], False)

    def test_same_export_and_missing_or_duplicate_export_metadata_are_refused(self):
        report = {"modern_sources": [source("ZL3b", ["fRos.1,@L0"]), source("GC2a", ["fRos.1,@L0"])]}
        with self.assertRaisesRegex(ValueError, "distinct"):
            check(report, "ZL3b", "ZL3b")
        with self.assertRaisesRegex(ValueError, "one record"):
            check(report, "ZL3b", "IT2a")
        report["modern_sources"].append(copy.deepcopy(report["modern_sources"][0]))
        with self.assertRaisesRegex(ValueError, "one record"):
            check(report, "ZL3b", "GC2a")

    def test_two_empty_sets_do_not_pass_even_with_declared_headers(self):
        report = {"modern_sources": [source("ZL3b", []), source("GC2a", [])]}
        self.assertEqual(len(check(report, "ZL3b", "GC2a")["errors"]), 2)
        report["modern_sources"][0]["pages"][0]["header_present"] = False
        self.assertTrue(any("absent exact" in error for error in check(report, "ZL3b", "GC2a")["errors"]))

    def test_same_keys_with_different_kinds_or_locators_are_not_the_same_cohort(self):
        report = {"modern_sources": [source("ZL3b", ["fRos.1,@L0"]), source("GC2a", ["fRos.1,=P0"])]}
        result = check(report, "ZL3b", "GC2a")
        self.assertEqual(result["shared_kind_disagreements"], ["fRos.1"])
        self.assertEqual(result["shared_locator_disagreements"], ["fRos.1"])
        self.assertTrue(result["errors"])

    def test_duplicate_wrong_page_nonexistent_or_interlinear_keys_are_refused(self):
        for identifiers, message in [
            (["fRos.1,@L0", "fRos.1,+L0"], "duplicate native key"),
            (["f85v2.1,@L0"], "wrong-page"),
            (["fRos.1,!L0"], "nonexistent"),
            (["fRos.1,@L0;A"], "interlinear"),
            (["fRos.0,@L0"], "invalid present"),
            (["fRos.1,@L0>ab"], "invalid present"),
        ]:
            with self.subTest(identifiers=identifiers):
                report = {"modern_sources": [source("ZL3b", identifiers), source("GC2a", ["fRos.1,@L0"])]}
                with self.assertRaisesRegex(ValueError, message):
                    check(report, "ZL3b", "GC2a")

    def test_count_and_header_metadata_cannot_hide_or_invent_records(self):
        original = {"modern_sources": [source("ZL3b", ["fRos.1,@L0"]), source("GC2a", ["fRos.1,@L0"])]}
        for field, value, message in [("present_loci", 2, "count differs"),
                                      ("present_loci", True, "presence/count"),
                                      ("header_present", False, "without a page header"),
                                      ("present_loci_by_kind", {"L0": 2}, "kind counts differ")]:
            report = copy.deepcopy(original)
            report["modern_sources"][0]["pages"][0][field] = value
            with self.assertRaisesRegex(ValueError, message):
                check(report, "ZL3b", "GC2a")
