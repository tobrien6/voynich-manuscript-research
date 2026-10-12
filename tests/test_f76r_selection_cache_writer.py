"""Generated writes protect temporary fixtures without changing frozen pins."""

from copy import deepcopy
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import write_f76r_selection_cache as writer


def fixture(root):
    catalog_path = root / "data/transliterations.json"
    catalog_path.parent.mkdir(parents=True)
    sources = []
    for name in ["selected", "other"]:
        path = "data/imported/" + name + ".txt"
        source = root / path
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes((name + " synthetic bytes").encode())
        sources.append({"id": name, "path": path})
    catalog_path.write_text(json.dumps({"sources": sources}))
    inputs = {"catalog": {"path": "data/transliterations.json"},
              "inventory": {"path": "research/pilot/inventory.json"},
              "plan": {"path": "research/pilot/F76R_ANCHOR_PLAN.md"}}
    frozen = {"inputs": inputs, "implementation_sha256": {"select_f76r_anchors.py": "synthetic"},
              "selection": {"anchors": ["synthetic"]}}
    for relative in ["research/pilot/inventory.json", "research/pilot/F76R_ANCHOR_PLAN.md", writer.REVIEW,
                     "scripts/select_f76r_anchors.py", "scripts/repetition_moments.py",
                     "scripts/write_eva_token_cache.py", "scripts/eva_token_adapter.py",
                     "scripts/write_f76r_selection_cache.py"]:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("synthetic protected input\n")
    snapshot = root / writer.SNAPSHOT
    snapshot.write_text(json.dumps(frozen, indent=2, ensure_ascii=False) + "\n")
    protected = [catalog_path, *(root / source["path"] for source in sources), snapshot,
                 root / writer.REVIEW, *(root / item["path"] for item in inputs.values()),
                 *(root / "scripts" / name for name in ["select_f76r_anchors.py", "repetition_moments.py",
                     "write_eva_token_cache.py", "eva_token_adapter.py", "write_f76r_selection_cache.py"])]
    return frozen, list(dict.fromkeys(protected))


class SelectionCacheTests(unittest.TestCase):
    def run_writer(self, root, output):
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return writer.main(["--output", str(output)], root=root)

    def test_all_direct_symlink_and_hardlink_inputs_fail_before_production(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            frozen, protected = fixture(root)
            original = {path: path.read_bytes() for path in protected}
            outputs = list(protected) + [root / "data/raw/new-output.json"]
            for index, source in enumerate(protected):
                symbolic = root / f"symbolic-{index}.json"
                symbolic.symlink_to(source)
                hard = root / f"hard-{index}.json"
                os.link(source, hard)
                outputs.extend([symbolic, hard])
            for output in outputs:
                with self.subTest(output=output.name), patch.object(writer.selector, "selection") as producer:
                    self.assertEqual(self.run_writer(root, output), 1)
                    producer.assert_not_called()
                self.assertEqual({path: path.read_bytes() for path in protected}, original)
            self.assertFalse((root / "data/raw/new-output.json").exists())

    def test_new_alias_created_during_production_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            frozen, protected = fixture(root)
            original = {path: path.read_bytes() for path in protected}
            output = root / "late-alias.json"
            def produce(*, root):
                os.link(root / writer.SNAPSHOT, output)
                return frozen
            with patch.object(writer.selector, "selection", side_effect=produce):
                self.assertEqual(self.run_writer(root, output), 1)
            self.assertEqual({path: path.read_bytes() for path in protected}, original)

    def test_changed_production_cannot_replace_or_create_a_cache(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            frozen, protected = fixture(root)
            changed = deepcopy(frozen)
            changed["selection"]["anchors"] = ["different"]
            output = root / "cache.json"
            output.write_bytes(b"prior disposable cache")
            with patch.object(writer.selector, "selection", return_value=changed):
                self.assertEqual(self.run_writer(root, output), 1)
            self.assertEqual(output.read_bytes(), b"prior disposable cache")

    def test_good_fixture_emits_exact_bytes_and_keeps_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            frozen, protected = fixture(root)
            original = {path: path.read_bytes() for path in protected}
            output = root / "cache.json"
            with patch.object(writer.selector, "selection", return_value=frozen):
                self.assertEqual(self.run_writer(root, output), 0)
            self.assertEqual(output.read_bytes(), original[root / writer.SNAPSHOT])
            self.assertEqual({path: path.read_bytes() for path in protected}, original)

    def test_real_frozen_selection_replays_as_literal_bytes(self):
        snapshot = writer.ROOT / writer.SNAPSHOT
        original = snapshot.read_bytes()
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "f76r-cache.json"
            self.assertEqual(self.run_writer(writer.ROOT, output), 0)
            self.assertEqual(output.read_bytes(), original)
        self.assertEqual(snapshot.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
