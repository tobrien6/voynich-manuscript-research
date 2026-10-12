"""Literal native text, region identity, pinned inputs and output aliases."""

from copy import deepcopy
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import build_f76r_viewer as viewer


class Capture(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.native, self.images, self.scripts, self.links = {}, [], 0, []
        self.current, self.pieces = None, []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "pre":
            self.current = (attrs["data-anchor"], attrs["data-source"], attrs["data-context"])
            self.pieces = []
        elif tag == "img":
            self.images.append(attrs)
        elif tag == "script":
            self.scripts += 1
        elif tag == "a":
            self.links.append(attrs["href"])

    def handle_data(self, text):
        if self.current is not None:
            self.pieces.append(text)

    def handle_endtag(self, tag):
        if tag == "pre":
            self.native[self.current] = "".join(self.pieces)
            self.current = None


class ViewerTests(unittest.TestCase):
    def setUp(self):
        self.review = json.loads((viewer.ROOT / viewer.INPUTS[0]).read_bytes())
        self.catalog = json.loads((viewer.ROOT / viewer.INPUTS[2]).read_bytes())
        self.settings = json.loads((viewer.ROOT / viewer.SETTINGS).read_bytes())
        self.template = (viewer.ROOT / viewer.TEMPLATE).read_text()

    def render(self, review):
        return viewer.render(review, self.catalog, self.settings, self.template, {})

    def test_every_native_locus_and_neighbor_round_trips_literally(self):
        parsed = Capture()
        parsed.feed(self.render(self.review))
        expected = {(row["key"], ident, context): locus["native_text"]
            for row in self.review["records"] for ident, sources in row["native_source_contexts"].items()
            for context, locus in sources.items() if locus is not None}
        self.assertEqual(parsed.native, expected)
        self.assertEqual(len(expected), 14)
        paths = {source["id"]: source["path"] for source in self.catalog["sources"]}
        expected_links = {"https://github.com/tobrien6/voynich-manuscript-research/blob/"
            + self.settings["accepted_input_commit"] + "/" + paths[ident] + "#L" + str(locus["source_file_line"])
            for row in self.review["records"] for ident, sources in row["native_source_contexts"].items()
            for locus in sources.values() if locus is not None}
        self.assertTrue(expected_links <= set(parsed.links))

    def test_region_images_and_provisional_status_are_preserved(self):
        page = self.render(self.review)
        parsed = Capture()
        parsed.feed(page)
        files = {item["id"]: item for item in self.review["inspection_files"]}
        self.assertEqual([item["src"] for item in parsed.images],
                         [files[row["inspection_file_id"]]["url"] for row in self.review["records"]])
        for attrs, row in zip(parsed.images, self.review["records"]):
            image = files[row["inspection_file_id"]]
            self.assertEqual((int(attrs["width"]), int(attrs["height"])), (image["width"], image["height"]))
        self.assertIn("Provisional row associations", page)
        self.assertEqual(parsed.scripts, 1)
        self.assertIn("<noscript>", page)

    def test_markup_in_native_text_cannot_create_executable_elements(self):
        review = deepcopy(self.review)
        text = 'x</pre><script>alert(1)</script>& <%> "literal"'
        review["records"][0]["native_source_contexts"]["ZL3b"]["locus"]["native_text"] = text
        parsed = Capture()
        parsed.feed(self.render(review))
        self.assertEqual(parsed.native[("f76r.1", "ZL3b", "locus")], text)
        self.assertEqual(parsed.scripts, 1)

    def input_fixture(self, root):
        for name in [viewer.SETTINGS, *viewer.INPUTS]:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((viewer.ROOT / name).read_bytes())

    def test_changed_input_fails_before_commit_lookup(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.input_fixture(root)
            (root / viewer.INPUTS[0]).write_bytes(b"changed input")
            with patch.object(viewer.subprocess, "run") as lookup:
                with self.assertRaisesRegex(ValueError, "fingerprint differs"):
                    viewer.build(root)
                lookup.assert_not_called()

    def test_wrong_accepted_commit_bytes_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.input_fixture(root)
            with patch.object(viewer.subprocess, "run", return_value=SimpleNamespace(stdout=b"wrong committed bytes")):
                with self.assertRaisesRegex(ValueError, "Accepted commit bytes differ"):
                    viewer.build(root)

    def test_generated_artifact_reproduces_from_actual_accepted_commit(self):
        self.assertEqual(viewer.build().encode("utf-8"), (viewer.ROOT / viewer.ARTIFACT).read_bytes())

    def test_temporary_input_aliases_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            self.input_fixture(root)
            for name in [viewer.TEMPLATE, "scripts/build_f76r_viewer.py"]:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("synthetic protected input")
            frozen = json.loads((root / viewer.writer.SNAPSHOT).read_bytes())
            for index, name in enumerate([viewer.SETTINGS, viewer.TEMPLATE, viewer.INPUTS[0], viewer.INPUTS[1]]):
                source = root / name
                before = source.read_bytes()
                for kind in ["hard", "symbolic"]:
                    output = root / f"{kind}-{index}.html"
                    if kind == "hard":
                        os.link(source, output)
                    else:
                        output.symlink_to(source)
                    with self.subTest(name=name, kind=kind), self.assertRaises(ValueError):
                        viewer.protect_output(output, root, frozen)
                    self.assertEqual(source.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
