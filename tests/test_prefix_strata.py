import unittest
from unittest.mock import patch

from scripts.ivtff import parse_ivtff
from scripts.prefix_strata import paragraph_start, select_locations, stratified_report


HEADER = '#=IVTFF Eva- 2.0 M\n'


class PrefixStrataTests(unittest.TestCase):
    def test_locator_must_be_regular_in_both_sources(self):
        left = parse_ivtff(HEADER + '<f1r>\n<f1r.1,@P0> q.a\n<f1r.2,+P0> y.a\n')
        right = parse_ivtff(HEADER + '<f1r>\n<f1r.1,@P0> q.a\n<f1r.2,=P0> y.a\n')
        present, regular = select_locations([({}, left), ({}, right)])
        self.assertEqual(present, {'f1r.1', 'f1r.2'})
        self.assertEqual(regular, {'f1r.1'})

    def test_comments_do_not_create_paragraph_start_marks(self):
        doc = parse_ivtff(HEADER + '<f1r>\n<f1r.1,@P0> q<! <%>.a\n')
        self.assertFalse(paragraph_start(doc.loci[0]))

    def test_partition_keeps_unset_labels_empty_cohorts_and_boundary_gaps(self):
        doc = parse_ivtff(HEADER + '<f1r> <! $L=A>\n'
                          '<f1r.1,@P0> <%>q.a\n<f1r.2,+P0> y.a\n'
                          '<f1v>\n<f1v.1,@P0> ?.y.a\n')
        sources = [({'id': 'ZL3b', 'sha256': 'synthetic'}, doc),
                   ({'id': 'IT2a', 'sha256': 'synthetic'}, doc)]
        with patch('scripts.prefix_strata.load_sources', return_value=sources):
            report = stratified_report(repetitions=1, seed=1)
        self.assertEqual(report['selection']['source_currier_labels_including_unset'], ['A', 'unset'])
        cohorts = report['sources'][0]['variants'][0]['cohorts']
        self.assertEqual(sum(cohort['selected_loci'] for cohort in cohorts), 3)
        unset = [cohort for cohort in cohorts if cohort['source_currier_label'] == 'unset']
        self.assertEqual([cohort['selected_loci'] for cohort in unset], [1, 0])
        self.assertEqual(unset[0]['positions'][0]['eligible_loci'], 0)
        self.assertEqual(unset[0]['positions'][1]['eligible_loci'], 1)
        for cohort in cohorts:
            for position in cohort['positions']:
                self.assertEqual([feature['feature'] for feature in position['features']],
                                 ['literal_q_prefix', 'literal_y_prefix'])


if __name__ == '__main__':
    unittest.main()
