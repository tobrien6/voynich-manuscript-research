import copy
import bisect
from collections import Counter
import json
from pathlib import Path
import tempfile
import unittest

from scripts.audit_self_citation_boundaries import digest, read_pins, reconstruct, write_new
from scripts.audit_self_citation_boundaries import ROOT, TRACE, REPORT


def row(index, initial, final, page, paragraph):
    return {'generated_row_index': index, 'initialized_input_row': index == 0,
            'model_paragraph_initial': initial, 'model_paragraph_final': final,
            'source_lines_in_page_pre_call': page,
            'source_lines_in_paragraph_pre_call': paragraph}


def two_pages():
    return [row(0, None, None, None, None), row(1, False, False, 2, 2),
            row(2, False, False, 3, 3), row(3, False, True, 0, 0),
            row(4, True, False, 1, 1), row(5, False, False, 2, 2),
            row(6, False, False, 3, 3), row(7, False, True, 0, 0)]


class BoundaryStateTests(unittest.TestCase):
    def test_coincident_terminal_and_page_closure_preserves_unknown_input(self):
        result = reconstruct(two_pages(), 1, 4)
        self.assertEqual(result['counts']['closure_conditions'], {
            'page_length': 1, 'terminal': 0, 'page_length_and_terminal': 1, 'threshold_branch': 0})
        self.assertEqual(result['page_block_row_count_distribution'], [{'row_count': 4, 'count': 2}])
        self.assertIsNone(result['segments'][0]['first_row_initial_call_flag'])
        self.assertEqual(result['segments'][0]['initialized_row_count'], 1)
        self.assertEqual(result['page_blocks'][1]['segment_indices'], [1])

    def test_terminal_reset_can_close_a_partial_block(self):
        rows = two_pages()[:6]
        rows[-1] = row(5, False, True, 0, 0)
        result = reconstruct(rows, 1, 4)
        self.assertEqual([page['row_count'] for page in result['page_blocks']], [4, 2])
        self.assertEqual(result['counts']['closure_conditions']['terminal'], 1)
        self.assertFalse(result['page_blocks'][-1]['page_length_reached'])

    def test_a_single_generated_row_can_be_both_initial_and_terminal(self):
        rows = two_pages()[:5]
        rows[-1] = row(4, True, True, 0, 0)
        result = reconstruct(rows, 1, 4)
        self.assertEqual(result['segments'][1]['row_count'], 1)
        self.assertTrue(result['segments'][1]['first_row_initial_call_flag'])

    def test_threshold_closure_resets_only_paragraph_before_generation(self):
        rows = [row(0, None, None, None, None), row(1, False, False, 2, 2),
                row(2, False, False, 3, 3), row(3, False, True, 4, 0),
                row(4, True, False, 5, 1), row(5, False, False, 6, 2),
                row(6, False, False, 7, 3), row(7, False, False, 8, 4),
                row(8, False, False, 9, 5), row(9, False, True, 0, 0)]
        result = reconstruct(rows, 1, 12)
        self.assertEqual(result['counts']['closure_conditions']['threshold_branch'], 1)
        self.assertEqual(result['counts']['eligible_threshold_branch_calls'], 2)
        self.assertEqual(result['counts']['eligible_threshold_branch_nonclosures'], 1)
        self.assertEqual(result['page_blocks'][0]['segment_indices'], [0, 1])
        self.assertEqual([s['row_count'] for s in result['segments']], [4, 6])
        for index in [2, 8]:
            changed = copy.deepcopy(rows)
            changed[index]['model_paragraph_final'] = True
            changed[index]['source_lines_in_paragraph_pre_call'] = 0
            with self.assertRaisesRegex(ValueError, 'flags disagree'):
                reconstruct(changed, 1, 12)

    def test_wrong_flags_and_pre_reset_counters_are_rejected(self):
        cases = [(3, 'model_paragraph_final', False), (4, 'model_paragraph_initial', False),
                 (3, 'source_lines_in_page_pre_call', 4), (3, 'source_lines_in_paragraph_pre_call', 4),
                 (2, 'model_paragraph_final', True)]
        for index, key, value in cases:
            changed = two_pages(); changed[index][key] = value
            with self.assertRaisesRegex(ValueError, 'disagree'):
                reconstruct(changed, 1, 4)

    def test_eligible_saturated_threshold_must_close(self):
        rows = [row(0, None, None, None, None)]
        rows.extend(row(index, False, False, index + 1, index + 1) for index in range(1, 9))
        rows.extend([row(9, False, True, 10, 0), row(10, True, False, 11, 1),
                     row(11, False, False, 12, 2), row(12, False, True, 0, 0)])
        result = reconstruct(rows, 1, 20)
        self.assertEqual(result['counts']['saturated_threshold_closures'], 1)
        changed = copy.deepcopy(rows)
        changed[9] = row(9, False, False, 10, 10)
        with self.assertRaisesRegex(ValueError, 'flags disagree'):
            reconstruct(changed, 1, 20)

    def test_malformed_indices_origins_metadata_and_types_are_rejected(self):
        cases = [(0, 'model_paragraph_initial', False), (1, 'generated_row_index', True),
                 (1, 'generated_row_index', 2), (1, 'initialized_input_row', True),
                 (1, 'model_paragraph_final', 0), (1, 'source_lines_in_page_pre_call', True),
                 (1, 'source_lines_in_paragraph_pre_call', -1)]
        for index, key, value in cases:
            changed = two_pages(); changed[index][key] = value
            with self.assertRaises(ValueError):
                reconstruct(changed, 1, 4)
        for rows, initial_count, page_length in [(two_pages()[1:], 1, 4), ([], 1, 4),
                                                (two_pages(), True, 4), (two_pages(), 1, True)]:
            with self.assertRaises(ValueError):
                reconstruct(rows, initial_count, page_length)

    def test_input_fingerprint_drift_fails_without_repair(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); path = root / 'synthetic.json'; path.write_bytes(b'{}\n')
            pins = {'synthetic.json': digest(path.read_bytes())}
            self.assertEqual(read_pins(root, pins), {'synthetic.json': b'{}\n'})
            path.write_bytes(b'{"changed":true}\n')
            with self.assertRaisesRegex(ValueError, 'pinned input changed'):
                read_pins(root, pins)

    def test_writer_creates_only_new_files_and_preserves_aliases(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); source = root / 'input'; source.write_bytes(b'synthetic source')
            link = root / 'symlink'; link.symlink_to(source)
            hardlink = root / 'hardlink'; hardlink.hardlink_to(source)
            for destination in [source, link, hardlink]:
                with self.assertRaises(FileExistsError):
                    write_new(destination, b'changed')
                self.assertEqual(source.read_bytes(), b'synthetic source')
            output = root / 'new'; write_new(output, b'report\n')
            self.assertEqual(output.read_bytes(), b'report\n')

    def test_actual_report_has_independent_closure_distance_and_modulo_identities(self):
        """Added after derivation; does not use the production state walk."""
        rows = json.loads((ROOT / TRACE).read_bytes())['ledger']
        report = json.loads((ROOT / REPORT).read_bytes())
        n = len(rows)
        finals = [r['generated_row_index'] for r in rows if r['model_paragraph_final'] is True]
        forced = set(range(28, n, 29))
        causes = Counter({key: 0 for key in ['page_length', 'terminal', 'page_length_and_terminal', 'threshold_branch']})
        eligible = saturated = 0
        for i in range(1, n):
            k = bisect.bisect_left(finals, i)
            previous = finals[k - 1] if k else -1
            distance = i - previous
            position = i % 29 + 1
            mandatory = i in forced or i == n - 1
            allowed = not mandatory and position < 27 and distance > 3 and i < n - 2
            eligible += allowed
            saturated += allowed and distance >= 10
            self.assertEqual(rows[i]['model_paragraph_initial'], distance == 1)
            self.assertEqual(rows[i]['source_lines_in_page_pre_call'], 0 if mandatory else position)
            self.assertEqual(rows[i]['source_lines_in_paragraph_pre_call'], 0 if i in finals else distance)
            if mandatory or (allowed and distance >= 10):
                self.assertIn(i, finals)
            if i in finals:
                self.assertTrue(mandatory or allowed)
                cause = ('page_length_and_terminal' if i in forced and i == n - 1 else
                         'page_length' if i in forced else 'terminal' if i == n - 1 else 'threshold_branch')
                causes[cause] += 1
        self.assertEqual(dict(causes), report['counts']['closure_conditions'])
        self.assertEqual(eligible, report['counts']['eligible_threshold_branch_calls'])
        self.assertEqual(eligible - causes['threshold_branch'], report['counts']['eligible_threshold_branch_nonclosures'])
        self.assertEqual(saturated, report['counts']['saturated_threshold_closures'])
        starts = [0] + [i + 1 for i in finals[:-1]]
        self.assertEqual(len(report['segments']), len(finals))
        for ordinal, (start, end) in enumerate(zip(starts, finals)):
            segment = report['segments'][ordinal]
            self.assertEqual((segment['segment_index'], segment['start_row_index'], segment['end_row_index_inclusive']),
                             (ordinal, start, end))
            self.assertEqual(segment['row_count'], end - start + 1)
            self.assertEqual(segment['source_page_block_index'], start // 29)
            self.assertEqual(start // 29, end // 29)
            self.assertEqual(segment['initialized_row_count'], int(start == 0))
            self.assertIs(segment['first_row_initial_call_flag'], None if start == 0 else True)
            self.assertEqual(segment['closure_condition'],
                             'page_length_and_terminal' if end in forced and end == n - 1 else
                             'page_length' if end in forced else 'terminal' if end == n - 1 else 'threshold_branch')
        self.assertEqual(len(report['page_blocks']), (n + 28) // 29)
        for ordinal, start in enumerate(range(0, n, 29)):
            end = min(n - 1, start + 28)
            self.assertEqual(report['page_blocks'][ordinal], {
                'source_page_block_index': ordinal, 'start_row_index': start,
                'end_row_index_inclusive': end, 'row_count': end - start + 1,
                'page_length_reached': end - start + 1 == 29, 'terminal_output_row': end == n - 1,
                'segment_indices': [s['segment_index'] for s in report['segments'] if s['source_page_block_index'] == ordinal],
            })
        for records, key in [(report['segments'], 'segment_row_count_distribution'),
                             (report['page_blocks'], 'page_block_row_count_distribution')]:
            self.assertEqual(sum(r['row_count'] for r in records), n)
            self.assertEqual(report[key], [{'row_count': length, 'count': count}
                                          for length, count in sorted(Counter(r['row_count'] for r in records).items())])
        self.assertEqual(report['counts']['output_rows'], n)
        self.assertEqual(report['counts']['initialized_rows'], 1)
        self.assertEqual(report['counts']['verified_generated_transitions'], n - 1)
        self.assertEqual(report['counts']['initial_call_flags'], len(finals) - 1)
        self.assertEqual(report['counts']['final_call_flags'], len(finals))
        self.assertEqual(report['counts']['algorithmic_segments'], len(finals))
        self.assertEqual(report['counts']['source_page_blocks'], len(report['page_blocks']))


if __name__ == '__main__':
    unittest.main()
