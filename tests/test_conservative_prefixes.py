from copy import deepcopy
import unittest

from scripts.conservative_prefixes import common_cohort


def payload(mode):
    records = []
    for source in ['ZL3b', 'IT2a']:
        for key in ['f1r.1', 'f1r.2']:
            records.append({'source_id': source, 'locus_key': key, 'locus_type': 'P0',
                            'locator': '+', 'eligible': True, 'tokens': ['q', 'a'],
                            'token_count': 2, 'exclusion_reasons': []})
    return {'schema_version': 1, 'adapter_version': 'plain-eva-v1',
            'analysis_unit': 'transcription_locus',
            'processing': {'uncertain_space_policy': mode, 'selected_locus_types': ['P0'],
                           'ambiguity_policy': 'exclude entire selected locus with explicit reasons'},
            'sources': [{'id': 'ZL3b', 'sha256': 'zl'}, {'id': 'IT2a', 'sha256': 'it'}],
            'records': records}


class ConservativeCohortTests(unittest.TestCase):
    def setUp(self):
        self.payloads = [payload('split'), payload('join')]
        self.hashes = {'ZL3b': 'zl', 'IT2a': 'it'}
        self.keys = {'f1r.1', 'f1r.2'}

    def test_a_single_policy_failure_removes_the_key_from_every_case(self):
        self.payloads[1]['records'][3]['tokens'] = ['qa']
        self.payloads[1]['records'][3]['token_count'] = 1
        selected, _, excluded, _ = common_cohort(self.payloads, self.hashes, self.keys)
        self.assertEqual(selected, {'f1r.1'})
        self.assertEqual(excluded[0]['locus_key'], 'f1r.2')
        self.assertEqual(excluded[0]['source_policy_failures'][0]['reasons'], ['fewer_than_two_tokens'])

    def test_ambiguity_and_same_line_locator_failures_are_recorded(self):
        record = self.payloads[0]['records'][0]
        record.update(eligible=False, tokens=None, token_count=None,
                      exclusion_reasons=['alternative_reading'], locator='=')
        selected, _, excluded, _ = common_cohort(self.payloads, self.hashes, self.keys)
        self.assertEqual(selected, {'f1r.2'})
        self.assertEqual(excluded[0]['source_policy_failures'][0]['reasons'],
                         ['alternative_reading', 'nonregular_locator'])

    def test_missing_records_changed_provenance_and_duplicate_policies_fail(self):
        changes = [lambda p: p[0]['records'].pop(),
                   lambda p: p[0]['sources'][0].update(sha256='changed'),
                   lambda p: p[0].update(adapter_version='plain-eva-v2'),
                   lambda p: p[1]['processing'].update(uncertain_space_policy='split'),
                   lambda p: p[0]['records'].append(deepcopy(p[0]['records'][0])),
                   lambda p: p[0]['records'][0].update(token_count=99),
                   lambda p: p[0]['records'][0].update(tokens=['@133;', 'a'])]
        for change in changes:
            variants = deepcopy(self.payloads)
            change(variants)
            with self.subTest(change=change), self.assertRaises(ValueError):
                common_cohort(variants, self.hashes, self.keys)


if __name__ == '__main__':
    unittest.main()
