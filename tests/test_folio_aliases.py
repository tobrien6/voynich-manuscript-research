"""Protect against silent historical-label remapping and stale review records."""

import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("aliases", ROOT / "scripts/check_folio_aliases.py")
ALIASES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ALIASES)
CANVAS = ALIASES.CANVAS_PREFIX + "1006277"
DIGEST = "a" * 64


def registry():
    return json.loads(ALIASES.DEFAULT_REGISTRY.read_bytes())


def verified_fixture():
    """Synthetic approval exercises the gate, not a real foliation finding."""
    data = registry()
    decision = data["decisions"][0]
    decision["decision_id"] = "synthetic-test-decision"
    decision["source_scheme"] = "synthetic_test_scheme"
    decision["source_label"] = "synthetic old reference"
    decision["status"] = "verified"
    decision["verified_target"] = {
        "label": "116v", "canvas_uris": [CANVAS], "manifest_sha256": DIGEST,
        "mapping_scope": "canvas_reference_only"}
    decision["review"] = {
        "reviewer": "Synthetic fixture, not a manuscript review",
        "reviewed_on": "2026-10-11", "finding": "Synthetic acceptance control",
        "evidence_urls": [decision["evidence"][0]["url"]]}
    return data


class AliasTests(unittest.TestCase):
    def test_real_117v_candidate_is_never_a_mapping(self):
        result = ALIASES.lookup(registry(), "yale_legacy_ms408_catalog", "117v")
        self.assertEqual(result["status"], "unresolved")
        self.assertFalse(result["mapping_allowed"])
        self.assertIsNone(result["target"])
        self.assertEqual(result["candidate_target"]["canvas_uris"], [CANVAS])

    def test_source_scheme_and_verbatim_label_are_required(self):
        for scheme, label in [("other_scheme", "117v"),
                              ("yale_legacy_ms408_catalog", "f117v"),
                              ("yale_legacy_ms408_catalog", "117v ")]:
            with self.subTest(scheme=scheme, label=label):
                result = ALIASES.lookup(registry(), scheme, label)
                self.assertEqual(result["source_label"], label)
                self.assertEqual(result["status"], "unregistered")
                self.assertFalse(result["mapping_allowed"])

    def test_duplicate_source_keys_fail_instead_of_picking_first(self):
        data = registry()
        duplicate = copy.deepcopy(data["decisions"][0])
        duplicate["decision_id"] = "second-decision"
        data["decisions"].append(duplicate)
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            ALIASES.validate_registry(data)

    def test_verified_status_requires_review_target_and_matching_snapshot(self):
        data = registry()
        data["decisions"][0]["status"] = "verified"
        with self.assertRaisesRegex(ValueError, "needs a target"):
            ALIASES.validate_registry(data)
        fixture = verified_fixture()
        with self.assertRaisesRegex(ValueError, "require the canvas index"):
            ALIASES.lookup(fixture, "synthetic_test_scheme", "synthetic old reference")
        with self.assertRaisesRegex(ValueError, "different manifest"):
            ALIASES.validate_registry(fixture, {CANVAS: "116v"}, "b" * 64)

    def test_verified_fixture_can_only_map_after_validation(self):
        result = ALIASES.lookup(verified_fixture(), "synthetic_test_scheme",
                                "synthetic old reference", {CANVAS: "116v"}, DIGEST)
        self.assertTrue(result["mapping_allowed"])
        self.assertEqual(result["target"]["mapping_scope"], "canvas_reference_only")

    def test_index_checks_candidate_and_verified_target_labels(self):
        for data in [registry(), verified_fixture()]:
            with self.subTest(status=data["decisions"][0]["status"]):
                with self.assertRaisesRegex(ValueError, "does not match"):
                    ALIASES.validate_registry(data, {CANVAS: "116r"}, DIGEST)

    def test_rejected_decision_remains_blocked(self):
        data = registry()
        data["decisions"][0]["status"] = "rejected"
        result = ALIASES.lookup(data, "yale_legacy_ms408_catalog", "117v")
        self.assertEqual(result["status"], "rejected")
        self.assertIsNone(result["target"])
        self.assertFalse(result["mapping_allowed"])

    def test_unsupported_scope_unrecorded_evidence_and_early_review_fail(self):
        for field, value, message in [
            ("mapping_scope", "whole_text_region", "canvas reference"),
            ("evidence_urls", ["https://example.org/unrecorded"], "cite evidence"),
            ("reviewed_on", "2026-10-10", "precedes")]:
            with self.subTest(field=field):
                data = verified_fixture()
                key = "verified_target" if field == "mapping_scope" else "review"
                data["decisions"][0][key][field] = value
                with self.assertRaisesRegex(ValueError, message):
                    ALIASES.validate_registry(data, {CANVAS: "116v"}, DIGEST)

    def test_unknown_fields_and_statuses_fail(self):
        for key, value in [("verification", "approved"), ("status", "probably_verified")]:
            data = registry()
            data["decisions"][0][key] = value
            with self.assertRaises(ValueError):
                ALIASES.validate_registry(data)

    def test_duplicate_or_empty_canvas_index_fails(self):
        for raw in [b"canvas_uri,yale_label\n", f"canvas_uri,yale_label\n{CANVAS},116v\n{CANVAS},116v\n".encode()]:
            with self.assertRaises(ValueError):
                ALIASES.read_index(raw)

    def test_cli_exit_codes_distinguish_blocked_lookup_and_invalid_data(self):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(ALIASES.main([]), 0)
            self.assertEqual(ALIASES.main(["--lookup", "yale_legacy_ms408_catalog", "117v"]), 1)
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "bad.json"
                path.write_text('{"schema_version": 999}')
                self.assertEqual(ALIASES.main(["--registry", str(path)]), 2)


if __name__ == "__main__":
    unittest.main()
