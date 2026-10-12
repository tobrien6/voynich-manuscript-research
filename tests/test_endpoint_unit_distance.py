from copy import deepcopy
from contextlib import redirect_stdout, redirect_stderr
from fractions import Fraction
from functools import lru_cache
from itertools import permutations, product
import io
import json
import os
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from scripts.audit_eva_token_coverage import encoded
from scripts.eva_unit_sensitivity import segment
from scripts.paragraph_endpoint_distance import analyze as parent_analyze, build as parent_build
from scripts.paragraph_token_corpus import build as corpus_build, digest
from scripts.endpoint_unit_distance import (
    PLAN, PARENT, SETTINGS, PINS, POLICY_IDS, BENCH, MINIM, EXAMPLES,
    policies, sequence_distance, matrix, difference, record_moments,
    aggregate, scope_audit, analyze, build, main,
)
from test_endpoint_distance import synthetic_root, orders, independent_probability


ROOT = Path(__file__).resolve().parents[1]
SETTINGS_VALUE = json.loads((ROOT / SETTINGS).read_text())


def independent_segments(token, patterns):
    expression = '|'.join(re.escape(p) for p in sorted(patterns, key=lambda x: (-len(x), x)))
    return re.findall(f'(?:{expression})|[A-Za-z]' if expression else '[A-Za-z]', token)


@lru_cache(None)
def independent_edit(left, right):
    if not left: return len(right)
    if not right: return len(left)
    return min(1 + independent_edit(left[1:], right), 1 + independent_edit(left, right[1:]),
               (left[0] != right[0]) + independent_edit(left[1:], right[1:]))


def independent_matrix(rows, patterns):
    endpoints = [(tuple(independent_segments(r['tokens'][0], patterns)),
                  tuple(independent_segments(r['tokens'][-1], patterns))) for r in rows]
    return [[None if a == b else Fraction(independent_edit(endpoints[a][1], endpoints[b][0]),
                                         max(len(endpoints[a][1]), len(endpoints[b][0])))
             for b in range(len(rows))] for a in range(len(rows))]


def fraction(value):
    return Fraction(value['numerator'], value['denominator'])


def exhaustive(weights):
    values = [sum((weights[a][b] for a, b in zip(order, order[1:])), Fraction())
              for order in orders(len(weights))]
    mean = sum(values, Fraction()) / len(values)
    variance = sum(((x - mean) ** 2 for x in values), Fraction()) / len(values)
    return values[0], mean, variance


def fixture(root):
    synthetic_root(root)
    (root / PLAN).write_text('Synthetic fixed unit-distance plan.\n')
    (root / SETTINGS).parent.mkdir(parents=True, exist_ok=True)
    (root / SETTINGS).write_bytes((ROOT / SETTINGS).read_bytes())
    (root / PARENT).write_bytes(encoded(parent_build(root)))
    return {**PINS, str(PARENT): digest((root / PARENT).read_bytes())}


