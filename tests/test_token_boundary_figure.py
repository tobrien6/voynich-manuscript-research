from contextlib import redirect_stderr
from copy import deepcopy
import hashlib
import io
from pathlib import Path
import struct
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from scripts.audit_eva_token_coverage import encoded, load_json
from scripts.plot_token_boundary_concordance import (
    FIGURES, REPORT, REPORT_SHA256, ROOT, STEM, figure_data, main,
)
from scripts.token_boundary_concordance import key_set


class BoundaryFigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = load_json(REPORT.read_bytes())

    def test_exact_source_counts_cohort_and_exported_values(self):
        expected = figure_data(self.report, REPORT_SHA256)
        provenance = load_json((FIGURES / (STEM + '.json')).read_bytes())
        self.assertEqual(encoded(expected), encoded({k: v for k, v in provenance.items()
                                                    if k not in ('renderer', 'output_sha256')}))
        self.assertEqual([list(row['category_counts'].values()) for row in expected['rows']],
                         [[1492, 562, 886], [1287, 767, 886]])
        self.assertEqual((expected['selected_native_loci'], expected['excluded_candidate_loci'],
                          expected['boundary_disagreements_under_both_policies']), (2940, 944, 359))
        self.assertEqual(hashlib.sha256(REPORT.read_bytes()).hexdigest(), REPORT_SHA256)

    def test_boolean_counts_and_overlapping_or_missing_categories_are_rejected(self):
        for mutation in ('boolean', 'overlap', 'missing'):
            report = deepcopy(self.report)
            groups = report['cross_source']['split']['category_key_sets']
            if mutation == 'boolean':
                groups['different_chains']['native_locus_count'] = True
            elif mutation == 'overlap':
                groups['different_chains'] = deepcopy(groups['same_chain_same_boundaries'])
            else:
                del groups['different_chains']
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                figure_data(report, REPORT_SHA256)

    def test_same_count_different_chain_identities_across_policies_are_rejected(self):
        report = deepcopy(self.report)
        groups = report['cross_source']['join']['category_key_sets']
        a = set(groups['different_chains']['native_locus_keys'])
        b = set(groups['same_chain_same_boundaries']['native_locus_keys'])
        left, right = sorted(a)[0], sorted(b)[0]
        groups['different_chains'] = key_set((a - {left}) | {right})
        groups['same_chain_same_boundaries'] = key_set((b - {right}) | {left})
        with self.assertRaisesRegex(ValueError, 'different-chain key identities'):
            figure_data(report, REPORT_SHA256)

    def test_persistent_intersection_is_verified(self):
        report = deepcopy(self.report)
        keys = report['cross_source_boundary_disagreements_under_both_policies']['native_locus_keys']
        report['cross_source_boundary_disagreements_under_both_policies'] = key_set(keys[1:])
        with self.assertRaisesRegex(ValueError, 'intersection'):
            figure_data(report, REPORT_SHA256)

    def test_exports_hash_dimensions_and_safe_svg_references(self):
        provenance = load_json((FIGURES / (STEM + '.json')).read_bytes())
        for ext in ('png', 'svg'):
            raw = (FIGURES / (STEM + '.' + ext)).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), provenance['output_sha256'][ext])
        png = (FIGURES / (STEM + '.png')).read_bytes()
        self.assertEqual(png[:8], bytes([137, 80, 78, 71, 13, 10, 26, 10]))
        self.assertEqual(struct.unpack('>II', png[16:24]), (1920, 1200))
        svg = (FIGURES / (STEM + '.svg')).read_text()
        self.assertNotIn('/Users/', svg)
        self.assertNotIn('file://', svg)
        tree = ET.fromstring(svg)
        self.assertFalse(any(node.tag.endswith('image') for node in tree.iter()))
        self.assertTrue(all(not k.endswith('href') or value.startswith('#')
                            for node in tree.iter() for k, value in node.attrib.items()))
        self.assertEqual(hashlib.sha256((ROOT / 'scripts/plot_token_boundary_concordance.py').read_bytes()).hexdigest(),
                         provenance['renderer']['script_sha256'])

    def test_output_guard_precedes_producer_and_renderer(self):
        with patch('sys.argv', ['plot', '--output-dir', str(ROOT / 'scripts')]), \
                patch('scripts.plot_token_boundary_concordance.build', side_effect=AssertionError('must not run')) as producer, \
                patch('scripts.plot_token_boundary_concordance.render', side_effect=AssertionError('must not run')) as renderer, \
                redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            main()
        producer.assert_not_called()
        renderer.assert_not_called()


if __name__ == '__main__':
    unittest.main()
