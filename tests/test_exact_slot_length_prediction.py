import contextlib
import copy
from fractions import Fraction
import gzip
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import exact_slot_length_prediction as m


def row(key, lengths, group='g', label='A', page='f1r'):
    return {'key': key, 'lengths': lengths, 'group': group, 'label': label, 'page': page}


class ExactSlotTests(unittest.TestCase):
    def fixture(self):
        rows = [row('r'+str(i), [1, 2, 1, 2], 'g'+str(i)) for i in range(5)]
        rows.append(row('extra', [2, 1, 2, 1], 'g0', page='f1v'))
        return rows, {'g'+str(i): i for i in range(5)}

    def test_exact_features_and_classes_preserve_original_target_slots(self):
        self.assertEqual(m.events(row('r', [1, 2, 3, 10, 50])),
                         [(('A', 5, 1), 1, 2), (('A', 5, 2), 2, 3),
                          (('A', 5, 3), 3, 10), (('A', 5, 4), 10, 10)])
        for bad in ([1, 2], [1, True, 2], [1, 0, 2]):
            with self.assertRaises(ValueError):
                m.events(row('bad', bad))

    def test_hand_probabilities_and_matched_training_frequency_mixture(self):
        model = m.fit([row('a', [1, 2, 1, 2]), row('b', [2, 3, 1, 2])])
        context = ('A', 4, 1)
        self.assertEqual(m.probabilities(model, context, 1, 2), (Fraction(2, 9), Fraction(11, 36)))
        self.assertEqual(m.probabilities(model, context, 2, 2), (Fraction(2, 9), Fraction(5, 36)))
        for c in model['targets']:
            n = sum(model['targets'][c].values())
            for y in range(1, 11):
                mixture = sum((Fraction(sum(model['pairs'].get((c, x), {}).values()), n)
                               * m.probabilities(model, c, x, y)[1] for x in range(1, 11)), Fraction())
                self.assertEqual(mixture, m.probabilities(model, c, 1, y)[0])
            for x in range(1, 11):
                pairs = [m.probabilities(model, c, x, y) for y in range(1, 11)]
                self.assertEqual(sum(p[0] for p in pairs), 1)
                self.assertEqual(sum(p[1] for p in pairs), 1)
                self.assertTrue(all(p[0] > 0 and p[1] > 0 for p in pairs))

    def test_constant_previous_variable_target_has_exactly_zero_feature_gain(self):
        model = m.fit([row('a', [1, 2, 1, 2]), row('b', [1, 3, 2, 2])])
        for x in range(1, 11):
            for y in range(1, 11):
                f0, f1 = m.probabilities(model, ('A', 4, 1), x, y)
                self.assertEqual(f0, f1)
        self.assertNotEqual(m.probabilities(model, ('A', 4, 1), 1, 2)[0], Fraction(1, 10))

    def test_unseen_previous_and_slot_backoff_preserve_coarse_prior(self):
        model = m.fit([row('a', [1, 2, 1, 2]), row('b', [2, 3, 1, 2])])
        self.assertEqual(m.probabilities(model, ('A', 4, 1), 10, 2), (Fraction(2, 9), Fraction(2, 9)))
        self.assertEqual(m.probabilities(model, ('A', 7, 5), 1, 2), (Fraction(3, 14), Fraction(3, 14)))
        self.assertEqual(m.probabilities(model, ('unseen', 7, 5), 1, 2), (Fraction(1, 10), Fraction(1, 10)))
        scored = m.score_row(row('new', [1]*7, label='unseen'), model, 0)
        support = m.aggregate([scored])['support']
        self.assertEqual(support['unseen_fine_context'], 6)
        self.assertEqual(support['unseen_coarse_context'], 6)
        self.assertEqual(support['seen_fine_unseen_previous'], 0)

    def test_invalid_context_class_and_training_identity_guards(self):
        model = m.fit([row('a', [1, 2, 3])])
        for c, x, y in ((('A', 2, 1), 1, 2), (('A', 3, 0), 1, 2),
                        (('A', 3, 3), 1, 2), ((True, 3, 1), 1, 2),
                        (('A', 3, 1), True, 2), (('A', 3, 1), 1, 11)):
            with self.assertRaises(ValueError):
                m.probabilities(model, c, x, y)
        with self.assertRaises(ValueError):
            m.fit([])
        with self.assertRaises(ValueError):
            m.fit([row('a', [1, 2, 3]), row('a', [2, 3, 4])])

    def test_each_original_locus_transition_loss_and_group_declaration_reproduces(self):
        rows, assignments = self.fixture()
        old = m.coarse.evaluate(rows, assignments)
        result = m.evaluate(rows, assignments, old)
        self.assertEqual(result['summary']['transitions'], old['summary']['transitions'])
        self.assertEqual(result['summary']['loci'], len(rows))
        self.assertEqual(sum(f['transitions'] for f in result['folds']), result['summary']['transitions'])
        for fold, previous in zip(result['folds'], old['folds']):
            self.assertEqual(fold['coarse_fitted_counts_sha256'], previous['fitted_counts_sha256'])
            self.assertFalse(set(fold['training_group_ids']) & set(fold['scoring_group_ids']))
        for saved, previous in zip(result['loci'], old['loci']):
            self.assertEqual(saved['loss_bits']['Q0'], previous['baseline_loss_bits'])
            self.assertEqual(saved['loss_bits']['Q1'], previous['transition_loss_bits'])
            self.assertEqual(len(saved['transition_receipts']), saved['transitions'])
        for tag, values in result['summary']['contrasts'].items():
            a, b = m.CONTRASTS[tag]
            self.assertEqual(values['micro_gain_bits_per_transition'],
                (result['summary']['loss_bits'][b] - result['summary']['loss_bits'][a]) / result['summary']['transitions'])
            if tag != 'previous_at_exact_slot':
                self.assertIsNone(values['fixed_diagnostic_preference'])

    def test_excluded_fold_values_labels_and_sizes_cannot_change_its_fit(self):
        rows, assignments = self.fixture()
        before = m.evaluate(rows, assignments, m.coarse.evaluate(rows, assignments))
        changed = copy.deepcopy(rows)
        for r in changed:
            if assignments[r['group']] == 0:
                r['lengths'] = [10, 2, 4, 5, 6]
                r['label'] = 'B'
        after = m.evaluate(changed, assignments, m.coarse.evaluate(changed, assignments))
        for key in ('fine_fitted_counts', 'fine_fitted_counts_sha256', 'coarse_fitted_counts_sha256'):
            self.assertEqual(before['folds'][0][key], after['folds'][0][key])
        self.assertNotEqual(before['folds'][1]['fine_fitted_counts_sha256'], after['folds'][1]['fine_fitted_counts_sha256'])

    def test_old_parent_drift_or_invalid_folds_precedes_new_fitting(self):
        rows, assignments = self.fixture()
        old = m.coarse.evaluate(rows, assignments)
        old['summary']['groups'] = 0
        with patch.object(m, 'fit') as fitter, self.assertRaisesRegex(ValueError, 'original coarse'):
            m.evaluate(rows, assignments, old)
        fitter.assert_not_called()
        for invalid in (rows + [rows[0]], rows[:1]):
            with self.assertRaises(ValueError):
                m.evaluate(invalid, assignments, {})

    def test_model_marginal_corruption_and_constant_feature_primary_zero(self):
        model = m.fit([row('a', [1, 2, 1, 2]), row('b', [2, 3, 1, 2])])
        changed = copy.deepcopy(model)
        changed['targets'][('A', 4, 1)][2] += 1
        with self.assertRaises(ValueError):
            m.validate_model(changed)
        changed = copy.deepcopy(model)
        changed['targets'][('A', 4, 1)] = {2: 2, 3: 0}
        with self.assertRaisesRegex(ValueError, 'mixture'):
            m.validate_model(changed)
        rows = [row('r'+str(i), [1, 2, 1, 2], 'g'+str(i)) for i in range(5)]
        assignments = {'g'+str(i): i for i in range(5)}
        result = m.evaluate(rows, assignments, m.coarse.evaluate(rows, assignments))
        primary = result['summary']['contrasts']['previous_at_exact_slot']
        self.assertEqual(primary['micro_gain_bits_per_transition'], 0)
        self.assertEqual(primary['group_macro_gain_bits_per_transition'], 0)
        self.assertEqual(primary['positive_fold_count'], 0)
        self.assertFalse(primary['fixed_diagnostic_preference'])

    def test_partial_treatment_family_is_refused_before_new_fit(self):
        variants = [(s, p) for s in ('ZL3b', 'IT2a') for p in ('split', 'join')]
        previous = {'treatments': [{'source_id': s, 'spacing': p} for s, p in variants]}
        prepared = [(s, p, [], '') for s, p in variants]
        for partial_rows, partial_previous in ((prepared[:3], previous),
                                               (prepared, {'treatments': previous['treatments'][:3]})):
            with patch.object(m, 'inputs', return_value=(partial_previous, {})), \
                    patch.object(m.coarse, 'inputs', return_value=(partial_rows, {}, [], {}, {})), \
                    patch.object(m, 'evaluate') as calculate, self.assertRaisesRegex(ValueError, 'four-treatment'):
                m.report()
            calculate.assert_not_called()

    def test_changed_manifest_or_input_blocks_native_preparation(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            p = root/m.PINS
            p.parent.mkdir(parents=True)
            source = root/'fixture.txt'
            source.write_text('changed')
            p.write_text(json.dumps({'fixture.txt': hashlib.sha256(b'original').hexdigest()}))
            with patch.object(m, 'ROOT', root), patch.object(m, 'PIN_SHA256', hashlib.sha256(p.read_bytes()).hexdigest()), \
                    patch.object(m.coarse, 'inputs') as prepare, self.assertRaisesRegex(ValueError, 'input changed'):
                m.report()
            prepare.assert_not_called()
            with patch.object(m, 'ROOT', root), self.assertRaisesRegex(ValueError, 'manifest changed'):
                m.inputs()

    def writer_fixture(self, root):
        plan = root/m.PLAN
        plan.parent.mkdir(parents=True)
        plan.write_text('preserve')
        native = root/'data/native.txt'
        native.parent.mkdir()
        native.write_text('native fixture')
        catalog = root/'data/transliterations.json'
        catalog.write_text(json.dumps({'sources': [{'path': 'data/native.txt'}]}))
        pin = root/m.PINS
        pin.write_text(json.dumps({m.PLAN: hashlib.sha256(plan.read_bytes()).hexdigest(),
                                  'data/transliterations.json': hashlib.sha256(catalog.read_bytes()).hexdigest()}))
        return plan, native, catalog, pin

    def test_all_initial_source_plan_catalog_manifest_code_aliases_are_protected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            inputs = self.writer_fixture(root)
            with patch.object(m, 'ROOT', root), patch.object(m, 'PIN_SHA256', hashlib.sha256(inputs[-1].read_bytes()).hexdigest()):
                for i, original in enumerate((*inputs, Path(m.__file__))):
                    symbolic = root/f'symbolic-{i}'
                    symbolic.symlink_to(original)
                    hard = root/f'hard-{i}'
                    hard.hardlink_to(original)
                    for path in (original, symbolic, hard):
                        with self.assertRaises(ValueError):
                            m.protect(path)
                redirect = root/'redirect'
                redirect.symlink_to(inputs[0].parent, target_is_directory=True)
                with self.assertRaises(ValueError):
                    m.protect(redirect/inputs[0].name)
                m.protect(root/'new.json')

    def test_existing_output_precedes_calculation_and_late_alias_preserves_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            plan, native, catalog, pin = self.writer_fixture(root)
            output = root/'output.json.gz'
            output.write_text('preserve')
            with patch.object(m, 'ROOT', root), patch.object(m, 'PIN_SHA256', hashlib.sha256(pin.read_bytes()).hexdigest()), \
                    patch.object(m, 'report') as calculate, patch('sys.argv', ['slot', '--new-report', str(output)]), \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                m.main()
            calculate.assert_not_called()
            output.unlink()
            def serialize(_, compressed):
                output.hardlink_to(native)
                return b'{}'
            with patch.object(m, 'ROOT', root), patch.object(m, 'PIN_SHA256', hashlib.sha256(pin.read_bytes()).hexdigest()), \
                    patch.object(m, 'report', return_value={}), patch.object(m, 'serialize', side_effect=serialize), \
                    patch('sys.argv', ['slot', '--new-report', str(output)]), \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                m.main()
            self.assertEqual(native.read_text(), 'native fixture')

    def test_exact_byte_cache_and_lossless_compression_preserve_scalar_types(self):
        raw = m.serialize({'count': 0, 'flag': False}, False)
        zipped = m.serialize({'count': 0, 'flag': False}, True)
        self.assertEqual(gzip.decompress(zipped), raw)
        self.assertEqual(zipped[4:8], bytes(4))
        self.assertFalse(zipped[3] & 8)
        self.assertFalse(m.same({'count': 0}, {'count': False}))
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)/'report.json'
            output.write_bytes(m.serialize({'count': False}, False))
            with patch.object(m, 'protect'), patch.object(m, 'report', return_value={'count': 0}), \
                    patch('sys.argv', ['slot', '--check', str(output)]), \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                m.main()


if __name__ == '__main__':
    unittest.main()
