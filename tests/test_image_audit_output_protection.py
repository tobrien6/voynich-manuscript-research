"""Synthetic writer-boundary checks; no manuscript inputs are modified."""

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import audit_transcription_images as module


def fixture(root):
    catalog = root / "data/transliterations.json"
    raw = root / "data/raw/fixture.txt"
    index = root / "research/image-index"
    raw.parent.mkdir(parents=True)
    raw.write_bytes(b"synthetic pinned input")
    catalog.write_text(json.dumps({"sources": [{"path": "data/raw/fixture.txt"}]}), encoding="utf-8")
    index.mkdir(parents=True)
    index_paths = [index / name for name in ("canvases.csv", "folio-sides.csv", "audit.json")]
    for path in index_paths:
        path.write_bytes(b"synthetic pinned image index")
    manifest, split = root / "manifest.json", root / "split.json"
    manifest.write_bytes(b"synthetic manifest")
    split.write_bytes(b"synthetic split")
    return [manifest, split, catalog, raw, *index_paths], manifest, split


class ImageAuditOutputProtectionTests(unittest.TestCase):
    def test_direct_input_paths_are_rejected_without_changing_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs, manifest, split = fixture(root)
            for target in inputs:
                before = target.read_bytes()
                with self.subTest(target=target.name), self.assertRaisesRegex(ValueError, "must not overwrite"):
                    module.protect_output(target, manifest, split, root=root)
                self.assertEqual(target.read_bytes(), before)

    def test_symlink_and_hardlink_aliases_cannot_bypass_input_protection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs, manifest, split = fixture(root)
            for number, source in enumerate(inputs):
                before = source.read_bytes()
                for kind in ("symlink", "hardlink"):
                    alias = root / f"alias-{number}-{kind}.json"
                    if kind == "symlink":
                        alias.symlink_to(source)
                    else:
                        alias.hardlink_to(source)
                    with self.subTest(source=source.name, kind=kind), self.assertRaisesRegex(ValueError, "must not overwrite"):
                        module.protect_output(alias, manifest, split, root=root)
                    self.assertEqual(source.read_bytes(), before)

    def test_raw_and_index_directories_cannot_receive_new_report_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, manifest, split = fixture(root)
            for parent in (root / "data/raw", root / "research/image-index"):
                target = parent / "new-report.json"
                with self.subTest(parent=parent.name), self.assertRaisesRegex(ValueError, "must not overwrite"):
                    module.protect_output(target, manifest, split, root=root)
                self.assertFalse(target.exists())

    def test_cli_refuses_input_destination_before_audit_or_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs, manifest, split = fixture(root)
            for target in (manifest, split):
                before = {path: path.read_bytes() for path in inputs}
                stdout, stderr = io.StringIO(), io.StringIO()
                argv = ["audit", "--manifest", str(manifest), "--split", str(split), "--output", str(target)]
                with patch.object(module, "ROOT", root), patch.object(module, "audit") as audit, \
                        patch("sys.argv", argv), contextlib.redirect_stdout(stdout), \
                        contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as error:
                    module.main()
                self.assertEqual(error.exception.code, 1)
                audit.assert_not_called()
                self.assertIn("must not overwrite", stderr.getvalue())
                self.assertNotIn("PASS:", stdout.getvalue())
                self.assertEqual({path: path.read_bytes() for path in inputs}, before)

    def test_separate_report_output_remains_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inputs, manifest, split = fixture(root)
            before = {path: path.read_bytes() for path in inputs}
            output = root / "report.json"
            result = {"synthetic": "writer-boundary fixture only"}
            argv = ["audit", "--manifest", str(manifest), "--output", str(output)]
            with patch.object(module, "ROOT", root), patch.object(module, "audit", return_value=result), \
                    patch("sys.argv", argv):
                module.main()
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), result)
            self.assertEqual({path: path.read_bytes() for path in inputs}, before)


if __name__ == "__main__":
    unittest.main()
