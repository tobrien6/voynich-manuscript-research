from copy import deepcopy
from contextlib import redirect_stderr
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.audit_eva_token_coverage import encoded
from scripts.audit_transliterations import ROOT, load_sources
from scripts.paragraph_membership import membership_report
from scripts.paragraph_token_corpus import (
    MEMBERSHIP_PATH, PLAN_PATH, build, construct, coverage, main, protect_outputs,
    strict_json, verify_corpus,
)


LEFT = ('<f1r> <! $L=A>\n<f1r.1,@P0> <%>Ab,cd\n<f1r.2,+Pc> E<$>\n'
        '<f1r.3,+P1> <%>Xy<$>\n<f1r.4,=Pr> <%><@L=B>ab,cd.ef<$>\n'
        '<f1r.5,+Pb> <%>P<$>\n<f1r.6,+Pt> <%>T<$>\n')
RIGHT = LEFT.replace('<f1r.2,+Pc> E<$>', '<f1r.2,+Pc> [E:F]<$>')


def fixture(root, left=LEFT, right=RIGHT):
    (root / 'data/raw').mkdir(parents=True)
    (root / 'research/transliteration').mkdir(parents=True)
    catalog = {'schema_version': 1, 'sources': []}
    for identifier, alphabet, body in [('ZL3b', 'Eva-', left), ('IT2a', 'EvaT', right)]:
        data = ('#=IVTFF ' + alphabet + ' 2.0 M\n' + body).encode('ascii')
        relative = 'data/raw/' + identifier + '.txt'
        (root / relative).write_bytes(data)
        catalog['sources'].append({'id': identifier, 'alphabet': alphabet, 'path': relative,
                                   'url': 'https://example.org/' + identifier,
                                   'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
    (root / 'data/transliterations.json').write_text(json.dumps(catalog))
    (root / MEMBERSHIP_PATH).write_bytes(encoded(membership_report(load_sources(root))))
    (root / PLAN_PATH).write_text('Synthetic corpus selection plan.\n')
    return root


class ParagraphTokenCorpusTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = fixture(Path(self.directory.name))

    def test_all_p_types_singletons_case_and_source_row_boundaries_are_retained(self):
        packet = build(self.root)
        self.assertEqual(packet['processing']['selected_locus_types'], ['P0', 'P1', 'Pb', 'Pc', 'Pr', 'Pt'])
        singleton = next(p for p in packet['paragraphs'] if p['member_keys'] == ['f1r.3'])
        self.assertTrue(singleton['common_eligible'])
        self.assertTrue(all(v['loci'][0]['tokens'] == ['Xy'] for v in singleton['variants']))
        joined = next(p for p in packet['paragraphs'] if p['member_keys'] == ['f1r.4'])
        self.assertEqual(joined['variants'][0]['loci'][0]['tokens'], ['ab', 'cd', 'ef'])
        self.assertEqual(joined['variants'][1]['loci'][0]['tokens'], ['abcd', 'ef'])
        self.assertEqual(joined['variants'][0]['loci'][0]['locator'], '=')
        self.assertEqual(joined['variants'][0]['loci'][0]['variables']['L'], 'B')
        self.assertIsNone(packet['processing']['minimum_token_count_filter'])

    def test_one_source_exclusion_suppresses_all_four_whole_unit_payloads(self):
        packet = build(self.root)
        excluded = next(p for p in packet['paragraphs'] if p['member_keys'] == ['f1r.1', 'f1r.2'])
        self.assertFalse(excluded['common_eligible'])
        self.assertEqual([v['locally_eligible'] for v in excluded['variants']], [True, True, False, False])
        for variant in excluded['variants']:
            self.assertIsNone(variant['common_corpus_token_count'])
            self.assertEqual([row['tokens'] for row in variant['loci']], [None, None])
            self.assertEqual([row['locus_key'] for row in variant['loci']], ['f1r.1', 'f1r.2'])
        self.assertEqual(excluded['variants'][2]['failed_loci'],
                         [{'locus_key': 'f1r.2', 'exclusion_reasons': ['alternative_reading']}])

    def test_eligible_multi_locus_units_are_never_flattened(self):
        # Recreate a separate fixture whose paired source rows are all readable.
        with tempfile.TemporaryDirectory() as directory:
            root = fixture(Path(directory), left=LEFT, right=LEFT)
            packet = build(root)
        paragraph = next(p for p in packet['paragraphs'] if len(p['member_keys']) == 2)
        self.assertTrue(paragraph['common_eligible'])
        split = paragraph['variants'][0]
        self.assertEqual([row['tokens'] for row in split['loci']], [['Ab', 'cd'], ['E']])
        self.assertEqual(split['common_corpus_token_count'], 3)

    def test_parent_membership_tampering_is_rejected_even_with_reconciled_totals(self):
        sources = load_sources(self.root)
        parent = membership_report(sources)
        parent['exact_unit_comparison']['matches'].pop()
        parent['exact_unit_comparison']['matching_complete_unit_count'] -= 1
        with self.assertRaisesRegex(ValueError, 'complete pinned-source replay'):
            construct(sources, parent, {})

    def test_cached_token_type_and_row_tampering_fail_complete_replay(self):
        packet = build(self.root)
        for mode in ('tokens', 'type', 'missing_row'):
            altered = deepcopy(packet)
            if mode == 'type':
                altered['schema_version'] = True
            elif mode == 'missing_row':
                altered['paragraphs'][0]['variants'][0]['loci'].pop()
            else:
                paragraph = next(p for p in altered['paragraphs'] if p['common_eligible'])
                paragraph['variants'][0]['loci'][0]['tokens'][0] = 'Changed'
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, 'complete pinned producer'):
                verify_corpus(encoded(altered), self.root)

    def test_cache_formatting_can_change_without_changing_canonical_content(self):
        packet = build(self.root)
        reformatted = json.dumps(packet, separators=(',', ':')).encode()
        self.assertEqual(verify_corpus(reformatted, self.root), packet)

    def test_strict_cache_json_rejects_duplicates_and_nonfinite_values(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                strict_json(raw)

    def test_coverage_contains_no_token_payload_and_accounts_for_all_candidates(self):
        packet = build(self.root)
        report = coverage(packet)
        self.assertEqual(len(report['unit_ledger']), packet['cohort']['candidate_units'])
        self.assertEqual(packet['cohort']['common_eligible_units'] + packet['cohort']['excluded_candidate_units'], 5)

        def keys(value):
            if isinstance(value, dict):
                return set(value) | set().union(*(keys(child) for child in value.values()))
            if isinstance(value, list):
                return set().union(*(keys(child) for child in value))
            return set()
        self.assertNotIn('tokens', keys(report))

    def test_outputs_cannot_alias_catalog_parent_plans_or_one_another(self):
        catalog = self.root / 'data/transliterations.json'
        for target in (catalog, self.root / MEMBERSHIP_PATH, self.root / PLAN_PATH):
            with self.subTest(target=target.name), self.assertRaises(ValueError):
                protect_outputs([target], root=self.root)
            alias = self.root / (target.name + '.hardlink')
            os.link(target, alias)
            with self.assertRaises(ValueError):
                protect_outputs([alias], root=self.root)
        with self.assertRaisesRegex(ValueError, 'distinct'):
            protect_outputs([self.root / 'same.json', self.root / 'same.json'], root=self.root)
        check = self.root / 'check.json'
        check.write_text('{}')
        with self.assertRaises(ValueError):
            protect_outputs([check], read_inputs=[check], root=self.root)

    def test_no_shared_eligible_units_produces_an_explicit_empty_cohort(self):
        left = '<f1r>\n<f1r.1,@P0> <%>[a:b]<$>\n'
        right = '<f1r>\n<f1r.1,@P0> <%>a<$>\n'
        with tempfile.TemporaryDirectory() as directory:
            packet = build(fixture(Path(directory), left, right))
        self.assertEqual(packet['cohort']['candidate_units'], 1)
        self.assertEqual(packet['cohort']['common_eligible_units'], 0)
        self.assertTrue(all(v['loci'][0]['tokens'] is None for v in packet['paragraphs'][0]['variants']))

    def test_cli_rejects_protected_output_before_preprocessing(self):
        target = self.root / 'data/transliterations.json'
        before = target.read_bytes()
        with patch('scripts.paragraph_token_corpus.ROOT', self.root), \
                patch('scripts.paragraph_token_corpus.build') as producer, \
                patch('sys.argv', ['paragraph_token_corpus.py', '--output', str(target)]), \
                redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            main()
        producer.assert_not_called()
        self.assertEqual(target.read_bytes(), before)

    def test_failed_full_cache_verification_writes_no_partial_coverage(self):
        packet = build(self.root)
        altered = deepcopy(packet)
        paragraph = next(p for p in altered['paragraphs'] if p['common_eligible'])
        paragraph['variants'][0]['loci'][0]['tokens'][0] = 'Changed'
        cache = self.root / 'changed-corpus.json'
        cache.write_bytes(encoded(altered))
        output = self.root / 'coverage.json'
        output.write_bytes(b'preserve existing output')
        with patch('scripts.paragraph_token_corpus.ROOT', self.root), \
                patch('sys.argv', ['paragraph_token_corpus.py', '--output', str(output),
                                   '--check-corpus', str(cache)]), \
                redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            main()
        self.assertEqual(output.read_bytes(), b'preserve existing output')

    def test_real_pins_reproduce_coverage_and_keep_every_excluded_unit_visible(self):
        packet = build()
        report = coverage(packet)
        expected = strict_json((ROOT / 'research/transliteration/paragraph_corpus_coverage.json').read_bytes())
        self.assertEqual(report, expected)
        self.assertEqual(packet['cohort']['candidate_units'], 671)
        self.assertEqual(packet['cohort']['common_eligible_units'], 233)
        self.assertEqual(packet['cohort']['common_eligible_member_loci'], 885)
        for paragraph in packet['paragraphs']:
            if not paragraph['common_eligible']:
                self.assertTrue(all(row['tokens'] is None for variant in paragraph['variants'] for row in variant['loci']))


if __name__ == '__main__':
    unittest.main()
