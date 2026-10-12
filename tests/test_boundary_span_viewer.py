from contextlib import redirect_stderr
from copy import deepcopy
import hashlib
from html.parser import HTMLParser
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.audit_eva_token_coverage import encoded
from scripts.build_boundary_span_viewer import BASE, INPUTS, ROOT, SETTINGS, TEMPLATE, load_inputs, main, package, render


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_data = False
        self.data = ''
        self.external_resources = []
        self.script_count = 0

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if tag == 'script':
            self.script_count += 1
            self.in_data = attributes.get('id') == 'span-data'
        if tag in ('img', 'iframe') or (tag == 'script' and 'src' in attributes) or (tag == 'link' and attributes.get('rel') == 'stylesheet'):
            self.external_resources.append((tag, attributes))

    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_data = False

    def handle_data(self, text):
        if self.in_data:
            self.data += text


class SpanViewerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings_raw, cls.settings, cls.payload = load_inputs()
        cls.template = (ROOT / TEMPLATE).read_text()

    def test_all_1628_literal_records_and_both_policy_denominators_are_preserved(self):
        parser = PageParser()
        parser.feed((ROOT / BASE / 'index.html').read_text())
        payload = json.loads(parser.data)
        self.assertEqual(encoded(payload), encoded(self.payload))
        self.assertEqual(len(payload['rows']), 1628)
        self.assertEqual(payload['policy_totals'], {'split': {'spans': 650, 'loci': 562}, 'join': {'spans': 978, 'loci': 767}})
        self.assertEqual(parser.external_resources, [])
        self.assertEqual(parser.script_count, 2)
        self.assertEqual(payload['parent_selected_native_loci'], 2940)

    def test_exact_input_commit_and_source_file_link_paths_are_pinned(self):
        for source in self.payload['sources']:
            self.assertIn('/blob/' + self.settings['input_commit'] + '/data/raw/', source['blob_url'])
            self.assertTrue(source['blob_url'].endswith(('ZL3b-n.txt', 'IT2a-n.txt')))
        row = next(r for r in self.payload['rows'] if r['native_locus_key'] == 'f67r1.1' and r['spacing'] == 'split')
        self.assertEqual((row['left_source_file_line'], row['right_source_file_line']), (2823, 1768))
        self.assertEqual(row['left_original_token_parts'], ['o', 'aiin'])
        self.assertEqual(row['right_original_token_parts'], ['oaiin'])

    def test_markup_and_template_marker_text_remain_inert_literal_data(self):
        payload = deepcopy(self.payload)
        text = '</script><svg onload="synthetic">&__REPORT_URL__'
        payload['sources'][0]['credit'] = text
        page = render(payload, self.template).decode()
        parser = PageParser()
        parser.feed(page)
        self.assertEqual(parser.script_count, 2)
        self.assertEqual(parser.external_resources, [])
        self.assertEqual(json.loads(parser.data)['sources'][0]['credit'], text)
        self.assertNotIn('<svg onload=', page)

    def test_missing_or_duplicated_template_markers_fail(self):
        for template in (self.template.replace('__DATA__', ''), self.template + '__REPORT_URL__'):
            with self.assertRaises(ValueError):
                render(self.payload, template)

    def test_input_byte_drift_is_rejected_before_reproduction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / SETTINGS).parent.mkdir(parents=True)
            (root / SETTINGS).write_bytes(self.settings_raw)
            (root / INPUTS[0]).write_bytes(b'changed input fixture')
            with patch('scripts.build_boundary_span_viewer.build_inventory', side_effect=AssertionError('must not run')) as producer, \
                    self.assertRaisesRegex(ValueError, 'input bytes changed'):
                load_inputs(root)
            producer.assert_not_called()

    def test_input_commit_blob_drift_is_rejected_before_reproduction(self):
        with patch('scripts.build_boundary_span_viewer.subprocess.check_output', return_value=b'different public fixture bytes'), \
                patch('scripts.build_boundary_span_viewer.build_inventory', side_effect=AssertionError('must not run')) as producer, \
                self.assertRaisesRegex(ValueError, 'input commit blob differs'):
            load_inputs()
        producer.assert_not_called()

    def test_unsafe_publisher_url_is_rejected_before_building_links(self):
        inventory = json.loads((ROOT / INPUTS[0]).read_bytes())
        catalog = json.loads((ROOT / INPUTS[1]).read_bytes())
        next(source for source in catalog['sources'] if source['id'] == 'ZL3b')['url'] = 'javascript:synthetic'
        catalog_raw = encoded(catalog)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / SETTINGS).parent.mkdir(parents=True)
            (root / 'data').mkdir()
            (root / INPUTS[0]).write_bytes((ROOT / INPUTS[0]).read_bytes())
            (root / INPUTS[1]).write_bytes(catalog_raw)
            settings = deepcopy(self.settings)
            settings['input_sha256'][str(INPUTS[1])] = hashlib.sha256(catalog_raw).hexdigest()
            (root / SETTINGS).write_bytes(encoded(settings))

            def blob(arguments, cwd):
                return (root / arguments[-1].split(':', 1)[1]).read_bytes()

            with patch('scripts.build_boundary_span_viewer.subprocess.check_output', side_effect=blob), \
                    patch('scripts.build_boundary_span_viewer.build_inventory', return_value=inventory), \
                    self.assertRaisesRegex(ValueError, 'unexpected publisher URL'):
                load_inputs(root)

    def test_complete_two_file_replay_and_provenance_fingerprints(self):
        files = package()
        for name, content in files.items():
            self.assertEqual(content, (ROOT / BASE / name).read_bytes())
        provenance = json.loads(files['provenance.json'])
        self.assertEqual(provenance['html_sha256'], hashlib.sha256(files['index.html']).hexdigest())
        self.assertEqual(provenance['embedded_span_records'], 1628)
        self.assertFalse(provenance['external_resources_loaded'])
        self.assertFalse(provenance['source_corrections_applied'])

    def test_late_package_aliases_reject_the_entire_output_set_before_writing(self):
        for alias_kind in ('symlink', 'hardlink'):
            with self.subTest(alias_kind=alias_kind), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / 'data').mkdir()
                (root / 'data/transliterations.json').write_text('{"sources":[]}')
                source = root / INPUTS[0]
                source.parent.mkdir(parents=True)
                source.write_bytes(b'unchanged public input fixture')
                output = root / 'viewer'

                def late_package():
                    output.mkdir()
                    target = output / 'provenance.json'
                    target.symlink_to(source) if alias_kind == 'symlink' else os.link(source, target)
                    return {'index.html': b'synthetic', 'provenance.json': b'{}'}

                with patch('sys.argv', ['viewer', '--output-dir', str(output)]), \
                        patch('scripts.build_boundary_span_viewer.ROOT', root), \
                        patch('scripts.build_boundary_span_viewer.package', side_effect=late_package), \
                        redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    main()
                self.assertEqual(source.read_bytes(), b'unchanged public input fixture')
                self.assertFalse((output / 'index.html').exists())

    def test_initial_implementation_guard_precedes_packaging(self):
        with patch('sys.argv', ['viewer', '--output-dir', str(ROOT / 'scripts')]), \
                patch('scripts.build_boundary_span_viewer.package', side_effect=AssertionError('must not run')) as producer, \
                redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            main()
        producer.assert_not_called()


if __name__ == '__main__':
    unittest.main()
