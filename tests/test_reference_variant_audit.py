"""Synthetic tests for the extra-edition audit; reader tests live in test_ivtff."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.inspect_ivtff import audit_registry, summarize
from scripts.ivtff import parse_ivtff


PREFIX = b"#=IVTFF Eva- 2.0 M synthetic\n<f999r> <! $I=T>\n"


class ReferenceAuditTests(unittest.TestCase):
    def test_marker_presence_ignores_comments_and_nonexistent_loci(self):
        data = PREFIX + b"<f999r.1,@P0> abc<! ?, [a:b], @192;, other>\n<f999r.2,!L0> x,y?\n"
        report = summarize(parse_ivtff(data.decode("ascii")), data)
        self.assertEqual(report["declared_locus_record_count"], 2)
        self.assertEqual(report["present_locus_record_count"], 1)
        self.assertFalse(any(report["records_containing_markers_in_present_records_outside_comments"].values()))
        self.assertEqual(report["explicitly_nonexistent_locus_identifiers"], ["f999r.2,!L0"])

    def test_marker_presence_counts_records_rather_than_symbols(self):
        data = PREFIX + b"<f999r.1,@P0> a,b,c.[d:e].@192;.@193;\n"
        report = summarize(parse_ivtff(data.decode("ascii")), data)
        counts = report["records_containing_markers_in_present_records_outside_comments"]
        self.assertEqual(counts["uncertain_space_marker"], 1)
        self.assertEqual(counts["extended_character_code"], 1)

    def test_same_headers_can_have_different_text(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = root / "catalog.json"
            catalog.write_text('{"sources": []}')
            editions = []
            for ident, text in (("full", "a.@192;.b"), ("basic", "a.c.b")):
                data = PREFIX + f"<f999r.1,@P0> {text}\n".encode("ascii")
                (root / f"{ident}.txt").write_bytes(data)
                editions.append({"id": ident, "filename": f"{ident}.txt", "edition": ident,
                                 "url": "https://example.invalid/" + ident,
                                 "alphabet": "Eva-", "sha256": hashlib.sha256(data).hexdigest()})
            registry = {"base_catalog": "catalog.json", "base_source_ids": [], "editions": editions,
                        "access_date_local": "2026-10-11", "timezone": "America/New_York",
                        "license_statement_url": "https://example.invalid/license",
                        "exact_record_comparisons": [["full", "basic"]]}
            report = audit_registry(registry, root, root)
            self.assertEqual(report["exact_record_comparisons"][0]["shared_records_with_different_native_text"], 1)
            self.assertEqual(report["editions"][0]["header"], report["editions"][1]["header"])
            self.assertNotIn("a.@192;.b", json.dumps(report))
            editions[0]["sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "Pinned SHA-256 mismatch"):
                audit_registry(registry, root, root)

    def test_catalog_cannot_read_outside_repository(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "inside the repository"):
                audit_registry({"base_catalog": "../outside.json"}, Path(directory), Path(directory))


if __name__ == "__main__":
    unittest.main()