class EndpointUnitDistanceTests(unittest.TestCase):
    def test_accepted_maps_reversible_precedence_case_and_partial_fallback(self):
        maps = policies(SETTINGS_VALUE)
        tokens = ['ch', 'Ch', 'cTh', 'ckh', 'qokaiin', 'iiiin', 'cTHh', 'cthh', 'ITh', 'Ao', 'Yk']
        tokens += [''.join(x) for n in range(1, 5) for x in product('cihn', repeat=n)]
        for patterns in maps:
            for token in tokens:
                actual = segment(token, patterns)
                self.assertEqual(actual, independent_segments(token, patterns))
                self.assertEqual(''.join(actual), token)
        self.assertEqual(segment('iiiin', maps[2]), ['i', 'iiin'])
        self.assertEqual(segment('cthh', maps[1]), ['cth', 'h'])
        self.assertEqual(segment('cTHh', maps[1]), ['c', 'T', 'H', 'h'])
        self.assertEqual(segment('CH', maps[1]), ['C', 'H'])
        changed = deepcopy(SETTINGS_VALUE);changed['policies'][1]['patterns'].append('Qo')
        with self.assertRaises(ValueError): policies(changed)

    def test_sequence_edit_matches_independent_recursion_and_has_segment_costs(self):
        values = [tuple(x) for n in range(4) for x in product(('ch', 'Ch'), repeat=n)]
        for left, right in product(values, repeat=2):
            denominator = max(len(left), len(right))
            expected = Fraction(independent_edit(left, right), denominator) if denominator else Fraction()
            self.assertEqual(sequence_distance(left, right), expected)
            self.assertEqual(sequence_distance(left, right), sequence_distance(right, left))
        self.assertEqual(sequence_distance(['ch'], ['sh']), 1)
        self.assertEqual(sequence_distance(list('ch'), list('sh')), Fraction(1, 2))
        self.assertEqual(sequence_distance(['a', 'b'], ['b', 'a']), 1)
        self.assertEqual(sequence_distance([], ['ch']), 1)
        for left in ('ch', [''], [1]):
            with self.assertRaises(ValueError): sequence_distance(left, [])

    def test_all_small_anchored_orders_and_paired_changes(self):
        maps = policies(SETTINGS_VALUE)
        tokens = ('ch', 'sh', 'qokaiin', 'cTh', 'iin', 'a', 'ckh')
        for size in range(1, 8):
            for offset in range(3):
                rows = [{'tokens': [tokens[(i + offset) % len(tokens)], tokens[(2*i + offset) % len(tokens)]]}
                        for i in range(size)]
                weights = [independent_matrix(rows, p) for p in maps]
                for i, patterns in enumerate(maps):
                    self.assertEqual(matrix([[segment(r['tokens'][0], patterns), segment(r['tokens'][-1], patterns)]
                                             for r in rows]), weights[i])
                for selected in weights + [difference(w, weights[0]) for w in weights[1:]]:
                    observed, mean, variance = exhaustive(selected)
                    result = record_moments(selected)
                    self.assertEqual(fraction(result['observed_cost_sum']), observed)
                    self.assertEqual(fraction(result['conditional_mean_cost_sum']), mean)
                    self.assertEqual(fraction(result['conditional_variance_cost_sum']), variance)
                    self.assertEqual(result['invariant'], variance == 0)

    def test_paired_variance_uses_shared_orders_and_can_be_zero_or_negative_change(self):
        size = 5
        base = [[None if a == b else Fraction((a * b + b) % 4, 4) for b in range(size)] for a in range(size)]
        shifted = [[None if a == b else base[a][b] - Fraction(1, 5) for b in range(size)] for a in range(size)]
        self.assertGreater(fraction(record_moments(base)['conditional_variance_cost_sum']), 0)
        self.assertEqual(fraction(record_moments(base)['conditional_variance_cost_sum']),
                         fraction(record_moments(shifted)['conditional_variance_cost_sum']))
        paired = record_moments(difference(shifted, base))
        self.assertEqual(fraction(paired['observed_cost_sum']), Fraction(-4, 5))
        self.assertEqual(fraction(paired['conditional_variance_cost_sum']), 0)
        self.assertTrue(paired['invariant'])

    def test_complete_synthetic_parent_and_cohort_metadata_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); pins = fixture(root)
            with patch('scripts.endpoint_unit_distance.PINS', pins): report = build(root)
            corpus = corpus_build(root);parent = parent_build(root)
            self.assertEqual(report['cohort'], corpus['cohort'])
            self.assertEqual([p['member_keys'] for p in report['paragraphs']],
                             [p['member_keys'] for p in parent['paragraphs']])
            for current, old in zip(report['variants'], parent['variants']):
                for key in old:
                    if key not in ('source_id', 'uncertain_spaces'):
                        self.assertEqual(current['policies'][0][key], old[key])
                self.assertEqual(current['policies'][0]['scope_audit']['endpoint_roles'], 2*old['boundary_count'])
            changed = deepcopy(corpus)
            next(p for p in changed['paragraphs'] if p['common_eligible'])['variants'][0]['loci'][0]['tokens'] = []
            with self.assertRaises(ValueError): analyze(changed, parent, SETTINGS_VALUE)
            forged = deepcopy(parent);forged['paragraphs'][0]['member_keys'].reverse()
            with self.assertRaises(ValueError): analyze(corpus, forged, SETTINGS_VALUE)

    def test_scope_audit_counts_endpoint_roles_without_changing_native_strings(self):
        patterns = policies(SETTINGS_VALUE)[2]
        native = ['cthh', 'qokaiin', 'CH', 'qokaiin']
        endpoints = [[segment(t, patterns), segment(t, patterns)] for t in native]
        result = scope_audit(native, patterns, endpoints)
        self.assertEqual(result['endpoint_roles'], 4)
        self.assertEqual(result['pattern_hits']['cth'], 1)
        self.assertEqual(result['pattern_hits']['iin'], 2)
        self.assertEqual(result['unlisted_example_substring_counts']['cthh'], 1)
        self.assertEqual(result['uppercase_single_letter_fallback_counts'], {'C': 1, 'H': 1})
        self.assertEqual(result['ordered_all_locus_endpoint_segments_sha256'], digest(encoded(endpoints)))

    def test_rejects_changed_pins_even_if_forged_parent_is_repinned(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);pins = fixture(root)
            value = json.loads((root / PARENT).read_text());value['variants'][0]['boundary_count'] += 1
            (root / PARENT).write_bytes(encoded(value))
            with patch('scripts.endpoint_unit_distance.PINS', pins), self.assertRaisesRegex(ValueError, 'pinned input'):
                build(root)
            pins[str(PARENT)] = digest((root / PARENT).read_bytes())
            with patch('scripts.endpoint_unit_distance.PINS', pins), self.assertRaisesRegex(ValueError, 'complete pinned-source replay'):
                build(root)

    def test_cli_strict_json_and_complete_replay_reject_types_and_altered_data(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);pins = fixture(root);output = root / 'report.json'
            def cli(*args):
                with patch('scripts.endpoint_unit_distance.ROOT', root), patch('scripts.endpoint_unit_distance.PINS', pins), \
                        patch('sys.argv', ['unit.py', *args]), redirect_stdout(io.StringIO()): main()
            cli('--output', str(output));report = json.loads(output.read_text())
            cli('--check', str(output))
            changed = deepcopy(report);changed['schema_version'] = True
            altered = deepcopy(report);altered['paragraphs'][0]['variants'][0]['policies'][1]['initial_terminal_segment_counts'][0][0] += 1
            decimal = deepcopy(report);decimal['schema_version'] = 1.0
            for raw in (encoded(changed), encoded(altered), encoded(decimal), b'{"x":1,"x":2}', b'{"x":NaN}'):
                output.write_bytes(raw)
                with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit): cli('--check', str(output))

    def test_initial_and_late_aliases_preserve_all_parent_and_plan_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory);pins = fixture(root)
            targets = [root / PLAN, root / PARENT, root / SETTINGS,
                       root / 'research/transliteration/ENDPOINT_EDIT_DISTANCE_PLAN.md',
                       root / 'research/transliteration/paragraph_corpus_coverage.json']
            for target in targets:
                original = target.read_bytes()
                for kind in ('symlink', 'hardlink'):
                    output = root / f'alias-{kind}.json'
                    if kind == 'symlink': output.symlink_to(target)
                    else: os.link(target, output)
                    with patch('scripts.endpoint_unit_distance.ROOT', root), \
                            patch('sys.argv', ['unit.py', '--output', str(output)]), \
                            redirect_stderr(io.StringIO()), self.assertRaises(SystemExit): main()
                    self.assertEqual(target.read_bytes(), original);output.unlink()
            for kind in ('symlink', 'hardlink'):
                target = root / PLAN;original = target.read_bytes();output = root / f'late-{kind}.json'
                def late_serialize(value):
                    raw = encoded(value)
                    if kind == 'symlink': output.symlink_to(target)
                    else: os.link(target, output)
                    return raw
                with patch('scripts.endpoint_unit_distance.ROOT', root), \
                        patch('scripts.endpoint_unit_distance.build', return_value={'cohort': {'common_eligible_units': 1}}), \
                        patch('scripts.endpoint_unit_distance.encoded', side_effect=late_serialize), \
                        patch('sys.argv', ['unit.py', '--output', str(output)]), \
                        redirect_stderr(io.StringIO()), self.assertRaises(SystemExit): main()
                self.assertEqual(target.read_bytes(), original);output.unlink()


if __name__ == '__main__':
    unittest.main()
