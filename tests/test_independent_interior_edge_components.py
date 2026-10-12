from fractions import Fraction
import gzip
import itertools
import json
from pathlib import Path
import tempfile
import unittest

from scripts import verify_interior_edge_components as m


class IndependentComponentTests(unittest.TestCase):
    def test_plain_and_lossless_compressed_transport_have_identical_records(self):
        with tempfile.TemporaryDirectory() as folder:
            plain = Path(folder) / 'report.json'
            zipped = Path(folder) / 'report.json.gz'
            raw = b'{"exact":["7","3"],"zero":0,"flag":false}\n'
            plain.write_bytes(raw)
            zipped.write_bytes(gzip.compress(raw, mtime=0))
            self.assertEqual(gzip.decompress(zipped.read_bytes()), raw)
            self.assertEqual(m.read_report(plain), m.read_report(zipped))
            self.assertEqual(m.read_report(zipped), json.loads(raw))
            zipped.write_bytes(zipped.read_bytes()[:15])
            with self.assertRaises((EOFError, OSError)):
                m.read_report(zipped)

    def test_ordered_pair_oracle_matches_occurrence_enumeration(self):
        for values in ([1, 3, 2], [1, 1, 4, 2], [1, 3, 2, 5, 2], [1, 4, 2, 3, 1, 6], [3, 3, 3]):
            expected = m.literal_components(values)
            cut = (len(values) + 1) // 2
            for scope, orders in (
                ('unrestricted', itertools.permutations(values)),
                ('half', (a + b for a, b in itertools.product(
                    itertools.permutations(values[:cut]), itertools.permutations(values[cut:]))))):
                outcomes = [m.literal_components(order)['raw'] for order in orders]
                actual = [sum((row[i] for row in outcomes), Fraction()) / len(outcomes) for i in range(3)]
                self.assertEqual(actual, expected[scope + '_expectation'])
        self.assertEqual(m.direct_pairs([Fraction(2)], [Fraction(2)], True), 0)
        self.assertEqual(m.direct_pairs([Fraction(2)], [Fraction(-3)], False), -6)

    def test_literal_scanner_retains_longest_match_case_and_fallback(self):
        patterns = ['ch', 'cth', 'iin', 'ii']
        self.assertEqual(m.count('cthchiin', patterns), 3)
        self.assertEqual(m.count('CTHchii', patterns), 5)
        self.assertEqual(m.count('cthchiin', []), 8)

    def test_independent_cohort_preserves_all_reasons_and_unshared_gaps(self):
        def row(**changes):
            return {'locus_type': 'P0', 'exclusion_reasons': [], 'eligible': True,
                    'drawing_interruption_count': 0, 'token_count': 5, **changes}
        mappings = {identity: {'keep': row(), 'drawing': row(drawing_interruption_count=1),
                              'short': row(token_count=4),
                              'ambiguous': row(exclusion_reasons=['unreadable'], eligible=False),
                              'wrongkind': row(locus_type='L0'),
                              'nonexistent': row(exclusion_reasons=['nonexistent_locus'], eligible=False)}
                    for identity in m.VARIANTS}
        mappings[m.VARIANTS[0]]['unshared'] = row()
        selected = m.independent_selection(mappings)
        self.assertEqual(selected['shared_present_P0_loci'], 4)
        self.assertEqual(selected['eligible_in_all_adapters'], 3)
        self.assertEqual(selected['eligible_after_drawing_exclusion'], 2)
        self.assertEqual(selected['retained_locus_keys'], ['keep'])
        self.assertEqual(selected['excluded_loci'], 3)
        self.assertEqual([e['locus_key'] for e in selected['exclusions']], ['ambiguous', 'drawing', 'short'])
        for entry, suffix in zip(selected['exclusions'], ('unreadable', 'drawing_interruption', 'fewer_than_five_tokens')):
            self.assertEqual(entry['reasons'], sorted(s + '/' + p + ':' + suffix for s, p in m.VARIANTS))


if __name__ == '__main__':
    unittest.main()
