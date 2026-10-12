from copy import deepcopy
import unittest

from scripts.select_initial_prefix_images import VARIANTS, select_cases, selection_report


def record(key, first):
    return {'locus_key': key, 'page_id': key.rsplit('.', 1)[0],
            'eligible': True, 'token_count': 2, 'tokens': [first, 'a'],
            'locator': '+', 'locus_identifier': key + ',+P0',
            'source_line_number': 1}


def canvas(page, oid):
    return {'label_class': 'exact_single_side_label', 'has_partial_marker': 'False',
            'has_multiple_explicit_sides': 'False', 'yale_label': page[1:],
            'canvas_uri': 'https://example.test/canvas/' + oid, 'image_oid': oid,
            'catalog_image_url': 'https://example.test/catalog/' + oid,
            'full_image_url': 'https://example.test/iiif/' + oid + '/full/full/0/default.jpg',
            'image_service_url': 'https://example.test/iiif/' + oid,
            'image_width': '1000', 'image_height': '2000'}


def maps_for(keys):
    return {variant: {key: record(key, 'qa' if variant[0] == 'ZL3b' else 'a')
                      for key in keys} for variant in VARIANTS}


class InitialPrefixImageTests(unittest.TestCase):
    def test_numeric_folio_order_and_one_case_per_side(self):
        keys = {'f100r.1', 'f18v.10', 'f18v.2', 'f18r.2', 'f78r.1'}
        images = [canvas(page, str(i)) for i, page in enumerate(
            ['f100r', 'f18v', 'f18r', 'f78r'])]
        result = select_cases(maps_for(keys), images, keys)
        self.assertEqual(result['selected_locus_keys'], ['f18r.2', 'f18v.2', 'f78r.1'])
        self.assertEqual(result['candidate_count'], 5)

    def test_one_ineligible_policy_excludes_the_whole_location(self):
        key = 'f1r.1'
        maps = maps_for({key})
        maps['IT2a', 'join'][key].update(eligible=False, tokens=None, token_count=None)
        result = select_cases(maps, [canvas('f1r', '1')], {key})
        self.assertEqual(result['candidate_count'], 0)
        self.assertEqual(result['excluded_union_count'], 1)
        self.assertEqual(result['unfilled_review_slots'], 3)

    def test_join_cannot_create_a_spacing_dependent_disagreement(self):
        key = 'f1r.1'
        maps = maps_for({key})
        maps['IT2a', 'join'][key]['tokens'][0] = 'qa'
        result = select_cases(maps, [canvas('f1r', '1')], {key})
        self.assertEqual(result['candidate_count'], 0)
        self.assertEqual(result['exclusions_may_overlap']['spacing_dependent_disagreement']['count'], 1)

    def test_duplicate_partial_and_compound_views_do_not_authorize_a_canvas(self):
        key = 'f1r.1'
        original = canvas('f1r', '1')
        partial = deepcopy(original)
        partial['has_partial_marker'] = 'True'
        combined = deepcopy(original)
        combined['has_multiple_explicit_sides'] = 'True'
        for views in ([original, canvas('f1r', '2')], [partial], [combined]):
            with self.subTest(views=views):
                result = select_cases(maps_for({key}), views, {key})
                self.assertEqual(result['candidate_count'], 0)

    def test_nonregular_locator_and_lone_token_are_retained_as_exclusions(self):
        key = 'f1r.1'
        maps = maps_for({key})
        maps['ZL3b', 'split'][key].update(locator='=', token_count=1, tokens=['qa'])
        result = select_cases(maps, [canvas('f1r', '1')], {key})
        self.assertEqual(result['excluded_union_count'], 1)
        self.assertEqual(len(result['exclusions_may_overlap']), 2)

    def test_missing_or_mismatched_identifiers_fail_instead_of_silent_selection(self):
        key = 'f1r.1'
        for mode in ('missing', 'wrong_page'):
            maps = maps_for({key})
            if mode == 'missing':
                del maps['IT2a', 'join'][key]
            else:
                maps['IT2a', 'join'][key]['page_id'] = 'f1v'
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                select_cases(maps, [canvas('f1r', '1')], {key})

    def test_empty_selection_does_not_invent_a_review_target(self):
        result = select_cases(maps_for(set()), [], set())
        self.assertEqual(result['selected_locus_keys'], [])
        self.assertEqual(result['unfilled_review_slots'], 3)

    def test_pinned_selection_covers_every_shared_locus_without_claiming_review(self):
        report = selection_report()
        selection = report['selection']
        self.assertEqual(selection['selected_locus_keys'], ['f18v.5', 'f78r.21'])
        self.assertEqual(selection['candidate_count'], 2)
        self.assertEqual(selection['unfilled_review_slots'], 1)
        self.assertEqual(selection['candidate_count'] + selection['excluded_union_count'],
                         selection['shared_present_p0_count'])
        self.assertFalse(report['image_alignment_verified'])
        self.assertFalse(report['source_corrections_applied'])


if __name__ == '__main__':
    unittest.main()
