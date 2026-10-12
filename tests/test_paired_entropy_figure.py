from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
import unittest

from scripts.plot_paired_entropy import REPORT, REPORT_SHA256, STEM, figure_data, load_report, protect_targets, write_artifacts


class PairedEntropyFigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(REPORT.read_bytes())

    def test_all_24_points_preserve_the_accepted_values_and_denominators(self):
        data = load_report(REPORT)
        self.assertEqual(data['selected_loci'], 2485)
        self.assertEqual(len(data['points']), 24)
        lookup = {(row['source_id'], row['spacing'], row['unit_policy'], row['boundary_policy']): row
                  for row in self.report['treatments']}
        for point in data['points']:
            row = lookup[point['source_id'], point['spacing'], point['unit_policy'], point['boundary_policy']]
            self.assertEqual(point['conditional_successor_bits'], row['bits']['conditional_successor_entropy'])
            self.assertEqual(point['full_marginal_shift_bits'], row['bits']['difference_due_to_full_marginal'])
            self.assertEqual(point['edge_count'], row['edge_count'])

    def test_missing_duplicate_or_changed_cohort_treatments_are_rejected(self):
        for change in ('missing', 'duplicate', 'cohort', 'pin', 'nonfinite'):
            altered = deepcopy(self.report)
            if change == 'missing': altered['treatments'].pop()
            elif change == 'duplicate': altered['treatments'].append(deepcopy(altered['treatments'][0]))
            elif change == 'cohort': altered['treatments'][0]['loci'] -= 1
            elif change == 'pin': altered['treatments'][0]['source_sha256'] = '0'*64
            else: altered['treatments'][0]['bits']['conditional_successor_entropy'] = float('nan')
            with self.subTest(change=change), self.assertRaises(ValueError):
                figure_data(altered, REPORT_SHA256)

    def test_changed_report_bytes_are_not_silently_rebound(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'report.json'
            path.write_bytes(REPORT.read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError, 'report bytes changed'):
                load_report(path)

    def test_output_aliases_preserve_the_input_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root/'input.json'
            source.write_bytes(b'synthetic report fixture')
            before = source.read_bytes()
            alias = root/(STEM+'.png')
            os.link(source, alias)
            with self.assertRaisesRegex(ValueError, 'aliases'):
                protect_targets(root, source)
            self.assertEqual(source.read_bytes(), before)
            self.assertEqual(alias.read_bytes(), before)

    def test_artifact_paths_cannot_share_an_existing_inode(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            png = root/(STEM+'.png')
            svg = root/(STEM+'.svg')
            png.write_bytes(b'synthetic artifact fixture')
            os.link(png, svg)
            with self.assertRaisesRegex(ValueError, 'distinct'):
                protect_targets(root, REPORT)
            self.assertEqual(png.read_bytes(), b'synthetic artifact fixture')

    def test_cataloged_source_aliases_are_protected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            catalog = root/'data/transliterations.json'
            catalog.parent.mkdir()
            raw = root/'data/source.txt'
            raw.write_bytes(b'original synthetic source')
            catalog.write_text(json.dumps({'sources':[{'path':'data/source.txt'}]}))
            os.link(raw, root/(STEM+'.svg'))
            with self.assertRaisesRegex(ValueError, 'aliases'):
                protect_targets(root, REPORT, root=root)
            self.assertEqual(raw.read_bytes(), b'original synthetic source')

    def test_alias_created_after_initial_check_is_rejected_before_artifact_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root/'input.json'
            source.write_bytes(b'original synthetic report')
            protect_targets(root, source)
            os.link(source, root/(STEM+'.svg'))
            with self.assertRaisesRegex(ValueError, 'aliases'):
                write_artifacts([b'png', b'svg', b'json'], root, source)
            self.assertEqual(source.read_bytes(), b'original synthetic report')
            self.assertFalse((root/(STEM+'.png')).exists())


if __name__ == '__main__':
    unittest.main()
