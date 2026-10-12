from contextlib import redirect_stderr
import io
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts.audit_eva_token_coverage import encoded
from scripts.audit_historical_record_projections import ROOT, compare_records, build, main


def historical(bodies, page='f1r', code='H'):
    return [SimpleNamespace(page=page, unit='P', body=body, transcriber=code,
                            locator=f'{page}.P.{i};{code}', physical_line=10+i)
            for i, body in enumerate(bodies)]


def modern(bodies, page='f1r'):
    return SimpleNamespace(loci=[SimpleNamespace(page=page, text=body, kind='P0',
                          transcriber=None, present=True, identifier=f'{page}.{i},+P0',
                          line_number=20+i) for i, body in enumerate(bodies)])


def fixture_root(root):
    paths = ['data/transliterations.json', 'data/historical/catalog.json',
             'data/historical/native.zip', 'data/raw/native.txt',
             'scripts/audit_historical_record_projections.py', 'scripts/paragraph_token_corpus.py',
             'research/historical/lowercase-projection.json',
             'research/historical/RECORD_PROJECTION_PLAN.md']
    for p in paths:
        path = root / p
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('public synthetic fixture')
    (root / paths[0]).write_text(json.dumps({'sources': [{'path': 'data/raw/native.txt'}]}))
    return [root / p for p in paths]


