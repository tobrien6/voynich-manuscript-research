from collections import Counter
from contextlib import redirect_stderr
from copy import deepcopy
from fractions import Fraction
import io
from itertools import permutations, product
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.audit_eva_token_coverage import encoded
from scripts.paragraph_token_corpus import build as corpus_build, coverage
from scripts.paragraph_boundary_repetition import (
    COVERAGE, PLAN, analyze, build, fraction, joint_probability, main, moments, probability,
)
from test_paragraph_token_corpus import LEFT, fixture


def exhaustive(rows, selected):
    # Permute occurrence indices: duplicate strings keep their correct weights.
    values = []
    for orders in product(*(permutations(range(len(row))) for row in rows)):
        arranged = [[row[i] for i in order] for row, order in zip(rows, orders)]
        values.append(sum(arranged[i][-1] == arranged[i + 1][0] for i in selected))
    mean = Fraction(sum(values), len(values))
    variance = sum((Fraction(v) - mean) ** 2 for v in values) / len(values)
    return mean, variance


def synthetic_root(root):
    fixture(root, left=LEFT, right=LEFT)
    (root / PLAN).write_text('Fixed synthetic boundary plan.\n')
    (root / COVERAGE).write_bytes(encoded(coverage(corpus_build(root))))
    return root


class BoundaryRepetitionTests(unittest.TestCase):
    def test_exact_moments_for_every_binary_assignment_in_small_layouts(self):
        for lengths in ((1, 1, 1), (2, 1, 2), (2, 2, 2), (2, 3, 2), (2, 2, 2, 2)):
            for letters in product('ab', repeat=sum(lengths)):
                rows, start = [], 0
                for size in lengths:
                    rows.append(list(letters[start:start + size]))
                    start += size
                selected = list(range(len(rows) - 1))
                result = moments(rows, selected)
                mean, variance = exhaustive(rows, selected)
                with self.subTest(lengths=lengths, letters=letters):
                    self.assertEqual(fraction(result['conditional_mean']), mean)
                    self.assertEqual(fraction(result['conditional_variance']), variance)

    def test_singleton_middle_uses_one_occurrence_for_both_boundaries(self):
        left, middle, right = ['a', 'b'], ['a'], ['a', 'b']
        self.assertEqual(joint_probability(left, middle, right), Fraction(1, 4))
        self.assertEqual(probability(left, middle), Fraction(1, 2))
        result = moments([left, middle, right], [0, 1])
        self.assertEqual(fraction(result['conditional_variance']), Fraction(1, 2))

    def test_repeated_middle_without_replacement_joint_can_be_negative_covariance(self):
        rows = [['a'], ['a', 'b'], ['a']]
        self.assertEqual(joint_probability(*rows), 0)
        result = moments(rows, [0, 1])
        self.assertEqual(fraction(result['adjacent_boundary_covariances'][0]['covariance']), Fraction(-1, 4))
        self.assertEqual(fraction(result['conditional_variance']), 0)
        self.assertEqual(result['observed_repeats'], 1)
        self.assertIsNone(result['sd_scaled_contrast'])

    def test_disjoint_boundaries_and_missing_loci_never_create_neighbors(self):
        rows = [['a', 'b'], ['a', 'a'], [], ['a', 'b'], ['a', 'b']]
        result = moments(rows, [0, 3])
        self.assertEqual(result['adjacent_boundary_covariances'], [])
        self.assertEqual(fraction(result['conditional_variance']), Fraction(1, 2))
        self.assertEqual([b['boundary_index'] for b in result['boundaries']], [0, 3])

    def test_invalid_indices_and_empty_endpoint_pairs_fail(self):
        for selected in ([0, 0], [True], [-1], [1]):
            with self.subTest(selected=selected), self.assertRaises(ValueError):
                moments([['a'], ['b']], selected)
        with self.assertRaises(ValueError):
            probability([], ['a'])
        with self.assertRaises(ValueError):
            joint_probability(['a'], [], ['b'])

    def test_common_boundary_exclusions_apply_to_every_variant_and_keep_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            packet = corpus_build(fixture(Path(directory), left=LEFT, right=LEFT))
        paragraph = next(p for p in packet['paragraphs'] if len(p['member_keys']) == 2)
        paragraph['variants'][2]['loci'][0]['tokens'] = []
        paragraph['variants'][2]['loci'][0]['token_count'] = 0
        before = deepcopy(packet)
        result = analyze(packet)
        row = next(p for p in result['paragraphs'] if len(p['member_keys']) == 2)
        self.assertFalse(row['boundary_ledger'][0]['eligible_in_all_variants'])
        self.assertEqual(len(row['boundary_ledger'][0]['omission_reasons']), 1)
        self.assertTrue(all(v['eligible_boundaries'] == 0 and len(v['loci']) == 2 for v in row['variants']))
        self.assertEqual(result['cohort']['common_eligible_units'], 5)
        self.assertEqual(result['cohort']['common_paragraphs_with_no_eligible_boundaries'], 5)
        self.assertEqual(packet, before)

    def test_report_has_no_native_token_payload_and_retains_singletons_and_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            report = build(synthetic_root(Path(directory)))
        self.assertEqual(len(report['paragraphs']), 5)
        self.assertEqual(report['cohort']['candidate_boundaries_in_common_paragraphs'], 1)
        self.assertEqual(report['cohort']['common_paragraphs_with_no_eligible_boundaries'], 4)
        pr = next(p for p in report['paragraphs'] if p['member_keys'] == ['f1r.4'])
        self.assertEqual(pr['variants'][0]['loci'][0]['locator'], '=')
        self.assertEqual(pr['variants'][0]['loci'][0]['variables']['L'], 'B')
        def walk(value):
            if isinstance(value, dict):
                self.assertNotIn('tokens', value)
                for child in value.values(): walk(child)
            elif isinstance(value, list):
                for child in value: walk(child)
        walk(report)

    def test_paragraph_totals_sum_exactly_and_excluded_candidates_remain_accounted(self):
        with tempfile.TemporaryDirectory() as directory:
            packet = corpus_build(fixture(Path(directory)))
        report = analyze(packet)
        self.assertEqual(report['cohort']['candidate_units'], 5)
        self.assertEqual(report['cohort']['excluded_candidate_units'], 1)
        self.assertEqual(len(report['paragraphs']), 4)
        for i, variant in enumerate(report['variants']):
            self.assertEqual(fraction(variant['conditional_mean']),
                             sum((fraction(p['variants'][i]['conditional_mean'])
                                  for p in report['paragraphs']), Fraction()))

    def test_forged_parent_coverage_is_rejected_before_boundary_analysis(self):
        with tempfile.TemporaryDirectory() as directory:
            root = synthetic_root(Path(directory))
            report = json.loads((root / COVERAGE).read_text())
            report['cohort']['common_eligible_units'] += 1
            (root / COVERAGE).write_bytes(encoded(report))
            with patch('scripts.paragraph_boundary_repetition.analyze') as analyzer, \
                    self.assertRaisesRegex(ValueError, 'complete producer replay'):
                build(root)
            analyzer.assert_not_called()

    def test_cli_protects_parent_plan_and_hardlink_aliases_before_computing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = synthetic_root(Path(directory))
            for target in (root / PLAN, root / COVERAGE):
                alias = root / (target.name + '.alias')
                os.link(target, alias)
                for output in (target, alias):
                    before = target.read_bytes()
                    with patch('scripts.paragraph_boundary_repetition.ROOT', root), \
                            patch('scripts.paragraph_boundary_repetition.build') as producer, \
                            patch('sys.argv', ['boundary.py', '--output', str(output)]), \
                            redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                        main()
                    producer.assert_not_called()
                    self.assertEqual(target.read_bytes(), before)

    def test_cli_rejects_symlink_and_hardlink_aliases_created_during_calculation(self):
        for link_kind in ('symlink', 'hardlink'):
            for protected in (PLAN, COVERAGE):
                with self.subTest(link_kind=link_kind, protected=protected), \
                        tempfile.TemporaryDirectory() as directory:
                    root = synthetic_root(Path(directory))
                    target, output = root / protected, root / 'late-output.json'
                    before = target.read_bytes()

                    def late_producer(root):
                        if link_kind == 'symlink':
                            output.symlink_to(target)
                        else:
                            os.link(target, output)
                        return {'cohort': {'common_eligible_units': 0,
                                           'eligible_boundaries_in_all_variants': 0}}

                    with patch('scripts.paragraph_boundary_repetition.ROOT', root), \
                            patch('scripts.paragraph_boundary_repetition.build', side_effect=late_producer), \
                            patch('sys.argv', ['boundary.py', '--output', str(output)]), \
                            redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as failed:
                        main()
                    self.assertEqual(failed.exception.code, 1)
                    self.assertEqual(target.read_bytes(), before)
                    self.assertEqual(output.read_bytes(), before)

    def test_complete_cli_replay_rejects_tampered_science_types_and_duplicate_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root = synthetic_root(Path(directory))
            report = build(root)
            altered = deepcopy(report)
            altered['variants'][0]['observed_repeats'] += 1
            typed = deepcopy(report)
            typed['schema_version'] = True
            for raw in (encoded(altered), encoded(typed), b'{"x":1,"x":2}', b'{"x":NaN}'):
                cache = root / 'changed.json'
                cache.write_bytes(raw)
                with patch('scripts.paragraph_boundary_repetition.ROOT', root), \
                        patch('sys.argv', ['boundary.py', '--check', str(cache)]), \
                        redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    main()


if __name__ == '__main__':
    unittest.main()
