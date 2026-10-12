"""Independent cut-point/edit oracle and complete finite probability ledgers."""

from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from itertools import product
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts import wrap_boundary_costs as producer


def recursive_cost(a, b):
    @lru_cache(None)
    def distance(i, j):
        if not i:
            return j
        if not j:
            return i
        return min(distance(i - 1, j) + 1, distance(i, j - 1) + 1,
                   distance(i - 1, j - 1) + (a[i - 1] != b[j - 1]))
    return Fraction(distance(len(a), len(b)), max(len(a), len(b)))


def independent_trace(widths, capacity, separator):
    rows, start = [], 0
    while start < len(widths):
        fits = [end for end in range(start + 1, len(widths) + 1)
                if sum(widths[start:end]) + separator * (end - start - 1) <= capacity]
        end = max(fits)
        occupied = sum(widths[start:end]) + separator * (end - start - 1)
        if end == len(widths):
            return rows, {'start': start, 'end_exclusive': end, 'occupied_width': occupied, 'closed_by_overflow': False}
        rows.append({'start': start, 'end_exclusive': end, 'occupied_width': occupied,
                     'carried_position': end, 'carried_width': widths[end]})
        start = end
    raise AssertionError('positive finite input must leave a tail')


def independent_law(law):
    probabilities = dict(zip(law['labels'], map(Fraction, law['probabilities'])))
    widths = sorted({len(label) for label in probabilities})
    bin_mass = {w: sum(p for label, p in probabilities.items() if len(label) == w) for w in widths}
    costs = {(a, b): recursive_cost(a, b) for a in probabilities for b in probabilities}
    mu = {(u, v): sum(probabilities[a] / bin_mass[u] * probabilities[b] / bin_mass[v] * costs[a, b]
                       for a in probabilities for b in probabilities if len(a) == u and len(b) == v)
          for u in widths for v in widths}
    incoming = sum(probabilities[a] * probabilities[b] * costs[a, b] for a in probabilities for b in probabilities)
    return probabilities, costs, mu, incoming


class BoundaryCalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = json.loads((producer.ROOT / producer.BASE / 'settings.json').read_bytes())
        cls.report = producer.build()

    def test_every_declared_stream_trace_cost_probability_and_mean(self):
        laws = {law['id']: law for law in self.settings['laws']}
        for case in self.report['cases']:
            law = laws[case['law_id']]
            probabilities, costs, mu, incoming = independent_law(law)
            self.assertEqual([s['labels'] for s in case['streams']],
                             [list(labels) for labels in product(law['labels'], repeat=7)])
            for stream in case['streams']:
                labels = stream['labels']; widths = list(map(len, labels))
                p = Fraction(1)
                for label in labels:
                    p *= probabilities[label]
                rows, tail = independent_trace(widths, case['capacity'], 1)
                self.assertEqual(stream['widths'], widths)
                self.assertEqual(stream['probability'], str(p))
                self.assertEqual(stream['completed_rows'], rows)
                self.assertEqual(stream['unclosed_tail'], tail)
                self.assertTrue(all(r['end_exclusive'] - r['start'] >= 2 for r in rows))
                ends = [position for row in [*rows, tail] for position in range(row['start'], row['end_exclusive'])]
                self.assertEqual(ends, list(range(7)))
                s = m = Fraction(); edges = []
                for index in range(len(rows) - 1):
                    a, b = rows[index]['end_exclusive'] - 1, rows[index + 1]['start']
                    self.assertEqual(b, a + 1)
                    d, expected = costs[labels[a], labels[b]], mu[widths[a], widths[b]]
                    s += d; m += expected
                    edges.append({'left_row_index': index, 'right_row_index': index + 1,
                                  'last_position': a, 'first_position': b, 'width_pair': [widths[a], widths[b]],
                                  'observed_cost': str(d), 'width_reference_cost': str(expected)})
                self.assertEqual(stream['boundaries'], edges)
                self.assertEqual(stream['boundary_count'], len(edges))
                self.assertEqual(stream['observed_cost_sum'], str(s))
                self.assertEqual(stream['width_reference_sum'], str(m))
                self.assertEqual(stream['width_centered_sum'], str(s - m))
                self.assertEqual(stream['incoming_centered_sum'], str(s - len(edges) * incoming))
                means = {'observed_mean': str(s / len(edges)), 'width_reference_mean': str(m / len(edges)),
                         'width_centered_mean': str((s - m) / len(edges)),
                         'incoming_centered_mean': str(s / len(edges) - incoming)} if edges else dict.fromkeys(stream['means'])
                self.assertEqual(stream['means'], means)

    def test_all_width_classes_and_two_aggregate_estimands(self):
        laws = {law['id']: law for law in self.settings['laws']}
        for case in self.report['cases']:
            incoming = independent_law(laws[case['law_id']])[3]
            groups = defaultdict(list)
            for stream in case['streams']:
                groups[tuple(stream['widths'])].append(stream)
            mass = sum(Fraction(s['probability']) for s in case['streams'])
            eligible = [s for s in case['streams'] if s['boundary_count']]
            em = sum((Fraction(s['probability']) for s in eligible), Fraction())
            den = sum((Fraction(s['probability']) * s['boundary_count'] for s in case['streams']), Fraction())
            observed = sum((Fraction(s['probability']) * Fraction(s['observed_cost_sum']) for s in case['streams']), Fraction())
            matched = sum((Fraction(s['probability']) * Fraction(s['width_reference_sum']) for s in case['streams']), Fraction())
            eo = sum((Fraction(s['probability']) * Fraction(s['observed_cost_sum']) / s['boundary_count'] for s in eligible), Fraction())
            er = sum((Fraction(s['probability']) * Fraction(s['width_reference_sum']) / s['boundary_count'] for s in eligible), Fraction())
            self.assertEqual(mass, 1)
            for key, value in [('probability_mass', mass), ('eligible_probability_mass', em),
                               ('no_boundary_probability_mass', 1 - em), ('expected_boundary_count', den),
                               ('weighted_observed_sum', observed), ('weighted_width_reference_sum', matched),
                               ('weighted_eligible_stream_mean_sum', eo), ('weighted_eligible_width_reference_mean_sum', er)]:
                self.assertEqual(case[key], str(value))
            self.assertEqual(case['eligible_streams'], len(eligible))
            self.assertEqual(case['total_streams'], len(case['streams']))
            for field, a, b, denominator in [('pooled_boundaries', observed, matched, den),
                                            ('equal_eligible_streams', eo, er, em)]:
                expected = {'observed_mean': str(a / denominator), 'width_reference_mean': str(b / denominator),
                            'width_centered_mean': str((a - b) / denominator),
                            'incoming_centered_mean': str(a / denominator - incoming)} if denominator else dict.fromkeys(case[field])
                self.assertEqual(case[field], expected)
            expected_signs = {key: sum((Fraction(s['probability']) for s in eligible
                                      if ('positive' if Fraction(s['width_centered_sum']) > 0 else
                                          'negative' if Fraction(s['width_centered_sum']) < 0 else 'zero') == key), Fraction())
                              for key in ['negative', 'zero', 'positive']}
            self.assertEqual(case['eligible_residual_sign_probability'], {k: str(v) for k, v in expected_signs.items()})
            self.assertEqual([g['widths'] for g in case['width_classes']], [list(w) for w in sorted(groups)])
            for record in case['width_classes']:
                group = groups[tuple(record['widths'])]
                gm = sum(Fraction(s['probability']) for s in group)
                gn = group[0]['boundary_count']
                go = sum(Fraction(s['probability']) * Fraction(s['observed_cost_sum']) for s in group)
                gr = sum(Fraction(s['probability']) * Fraction(s['width_reference_sum']) for s in group)
                self.assertEqual(record['label_stream_count'], len(group))
                self.assertEqual(record['probability_mass'], str(gm))
                self.assertEqual(record['boundary_count'], gn)
                self.assertEqual(record['weighted_observed_sum'], str(go))
                self.assertEqual(record['weighted_width_reference_sum'], str(gr))
                self.assertEqual(go, gr)
                means = {'observed_mean': str(go / (gm * gn)), 'width_reference_mean': str(gr / (gm * gn)),
                         'width_centered_mean': '0', 'incoming_centered_mean': str(go / (gm * gn) - incoming)} if gn else dict.fromkeys(record['means'])
                self.assertEqual(record['means'], means)

    def test_pair_matrices_keep_repeated_labels_and_unequal_bins(self):
        for law, record in zip(self.settings['laws'], self.report['laws']):
            p, costs, mu, incoming = independent_law(law)
            self.assertEqual(record['pair_costs'], [[str(costs[a, b]) for b in law['labels']] for a in law['labels']])
            self.assertEqual(record['incoming_pair_mean_cost'], str(incoming))
            self.assertEqual(record['width_conditioned_costs'],
                             [{'left_width': u, 'right_width': v, 'mean_cost': str(mu[u, v])} for u, v in sorted(mu)])
            self.assertEqual(record['width_probabilities'],
                             [{'width': w, 'probability': str(sum(prob for label, prob in p.items() if len(label) == w))}
                              for w in sorted({len(label) for label in p})])
        unequal = self.report['laws'][1]
        self.assertIn({'left_width': 2, 'right_width': 2, 'mean_cost': '3/16'}, unequal['width_conditioned_costs'])

    def test_known_zero_empty_and_nonzero_realization_calibrations(self):
        constant, empty = self.report['cases'][-2:]
        for field in ['pooled_boundaries', 'equal_eligible_streams']:
            self.assertEqual(constant[field]['incoming_centered_mean'], '0')
            self.assertEqual(constant[field]['width_centered_mean'], '0')
            self.assertTrue(all(value is None for value in empty[field].values()))
        self.assertGreater(Fraction(constant['eligible_residual_sign_probability']['negative']), 0)
        self.assertGreater(Fraction(constant['eligible_residual_sign_probability']['positive']), 0)
        self.assertEqual(empty['eligible_streams'], 0)
        self.assertEqual(empty['expected_boundary_count'], '0')
        self.assertTrue(any(s['unclosed_tail']['occupied_width'] == 20 for s in empty['streams']))
        self.assertTrue(all(s['unclosed_tail']['closed_by_overflow'] is False for c in self.report['cases'] for s in c['streams']))

    def test_separate_estimands_and_geometry_implementation_examples(self):
        record = producer.case_record({'id': 'known weighting fixture', 'capacity': 5},
                                     {'id': 'tiny', 'labels': ['a', 'bb'], 'probabilities': ['1/2', '1/2']}, 7, 1)
        self.assertNotEqual(record['pooled_boundaries']['observed_mean'], record['equal_eligible_streams']['observed_mean'])
        for widths, capacity, separator in [([1, 2, 1, 2, 2], 4, 0), ([2, 2, 2], 5, 1), ([1, 1, 1], 5, 1)]:
            self.assertEqual(producer.wrap_trace(widths, capacity, separator), independent_trace(widths, capacity, separator))
        with self.assertRaises(ValueError):
            producer.case_record({'id': 'singleton', 'capacity': 2}, self.settings['laws'][0], 7, 1)

    def test_input_domain_and_archive_drift_fail(self):
        for law in [{'id': 'bad', 'labels': ['a', 'a'], 'probabilities': ['1/2', '1/2']},
                    {'id': 'bad', 'labels': ['a', 'bb'], 'probabilities': ['1', '0']},
                    {'id': 'bad', 'labels': [''], 'probabilities': ['1']}]:
            with self.assertRaises(ValueError):
                producer.law_record(law)
        with patch.object(producer.subprocess, 'check_output', return_value=b'changed'):
            with self.assertRaisesRegex(ValueError, 'frozen protocol differs'):
                producer.frozen_inputs()

    def test_protocol_verification_does_not_require_the_topic_object(self):
        original_lookup = producer.subprocess.check_output
        calls = []
        def main_only_lookup(args, **kwargs):
            calls.append(args)
            if any(isinstance(arg, str) and arg.startswith(producer.PROTOCOL_COMMIT + ':') for arg in args):
                raise subprocess.CalledProcessError(128, args)
            return original_lookup(args, **kwargs)
        with patch.object(producer.subprocess, 'check_output', side_effect=main_only_lookup):
            settings, hashes = producer.frozen_inputs()
        self.assertEqual(settings, self.settings)
        self.assertEqual(hashes, self.report['protocol_sha256'])
        self.assertEqual([args[2].split(':')[0] for args in calls[:2]], [producer.PROTOCOL_SOURCE_COMMIT] * 2)

    def test_repair_preserves_every_original_field_except_two_runtime_fingerprints(self):
        raw = subprocess.check_output(['git', 'show', producer.PROTOCOL_SOURCE_COMMIT + ':' + producer.BASE + '/results.json'],
                                      cwd=producer.ROOT)
        self.assertEqual(producer.sha(raw), '6aa35b7ace4bcac9f968139aea286eed2b7ecb194a7d1f9d1c41e3f367ec5bba')
        original = json.loads(raw)
        current = dict(self.report)
        old_hashes = original.pop('implementation_sha256')
        new_hashes = current.pop('implementation_sha256')
        self.assertEqual(original, current)
        paths = {'scripts/wrap_boundary_costs.py', 'tests/test_wrap_boundary_costs.py'}
        self.assertEqual(set(old_hashes), paths)
        self.assertEqual(set(new_hashes), paths)
        for path in paths:
            archived = subprocess.check_output(['git', 'show', producer.PROTOCOL_SOURCE_COMMIT + ':' + path], cwd=producer.ROOT)
            self.assertEqual(old_hashes[path], producer.sha(archived))
            self.assertEqual(new_hashes[path], producer.sha((producer.ROOT / path).read_bytes()))
        self.assertNotEqual(old_hashes, new_hashes)

    def test_existing_alias_and_late_output_preservation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); original = root / 'original'; original.write_bytes(b'keep original')
            for name, symbolic in [('symbolic', True), ('hardlink', False)]:
                target = root / name
                target.symlink_to(original) if symbolic else os.link(original, target)
                with self.assertRaises(ValueError):
                    producer.write_new(target, b'changed')
            real_open = Path.open
            def late_alias(path, *args, **kwargs):
                os.link(original, path)
                return real_open(path, *args, **kwargs)
            with patch.object(Path, 'open', autospec=True, side_effect=late_alias):
                with self.assertRaises(FileExistsError):
                    producer.write_new(root / 'late', b'changed')
            self.assertEqual(original.read_bytes(), b'keep original')
            self.assertEqual((root / 'late').read_bytes(), b'keep original')
            output = root / 'new.json'; producer.write_new(output, producer.serialize(self.report))
            self.assertEqual(json.loads(output.read_bytes()), self.report)
            with self.assertRaises(ValueError):
                producer.write_new(output, b'changed')

    def test_complete_deterministic_replay(self):
        self.assertEqual(producer.serialize(producer.build()), producer.serialize(self.report))


if __name__ == '__main__':
    unittest.main()
