"""Synthetic accounting and writer-boundary tests; no manuscript observations."""

import contextlib
import copy
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import y_prefix_form_accounting as module


def fraction(item):
    return Fraction(item['numerator'], item['denominator'])


def protection_fixture(root):
    names = {'producer': 'scripts/parent.py', 'report': 'parent.json', 'partition': 'partition.json',
             'parent_plan': 'PLAN.md', 'accounting_plan': 'ACCOUNTING_PLAN.md'}
    (root / 'scripts').mkdir()
    (root / 'data/raw').mkdir(parents=True)
    (root / 'research/image-index').mkdir(parents=True)
    raw = root / 'data/raw/source.txt'
    raw.write_bytes(b'synthetic pinned source')
    catalog = root / 'data/transliterations.json'
    catalog.write_text(json.dumps({'sources': [{'path': 'data/raw/source.txt'}]}))
    for path in names.values():
        (root / path).write_bytes(b'synthetic pinned artifact')
    (root / names['report']).write_text(json.dumps({'input_pins': {
        'catalog': {'path': 'data/transliterations.json'},
        'image': {'path': 'research/image-index/audit.json'}}}))
    (root / 'research/image-index/audit.json').write_bytes(b'synthetic index')
    helper = root / 'scripts/helper.py'
    helper.write_bytes(b'synthetic helper')
    manifest = {'parent_files': {key: {'path': path, 'sha256': module.sha((root / path).read_bytes())}
                                for key, path in names.items()},
                'helper_files': [{'path': 'scripts/helper.py', 'sha256': module.sha(helper.read_bytes())}]}
    (root / module.INPUTS).parent.mkdir(parents=True, exist_ok=True)
    (root / module.INPUTS).write_text(json.dumps(manifest))
    return manifest, [root / name for name in names.values()] + [raw, catalog, helper,
        root / 'research/image-index/audit.json', root / module.INPUTS]


