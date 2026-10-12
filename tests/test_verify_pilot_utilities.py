import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class PilotUtilityTests(unittest.TestCase):
    def fixture(self, directory):
        inventory = json.loads((ROOT / "research/pilot/inventory.json").read_text())
        items = []
        for record in inventory["records"]:
            payload = ("synthetic image " + record["image_id"]).encode()
            (directory / (record["image_id"] + ".jpg")).write_bytes(payload)
            record["inspection_sha256"] = hashlib.sha256(payload).hexdigest()
            items.append({
                "id": record["canvas_uri"], "label": {"none": [record["yale_label"]]},
                "items": [{"items": [{"body": {
                    "id": record["full_image_url"], "width": record["source_width"],
                    "height": record["source_height"],
                    "service": [{"@id": record["inspection_image_url"].split("/full/")[0]}],
                }}]}],
            })
        manifest = directory / "manifest.json"
        manifest.write_text(json.dumps({"items": items}))
        path = directory / "inventory.json"
        path.write_text(json.dumps(inventory))
        return inventory, manifest, path

    def run_cli(self, manifest, inventory, *options):
        return subprocess.run([
            sys.executable, str(ROOT / "scripts/verify_pilot.py"),
            "--manifest", str(manifest), "--inventory", str(inventory), *options,
        ], capture_output=True, text=True)

    def test_complete_csv_retains_nested_evidence_and_separates_status(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inventory, manifest, path = self.fixture(root)
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            result = self.run_cli(manifest, path, "--images", str(root), "--csv")
            self.assertEqual(result.returncode, 0, result.stderr)
            rows = list(csv.DictReader(io.StringIO(result.stdout)))
            self.assertEqual(len(rows), 10)
            for expected, row in zip(inventory["records"], rows):
                self.assertEqual(set(row), set(expected))
                for key, value in expected.items():
                    self.assertEqual(json.loads(row[key]) if isinstance(value, (dict, list))
                                     else row[key], value if isinstance(value, (dict, list)) else str(value))
            self.assertNotIn("PASS:", result.stdout)
            self.assertIn("all ten local JPEG checksums match", result.stderr)
            self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})

    def test_changed_or_missing_image_fails_before_any_csv_is_emitted(self):
        for missing in (False, True):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                inventory, manifest, path = self.fixture(root)
                image = root / (inventory["records"][-1]["image_id"] + ".jpg")
                image.unlink() if missing else image.write_bytes(b"changed bytes")
                result = self.run_cli(manifest, path, "--images", str(root), "--csv")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertNotIn("PASS:", result.stderr)

    def test_existing_metadata_only_mode_does_not_require_image_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _, manifest, path = self.fixture(root)
            for image in root.glob("*.jpg"):
                image.unlink()
            result = self.run_cli(manifest, path)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("PASS: 10 selected canvases", result.stdout)
            self.assertIn("Image-file checksums were not checked", result.stdout)


if __name__ == "__main__":
    unittest.main()
