"""Synthetic adapter packets test common-cohort and provenance failures."""

import copy
import json
import unittest
from scripts import run_locus_position_baseline as RUNNER


def protocol():
    return json.loads(RUNNER.PROTOCOL.read_bytes())


def packets():
    """Declared source fields are toy metadata, not actual manuscript samples."""
    settings = protocol()
    result = {}
    for policy in ["split", "join"]:
        records = []
        sources = []
        for ident, alphabet in [("ZL3b", "Eva-"), ("IT2a", "EvaT")]:
            sources.append({"id": ident, "alphabet": alphabet, "sha256": settings["sources"][ident]})
            for number in [1, 2]:
                records.append({"source_id": ident, "locus_key": f"f1r.{number}",
                    "page_id": "f1r", "locus_identifier": f"f1r.{number},+P0",
                    "locus_type": "P0", "locator": "+", "transcriber": None,
                    "source_line_number": number, "eligible": True,
                    "tokens": ["aaa", "b"], "token_count": 2, "exclusion_reasons": []})
        result[policy] = {"schema_version": 1, "adapter_version": "plain-eva-v1",
                          "processing": {"uncertain_space_policy": policy,
                                         "selected_locus_types": ["P0", "P1"]},
                          "sources": sources, "records": records}
    return result


class CohortTests(unittest.TestCase):
    def test_fixed_intersection_drops_a_single_token_locus_from_every_variant(self):
        data = packets()
        record = next(row for row in data["join"]["records"]
                      if row["source_id"] == "ZL3b" and row["locus_key"] == "f1r.2")
        record.update(tokens=["aaab"], token_count=1)
        report = RUNNER.build_report(protocol(), data)
        self.assertEqual(report["cohort"]["locus_keys"], ["f1r.1"])
        for variant in report["variants"]:
            self.assertEqual(variant["cohort_locus_count"], 1)
            self.assertEqual(variant["selection_audit"]["excluded_record_count"], 1)
            self.assertEqual(variant["selection_audit"]["excluded_locus_groups"][0]["locus_keys"], ["f1r.2"])
        self.assertEqual(report["variants"][0]["observed_equal_locus_mean_contrast"], 2)

    def test_excluded_ambiguity_is_visible_and_never_replaced_by_candidate_tokens(self):
        data = packets()
        record = data["split"]["records"][0]
        record.update(eligible=False, tokens=None, token_count=None, exclusion_reasons=["alternative_reading"])
        report = RUNNER.build_report(protocol(), data)
        self.assertEqual(report["cohort"]["locus_keys"], ["f1r.2"])
        audit = next(row for row in report["variants"] if row["source_id"] == "ZL3b" and row["spacing_policy"] == "split")["selection_audit"]
        self.assertEqual(audit["excluded_locus_groups"][0]["reasons"], ["alternative_reading"])
        record["tokens"] = ["aaa", "b"]
        with self.assertRaisesRegex(ValueError, "Inconsistent excluded"):
            RUNNER.build_report(protocol(), data)

    def test_mismatched_packet_policy_and_source_checksums_fail(self):
        for change, message in [("policy", "policy mismatch"), ("checksum", "checksum mismatch")]:
            data = packets()
            if change == "policy":
                data["split"]["processing"]["uncertain_space_policy"] = "join"
            else:
                data["split"]["sources"][0]["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, message):
                RUNNER.build_report(protocol(), data)

    def test_duplicate_records_and_missing_policy_records_fail(self):
        data = packets()
        data["split"]["records"].append(copy.deepcopy(data["split"]["records"][0]))
        with self.assertRaisesRegex(ValueError, "Duplicate source/locus"):
            RUNNER.build_report(protocol(), data)
        data = packets()
        data["join"]["records"].pop()
        with self.assertRaisesRegex(ValueError, "Different source/locus sets"):
            RUNNER.build_report(protocol(), data)

    def test_metadata_changes_across_token_policies_fail(self):
        data = packets()
        data["join"]["records"][0]["locator"] = "@"
        with self.assertRaisesRegex(ValueError, "metadata changed"):
            RUNNER.build_report(protocol(), data)

    def test_unselected_locator_is_excluded_even_if_adapter_tokens_are_eligible(self):
        data = packets()
        for packet in data.values():
            for record in packet["records"]:
                if record["locus_key"] == "f1r.1":
                    record["locator"] = "="
        report = RUNNER.build_report(protocol(), data)
        self.assertEqual(report["cohort"]["locus_keys"], ["f1r.2"])
        self.assertTrue(all("baseline_unselected_locator" in row["selection_audit"]["excluded_locus_groups"][0]["reasons"]
                            for row in report["variants"]))

    def test_empty_common_cohort_fails(self):
        data = packets()
        for record in data["split"]["records"]:
            record.update(tokens=["ab"], token_count=1)
        with self.assertRaisesRegex(ValueError, "No common eligible"):
            RUNNER.build_report(protocol(), data)

    def test_relabeling_units_or_changing_v1_settings_requires_a_new_implementation(self):
        for key, value in [("unit", "manuscript glyphs"), ("null_replicates", 199),
                           ("analysis_status", "confirmatory")]:
            settings = protocol()
            settings[key] = value
            with self.assertRaises(ValueError):
                RUNNER.build_report(settings, packets())


if __name__ == "__main__":
    unittest.main()
