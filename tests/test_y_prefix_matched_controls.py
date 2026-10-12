"""Enumerated lookup/matching examples and source-free lifecycle checks."""

from collections import Counter
from contextlib import redirect_stderr
from fractions import Fraction
import io
import json
import os
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from scripts import y_prefix_matched_controls as control


def row(page, *values):
    return SimpleNamespace(page=page), [None if value is None else SimpleNamespace(value=value) for value in values]


def unit_map(**pages):
    return {page: {'unit_id': unit, 'partition': 'diagnostic_evaluation'} for page, unit in pages.items()}


def rational(value):
    return None if value is None else Fraction(value['numerator'], value['denominator'])


class MatchingTests(unittest.TestCase):
    def test_lookup_cells_and_invalid_representations(self):
        vocabulary = {'a', 'qb', 'c', 'qc'}
        scores = [control.lookup(value, vocabulary) for value in ('ya', 'qb', 'qc', 'qd')]
        self.assertEqual([score[2] for score in scores], [1, -1, 0, 0])
        self.assertEqual(control.cells(scores), {'occurrences': 4, 'both_match': 1,
                         'neither_matches': 1, 'original_only': 1, 'stripped_only': 1})
        for value in ('y', 'Qa', 'y?', 'yä', '{y}a', None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                control.lookup(value, vocabulary)

    def test_frequency_boundaries_and_exact_original_membership_cancellation(self):
        self.assertEqual([control.frequency_bin(n) for n in (0, 1, 2, 3, 4, 7, 8, 15, 16)],
                         [0, 1, 2, 2, 3, 3, 4, 4, 5])
        for invalid in (-1, True, 1.0):
            with self.assertRaises(ValueError):
                control.frequency_bin(invalid)
        result, _ = control.treatment([row('p', 'ya'), row('p', 'qb')], unit_map(p='u'), ['u'],
                                      Counter({'ya': 2, 'qb': 3, 'a': 5}))
        stratum = result['strata'][0]
        self.assertEqual(stratum['frequency_bin'], 2)
        self.assertEqual(rational(stratum['mean_target_gain']), 0)
        self.assertEqual(rational(stratum['mean_control_gain']), -1)
        self.assertEqual(rational(stratum['mean_adjusted_gain']), 1)

    def test_occurrence_pool_weight_and_reused_pool_are_explicit(self):
        rows = [row('p', value) for value in ('ya', 'ya', 'qa', 'qa', 'qb')]
        result, _ = control.treatment(rows, unit_map(p='u'), ['u'], Counter({'a': 1}))
        first = result['units'][0]['positions']['first']
        self.assertEqual(first['matched_targets']['occurrences'], 2)
        self.assertEqual(first['distinct_pool_control_occurrences'], 3)
        self.assertEqual(first['target_control_pair_uses'], 6)
        self.assertEqual(rational(first['mean_assigned_control_gain']), Fraction(2, 3))
        self.assertEqual(rational(first['mean_adjusted_gain']), Fraction(1, 3))
        self.assertEqual(result['strata'][0]['control_prefix_occurrences'], {'q': 3})

    def test_unit_role_length_and_frequency_must_all_match(self):
        cases = [([row('a', 'ya'), row('b', 'qa')], Counter({'a': 1}), 'unit'),
                 ([row('a', 'ya'), row('a', 'x', 'qa')], Counter({'a': 1}), 'role'),
                 ([row('a', 'ya'), row('a', 'qqa')], Counter({'a': 1}), 'length'),
                 ([row('a', 'ya'), row('a', 'qa')], Counter({'a': 1, 'qa': 1}), 'frequency')]
        for rows, counts, dimension in cases:
            result, _ = control.treatment(rows, unit_map(a='u', b='v'), ['u', 'v'], counts)
            first = result['units'][0]['positions']['first']
            with self.subTest(dimension=dimension):
                self.assertEqual(first['matched_targets']['occurrences'], 0)
                self.assertEqual(first['unmatched_targets']['occurrences'], 1)

    def test_original_gap_and_uppercase_initial_are_not_promoted(self):
        result, _ = control.treatment([row('p', None, 'ya', 'qa'), row('p', 'Qa')],
                                      unit_map(p='u'), ['u'], Counter({'a': 1}))
        positions = result['units'][0]['positions']
        self.assertEqual(positions['first']['all_targets']['occurrences'], 0)
        self.assertEqual(positions['other']['matched_targets']['occurrences'], 1)
        self.assertEqual(result['units'][0]['missing_matched_classes'], ['first'])

    def test_only_development_internal_ascii_occurrences_define_frequency(self):
        rows = [row('d', 'yfirst', 'a', 'qb', None, 'a', 'a?'), row('e', 'ya', 'evalonly')]
        pages = {'d': {'partition': 'dictionary_development'}, 'e': {'partition': 'diagnostic_evaluation'}}
        self.assertEqual(control.fit_counts(rows, pages), Counter({'a': 2, 'qb': 1}))

    def test_all_strata_and_unmatched_targets_are_retained(self):
        result, _ = control.treatment([row('p', 'ya'), row('p', 'qaa'), row('p', 'yaa')],
                                      unit_map(p='u'), ['u'], Counter({'a': 1}))
        self.assertEqual(len(result['strata']), 2)
        first = result['units'][0]['positions']['first']
        self.assertEqual(first['all_targets']['occurrences'], 2)
        self.assertEqual(first['matched_targets']['occurrences'], 1)
        self.assertEqual(first['unmatched_targets']['occurrences'], 1)


class AggregationTests(unittest.TestCase):
    def result(self, frame):
        return {'units': [{'unit_id': unit} for unit in frame]}

    def test_equal_unit_weights_and_exact_signs(self):
        # The unit-level inputs are hand-set, not generated by the scorer.
        frame = ['small', 'large']
        gains = {'small': [(Fraction(1), Fraction(0), Fraction(1)), (Fraction(0), Fraction(0), Fraction(0))],
                 'large': [(Fraction(-1), Fraction(0), Fraction(-1)), (Fraction(0), Fraction(0), Fraction(0))]}
        output = control.summarize([self.result(frame) for _ in range(8)], [gains] * 8, frame)
        self.assertEqual(output['decision'], 'mixed_or_nonpositive_adjusted_selectivity')
        self.assertEqual(rational(output['variants'][0]['equal_unit_summary']['adjusted']['first_minus_other']), 0)
        for unit in frame:
            gains[unit][0] = (Fraction(1, 10**12), Fraction(0), Fraction(1, 10**12))
        output = control.summarize([self.result(frame) for _ in range(8)], [gains] * 8, frame)
        self.assertEqual(output['decision'], 'positive_adjusted_selectivity_in_all_variants')
        self.assertEqual(output['variants'][0]['equal_unit_summary']['adjusted']['first_minus_other']['decimal'], 0.0)

    def test_one_missing_variant_excludes_unit_from_every_variant(self):
        frame = ['a', 'b']
        means = [(Fraction(1), Fraction(0), Fraction(1)), (Fraction(0), Fraction(0), Fraction(0))]
        maps = [{'a': means, 'b': means} for _ in range(8)]
        maps[-1].pop('b')
        output = control.summarize([self.result(frame) for _ in range(8)], maps, frame)
        self.assertEqual(output['joint_unit_ids'], ['a'])
        self.assertEqual(output['excluded_frame_units'], ['b'])
        self.assertTrue(all(not variant['units'][1]['included_in_all_variant_joint_summary']
                            for variant in output['variants']))

    def test_empty_joint_coverage_stays_undefined_and_every_variant_required(self):
        output = control.summarize([self.result(['a']) for _ in range(8)], [{} for _ in range(8)], ['a'])
        self.assertEqual(output['decision'], 'indeterminate_matching_coverage')
        self.assertIsNone(output['variants'][0]['equal_unit_summary']['adjusted']['first_mean'])
        with self.assertRaises(ValueError):
            control.summarize([], [], ['a'])


class ProvenanceTests(unittest.TestCase):
    def test_changed_input_or_dependency_fails_before_parent_replay(self):
        protocol = {'schema_version': 1, 'analysis_id': 'y-prefix-matched-other-prefix-v1',
                    'target_prefix': 'y', 'exact_ascii_length_match': True,
                    'position_classes': ['first', 'other'],
                    'frequency_bin': '0 if count is zero else count.bit_length()',
                    'input_sha256': {}, 'dependency_sha256': {}}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'input.json').write_bytes(b'changed input')
            (root / 'scripts').mkdir()
            (root / 'scripts/parent.py').write_bytes(b'changed dependency')
            for kind, pins in (('input_sha256', {'input.json': '0' * 64}),
                               ('dependency_sha256', {'parent.py': '0' * 64})):
                configured = dict(protocol, **{kind: pins})
                with self.subTest(kind=kind), patch.object(control, 'ROOT', root), \
                        patch.object(control.parent, 'prepare_partition') as replay:
                    with self.assertRaisesRegex(ValueError, 'drift'):
                        control.verified_inputs(configured)
                    replay.assert_not_called()

    def test_registration_requires_frozen_files_and_pre_measurement_time(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base = root / control.BASE
            base.mkdir(parents=True)
            for name in ('MATCHED_CONTROL_PLAN.md', 'MATCHED_CONTROL_EXPOSURE.md', 'matched-control-protocol.json'):
                (base / name).write_bytes(b'current')
            script = root / 'program.py'
            script.write_bytes(b'current')
            with patch.object(control, 'ROOT', root), patch.object(control, '__file__', str(script)), \
                    patch.object(control.subprocess, 'check_output', return_value=b'old'):
                with self.assertRaisesRegex(ValueError, 'file drift'):
                    control.registration('a' * 40, base / 'matched-control-protocol.json', '2026-01-02T00:00:00+00:00')
            with patch.object(control, 'ROOT', root), patch.object(control, '__file__', str(script)), \
                    patch.object(control.subprocess, 'check_output', side_effect=[b'current'] * 4 + [b'2026-01-03T00:00:00+00:00']):
                with self.assertRaisesRegex(ValueError, 'must begin after'):
                    control.registration('a' * 40, base / 'matched-control-protocol.json', '2026-01-02T00:00:00+00:00')

    def test_hardlink_output_cannot_replace_parent_or_source_before_any_measurement(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            raw = root / 'data/raw/source.txt'
            raw.parent.mkdir(parents=True)
            raw.write_bytes(b'pinned source')
            (root / 'data/transliterations.json').write_text(json.dumps({'sources': [{'path': 'data/raw/source.txt'}]}))
            protocol = root / 'protocol.json'
            protocol.write_text(json.dumps({'input_sha256': {}}))
            alias = root / 'output.json'
            os.link(raw, alias)
            with patch.object(control, 'ROOT', root), patch.object(control.parent, 'ROOT', root), \
                    patch.object(control, 'registration') as registration, patch.object(control, 'report') as measure, \
                    redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                control.main(['--protocol', str(protocol), '--output', str(alias)])
            registration.assert_not_called()
            measure.assert_not_called()
            self.assertEqual(raw.read_bytes(), b'pinned source')


if __name__ == '__main__':
    unittest.main()
