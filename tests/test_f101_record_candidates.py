from contextlib import redirect_stderr
import io
import itertools
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import audit_f101_record_candidates as audit


def rows(strings, page='f101r1', historical=True):
    return [(s, {'native_locator': f'{page}.{i}', 'source_file_line': 100+i,
                 'native_unit' if historical else 'locus_kind': 'P' if historical else 'P0',
                 'source_order_index_zero_based_on_page': i}) for i, s in enumerate(strings)]


def fixture(root):
    names = list(audit.FROZEN) + [str(audit.PLAN), str(audit.HUMAN_PLAN),
             'scripts/audit_f101_record_candidates.py', 'data/transliterations.json',
             'data/historical/catalog.json', 'data/historical/native.zip', 'data/raw/native.txt']
    paths = [root / name for name in names]
    for p in paths:
        p.parent.mkdir(parents=True, exist_ok=True); p.write_text('synthetic preserve')
    (root / 'data/transliterations.json').write_text(json.dumps({'sources': [{'path': 'data/raw/native.txt'}]}))
    loaded = ([], None, {}, {root / name for name in names[-4:]})
    return paths, loaded


class CandidateTests(unittest.TestCase):
    def test_complete_source_parent_and_candidate_report_replay(self):
        raw=(audit.ROOT/'research/historical/f101-record-candidates.json').read_bytes()
        self.assertEqual(audit.parent.encoded(audit.parent.load_json(raw)),audit.parent.encoded(audit.build()))

    def test_all_four_pairs_keep_literal_page_names_and_no_alias(self):
        old = {p: rows(['ab'], p) for p in audit.HISTORICAL}
        new = {p: rows(['ab'], p, False) for p in audit.MODERN}
        matrix = audit.candidate_matrix(old, new)
        self.assertEqual([(r['historical_page_id'], r['modern_page_id']) for r in matrix],
                         [(a,b) for a in audit.HISTORICAL for b in audit.MODERN])
        for r in matrix:
            self.assertFalse(r['accepted_page_alias']); self.assertFalse(r['usable_as_verified_locus_crosswalk'])
            self.assertTrue(r['nonempty_record_projection_order_equal'])
            g = r['projection_groups'][0]
            self.assertTrue(g['historical_H_records'][0]['native_locator'].startswith(r['historical_page_id']))
            self.assertTrue(g['modern_IT2a_present_records'][0]['native_locator'].startswith(r['modern_page_id']))
        del old[audit.HISTORICAL[0]]
        with self.assertRaisesRegex(ValueError, 'absent'): audit.candidate_matrix(old, new)

    def test_permutation_split_duplicates_and_empty_denominators(self):
        perm = audit.compare_pair(rows(['ab','cd']), rows(['cd','ab'],historical=False))
        self.assertTrue(perm['nonempty_record_projection_bags_equal'])
        self.assertFalse(perm['nonempty_record_projection_order_equal'])
        split = audit.compare_pair(rows(['a','bc']), rows(['ab','c'],historical=False))
        self.assertTrue(split['joined_lowercase_streams_equal']); self.assertFalse(split['nonempty_record_projection_bags_equal'])
        dup = audit.compare_pair(rows(['ab','ab','']), rows(['ab'],historical=False))
        self.assertEqual(dup['ambiguous_shared_projection_groups'],1)
        self.assertEqual(dup['shared_projection_group_records'],{'historical_H':2,'modern_IT2a_present':1})
        self.assertEqual(len(dup['projection_groups'][0]['historical_H_records']),2)
        self.assertEqual(audit.parent.side_profile(rows(['ab','']))['selected_native_records'],2)
        for empty in (audit.compare_pair(rows(['']), rows([''],historical=False)),
                      audit.compare_pair(rows(['']), rows(['ab'],historical=False))):
            for key in ['nonempty_record_projection_order_equal','nonempty_record_projection_bags_equal',
                        'joined_lowercase_streams_equal','lowercase_symbol_frequencies_equal']:
                self.assertIsNone(empty[key])
            self.assertEqual(empty['shared_projection_groups'],0)

    def test_exhaustive_small_sequences_against_direct_string_and_group_oracle(self):
        sequences = [list(x) for n in range(4) for x in itertools.product(['a','b'],repeat=n)]
        for a,b in itertools.product(sequences,repeat=2):
            result = audit.compare_pair(rows(a), rows(b,historical=False))
            if a and b:
                self.assertEqual(result['nonempty_record_projection_order_equal'],a==b)
                self.assertEqual(result['nonempty_record_projection_bags_equal'],sorted(a)==sorted(b))
                self.assertEqual(result['joined_lowercase_streams_equal'],''.join(a)==''.join(b))
                self.assertEqual(result['lowercase_symbol_frequencies_equal'],sorted(''.join(a))==sorted(''.join(b)))
            self.assertEqual(result['shared_projection_groups'],len(set(a)&set(b)))
            groups = {g['projection_sha256']:g for g in result['projection_groups']}
            for s in set(a)|set(b):
                g=groups[audit.sha(s.encode())]
                self.assertEqual([r['source_order_index_zero_based_on_page'] for r in g['historical_H_records']],
                                 [i for i,x in enumerate(a) if x==s])
                self.assertEqual([r['source_order_index_zero_based_on_page'] for r in g['modern_IT2a_present_records']],
                                 [i for i,x in enumerate(b) if x==s])

    def test_digest_collision_fails_before_merging_groups(self):
        with patch.object(audit,'sha',return_value='same'):
            with self.assertRaisesRegex(ValueError,'collision'):
                audit.compare_pair(rows(['a','b']),rows(['a'],historical=False))

    def test_fixed_plan_numeric_flags_pairs_pins_and_duplicate_keys(self):
        original=json.loads((audit.ROOT/audit.PLAN).read_bytes())
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/audit.PLAN).parent.mkdir(parents=True)
            for key,value in [('schema_version',True),('schema_version',1.0),('apply_to_statistics',0),
                              ('untouched_evaluation',0),('candidate_pairs',[]),('accepted_page_aliases',['f101r1'])]:
                changed=dict(original); changed[key]=value; (root/audit.PLAN).write_text(json.dumps(changed))
                with self.assertRaisesRegex(ValueError,'plan changed'): audit.load_plan(root)
            (root/audit.PLAN).write_text('{"schema_version":1,"schema_version":1}')
            with self.assertRaisesRegex(ValueError,'Duplicate'): audit.load_plan(root)
        plan,_=audit.load_plan(audit.ROOT)
        self.assertEqual(len(plan['frozen_sha256']),11)
        with patch.object(audit,'sha',return_value='changed'):
            with self.assertRaisesRegex(ValueError,'frozen dependency changed'): audit.load_plan(audit.ROOT)

    def test_check_target_output_aliases_fail_before_calculation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'repo'; _,loaded=fixture(root); target=Path(d)/'checked.json'; target.write_bytes(b'preserve')
            symlink=Path(d)/'symlink'; symlink.symlink_to(target)
            hardlink=Path(d)/'hardlink'; os.link(target,hardlink)
            for output in [target,symlink,hardlink]:
                with patch.object(audit,'ROOT',root), patch.object(audit,'load_plan',return_value=({},b'{}')), \
                     patch.object(audit.parent,'load_inputs',return_value=loaded), \
                     patch.object(audit,'build',side_effect=AssertionError('must not calculate')) as producer, \
                     patch('sys.argv',['audit','--check',str(target),'--output',str(output)]), redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit): audit.main()
                producer.assert_not_called(); self.assertEqual(target.read_bytes(),b'preserve')

    def test_all_protected_paths_and_early_late_aliases_preserve_bytes(self):
        for stage in ['direct','symlink','hardlink','late_symlink','late_hardlink']:
            with tempfile.TemporaryDirectory() as d:
                root=Path(d)/'repo'; paths,loaded=fixture(root)
                for i,target in enumerate(paths):
                    output=target if stage=='direct' else Path(d)/f'out-{i}'
                    before=target.read_bytes()
                    def link():
                        if 'symlink' in stage: output.symlink_to(target)
                        else: os.link(target,output)
                    if stage in ['symlink','hardlink']: link()
                    def calculation(*args):
                        if stage.startswith('late_'): link()
                        return {'count':1}
                    with patch.object(audit,'ROOT',root), patch.object(audit,'load_plan',return_value=({},b'{}')), \
                         patch.object(audit.parent,'load_inputs',return_value=loaded), \
                         patch.object(audit,'build',side_effect=calculation) as producer, \
                         patch('sys.argv',['audit','--output',str(output)]), redirect_stderr(io.StringIO()):
                        with self.assertRaises(SystemExit): audit.main()
                    if not stage.startswith('late_'): producer.assert_not_called()
                    self.assertEqual(target.read_bytes(),before)

    def test_failed_check_and_serialization_aliases_preserve_output_and_sources(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'repo'; paths,loaded=fixture(root); check=Path(d)/'check.json'; output=Path(d)/'output.json'
            for text in ['{"count":true}','{"count":1.0}','{"count":1,"count":1}','{"count":NaN}']:
                check.write_text(text); output.write_bytes(b'preserve')
                with patch.object(audit,'ROOT',root), patch.object(audit,'load_plan',return_value=({},b'{}')), \
                     patch.object(audit.parent,'load_inputs',return_value=loaded), patch.object(audit,'build',return_value={'count':1}), \
                     patch('sys.argv',['audit','--check',str(check),'--output',str(output)]), redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit): audit.main()
                self.assertEqual(output.read_bytes(),b'preserve')
            for kind in ['symlink','hardlink']:
                target=paths[0]; before=target.read_bytes(); output.unlink()
                original_encoded=audit.parent.encoded
                def serialize(value):
                    if kind=='symlink': output.symlink_to(target)
                    else: os.link(target,output)
                    return original_encoded(value)
                with patch.object(audit,'ROOT',root), patch.object(audit,'load_plan',return_value=({},b'{}')), \
                     patch.object(audit.parent,'load_inputs',return_value=loaded), patch.object(audit,'build',return_value={'count':1}), \
                     patch.object(audit.parent,'encoded',side_effect=serialize), \
                     patch('sys.argv',['audit','--output',str(output)]), redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit): audit.main()
                self.assertEqual(target.read_bytes(),before)


if __name__=='__main__':
    unittest.main()
