from copy import deepcopy
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import build_immediate_repeat_viewer as builder


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.case, self.pre_key, self.slot_key, self.code_slot = None, None, None, False
        self.native, self.slots, self.treatments, self.images = {}, {}, [], []
        self.treatment = None
        self.feed(html)

    def handle_starttag(self, tag, attributes):
        a = dict(attributes)
        if tag == 'section' and a.get('class') == 'case':
            self.case = a['id']
        elif tag == 'pre':
            self.pre_key = (self.case, a['data-source'], a['data-context'])
            self.native[self.pre_key] = ''
        elif tag == 'div' and a.get('class') == 'treatment':
            self.treatment = (self.case, a['data-source'], a['data-policy'])
            self.treatments.append(self.treatment)
        elif tag == 'li' and 'slot' in a.get('class', '').split():
            self.slot_key = (*self.treatment, int(a['data-slot']))
            self.slots[self.slot_key] = {'value': '', 'highlighted': 'repeated' in a['class'].split()}
        elif tag == 'code' and self.slot_key is not None:
            self.code_slot = True
        elif tag == 'img':
            self.images.append(a)

    def handle_data(self, data):
        if self.pre_key is not None:
            self.native[self.pre_key] += data
        if self.code_slot:
            self.slots[self.slot_key]['value'] += data

    def handle_endtag(self, tag):
        if tag == 'pre':
            self.pre_key = None
        elif tag == 'code':
            self.code_slot = False
        elif tag == 'li':
            self.slot_key = None


class ImmediateRepeatViewerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings, cls.selection, cls.review, cls.catalog = builder.load_inputs()
        cls.template = (builder.ROOT / builder.TEMPLATE).read_text()

    def render(self, selection=None, review=None):
        return builder.render(self.settings, selection or self.selection, review or self.review,
                              self.catalog, self.template)

    def test_all18_native_fields_and_exact_frozen_source_links(self):
        html = self.render()
        page = Page(html)
        sources = {s['id']: s for s in self.catalog['sources']}
        count = 0
        for case in self.selection['selected']:
            dom = 'case-' + case['locus_key'].replace('.', '-')
            for source in case['native_source_records']:
                for role, record in [('selected', source), ('preceding', source['preceding_native_record']),
                                     ('following', source['following_native_record'])]:
                    if record is None:
                        continue
                    self.assertEqual(page.native[dom, source['source_id'], role], record['native_text'])
                    self.assertIn('/blob/' + self.settings['accepted_input_commit'] + '/'
                                  + sources[source['source_id']]['path'] + '#L' + str(record['source_file_line']), html)
                    count += 1
        self.assertEqual(count, 18)
        self.assertEqual(len(page.native), 18)

    def test_all24_source_policy_arrays_and_original_event_slot_highlights(self):
        page = Page(self.render())
        expected = {}
        for case in self.selection['selected']:
            dom = 'case-' + case['locus_key'].replace('.', '-')
            for variant in case['variants']:
                repeated = set()
                for left, right, representation in variant['events']:
                    self.assertEqual(variant['slots'][left], representation)
                    self.assertEqual(variant['slots'][right], representation)
                    repeated.update([left, right])
                policy = variant['uncertain_spaces'] + '/' + variant['alternatives']
                for i, value in enumerate(variant['slots']):
                    expected[dom, variant['source_id'], policy, i] = {'value': 'excluded' if value is None else value,
                                                                    'highlighted': i in repeated}
        self.assertEqual(page.slots, expected)
        self.assertEqual(len(page.treatments), 24)
        self.assertEqual(sum(v['highlighted'] for v in page.slots.values()), 32)
        self.assertTrue(page.slots['case-f1r-15', 'ZL3b', 'split/exclude', 7]['highlighted'])
        self.assertTrue(page.slots['case-f1r-15', 'IT2a', 'split/exclude', 6]['highlighted'])
        self.assertFalse(any(v['highlighted'] for k, v in page.slots.items()
                             if k[0] == 'case-f4r-2' and k[1] == 'IT2a'))

    def test_ten_local_images_original_receipts_and_provisional_attribution(self):
        html = self.render()
        page = Page(html)
        self.assertEqual(len(page.images), 10)
        expected = {f['file_name']: f for c in self.review['cases'] for f in c['inspected_files'] if f['role'] != 'info'}
        actual = {i['src'].removeprefix('assets/'): i for i in page.images}
        self.assertEqual(set(actual), set(expected))
        for name, receipt in expected.items():
            self.assertEqual(int(actual[name]['width']), receipt['width'])
            self.assertEqual(int(actual[name]['height']), receipt['height'])
            self.assertEqual(actual[name]['data-hash'], receipt['sha256'])
            self.assertIn(receipt['url'], html)
        self.assertNotIn('<img src="https:', html)
        self.assertIn('Original nonblind AI notes from PR #154', html)
        self.assertEqual(html.count('Provisional mapping'), 3)
        self.assertNotIn('<details class="observations" open', html)
        for case in self.review['cases']:
            for field in ('direct_image_observation', 'source_informed_correspondence'):
                self.assertIn(escape(case[field]), html)

    def test_native_notes_and_slot_markup_are_escaped(self):
        selection, review = deepcopy(self.selection), deepcopy(self.review)
        payload = '<script>alert("bad")</script><img onerror="bad">'
        selection['selected'][0]['native_source_records'][0]['native_text'] = payload
        selection['selected'][0]['variants'][0]['slots'][0] = payload
        review['cases'][0]['direct_image_observation'] = payload
        html = self.render(selection, review)
        self.assertNotIn(payload, html)
        self.assertIn(escape(payload), html)
        self.assertEqual(html.count('<script>'), 1)

    def test_changed_fingerprints_commit_blobs_and_bool_schema_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in (builder.SETTINGS, *builder.INPUTS):
                p = root / name
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes((builder.ROOT / name).read_bytes())
            with patch.object(builder, 'ROOT', root), patch.object(builder.subprocess, 'check_output', return_value=b'wrong'):
                with self.assertRaisesRegex(ValueError, 'input blob'):
                    builder.load_inputs()
            (root / builder.INPUTS[0]).write_bytes(b'changed')
            with patch.object(builder, 'ROOT', root), self.assertRaisesRegex(ValueError, 'fingerprint'):
                builder.load_inputs()
            settings = deepcopy(self.settings)
            settings['schema_version'] = True
            (root / builder.SETTINGS).write_text(json.dumps(settings))
            with patch.object(builder, 'ROOT', root), self.assertRaisesRegex(ValueError, 'declaration'):
                builder.load_inputs()

    def test_only_declared_assets_and_no_mid_generation_drift(self):
        review = deepcopy(self.review)
        raws = {'first.jpg': b'first', 'metadata.json': b'metadata'}
        review['cases'] = [{'inspected_files': [{'file_name': n, 'sha256': builder.sha(v)} for n, v in raws.items()]}]
        with tempfile.TemporaryDirectory() as directory:
            images = Path(directory)
            for name, raw in raws.items():
                (images / name).write_bytes(raw)
            (images / 'unrelated-private.txt').write_bytes(b'unrelated fixture')
            with patch.object(builder, 'load_inputs', return_value=(self.settings, self.selection, review, self.catalog)), \
                    patch.object(builder, 'verify'), patch.object(builder, 'render', return_value='page'):
                result = builder.packet_bytes(images)
                self.assertEqual(set(result), {'index.html', 'packet.json', 'assets/first.jpg', 'assets/metadata.json'})
                (images / 'first.jpg').write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError, 'changed during generation'):
                    builder.packet_bytes(images)

    def test_fresh_outputs_early_and_construction_aliases(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            images = base / 'images'
            images.mkdir()
            original = images / 'input.jpg'
            original.write_bytes(b'original')
            for output in (builder.ROOT / 'viewer', images / 'viewer', base):
                with self.subTest(output=output), self.assertRaises(ValueError):
                    builder.protect_output(output, images)
            output = base / 'viewer'
            def construct(_):
                output.symlink_to(images, target_is_directory=True)
                return {'index.html': b'page'}
            with patch.object(builder, 'packet_bytes', side_effect=construct), self.assertRaises(ValueError):
                builder.write_packet(output, images)
            self.assertEqual(original.read_bytes(), b'original')
            self.assertFalse((images / 'index.html').exists())

    def test_complete_packet_replay_changed_extra_and_linked_files(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
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
                with self.assertRaisesRegex(ValueError, 'bytes differ'):
                    builder.check_packet(output, images)
                image.unlink()
                other = images / 'original.jpg'
                other.write_bytes(b'pixels')
                os.link(other, image)
                with self.assertRaisesRegex(ValueError, 'linked'):
                    builder.check_packet(output, images)
                image.unlink()
                image.symlink_to(other)
                with self.assertRaisesRegex(ValueError, 'linked'):
                    builder.check_packet(output, images)
                image.unlink()
                image.write_bytes(b'pixels')
                (output / 'extra.txt').write_bytes(b'extra')
                with self.assertRaisesRegex(ValueError, 'unexpected'):
                    builder.check_packet(output, images)


if __name__ == '__main__':
    unittest.main()
