"""Reject changed evidence links and unsupported image-review status."""

from copy import deepcopy
import json
import hashlib
from pathlib import Path
import tempfile
import unittest

from scripts.verify_f76r_review import REVIEW, geometry, verify


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.record = json.loads(REVIEW.read_bytes())

    def test_all_three_frozen_contexts_verify(self):
        self.assertEqual(verify(self.record), 3)

    def test_omitted_reordered_or_changed_native_context_fails(self):
        for kind in ["omitted", "order", "native"]:
            record = deepcopy(self.record)
            if kind == "omitted":
                record["records"].pop()
            elif kind == "order":
                record["records"].reverse()
            else:
                record["records"][0]["native_source_contexts"]["IT2a"]["locus"]["native_text"] = "corrected"
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                verify(record)

    def test_wrong_image_source_coordinate_or_fingerprint_fails(self):
        mutations = [("image", "image_oid", "wrong"),
                     ("coordinate_system", "units", "display pixels"),
                     (None, "selection_sha256", "0" * 64)]
        for section, key, value in mutations:
            record = deepcopy(self.record)
            target = record if section is None else record[section]
            target[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify(record)
        record = deepcopy(self.record)
        record["sources"][0]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            verify(record)

    def test_native_bounds_dimensions_and_url_are_checked(self):
        for kind in ["bounds", "dimensions", "url"]:
            record = deepcopy(self.record)
            item = record["inspection_files"][2]
            if kind == "bounds":
                item["native_region"][1] = 3769
            elif kind == "dimensions":
                item["width"] -= 1
            else:
                item["url"] = record["image"]["full_image_url"]
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                verify(record)
        for region in [[True, 1, 2, 3], [0, 0, 0, 3], [-1, 0, 2, 3], [0, 0, 11, 3]]:
            with self.assertRaises(ValueError):
                geometry(region, 10, 10)

    def test_confirmed_glyphs_source_correction_and_untouched_claim_fail(self):
        for kind in ["row", "glyph", "correction", "exposure"]:
            record = deepcopy(self.record)
            if kind == "row":
                record["records"][0]["source_row_association"]["status"] = "verified"
            elif kind == "glyph":
                record["glyph_adjudication"] = "confirmed"
            elif kind == "correction":
                record["source_corrections_applied"] = True
            else:
                record["exposure"]["untouched_evaluation"] = True
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                verify(record)

    def test_unresolved_attempt_and_alternative_region_can_be_retained(self):
        record = deepcopy(self.record)
        association = record["records"][1]["source_row_association"]
        association["status"] = "unresolved"
        association["other_candidate_regions"] = [[240, 1550, 2190, 210]]
        self.assertEqual(verify(record), 3)

    def test_wrong_local_image_bytes_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path / self.record["inspection_files"][0]["local_filename"]).write_bytes(b"wrong image")
            with self.assertRaisesRegex(ValueError, "Local inspected image bytes differ"):
                verify(self.record, path)

    def test_matching_hash_cannot_hide_wrong_bitmap_dimensions(self):
        # Minimal JPEG SOF header: the shared helper reads dimensions, not pixels.
        data = bytes.fromhex("ffd8ffc000080801c8007b01")  # 123 by 456
        record = deepcopy(self.record)
        item = record["inspection_files"][0]
        item["sha256"] = hashlib.sha256(data).hexdigest()
        item["bytes"] = len(data)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path / item["local_filename"]).write_bytes(data)
            with self.assertRaisesRegex(ValueError, "Local bitmap header dimensions differ"):
                verify(record, path)


if __name__ == "__main__":
    unittest.main()
