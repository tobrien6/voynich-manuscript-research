from contextlib import redirect_stderr
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.audit_eva_token_coverage import encoded
from scripts.boundary_disagreement_spans import PARENT, ROOT, build, main, spans


def partition(chain, cuts):
    edges = [0, *sorted(cuts), len(chain)]
    return [chain[a:b] for a, b in zip(edges, edges[1:])]


class BoundarySpanTests(unittest.TestCase):
    def test_singletons_agreement_and_different_case_or_chain(self):
        self.assertEqual(spans(['abc'], ['abc']), [])
        self.assertEqual(spans(['a', 'bc'], ['a', 'bc']), [])
        for left, right in ((['Ab'], ['ab']), (['a'], ['b']), ([], ['a']), (['a?'], ['a'])):
            with self.subTest(left=left, right=right), self.assertRaises(ValueError):
                spans(left, right)

    def test_context_is_cut_at_shared_boundaries_without_partial_tokens(self):
        result = spans(['ab', 's', 'or', 'cd'], ['ab', 'sor', 'cd'])
        self.assertEqual(len(result), 1)
        row = result[0]
        self.assertEqual((row['start_ascii_offset'], row['end_ascii_offset_exclusive'], row['span_ascii']),
                         (2, 5, 'sor'))
        self.assertEqual(row['left_original_token_parts'], ['s', 'or'])
        self.assertEqual(row['right_original_token_parts'], ['sor'])
        self.assertEqual(row['left_only_internal_ascii_offsets'], [3])
        self.assertEqual(row['left_minus_right_native_token_count'], 1)

    def test_both_sources_can_have_unique_cuts_in_one_zero_delta_span(self):
        row = spans(['ab', 'cd'], ['a', 'bcd'])[0]
        self.assertEqual(row['category'], 'both_sources_internal_cuts')
        self.assertEqual(row['left_only_internal_ascii_offsets'], [2])
        self.assertEqual(row['right_only_internal_ascii_offsets'], [1])
        self.assertEqual(row['left_minus_right_native_token_count'], 0)

    def test_equal_locus_counts_can_cancel_across_two_opposite_spans(self):
        result = spans(['a', 'b', 'cd'], ['ab', 'c', 'd'])
        self.assertEqual([r['span_ascii'] for r in result], ['ab', 'cd'])
        self.assertEqual([r['left_minus_right_native_token_count'] for r in result], [1, -1])
        self.assertEqual([r['category'] for r in result], ['left_only_internal_cuts', 'right_only_internal_cuts'])

    def test_all_1024_pairs_of_six_letter_partitions_retain_every_exclusive_cut(self):
        chain = 'abcdef'
        partitions = [{i + 1 for i in range(5) if mask & (1 << i)} for mask in range(32)]
        for left in partitions:
            a = partition(chain, left)
            for right in partitions:
                b = partition(chain, right)
                result = spans(a, b)
                left_emitted = [x for row in result for x in row['left_only_internal_ascii_offsets']]
                right_emitted = [x for row in result for x in row['right_only_internal_ascii_offsets']]
                self.assertEqual(sorted(left_emitted), sorted(left - right))
                self.assertEqual(sorted(right_emitted), sorted(right - left))
                self.assertEqual(sum(r['left_minus_right_native_token_count'] for r in result), len(a) - len(b))
                for row in result:
                    start, end = row['start_ascii_offset'], row['end_ascii_offset_exclusive']
                    self.assertIn(start, {0, len(chain)} | (left & right))
                    self.assertIn(end, {0, len(chain)} | (left & right))
                    self.assertFalse(any(start < cut < end for cut in left & right))
                    for key, original in (('left_original_token_parts', a), ('right_original_token_parts', b)):
                        parts = row[key]
                        self.assertEqual(''.join(parts), chain[start:end])
                        self.assertTrue(any(original[i:i+len(parts)] == parts for i in range(len(original))))

    def test_complete_pinned_inventory_and_exact_known_cases(self):
        report = build()
        self.assertEqual(encoded(report), (ROOT / 'research/transliteration/boundary_disagreement_spans.json').read_bytes())
        self.assertEqual([(r['span_count'], r['disagreement_loci']['native_locus_count']) for r in report['comparisons']],
                         [(650, 562), (978, 767)])
        for comparison in report['comparisons']:
            row = next(r for r in comparison['span_records'] if r['native_locus_key'] == 'f67r1.1')
            self.assertEqual((row['start_ascii_offset'], row['end_ascii_offset_exclusive'], row['span_ascii']), (44, 49, 'oaiin'))
            self.assertEqual(row['left_original_token_parts'], ['o', 'aiin'])
            self.assertEqual(row['right_original_token_parts'], ['oaiin'])
        split = report['comparisons'][0]
        pair = [r for r in split['span_records'] if r['native_locus_key'] == 'f100r.24']
        self.assertEqual([r['span_ascii'] for r in pair], ['yksheey', 'cholsheody'])
        self.assertEqual([r['left_minus_right_native_token_count'] for r in pair], [1, -1])

    def test_late_builder_aliases_cannot_overwrite_the_parent_input(self):
        for alias in ('symlink', 'hardlink'):
            with self.subTest(alias=alias), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / 'data').mkdir()
                (root / 'data/transliterations.json').write_text('{"sources":[]}')
                source = root / PARENT
                source.parent.mkdir(parents=True)
                source.write_bytes(b'unchanged public input fixture')
                output = root / 'output.json'

                def late_builder():
                    output.symlink_to(source) if alias == 'symlink' else os.link(source, output)
                    return {'synthetic': True}

                with patch('sys.argv', ['spans', '--output', str(output)]), \
                        patch('scripts.boundary_disagreement_spans.ROOT', root), \
                        patch('scripts.boundary_disagreement_spans.build', side_effect=late_builder), \
                        redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    main()
                self.assertEqual(source.read_bytes(), b'unchanged public input fixture')

    def test_initial_implementation_guard_precedes_calculation(self):
        with patch('sys.argv', ['spans', '--output', str(ROOT / 'scripts/boundary_disagreement_spans.py')]), \
                patch('scripts.boundary_disagreement_spans.build', side_effect=AssertionError('must not run')) as producer, \
                redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            main()
        producer.assert_not_called()

    def test_serialization_aliases_are_rejected_before_writing(self):
        for alias in ('symlink', 'hardlink'):
            with self.subTest(alias=alias), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / 'data').mkdir()
                (root / 'data/transliterations.json').write_text('{"sources":[]}')
                source = root / PARENT
                source.parent.mkdir(parents=True)
                source.write_bytes(b'unchanged public input fixture')
                output = root / 'output.json'

                def late_encoding(report):
                    output.symlink_to(source) if alias == 'symlink' else os.link(source, output)
                    return b'{}'

                with patch('sys.argv', ['spans', '--output', str(output)]), \
                        patch('scripts.boundary_disagreement_spans.ROOT', root), \
                        patch('scripts.boundary_disagreement_spans.build', return_value={'synthetic': True}), \
                        patch('scripts.boundary_disagreement_spans.encoded', side_effect=late_encoding), \
                        redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    main()
                self.assertEqual(source.read_bytes(), b'unchanged public input fixture')


if __name__ == '__main__':
    unittest.main()
