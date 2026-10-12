import unittest

from scripts.ivtff import parse_ivtff
from scripts.y_layout_prefix import build_partition, repetition_body


def paired(text):
    doc = parse_ivtff('#=IVTFF Eva- 2.0 M\n' + text)
    return [({'id': identifier, 'sha256': 'synthetic'}, doc) for identifier in ('ZL3b', 'IT2a')]


def images(groups):
    return {'dependency_components': [{'folio_ids': list(group)} for group in groups],
            'indexed_canvas_ids_by_leaf': {family: ['canvas:' + family]
                                          for group in groups for family in group}}


class YPartitionTests(unittest.TestCase):
    def test_shared_scan_and_repeated_string_dependencies_close_transitively(self):
        source = paired('<f1r>\n<f1r.1,@P0> a.b.c\n'
                        '<f2r>\n<f2r.1,@P0> d.e.f\n'
                        '<f3r>\n<f3r.1,@P0> <!note><@H=2>a.b.c\n'
                        '<f4r>\n<f4r.1,@P0> g.h.i\n')
        report = build_partition(source, images([['1', '2'], ['3'], ['4']]))
        groups = [unit['numeric_source_families'] for unit in report['units']]
        self.assertIn(['1', '2', '3'], groups)
        self.assertIn(['4'], groups)
        self.assertEqual(len(report['exact_string_dependency_edges']), 2)
        self.assertFalse(report['valid_candidate_holdout'])

    def test_partition_order_is_deterministic_and_cannot_split_sides_or_panels(self):
        source = paired('<f1r>\n<f1r.1,@P0> a.b.c\n'
                        '<f1v>\n<f1v.1,@P0> d.e.f\n'
                        '<f67r1>\n<f67r1.1,@P0> g.h.i\n'
                        '<f67r2>\n<f67r2.1,@P0> j.k.l\n')
        report = build_partition(source, images([['1'], ['67']]))
        reordered = images([['67'], ['1']])
        self.assertEqual(report, build_partition(list(reversed(source)), reordered))
        self.assertEqual([unit['partition'] for unit in report['units']],
                         ['diagnostic_evaluation', 'dictionary_development'])
        self.assertEqual(sum(len(unit['selected_source_pages']) for unit in report['units']), 4)

    def test_joint_paragraph_and_locator_exclusions_precede_partitioning(self):
        left = parse_ivtff('#=IVTFF Eva- 2.0 M\n<f1r>\n'
                           '<f1r.1,@P0> <%>a.b.c\n<f1r.2,=P0> d.e.f\n'
                           '<f1r.3,+P0> g.h.i\n<f2r>\n<f2r.1,@P0> j.k.l\n')
        right = parse_ivtff('#=IVTFF Eva- 2.0 M\n<f1r>\n'
                            '<f1r.1,@P0> a.b.c\n<f1r.2,+P0> d.e.f\n'
                            '<f1r.3,+P0> g.h.i\n<f2r>\n<f2r.1,@P0> j.k.l\n')
        report = build_partition([({'id': 'ZL3b', 'sha256': 'synthetic'}, left),
                                  ({'id': 'IT2a', 'sha256': 'synthetic'}, right)], images([['1'], ['2']]))
        self.assertEqual(report['selection']['selected_location_count'], 2)
        self.assertEqual(report['selection']['excluded_source_paragraph_start_keys'], ['f1r.1'])
        self.assertEqual(report['selection']['excluded_nonregular_keys'], ['f1r.2'])

    def test_unknown_or_ambiguous_strings_do_not_establish_repeated_passages(self):
        doc = parse_ivtff('#=IVTFF Eva- 2.0 M\n<f1r>\n'
                          '<f1r.1,@P0> a.b.?\n<f1r.2,+P0> a.[b:c].d\n'
                          '<f1r.3,+P0> a.b\n')
        self.assertTrue(all(repetition_body(locus) is None for locus in doc.loci))

    def test_one_connected_unit_is_a_failure_not_a_fake_partition(self):
        with self.assertRaisesRegex(ValueError, 'at least two dependency units'):
            build_partition(paired('<f1r>\n<f1r.1,@P0> a.b.c\n'), images([['1']]))


if __name__ == '__main__':
    unittest.main()
