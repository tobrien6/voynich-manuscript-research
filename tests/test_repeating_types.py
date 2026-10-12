import copy
from decimal import Decimal, localcontext
from fractions import Fraction
from itertools import combinations, permutations, product
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import repeating_types as module
from scripts import token_baselines
from scripts.audit_transliterations import load_sources


def brute_expected_types(rows):
    original = [slots for _, slots in rows]
    bags = [[value for value in slots if value is not None] for slots in original]
    counts = []
    for orders in product(*(set(permutations(bag)) for bag in bags)):
        repeated = set()
        for slots, order in zip(original, orders):
            available = iter(order)
            placed = [None if value is None else next(available) for value in slots]
            repeated.update(placed[i] for i in range(len(placed) - 1)
                            if placed[i] is not None and placed[i] == placed[i + 1])
        counts.append(len(repeated))
    return Fraction(sum(counts), len(counts))


def synthetic_root(root):
    (root / 'data/raw').mkdir(parents=True)
    (root / 'research/transliteration').mkdir(parents=True)
    (root / 'scripts').mkdir()
    for name in module.ENGINES:
        shutil.copyfile(module.ROOT / name, root / name)
    (root / module.PLAN).write_text('Synthetic repeating-type plan only.\n')
    raw = ['#=IVTFF Eva- 2.0 M\n<f1r>\n<f1r.1,@P0> a,[a:b].?.a\n',
           '#=IVTFF Eva- 2.0 M\n<f1r>\n<f1r.1,@P0> a.a.b.a\n']
    catalog = {'sources': []}
    for identifier, text in zip(('ZL3b', 'IT2a'), raw):
        path = f'data/raw/{identifier}.txt'
        data = text.encode('ascii')
        (root / path).write_bytes(data)
        catalog['sources'].append({'id': identifier, 'url': 'urn:synthetic:' + identifier,
                                   'path': path, 'alphabet': 'Eva-',
                                   'sha256': module.hashlib.sha256(data).hexdigest(), 'bytes': len(data)})
    (root / 'data/transliterations.json').write_bytes(module.encoded(catalog))
    with patch.object(token_baselines, 'load_sources', return_value=load_sources(root=root)):
        reference = token_baselines.baselines(repetitions=1, seed=1)
    (root / module.BASELINE).write_bytes(module.encoded(reference))
    return root


