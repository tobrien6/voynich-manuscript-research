from copy import deepcopy
import unittest

from scripts.ivtff import parse_ivtff
from scripts.section_agreement import agreement_report
from scripts.section_strata import section_report


def sources(left, right):
    return [({'id': identifier, 'sha256': 'synthetic'},
             parse_ivtff('#=IVTFF Eva- 2.0 M\n' + text))
            for identifier, text in [('ZL3b', left), ('IT2a', right)]]


class SectionAgreementTests(unittest.TestCase):
    def analyze(self, paired):
        baseline = section_report(3, 1, sources=paired)
        return agreement_report(paired, baseline, 3, 1)

    def test_disagreements_are_removed_from_both_sources_and_effect_change_is_exact(self):
        paired = sources('<f1r>\n<f1r.1,@P0> q.a\n<f1r.2,+P0> y.a\n',
                         '<f1r>\n<f1r.1,@P0> <%>q.a\n<f1r.2,+P0> y.a\n')
        report = self.analyze(paired)
        self.assertEqual(report['selection']['agreement_selected_location_count'], 1)
        self.assertEqual(report['selection']['removed_paragraph_start_disagreements'],
                         [{'key': 'f1r.1', 'ZL3b_paragraph_start': False, 'IT2a_paragraph_start': True}])
        left = report['sources'][0]['variants'][0]['cohorts'][0]
        self.assertEqual(left['removed_eligible_loci'], 1)
        self.assertEqual(left['feature_comparisons'][0],
                         {'feature': 'literal_q_prefix', 'before': .5, 'after': 0, 'after_minus_before': -.5})

    def test_comments_and_end_only_disagreements_do_not_change_start_membership(self):
        report = self.analyze(sources('<f1r>\n<f1r.1,@P0> q<! <%>.a<$>\n',
                                     '<f1r>\n<f1r.1,@P0> q.a\n'))
        self.assertEqual(report['selection']['removed_paragraph_start_disagreements'], [])
        for source in report['sources']:
            for variant in source['variants']:
                for cohort in variant['cohorts']:
                    for comparison in cohort['feature_comparisons']:
                        self.assertIn(comparison['after_minus_before'], (0, None))

    def test_common_annotation_membership_does_not_claim_common_token_eligibility(self):
        report = self.analyze(sources('<f1r>\n<f1r.1,@P0> ?.q.a\n',
                                     '<f1r>\n<f1r.1,@P0> y.q.a\n'))
        self.assertFalse(report['selection']['token_eligibility_fixed_across_variants'])
        cohorts = [source['variants'][0]['cohorts'][0] for source in report['sources']]
        self.assertEqual([cohort['selected_loci'] for cohort in cohorts], [1, 1])
        self.assertEqual([cohort['first_position']['eligible_loci'] for cohort in cohorts], [0, 1])

    def test_complete_exclusion_retains_empty_cells_and_undefined_effects(self):
        report = self.analyze(sources('<fRos>\n<fRos.1,@P0> <%>q.a\n',
                                     '<fRos>\n<fRos.1,@P0> q.a\n'))
        self.assertEqual(report['selection']['agreement_selected_location_count'], 0)
        for source in report['sources']:
            for variant in source['variants']:
                self.assertEqual(len(variant['cohorts']), 14)
                for cohort in variant['cohorts']:
                    self.assertEqual(cohort['selected_loci'], 0)
                    self.assertIsNone(cohort['feature_comparisons'][0]['after'])
                    self.assertIsNone(cohort['feature_comparisons'][0]['after_minus_before'])

    def test_stale_baseline_is_rejected_before_comparing(self):
        paired = sources('<f1r>\n<f1r.1,@P0> q.a\n', '<f1r>\n<f1r.1,@P0> q.a\n')
        baseline = deepcopy(section_report(3, 1, sources=paired))
        baseline['sources'][0]['variants'][0]['cohorts'][0]['selected_loci'] = 2
        with self.assertRaisesRegex(ValueError, 'baseline differs'):
            agreement_report(paired, baseline, 3, 1)


if __name__ == '__main__':
    unittest.main()
