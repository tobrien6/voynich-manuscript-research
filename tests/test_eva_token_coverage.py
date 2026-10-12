"""Synthetic accounting cases plus a replay of the pinned preprocessing corpus."""

from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import contextlib
import io
import tempfile
import unittest
from unittest.mock import patch

from scripts.audit_eva_token_coverage import audit, encoded, load_json, main, selection_manifest, summarize_outputs, verify_cached


ROOT = Path(__file__).resolve().parents[1]


def fixture():
    outputs = {}
    for policy in ("split", "join"):
        records = []
        for source in ("left", "right"):
            values = (["CANARYTOKENMUSTNOTAPPEAR", "b"] if policy == "split" else ["joined"])
            token_lists = [values, ["c"], None] if source == "left" else [["a", "b"], None, ["d", "e"]]
            for number, tokens in enumerate(token_lists, 1):
                key = f"f1r.{number}"
                reasons = ([] if tokens is not None else ["unreadable", "alternative_reading"]
                           if source == "left" else ["unreadable"])
                records.append({"source_id": source, "page_id": "f1r", "locus_key": key,
                                "locus_identifier": key + ",+P0", "locus_type": "P0", "locator": "+",
                                "transcriber": None, "source_line_number": number + 2, "variables": {},
                                "eligible": tokens is not None, "tokens": tokens,
                                "token_count": len(tokens) if tokens is not None else None,
                                "exclusion_reasons": reasons})
        outputs[policy] = {"schema_version": 1, "adapter_version": "plain-eva-v1",
                           "analysis_unit": "transcription_locus",
                           "sources": [{"id": ident, "sha256": "a" * 64,
                                        "alphabet": "Eva-", "url": "https://example.invalid/" + ident,
                                        "path": "synthetic.txt"} for ident in ("left", "right")],
                           "processing": {"uncertain_space_policy": policy, "selected_locus_types": ["P0", "P1"]},
                           "records": records,
                           "summary": {"records": 6, "eligible_records": 4, "excluded_records": 2,
                                       "exclusion_reason_record_counts": dict(sorted(Counter(
                                           reason for record in records for reason in record["exclusion_reasons"]).items()))}}
    return outputs


