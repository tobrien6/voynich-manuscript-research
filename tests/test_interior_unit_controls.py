from collections import Counter
import contextlib
from copy import deepcopy
from fractions import Fraction
import hashlib
import io
import itertools
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import interior_unit_controls as module


def settings():
    return json.loads((module.ROOT / module.SETTINGS).read_text())


def converted(token_rows):
    policy = settings()
    return module.convert_rows(token_rows, policy['policies'], policy['fallback_examples_not_grouped'])


def rational_r(values):
    m, total = len(values), sum(values)
    d = [m * x - total for x in values]
    squared = sum(x * x for x in d)
    return Fraction(m * sum(a * b for a, b in zip(d, d[1:])), (m - 1) * squared) if squared else Fraction(0)


class InteriorUnitControlTests(unittest.TestCase):
    def fixture(self):
        return [('f1r', 'f1r.1', ['left', 'Ch', 'iin', 'cthh', 'right']),
                ('f1r', 'f1r.2', ['start', 'a', 'b', 'c', 'end']),
                ('f1v', 'f1v.1', ['y', 'ch', 'a', 'sh', 'y']),
                ('f2r', 'f2r.1', ['first', 'a', 'ch', 'iiiir', 'cph', 'il', 'a', 'last'])]

    def test_longest_match_preserves_case_boundaries_endpoints_and_source_tokens(self):
        rows = [('f1r', 'k', ['cph', 'Ch', 'iin', 'cthh', 'sh'])]
        saved = deepcopy(rows)
        variants = converted(rows)
        self.assertEqual([v['rows'][0][2] for v in variants], [[2, 3, 4], [1, 3, 2], [1, 1, 2]])
        self.assertEqual(rows, saved)
        audit = variants[2]['scope_audit']
        self.assertEqual(audit['tokens'], 3)
        self.assertEqual(audit['native_ascii_letters'], 9)
        self.assertEqual(audit['emitted_segments'], 4)
        self.assertEqual(audit['pattern_hits']['Ch'], 1)
        self.assertEqual(audit['pattern_hits']['iin'], 1)
        self.assertEqual(audit['pattern_hits']['cth'], 1)
        self.assertEqual(audit['pattern_hits']['cph'], 0)  # Endpoint is outside audit/statistic.
        self.assertEqual(audit['pattern_hits']['sh'], 0)
        self.assertEqual(audit['unlisted_example_substring_counts']['cthh'], 1)

    def test_unlisted_forms_and_uppercase_fallback_are_not_invented_new_units(self):
        rows = [('p', 'k', ['a', 'cTHh', 'iiiin', 'Aa', 'y'])]
        v = converted(rows)[2]
        self.assertEqual(v['rows'][0][2], [4, 2, 2])
        self.assertEqual(v['scope_audit']['uppercase_single_letter_fallback_counts'], {'A': 1, 'H': 1, 'T': 1})
        self.assertEqual(v['scope_audit']['unlisted_example_substring_counts']['cTHh'], 1)

    def test_invalid_native_rows_and_policy_contracts_fail(self):
        for rows in ([], [('p', 'k', ['a'] * 4)], [('p', 'k', 'abcde')],
                     [('p', 'k', ['a', 'b', '?', 'd', 'e'])], self.fixture() + self.fixture()[:1]):
            with self.assertRaises(ValueError):
                converted(rows)
        policy = settings()['policies']
        for changed in (list(reversed(policy)), [{**policy[0], 'patterns': ['ch']}, *policy[1:]]):
            with self.assertRaises(ValueError):
                module.convert_rows(self.fixture(), changed, [])

    def test_original_index_permutations_are_paired_across_every_unit_policy(self):
        variants = converted(self.fixture())
        base = variants[0]['rows']; digest = module.corpus_digest(base)
        index_rows = [(p, k, list(range(len(x)))) for p, k, x in base]
        for generator in (module.original.control_rows, module.half.control_rows):
            for trial in range(9):
                indices = generator(index_rows, digest, 17, trial)
                for v in variants:
                    applied = module.apply_indices(v['rows'], indices)
                    self.assertEqual(applied, generator(v['rows'], digest, 17, trial))
                    for before, after in zip(v['rows'], applied):
                        self.assertEqual(Counter(before[2]), Counter(after[2]))
                        if generator == module.half.control_rows:
                            split = (len(before[2]) + 1) // 2
                            self.assertEqual(Counter(before[2][:split]), Counter(after[2][:split]))
                            self.assertEqual(Counter(before[2][split:]), Counter(after[2][split:]))
        for order in ([0, 0, 2], [False, True, 2], [0., 1, 2], [0, 1], [0, 1, 3]):
            with self.assertRaises(ValueError):
                module.apply_indices([('p', 'k', [1, 2, 3])], [('p', 'k', order)])
        with self.assertRaises(ValueError):
            module.apply_indices([('p', 'k', [1, 2, 3])], [('other', 'k', [0, 1, 2])])

    def test_half_expectation_matches_independent_exhaustive_permutations(self):
        for values in ([1, 2, 3], [1, 3, 2], [2, 2, 2], [1, 3, 2, 1], [1, 3, 2, 1, 1]):
            split = (len(values) + 1) // 2
            orders = [a + b for a in itertools.permutations(values[:split])
                      for b in itertools.permutations(values[split:])]
            expected = sum((rational_r(order) for order in orders), Fraction(0)) / len(orders)
            actual = module.moments([('p', 'k', values)])
            recorded = actual['half_expectation_rational']
            self.assertEqual(Fraction(int(recorded['numerator']), int(recorded['denominator'])), expected)
            self.assertAlmostEqual(actual['half_centered_association'], float(rational_r(values) - expected))
            full = list(itertools.permutations(values))
            expectation = sum((rational_r(order) for order in full), Fraction(0)) / len(full)
            self.assertAlmostEqual(actual['exact_unrestricted_null_expectation'], float(expectation))

    def test_constant_collapse_and_all_invariant_cases_remain_in_denominator(self):
        rows = [('p', 'collapse', ['left', 'ch', 'a', 'sh', 'right']),
                ('p', 'already', ['left', 'a', 'b', 'c', 'right'])]
        v = converted(rows)
        analyzed = module.analyze(v, v[0]['length_corpus_sha256'], trials=7, seed=17)
        for result in analyzed:
            self.assertEqual(result['loci'], 2)
            self.assertEqual(result['interior_tokens'], 6)
            self.assertEqual(result['interior_adjacent_pairs'], 4)
            self.assertEqual(result['exact_half_invariance']['accepted_effect_denominator'], 2)
        for result in analyzed[1:]:
            self.assertEqual(result['newly_constant_from_ascii'], ['collapse'])
            self.assertEqual(result['constant_interior_loci'], 2)
            for scope in ('unrestricted', 'half'):
                self.assertEqual(result[scope]['observed_centered_association'], 0)
                self.assertEqual(result[scope]['control_statistics'], [0.] * 7)
        invariant = module.classify([('p', 'nonconstant', [1, 3, 2])])
        self.assertEqual(invariant['both_half_constant_loci'], 0)
        self.assertEqual(invariant['exact_invariant_loci'], 1)

    def test_ascii_reproduces_both_original_producers_and_every_draw(self):
        tokens = self.fixture(); v = converted(tokens)
        new = module.analyze(v, v[0]['length_corpus_sha256'], trials=17, seed=module.SEED)
        mapping = {key: {'page_id': page, 'tokens': native} for page, key, native in tokens}
        full = module.original.summarize(mapping, [key for _, key, _ in tokens], 17, module.SEED)
        halves = module.half.summarize(v[0]['rows'], repetitions=17, seed=module.SEED)
        module.verify_ascii(new[0], full, halves)
        changed = deepcopy(new[0]); changed['half']['control_statistics'][0] += 1e-4
        with self.assertRaisesRegex(ValueError, 'reproduction differs'):
            module.verify_ascii(changed, full, halves)

    def test_paired_changes_use_identical_draw_indices_and_retain_all_trials(self):
        v = converted(self.fixture()); analyzed = module.analyze(v, v[0]['length_corpus_sha256'], trials=11, seed=17)
        for result in analyzed[1:]:
            for scope in ('unrestricted', 'half'):
                paired = result['paired_change_from_ascii'][scope]
                self.assertEqual(paired['control_statistics'], [g - a for g, a in zip(
                    result[scope]['control_statistics'], analyzed[0][scope]['control_statistics'])])
                self.assertEqual(paired['observed_centered_association'],
                    result[scope]['observed_centered_association'] - analyzed[0][scope]['observed_centered_association'])
                self.assertEqual(len(paired['control_statistics']), 11)
        with self.assertRaises(ValueError):
            module.paired_change({'control_statistics': [1]}, {'control_statistics': [1, 2]})

    def test_changed_ascii_digest_slots_or_seed_are_rejected(self):
        v = converted(self.fixture())
        for trials, seed in ((True, 17), (0, 17), (1, True), (1, -1)):
            with self.assertRaises(ValueError):
                module.analyze(v, v[0]['length_corpus_sha256'], trials=trials, seed=seed)
        with self.assertRaises(ValueError):
            module.analyze(v, 'wrong', trials=1)
        changed = deepcopy(v); changed[2]['rows'][0][2].append(1)
        with self.assertRaises(ValueError):
            module.analyze(changed, v[0]['length_corpus_sha256'], trials=1)

    def test_pin_drift_is_rejected_before_json_or_corpus_processing(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); path = root / 'fixture.json'; path.write_bytes(b'changed')
            with patch.object(module, 'PINS', {'fixture.json': hashlib.sha256(b'original').hexdigest()}):
                with self.assertRaisesRegex(ValueError, 'pinned input changed'):
                    module.pinned_inputs(root)

    def fixture_root(self, root):
        catalog = root / 'data/transliterations.json'; catalog.parent.mkdir()
        native = root / 'native.txt'; native.write_text('synthetic native source')
        catalog.write_text(json.dumps({'sources': [{'path': 'native.txt'}]}))
        plan = root / 'plan.md'; plan.write_text('synthetic plan')
        pin = root / 'pin.json'; pin.write_text('synthetic pin')
        return native, catalog, plan, pin

    def test_output_paths_symbolic_hardlink_and_native_aliases_are_protected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); paths = self.fixture_root(root)
            with patch.multiple(module, PLAN='plan.md', PINS={'pin.json': 'synthetic'}):
                for i, path in enumerate(paths):
                    before = path.read_bytes()
                    for kind in ('direct', 'symbolic', 'hard'):
                        output = path if kind == 'direct' else root / f'alias-{i}-{kind}'
                        if kind == 'symbolic': output.symlink_to(path)
                        if kind == 'hard': output.hardlink_to(path)
                        with self.assertRaises(ValueError): module.protect_output(output, root)
                        self.assertEqual(path.read_bytes(), before)
                for name in ('data/new.json', 'scripts/new.py'):
                    with self.assertRaises(ValueError): module.protect_output(root / name, root)
                module.protect_output(root / 'separate.json', root)

    def test_late_alias_is_rejected_after_stubbed_calculation_without_input_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); native, catalog, plan, pin = self.fixture_root(root)
            output = root / 'report.json'
            before = {p: p.read_bytes() for p in (native, catalog, plan, pin)}
            def produce(*args):
                output.hardlink_to(native)
                return {'synthetic': True}
            with patch.multiple(module, ROOT=root, PLAN='plan.md', PINS={'pin.json': 'synthetic'}):
                with patch.object(module, 'report', side_effect=produce), patch('sys.argv', ['units', '--output', str(output)]):
                    with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                        module.main()
            self.assertEqual(error.exception.code, 1)
            self.assertEqual({p: p.read_bytes() for p in before}, before)


if __name__ == '__main__':
    unittest.main()
