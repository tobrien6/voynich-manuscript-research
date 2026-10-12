import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from align_folio_canvases import align


def make_canvas(label, oid):
    uri = f"https://collections.library.yale.edu/manifests/2002046/canvas/{oid}"
    service = f"https://collections.library.yale.edu/iiif/2/{oid}"
    return {
        "id": uri, "type": "Canvas", "label": {"none": [label]},
        "items": [{"items": [{"motivation": "painting", "target": uri, "body": {
            "type": "Image", "id": service + "/full/full/0/default.jpg",
            "service": [{"@id": service}], "width": 100, "height": 200,
        }}]}],
    }


def fixture(labels):
    return json.dumps({
        "id": "https://collections.library.yale.edu/manifests/2002046",
        "type": "Manifest",
        "items": [
            make_canvas(label, index + 1)
            for index, label in enumerate(labels)
        ],
    }).encode()


class FolioCanvasAlignmentTests(unittest.TestCase):
    def test_every_partial_canvas_is_kept_in_manifest_order(self):
        result = align(fixture(["70v (part)", "70v (part)"]), ["f70v"], "2026-10-11")
        entry = result["entries"][0]
        self.assertEqual(entry["requested_identifier"], "f70v")
        self.assertEqual(entry["canonical_folio_side"], "70v")
        self.assertEqual([match["canvas_index"] for match in entry["matches"]], [0, 1])
        self.assertTrue(all(match["partial_view"] for match in entry["matches"]))

    def test_combined_canvas_matches_both_sides_without_assigning_panels(self):
        result = align(fixture(["85r (part) 86v (part) (part of 85-86 foldout)"]), ["85r", "86v", "85v"], "2026-10-11")
        first, second, third = result["entries"]
        self.assertEqual(first["matches"], second["matches"])
        self.assertTrue(first["matches"][0]["combined_view"])
        self.assertEqual(third["status"], "label_unmatched")

    def test_no_terminal_folio_alias_or_panel_suffix_is_invented(self):
        result = align(fixture(["116v", "67r", "[Back flyleaf recto]"]), ["117v", "f67r1", "  F116V  "], "2026-10-11")
        self.assertEqual([entry["status"] for entry in result["entries"]], ["label_unmatched", "unsupported_identifier", "matched"])
        self.assertEqual(result["entries"][2]["canonical_folio_side"], "116v")

    def test_image_references_come_from_the_shared_index(self):
        result = align(fixture(["1r"]), ["1r"], "2026-10-11")
        match = result["entries"][0]["matches"][0]
        self.assertEqual(match["image_urls"], ["https://collections.library.yale.edu/iiif/2/1/full/full/0/default.jpg"])
        self.assertEqual(match["image_oid"], "1")
        self.assertEqual(result["access_date"], "2026-10-11")

    def test_cli_writes_the_incomplete_report_and_returns_failure(self):
        script = Path(__file__).with_name("align_folio_canvases.py")
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.json"
            manifest.write_bytes(fixture(["116v"]))
            output = Path(directory) / "join.json"
            command = [sys.executable, str(script), str(manifest), "117v", "--access-date", "2026-10-11", "--output", str(output)]
            failed = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(failed.returncode, 2)
            self.assertEqual(json.loads(output.read_text())["label_unmatched_count"], 1)
            allowed = subprocess.run(command + ["--allow-incomplete"], capture_output=True, text=True)
            self.assertEqual(allowed.returncode, 0)

    def test_sha_mismatch_prevents_output(self):
        script = Path(__file__).with_name("align_folio_canvases.py")
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.json"
            manifest.write_bytes(fixture(["1r"]))
            output = Path(directory) / "join.json"
            command = [sys.executable, str(script), str(manifest), "1r", "--expected-sha256", "0" * 64, "--access-date", "2026-10-11", "--output", str(output)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
