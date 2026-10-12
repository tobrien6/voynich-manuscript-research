import csv
import io
import json
from pathlib import Path
import unittest

from scripts.audit_pilot_overlap import INVENTORIES, load_inventory, make_report


ROOT = Path(__file__).resolve().parents[1]
INDEX = {row["image_oid"]: row for row in csv.DictReader(io.StringIO((ROOT / "research/image-index/canvases.csv").read_text()))}
DIGEST = json.loads((ROOT / "research/image-index/audit.json").read_text())["manifest_sha256"]


class PilotOverlapTests(unittest.TestCase):
    def test_all_initial_records_preserve_shared_image_and_component_identity(self):
        records = []
        for name, metadata, _ in INVENTORIES:
            records.extend(load_inventory(name, (ROOT / metadata).read_bytes(), INDEX, DIGEST))
        coverage = json.loads((ROOT / "research/folio-alignment/transcription-image-coverage.json").read_text())
        report = make_report(records, coverage, [])
        self.assertEqual((report["record_count"], report["distinct_canvas_count"],
                          report["distinct_dependency_component_count"]), (30, 15, 14))
        self.assertEqual(report["explicit_label_leaf_count"], 17)
        overlap = report["pairwise_overlaps"][-1]
        self.assertEqual((len(overlap["shared_canvases"]), len(overlap["shared_dependency_groups"])), (9, 10))
        rosettes = next(c for c in report["canvases"] if c["image_oid"] == "1006231")
        self.assertEqual({r["source_target"] for r in rosettes["inventory_references"]}, {"85v", "86r", None})

    def test_removed_records_cannot_make_a_smaller_inventory_look_complete(self):
        original = json.loads((ROOT / INVENTORIES[0][1]).read_text())
        original["records"].pop()
        with self.assertRaisesRegex(ValueError, "require the declared 10"):
            load_inventory("section_beginnings", json.dumps(original).encode(), INDEX, DIGEST)

    def test_changed_image_identity_or_target_is_refused(self):
        for field, value, message in [("canvas_uri", "canvas:wrong", "identity differs"),
                                      ("target", "117v", "not explicitly named")]:
            changed = json.loads((ROOT / INVENTORIES[0][1]).read_text())
            changed["records"][0][field] = value
            with self.assertRaisesRegex(ValueError, message):
                load_inventory("section_beginnings", json.dumps(changed).encode(), INDEX, DIGEST)
        changed["manifest_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "manifest identity differs"):
            load_inventory("section_beginnings", json.dumps(changed).encode(), INDEX, DIGEST)

    def test_duplicate_canvas_cannot_inflate_one_inventory(self):
        rows = list(csv.DictReader(io.StringIO((ROOT / INVENTORIES[2][1]).read_text())))
        rows[-1] = dict(rows[0])
        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
        with self.assertRaisesRegex(ValueError, "repeated selected image"):
            load_inventory("standalone_rectos", stream.getvalue().encode(), INDEX, DIGEST)


if __name__ == "__main__":
    unittest.main()
