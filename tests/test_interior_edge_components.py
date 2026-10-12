import contextlib
import copy
from decimal import localcontext, ROUND_FLOOR
from fractions import Fraction
import io
import itertools
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import interior_edge_components as m


def literal_raw(values):
    size = len(values)
    mean = Fraction(sum(values), size)
    deviations = [x - mean for x in values]
    squared = sum(x * x for x in deviations)
    cut = (size + 1) // 2
    result = [Fraction()] * 3
    for index, (a, b) in enumerate(zip(deviations, deviations[1:])):
        region = 0 if index < cut - 1 else (1 if index == cut - 1 else 2)
        if squared:
            result[region] += Fraction(size, size - 1) * a * b / squared
    return result


def synthetic_family():
    families = [[[1, 4, 2, 5, 3], [2, 2, 2]], [[1, 2, 2, 3, 2], [2, 2, 2]],
                [[1, 3, 2, 4, 2], [2, 2, 2]]]
    converted = [{'policy_id': pid, 'length_corpus_sha256': 'synthetic',
                  'rows': [('page', 'first', values[0]), ('page', 'constant', values[1])]}
                 for pid, values in zip(m.parent.POLICIES, families)]
    old = {'source_id': 'synthetic', 'spacing': 'split', 'source_sha256': 'synthetic', 'unit_policies': []}
    exact = []
    for pid, values, new in zip(m.parent.POLICIES, families, converted):
        means = {}
        for scope in m.parent.SCOPES:
            centered = []
            for vector in values:
                expected = m.parent.unit.half.exact_half_expectation(vector) if scope == 'half' else (
                    Fraction(-1, len(vector) - 1) if len(set(vector)) > 1 else Fraction())
                centered.append(sum(literal_raw(vector)) - expected)
            means[scope] = sum(centered, Fraction()) / 2
        exact.append(means)
        saved = {'policy_id': pid, 'loci': 2, **m.parent.unit.moments(new['rows'])}
        for scope in m.parent.SCOPES:
            saved[scope] = {'observed_centered_association': float(means[scope]),
                            'two_sided_tail_count': 0, 'exploratory_two_sided_tail': .001}
        if len(exact) > 1:
            saved['paired_change_from_ascii'] = {scope: {'observed_centered_association': float(means[scope] - exact[0][scope])}
                                                for scope in m.parent.SCOPES}
        old['unit_policies'].append(saved)
    joint = {'per_locus': []}
    for index, key in enumerate(('first', 'constant')):
        record = {'page_id': 'page', 'locus_key': key}
        for scope in m.parent.SCOPES:
            means = []
            for family in families:
                vector = family[index]
                mean = m.parent.unit.half.exact_half_expectation(vector) if scope == 'half' else (
                    Fraction(-1, len(vector) - 1) if len(set(vector)) > 1 else Fraction())
                means.append(m.parent.small(mean))
            record[scope] = {'uncentered_means': means}
        joint['per_locus'].append(record)
    for scope in m.parent.SCOPES:
        joint[scope] = {'exact_observed_centered_means': [m.parent.large(v[scope]) for v in exact],
                        'paired_changes': [{'observed_change_exact': m.parent.large(v[scope] - exact[0][scope])}
                                           for v in exact[1:]]}
    return old, converted, joint


