from dataclasses import replace
import json
import unittest

from scripts.annotation_agreement import annotations, annotation_report
from scripts.audit_transliterations import ROOT, load_sources
from scripts.ivtff import parse_ivtff


HEADER = '#=IVTFF Eva- 2.0 M\n'


def sources(left, right):
    return [({'id': identifier, 'url': 'https://example.org/' + identifier,
              'path': 'synthetic/' + identifier, 'sha256': 'synthetic', 'alphabet': 'Eva-'},
             parse_ivtff(HEADER + text))
            for identifier, text in [('ZL3b', left), ('IT2a', right)]]


class AnnotationAgreementTests(unittest.TestCase):
    def test_comment_marks_do_not_change_boundary_presence_or_count(self):
        doc = parse_ivtff(HEADER + '<f1r>\n<f1r.1,@P0> <! <%>a<! <$>\n'
                          '<f1r.2,+P0> <%>a<$>\n')
        first, second = map(annotations, doc.loci)
        self.assertEqual((first['start_marker_count'], first['end_marker_count']), (0, 0))
        self.assertEqual((second['paragraph_start'], second['paragraph_end']), (True, True))

    def test_confusion_cells_include_zero_and_directional_disagreements(self):
        report = annotation_report(sources(
            '<f1r>\n<f1r.1,@P0> <%>a\n<f1r.2,+P0> a\n',
            '<f1r>\n<f1r.1,@P0> a\n<f1r.2,+P0> <%>a\n'))
        start = report['cohorts']['shared_present_p0']['comparisons'][0]
        self.assertEqual(start['disagreement_count'], 2)
        self.assertEqual([cell['count'] for cell in start['cells']], [0, 1, 1, 0])
        self.assertEqual([row['key'] for row in report['discordant_loci']], ['f1r.1', 'f1r.2'])
        self.assertEqual(report['discordant_loci'][0]['left']['file_line_number'], 3)

    def test_effective_labels_preserve_missing_and_unknown_values(self):
        report = annotation_report(sources(
            '<f1r> <! $L=@>\n<f1r.1,@P0> <@L=C>a\n<f1r.2,+P0> a\n'
            '<f1v>\n<f1v.1,@P0> a\n',
            '<f1r> <! $L=B>\n<f1r.1,@P0> a\n<f1r.2,+P0> a\n'
            '<f1v> <! $L=A>\n<f1v.1,@P0> a\n'))
        rows = report['discordant_loci']
        self.assertEqual([row['left']['currier_label'] for row in rows], ['C', 'C', None])
        labels = report['cohorts']['shared_present_p0']['comparisons'][2]
        self.assertEqual(labels['disagreement_count'], 3)
        self.assertEqual(sum(cell['count'] for cell in labels['cells']), 3)

    def test_intersection_and_joint_locator_filter_keep_exclusions_explicit(self):
        report = annotation_report(sources(
            '<f1r>\n<f1r.1,@P0> a\n<f1r.2,+P0> a\n<f1r.3,+P0> a\n'
            '<f1r.4,!P0> a\n<f1r.5,+P0> a\n',
            '<f1r>\n<f1r.1,@P0> a\n<f1r.2,=P0> a\n<f1r.3,+P1> a\n'
            '<f1r.4,+P0> a\n'))
        self.assertEqual(report['selection']['source_present_p0_counts'], {'ZL3b': 4, 'IT2a': 3})
        self.assertEqual(report['selection']['present_p0_keys_excluded_by_intersection'],
                         {'ZL3b': ['f1r.3', 'f1r.5'], 'IT2a': ['f1r.4']})
        self.assertEqual(report['selection']['shared_p0_keys_excluded_by_locator_rule'], ['f1r.2'])
        self.assertEqual(report['cohorts']['shared_regular_p0']['selected_loci'], 1)
        self.assertFalse(report['discordant_loci'][0]['in_regular_cohort'])

    def test_repeated_markers_are_visible_even_when_boolean_presence_agrees(self):
        report = annotation_report(sources(
            '<f1r>\n<f1r.1,@P0> <%><%>a<$>\n',
            '<f1r>\n<f1r.1,@P0> <%>a<$>\n'))
        start = report['cohorts']['shared_present_p0']['comparisons'][0]
        self.assertEqual(start['disagreement_count'], 0)
        self.assertEqual(report['discordant_loci'][0]['discordant_fields'], ['start_marker_count'])
        self.assertEqual(len(report['repeated_marker_loci']), 1)

    def test_empty_regular_cohort_is_reported_without_inventing_a_rate(self):
        text = '<f1r>\n<f1r.1,=P0> a\n'
        report = annotation_report(sources(text, text))
        regular = report['cohorts']['shared_regular_p0']
        self.assertEqual(regular['selected_loci'], 0)
        self.assertIsNone(regular['comparisons'][0]['disagreement_fraction'])
        self.assertEqual([cell['count'] for cell in regular['comparisons'][0]['cells']], [0] * 4)

    def test_missing_pair_duplicate_keys_and_no_shared_p0_fail(self):
        text = '<f1r>\n<f1r.1,@P0> a\n'
        paired = sources(text, text)
        with self.assertRaisesRegex(ValueError, 'exactly one pinned IT2a'):
            annotation_report(paired[:1])
        source, doc = paired[0]
        duplicated = (source, replace(doc, loci=doc.loci + doc.loci))
        with self.assertRaisesRegex(ValueError, 'unique non-interlinear'):
            annotation_report([duplicated, paired[1]])
        with self.assertRaisesRegex(ValueError, 'no shared present P0'):
            annotation_report(sources(text, '<f1r>\n<f1r.1,@P1> a\n'))

    def test_pinned_inputs_reproduce_report_and_unrelated_editions_are_ignored(self):
        loaded = load_sources()
        report = annotation_report(loaded)
        committed = json.loads((ROOT / 'research/transliteration/annotation_agreement.json').read_text())
        self.assertEqual(report, committed)
        self.assertEqual(annotation_report(loaded[:2]), report)
        self.assertEqual(report['cohorts']['shared_present_p0']['selected_loci'], 3884)
        self.assertEqual(report['cohorts']['shared_regular_p0']['selected_loci'], 3848)


if __name__ == '__main__':
    unittest.main()
