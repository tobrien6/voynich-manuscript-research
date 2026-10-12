import copy
from html import escape
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import build_y_lookup_viewer as builder


class LookupViewerTests(unittest.TestCase):
    def setUp(self):
        self.settings, self.selection, self.review, self.catalog = builder.load_inputs()
        self.template = (builder.ROOT / builder.TEMPLATE).read_text()

    def render(self, selection=None, review=None):
        return builder.render(self.settings, selection or self.selection, review or self.review, self.catalog, self.template)

    def test_every_native_context_is_literal_and_linked_to_accepted_source_line(self):
        html = self.render()
        by_source = {item['id']: item for item in self.catalog['sources']}
        count = 0
        for pair in self.selection['selection']['selected_pairs']:
            for name in ('target_native_context', 'reference_native_context'):
                for source, contexts in pair[name].items():
                    for context in ('locus', 'preceding', 'following'):
                        locus = contexts[context]
                        if locus is not None:
                            self.assertIn(escape(locus['text']), html)
                            self.assertIn(f'/blob/{self.settings["accepted_input_commit"]}/{by_source[source]["path"]}#L{locus["file_line"]}', html)
                            count += 1
        self.assertEqual(count, 24)
        self.assertIn('choky', html)
        self.assertIn('shoky', html)
        self.assertIn('development slot 2', html)
        self.assertIn('development slot 3', html)

    def test_both_pairs_twelve_page_windows_and_provisional_attribution_remain_visible(self):
        html = self.render()
        self.assertEqual(html.count('<section class="pair"'), 2)
        self.assertEqual(html.count('<figure>'), 13)
        self.assertIn('f17r.2 → f18r.6', html)
        self.assertIn('f19v.4 → f35v.15', html)
        self.assertIn('Provisional associations', html)
        self.assertIn('nonblind AI observations from PR #115', html)
        self.assertNotIn('<details class="observations" open', html)
        for resource in self.review['retrieved_resources']:
            if resource['name'].endswith('.jpg') or resource['name'] == 'basic-eva.gif':
                self.assertIn(resource['url'], html)
                self.assertIn(resource['sha256'], html)
        self.assertIn('assets/basic-eva.gif', html)
        self.assertNotIn('<img src="https:', html)

    def test_native_markup_and_old_observations_are_escaped(self):
        selection, review = copy.deepcopy(self.selection), copy.deepcopy(self.review)
        payload = '<script>alert("injected")</script><img onerror="bad">'
        selection['selection']['selected_pairs'][0]['target_native_context']['ZL3b']['locus']['text'] = payload
        review['cases'][0]['comparison'] = payload
        html = self.render(selection, review)
        self.assertIn(escape(payload), html)
        self.assertNotIn(payload, html)

    def test_changed_fingerprint_and_registered_blob_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            settings_path = root / builder.SETTINGS
            settings_path.parent.mkdir(parents=True)
            for path in builder.INPUTS:
                target = root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((builder.ROOT / path).read_bytes())
            settings_path.write_text(json.dumps(self.settings))
            with patch.object(builder, 'ROOT', root), patch.object(builder.subprocess, 'check_output', return_value=b'old blob'):
                with self.assertRaisesRegex(ValueError, 'input blob'):
                    builder.load_inputs()
            (root / builder.INPUTS[0]).write_bytes(b'changed')
            with patch.object(builder, 'ROOT', root), self.assertRaisesRegex(ValueError, 'fingerprint'):
                builder.load_inputs()

    def test_only_declared_assets_are_copied_and_mid_generation_drift_is_rejected(self):
        selection, review = copy.deepcopy(self.selection), copy.deepcopy(self.review)
        names = ['first.jpg', 'metadata.json']
        raws = {name: name.encode() for name in names}
        review['retrieved_resources'] = [{'name': name, 'sha256': builder.sha(raw)} for name, raw in raws.items()]
        with tempfile.TemporaryDirectory() as folder:
            images = Path(folder)
            for name, raw in raws.items(): (images / name).write_bytes(raw)
            (images / 'unrelated-private.txt').write_bytes(b'unrelated fixture that must stay local')
            with patch.object(builder, 'load_inputs', return_value=(self.settings, selection, review, self.catalog)), \
                    patch.object(builder, 'verify_record'), patch.object(builder, 'render', return_value='page'):
                result = builder.packet_bytes(images)
                self.assertEqual(set(result), {'index.html', 'packet.json', 'assets/first.jpg', 'assets/metadata.json'})
                (images / 'first.jpg').write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError, 'changed during generation'):
                    builder.packet_bytes(images)

    def test_fresh_outputs_reject_repository_input_ancestors_and_directory_links(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            images, output = base / 'images', base / 'viewer'
            images.mkdir()
            (images / 'source.jpg').write_bytes(b'original')
            builder.protect_output(output, images)
            for path in (builder.ROOT / 'generated-viewer', images / 'nested', base):
                with self.subTest(path=path), self.assertRaises(ValueError):
                    builder.protect_output(path, images)
            empty = base / 'empty'
            empty.mkdir()
            alias = base / 'alias'
            alias.symlink_to(empty, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'symbolic link'):
                builder.protect_output(alias, images)

    def test_packet_replay_detects_changed_bytes_extra_files_and_link_aliases(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            images, output = base / 'images', base / 'viewer'
            images.mkdir()
            files = {'index.html': b'page', 'assets/image.jpg': b'pixels', 'packet.json': b'manifest'}
            with patch.object(builder, 'packet_bytes', return_value=files):
                builder.write_packet(output, images)
                builder.check_packet(output, images)
                with self.assertRaisesRegex(ValueError, 'fresh empty'):
                    builder.write_packet(output, images)
                image = output / 'assets/image.jpg'
                image.write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError, 'file differs'):
                    builder.check_packet(output, images)
                image.unlink()
                original = images / 'original.jpg'
                original.write_bytes(b'pixels')
                os.link(original, image)
                with self.assertRaisesRegex(ValueError, 'linked'):
                    builder.check_packet(output, images)
                image.unlink()
                image.symlink_to(original)
                with self.assertRaisesRegex(ValueError, 'linked'):
                    builder.check_packet(output, images)
                image.unlink()
                image.write_bytes(b'pixels')
                (output / 'extra.txt').write_bytes(b'extra')
                with self.assertRaisesRegex(ValueError, 'unexpected'):
                    builder.check_packet(output, images)


if __name__ == '__main__':
    unittest.main()
