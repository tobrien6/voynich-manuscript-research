from collections import defaultdict
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from fractions import Fraction
import hashlib
import io
import json
import math
from pathlib import Path
import string
import tempfile
import unittest
from unittest.mock import patch

from scripts import grouped_symbol_prediction as g


ABC = ('<EOS>', 'a', 'b')


def row(i, segments=None):
    return {'key': f'f{i + 1}r.1', 'page': f'f{i + 1}r', 'group': f'group{i}',
            'segments': segments if segments is not None else [['a', 'b'], ['a']]}


def synthetic_plan(root):
    original = json.loads((g.ROOT / g.PLAN).read_bytes())
    pins = {}
    for name in sorted(g.PIN_PATHS):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = ('Synthetic fixture: ' + name).encode()
        path.write_bytes(raw)
        pins[name] = hashlib.sha256(raw).hexdigest()
    original['input_pins'] = pins
    (root / g.PLAN).parent.mkdir(parents=True, exist_ok=True)
    (root / g.PLAN).write_bytes(g.encoded(original))
    return original


def image_fixture():
    # An unselected intermediate leaf 3 joins selected leaves 2 and 4.
    canvases = [{'explicit_folio_sides': f'{i}r', 'canvas_uri': f'canvas:{i}'} for i in range(1, 51)]
    canvases += [{'explicit_folio_sides': '2r;3r', 'canvas_uri': 'bridge:23'},
                 {'explicit_folio_sides': '3v;4r', 'canvas_uri': 'bridge:34'}]
    components = g.dependency_components(canvases)
    groups = {leaf: c['group_id'] for c in components for leaf in c['folio_ids']}
    leaf_canvases = defaultdict(set)
    for canvas in canvases:
        for side in canvas['explicit_folio_sides'].split(';'):
            leaf_canvases[side[:-1]].add(canvas['canvas_uri'])
    image = {'dependency_components': components,
             'indexed_canvas_ids_by_leaf': {k: sorted(v) for k, v in leaf_canvases.items()},
             'pages': [{'page_id': f'f{i}r', 'side_reference_status': 'side_references_matched',
                        'dependency_group': groups[str(i)]} for i in range(1, 51)]}
    rows = [{'key': f'f{i}r.1', 'page': f'f{i}r'} for i in range(1, 51) if i != 3]
    return rows, image, canvases