class CoverageTests(unittest.TestCase):
    def test_source_denominators_reason_overlap_and_common_cohort_are_distinct(self):
        report = summarize_outputs(fixture())
        self.assertEqual(report["source_coverage"]["left"]["selected_present_locus_records"], 3)
        profile = report["policy_coverage"]["split"]["left"]
        self.assertEqual(profile["eligible_locus_records"], 2)
        self.assertEqual(profile["excluded_after_selected_present_filter"], 1)
        self.assertEqual(sum(profile["exclusion_reason_record_counts_may_overlap"].values()), 2)
        shared = report["cohorts"]["eligible_in_every_source_and_policy"]
        self.assertEqual(shared["native_locus_count"], 1)
        self.assertEqual(shared["sorted_native_keys_sha256"], hashlib.sha256(b"f1r.1\n").hexdigest())
        self.assertEqual(report["cohorts"]["at_least_two_tokens_in_every_source_and_policy"]["native_locus_count"], 0)
        self.assertNotIn("CANARYTOKENMUSTNOTAPPEAR", encoded(report).decode())
        self.assertNotEqual(report["adapter_snapshot_sha256"]["split"], report["adapter_snapshot_sha256"]["join"])

    def test_exact_key_export_preserves_source_policy_and_exclusion_dimensions(self):
        result = selection_manifest(fixture())
        for policy in ("split", "join"):
            left = result["policy_key_sets"][policy]["left"]
            eligible = result["key_sets"][left["eligible"]["sorted_native_keys_sha256"]]
            excluded = result["key_sets"][left["excluded"]["sorted_native_keys_sha256"]]
            self.assertEqual(eligible, ["f1r.1", "f1r.2"])
            self.assertEqual(excluded, ["f1r.3"])
            self.assertFalse(set(eligible) & set(excluded))
        for digest, keys in result["key_sets"].items():
            self.assertEqual(digest, hashlib.sha256("".join(key + "\n" for key in keys).encode()).hexdigest())
            self.assertEqual(keys, sorted(set(keys)))
        shared = result["shared_cohort_key_sets"]["eligible_in_every_source_and_policy"]
        self.assertEqual(result["key_sets"][shared["sorted_native_keys_sha256"]], ["f1r.1"])
        self.assertNotIn("CANARYTOKENMUSTNOTAPPEAR", encoded(result).decode())

    def test_summary_tampering_and_policy_identity_drift_fail(self):
        outputs = fixture()
        outputs["split"]["summary"]["records"] = 7
        with self.assertRaisesRegex(ValueError, "does not reconcile"):
            summarize_outputs(outputs)
        outputs = fixture()
        outputs["join"]["records"][0]["source_line_number"] = 999
        with self.assertRaisesRegex(ValueError, "metadata changed"):
            summarize_outputs(outputs)

    def test_multiple_transcribers_cannot_silently_collapse_a_native_key(self):
        outputs = fixture()
        record = deepcopy(outputs["split"]["records"][0])
        record.update(transcriber="B", locus_identifier="f1r.1,+P0;B")
        outputs["split"]["records"].append(record)
        with self.assertRaisesRegex(ValueError, "resolve transcriber pairing"):
            summarize_outputs(outputs)

    def test_cross_source_kind_disagreement_is_reported_without_remapping(self):
        outputs = fixture()
        for output in outputs.values():
            record = output["records"][3]
            record.update(locus_type="P1", locus_identifier="f1r.1,+P1")
        report = summarize_outputs(outputs)
        self.assertEqual(report["cohorts"]["cross_source_metadata_differences_in_shared_eligible_cohort"],
                         {"locus_type": 1, "locator": 0})
        self.assertEqual(report["cohorts"]["eligible_in_every_source_and_policy"]["native_locus_count"], 1)

    def test_cached_tokens_and_provenance_are_replayed_not_trusted(self):
        expected = fixture()["split"]
        with patch("scripts.audit_eva_token_coverage.build", return_value=expected):
            self.assertEqual(verify_cached(json.dumps(dict(reversed(list(expected.items())))).encode()), expected)
            for change in ("token", "source", "numeric_type"):
                altered = deepcopy(expected)
                if change == "token":
                    altered["records"][0]["tokens"][0] = "fabricated"
                elif change == "source":
                    altered["sources"][0]["sha256"] = "b" * 64
                else:
                    altered["summary"]["records"] = 6.0
                with self.subTest(change=change), self.assertRaisesRegex(ValueError, "differs from the pinned producer"):
                    verify_cached(encoded(altered))

    def test_duplicate_json_keys_are_not_silently_overwritten(self):
        with self.assertRaisesRegex(ValueError, "Duplicate JSON object key"):
            load_json(b'{"schema_version": 0, "schema_version": 1}')

    def test_cli_cannot_overwrite_a_checked_report_or_raw_source(self):
        outputs = fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            checked = root / "coverage.json"
            checked.write_bytes(encoded(summarize_outputs(outputs)))
            raw = root / "data/raw/source.txt"
            raw.parent.mkdir(parents=True)
            raw.write_bytes(b"original source bytes")
            cases = [(["--check", str(checked), "--keys-output", str(checked)], checked),
                     (["--output", str(raw)], raw)]
            with patch("scripts.audit_eva_token_coverage.ROOT", root), \
                 patch("scripts.audit_eva_token_coverage.build", side_effect=lambda policy, *_: outputs[policy]), \
                 contextlib.redirect_stderr(io.StringIO()):
                for arguments, path in cases:
                    before = path.read_bytes()
                    with self.subTest(arguments=arguments), patch("sys.argv", ["audit", *arguments]):
                        with self.assertRaises(SystemExit) as caught:
                            main()
                        self.assertEqual(caught.exception.code, 1)
                        self.assertEqual(path.read_bytes(), before)

    def test_pinned_report_replays_with_source_separated_counts(self):
        result = audit()
        expected = load_json((ROOT / "research/transliteration/token_adapter_coverage.json").read_bytes())
        self.assertEqual(result, expected)
        self.assertEqual(result["policy_coverage"]["split"]["ZL3b"]["eligible_locus_records"], 3012)
        self.assertEqual(result["policy_coverage"]["split"]["IT2a"]["eligible_locus_records"], 3894)
        self.assertEqual(result["cohorts"]["eligible_in_every_source_and_policy"]["native_locus_count"], 2997)
        self.assertEqual(result["cohorts"]["at_least_two_tokens_in_every_source_and_policy"]["native_locus_count"], 2993)


if __name__ == "__main__":
    unittest.main()
