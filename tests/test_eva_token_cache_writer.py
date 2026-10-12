import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import write_eva_token_cache as module
from scripts.eva_token_adapter import build


class TokenCacheWriterTests(unittest.TestCase):
    def run_cli(self, root, output):
        with patch.object(module, "ROOT", root), patch("sys.argv", [
                "writer", "--uncertain-spaces", "split", "--source", "ZL3b",
                "--output", str(output)]), contextlib.redirect_stdout(io.StringIO()), \
                contextlib.redirect_stderr(io.StringIO()):
            module.main()

    def source_fixture(self, root):
        raw = root / "data/raw"
        raw.mkdir(parents=True)
        sources = []
        for ident in ("ZL3b", "IT2a"):
            payload = b"#=IVTFF Eva- 2.0 M\n<f1r>\n<f1r.1,@P0> a,b.c\n"
            folder = raw if ident == "ZL3b" else root / "data/imported"
            folder.mkdir(parents=True, exist_ok=True)
            path = folder / f"{ident}.txt"
            path.write_bytes(payload)
            sources.append({"id": ident, "path": str(path.relative_to(root)),
                            "url": "urn:synthetic:" + ident, "alphabet": "Eva-",
                            "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()})
        catalog = root / "data/transliterations.json"
        catalog.write_text(json.dumps({"sources": sources}))
        return [catalog, *(root / source["path"] for source in sources)]

    def test_rejects_catalog_selected_and_unselected_source_paths_before_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protected = self.source_fixture(root)
            for output in protected:
                before = {path: path.read_bytes() for path in protected}
                with self.subTest(output=output.name), patch.object(module, "build") as producer:
                    with self.assertRaises(SystemExit) as error:
                        self.run_cli(root, output)
                    self.assertEqual(error.exception.code, 1)
                    producer.assert_not_called()
                self.assertEqual({path: path.read_bytes() for path in protected}, before)

    def test_rejects_symlink_hardlink_aliases_and_new_raw_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protected = self.source_fixture(root)
            outputs = [root / "data/raw/new-cache.json"]
            for index, source in enumerate(protected):
                symbolic = root / f"symbolic-{index}.json"
                symbolic.symlink_to(source)
                hard = root / f"hard-{index}.json"
                os.link(source, hard)
                outputs.extend((symbolic, hard))
            before = {path: path.read_bytes() for path in protected}
            for output in outputs:
                with self.subTest(output=output.name), patch.object(module, "build") as producer:
                    with self.assertRaises(SystemExit):
                        self.run_cli(root, output)
                    producer.assert_not_called()
                self.assertEqual({path: path.read_bytes() for path in protected}, before)
            self.assertFalse(outputs[0].exists())

    def test_separate_output_matches_real_producer_and_keeps_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protected = self.source_fixture(root)
            before = {path: path.read_bytes() for path in protected}
            output = root / "cache.json"
            expected = json.dumps(build("split", ("ZL3b",), root=root), indent=2, sort_keys=True) + "\n"
            self.run_cli(root, output)
            self.assertEqual(output.read_text(), expected)
            self.assertEqual({path: path.read_bytes() for path in protected}, before)


if __name__ == "__main__":
    unittest.main()
