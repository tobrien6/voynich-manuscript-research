import copy
from pathlib import Path
import tempfile
import unittest

from scripts.audit_self_citation_boundaries import digest, read_pins, reconstruct, write_new


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


if __name__ == '__main__':
    unittest.main()
