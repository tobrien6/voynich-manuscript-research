import contextlib
import copy
import gzip
import hashlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import exact_slot_predictor_controls as m


class FixedDraws:
    def __init__(self, values):
        self.values = iter(values)
        self.bounds = []
    def below(self, bound):
        self.bounds.append(bound)
        return next(self.values)


class ExactSlotControlTests(unittest.TestCase):
    def test_new_generator_exact_boundaries_and_one_draw_per_slot(self):
        draws = FixedDraws([0, 2, 1, 3, 3, 0])
        self.assertEqual(m.alternating_sequence(6, draws), [10, 10, 1, 1, 1, 10])
        self.assertEqual(draws.bounds, [4]*6)
        for size in (2, True, 3.):
            with self.assertRaises(ValueError):
                m.alternating_sequence(size, FixedDraws([]))

    def test_local_binary_oracle_does_not_use_uniform_ten_class_reference(self):
        result = m.alternating_oracle([{'lengths': [1, 10, 1, 1]}])
        expected = 2 * m.math.log2(1.5) + m.math.log2(.5)
        self.assertEqual(result['transitions'], 3)
        self.assertEqual(result['favorable_position_classes'], 2)
        self.assertAlmostEqual(result['gain_bits'], expected)
        self.assertEqual(result['binary_uniform_loss_bits'], 3.)
        with self.assertRaises(ValueError):
            m.alternating_oracle([{'lengths': [1, 2, 10]}])
        with self.assertRaises(ValueError):
            m.alternating_oracle([])

    def test_streams_are_repeatable_separate_and_old_generator_is_used_verbatim(self):
        _, _, _, generator, _ = m.load_inputs()
        templates = [{'key': 'invented-one', 'page': 'f1r', 'group': 'g', 'label': 'A', 'interior_size': 50},
                     {'key': 'invented-two', 'page': 'f1v', 'group': 'g', 'label': 'B', 'interior_size': 50}]
        first = m.generate(templates, 0, m.NEW_CASE, generator)
        self.assertEqual(first, m.generate(templates, 0, m.NEW_CASE, generator))
        self.assertNotEqual(first, m.generate(templates, 1, m.NEW_CASE, generator))
        self.assertNotEqual(first[0]['lengths'], first[1]['lengths'])
        self.assertEqual([r['label'] for r in first], ['A', 'B'])
        for case in m.CASES[:3]:
            self.assertEqual(m.generate(templates, 0, case, generator), generator.simulate(templates, 0, case))
        with self.assertRaises(ValueError):
            m.generate(templates, 64, m.NEW_CASE, generator)

    def test_layout_binding_reads_metadata_and_keeps_explicit_old_current_identity(self):
        old, pins, identities, _, _ = m.load_inputs()
        self.assertEqual(len(old['layout']['templates']), 2165)
        self.assertEqual(len(old['layout']['group_assignments']), 86)
        self.assertEqual(sum(r['interior_size']-1 for r in old['layout']['templates']), 13713)
        self.assertNotEqual(old['input_pins']['scripts/grouped_length_prediction.py'], identities['scripts/grouped_length_prediction.py'])
        self.assertEqual(pins['scripts/exact_slot_length_prediction.py'], 'f299d79d49555b312651658e71289b77c97f5e2aac9067fa6594bfd1a9e2632f')
        self.assertFalse(any('data/raw/' in name for name in pins))

    def test_old_record_mismatch_precedes_any_new_fine_fit_on_local_invented_rows(self):
        old, _, _, generator, fine = m.load_inputs()
        templates = [{'key': 'fixture-'+str(i), 'page': 'f1r', 'group': 'g'+str(i),
                      'label': 'A', 'interior_size': 3} for i in range(5)]
        assignments = {'g'+str(i): i for i in range(5)}
        rows = generator.simulate(templates, 0, 'independent_uniform')
        evaluated = generator.estimator.evaluate(rows, assignments)
        record = {'replicate': 0, 'sequence_sha256': generator.digest(rows),
                  'oracle': generator.oracle_score(rows, 0), **generator.compact_evaluation(evaluated)}
        fake = SimpleNamespace(evaluate=lambda *args: {'summary': 'fixture', 'folds': [], 'groups': [], 'loci': []})
        result = m.evaluate_dataset(templates, assignments, 0, 'independent_uniform', record, generator, fake)
        self.assertEqual(result['original_control_record_sha256'], m.digest(record))
        changed = copy.deepcopy(record)
        changed['sequence_sha256'] = 'changed'
        with patch.object(fine, 'evaluate') as calculate, self.assertRaisesRegex(ValueError, 'original full coarse'):
            m.evaluate_dataset(templates, assignments, 0, 'independent_uniform', changed, generator, fine)
        calculate.assert_not_called()

    def test_full_evaluation_digest_is_order_independent_but_preserves_every_scalar_type(self):
        self.assertEqual(m.digest({'a': 1, 'b': [2, 3]}), m.digest({'b': [2, 3], 'a': 1}))
        self.assertNotEqual(m.digest({'n': 0}), m.digest({'n': False}))
        self.assertNotEqual(m.digest({'n': 0}), m.digest({'n': 0.0}))
        self.assertNotEqual(m.digest({'scores': [1, 2]}), m.digest({'scores': [2, 1]}))
        full = {'summary': {}, 'folds': [{'fine_fitted_counts': ['keep-in-digest'], 'hash': 'f'}], 'groups': [], 'loci': ['keep-in-digest']}
        compact = m.compact_fine(full)
        self.assertNotIn('fine_fitted_counts', compact['folds'][0])
        self.assertNotIn('loci', compact)
        self.assertEqual(full['loci'], ['keep-in-digest'])

    def test_local_end_to_end_new_process_binds_complete_fine_output(self):
        _, _, _, generator, fine = m.load_inputs()
        templates = [{'key': 'local-'+str(i), 'page': 'f1r', 'group': 'g'+str(i),
                      'label': 'A', 'interior_size': 5} for i in range(5)]
        assignments = {'g'+str(i): i for i in range(5)}
        result = m.evaluate_dataset(templates, assignments, 0, m.NEW_CASE, None, generator, fine)
        rows = m.generate(templates, 0, m.NEW_CASE, generator)
        entire = fine.evaluate(rows, assignments, generator.estimator.evaluate(rows, assignments))
        self.assertEqual(result['complete_fine_evaluation_sha256'], m.digest(entire))
        self.assertEqual(result['summary']['loci'], 5)
        self.assertEqual(result['summary']['transitions'], 20)
        self.assertEqual(len(result['groups']), 5)
        self.assertEqual(len(result['folds']), 5)
        self.assertIsNone(result['original_control_record_sha256'])

    def test_all_replicates_and_unfavorable_contrasts_are_retained(self):
        records = []
        for i in range(64):
            contrasts = {c: {'micro_gain_bits_per_transition': -float(i+1),
                             'group_macro_gain_bits_per_transition': -2.*(i+1),
                             'locus_macro_gain_bits_per_transition': float(i+1),
                             'fixed_diagnostic_preference': False} for c in m.CONTRASTS}
            records.append({'replicate': i, 'summary': {'contrasts': contrasts}, 'oracle': {'gain_bits_per_transition': 0.}})
        summary = m.summaries(records)
        self.assertEqual(summary['primary_fixed_criterion_hits'], 0)
        for c in m.CONTRASTS:
            self.assertEqual(summary['contrasts'][c]['micro_gain_bits_per_transition'], {'mean': -32.5, 'min': -64., 'max': -1.})
            self.assertEqual(summary['contrasts'][c]['positive_equal_group_replicates'], 0)
        for bad in (records[:63], records+[records[0]], list(reversed(records))):
            with self.assertRaises(ValueError):
                m.summaries(bad)

    def test_changed_manifest_or_source_precedes_runtime_api_imports(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            pin = root/m.PINS
            pin.parent.mkdir(parents=True)
            source = root/'fixture.txt'
            source.write_text('changed')
            pin.write_text(json.dumps({'fixture.txt': hashlib.sha256(b'original').hexdigest()}))
            with patch.object(m, 'ROOT', root), patch.object(m, 'PIN_SHA256', hashlib.sha256(pin.read_bytes()).hexdigest()), \
                    patch.object(m, 'module') as imports, self.assertRaisesRegex(ValueError, 'input changed'):
                m.load_inputs()
            imports.assert_not_called()
            with patch.object(m, 'ROOT', root), self.assertRaisesRegex(ValueError, 'manifest changed'):
                m.load_inputs()

    def writer_fixture(self, root):
        source = root/m.PLAN
        source.parent.mkdir(parents=True)
        source.write_text('preserve')
        native = root/'data/native.txt'
        native.parent.mkdir()
        native.write_text('native')
        (root/'data/transliterations.json').write_text(json.dumps({'sources': [{'path': 'data/native.txt'}]}))
        pin = root/m.PINS
        pin.write_text(json.dumps({m.PLAN: hashlib.sha256(source.read_bytes()).hexdigest()}))
        return source, native, pin

    def test_initial_and_late_input_native_aliases_protected_before_exclusive_write(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source, native, pin = self.writer_fixture(root)
            with patch.object(m, 'ROOT', root), patch.object(m, 'PIN_SHA256', hashlib.sha256(pin.read_bytes()).hexdigest()):
                for i, original in enumerate((source, native, pin, Path(m.__file__))):
                    symbolic = root/f'symbolic-{i}'
                    symbolic.symlink_to(original)
                    hard = root/f'hard-{i}'
                    hard.hardlink_to(original)
                    for alias in (original, symbolic, hard):
                        with self.assertRaises(ValueError):
                            m.protect(alias)
                output = root/'new.json'
                def serialize(_, compressed):
                    output.hardlink_to(native)
                    return b'{}'
                with patch.object(m, 'report', return_value={}), patch.object(m, 'serialize', side_effect=serialize), \
                        patch('sys.argv', ['controls', '--new-report', str(output)]), \
                        contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    m.main()
            self.assertEqual(native.read_text(), 'native')

    def test_existing_outputs_fail_before_calculation_and_compression_preserves_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)/'out.json'
            output.write_text('preserve')
            with patch.object(m, 'protect'), patch.object(m, 'report') as calculate, \
                    patch('sys.argv', ['controls', '--new-report', str(output)]), \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                m.main()
            calculate.assert_not_called()
            self.assertEqual(output.read_text(), 'preserve')
        raw = m.serialize({'flag': False, 'n': 0}, False)
        compressed = m.serialize({'flag': False, 'n': 0}, True)
        self.assertEqual(gzip.decompress(compressed), raw)
        self.assertEqual(compressed[4:8], bytes(4))
        self.assertFalse(compressed[3] & 8)


if __name__ == '__main__':
    unittest.main()
