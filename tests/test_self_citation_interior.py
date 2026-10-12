import contextlib
from copy import deepcopy
from fractions import Fraction
import hashlib
import io
import itertools
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import self_citation_interior as m


def policies():
    return json.loads((m.ROOT/m.SETTINGS).read_bytes())['policies']


def fixture(bodies=None):
    bodies=bodies or ['a bb ccc','a bb ccc dddd e','a bb c']
    raw=b'# synthetic header\n';ledger=[]
    for i,text in enumerate(bodies):
        body=text.encode();start=len(raw)
        ledger.append({'generated_row_index':i,'initialized_input_row':i==0,'native_file_line_number':i+2,
          'start_byte':start,'end_byte_exclusive_without_line_ending':start+len(body),'row_sha256':m.sha(body),
          'space_delimited_token_count':len(body.split(b' ')),
          'model_paragraph_initial':None if i==0 else False,'model_paragraph_final':None if i==0 else True,
          'source_lines_in_page_pre_call':None if i==0 else i,'source_lines_in_paragraph_pre_call':None if i==0 else i})
        raw+=body+b'\n'
    return raw,ledger


def simple_profile(value):
    return [{'policy_id':p,'scores':{scope:m.packed(value) for scope in m.SCOPES}} for p in m.POLICIES]