class RecordProjectionTests(unittest.TestCase):
    def test_permutation_preserves_bag_not_native_record_order(self):
        report = compare_records(historical(['ab', 'cd']), modern(['cd', 'ab']))
        page = report['page_profiles'][0]
        self.assertTrue(page['nonempty_record_projection_bags_equal'])
        self.assertFalse(page['nonempty_record_projection_order_equal'])
        self.assertFalse(page['joined_lowercase_streams_equal'])
        self.assertTrue(page['lowercase_symbol_frequencies_equal'])
        self.assertEqual(report['summary']['equal_bag_different_record_order_page_ids'], ['f1r'])
        self.assertEqual(report['summary']['one_to_one_lossy_projection_groups'], 2)

    def test_duplicate_groups_remain_ambiguous_without_pairing(self):
        report = compare_records(historical(['ab', 'a.b']), modern(['ab']))
        group = report['page_profiles'][0]['projection_groups'][0]
        self.assertEqual(group['status'], 'ambiguous_shared_projection')
        self.assertEqual(len(group['historical_H_records']), 2)
        self.assertEqual(len(group['modern_IT2a_present_records']), 1)
        self.assertEqual(report['summary']['one_to_one_lossy_projection_groups'], 0)
        self.assertFalse(report['page_profiles'][0]['nonempty_record_projection_bags_equal'])

    def test_joined_stream_hides_changed_record_boundaries(self):
        report = compare_records(historical(['a', 'bc']), modern(['ab', 'c']))
        page = report['page_profiles'][0]
        self.assertTrue(page['joined_lowercase_streams_equal'])
        self.assertFalse(page['nonempty_record_projection_bags_equal'])
        self.assertEqual(report['summary']['equal_joined_stream_different_record_bag_page_ids'], ['f1r'])

    def test_empty_records_preserve_denominator_and_never_supply_matches(self):
        report = compare_records(historical(['ab', '%%%!-']), modern(['ab']))
        page = report['page_profiles'][0]
        self.assertTrue(page['nonempty_record_projection_order_equal'])
        self.assertEqual(page['historical_H']['selected_native_records'], 2)
        self.assertEqual(page['historical_H']['empty_projection_records'][0]['native_locator'], 'f1r.P.1;H')
        empty = compare_records(historical(['%%%']), modern(['???']))['page_profiles'][0]
        self.assertIsNone(empty['nonempty_record_projection_bags_equal'])
        self.assertIsNone(empty['joined_lowercase_streams_equal'])
        self.assertEqual(empty['projection_groups'], [])

    def test_comments_metadata_and_case_follow_source_specific_rules(self):
        page = compare_records(historical(['a{human}b!C']), modern(['a<!human>b<@X=v>C']))['page_profiles'][0]
        self.assertTrue(page['nonempty_record_projection_order_equal'])
        self.assertEqual(page['projection_groups'][0]['projected_lowercase_symbols'], 2)
        different = compare_records(historical(['a{human}b']), modern(['a{human}b']))['page_profiles'][0]
        self.assertFalse(different['nonempty_record_projection_bags_equal'])

    def test_exact_pages_nonexistent_and_non_h_selection_are_preserved(self):
        old = historical(['ab'], page='f101r1') + historical(['ignored'], page='f101r1', code='U')
        new = modern(['ab', 'ghost'], page='f101r')
        new.loci[-1].present = False
        report = compare_records(old, new)
        self.assertEqual(report['summary']['shared_exact_page_ids'], 0)
        self.assertEqual(report['summary']['historical_H_native_records'], 1)
        self.assertEqual(report['summary']['modern_IT2a_present_native_records'], 1)
        self.assertEqual(report['summary']['historical_only_page_ids'], ['f101r1'])
        self.assertEqual(report['summary']['modern_only_page_ids'], ['f101r'])
        self.assertEqual(report['modern_nonexistent_loci_excluded'], ['f101r.1,+P0'])

    def test_invalid_source_contracts_and_digest_collisions_fail(self):
        old = historical(['ab'])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            compare_records(old + old, modern(['ab']))
        new = modern(['ab']); new.loci[0].transcriber = 'H'
        with self.assertRaisesRegex(ValueError, 'single-source'):
            compare_records(old, new)
        with self.assertRaisesRegex(ValueError, 'selected'):
            compare_records([], modern(['ab']))
        with patch('scripts.audit_historical_record_projections.digest', return_value='same'):
            with self.assertRaisesRegex(ValueError, 'collision'):
                compare_records(historical(['ab', 'cd']), modern(['ab', 'cd']))

    def test_outputs_reject_direct_symlink_hardlink_input_and_reader_aliases(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'repo'
            protected = fixture_root(root)
            loaded = ([], None, {}, set(protected))
            for i, target in enumerate(protected):
                before = target.read_bytes()
                symlink = Path(d) / f'sym-{i}'; symlink.symlink_to(target)
                hardlink = Path(d) / f'hard-{i}'; os.link(target, hardlink)
                for output in (target, symlink, hardlink):
                    with self.subTest(target=target.name, output=output.name), \
                            patch('scripts.audit_historical_record_projections.ROOT', root), \
                            patch('scripts.paragraph_token_corpus.__file__', str(root / 'scripts/paragraph_token_corpus.py')), \
                            patch('scripts.audit_historical_record_projections.load_inputs', return_value=loaded), \
                            patch('scripts.audit_historical_record_projections.build', side_effect=AssertionError('must not build')) as producer, \
                            patch('sys.argv', ['audit', '--output', str(output)]), \
                            redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                        main()
                    producer.assert_not_called()
                    self.assertEqual(target.read_bytes(), before)

    def test_failed_complete_check_preserves_output_and_numeric_types(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'repo'; protected = fixture_root(root)
            loaded = ([], None, {}, set(protected))
            check = Path(d) / 'check.json'; output = Path(d) / 'output.json'
            for value in ['{"count": true}', '{"count": 1.0}', '{"count": 1, "count": 1}']:
                check.write_text(value); output.write_bytes(b'preserved')
                with patch('scripts.audit_historical_record_projections.ROOT', root), \
                        patch('scripts.audit_historical_record_projections.load_inputs', return_value=loaded), \
                        patch('scripts.audit_historical_record_projections.build', return_value={'count': 1}), \
                        patch('sys.argv', ['audit', '--check', str(check), '--output', str(output)]), \
                        redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    main()
                self.assertEqual(output.read_bytes(), b'preserved')

    def test_late_output_aliases_from_calculation_or_serialization_preserve_inputs(self):
        for stage in ('calculation', 'serialization'):
            for kind in ('symlink', 'hardlink'):
                with self.subTest(stage=stage, kind=kind), tempfile.TemporaryDirectory() as d:
                    root = Path(d) / 'repo'; protected = fixture_root(root)
                    target = root / 'data/raw/native.txt'; before = target.read_bytes()
                    output = Path(d) / 'output.json'
                    loaded = ([], None, {}, set(protected))
                    result = {'summary': {'shared_exact_page_ids': 0}}
                    def introduce_alias():
                        output.symlink_to(target) if kind == 'symlink' else os.link(target, output)
                    def calculate(*args):
                        if stage == 'calculation':
                            introduce_alias()
                        return result
                    def serialize(value):
                        raw = encoded(value)
                        if stage == 'serialization':
                            introduce_alias()
                        return raw
                    with patch('scripts.audit_historical_record_projections.ROOT', root), \
                            patch('scripts.audit_historical_record_projections.load_inputs', return_value=loaded), \
                            patch('scripts.audit_historical_record_projections.build', side_effect=calculate), \
                            patch('scripts.audit_historical_record_projections.encoded', side_effect=serialize), \
                            patch('sys.argv', ['audit', '--output', str(output)]), \
                            redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                        main()
                    self.assertEqual(target.read_bytes(), before)

    def test_real_complete_report_replay(self):
        report = build()
        self.assertEqual(report['summary']['shared_exact_page_ids'], 223)
        self.assertEqual(report['summary']['historical_H_native_records'], 5214)
        self.assertEqual(report['summary']['modern_IT2a_present_native_records'], 5214)
        self.assertFalse(report['usable_as_verified_locus_crosswalk'])
        self.assertEqual(encoded(report), (ROOT / 'research/historical/record-projections.json').read_bytes())


if __name__ == '__main__':
    unittest.main()
