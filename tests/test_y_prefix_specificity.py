import copy
from collections import Counter
from fractions import Fraction
import json
import os
from contextlib import redirect_stderr
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.ivtff import parse_ivtff
from scripts import y_prefix_specificity as controls


def paired(left, right=None):
    return [({'id': name, 'sha256': 'synthetic'}, parse_ivtff('#=IVTFF Eva- 2.0 M\n' + text))
            for name, text in (('ZL3b', left), ('IT2a', right if right is not None else left))]


def partition(evaluation=('2',)):
    return {'units': [{'unit_id': 'unit:' + family, 'selected_source_pages': ['f' + family + 'r'],
                       'partition': 'dictionary_development' if family == '1' else 'diagnostic_evaluation'}
                      for family in ('1', *evaluation)]}


def report(sources, units):
    return controls.control_report(sources, units, controls.source.analyze(sources, units))


class PrefixControlTests(unittest.TestCase):
    def test_four_lookup_cells_and_opportunity_restriction_for_each_prefix(self):
        for prefix in controls.PREFIXES:
            counts = Counter({'a': 1, prefix + 'b': 2, 'c': 1, prefix + 'c': 1})
            summary, gain = controls.lookup_summary([prefix + c for c in 'abcd'], counts, prefix)
            self.assertEqual(gain, Fraction(0))
            self.assertEqual([summary[key] for key in ('both_match', 'neither_matches', 'original_only', 'stripped_only')], [1] * 4)
            absent = [prefix + 'a', prefix + 'd']
            present = [prefix + 'b', prefix + 'c']
            self.assertEqual(controls.lookup_summary(absent, counts, prefix)[1], Fraction(1, 2))
            self.assertEqual(controls.lookup_summary(present, counts, prefix)[1], Fraction(-1, 2))
            for invalid in (prefix, prefix.upper() + 'a', prefix + '?', prefix + 'ä'):
                with self.subTest(prefix=prefix, invalid=invalid), self.assertRaises(ValueError):
                    controls.lookup_summary([invalid], counts, prefix)

    def test_bins_have_fixed_boundaries_and_reject_invalid_counts(self):
        self.assertEqual([controls.frequency_bin(n) for n in (0, 1, 2, 100)], ['0', '1', '2+', '2+'])
        self.assertEqual([controls.length_bin(n) for n in (2, 4, 5, 7, 8, 100)], ['2-4', '2-4', '5-7', '5-7', '8+', '8+'])
        for invalid in (-1, 1.5, True):
            with self.assertRaises(ValueError):
                controls.frequency_bin(invalid)
        for invalid in (1, 2.5, True):
            with self.assertRaises(ValueError):
                controls.length_bin(invalid)

    def test_matched_cells_and_units_have_equal_weight_and_development_only_frequency(self):
        text = '<f1r>\n<f1r.1,@P0> z.a.yb.yb.d\n<f2r>\n'
        text += '<f2r.1,@P0> ya.ye\n<f2r.2,+P0> ya.z\n<f2r.3,+P0> ya.z\n<f2r.4,+P0> yb.yb\n<f3r>\n'
        text += ''.join(f'<f3r.{n},+P0> ye.yd.z\n' for n in range(1, 10))
        result = report(paired(text), partition(('2', '3')))
        self.assertEqual(result['comparison_b_common_unit_ids'], ['unit:2', 'unit:3'])
        self.assertEqual([(c['unit_id'], c['frequency_bin']) for c in result['comparison_b_common_cells']],
                         [('unit:2', '0'), ('unit:2', '2+'), ('unit:3', '0')])
        for variant in result['variants']:
            b = variant['comparison_b']
            self.assertEqual(b['matched_cells_equal_weight_within_unit'],
                             {'first_gain': 0, 'other_gain': .25, 'first_minus_other_gain': -.25})
            self.assertEqual(b['unmatched_y_on_same_units'],
                             {'first_gain': .25, 'other_gain': .25, 'first_minus_other_gain': 0})
            self.assertEqual(b['matched_minus_unmatched_selectivity'], -.25)
            unit = variant['evaluation_units'][0]
            absent = next(c for c in unit['y_opportunity_cells'] if c['frequency_bin'] == '0' and c['length_bin'] == '2-4')
            repeated = next(c for c in unit['y_opportunity_cells'] if c['frequency_bin'] == '2+' and c['length_bin'] == '2-4')
            # Three evaluation occurrences of ya do not make its development frequency repeated.
            self.assertEqual(absent['first_slot']['candidate_tokens'], 3)
            self.assertEqual(repeated['first_slot']['candidate_tokens'], 1)
            self.assertEqual(variant['vocabulary']['development_internal_tokens'], 4)
        self.assertFalse(result['valid_candidate_holdout'])
        self.assertNotIn('decision', result)

    def test_prefix_common_cohort_requires_all_prefixes_and_all_variants(self):
        text = '<f1r>\n<f1r.1,@P0> z.a.b\n<f2r>\n<f2r.1,@P0> ya.yb\n<f2r.2,+P0> qa.qb\n<f2r.3,+P0> oa.ob\n'
        complete = report(paired(text), partition())
        self.assertEqual(complete['comparison_a_common_unit_ids'], ['unit:2'])
        for variant in complete['variants']:
            self.assertEqual([p['first_gain'] for p in variant['comparison_a']['prefixes']], [1] * 3)
            self.assertEqual(variant['comparison_a']['y_minus_q_selectivity'], 0)
        result = report(paired(text, text.replace('qa.qb', 'za.qb')), partition())
        self.assertEqual(result['comparison_a_common_unit_ids'], [])
        for variant in result['variants']:
            self.assertIsNone(variant['comparison_a']['y_minus_q_selectivity'])
            availability = variant['evaluation_units'][0]['comparison_a_eligibility']
            self.assertEqual(availability['excluded_only_by_other_variants'], variant['source_id'] == 'ZL3b')
        self.assertEqual(result['variants'][4]['evaluation_units'][0]['comparison_a_eligibility']['missing_candidate_classes_in_this_variant'],
                         [{'prefix': 'q', 'role': 'first_slot'}])

    def test_opportunity_cells_require_both_roles_in_every_variant(self):
        text = '<f1r>\n<f1r.1,@P0> z.a\n<f2r>\n<f2r.1,@P0> ya.yb\n'
        result = report(paired(text, text.replace('ya.yb', 'ya.ybbbb')), partition())
        self.assertEqual(result['comparison_b_common_cells'], [])
        self.assertEqual(result['comparison_b_excluded_unit_ids'], ['unit:2'])
        for variant in result['variants']:
            self.assertIsNone(variant['comparison_b']['matched_minus_unmatched_selectivity'])
            self.assertEqual(len(variant['evaluation_units'][0]['y_opportunity_cells']), 9)
        cell = result['variants'][0]['evaluation_units'][0]['y_opportunity_cells'][0]
        self.assertTrue(cell['eligibility']['excluded_only_by_other_variants'])

    def test_empty_classes_are_undefined_and_excluded_original_first_slot_is_not_promoted(self):
        text = '<f1r>\n<f1r.1,@P0> z.a\n<f2r>\n<f2r.1,@P0> ?.ya.yb\n<f2r.2,+P0> za.b\n'
        result = report(paired(text), partition())
        self.assertEqual(result['common_eligible_locations'], 2)
        for variant in result['variants']:
            first = variant['evaluation_units'][0]['prefixes'][0]['first_slot']
            self.assertEqual(first['candidate_tokens'], 0)
            self.assertIsNone(first['mean_match_gain'])

    def test_changed_v1_scientific_record_is_rejected(self):
        sources = paired('<f1r>\n<f1r.1,@P0> z.a\n<f2r>\n<f2r.1,@P0> ya.yb\n')
        units = partition()
        baseline = controls.source.analyze(sources, units)
        baseline['variants'][0]['evaluation_units'][0]['first_slot']['original_only'] += 1
        with self.assertRaisesRegex(ValueError, 'scientific reconstruction'):
            controls.control_report(sources, units, baseline)


class ControlProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.directory = self.root / controls.BASE
        self.directory.mkdir(parents=True)
        self.pin = self.root / 'pinned.txt'
        self.pin.write_bytes(b'fixed input')
        self.record = {'control_version': 'y-prefix-specificity-v1', 'prefixes': list(controls.PREFIXES),
                       'frequency_bins': list(controls.FREQUENCIES), 'length_bins': list(controls.LENGTHS),
                       'pins': {'synthetic': {'path': 'pinned.txt', 'sha256': controls.sha(self.pin.read_bytes())}}}
        (self.directory / 'inputs.json').write_text(json.dumps(self.record))
        (self.directory / 'PLAN.md').write_bytes(b'fixed plan')

    def test_pinned_bytes_or_declaration_drift_is_rejected(self):
        with patch.object(controls.source, 'ROOT', self.root):
            self.assertEqual(controls.verify_inputs(), self.record)
            self.pin.write_bytes(b'changed input')
            with self.assertRaisesRegex(ValueError, 'pin changed'):
                controls.verify_inputs()
            changed = copy.deepcopy(self.record)
            changed['prefixes'] = ['y', 's', 'o']
            (self.directory / 'inputs.json').write_text(json.dumps(changed))
            with self.assertRaisesRegex(ValueError, 'declarations'):
                controls.verify_inputs()

    def test_chronology_and_plan_identity_are_checked(self):
        receipt = [(self.directory / 'PLAN.md').read_bytes(), (self.directory / 'inputs.json').read_bytes(), b'2026-01-03T00:00:00+00:00\n']
        with patch.object(controls.source, 'ROOT', self.root), patch.object(controls.subprocess, 'check_output', side_effect=receipt):
            with self.assertRaisesRegex(ValueError, 'follow registration'):
                controls.registration('a' * 40, '2026-01-02T00:00:00+00:00')
        with patch.object(controls.source, 'ROOT', self.root), patch.object(controls.subprocess, 'check_output', return_value=b'different'):
            with self.assertRaisesRegex(ValueError, 'changed after registration'):
                controls.registration('a' * 40, '2026-01-04T00:00:00+00:00')
        with self.assertRaisesRegex(ValueError, 'pre-control commit'):
            controls.registration('not-a-commit', '2026-01-04T00:00:00+00:00')

    def test_control_output_rejects_direct_symlink_and_hardlink_input_aliases(self):
        catalog = self.root / 'data/transliterations.json'
        catalog.parent.mkdir()
        catalog.write_text(json.dumps({'sources': []}))
        prepared = {'input_pins': {}}
        for original in (self.pin, self.directory / 'inputs.json', self.directory / 'PLAN.md'):
            for kind in ('direct', 'symlink', 'hardlink'):
                alias = self.root / ('alias-' + original.name + '-' + kind)
                if kind == 'symlink':
                    alias.symlink_to(original)
                elif kind == 'hardlink':
                    os.link(original, alias)
                else:
                    alias = original
                with self.subTest(original=original.name, kind=kind), patch.object(controls.source, 'ROOT', self.root), \
                        patch.object(controls.source, 'prepare_partition', return_value=prepared), self.assertRaises(ValueError):
                    controls.protect_output(alias, self.record)
        with patch.object(controls.source, 'ROOT', self.root), patch.object(controls.source, 'prepare_partition', return_value=prepared):
            controls.protect_output(self.root / 'safe.json', self.record)

    def test_cli_refuses_input_output_before_control_analysis(self):
        catalog = self.root / 'data/transliterations.json'
        catalog.parent.mkdir()
        catalog.write_text(json.dumps({'sources': []}))
        errors = io.StringIO()
        with patch.object(controls.source, 'ROOT', self.root), \
                patch.object(controls.source, 'prepare_partition', return_value={'input_pins': {}}), \
                patch.object(controls, 'control_report') as calculate, \
                patch('sys.argv', ['controls', '--output', str(self.pin)]), \
                redirect_stderr(errors), self.assertRaises(SystemExit) as failed:
            controls.main()
        self.assertEqual(failed.exception.code, 1)
        calculate.assert_not_called()
        self.assertEqual(self.pin.read_bytes(), b'fixed input')

    def test_cli_rechecks_output_if_analysis_introduces_an_input_hardlink(self):
        catalog = self.root / 'data/transliterations.json'
        catalog.parent.mkdir()
        catalog.write_text(json.dumps({'sources': []}))
        parent = self.root / controls.source.BASE
        parent.mkdir(parents=True)
        prepared = {'input_pins': {}}
        (parent / 'partition.json').write_text(json.dumps(prepared))
        (parent / 'results.json').write_text('{}')
        output = self.root / 'output.json'

        def replace_output(*args):
            os.link(self.pin, output)
            return {}

        with patch.object(controls.source, 'ROOT', self.root), \
                patch.object(controls.source, 'prepare_partition', return_value=prepared), \
                patch.object(controls.source, 'load_pins', return_value=([], {}, {})), \
                patch.object(controls, 'registration', return_value='2026-01-01T00:00:00+00:00'), \
                patch.object(controls, 'control_report', side_effect=replace_output), \
                patch('sys.argv', ['controls', '--output', str(output), '--pre-control-commit', 'a' * 40]), \
                redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as failed:
            controls.main()
        self.assertEqual(failed.exception.code, 1)
        self.assertEqual(self.pin.read_bytes(), b'fixed input')
        self.assertEqual(output.read_bytes(), b'fixed input')


if __name__ == '__main__':
    unittest.main()
