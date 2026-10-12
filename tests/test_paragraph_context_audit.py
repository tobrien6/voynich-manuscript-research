from copy import deepcopy
import json
import unittest

from scripts.audit_transliterations import ROOT, load_sources
from scripts.paragraph_context_audit import context_report, separate_centered_locus_source
from test_annotation_agreement import sources


class ParagraphContextAuditTests(unittest.TestCase):
    def test_centered_context_counts_both_directions(self):
        joined = '<f1r>\n<f1r.1,@P0> <%>a\n<f1r.2,+Pc> a<$>\n'
        separate = '<f1r>\n<f1r.1,@P0> <%>a<$>\n<f1r.2,+Pc> <%>a<$>\n'
        for left, right, identifier in [(joined, separate, 'IT2a'), (separate, joined, 'ZL3b')]:
            report = context_report(sources(left, right))
            with self.subTest(identifier=identifier):
                summary = report['centered_locus_context_summary']
                self.assertEqual(summary['p0_end_disagreement_denominator'], 1)
                self.assertEqual(summary['matching_context_count_by_source_marking_separate_centered_locus'][identifier], 1)
                self.assertEqual(summary['other_context_count'], 0)
                self.assertEqual(len(report['discordant_loci']), 2)

    def test_changed_next_key_subtype_or_marker_count_is_not_a_match(self):
        joined = '<f1r>\n<f1r.1,@P0> <%>a\n<f1r.2,+Pc> a<$>\n'
        separate = '<f1r>\n<f1r.1,@P0> <%>a<$>\n<f1r.2,+Pc> <%>a<$>\n'
        context = context_report(sources(joined, separate))['shared_p0_end_disagreement_contexts'][0]
        for field, value in [('key', 'f1r.3'), ('kind', 'Pr'), ('start_marker_count', 2), ('end_marker_count', 0)]:
            following = deepcopy(context['next_present_generic_p_on_same_page'])
            following['right'][field] = value
            with self.subTest(field=field):
                self.assertIsNone(separate_centered_locus_source(context['current'], following, ['ZL3b', 'IT2a']))

    def test_next_locus_cannot_cross_page_or_skip_generic_p(self):
        report = context_report(sources(
            '<f1r>\n<f1r.1,@P0> a\n<f1v>\n<f1v.1,@Pc> a<$>\n',
            '<f1r>\n<f1r.1,@P0> a<$>\n<f1v>\n<f1v.1,@Pc> <%>a<$>\n'))
        context = report['shared_p0_end_disagreement_contexts'][0]
        self.assertEqual(context['next_present_generic_p_on_same_page'], {'left': None, 'right': None})
        report = context_report(sources(
            '<f1r>\n<f1r.1,@P0> a\n<f1r.2,+Pr> a\n<f1r.3,+Pc> a<$>\n',
            '<f1r>\n<f1r.1,@P0> a<$>\n<f1r.2,+Pr> a\n<f1r.3,+Pc> <%>a<$>\n'))
        self.assertEqual(report['centered_locus_context_summary']['other_context_count'], 1)
        self.assertEqual(report['shared_p0_end_disagreement_contexts'][0]['next_present_generic_p_on_same_page']['left']['key'], 'f1r.2')

    def test_subtype_changes_and_intersection_exclusions_are_retained(self):
        report = context_report(sources(
            '<f1r>\n<f1r.1,@P0> a\n<f1r.2,+Pc> a\n<f1r.3,+Pr> a\n',
            '<f1r>\n<f1r.1,@P1> a\n<f1r.2,+Pc> a\n<f1r.3,+L0> a\n'))
        self.assertEqual(report['shared_generic_p_annotations']['selected_loci'], 2)
        self.assertEqual(report['discordant_loci'][0]['discordant_fields'], ['kind'])
        self.assertEqual(report['selection']['present_generic_p_keys_excluded_by_intersection'],
                         {'ZL3b': ['f1r.3'], 'IT2a': []})
        self.assertEqual(sum(pair['count'] for pair in report['subtype_pairs']), 2)

    def test_pinned_report_reproduces_without_comparator_editions(self):
        loaded = load_sources()
        report = context_report(loaded)
        expected = json.loads((ROOT / 'research/transliteration/generic_p_context.json').read_text())
        self.assertEqual(report, expected)
        self.assertEqual(context_report(loaded[:2]), report)
        summary = report['centered_locus_context_summary']
        self.assertEqual(summary['p0_end_disagreement_denominator'], 54)
        self.assertEqual(sum(summary['matching_context_count_by_source_marking_separate_centered_locus'].values())
                         + summary['other_context_count'], 54)


if __name__ == '__main__':
    unittest.main()