class SelfCitationInteriorTests(unittest.TestCase):
    def test_ledger_byte_intervals_all_rows_and_exclusions_are_preserved(self):
        raw,ledger=fixture();rows,audit=m.validate_rows(raw,ledger,3)
        self.assertEqual(rows,[('1',['a','bb','ccc','dddd','e'])])
        self.assertEqual(audit['newly_generated_rows'],2)
        self.assertEqual(audit['excluded_rows'],[{'row_index':0,'reason':'initialized_input','groups':3},
                                               {'row_index':2,'reason':'fewer_than_five_groups','groups':3}])
        self.assertEqual(audit['generated_group_count_histogram'],{3:1,5:1})

    def test_changed_index_interval_hash_count_and_flags_fail(self):
        raw,ledger=fixture()
        for field,value in [('generated_row_index',False),('start_byte',1),('row_sha256','0'*64),
                            ('space_delimited_token_count',4),('initialized_input_row',True),
                            ('model_paragraph_initial',None),('source_lines_in_page_pre_call',True)]:
            changed=deepcopy(ledger);changed[1][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):m.validate_rows(raw,changed,3)
        for changed in (ledger[:-1],list(reversed(ledger)),ledger+[ledger[1]]):
            with self.assertRaises(ValueError):m.validate_rows(raw,changed,3)

    def test_unsupported_short_notation_is_not_silently_excluded(self):
        for text in ('a ? b','a  b',' a b','a b ','a.b'):
            raw,ledger=fixture(['a b c',text])
            with self.subTest(text=text),self.assertRaises(ValueError):m.validate_rows(raw,ledger,2)

    def test_common_minimum_uses_all_variants_without_selecting_from_scores(self):
        maps={(s,p):{'a':{'tokens':['x']*5},'b':{'tokens':['x']*6}}
              for s in m.prefix.SOURCE_IDS for p in m.prefix.SPACING}
        maps['ZL3b','join']['b']['tokens']=['x']*4
        selected,excluded=m.select_minimum(maps,['a','b'])
        self.assertEqual(selected,['a']);self.assertEqual(excluded,[{'locus_key':'b','reasons':['ZL3b/join:fewer_than_five_tokens']}])
        changed=deepcopy(maps);del changed['IT2a','split']['a']
        with self.assertRaises(ValueError):m.select_minimum(changed,['a','b'])

    def test_exact_known_scores_and_equal_row_weight(self):
        rows=[('linear',['x','a','bb','ccc','y']),('constant',['x','a','b','c','d','e','y'])]
        measured=m.measure(rows,policies())[0]
        self.assertEqual(m.unpack(measured['scores']['unrestricted']),Fraction(1,4))
        self.assertEqual(m.unpack(measured['scores']['half']),Fraction(3,16))
        self.assertEqual(measured['rows'],2);self.assertEqual(measured['constant_interiors'],1)
        self.assertEqual(measured['interior_groups'],8);self.assertEqual(measured['interior_pairs'],6)

    def test_grouping_case_boundaries_and_both_constant_transitions(self):
        rows=[('collapse',['left','ch','a','sh','right']),('reverse',['left','ch','aa','sh','right'])]
        results=m.measure(rows,policies())
        self.assertEqual([r['constant_interiors'] for r in results],[1,1,1])
        self.assertTrue(all(r['rows']==2 for r in results))
        self.assertEqual([r['constant_interiors'] for r in m.measure(rows[:1],policies())],[0,1,1])
        self.assertEqual([r['constant_interiors'] for r in m.measure(rows[1:],policies())],[1,0,0])
        single=m.measure([('case',['left','Ch','iin','cthh','right'])],policies())
        self.assertEqual([r['scope_audit']['pattern_hits'].get('Ch',0) for r in single],[0,1,1])
        self.assertTrue(all(r['scope_audit']['pattern_hits'].get('cph',0)==0 for r in single))

    def test_half_centering_matches_exhaustive_small_ensemble(self):
        values=[1,3,2,1,1];split=3
        def raw_r(v):
            n=len(v);s=sum(v);d=[n*x-s for x in v];q=sum(x*x for x in d)
            return Fraction(n*sum(a*b for a,b in zip(d,d[1:])),(n-1)*q) if q else Fraction(0)
        ensemble=[a+b for a in itertools.permutations(values[:split]) for b in itertools.permutations(values[split:])]
        expected=sum(map(raw_r,ensemble),Fraction(0))/len(ensemble)
        native=['endpoint',*['a'*x for x in values],'endpoint']
        result=m.measure([('row',native)],policies())[0]
        self.assertEqual(m.unpack(result['half_expectation']),expected)
        self.assertEqual(m.unpack(result['scores']['half']),raw_r(values)-expected)

    def test_empty_eligibility_remains_explicitly_undefined(self):
        results=m.measure([],policies())
        self.assertTrue(all(r['rows']==0 and r['half_invariance'] is None for r in results))
        self.assertTrue(all(r['scores']=={'unrestricted':None,'half':None} for r in results))

    def test_all_seed_ranges_inclusive_endpoints_and_exact_gaps(self):
        targets=[{'source_id':s,'spacing':p,'policies':simple_profile(Fraction(1))}
                 for s in m.prefix.SOURCE_IDS for p in m.prefix.SPACING]
        cases=[{'seed':seed,'policies':simple_profile(Fraction(seed,31))} for seed in m.SEEDS]
        result=m.ranges(targets,cases)
        self.assertEqual(len(result),24);self.assertTrue(all(r['within_fixed_seed_range'] for r in result))
        targets[0]['policies'][0]['scores']['half']=m.packed(Fraction(3,2))
        result=m.ranges(targets,cases)
        missed=next(r for r in result if r['source_id']=='ZL3b' and r['spacing']=='split' and r['policy_id']=='ascii_letters' and r['scope']=='half')
        self.assertFalse(missed['within_fixed_seed_range']);self.assertEqual(m.unpack(missed['outside_range_gap']),Fraction(1,2))

    def test_one_undefined_seed_is_retained_and_blocks_only_corresponding_ranges(self):
        targets=[{'source_id':s,'spacing':p,'policies':simple_profile(Fraction(0))}
                 for s in m.prefix.SOURCE_IDS for p in m.prefix.SPACING]
        cases=[{'seed':seed,'policies':simple_profile(Fraction(0))} for seed in m.SEEDS]
        cases[7]['policies'][2]['scores']['half']=None
        result=m.ranges(targets,cases)
        self.assertEqual(len(cases),31)
        self.assertEqual(sum(r['within_fixed_seed_range'] is None for r in result),4)
        for invalid in (cases[:-1],cases+cases[:1],list(reversed(cases))):
            with self.assertRaises(ValueError):m.ranges(targets,invalid)

    def test_changed_artifact_pin_fails_before_measurement(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);pins=root/m.PINS;pins.parent.mkdir(parents=True)
            (root/'fixture.txt').write_text('changed');pins.write_text(json.dumps({'fixture.txt':m.sha(b'original')}))
            with patch.object(m,'PIN_MANIFEST_SHA256',m.sha(pins.read_bytes())),self.assertRaisesRegex(ValueError,'frozen artifact/helper changed'):
                m.load_inputs(root)
            with self.assertRaisesRegex(ValueError,'frozen pin manifest changed'):m.load_inputs(root)

    def test_complete_replay_preserves_json_scalar_types(self):
        self.assertFalse(m.same_json({'count':1},{'count':True}))
        self.assertFalse(m.same_json({'score':0.0},{'score':0}))
        self.assertTrue(m.same_json({'a':[1,False],'b':None},{'b':None,'a':[1,False]}))
        self.assertTrue(m.same_json({5:1,10:2},{'10':2,'5':1}))
        value=Fraction(10**5000+1,10**5001+1)
        self.assertEqual(m.unpack(m.packed(value)),value)

    def test_every_fixed_run_receipt_is_verified_before_measurement(self):
        with tempfile.TemporaryDirectory() as folder:
            runs=Path(folder);raw,ledger=fixture();ledger_raw=json.dumps(ledger).encode()
            cases=[]
            for seed in m.SEEDS:
                cases.append({'seed':seed,'accepted':True,'complete_control_observed_bytes_equal':True,
                              'output_sha256':{mode:m.sha(raw) for mode in ('control','observed')},
                              'effective_configuration_sha256':m.sha(b'synthetic'),
                              'row_ledger_sha256':m.sha(ledger_raw),'total_output_rows':3,
                              'processes':{mode:{'returncode':0,'timed_out':False,'stdout_sha256':m.sha(b''),
                                                 'stderr_sha256':m.sha(b'')} for mode in ('control','observed')}})
                for mode in ('control','observed'):
                    destination=runs/f'seed-{seed:02d}'/mode;(destination/'output').mkdir(parents=True)
                    (destination/'output/generated.txt').write_bytes(raw)
                    (destination/'conf.properties').write_bytes(b'synthetic')
                    (destination/'process.stdout').write_bytes(b'');(destination/'process.stderr').write_bytes(b'')
                    if mode=='observed':(destination/'ledger.json').write_bytes(ledger_raw)
            parent={'cases':cases}
            self.assertEqual(len(m.verified_runs(runs,parent)),31)
            last=runs/'seed-31'
            for relative in ('control/output/generated.txt','observed/conf.properties','control/process.stderr','observed/ledger.json'):
                path=last/relative;before=path.read_bytes();path.write_bytes(b'changed')
                with patch.object(m,'load_inputs',return_value=(parent,{}, {},'pin')),patch.object(m,'measure') as measure:
                    with self.subTest(relative=relative),self.assertRaises(ValueError):m.report(runs)
                    measure.assert_not_called()
                path.write_bytes(before)

    def test_run_code_catalog_native_aliases_and_new_existing_outputs_are_protected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)/'root';root.mkdir();runs=Path(folder)/'runs';runs.mkdir()
            source=root/'native.txt';source.write_text('synthetic source')
            catalog=root/'data/transliterations.json';catalog.parent.mkdir();catalog.write_text(json.dumps({'sources':[{'path':'native.txt'}]}))
            pins=root/m.PINS;pins.parent.mkdir(parents=True);pins.write_text(json.dumps({'data/transliterations.json':m.sha(catalog.read_bytes())}))
            plan=root/m.PLAN;plan.write_text('synthetic plan');artifact=runs/'generated.txt';artifact.write_text('synthetic output')
            for i,path in enumerate((source,catalog,pins,plan,artifact,Path(m.__file__))):
                alias=root/f'alias-{i}';alias.hardlink_to(path)
                with self.assertRaises(ValueError):m.protect_output(alias,runs,root)
                with self.assertRaises(ValueError):m.protect_output(path,runs,root)
            m.protect_output(root/'new-report.json',runs,root)

    def test_writer_refuses_existing_output_before_analysis_and_rechecks_late_alias(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'report.json';output.write_text('preserve')
            with patch('sys.argv',['comparison','--runs',folder,'--new-report',str(output)]),patch.object(m,'protect_output'), \
                    patch.object(m,'report') as calculate,contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
                m.main()
            calculate.assert_not_called();self.assertEqual(output.read_text(),'preserve')
            output.unlink();source=Path(folder)/'input.txt';source.write_text('preserve')
            def calculate(_):
                output.hardlink_to(source)
                return {}
            with patch('sys.argv',['comparison','--runs',folder,'--new-report',str(output)]), \
                    patch.object(m,'protect_output',side_effect=[None,ValueError('late alias')]) as guard, \
                    patch.object(m,'report',side_effect=calculate),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
                m.main()
            self.assertEqual(guard.call_count,2);self.assertEqual(source.read_text(),'preserve')


if __name__=='__main__':
    unittest.main()
