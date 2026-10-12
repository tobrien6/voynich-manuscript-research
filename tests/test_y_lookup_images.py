import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.ivtff import parse_ivtff
from scripts import select_y_lookup_images as selector


def image(page, oid=None):
    return {'label_class': 'exact_single_side_label', 'has_partial_marker': 'False',
            'has_multiple_explicit_sides': 'False', 'yale_label': page[1:],
            **{key: (oid or page) for key in ('canvas_uri', 'image_oid', 'catalog_image_url', 'full_image_url',
                                            'image_service_url', 'image_width', 'image_height')}}


def fixtures(text, development=('1',), evaluation=('2',)):
    doc = parse_ivtff('#=IVTFF Eva- 2.0 M\n' + text)
    rows = [(variant, selector.parent.prepare_rows(doc.loci, variant[1], variant[2])) for variant in selector.VARIANTS]
    units = {'units': [{'unit_id': 'unit:' + family, 'selected_source_pages': ['f' + family + 'r'],
                       'partition': 'dictionary_development' if family in development else 'diagnostic_evaluation'}
                      for family in (*development, *evaluation)]}
    images = [image('f' + family + 'r') for family in (*development, *evaluation)]
    allowed = {'unit:' + family for family in evaluation}
    return rows, units, images, allowed


class LookupImageTests(unittest.TestCase):
    def test_positive_lookup_pair_keeps_original_internal_slot(self):
        args = fixtures('<f1r>\n<f1r.1,@P0> z.?.a.b\n<f2r>\n<f2r.1,@P0> ya.yb\n')
        r = selector.select_pairs(*args)
        pair = r['selected_pairs'][0]
        self.assertEqual(pair['original_first_form'], 'ya')
        self.assertEqual(pair['reference_form'], 'a')
        self.assertEqual(pair['chosen_reference'], {'locus_key': 'f1r.1', 'original_slot_zero_based': 2, 'unit_id': 'unit:1'})
        self.assertEqual(r['unfilled_target_units'], 1)

    def test_original_matches_and_nonpositive_gains_are_excluded(self):
        args = fixtures('<f1r>\n<f1r.1,@P0> z.ya.yb\n<f2r>\n<f2r.1,@P0> ya.yb\n<f2r.2,+P0> yc.yb\n')
        r = selector.select_pairs(*args)
        self.assertEqual(r['selected_pairs'], [])
        self.assertEqual(r['unfilled_target_units'], 2)
        self.assertTrue(all('not_a_positive_lookup_gain_in_every_treatment' in item['reasons'] for item in r['excluded_diagnostic_loci']))

    def test_development_first_slots_and_evaluation_internal_tokens_are_not_references(self):
        args = fixtures('<f1r>\n<f1r.1,@P0> a.b\n<f2r>\n<f2r.1,@P0> ya.a\n')
        r = selector.select_pairs(*args)
        self.assertEqual(r['candidate_count'], 0)
        self.assertEqual(r['stable_development_reference_occurrences'], 1)

    def test_all_eight_treatments_must_share_target_and_reference_slot(self):
        args = fixtures('<f1r>\n<f1r.1,@P0> z.a,b\n<f2r>\n<f2r.1,@P0> ya.yb\n')
        r = selector.select_pairs(*args)
        self.assertEqual(r['candidate_count'], 0)
        self.assertEqual(r['common_eligible_locations'], 2)
        # Both forms remain vocabulary entries, but source-slot agreement fails in one edition.
        args = list(fixtures('<f1r>\n<f1r.1,@P0> z.a.b\n<f2r>\n<f2r.1,@P0> ya.yb\n'))
        replacement = parse_ivtff('#=IVTFF Eva- 2.0 M\n<f1r>\n<f1r.1,@P0> z.b.a\n<f2r>\n<f2r.1,@P0> ya.yb\n')
        args[0][-1] = (selector.VARIANTS[-1], selector.parent.prepare_rows(replacement.loci, 'join', 'first'))
        r = selector.select_pairs(*args)
        self.assertEqual(r['excluded_diagnostic_loci'][0]['reasons'], ['no_qualifying_development_reference'])
        args = list(fixtures('<f1r>\n<f1r.1,@P0> z.a.b\n<f2r>\n<f2r.1,@P0> ya.yb\n'))
        replacement = parse_ivtff('#=IVTFF Eva- 2.0 M\n<f1r>\n<f1r.1,@P0> z.a.b\n<f2r>\n<f2r.1,@P0> yb.ya\n')
        args[0][-1] = (selector.VARIANTS[-1], selector.parent.prepare_rows(replacement.loci, 'join', 'first'))
        r = selector.select_pairs(*args)
        self.assertIn('first_form_differs_across_treatments', r['excluded_diagnostic_loci'][0]['reasons'])

    def test_drawing_markers_exclude_targets_and_references_but_comments_do_not(self):
        for text, reason in (('<f1r>\n<f1r.1,@P0> z<->a.b\n<f2r>\n<f2r.1,@P0> ya.yb\n', 'no_qualifying_development_reference'),
                             ('<f1r>\n<f1r.1,@P0> z.a.b\n<f2r>\n<f2r.1,@P0> ya<~>yb\n', 'target_inline_drawing_interruption')):
            r = selector.select_pairs(*fixtures(text))
            self.assertIn(reason, r['excluded_diagnostic_loci'][0]['reasons'])
        r = selector.select_pairs(*fixtures('<f1r>\n<f1r.1,@P0> <!<->z.a.b\n<f2r>\n<f2r.1,@P0> ya.yb\n'))
        self.assertEqual(r['candidate_count'], 1)

    def test_unique_exact_canvas_required_and_unsupported_panel_not_sorted_as_side(self):
        args = list(fixtures('<f1r>\n<f1r.1,@P0> z.a.b\n<f2r>\n<f2r.1,@P0> ya.yb\n'))
        args[2].append(image('f1r', 'duplicate'))
        r = selector.select_pairs(*args)
        self.assertEqual(r['selected_pairs'], [])
        self.assertEqual(r['reference_pools']['a']['excluded_stable_occurrences'][0]['reasons'], ['reference_no_unique_exact_single_side_canvas'])
        args = list(fixtures('<f1r>\n<f1r.1,@P0> z.a.b\n<f2r>\n<f2r.1,@P0> ya.yb\n'))
        args[2][1]['has_partial_marker'] = 'True'
        r = selector.select_pairs(*args)
        self.assertIn('target_no_unique_exact_single_side_canvas', r['excluded_diagnostic_loci'][0]['reasons'])
        args = list(fixtures('<f1r>\n<f1r.1,@P0> z.a.b\n<f67r1>\n<f67r1.1,@P0> z.a.b\n<f2r>\n<f2r.1,@P0> ya.yb\n'))
        args[1]['units'][0]['selected_source_pages'].append('f67r1')
        r = selector.select_pairs(*args)
        self.assertEqual(r['selected_pairs'][0]['chosen_reference']['locus_key'], 'f1r.1')
        self.assertEqual(len(r['reference_pools']['a']['excluded_stable_occurrences']), 1)

    def test_numeric_reference_order_slot_order_and_two_distinct_dependency_units(self):
        text = '<f1r>\n<f1r.1,@P0> z.a.a\n<f10r>\n<f10r.1,@P0> z.a.b\n'
        text += '<f2r>\n<f2r.1,@P0> ya.yb\n<f3r>\n<f3r.1,@P0> ya.yb\n<f4r>\n<f4r.1,@P0> ya.yb\n'
        args = list(fixtures(text, ('1', '10'), ('2', '3', '4')))
        args[1]['units'][2]['selected_source_pages'].append('f3r')
        args[1]['units'].pop(3)
        r = selector.select_pairs(*args)
        self.assertEqual([p['locus_key'] for p in r['selected_pairs']], ['f2r.1', 'f4r.1'])
        self.assertEqual(r['selected_pairs'][0]['chosen_reference']['locus_key'], 'f1r.1')
        self.assertEqual(r['selected_pairs'][0]['chosen_reference']['original_slot_zero_based'], 1)
        self.assertEqual(r['candidate_count'], 3)

    def test_parent_unscorable_units_and_excluded_first_slots_stay_excluded(self):
        args = list(fixtures('<f1r>\n<f1r.1,@P0> z.a.b\n<f2r>\n<f2r.1,@P0> ya.yb\n<f2r.2,+P0> ?.ya.yb\n'))
        args[3] = set()
        r = selector.select_pairs(*args)
        self.assertEqual(r['diagnostic_eligible_locus_count'], 1)
        self.assertEqual(r['excluded_diagnostic_loci'][0]['reasons'], ['unit_not_scorable_in_parent_all_treatments'])

    def test_missing_or_duplicate_treatments_are_rejected(self):
        args = list(fixtures('<f1r>\n<f1r.1,@P0> z.a.b\n<f2r>\n<f2r.1,@P0> ya.yb\n'))
        args[0] = args[0][:-1]
        with self.assertRaisesRegex(ValueError, 'eight declared'):
            selector.select_pairs(*args)

    def test_input_pins_and_protected_output_aliases(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            directory = root / selector.BASE
            directory.mkdir(parents=True)
            plan = directory / 'PLAN.md'
            plan.write_bytes(b'fixed plan')
            record = {'analysis_id': 'y-lookup-image-v1', 'maximum_target_units': 2,
                      'pins': {'plan': {'path': selector.BASE + '/PLAN.md', 'sha256': selector.sha(plan.read_bytes())}}}
            (directory / 'inputs.json').write_text(json.dumps(record))
            catalog = root / 'data/transliterations.json'
            catalog.parent.mkdir()
            catalog.write_text(json.dumps({'sources': []}))
            with patch.object(selector.parent, 'ROOT', root), \
                    patch.object(selector.parent, 'prepare_partition', return_value={'input_pins': {}}):
                self.assertEqual(selector.verify_inputs(), record)
                for original in (plan, directory / 'inputs.json'):
                    for kind in ('direct', 'symlink', 'hardlink'):
                        alias = root / (original.name + '-' + kind)
                        if kind == 'direct': alias = original
                        elif kind == 'symlink': alias.symlink_to(original)
                        else: os.link(original, alias)
                        with self.subTest(kind=kind), self.assertRaises(ValueError):
                            selector.protect_output(alias, record)
                selector.protect_output(root / 'safe.json', record)
                plan.write_bytes(b'changed plan')
                with self.assertRaisesRegex(ValueError, 'pin changed'):
                    selector.verify_inputs()


if __name__ == '__main__':
    unittest.main()
