import unittest
from unittest.mock import patch

from scripts.ivtff import parse_ivtff
from scripts.section_strata import GROUPS, page_assignment, section_report, selected_records


HEADER = '#=IVTFF Eva- 2.0 M\n'


class SectionStrataTests(unittest.TestCase):
    def report(self, left, right=None):
        sources = [({'id': 'ZL3b', 'sha256': 'synthetic'}, parse_ivtff(HEADER + left)),
                   ({'id': 'IT2a', 'sha256': 'synthetic'}, parse_ivtff(HEADER + (right or left)))]
        with patch('scripts.section_strata.load_sources', return_value=sources):
            return section_report(repetitions=3, seed=1)

    def test_all_range_endpoints_and_panels_keep_exact_source_names(self):
        for part, first, last in [('I', 1, 66), ('II', 67, 73), ('III', 75, 84),
                                  ('IV', 85, 86), ('V', 87, 102), ('VI', 103, 117)]:
            for number in (first, last):
                for side in ('r', 'v'):
                    for suffix in ('', '1', '6'):
                        page = f'f{number}{side}{suffix}'
                        assignment = page_assignment(page)
                        self.assertEqual(assignment['catalog_part'], part)
                        self.assertEqual(assignment['source_page'], page)
                        self.assertEqual(assignment['source_folio_number'], number)

    def test_special_pages_and_gaps_do_not_gain_invented_aliases(self):
        for page in ('fRos', 'f74r', 'f118v'):
            self.assertEqual(page_assignment(page)['catalog_part'], 'unassigned')
        self.assertEqual(page_assignment('fRos')['reason'], 'non_numeric_page_name')
        for page in ('85v', 'f085v', 'f85v7', 'fRos1'):
            with self.subTest(page=page), self.assertRaises(ValueError):
                page_assignment(page)

    def test_joint_locator_rule_and_source_paragraph_disagreements_are_recorded(self):
        left = '<f1r>\n<f1r.1,@P0> <%>y.a\n<f1r.2,+P0> q.a\n'
        right = '<f1r>\n<f1r.1,@P0> y.a\n<f1r.2,=P0> q.a\n'
        report = self.report(left, right)
        self.assertEqual(report['selection']['selected_location_count'], 1)
        self.assertEqual(report['selection']['excluded_nonregular_locations'], ['f1r.2'])
        self.assertEqual(report['selection']['source_paragraph_disagreement_locations'], ['f1r.1'])
        for source, state in zip(report['sources'], (True, False)):
            populated = [cohort for cohort in source['variants'][0]['cohorts'] if cohort['selected_loci']]
            self.assertEqual(populated[0]['source_paragraph_start'], state)

    def test_cohorts_partition_records_and_retain_empty_unassigned_and_boundary_gaps(self):
        report = self.report('<f1r> <! $L=A>\n<f1r.1,@P0> q<! <%>.a\n'
                             '<f1r.2,+P0> <%>?.y.a\n<f67r1>\n<f67r1.1,@P0> y.a\n'
                             '<fRos>\n<fRos.1,@P0> <%>q.a\n')
        for source in report['sources']:
            for variant in source['variants']:
                cohorts = variant['cohorts']
                self.assertEqual(len(cohorts), len(GROUPS) * 2)
                self.assertEqual(sum(cohort['selected_loci'] for cohort in cohorts), 4)
                part_i = [cohort for cohort in cohorts if cohort['catalog_part'] == 'I']
                self.assertEqual([cohort['selected_loci'] for cohort in part_i], [1, 1])
                self.assertEqual(part_i[1]['first_position']['eligible_loci'], 0)
                self.assertEqual(part_i[0]['first_position']['features'][0]['paired_difference'], 1)
                unassigned = [cohort for cohort in cohorts if cohort['catalog_part'] == 'unassigned']
                self.assertEqual([cohort['selected_loci'] for cohort in unassigned], [0, 1])
                self.assertEqual(unassigned[1]['source_page_locus_counts'], {'fRos': 1})
                empty = next(cohort for cohort in cohorts if cohort['catalog_part'] == 'VI')
                self.assertIsNone(empty['first_position']['features'][0]['paired_difference'])
                for cohort in cohorts:
                    self.assertEqual(sum(cohort['source_page_locus_counts'].values()), cohort['selected_loci'])
                    self.assertEqual([feature['feature'] for feature in cohort['first_position']['features']],
                                     ['literal_q_prefix', 'literal_y_prefix'])

    def test_duplicate_transcriber_records_cannot_gain_extra_locus_weight(self):
        document = parse_ivtff(HEADER + '<f1r>\n<f1r.1,@P0;A> q.a\n<f1r.1,@P0;B> y.a\n')
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            selected_records(document, {'f1r.1'})

    def test_no_selected_locations_is_an_explicit_failure(self):
        with self.assertRaisesRegex(ValueError, 'no paired regular P0'):
            self.report('<f1r>\n<f1r.1,=P0> q.a\n')


if __name__ == '__main__':
    unittest.main()