class EdgeComponentTests(unittest.TestCase):
    def test_each_expectation_against_complete_occurrence_orders(self):
        fixtures = list(itertools.product((1, 2, 3), repeat=3)) + [
            (1, 3, 2, 4), (1, 1, 4, 2), (2, 2, 2, 2),
            (1, 4, 3, 2, 2), (1, 3, 2, 6, 4, 2), (3, 3, 3, 3, 3)]
        for values in fixtures:
            measured = m.components(values)
            self.assertEqual(measured['raw'], literal_raw(values))
            cut = (len(values) + 1) // 2
            orders = {'unrestricted': itertools.permutations(values),
                      'half': (a + b for a, b in itertools.product(
                          itertools.permutations(values[:cut]), itertools.permutations(values[cut:])))}
            for scope, population in orders.items():
                outcomes = [literal_raw(order) for order in population]
                expected = [sum((v[i] for v in outcomes), Fraction()) / len(outcomes) for i in range(3)]
                self.assertEqual(expected, measured[scope + '_expectation'])
                self.assertEqual([sum(v - expected[i] for v in [row[i] for row in outcomes]) for i in range(3)], [0, 0, 0])

    def test_additivity_singleton_constants_and_affine_invariance(self):
        for values in ([1, 3, 2], [1, 7, 2, 3, 4], [2, 2, 2, 2], [1, 3, 4, 2, 6, 1]):
            record = m.components(values)
            size, squared, adjacent = m.parent.unit.original.components(values)
            raw = Fraction(size * adjacent, (size - 1) * squared) if squared else Fraction()
            self.assertEqual(sum(record['raw']), raw)
            self.assertEqual(sum(record['half_expectation']), m.parent.unit.half.exact_half_expectation(values))
            self.assertEqual(sum(record['unrestricted_expectation']), Fraction(-1, size - 1) if squared else 0)
            self.assertEqual(m.components([5 * x + 10 for x in values]), record)
        singleton = m.components([1, 3, 2])
        self.assertEqual(singleton['edge_counts'], [1, 1, 0])
        self.assertEqual(singleton['raw'][2], 0)
        self.assertEqual(singleton['half_expectation'][2], 0)
        constant = m.components([2, 2, 2])
        self.assertEqual([constant[field] for field in m.FIELDS], [[0, 0, 0]] * 3)

    def test_equal_locus_denominator_paired_changes_and_shift_sign(self):
        first = m.components([1, 4, 2, 5, 3])
        zero = m.components([2, 2, 2])
        mean = m.average([first, zero])
        for scope in m.parent.SCOPES:
            self.assertEqual(mean[scope + '_centered'], [v / 2 for v in m.centered(first, scope)])
        shift = mean['half_minus_unrestricted_expectation']
        self.assertEqual([a - b for a, b in zip(mean['unrestricted_centered'], mean['half_centered'])], shift)
        grouped = m.average([m.components([1, 2, 2, 3, 2]), zero])
        paired = m.difference(grouped, mean)
        for scope in m.parent.SCOPES:
            self.assertEqual(sum(paired[scope]), sum(grouped[scope + '_centered']) - sum(mean[scope + '_centered']))
        with self.assertRaises(ValueError):
            m.average([])

    def test_malformed_counts_and_scopes_are_refused(self):
        for values in ([], [1, 2], [1, True, 3], [1, 2., 3], [1, 0, 3], [1, -2, 3], '123', None):
            with self.subTest(values=values), self.assertRaises(ValueError):
                m.components(values)
        with self.assertRaises(ValueError):
            m.centered(m.components([1, 2, 3]), 'quarters')
        with self.assertRaisesRegex(ValueError, 'family'):
            m.summarize({}, [], {})

    def test_complete_family_reassembly_refuses_missing_or_changed_parent_evidence(self):
        old, converted, joint = synthetic_family()
        result = m.summarize(old, converted, joint)
        self.assertEqual([p['loci'] for p in result['unit_policies']], [2, 2, 2])
        for saved in result['unit_policies']:
            self.assertEqual(saved['per_locus'][1]['raw'], [['0', '1']] * 3)
            self.assertEqual(saved['accepted_effect_denominator'], 2)
        corruptions = []
        missing = copy.deepcopy(converted)
        missing[1]['rows'].pop()
        corruptions.append((old, missing, joint))
        duplicate = copy.deepcopy(converted)
        for policy in duplicate:
            policy['rows'][1] = policy['rows'][0]
        corruptions.append((old, duplicate, joint))
        changed = copy.deepcopy(joint)
        changed['per_locus'][0]['half']['uncentered_means'][0] = ['0', '1']
        corruptions.append((old, converted, changed))
        changed = copy.deepcopy(joint)
        changed['half']['exact_observed_centered_means'][0] = m.parent.large(Fraction(99))
        corruptions.append((old, converted, changed))
        corruptions.append((dict(old, unit_policies=old['unit_policies'][:2]), converted, joint))
        for fixture in corruptions:
            with self.assertRaises(ValueError):
                m.summarize(*fixture)

    def test_changed_manifest_or_input_precedes_corpus_preparation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pin = root / m.PINS
            pin.parent.mkdir(parents=True)
            fixture = root / 'fixture.txt'
            fixture.write_text('changed')
            pin.write_text(json.dumps({'fixture.txt': m.parent.sha(b'original')}))
            with patch.object(m, 'ROOT', root), patch.object(m, 'PIN_SHA256', m.parent.sha(pin.read_bytes())), \
                    patch.object(m.parent, 'prepare') as calculate, self.assertRaisesRegex(ValueError, 'input changed'):
                m.report()
            calculate.assert_not_called()
            with patch.object(m, 'ROOT', root), self.assertRaisesRegex(ValueError, 'manifest changed'):
                m.load_inputs()

    def test_direct_symbolic_hard_and_parent_redirect_aliases_protect_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pin = root / m.PINS
            pin.parent.mkdir(parents=True)
            source = root / m.PLAN
            source.write_text('preserve')
            pin.write_text(json.dumps({m.PLAN: m.parent.sha(source.read_bytes())}))
            with patch.object(m, 'ROOT', root), patch.object(m.parent.unit, 'protect_output'):
                for index, original in enumerate((source, pin, Path(m.__file__))):
                    symbolic = root / f'symbolic-{index}'
                    symbolic.symlink_to(original)
                    hard = root / f'hard-{index}'
                    hard.hardlink_to(original)
                    for alias in (original, symbolic, hard):
                        with self.assertRaises(ValueError):
                            m.protect_output(alias)
                link = root / 'redirect'
                link.symlink_to(source.parent, target_is_directory=True)
                with self.assertRaises(ValueError):
                    m.protect_output(link / source.name)
                m.protect_output(root / 'new.json')
            self.assertEqual(source.read_text(), 'preserve')

    def test_existing_outputs_refused_before_calculation(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'report.json'
            output.write_text('preserve')
            with patch.object(m, 'protect_output'), patch.object(m, 'report') as calculate, \
                    patch('sys.argv', ['components', '--new-report', str(output)]), \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                m.main()
            calculate.assert_not_called()
            self.assertEqual(output.read_text(), 'preserve')

    def test_serialization_time_alias_refused_with_real_late_guard(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pin = root / m.PINS
            pin.parent.mkdir(parents=True)
            source = root / m.PLAN
            source.write_text('preserve')
            pin.write_text(json.dumps({m.PLAN: m.parent.sha(source.read_bytes())}))
            output = root / 'new.json'
            def serialize(_):
                output.hardlink_to(source)
                return '{}\n'
            with patch.object(m, 'ROOT', root), patch.object(m.parent.unit, 'protect_output'), \
                    patch.object(m, 'report', return_value={}), patch.object(m, 'serialize', side_effect=serialize), \
                    patch('sys.argv', ['components', '--new-report', str(output)]), \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                m.main()
            self.assertEqual(source.read_text(), 'preserve')

    def test_complete_typed_cache_check_and_exclusive_new_output(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / 'report.json'
            with patch.object(m, 'protect_output'), patch.object(m, 'report', return_value={'count': 0}), \
                    patch('sys.argv', ['components', '--new-report', str(output)]), contextlib.redirect_stdout(io.StringIO()):
                m.main()
            self.assertEqual(json.loads(output.read_text()), {'count': 0})
            output.write_text('{"count":false}')
            with patch.object(m, 'protect_output'), patch.object(m, 'report', return_value={'count': 0}), \
                    patch('sys.argv', ['components', '--check', str(output)]), \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                m.main()

    def test_large_aggregate_preserves_global_integer_and_decimal_settings(self):
        digit_guard = sys.get_int_max_str_digits()
        value = Fraction(10 ** 9000 + 1, 10 ** 9001 + 3)
        with localcontext() as context:
            context.prec = 2
            context.rounding = ROUND_FLOOR
            encoded = m.parent.large(value)
            self.assertEqual(m.parent.unpack(encoded), value)
            self.assertEqual(context.prec, 2)
            self.assertEqual(context.rounding, ROUND_FLOOR)
            self.assertEqual(json.loads(m.serialize({'value': encoded})), {'value': encoded})
        self.assertEqual(sys.get_int_max_str_digits(), digit_guard)


if __name__ == '__main__':
    unittest.main()
