import contextlib
import io
import itertools
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts import currier_roundtrip_language as study


class LanguageTests(unittest.TestCase):
    def compare_all(self, rules, maximum):
        machine = study.graph(rules)
        expected = []
        for n in range(maximum + 1):
            passed = 0
            for sequence in itertools.product(sorted(rules), repeat=n):
                encoded = ''.join(rules[k] for k in sequence)
                # Independent exhaustive segmentation: enumerate every possible
                # prefix at each position, then select the longest whole-word match.
                position, returned, invalid = 0, [], False
                while position < len(encoded):
                    candidates = [(end, k) for end in range(position + 1, len(encoded) + 1)
                                  for k, word in rules.items() if encoded[position:end] == word]
                    if not candidates:
                        invalid = True
                        break
                    end, k = max(candidates)
                    returned.append(k)
                    position = end
                accept = not invalid and tuple(returned) == sequence
                self.assertEqual(study.decisions(machine, sequence), accept, (rules, sequence))
                passed += accept
            expected.append(passed)
        self.assertEqual([r['accepted'] for r in study.counts(machine, list(range(maximum + 1)))], expected)
        return machine

    def test_all_small_injective_binary_dictionaries(self):
        words = ['0', '1', '00', '01', '10', '11']
        assignments = cases = 0
        for size in (2, 3):
            for definition in itertools.permutations(words, size):
                self.compare_all(dict(enumerate(definition, 1)), 5)
                assignments += 1
                cases += sum(size ** n for n in range(6))
        self.assertEqual(assignments, 150)
        self.assertEqual(cases, 45570)

    def test_long_delay_straddling_and_eof(self):
        for rules in ({1: 'a', 2: 'aa', 3: 'aaaa'}, {1: 'a', 2: 'b', 3: 'aabb'},
                      {1: 'ab', 2: 'b', 3: 'aba'}, {1: 'a', 2: 'bc', 3: 'ab'}):
            self.compare_all(rules, 6)
        machine = study.graph({1: 'a', 2: 'aa', 3: 'aaaa'})
        self.assertTrue(study.decisions(machine, (1,)))
        self.assertFalse(study.decisions(machine, (1, 1)))
        self.assertTrue(study.decisions(machine, (2,)))
        self.assertTrue(study.decisions(machine, (3,)))

    def test_prefix_free_complete_recovery_and_count_mass(self):
        machine = self.compare_all({1: '00', 2: '01', 3: '10'}, 5)
        self.assertEqual(len(machine['states']), 2)
        for row in study.counts(machine, list(range(13))):
            self.assertEqual(row['accepted'], 3 ** row['source_codes'])
            self.assertEqual(row['accepted_fraction'], {'numerator': 1, 'denominator': 1})

    def test_irrevocable_mismatch_and_unmatched_reference(self):
        rules = {1: 'a', 2: 'bc', 3: 'ab'}
        self.assertIsNone(study.advance((1,), 2, rules))
        returned, unknown = study.reference_decode('abc', rules)
        self.assertEqual(returned, (3, None))
        self.assertEqual(unknown[0]['encoded_offset_0based'], 2)

    def test_all_states_have_shortest_reaching_paths(self):
        machine = study.graph({1: 'a', 2: 'aa', 3: 'aaaa'})
        for state in machine['states'][:-1]:
            path = tuple(state['shortest_reaching_rule_lines'])
            pending = ()
            for k in path:
                pending = study.advance(pending, k, {1: 'a', 2: 'aa', 3: 'aaaa'})
            self.assertEqual(list(pending), state['pending_rule_lines'])
            for n in range(len(path)):
                for shorter in itertools.product((1, 2, 3), repeat=n):
                    q = ()
                    for k in shorter:
                        if q is not None:
                            q = study.advance(q, k, {1: 'a', 2: 'aa', 3: 'aaaa'})
                    self.assertNotEqual(q, pending)

    def test_invalid_rules_and_reference_empty(self):
        for rules in ({}, {1: ''}, {1: 'a', 2: 'a'}, {True: 'a'}, {'1': 'a'}):
            with self.assertRaises(ValueError):
                study.graph(rules)
        self.assertEqual(study.reference_decode('', {1: 'a'}), ((), []))


