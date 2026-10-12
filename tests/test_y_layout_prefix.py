import unittest
from fractions import Fraction
from contextlib import redirect_stderr
import io
import json
from pathlib import Path
import tempfile
from unittest.mock import patch

from scripts.ivtff import parse_ivtff
from scripts.y_layout_prefix import (analyze, build_partition, case_summary, fit_vocabulary,
                                    fixed_decision, main, match_gain, repetition_body, verify_registration, BASE)
from scripts.locus_positions import prepare_rows


def paired(text):
    doc = parse_ivtff('#=IVTFF Eva- 2.0 M\n' + text)
    return [({'id': identifier, 'sha256': 'synthetic'}, doc) for identifier in ('ZL3b', 'IT2a')]


def images(groups):
    return {'dependency_components': [{'folio_ids': list(group)} for group in groups],
            'indexed_canvas_ids_by_leaf': {family: ['canvas:' + family]
                                          for group in groups for family in group}}


class YPartitionTests(unittest.TestCase):
    def test_shared_scan_and_repeated_string_dependencies_close_transitively(self):
        source = paired('<f1r>\n<f1r.1,@P0> a.b.c\n'
                        '<f2r>\n<f2r.1,@P0> d.e.f\n'
                        '<f3r>\n<f3r.1,@P0> <!note><@H=2>a.b.c\n'
                        '<f4r>\n<f4r.1,@P0> g.h.i\n')
        report = build_partition(source, images([['1', '2'], ['3'], ['4']]))
        groups = [unit['numeric_source_families'] for unit in report['units']]
        self.assertIn(['1', '2', '3'], groups)
        self.assertIn(['4'], groups)
        self.assertEqual(len(report['exact_string_dependency_edges']), 2)
        self.assertFalse(report['valid_candidate_holdout'])

    def test_partition_order_is_deterministic_and_cannot_split_sides_or_panels(self):
        source = paired('<f1r>\n<f1r.1,@P0> a.b.c\n'
                        '<f1v>\n<f1v.1,@P0> d.e.f\n'
                        '<f67r1>\n<f67r1.1,@P0> g.h.i\n'
                        '<f67r2>\n<f67r2.1,@P0> j.k.l\n')
        report = build_partition(source, images([['1'], ['67']]))
        reordered = images([['67'], ['1']])
        self.assertEqual(report, build_partition(list(reversed(source)), reordered))
        self.assertEqual([unit['partition'] for unit in report['units']],
                         ['diagnostic_evaluation', 'dictionary_development'])
        self.assertEqual(sum(len(unit['selected_source_pages']) for unit in report['units']), 4)

    def test_joint_paragraph_and_locator_exclusions_precede_partitioning(self):
        left = parse_ivtff('#=IVTFF Eva- 2.0 M\n<f1r>\n'
                           '<f1r.1,@P0> <%>a.b.c\n<f1r.2,=P0> d.e.f\n'
                           '<f1r.3,+P0> g.h.i\n<f2r>\n<f2r.1,@P0> j.k.l\n')
        right = parse_ivtff('#=IVTFF Eva- 2.0 M\n<f1r>\n'
                            '<f1r.1,@P0> a.b.c\n<f1r.2,+P0> d.e.f\n'
                            '<f1r.3,+P0> g.h.i\n<f2r>\n<f2r.1,@P0> j.k.l\n')
        report = build_partition([({'id': 'ZL3b', 'sha256': 'synthetic'}, left),
                                  ({'id': 'IT2a', 'sha256': 'synthetic'}, right)], images([['1'], ['2']]))
        self.assertEqual(report['selection']['selected_location_count'], 2)
        self.assertEqual(report['selection']['excluded_source_paragraph_start_keys'], ['f1r.1'])
        self.assertEqual(report['selection']['excluded_nonregular_keys'], ['f1r.2'])

    def test_unknown_or_ambiguous_strings_do_not_establish_repeated_passages(self):
        doc = parse_ivtff('#=IVTFF Eva- 2.0 M\n<f1r>\n'
                          '<f1r.1,@P0> a.b.?\n<f1r.2,+P0> a.[b:c].d\n'
                          '<f1r.3,+P0> a.b\n')
        self.assertTrue(all(repetition_body(locus) is None for locus in doc.loci))

    def test_one_connected_unit_is_a_failure_not_a_fake_partition(self):
        with self.assertRaisesRegex(ValueError, 'at least two dependency units'):
            build_partition(paired('<f1r>\n<f1r.1,@P0> a.b.c\n'), images([['1']]))