class FormAccountingTests(unittest.TestCase):
    def test_all_four_lookup_cells_and_one_letter_strip(self):
        vocabulary = {'a', 'yb', 'yc', 'c', 'y'}
        self.assertEqual(module.score('ya', vocabulary), (False, True, 1))
        self.assertEqual(module.score('yb', vocabulary), (True, False, -1))
        self.assertEqual(module.score('yc', vocabulary), (True, True, 0))
        self.assertEqual(module.score('yd', vocabulary), (False, False, 0))
        self.assertEqual(module.score('yy', vocabulary), (False, True, 1))

    def test_exact_unit_weights_are_not_pooled_token_weights(self):
        cases = {'u1': (['ya', 'ya', 'yb'], ['yb', 'yc']),
                 'u2': (['yd'], ['ya', 'yc', 'yc', 'yd'])}
        result = module.account_forms(cases, {'a', 'yb', 'c', 'yc'}, ['u1', 'u2'])
        self.assertEqual(fraction(result['exact_first_gain']), Fraction(1, 6))
        self.assertEqual(fraction(result['exact_other_gain']), Fraction(-1, 8))
        self.assertEqual(fraction(result['exact_selective_gain']), Fraction(7, 24))
        self.assertEqual(result['pooled_first_cells']['mean_match_gain'], 0.25)
        self.assertEqual(result['pooled_other_cells']['mean_match_gain'], 0)
        terms = {term['form']: term for term in result['forms']}
        self.assertEqual(fraction(terms['ya']['selectivity_contribution']), Fraction(5, 24))
        # A negative lookup score can contribute positively when its other-slot
        # weight exceeds its first-slot weight; terms are not causal effects.
        self.assertEqual(fraction(terms['yb']['selectivity_contribution']), Fraction(1, 12))
        self.assertEqual(fraction(terms['yc']['selectivity_contribution']), 0)
        self.assertEqual(fraction(terms['yd']['selectivity_contribution']), 0)
        self.assertEqual(sum(fraction(term['frequency_difference']) for term in result['forms']), 0)

    def test_same_forms_can_have_nonzero_unmatched_composition_contrast(self):
        result = module.account_forms({'u': (['ya', 'ya', 'yb'], ['ya', 'yb', 'yb'])},
                                      {'a', 'yb'}, ['u'])
        self.assertEqual(fraction(result['exact_selective_gain']), Fraction(2, 3))
        self.assertTrue(all(term['pooled_first_occurrences'] and term['pooled_other_occurrences']
                            for term in result['forms']))

    def test_exact_form_matching_at_equal_weights_is_zero_by_construction(self):
        cases = {'u1': (['ya', 'yb', 'yc'], ['yc', 'ya', 'yb']),
                 'u2': (['yd', 'ya', 'ya'], ['ya', 'yd', 'ya'])}
        result = module.account_forms(cases, {'a', 'yb', 'yc', 'c'}, ['u1', 'u2'])
        self.assertEqual(fraction(result['exact_selective_gain']), 0)
        self.assertTrue(all(fraction(term['selectivity_contribution']) == 0 for term in result['forms']))

    def test_case_is_literal_and_neutral_forms_are_retained(self):
        result = module.account_forms({'u': (['yA'], ['ya'])}, {'a'}, ['u'])
        self.assertEqual([term['form'] for term in result['forms']], ['yA', 'ya'])
        self.assertEqual(fraction(result['exact_selective_gain']), -1)
        self.assertEqual(result['forms'][0]['lookup_gain'], 0)

    def test_missing_classes_and_noncommon_units_remain_in_ledger(self):
        result = module.account_forms({'u': (['ya'], ['yb']), 'missing': ([], ['yc'])},
                                      {'a', 'yb'}, ['u'])
        self.assertEqual(result['common_unit_count'], 1)
        ledger = {item['unit_id']: item for item in result['all_diagnostic_unit_frequencies']}
        self.assertEqual(ledger['missing']['missing_classes_in_this_variant'], ['first'])
        self.assertFalse(ledger['missing']['included_in_common_summary'])
        self.assertEqual(ledger['missing']['first_slot']['candidate_tokens'], 0)
        self.assertNotIn('yc', [term['form'] for term in result['forms']])

    def test_invalid_or_empty_classes_do_not_produce_a_valid_account(self):
        for cases, common in [({}, []), ({'u': ([], ['ya'])}, ['u']),
                              ({'u': (['ya'], ['yb'])}, ['u', 'u']),
                              ({'u': (['ya'], ['yb'])}, ['missing']),
                              ({'u': (['ya'], ['yb'])}, 'u')]:
            with self.subTest(cases=cases, common=common), self.assertRaises(ValueError):
                module.account_forms(cases, {'a'}, common)
        for value in ['Yaa', 'y', 'y?', 'yé', 1]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                module.score(value, {'a'})

    def test_parent_variant_vocabulary_cells_and_identity_drift_fail(self):
        cases = {'u': (['ya', 'yb'], ['yc', 'yd'])}
        vocabulary = {'a', 'yb', 'yc', 'c'}
        metadata = {'source_id': 'fixture', 'source_sha256': 'a' * 64}
        expected = {**metadata, 'vocabulary': {'distinct_strings': 4,
            'development_internal_tokens': 42, 'sorted_strings_sha256': module.parent.key_digest(vocabulary)},
            'evaluation_units': [{'unit_id': 'u',
                'first_slot': {'candidate_tokens': 2, 'original_matches': 1, 'stripped_matches': 1,
                    'both_match': 0, 'neither_matches': 0, 'original_only': 1, 'stripped_only': 1, 'mean_match_gain': 0.0},
                'other_slots': {'candidate_tokens': 2, 'original_matches': 1, 'stripped_matches': 1,
                    'both_match': 1, 'neither_matches': 1, 'original_only': 0, 'stripped_only': 0, 'mean_match_gain': 0.0}}],
            'excluded_evaluation_units_missing_candidate_class': []}
        self.assertEqual(module.verify_variant(metadata, cases, vocabulary, 42, expected), {'u'})
        for field in ['source_sha256', 'vocabulary', 'evaluation_units', 'excluded_evaluation_units_missing_candidate_class']:
            changed = copy.deepcopy(expected)
            if field == 'source_sha256':
                changed[field] = 'b' * 64
            elif field == 'vocabulary':
                changed[field]['distinct_strings'] += 1
            elif field == 'evaluation_units':
                changed[field][0]['first_slot']['candidate_tokens'] += 1
            else:
                changed[field] = ['u']
            with self.subTest(field=field), self.assertRaises(ValueError):
                module.verify_variant(metadata, cases, vocabulary, 42, changed)

    def test_collection_keeps_true_first_and_final_slots_and_development_only_vocabulary(self):
        loci = [SimpleNamespace(key='f1r.1', page='f1r'),
                *(SimpleNamespace(key=f'f2r.{i}', page='f2r') for i in range(1, 4))]
        token = lambda value: SimpleNamespace(value=value)
        slots = [[token('yd'), token('a'), token('yc'), token('c'), token('yb')],
                 [token('ya'), token('yc')], [token('x'), None, token('yb')],
                 [None, token('ya'), token('yc')]]
        rows = list(zip(loci, slots))
        selected = {locus.key for locus in loci}
        common = selected - {'f2r.3'}
        sources = [({'id': sid, 'sha256': 'a' * 64}, object()) for sid in ['ZL3b', 'IT2a']]
        partition = {'units': [{'unit_id': 'd', 'partition': 'dictionary_development', 'selected_source_pages': ['f1r']},
                              {'unit_id': 'e', 'partition': 'diagnostic_evaluation', 'selected_source_pages': ['f2r']}]}
        vocabulary = {'a', 'yc', 'c', 'yb'}
        variants = []
        for sid in ['ZL3b', 'IT2a']:
            for spacing in ['split', 'join']:
                for alternative in ['exclude', 'first']:
                    variants.append({'source_id': sid, 'source_sha256': 'a' * 64,
                        'uncertain_spaces': spacing, 'alternatives': alternative, 'own_eligible_locus_count': 3,
                        'excluded_from_common_locus_cohort': ['f2r.3'],
                        'vocabulary': {'distinct_strings': 4, 'development_internal_tokens': 4,
                                       'sorted_strings_sha256': module.parent.key_digest(vocabulary)},
                        'evaluation_units': [{'unit_id': 'e',
                            'first_slot': {'candidate_tokens': 1, 'original_matches': 0, 'stripped_matches': 1,
                                'both_match': 0, 'neither_matches': 0, 'original_only': 0, 'stripped_only': 1, 'mean_match_gain': 1.0},
                            'other_slots': {'candidate_tokens': 2, 'original_matches': 2, 'stripped_matches': 1,
                                'both_match': 1, 'neither_matches': 0, 'original_only': 1, 'stripped_only': 0, 'mean_match_gain': -0.5}}],
                        'excluded_evaluation_units_missing_candidate_class': []})
        expected = {'selection': {'selected_locations': 4, 'common_eligible_locations': 3,
            'sorted_common_eligible_keys_sha256': module.parent.key_digest(common),
            'diagnostic_evaluation_unit_count': 1, 'common_evaluation_unit_ids': ['e'],
            'common_evaluation_unit_count': 1}, 'variants': variants}
        with patch.object(module.parent, 'selection', return_value=(sources, selected, {})), \
                patch.object(module.parent, 'selected_records', return_value=loci), \
                patch.object(module.parent, 'prepare_rows', return_value=rows):
            captured, units = module.collect_variants(sources, partition, expected)
            self.assertEqual(units, ['e'])
            self.assertEqual(len(captured), 8)
            for _, cases, fitted, _ in captured:
                self.assertEqual(cases['e'], [['ya'], ['yc', 'yb']])
                self.assertEqual(fitted, vocabulary)
                self.assertNotIn('yd', fitted)  # Development first position.
                self.assertNotIn('ya', fitted)  # Evaluation-only representation.
            changed = copy.deepcopy(expected)
            changed['selection']['sorted_common_eligible_keys_sha256'] = '0' * 64
            with self.assertRaisesRegex(ValueError, 'common locus cohort changed'):
                module.collect_variants(sources, partition, changed)

    def test_pinned_input_or_helper_drift_fails_before_parent_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, inputs = protection_fixture(root)
            module.validate_pins(manifest, root)
            (root / 'scripts/helper.py').write_bytes(b'changed helper')
            with patch.object(module.parent, 'prepare_partition') as prepare, self.assertRaisesRegex(ValueError, 'helper changed'):
                module.load_parent(manifest, root)
            prepare.assert_not_called()


