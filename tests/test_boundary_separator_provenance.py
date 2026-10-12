from contextlib import redirect_stderr
import hashlib
import io
import itertools
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.boundary_separator_provenance import (
    INPUTS, MARKERS, PLAN, ROOT, build, differences, endpoint, main, pinned_inputs, tokens, trace,
)


class SeparatorTraceTests(unittest.TestCase):
    def test_all_marker_sequences_reproduce_exact_plain_token_partitions(self):
        count = 0
        for length in range(1, 6):
            for markers in itertools.product(MARKERS, repeat=length - 1):
                pieces = ['aB'] * length
                text = pieces[0] + ''.join(marker + piece for marker, piece in zip(markers, pieces[1:]))
                row = trace(text)
                self.assertEqual(row['chain'], ''.join(pieces))
                self.assertEqual(tokens(row, 'split'), pieces)
                expected, pending = [], pieces[0]
                for marker, piece in zip(markers, pieces[1:]):
                    if marker == ',':
                        pending += piece
                    else:
                        expected.append(pending)
                        pending = piece
                expected.append(pending)
                self.assertEqual(tokens(row, 'join'), expected)
                for index, event in enumerate(row['events']):
                    self.assertEqual(event['ascii_offset'], (index + 1) * 2)
                    self.assertEqual(text[event['raw_locus_start']:event['raw_locus_end_exclusive']], markers[index])
                count += 1
        self.assertEqual(count, 341)

    def test_comments_tags_paragraph_annotations_and_whitespace_are_not_spaces(self):
        text = '<%><@P=A>a<! x., y>a , \tB<~>c<$>'
        row = trace(text)
        self.assertEqual(row['chain'], 'aaBc')
        self.assertEqual(tokens(row, 'split'), ['aa', 'B', 'c'])
        self.assertEqual(tokens(row, 'join'), ['aaB', 'c'])
        self.assertEqual([e['native_marker'] for e in row['events']], [',', '<~>'])
        self.assertEqual(endpoint(row, 1)['native_marker'], None)
        self.assertEqual(endpoint(row, 1)['neighbor_letter_raw_positions'], [text.index('a<!'), text.index('a ,')])
        self.assertEqual(row['raw_locus_sha256'], hashlib.sha256(text.encode('ascii')).hexdigest())

    def test_unsupported_malformed_or_invalid_boundaries_fail_closed(self):
        for text in ('', '<%>', '.ab', 'ab,', 'ab.<! ignored >,cd', 'ab<->.cd',
                     'a[bc:d]', 'a?', 'a@123;', 'a{bc}', "a'b", 'a<unknown>b', 'a<! unclosed'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                trace(text)
        with self.assertRaises(ValueError):
            tokens(trace('ab'), 'invalid')
        for offset in (0, 2):
            with self.assertRaises(ValueError):
                endpoint(trace('ab'), offset)

    def test_all_native_marker_and_absence_pairs_keep_every_policy_difference(self):
        count = 0
        for left_marker, right_marker in itertools.product(('', *MARKERS), repeat=2):
            left, right = trace('ab' + left_marker + 'cd'), trace('ab' + right_marker + 'cd')
            actual = differences(left, right)
            expected = [policy for policy in ('split', 'join')
                        if bool(left_marker and (policy == 'split' or left_marker != ',')) !=
                        bool(right_marker and (policy == 'split' or right_marker != ','))]
            self.assertEqual(len(actual), bool(expected))
            if expected:
                self.assertEqual(actual[0]['disagreement_policies'], expected)
                self.assertEqual(actual[0]['left']['native_marker'], left_marker or None)
                self.assertEqual(actual[0]['right']['native_marker'], right_marker or None)
                self.assertEqual(actual[0]['ascii_offset'], 2)
            count += 1
        self.assertEqual(count, 25)

    def test_different_encoded_chains_are_never_aligned(self):
        with self.assertRaisesRegex(ValueError, 'different chains'):
            differences(trace('ab.cd'), trace('AB.cd'))


class SeparatorGuardTests(unittest.TestCase):
    def test_dropped_frozen_input_fails_before_reading_or_replay(self):
        plan = json.loads((ROOT / PLAN).read_bytes())
        plan['input_sha256'].pop('scripts/ivtff.py')
        with patch('scripts.boundary_separator_provenance.load_json', return_value=plan), \
                patch('scripts.boundary_separator_provenance.build_parent', side_effect=AssertionError('must not run')) as producer, \
                self.assertRaisesRegex(ValueError, 'frozen input set changed'):
            pinned_inputs()
        producer.assert_not_called()

    def test_frozen_input_drift_stops_before_parent_replay(self):
        with patch('scripts.boundary_separator_provenance.sha', return_value='changed'), \
                patch('scripts.boundary_separator_provenance.build_parent', side_effect=AssertionError('must not run')) as producer, \
                self.assertRaisesRegex(ValueError, 'frozen separator input changed'):
            pinned_inputs()
        producer.assert_not_called()

    def test_git_blob_drift_stops_before_parent_replay(self):
        with patch('scripts.boundary_separator_provenance.subprocess.check_output', return_value=b'changed fixture'), \
                patch('scripts.boundary_separator_provenance.build_parent', side_effect=AssertionError('must not run')) as producer, \
                self.assertRaisesRegex(ValueError, 'Git blob differs'):
            pinned_inputs()
        producer.assert_not_called()

    def test_initial_output_alias_stops_before_measurement(self):
        with patch('sys.argv', ['separators', '--output', str(ROOT / PLAN)]), \
                patch('scripts.boundary_separator_provenance.build', side_effect=AssertionError('must not run')) as producer, \
                redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            main()
        producer.assert_not_called()

    def test_late_serialization_aliases_preserve_temporary_parent_fixture(self):
        for alias_kind in ('symlink', 'hardlink'):
            with self.subTest(alias_kind=alias_kind), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / 'data').mkdir()
                (root / 'data/transliterations.json').write_text('{"sources":[]}')
                parent = root / INPUTS[0]
                parent.parent.mkdir(parents=True)
                parent.write_bytes(b'unchanged public parent fixture')
                output = root / 'output.json'

                def serialization(value):
                    output.symlink_to(parent) if alias_kind == 'symlink' else os.link(parent, output)
                    return b'{}'

                with patch('sys.argv', ['separators', '--output', str(output)]), \
                        patch('scripts.boundary_separator_provenance.ROOT', root), \
                        patch('scripts.boundary_separator_provenance.build', return_value={}), \
                        patch('scripts.boundary_separator_provenance.encoded', side_effect=serialization), \
                        redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    main()
                self.assertEqual(parent.read_bytes(), b'unchanged public parent fixture')


class NativeSeparatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((ROOT / 'research/transliteration/boundary_separator_provenance.json').read_bytes())

    def test_entire_committed_inventory_matches_complete_pinned_replay(self):
        self.assertEqual(build(), self.report)
        self.assertEqual(self.report['source_internal_validation']['source_policy_token_arrays'], 11760)
        self.assertEqual(self.report['union_disagreement_offset_count'], 1458)
        self.assertEqual(self.report['union_disagreement_locus_count'], 970)
        self.assertEqual(self.report['different_chain_unaligned']['native_locus_count'], 886)
        self.assertFalse(self.report['verified_glyph_regions'])
        self.assertFalse(self.report['source_corrections_applied'])

    def test_known_native_cases_retain_opposite_directions_uncertainty_and_drawings(self):
        expected = {
            'f67r1.1': [(45, '.', None, ['split', 'join'])],
            'f102r1.14': [(38, '.', None, ['split', 'join'])],
            'f102r1.15': [(39, None, '.', ['split', 'join'])],
            'f100r.24': [(28, ',', None, ['split']), (37, None, '.', ['split', 'join'])],
            'f13v.8': [(30, ',', '<->', ['join'])],
            'f75r.44': [(48, '<->', None, ['split', 'join'])],
        }
        for key, cases in expected.items():
            row = next(r for r in self.report['records'] if r['native_locus_key'] == key)
            actual = [(r['ascii_offset'], r['left']['native_marker'], r['right']['native_marker'],
                       r['disagreement_policies']) for r in row['offset_records']]
            if key in ('f13v.8', 'f75r.44'):
                self.assertTrue(all(case in actual for case in cases))
            else:
                self.assertEqual(actual, cases)

    def test_all_output_raw_ranges_and_neighbor_letters_match_public_physical_lines(self):
        sources = {source['id']: (ROOT / source['path']).read_text('ascii').splitlines()
                   for source in self.report['sources']}
        total = 0
        for row in self.report['records']:
            for side, source in (('left', 'ZL3b'), ('right', 'IT2a')):
                identity = row[source]
                line = sources[source][identity['source_file_first_line'] - 1]
                self.assertTrue(line.startswith('<' + identity['locus_identifier'] + '>'))
                text = line.split('>', 1)[1].strip()
                # Both pinned inputs have no continuation lines. The producer
                # still names offsets in assembled logical text for future files.
                self.assertFalse(text.endswith('/'))
                self.assertEqual(hashlib.sha256(text.encode('ascii')).hexdigest(), identity['raw_locus_text_sha256'])
                for offset in row['offset_records']:
                    info = offset[side]
                    a, b = info['neighbor_letter_raw_positions']
                    self.assertTrue(text[a].isascii() and text[a].isalpha())
                    self.assertTrue(text[b].isascii() and text[b].isalpha())
                    if info['native_marker'] is None:
                        self.assertIsNone(info['raw_locus_separator_range'])
                    else:
                        start, end = info['raw_locus_separator_range']
                        self.assertEqual(text[start:end], info['native_marker'])
                        self.assertTrue(a < start < end <= b)
                    total += 1
        self.assertEqual(total, 2916)


if __name__ == '__main__':
    unittest.main()