class RepeatingTypeTests(unittest.TestCase):
    def test_independent_sets_match_every_original_gap_layout_and_position_subset(self):
        for size in range(9):
            for mask in range(1 << size):
                slots = ['x' if mask & (1 << i) else None for i in range(size)]
                positions = [i for i, value in enumerate(slots) if value is not None]
                _, _, components = module.adjacency_graph(slots)
                for count in range(len(positions) + 1):
                    expected = sum(not any(i + 1 in selected for i in selected)
                                   for selected in map(set, combinations(positions, count)))
                    with self.subTest(size=size, mask=mask, count=count):
                        self.assertEqual(module.independent_set_count(components, count), expected)

    def test_corpus_expectation_matches_full_multiset_permutations_with_fixed_gaps(self):
        cases = [[], [['a']], [list('abcde')], [list('aaaa')], [list('aaabb')],
                 [['a', None, 'a']], [['a', None, 'a', 'b']],
                 [list('aab'), list('aab')], [list('aabb'), [None, 'a', 'b', 'b', None]],
                 [list('aab'), [], ['a', None, 'b', 'a']]]
        for slots in cases:
            rows = [[str(i), value] for i, value in enumerate(slots)]
            with self.subTest(slots=slots):
                expected = brute_expected_types(rows)
                actual = module.summarize(rows)
                self.assertEqual(Fraction(actual['conditional_expected_repeating_types_fraction']), expected)

    def test_types_are_deduplicated_across_events_and_loci(self):
        pair = module.summarize([['first', list('aab')], ['second', list('aab')]])
        self.assertEqual(pair['observed_equal_pair_events'], 2)
        self.assertEqual(pair['observed_distinct_repeating_types'], 1)
        self.assertEqual(Fraction(pair['conditional_expected_repeating_types_fraction']), Fraction(8, 9))
        self.assertEqual(Fraction(pair['conditional_expected_pair_events_fraction']), Fraction(4, 3))
        multiple = module.summarize([['first', list('aaabbb')], ['second', list('aab')]])
        self.assertEqual(multiple['observed_event_counts_per_repeating_type'], {'2': 1, '3': 1})
        self.assertEqual(multiple['observed_equal_pair_events'], 5)
        self.assertEqual(multiple['observed_distinct_repeating_types'], 2)
        self.assertEqual(Fraction(multiple['conditional_expected_repeating_types_fraction']), Fraction(26, 15))

    def test_global_frequency_alone_does_not_create_a_locus_repeat_opportunity(self):
        result = module.summarize([[str(i), ['a', 'b', 'c']] for i in range(20)])
        self.assertEqual(result['repetition_capable_types_under_control'], 0)
        self.assertEqual(result['conditional_expected_repeating_types_fraction'], '0')
        gaps = module.summarize([['gaps', ['a', None, 'a', None, 'a']]])
        self.assertEqual(gaps['eligible_adjacent_pairs'], 0)
        self.assertEqual(gaps['conditional_expected_repeating_types_fraction'], '0')

    def test_invalid_components_counts_slots_and_duplicate_keys_fail(self):
        for components, count in [([0], 0), ([True], 1), ([-1], 0), ([2], True),
                                  ([2], -1), ([2], 3), ([], 1), ('12', 1)]:
            with self.subTest(components=components, count=count), self.assertRaises(ValueError):
                module.independent_set_count(components, count)
        for slots in ('aab', [''], [1], [False]):
            with self.subTest(slots=slots), self.assertRaises(ValueError):
                module.summarize([['fixture', slots]])
        with self.assertRaises(ValueError):
            module.summarize([['same', ['a']], ['same', ['b']]])

    def test_long_component_products_and_large_exact_serialization_remain_exact(self):
        self.assertEqual(module.independent_set_count([3] * 50, 100), 1)
        self.assertEqual(module.independent_set_count([3] * 50, 101), 0)
        rows = [[str(i), list('aab')] for i in range(1000)]
        result = module.summarize(rows)
        self.assertEqual(Fraction(result['conditional_expected_repeating_types_fraction']), 1 - Fraction(1, 3) ** 1000)
        self.assertEqual(json.loads(module.encoded(result)), result)
        limits = getattr(sys, 'get_int_max_str_digits', lambda: None)
        before = limits()
        with localcontext() as context:
            context.prec = 1
            long_result = module.summarize([[str(i), list('abacabcaa')] for i in range(3884)])
        numerator, denominator = long_result['conditional_expected_repeating_types_fraction'].split('/')
        restored = Fraction(int(Decimal(numerator)), int(Decimal(denominator)))
        self.assertEqual(restored, 3 - Fraction(1, 126) ** 3884 - 2 * Fraction(7, 9) ** 3884)
        self.assertGreater(len(denominator), 4300)
        self.assertEqual(json.loads(module.encoded(long_result)), long_result)
        self.assertEqual(limits(), before)

    def test_complete_synthetic_source_pipeline_and_pair_reference_gate(self):
        with tempfile.TemporaryDirectory(prefix='synthetic-type-pipeline-') as directory:
            root = synthetic_root(Path(directory))
            with patch.object(module, 'ROOT', root):
                result = module.report()
            self.assertEqual(result['selection']['count'], 1)
            self.assertEqual([v['observed_distinct_repeating_types'] for v in result['sources'][0]['variants']],
                             [0, 1, 0, 0])
            self.assertEqual([v['observed_distinct_repeating_types'] for v in result['sources'][1]['variants']],
                             [1, 1, 1, 1])
            reference = json.loads((root / module.BASELINE).read_bytes())
            for changed in ('count', 'events', 'type', 'selection_type', 'kind'):
                altered = copy.deepcopy(reference)
                if changed == 'count': altered['selection']['count'] += 1
                elif changed == 'events': altered['sources'][0]['variants'][0]['adjacent_repetition']['observed_equal_pairs'] += 1
                elif changed == 'type': altered['sources'][0]['variants'][0]['selected_loci'] = True
                elif changed == 'selection_type': altered['selection']['count'] = True
                else: altered['selection']['kind'] = 'P1'
                with self.subTest(changed=changed), self.assertRaises(ValueError):
                    module.verify_pair_baseline(result, altered)

    def test_actual_cli_preserves_protected_aliases_and_replays_typed_cache(self):
        with tempfile.TemporaryDirectory(prefix='synthetic-type-cli-') as directory:
            root = synthetic_root(Path(directory))
            script = root / 'scripts/repeating_types.py'
            protected = [root / 'data/raw/ZL3b.txt', root / 'data/transliterations.json',
                         root / module.PLAN, root / module.BASELINE, script]
            before = {path: path.read_bytes() for path in protected}
            for i, path in enumerate(protected):
                symbolic, hardlink = root / f'symlink-{i}.json', root / f'hardlink-{i}.json'
                symbolic.symlink_to(path)
                os.link(path, hardlink)
                for output in (path, symbolic, hardlink):
                    result = subprocess.run([sys.executable, '-B', str(script), '--output', str(output)],
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn('output aliases', result.stderr)
                    self.assertEqual({p: p.read_bytes() for p in protected}, before)
            target = root / 'report.json'
            output = subprocess.run([sys.executable, '-B', str(script), '--output', str(target)], capture_output=True, text=True)
            self.assertEqual(output.returncode, 0, output.stderr)
            original = target.read_bytes()
            check = subprocess.run([sys.executable, '-B', str(script), '--check', str(target)], capture_output=True, text=True)
            self.assertEqual(check.returncode, 0, check.stderr)
            altered = json.loads(original)
            altered['schema_version'] = True
            target.write_bytes(module.encoded(altered))
            failed = subprocess.run([sys.executable, '-B', str(script), '--check', str(target)], capture_output=True, text=True)
            self.assertEqual(failed.returncode, 1)
            self.assertIn('differs from recomputation', failed.stderr)


if __name__ == '__main__':
    unittest.main()
