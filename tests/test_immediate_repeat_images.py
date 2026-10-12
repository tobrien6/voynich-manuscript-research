from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import select_immediate_repeat_images as module


def canvas(page='1r', oid='1000000'):
    return {'label_class': 'exact_single_side_label', 'has_partial_marker': 'False',
            'has_multiple_explicit_sides': 'False', 'yale_label': page, 'image_oid': oid}


def maps(texts):
    result = {v: {} for v in module.VARIANTS}
    for key, pair in texts.items():
        for source, spacing, alternatives in module.VARIANTS:
            text = pair[source == 'IT2a']
            result[source, spacing, alternatives][key] = {
                'locus_key': key, 'page': key.rsplit('.', 1)[0], 'locator': '@',
                'slots': [t.value if module.retain(t, alternatives) else None
                          for t in module.tokenize(text, spacing)]}
    return result


class RepeatImageSelectionTests(unittest.TestCase):
    def test_original_coordinates_and_overlapping_events(self):
        self.assertEqual(module.events(['a', 'a', 'a', None, 'a', None, 'a', 'a']),
                         [[0, 1, 'a'], [1, 2, 'a'], [6, 7, 'a']])
        for bad in ([''], [1], 'aa'):
            with self.assertRaises(ValueError):
                module.events(bad)

    def test_groups_numeric_order_and_complete_partition(self):
        texts = {'f1r.10': ('a.a.b', 'a.a.c'), 'f1r.2': ('b.b.c', 'b.b.d'),
                 'f1v.1': ('a.a.c', 'a.b.c'), 'f2r.1': ('a.b.c', 'a.a.c'),
                 'f2r.2': ('a.b.c', 'a.b.c'), 'f2r.3': ('a.a.a', 'a.a.a')}
        result, _ = module.select_cases(maps(texts), [canvas('1r'), canvas('1v'), canvas('2r')], texts)
        self.assertEqual(result['selected_locus_keys'], {
            'paired_agreement': 'f1r.2', 'ZL_only': 'f1v.1', 'IT_only': 'f2r.1'})
        self.assertEqual(result['candidate_keys']['paired_agreement'], ['f1r.2', 'f1r.10'])
        self.assertEqual(result['zero_repeat_locus_keys'], ['f2r.2'])
        self.assertEqual(result['other_eligible_pattern_locus_keys'], ['f2r.2', 'f2r.3'])
        self.assertEqual(result['variants'][0]['observed_equal_pair_events'], 5)
        self.assertEqual(result['variants'][0]['observed_distinct_repeating_types'], 2)

    def test_uncertainties_retained_in_audit_not_candidates(self):
        texts = {'f1r.1': ('a,a.b', 'a.a.b'), 'f1r.2': ('a.[a:b].c', 'a.a.c'),
                 'f1r.3': ('a.?.a', 'a.b.a')}
        result, _ = module.select_cases(maps(texts), [canvas()], texts)
        self.assertEqual(result['excluded_union_count'], 2)
        self.assertEqual(result['candidate_keys'], {g: [] for g in module.GROUPS})
        self.assertEqual(result['other_eligible_pattern_locus_keys'], ['f1r.1'])
        self.assertEqual(result['loci_with_any_repeat'][0]['events_in_variant_order'][0], [[0, 1, 'a']])
        self.assertEqual(result['loci_with_any_repeat'][0]['events_in_variant_order'][2], [])
        self.assertEqual(result['zero_repeat_locus_keys'], ['f1r.3'])

    def test_literal_case_and_different_repeat_types_do_not_agree(self):
        texts = {'f1r.1': ('A.A.b', 'a.a.b')}
        result, _ = module.select_cases(maps(texts), [canvas()], texts)
        self.assertEqual(result['other_eligible_pattern_locus_keys'], ['f1r.1'])
        self.assertEqual(result['unfilled_groups'], list(module.GROUPS))

    def test_mapping_locator_and_panel_failures_preserved(self):
        texts = {'f1r.1': ('a.a', 'a.a'), 'f2r.1': ('a.a', 'a.a'), 'f3r1.1': ('a.a', 'a.a')}
        source_maps = maps(texts)
        source_maps[module.VARIANTS[0]]['f2r.1']['locator'] = '='
        result, _ = module.select_cases(source_maps, [canvas(), canvas(), canvas('2r')], texts)
        self.assertEqual(result['excluded_union_count'], 3)
        self.assertEqual(result['exclusions_may_overlap']['no_unique_exact_canvas'], ['f1r.1', 'f3r1.1'])
        self.assertEqual(result['exclusions_may_overlap']['unsupported_panel_page'], ['f3r1.1'])
        self.assertEqual(result['exclusions_may_overlap']['ZL3b/split/exclude:nonregular_locator'], ['f2r.1'])
        # Partial and compound flags never qualify, even with an exact label.
        for field in ('has_partial_marker', 'has_multiple_explicit_sides'):
            image = canvas()
            image[field] = 'True'
            result, _ = module.select_cases(maps({'f1r.1': texts['f1r.1']}), [image], {'f1r.1'})
            self.assertEqual(result['excluded_union_count'], 1)

    def test_complete_variant_maps_and_identity_required(self):
        original = maps({'f1r.1': ('a.a', 'a.a')})
        for change in ('missing_variant', 'missing_key', 'extra_key', 'wrong_identity'):
            value = deepcopy(original)
            if change == 'missing_variant':
                value.pop(module.VARIANTS[0])
            elif change == 'missing_key':
                value[module.VARIANTS[0]].clear()
            elif change == 'extra_key':
                value[module.VARIANTS[0]]['f1r.2'] = deepcopy(value[module.VARIANTS[0]]['f1r.1'])
            else:
                value[module.VARIANTS[0]]['f1r.1']['locus_key'] = 'f1r.2'
            with self.subTest(change=change), self.assertRaises(ValueError):
                module.select_cases(value, [canvas()], {'f1r.1'})

    def test_empty_population_retains_unfilled_groups(self):
        result, _ = module.select_cases({v: {} for v in module.VARIANTS}, [], [])
        self.assertEqual(result['count'], 0)
        self.assertEqual(result['selected_locus_keys'], {g: None for g in module.GROUPS})

    def test_final_guard_after_report_and_serialization(self):
        for stage in ('report', 'serialization'):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                protected = [*module.ENGINES, module.PLAN, module.PARENT, module.INDEX,
                             'data/transliterations.json', 'data/raw.txt']
                for name in protected:
                    path = root / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text('protected')
                (root / 'data/transliterations.json').write_text('{"sources":[{"path":"data/raw.txt"}]}')
                output, target = root / 'output.json', root / module.PLAN
                before = target.read_bytes()
                real_encoded = module.encoded
                def calculate():
                    if stage == 'report':
                        output.hardlink_to(target)
                    return {'small': True}
                def serialize(value):
                    payload = real_encoded(value)
                    if stage == 'serialization':
                        output.symlink_to(target)
                    return payload
                with patch.object(module, 'ROOT', root), patch.object(module, 'report', calculate), \
                        patch.object(module, 'encoded', serialize), \
                        patch('sys.argv', ['select_immediate_repeat_images.py', '--output', str(output)]):
                    with self.assertRaises(SystemExit) as failure:
                        module.main()
                self.assertEqual(failure.exception.code, 1)
                self.assertEqual(target.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
