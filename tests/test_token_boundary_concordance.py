from contextlib import redirect_stderr
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.audit_eva_token_coverage import encoded
from scripts.eva_token_adapter import build as adapter
from scripts.token_boundary_concordance import ROOT, build, compare, construct, main, representation


def fixture(root):
    (root / 'data/raw').mkdir(parents=True)
    bodies = {
        'ZL3b': ('<f1r.1,@P0> o.aiin\n<f1r.2,+P0> ab,cd\n'
                 '<f1r.3,+P0> Ab.cd\n<f1r.4,=P0> a<->b\n'
                 '<f1r.5,+P0> ab.[c:d]\n<f1r.6,+P1> ab.cd\n'
                 '<f1r.7,!P0> a\n<f1r.8,+P0> ef\n'),
        'IT2a': ('<f1r.1,@P0> oaiin\n<f1r.2,+P0> abcd\n'
                 '<f1r.3,+P0> ab.cd\n<f1r.4,+P0> a.b\n'
                 '<f1r.5,+P0> ab.c\n<f1r.6,+P1> ab.cd\n'
                 '<f1r.7,!P0> a\n'),
    }
    sources = []
    for ident, alphabet in (('ZL3b', 'Eva-'), ('IT2a', 'EvaT')):
        data = ('#=IVTFF ' + alphabet + ' 2.0 M\n<f1r>\n' + bodies[ident]).encode('ascii')
        path = 'data/raw/' + ident + '.txt'
        (root / path).write_bytes(data)
        sources.append({'id': ident, 'alphabet': alphabet, 'path': path,
                        'url': 'https://example.org/' + ident,
                        'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
    (root / 'data/transliterations.json').write_text(json.dumps({'sources': sources}))
    return {policy: adapter(policy, kinds=('P0',), root=root) for policy in ('split', 'join')}


class BoundaryConcordanceTests(unittest.TestCase):
    def test_one_token_and_equal_count_moved_boundaries(self):
        self.assertEqual(representation(['oaiin']), ('oaiin', []))
        result = compare(['o', 'aiin'], ['oaiin'])
        self.assertEqual(result['category'], 'same_chain_different_boundaries')
        self.assertEqual(result['aligned_boundary_difference']['only_left_boundary_offsets'], [1])
        moved = compare(['ab', 'c'], ['a', 'bc'])['aligned_boundary_difference']
        self.assertEqual(moved['only_left_boundary_offsets'], [2])
        self.assertEqual(moved['only_right_boundary_offsets'], [1])

    def test_case_difference_has_no_aligned_boundary_comparison(self):
        self.assertEqual(compare(['Ab', 'cd'], ['ab', 'cd']),
                         {'category': 'different_chains', 'aligned_boundary_difference': None})
        self.assertEqual(compare(['ab'], ['ab'])['category'], 'same_chain_same_boundaries')

    def test_invalid_or_empty_tokens_are_rejected(self):
        for tokens in ([], [''], ['a', ''], ['a?'], ['a b'], [None], ['é'], 'ab'):
            with self.subTest(tokens=tokens), self.assertRaises(ValueError):
                representation(tokens)

    def test_fixed_four_treatment_cohort_excludes_whole_ambiguous_locus(self):
        with tempfile.TemporaryDirectory() as directory:
            outputs = fixture(Path(directory))
            report = construct(outputs)
        self.assertEqual(report['selection']['candidate_shared_present_p0']['native_locus_count'], 5)
        self.assertEqual(report['selection']['common_eligible']['native_locus_keys'],
                         ['f1r.1', 'f1r.2', 'f1r.3', 'f1r.4'])
        self.assertEqual(report['selection']['present_p0_only_in_ZL3b']['native_locus_keys'], ['f1r.8'])
        self.assertEqual(report['selection']['excluded_candidate_loci'][0]['native_locus_key'], 'f1r.5')
        self.assertEqual(report['cross_source']['split']['category_key_sets']['same_chain_different_boundaries']
                         ['native_locus_keys'], ['f1r.1', 'f1r.2'])
        self.assertEqual(report['cross_source']['join']['category_key_sets']['same_chain_different_boundaries']
                         ['native_locus_keys'], ['f1r.1'])
        self.assertEqual(report['cross_source_boundary_disagreements_under_both_policies']['native_locus_keys'],
                         ['f1r.1'])
        self.assertEqual(report['cross_source_locator_differences'][0]['native_locus_key'], 'f1r.4')
        self.assertEqual(report['variants'][0]['drawing_interruption_count'], 1)

    def test_changed_source_order_kind_duplicate_or_noninvariant_chain_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            original = fixture(Path(directory))
        for mutation, message in (
                ('order', 'ordered'), ('kind', 'only P0'), ('duplicate', 'Multiple records'),
                ('chain', 'change a literal encoded chain')):
            outputs = deepcopy(original)
            if mutation == 'order':
                for payload in outputs.values():
                    payload['sources'].reverse()
            elif mutation == 'kind':
                for payload in outputs.values():
                    payload['processing']['selected_locus_types'] = ['P0', 'P1']
            elif mutation == 'duplicate':
                outputs['join']['records'].append(deepcopy(outputs['join']['records'][0]))
            else:
                row = outputs['join']['records'][0]
                row['tokens'] = ['XY']
                row['token_count'] = 1
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError, message):
                construct(outputs)

    def test_real_pinned_case_and_complete_report_replay(self):
        report = build()
        self.assertEqual(report['selection']['common_eligible']['native_locus_count'], 2940)
        for policy in ('split', 'join'):
            row = next(row for row in report['cross_source'][policy]['boundary_disagreements_on_identical_chains']
                       if row['native_locus_key'] == 'f67r1.1')
            self.assertEqual((row['chain_ascii_length'], row['left_token_count'], row['right_token_count']), (49, 9, 8))
            self.assertEqual(row['only_left_boundary_offsets'], [45])
            self.assertEqual(row['only_right_boundary_offsets'], [])
        self.assertEqual(encoded(report), (ROOT / 'research/transliteration/token_boundary_concordance.json').read_bytes())

    def test_cli_rejects_source_implementation_and_alias_outputs_before_building(self):
        script = ROOT / 'scripts/token_boundary_concordance.py'
        with tempfile.TemporaryDirectory() as directory:
            symlink = Path(directory) / 'alias.json'
            symlink.symlink_to(script)
            paths = [script, ROOT / 'data/transliterations.json', ROOT / 'data/raw/ZL3b-n.txt', symlink]
            for path in paths:
                with self.subTest(path=path.name), \
                        patch('sys.argv', ['audit', '--output', str(path)]), \
                        patch('scripts.token_boundary_concordance.build', side_effect=AssertionError('must not run')) as producer, \
                        redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    main()
                producer.assert_not_called()

    def test_cli_checks_complete_content_and_numeric_types(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.json'
            expected = {'counts': 1, 'details': ['offset']}
            for changed in ({'counts': True, 'details': ['offset']}, {'counts': 1, 'details': []}):
                path.write_bytes(encoded(changed))
                with patch('sys.argv', ['audit', '--check', str(path)]), \
                        patch('scripts.token_boundary_concordance.build', return_value=expected), \
                        redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    main()


if __name__ == '__main__':
    unittest.main()
