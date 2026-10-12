import hashlib
import json
from pathlib import Path
import unittest

from scripts.plot_conservative_prefixes import ROOT, plot_data, quantile


class PrefixFigureDataTests(unittest.TestCase):
    def test_quantiles_are_control_values_without_observed_shift(self):
        self.assertAlmostEqual(quantile([-.1, 0, .1], .025), -.095)
        self.assertAlmostEqual(quantile([-.1, 0, .1], .975), .095)
        self.assertIsNone(quantile([], .025))

    def test_primary_point_units_counts_and_source_identity(self):
        raw = (ROOT / 'research/transliteration/conservative_prefixes.json').read_bytes()
        report = json.loads(raw)
        catalog = json.loads((ROOT / 'data/transliterations.json').read_text())
        hashes = {source['id']: source['sha256'] for source in catalog['sources']}
        data = plot_data(report, hashlib.sha256(raw).hexdigest(), hashes, 'split')
        point = next(point for point in data['points'] if point['source_id'] == 'ZL3b' and
                     point['source_currier_label'] == 'A' and not point['source_paragraph_start'] and
                     point['boundary'] == 'first' and point['feature'] == 'literal_q_prefix')
        self.assertEqual(data['selected_loci'], 2907)
        self.assertEqual(point['loci'], 929)
        self.assertAlmostEqual(point['observed_percentage_points'], 6.105493)
        with self.assertRaisesRegex(ValueError, 'source hash'):
            plot_data(report, 'synthetic', {**hashes, 'ZL3b': 'changed'}, 'split')


if __name__ == '__main__':
    unittest.main()