class ProtectionTests(unittest.TestCase):
    def test_eight_input_direct_and_early_late_link_aliases(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = [root / str(n) for n in range(8)]
            for source in sources:
                source.write_bytes(b'protected')
            checked = 0
            for n, source in enumerate(sources):
                with self.assertRaises(ValueError):
                    study.guard_output(source, sources)
                checked += 1
                for late in (False, True):
                    for symbolic in (False, True):
                        output = root / f'output-{n}-{late}-{symbolic}'
                        if late:
                            study.guard_output(output, sources)
                        if symbolic:
                            output.symlink_to(source)
                        else:
                            os.link(source, output)
                        with self.assertRaises(ValueError):
                            study.guard_output(output, sources)
                        checked += 1
            self.assertEqual(checked, 40)
            self.assertTrue(all(s.read_bytes() == b'protected' for s in sources))

    def test_strict_json_rejects_duplicate_nonfinite_and_preserves_types(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'x.json'
            for bad in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}', '{"a":-Infinity}'):
                path.write_text(bad)
                with self.assertRaises(ValueError):
                    study.read_json(path)
            path.write_text('{"a":true}')
            self.assertNotEqual(study.canonical(study.read_json(path)), study.canonical({'a': 1}))

    def test_source_and_dependency_failure_preserves_existing_output(self):
        # Source identity checks only: no graph/count measurement on primary bytes.
        reference = Path('/private/tmp/voynich-currier-conversion-reference-01a12dd5')
        if not reference.is_dir():
            self.skipTest('local primary cache unavailable; use --reference for primary replay')
        with tempfile.TemporaryDirectory() as directory:
            root, refs = Path(directory) / 'root', Path(directory) / 'refs'
            refs.mkdir(parents=True)
            for name in ('Curr-Eva_def.bit', 'Bitrans_manual.pdf', '000_README.txt'):
                shutil.copyfile(reference / name, refs / name)
            plan = study.read_json(study.ROOT / study.PLAN)
            for name in [study.PLAN, plan['human_plan'], *plan['dependency_hashes']]:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(study.ROOT / name, target)
            self.assertEqual(len(study.load_inputs(refs, root)[2]), 38)
            paths = [root / study.PLAN, root / plan['human_plan'],
                     *[root / name for name in plan['dependency_hashes']],
                     *[refs / name for name in ('Curr-Eva_def.bit', 'Bitrans_manual.pdf', '000_README.txt')]]
            output = Path(directory) / 'existing.json'
            for path in paths:
                original = path.read_bytes()
                path.write_bytes(original + b'changed')
                output.write_bytes(b'keep')
                with self.assertRaises(ValueError):
                    study.load_inputs(refs, root)
                with patch.object(study, 'run_study', side_effect=lambda ref: study.load_inputs(ref, root)), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(study.main(['--reference', str(refs), '--output', str(output)]), 1)
                self.assertEqual(output.read_bytes(), b'keep')
                path.write_bytes(original)

    def test_late_alias_swap_in_cli_does_not_overwrite_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / 'source', root / 'output'
            source.write_bytes(b'keep')
            def calculate(reference):
                output.symlink_to(source)
                return {'result': 1}
            with patch.object(study, 'protected_files', return_value=[source]), patch.object(study, 'run_study', side_effect=calculate), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(study.main(['--reference', str(root), '--output', str(output)]), 1)
            self.assertEqual(source.read_bytes(), b'keep')


    def test_serialization_alias_swap_and_failure_preserve_input_and_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / 'source', root / 'output'
            source.write_bytes(b'keep source')
            output.write_bytes(b'keep output')
            original_dumps = json.dumps
            def swapped(*args, **kwargs):
                output.unlink()
                output.symlink_to(source)
                return original_dumps(*args, **kwargs)
            with patch.object(study, 'protected_files', return_value=[source]), patch.object(study, 'run_study', return_value={'result': 1}), patch.object(study.json, 'dumps', side_effect=swapped), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(study.main(['--reference', str(root), '--output', str(output)]), 1)
            self.assertEqual(source.read_bytes(), b'keep source')
            output.unlink()
            output.write_bytes(b'keep output')
            with patch.object(study, 'protected_files', return_value=[source]), patch.object(study, 'run_study', return_value={'value': float('nan')}), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(study.main(['--reference', str(root), '--output', str(output)]), 1)
            self.assertEqual(output.read_bytes(), b'keep output')

    def test_removed_name_and_entry_target_are_retained_until_write(self):
        for retarget in (False, True):
            with self.subTest(retarget=retarget), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                empty = root / 'empty'; empty.mkdir()
                original = root / 'Protected.txt'; original.write_bytes(b'synthetic')
                source = root / 'source'; source.symlink_to(original)
                output_parent = root / 'output-parent'; output_parent.symlink_to(empty, target_is_directory=True)
                output = output_parent / 'PROTECTED.TXT'
                def changed(*args):
                    original.unlink()
                    if retarget:
                        source.unlink(); source.symlink_to(root / 'elsewhere.txt')
                    output_parent.unlink(); output_parent.symlink_to(root, target_is_directory=True)
                    return {'result': 1}
                with patch.object(study, 'protected_files', return_value=[source]), patch.object(study, 'run_study', side_effect=changed), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(study.main(['--reference', str(root), '--output', str(output)]), 1)
                self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