class YLookupTests(unittest.TestCase):
    def partition(self, sources, family_groups, evaluation_families):
        partition = build_partition(sources, images(family_groups))
        for unit in partition['units']:
            unit['partition'] = ('diagnostic_evaluation' if
                                 set(unit['numeric_source_families']) & set(evaluation_families)
                                 else 'dictionary_development')
        return partition

    def test_known_lookup_scores_and_all_four_cells_are_exact(self):
        vocabulary = {'a', 'yb', 'c', 'yc'}
        self.assertEqual(match_gain('ya', vocabulary), (False, True, 1))
        self.assertEqual(match_gain('yb', vocabulary), (True, False, -1))
        summary, gain = case_summary(['ya', 'yb', 'yc', 'yd'], vocabulary)
        self.assertEqual(gain, 0)
        self.assertEqual([summary[key] for key in
                          ('both_match', 'neither_matches', 'original_only', 'stripped_only')], [1] * 4)
        empty, unknown = case_summary([], vocabulary)
        self.assertIsNone(unknown)
        self.assertIsNone(empty['mean_match_gain'])
        for invalid in ('y', 'Ya', 'y?', 'yä', '{y}a'):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                match_gain(invalid, vocabulary)

    def test_vocabulary_has_only_development_internal_tokens(self):
        source = paired('<f1r>\n<f1r.1,@P0> z.a.yb\n<f2r>\n<f2r.1,@P0> ya.yb.b\n')
        partition = self.partition(source, [['1'], ['2']], ['2'])
        units = {page: unit for unit in partition['units'] for page in unit['selected_source_pages']}
        vocabulary, count = fit_vocabulary(prepare_rows(source[0][1].loci, 'split', 'exclude'), units)
        self.assertEqual(vocabulary, {'a', 'yb'})
        self.assertEqual(count, 2)
        report = analyze(source, partition)
        self.assertEqual(report['decision'], 'survives_v1_diagnostic')
        for variant in report['variants']:
            self.assertEqual(variant['common_unit_summary']['mean_unit_first_slot_gain'], 1)
            self.assertEqual(variant['common_unit_summary']['mean_unit_other_slot_gain'], -1)
            self.assertEqual(variant['common_unit_summary']['mean_unit_first_minus_other_gain'], 2)
        self.assertFalse(report['valid_candidate_holdout'])

    def test_equal_unit_weight_does_not_become_token_weight(self):
        text = '<f1r>\n<f1r.1,@P0> z.a.yb.yc\n<f2r>\n<f2r.1,@P0> ya.yc.d\n<f3r>\n'
        text += ''.join(f'<f3r.{n},{"@" if n==1 else "+"}P0> yb.yc.d\n' for n in range(1, 11))
        source = paired(text)
        report = analyze(source, self.partition(source, [['1'], ['2'], ['3']], ['2', '3']))
        self.assertEqual(report['selection']['common_evaluation_unit_count'], 2)
        summary = report['variants'][0]['common_unit_summary']
        self.assertEqual(summary['mean_unit_first_slot_gain'], 0)
        self.assertEqual(summary['mean_unit_other_slot_gain'], -1)
        self.assertEqual(report['decision'], 'fails_v1_diagnostic')

    def test_excluded_boundary_cannot_be_promoted_in_any_variant(self):
        left = paired('<f1r>\n<f1r.1,@P0> z.a.yb\n'
                      '<f2r>\n<f2r.1,@P0> ?.ya.yb\n<f2r.2,+P0> ya.yb.b\n')[0]
        right = paired('<f1r>\n<f1r.1,@P0> z.a.yb\n'
                       '<f2r>\n<f2r.1,@P0> ya.ya.yb\n<f2r.2,+P0> ya.yb.b\n')[1]
        source = [left, right]
        report = analyze(source, self.partition(source, [['1'], ['2']], ['2']))
        self.assertEqual(report['selection']['common_eligible_locations'], 2)
        for variant in report['variants']:
            self.assertEqual(variant['excluded_from_common_locus_cohort'], ['f2r.1'])

    def test_no_common_candidate_units_stays_indeterminate(self):
        source = paired('<f1r>\n<f1r.1,@P0> z.a.b\n<f2r>\n<f2r.1,@P0> ya.a.b\n')
        report = analyze(source, self.partition(source, [['1'], ['2']], ['2']))
        self.assertEqual(report['decision'], 'indeterminate')
        self.assertIsNone(report['variants'][0]['common_unit_summary']['mean_unit_first_slot_gain'])

    def test_exact_threshold_and_sensitivity_failure_are_fixed(self):
        passing = [(Fraction(1, 10), Fraction(1, 20))] * 8
        self.assertEqual(fixed_decision(passing), 'survives_v1_diagnostic')
        failing = passing.copy()
        failing[0] = (Fraction(1, 10), Fraction(51, 1000))
        self.assertEqual(fixed_decision(failing), 'fails_v1_diagnostic')
        failing = passing.copy()
        failing[-1] = (Fraction(1, 10), Fraction(1, 5))
        self.assertEqual(fixed_decision(failing), 'fails_v1_diagnostic')
        self.assertEqual(fixed_decision([]), 'indeterminate')
        with self.assertRaisesRegex(ValueError, 'all eight'):
            fixed_decision(passing[:1])