class OutputProtectionTests(unittest.TestCase):
    def test_direct_symlink_hardlink_and_check_report_aliases_preserve_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, inputs = protection_fixture(root)
            check = root / 'check.json'
            check.write_bytes(b'synthetic check report')
            inputs.append(check)
            for index, source in enumerate(inputs):
                before = source.read_bytes()
                for kind in ['direct', 'symlink', 'hardlink']:
                    output = source if kind == 'direct' else root / f'alias-{index}-{kind}.json'
                    if kind == 'symlink':
                        output.symlink_to(source)
                    elif kind == 'hardlink':
                        output.hardlink_to(source)
                    with self.subTest(source=source.name, kind=kind), self.assertRaisesRegex(ValueError, 'must not overwrite'):
                        module.protect_output(output, manifest, root, check)
                    self.assertEqual(source.read_bytes(), before)

    def test_new_raw_script_or_index_destination_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, _ = protection_fixture(root)
            for directory in ['data/raw', 'scripts', 'research/image-index']:
                output = root / directory / 'new-report.json'
                with self.subTest(directory=directory), self.assertRaises(ValueError):
                    module.protect_output(output, manifest, root)
                self.assertFalse(output.exists())

    def test_cli_refuses_alias_before_computation_and_separate_output_succeeds(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, inputs = protection_fixture(root)
            before = {path: path.read_bytes() for path in inputs}
            target = root / 'data/raw/source.txt'
            argv = ['account', '--output', str(target)]
            with patch.object(module, 'ROOT', root), patch.object(module, 'load_manifest', return_value=manifest), \
                    patch.object(module, 'report') as compute, patch('sys.argv', argv), \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                module.main()
            self.assertEqual(error.exception.code, 1)
            compute.assert_not_called()
            target = root / 'separate-report.json'
            result = {'variants': [], 'synthetic': 'writer boundary only'}
            with patch.object(module, 'ROOT', root), patch.object(module, 'load_manifest', return_value=manifest), \
                    patch.object(module, 'report', return_value=result), patch('sys.argv', ['account', '--output', str(target)]):
                module.main()
            self.assertEqual(json.loads(target.read_text()), result)
            self.assertEqual({path: path.read_bytes() for path in inputs}, before)

    def test_alias_created_during_computation_is_refused_immediately_before_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, inputs = protection_fixture(root)
            source = root / 'data/raw/source.txt'
            before = source.read_bytes()
            output = root / 'late-alias.json'
            def compute(*args, **kwargs):
                output.hardlink_to(source)
                return {'variants': [], 'synthetic': 'late alias only'}
            with patch.object(module, 'ROOT', root), patch.object(module, 'load_manifest', return_value=manifest), \
                    patch.object(module, 'report', side_effect=compute), \
                    patch('sys.argv', ['account', '--output', str(output)]), \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                module.main()
            self.assertEqual(error.exception.code, 1)
            self.assertEqual(source.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