class GroupedSymbolTests(unittest.TestCase):
    def test_hand_computed_probabilities_and_complete_token_losses(self):
        model = g.fit([row(0)], ABC)
        q0, q1, q2 = g.probabilities(model, g.BOS, 'a', 'b')
        self.assertAlmostEqual(q0, float(Fraction(3, 13)))
        self.assertAlmostEqual(q1, float(Fraction(61, 234)))
        self.assertAlmostEqual(q2, float(Fraction(605, 2106)))
        score = g.score_row(row(1, [['a', 'b']]), model, 0, {})
        expected = [(Fraction(5, 13), Fraction(3, 13), Fraction(5, 13)),
                    (Fraction(53, 117), Fraction(61, 234), Fraction(93, 221)),
                    (Fraction(541, 1053), Fraction(605, 2106), Fraction(1709, 3757))]
        for actual, values in zip(score['loss_bits_order0_order1_order2'], expected):
            self.assertAlmostEqual(actual, -math.fsum(math.log2(float(v)) for v in values))
        self.assertEqual((score['tokens'], score['units'], score['targets']), (1, 2, 3))

    def test_normalized_distributions_and_exact_unseen_context_backoff(self):
        model = g.fit([row(0)], ABC)
        for w, x in [(g.BOS, g.BOS), (g.BOS, 'a'), ('a', 'b'), ('unseen', 'a'), ('unseen', 'unseen')]:
            distributions = [g.probabilities(model, w, x, y) for y in ABC]
            for order in range(3):
                self.assertAlmostEqual(math.fsum(p[order] for p in distributions), 1)
                self.assertTrue(all(0 < p[order] < 1 for p in distributions))
        for y in ABC:
            q0, q1, q2 = g.probabilities(model, 'unseen', 'unseen', y)
            self.assertEqual(q0, q1)
            self.assertEqual(q1, q2)
            _, q1, q2 = g.probabilities(model, 'unseen', 'a', y)
            self.assertEqual(q1, q2)

    def test_every_token_resets_two_bos_and_has_exactly_one_eos(self):
        self.assertEqual(list(g.events(['a'])), [(g.BOS, g.BOS, 'a'), (g.BOS, 'a', g.EOS)])
        model = g.fit([row(0, [['a'], ['b']])], ABC)
        self.assertEqual(model['total'], 4)
        self.assertEqual(model['targets'][g.EOS], 2)
        self.assertEqual(model['first'][g.BOS], {'a': 1, 'b': 1})
        self.assertNotIn(g.EOS, model['first'])
        self.assertNotIn(('a', 'b'), model['second'])
        self.assertEqual(sum(model['first_totals'].values()), model['total'])
        self.assertEqual(sum(model['second_totals'].values()), model['total'])

    def test_fixed_alphabet_keeps_unseen_case_and_pattern_mass(self):
        alphabet = g.alphabet_for(['ch', 'iin'])
        self.assertEqual(set(alphabet), set(string.ascii_letters) | {'ch', 'iin', g.EOS})
        self.assertNotIn(g.BOS, alphabet)
        model = g.fit([row(0, [['a']])], alphabet)
        self.assertGreater(g.probabilities(model, g.BOS, g.BOS, 'ch')[0], 0)
        self.assertGreater(g.probabilities(model, g.BOS, g.BOS, 'A')[0], 0)
        for segments in [[], [[]], [[g.EOS]], [[g.BOS]], [['unknown']]]:
            with self.subTest(segments=segments), self.assertRaises(ValueError):
                g.fit([row(0, segments)], alphabet)
        with self.assertRaises(ValueError):
            g.fit([row(0)], ABC + ('a',))

    def test_count_serialization_is_order_independent(self):
        rows = [row(0), row(1, [['b'], ['b', 'a']])]
        before = deepcopy(rows)
        self.assertEqual(g.model_record(g.fit(rows, ABC)), g.model_record(g.fit(rows[::-1], ABC)))
        self.assertEqual(rows, before)

    def test_unequal_denominators_and_fixed_criterion_keep_sign_reversals(self):
        model = g.fit([row(0)], ABC)
        scores = [g.score_row(row(1, [['a']]), model, 0, {}),
                  g.score_row(row(2, [['a', 'b']] * 3), model, 1, {})]
        scores[0]['loss_bits_order0_order1_order2'] = [6, 4, 2]
        scores[1]['loss_bits_order0_order1_order2'] = [27, 18, 19]
        for score in scores:
            a, b, c = score['loss_bits_order0_order1_order2']
            score['gain01_bits_per_target'] = (a - b) / score['targets']
            score['gain12_bits_per_target'] = (b - c) / score['targets']
        summary = g.aggregate(scores)
        self.assertEqual(summary['targets'], 11)
        self.assertAlmostEqual(summary['pooled_gain12_bits_per_target'], 1 / 11)
        self.assertAlmostEqual(summary['locus_macro_gain12_bits_per_target'], (1 - 1 / 9) / 2)
        self.assertNotEqual(summary['pooled_gain12_bits_per_target'], summary['locus_macro_gain12_bits_per_target'])
        self.assertTrue(g.second_order_preference(0.02, 0.001, [0.001] * 5))
        for pooled, group, folds in [(0.0199, 0.1, [1] * 5), (0.1, 0, [1] * 5),
                                     (0.1, 0.1, [1, 1, 1, 1, 0]), (0.1, 0.1, [1, 1, 1, 1, -0.1])]:
            self.assertFalse(g.second_order_preference(pooled, group, folds))
        with self.assertRaises(ValueError):
            g.second_order_preference(1, 1, [1] * 4)

    def test_group_excluded_fit_coverage_and_scoring_perturbation(self):
        rows = [row(i) for i in range(5)]
        assignments = {f'group{i}': i for i in range(5)}
        result = g.evaluate(rows, assignments, ABC)
        changed = deepcopy(rows)
        changed[2]['segments'] = [['b'] * 14]
        altered = g.evaluate(changed, assignments, ABC)
        self.assertEqual(result['folds'][2]['fitted_counts_sha256'], altered['folds'][2]['fitted_counts_sha256'])
        self.assertNotEqual(result['folds'][2]['loss_bits_order0_order1_order2'],
                            altered['folds'][2]['loss_bits_order0_order1_order2'])
        self.assertNotEqual(result['folds'][0]['fitted_counts_sha256'], altered['folds'][0]['fitted_counts_sha256'])
        self.assertEqual(result['summary']['targets'], 25)
        self.assertEqual(len(result['loci']), 5)
        for fold in result['folds']:
            self.assertEqual(fold['training_targets'], 20)
            self.assertFalse(set(fold['training_group_ids']) & set(fold['scoring_group_ids']))
            self.assertEqual(sum(n for _, n in fold['training_target_counts']), 20)
        for score in result['loci']:
            self.assertEqual(score['fold'], assignments[score['group_id']])
        for bad in [dict(assignments, group0=True), {**assignments, 'extra': 2}, dict(assignments, group4=3)]:
            with self.assertRaises(ValueError):
                g.evaluate(rows, bad, ABC)
        with self.assertRaises(ValueError):
            g.evaluate(rows + [rows[0]], assignments, ABC)

    def test_full_transitive_component_and_unselected_leaf_stay_together(self):
        rows, image, canvases = image_fixture()
        assignments, manifest, pages = g.declare_folds(rows, image, canvases)
        self.assertEqual(pages['f2r'], pages['f4r'])
        joined = next(m for m in manifest if m['group_id'] == pages['f2r'])
        self.assertEqual(joined['folio_ids'], ['2', '3', '4'])
        self.assertIn('canvas:3', joined['canvas_ids'])
        self.assertIn('bridge:34', joined['canvas_ids'])
        self.assertNotIn('f3r.1', joined['locus_keys'])
        self.assertEqual(sum(len(m['locus_keys']) for m in manifest), len(rows))
        self.assertEqual(set(assignments.values()), set(range(5)))
        with self.assertRaisesRegex(ValueError, 'empty declared fold'):
            g.declare_folds(rows[:1], image, canvases)
        for group, fold in assignments.items():
            raw = json.dumps([g.METHOD, 20261012, group], ensure_ascii=False, separators=(',', ':')).encode()
            self.assertEqual(fold, int.from_bytes(hashlib.sha256(raw).digest(), 'big') % 5)
        for mode in ['unsupported', 'missing_side', 'bad_report']:
            bad_rows, bad_image, bad_canvases = deepcopy(rows), deepcopy(image), deepcopy(canvases)
            if mode == 'unsupported':
                bad_rows[0]['page'] = 'f117x'
            elif mode == 'missing_side':
                bad_rows[0]['page'] = 'f1v'
            else:
                bad_image['dependency_components'][0]['folio_ids'] = ['99']
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                g.declare_folds(bad_rows, bad_image, bad_canvases)

    def test_fixed_pins_and_typed_plan_reject_drift(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            plan = synthetic_plan(root)
            self.assertEqual(g.load_plan(root), plan)
            for field, changed in [('folds', True), ('root_pseudocount', 1), ('context_prior_strength', 16.0)]:
                bad = deepcopy(plan); bad[field] = changed
                (root / g.PLAN).write_bytes(g.encoded(bad))
                with self.assertRaisesRegex(ValueError, 'review changed plan'):
                    g.load_plan(root)
            (root / g.PLAN).write_bytes(g.encoded(plan))
            (root / next(iter(plan['input_pins']))).write_bytes(b'changed synthetic input')
            with self.assertRaisesRegex(ValueError, 'pinned input changed'):
                g.load_plan(root)
        for raw in [b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":{"z":1,"z":1}}']:
            with self.assertRaises(ValueError):
                g.strict_json(raw)

    def test_tampered_parent_receipt_stops_before_model_fitting(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / g.PARENT
            path.parent.mkdir(parents=True)
            path.write_bytes(g.encoded({'frequency': 2}))
            with patch.object(g, 'load_plan', return_value={}), \
                    patch.object(g.parent, 'make_report', return_value={'frequency': 1}), \
                    patch.object(g, 'evaluate') as fitter, \
                    self.assertRaisesRegex(ValueError, 'complete paired entropy receipt'):
                g.make_report(root)
            fitter.assert_not_called()

    def test_cli_exclusive_output_handles_late_aliases_and_exact_replay_types(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root / 'source'; source.write_bytes(b'synthetic input\n')
            output = root / 'new'
            with patch.object(g, 'make_report', return_value={'schema_version': 1}), \
                    patch('sys.argv', ['predict', '--output', str(output)]), redirect_stdout(io.StringIO()):
                g.main()
            self.assertEqual(output.read_bytes(), g.encoded({'schema_version': 1}))
            for raw in [g.encoded({'schema_version': True}), b'{"schema_version":1,"schema_version":1}']:
                output.write_bytes(raw)
                with patch.object(g, 'make_report', return_value={'schema_version': 1}), \
                        patch('sys.argv', ['predict', '--check', str(output)]), redirect_stderr(io.StringIO()), \
                        self.assertRaises(SystemExit):
                    g.main()
            for kind in ('symlink', 'hardlink'):
                destination = root / kind
                def late(_root):
                    if kind == 'symlink': destination.symlink_to(source)
                    else: destination.hardlink_to(source)
                    return {'schema_version': 1}
                with patch.object(g, 'make_report', side_effect=late), \
                        patch('sys.argv', ['predict', '--output', str(destination)]), redirect_stderr(io.StringIO()), \
                        self.assertRaises(SystemExit):
                    g.main()
                self.assertEqual(destination.read_bytes(), source.read_bytes())
                self.assertEqual(source.read_bytes(), b'synthetic input\n')


if __name__ == '__main__':
    unittest.main()