class YProvenanceTests(unittest.TestCase):
    def test_changed_partition_is_rejected_before_any_vocabulary_fit(self):
        original = {'units': [{'partition': 'dictionary_development'}]}
        with tempfile.TemporaryDirectory() as folder:
            partition = Path(folder) / 'partition.json'
            partition.write_text(json.dumps({'units': [{'partition': 'diagnostic_evaluation'}]}))
            output = Path(folder) / 'results.json'
            with patch('scripts.y_layout_prefix.prepare_partition', return_value=original), \
                    patch('scripts.y_layout_prefix.analyze') as fit, \
                    patch('sys.argv', ['diagnostic', '--partition', str(partition), '--output', str(output)]), \
                    redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as failed:
                main()
            self.assertEqual(failed.exception.code, 1)
            fit.assert_not_called()
            self.assertFalse(output.exists())

    def test_rule_drift_and_post_fit_registration_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            plan = root / BASE / 'PLAN.md'
            plan.parent.mkdir(parents=True)
            plan.write_bytes(b'current plan')
            partition = root / 'partition.json'
            partition.write_bytes(b'current partition')
            with patch('scripts.y_layout_prefix.ROOT', root), \
                    patch('scripts.y_layout_prefix.subprocess.check_output', return_value=b'older plan'), \
                    self.assertRaisesRegex(ValueError, 'differ from the pre-fit commit'):
                verify_registration('a' * 40, partition, '2026-01-02T00:00:00+00:00')
            receipt = [b'current plan', b'current partition', b'2026-01-03T00:00:00+00:00\n']
            with patch('scripts.y_layout_prefix.ROOT', root), \
                    patch('scripts.y_layout_prefix.subprocess.check_output', side_effect=receipt), \
                    self.assertRaisesRegex(ValueError, 'must start after'):
                verify_registration('a' * 40, partition, '2026-01-02T00:00:00+00:00')


if __name__ == '__main__':
    unittest.main()
