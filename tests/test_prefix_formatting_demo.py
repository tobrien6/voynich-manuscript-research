import contextlib
from fractions import Fraction
import io
import itertools
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import prefix_formatting_demo as module
from scripts.prefix_formatting_demo import (
    boundary_metrics, decode_rows, encode_rows, extreme_tail, lookup_counts, report, source_rows,
)


class PrefixFormattingTests(unittest.TestCase):
    def test_complete_message_round_trip_preserves_rows_slots_and_all_tokens(self):
        rows = [['aaa', 'bcd'], ['ccc', 'ddd', 'abc']]
        carrier = encode_rows(rows)
        self.assertEqual(carrier, [['yaaa', 'bcd'], ['yccc', 'ddd', 'abc']])
        self.assertEqual(decode_rows(carrier), rows)
        self.assertEqual(rows, [['aaa', 'bcd'], ['ccc', 'ddd', 'abc']])

    def test_malformed_codewords_are_rejected_without_repair(self):
        for rows in ([], [[]], [['qaa', 'aaa']], [['yaaa', 'aaa']]):
            with self.subTest(source=rows), self.assertRaises(ValueError):
                encode_rows(rows)
        for rows in ([], [[]], [['aaa', 'bbb']], [['yyaaa', 'bbb']], [['yaaa', 'ybbb']]):
            with self.subTest(carrier=rows), self.assertRaises(ValueError):
                decode_rows(rows)

    def test_shared_measurement_functions_give_the_fixed_prefix_and_length_effects(self):
        source = [['aaa', 'bbb', 'ccc', 'ddd'], ['abc', 'cba', 'add', 'bba']]
        carrier = encode_rows(source)
        for feature in ('literal_y_prefix', 'ascii_token_length'):
            self.assertEqual(boundary_metrics(source, 'first', feature)['equal_row_mean_contrast'], module.rational(0))
            self.assertEqual(boundary_metrics(carrier, 'first', feature)['equal_row_mean_contrast'], module.rational(1))
            self.assertEqual(boundary_metrics(carrier, 'last', feature)['equal_row_mean_contrast'], module.rational(Fraction(-1, 3)))
            self.assertEqual(boundary_metrics(carrier, 'first', feature)['conditional_variance_of_equal_row_mean'],
                             module.rational(Fraction(1, 6)))

    def test_exact_two_sided_tail_matches_every_small_assignment_space(self):
        for count in range(1, 5):
            for width in range(2, 6):
                outcomes = [sum((Fraction(1) if slot == 0 else Fraction(-1, width - 1)
                                 for slot in placements), Fraction(0)) / count
                            for placements in itertools.product(range(width), repeat=count)]
                actual = Fraction(sum(abs(value) >= 1 for value in outcomes), len(outcomes))
                self.assertEqual(extreme_tail(count, width), actual)

    def test_fixed_dictionary_reproduces_source_matches_after_removing_the_marker(self):
        source = [['aaa', 'bbb', 'ccc'], ['bbb', 'aaa', 'ccc']]
        carrier = encode_rows(source)
        dictionary = {token for row in carrier for token in row[1:]}
        before, after = lookup_counts(source, dictionary), lookup_counts(carrier, dictionary)
        self.assertEqual(after[0]['raw_matches'], 0)
        self.assertEqual(after[0]['matches_after_one_leading_y_removed'], before[0]['raw_matches'])
        self.assertEqual(after[1], before[1])
        self.assertEqual(dictionary, {'aaa', 'bbb', 'ccc'})

    def test_generator_is_deterministic_and_report_keeps_information_denominators(self):
        self.assertEqual(source_rows(2, 3, 17), source_rows(2, 3, 17))
        self.assertNotEqual(source_rows(2, 3, 17), source_rows(2, 3, 18))
        result = report(2, 3, 17)
        self.assertEqual(result['source_matrix_sha256'], result['decoded_matrix_sha256'])
        self.assertNotEqual(result['source_matrix_sha256'], result['encoded_matrix_sha256'])
        self.assertEqual(result['token_count_in_each_matrix'], 6)
        self.assertEqual(result['ideal_uniform_source_ensemble']['joint_bits_in_either_representation'], 36)
        self.assertEqual(result['source_ascii_characters'], 18)
        self.assertEqual(result['encoded_ascii_characters'], 20)
        for args in ((0, 3, 1), (2, 1, 1), (2, 3, -1), (True, 3, 1)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                source_rows(*args)

    def test_committed_realization_replays_with_plan_and_implementation_pins(self):
        saved = json.loads((module.ROOT / 'research/representation/prefix_formatting_demo.json').read_text())
        self.assertEqual(report(), saved)

    def test_cli_protects_the_plan_source_catalog_and_link_aliases_before_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = root / module.PLAN
            plan.parent.mkdir(parents=True)
            plan.write_text('synthetic fixed plan')
            data = root / 'data'
            data.mkdir()
            catalog = data / 'transliterations.json'
            catalog.write_text(json.dumps({'sources': []}))
            alias = root / 'linked-plan.json'
            alias.symlink_to(plan)
            for output in (plan, alias, catalog, data / 'new.json'):
                with self.subTest(output=output), patch.object(module, 'ROOT', root), \
                        patch.object(module, 'report') as run, patch('sys.argv', ['demo', '--output', str(output)]), \
                        contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    module.main()
                run.assert_not_called()
            self.assertEqual(plan.read_text(), 'synthetic fixed plan')
            self.assertEqual(json.loads(catalog.read_text()), {'sources': []})


if __name__ == '__main__':
    unittest.main()
