import json
from pathlib import Path
import tempfile
import unittest

from scripts.audit_transliterations import ROOT, load_sources
from scripts.ivtff import parse_ivtff
from scripts.paragraph_membership import membership_report, page_units, validate_output_path


HEADER = '#=IVTFF Eva- 2.0 M\n'


def sources(left, right):
    return [({'id': identifier, 'url': 'https://example.org/' + identifier,
              'path': 'synthetic/' + identifier, 'sha256': 'synthetic', 'alphabet': 'Eva-'},
             parse_ivtff(HEADER + text))
            for identifier, text in [('ZL3b', left), ('IT2a', right)]]


class ParagraphMembershipTests(unittest.TestCase):
    def test_complete_units_include_every_p_subtype_and_single_locus_units(self):
        text = '<f1r>\n<f1r.1,@P0> <%>a\n<f1r.2,+L0> a\n<f1r.3,+Pc> a<$>\n'
        text += '<f1r.4,+Pr> <%>a<$>\n'
        report = membership_report(sources(text, text))
        units = report['sources'][0]['pages'][0]['units']
        self.assertEqual([unit['member_keys'] for unit in units], [['f1r.1', 'f1r.3'], ['f1r.4']])
        self.assertEqual(report['exact_unit_comparison']['matching_complete_unit_count'], 2)
        self.assertEqual(report['shared_locus_membership']['status_counts']['same_ordered_unit_members'], 3)

    def test_pairing_does_not_cross_pages_or_repair_anomalies(self):
        text = '<f1r>\n<f1r.1,@P0> <%>a\n<f1v>\n<f1v.1,@P0> a<$>\n'
        doc = parse_ivtff(HEADER + text)
        left = page_units('ZL3b', 'f1r', doc.loci[:1])
        right = page_units('ZL3b', 'f1v', doc.loci[1:])
        self.assertEqual(left['status'], 'anomalous')
        self.assertEqual(right['status'], 'anomalous')
        self.assertEqual(left['units'] + right['units'], [])
        self.assertEqual(left['anomalies_reasons_may_overlap'][0]['reason'], 'unit_open_at_page_end')
        self.assertEqual(right['anomalies_reasons_may_overlap'][0]['reason'], 'end_without_open_unit')
        report = membership_report(sources(text, text))
        self.assertEqual(report['shared_locus_membership']['status_counts']['ineligible_page_annotations'], 2)

    def test_one_anomaly_withholds_the_entire_page(self):
        for text in ('<%><%>a<$>', 'a<$>', '<$><%>a', '<%>a'):
            doc = parse_ivtff(HEADER + '<f1r>\n<f1r.1,@P0> <%>a<$>\n<f1r.2,+P0> ' + text + '\n')
            with self.subTest(text=text):
                page = page_units('ZL3b', 'f1r', doc.loci)
                self.assertEqual(page['units'], [])
                self.assertEqual(page['unassigned_locus_keys'], ['f1r.1', 'f1r.2'])
                self.assertEqual(page['status'], 'anomalous')

    def test_free_comments_and_nonexistent_records_do_not_create_units(self):
        text = '<f1r>\n<f1r.1,@P0> <! <%>a<! <$>\n<f1r.2,!P0> <%>a<$>\n'
        report = membership_report(sources(text, text))
        page = report['sources'][0]['pages'][0]
        self.assertEqual(page['status'], 'unmarked')
        self.assertEqual(page['unassigned_locus_keys'], ['f1r.1'])
        self.assertEqual(len(report['sources'][0]['nonexistent_generic_p_records']), 1)
        self.assertEqual(report['shared_locus_membership']['status_counts']['ungrouped_both'], 1)

    def test_leading_and_trailing_unmarked_loci_remain_unassigned(self):
        left = '<f1r>\n<f1r.1,@P0> a\n<f1r.2,+P0> <%>a<$>\n<f1r.3,+P0> a\n'
        right = '<f1r>\n<f1r.1,@P0> <%>a<$>\n<f1r.2,+P0> a\n<f1r.3,+P0> <%>a<$>\n'
        report = membership_report(sources(left, right))
        counts = report['shared_locus_membership']['status_counts']
        self.assertEqual(counts['grouped_only_left'], 1)
        self.assertEqual(counts['grouped_only_right'], 2)
        self.assertEqual(report['sources'][0]['pages'][0]['unassigned_locus_keys'], ['f1r.1', 'f1r.3'])

    def test_split_membership_and_source_coverage_are_distinguished(self):
        joined = '<f1r>\n<f1r.1,@P0> <%>a\n<f1r.2,+P0> a\n<f1r.3,+Pc> a<$>\n'
        split = '<f1r>\n<f1r.1,@P0> <%>a\n<f1r.2,+P0> a<$>\n<f1r.3,+Pc> <%>a<$>\n'
        report = membership_report(sources(joined, split))
        comparison = report['shared_locus_membership']
        self.assertEqual(comparison['different_membership_without_unpaired_unit_members'], ['f1r.1', 'f1r.2', 'f1r.3'])
        self.assertEqual(comparison['different_membership_with_unpaired_unit_members'], [])
        partial = '<f1r>\n<f1r.1,@P0> <%>a\n<f1r.3,+Pc> a<$>\n'
        report = membership_report(sources(joined, partial))
        self.assertEqual(report['shared_locus_membership']['different_membership_with_unpaired_unit_members'], ['f1r.1', 'f1r.3'])
        exclusion = report['selection']['generic_p_records_excluded_by_intersection']['ZL3b'][0]
        self.assertEqual(exclusion['selected_source_record']['key'], 'f1r.2')
        self.assertIsNone(exclusion['other_source_record'])

    def test_anomalous_page_and_non_p_marks_are_retained(self):
        left = '<f1r>\n<f1r.1,@P0> <%>a\n<f1r.2,+L0> <%>a<$>\n'
        right = '<f1r>\n<f1r.1,@P0> <%>a<$>\n<f1r.2,+L0> a\n'
        report = membership_report(sources(left, right))
        self.assertEqual(report['shared_locus_membership']['status_counts']['ineligible_page_annotations'], 1)
        self.assertEqual(report['sources'][0]['paragraph_marks_on_present_non_p_loci'][0]['key'], 'f1r.2')

    def test_output_guards_reject_sources_catalog_and_resolved_aliases(self):
        for path in (ROOT / 'data/transliterations.json', ROOT / 'data/raw/report.json',
                     ROOT / 'research/transliteration/PARAGRAPH_MEMBERSHIP_PLAN.md',
                     ROOT / 'scripts/ivtff.py'):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'overwrite'):
                validate_output_path(path)
        with tempfile.TemporaryDirectory() as directory:
            alias = Path(directory) / 'alias.json'
            alias.symlink_to(ROOT / 'data/transliterations.json')
            with self.assertRaisesRegex(ValueError, 'overwrite'):
                validate_output_path(alias)

    def test_pinned_report_reproduces_and_every_shared_key_is_accounted_for(self):
        loaded = load_sources()
        report = membership_report(loaded)
        expected = json.loads((ROOT / 'research/transliteration/paragraph_membership.json').read_text())
        self.assertEqual(report, expected)
        pair_only = [item for item in loaded if item[0]['id'] in {'ZL3b', 'IT2a'}]
        self.assertEqual(membership_report(pair_only), report)
        self.assertEqual(membership_report(list(reversed(loaded))), report)
        comparison = report['shared_locus_membership']
        all_keys = [key for keys in comparison['status_locus_keys'].values() for key in keys]
        self.assertEqual(len(all_keys), len(set(all_keys)))
        self.assertEqual(len(all_keys), 4118)
        self.assertEqual(sum(comparison['status_counts'].values()), 4118)
        for source in report['sources']:
            summary = source['summary']
            self.assertEqual(summary['assigned_locus_count'] + summary['unassigned_locus_count'], summary['present_generic_p_loci'])


if __name__ == '__main__':
    unittest.main()
