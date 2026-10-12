import unittest
from unittest.mock import patch

from scripts.ivtff import parse_ivtff
from scripts.locus_positions import prepare_rows, summarize_position
from scripts.position_cohorts import cohort_report, eligible_contrasts


def document(text):
    return parse_ivtff('#=IVTFF Eva- 2.0 M\n<f1r>\n' + text)


def report(zl, it, extras=()):
    sources = [({'id': 'ZL3b', 'sha256': 'synthetic-zl'}, zl),
               ({'id': 'IT2a', 'sha256': 'synthetic-it'}, it), *extras]
    with patch('scripts.position_cohorts.load_sources', return_value=sources):
        return cohort_report()


class FixedCohortTests(unittest.TestCase):
    def test_cohort_removes_selection_shift_and_pairs_the_same_keys(self):
        zl = document('<f1r.1,@P0> q.a\n<f1r.2,+P0> a.q\n')
        it = document('<f1r.1,@P0> ?.a\n<f1r.2,+P0> q.a\n')
        result = report(zl, it)['boundaries'][0]
        self.assertEqual(result['common_eligible_loci'], 1)
        primary = result['variants'][0]
        other = result['variants'][4]
        self.assertEqual(primary['own_eligible_loci'], 2)
        self.assertEqual(other['ineligible_locus_keys'], ['f1r.1'])
        primary_q, other_q = primary['features'][0], other['features'][0]
        self.assertEqual(primary_q['own_eligible_mean_contrast'], 0)
        self.assertEqual(primary_q['common_cohort_mean_contrast'], -1)
        self.assertEqual(primary_q['common_minus_own_mean_contrast'], -1)
        self.assertEqual(other_q['paired_mean_difference_from_primary'], 2)
        self.assertEqual(other_q['paired_mean_absolute_difference_from_primary'], 2)

    def test_boundaries_have_separate_cohorts_without_promoting_tokens(self):
        zl = document('<f1r.1,@P0> ?.q.a\n<f1r.2,+P0> q.a.?\n')
        result = report(zl, zl)['boundaries']
        self.assertEqual([row['common_eligible_loci'] for row in result], [1, 1])
        self.assertNotEqual(result[0]['sorted_common_locus_keys_sha256'],
                            result[1]['sorted_common_locus_keys_sha256'])
        self.assertEqual(result[0]['variants'][0]['ineligible_locus_keys'], ['f1r.1'])
        self.assertEqual(result[1]['variants'][0]['ineligible_locus_keys'], ['f1r.2'])

    def test_empty_common_cohort_does_not_report_zero_effects(self):
        zl = document('<f1r.1,@P0> q.a\n<f1r.2,+P0> ?.a\n')
        it = document('<f1r.1,@P0> ?.a\n<f1r.2,+P0> q.a\n')
        first = report(zl, it)['boundaries'][0]
        self.assertEqual(first['common_eligible_loci'], 0)
        q = first['variants'][0]['features'][0]
        self.assertEqual(q['own_eligible_mean_contrast'], 1)
        self.assertIsNone(q['common_cohort_mean_contrast'])
        self.assertIsNone(q['paired_mean_difference_from_primary'])

    def test_all_policies_enter_the_intersection(self):
        zl = document('<f1r.1,@P0> [q:a].a\n<f1r.2,+P0> q,a\n'
                      '<f1r.3,+P0> q.a\n')
        it = document('<f1r.1,@P0> q.a\n<f1r.2,+P0> q.a\n'
                      '<f1r.3,+P0> q.a\n')
        first = report(zl, it)['boundaries'][0]
        self.assertEqual(first['common_eligible_loci'], 1)
        self.assertEqual(first['variants'][0]['own_eligible_loci'], 2)
        self.assertEqual(first['variants'][1]['own_eligible_loci'], 3)
        self.assertEqual(first['variants'][2]['own_eligible_loci'], 1)

    def test_absolute_differences_expose_cancelling_changes(self):
        zl = document('<f1r.1,@P0> q.a\n<f1r.2,+P0> a.q\n')
        it = document('<f1r.1,@P0> a.q\n<f1r.2,+P0> q.a\n')
        q = report(zl, it)['boundaries'][0]['variants'][4]['features'][0]
        self.assertEqual(q['paired_mean_difference_from_primary'], 0)
        self.assertEqual(q['paired_mean_absolute_difference_from_primary'], 2)
        self.assertEqual(q['paired_loci_differing_from_primary'], 2)

    def test_matches_accepted_equal_locus_weight_contrasts(self):
        zl = document('<f1r.1,@P0> q.a\n<f1r.2,+P0> a.q.q.q\n')
        rows = prepare_rows(zl.loci, 'split', 'exclude')
        accepted = summarize_position(rows, 'first', 1, 1)
        current = report(zl, zl)['boundaries'][0]['variants'][0]
        for old, new in zip(accepted['features'], current['features']):
            self.assertEqual(old['paired_difference'], new['own_eligible_mean_contrast'])
            self.assertEqual(old['paired_difference'], new['common_cohort_mean_contrast'])

    def test_duplicate_keys_and_unsupported_boundary_fail(self):
        doc = document('<f1r.1,@P0;A> q.a\n<f1r.1,@P0;B> q.a\n')
        with self.assertRaisesRegex(ValueError, 'duplicate selected locus key'):
            report(doc, doc)
        with self.assertRaisesRegex(ValueError, 'duplicate selected locus key'):
            eligible_contrasts(prepare_rows(doc.loci, 'split', 'exclude'), 'first')
        with self.assertRaisesRegex(ValueError, 'boundary must'):
            eligible_contrasts([], 'middle')

    def test_missing_shared_p0_fails_and_comparators_do_not_enter(self):
        doc = document('<f1r.1,@P0> q.a\n')
        other = document('<f1r.2,@P0> q.a\n')
        with self.assertRaisesRegex(ValueError, 'no common P0'):
            report(doc, other)
        extra = ({'id': 'GC2a', 'sha256': 'synthetic'}, other)
        result = report(doc, doc, [extra])
        self.assertEqual([source['id'] for source in result['sources']], ['ZL3b', 'IT2a'])
        self.assertEqual(result['selection']['count'], 1)


if __name__ == '__main__':
    unittest.main()
