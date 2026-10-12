"""Checks for the sampling-unit mistakes this research audit guards against."""

import json
from pathlib import Path
import unittest

from audit_yale_manifest import audit


class ManifestAuditTests(unittest.TestCase):
    def test_combined_and_partial_scans_do_not_add_physical_folio_numbers(self):
        labels = ["70v (part)", "70v (part)", "71v and 72r", "85r (part) 86v (part) (part of 85-86 foldout)", "[Back cover]"]
        manifest = {
            "id": "https://example.org/manifest",
            "type": "Manifest",
            "items": [
                {"id": f"https://example.org/canvas/{i}", "type": "Canvas", "label": {"none": [label]}}
                for i, label in enumerate(labels)
            ],
        }
        result = audit(json.dumps(manifest).encode(), "2026-10-12T02:00:00Z")
        self.assertEqual(result["canvas_count"], 5)
        self.assertEqual(result["numbered_canvas_count"], 4)
        self.assertEqual(result["distinct_folio_number_count"], 5)
        self.assertEqual(result["distinct_folio_side_reference_count"], 5)
        self.assertEqual(result["partial_canvas_count"], 3)
        self.assertEqual(result["combined_canvas_count"], 2)

    def test_frozen_labels_reproduce_published_findings(self):
        directory = Path(__file__).resolve().parents[1] / "research" / "source-audit"
        published = json.loads((directory / "manifest-audit.json").read_text())
        result = audit((directory / "manifest-labels.json").read_bytes(), published["retrieved_at_utc"])
        # The extract has different bytes from the complete live manifest.
        result.pop("manifest_sha256")
        published.pop("manifest_sha256")
        self.assertEqual(result, published)

    def test_incompatible_manifest_version_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Presentation 3"):
            audit(b'{"@type":"sc:Manifest","sequences":[]}', "2026-10-12T02:00:00Z")


if __name__ == "__main__":
    unittest.main()
