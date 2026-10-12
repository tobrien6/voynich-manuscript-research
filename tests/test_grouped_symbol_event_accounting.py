from collections import Counter
import csv
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import io
import json
import math
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts import grouped_symbol_event_accounting as c


def arbitrary_row(key,counts,losses):
    roles=[]
    for role,count,values in zip(c.ROLES,counts,losses):
        gain=values[1]-values[2]
        roles.append({'role':role,'targets':count,'loss_bits_order0_order1_order2':values,
                      'gain12_bits':gain,'mean_gain12_bits_per_target':gain/count if count else None})
    total=[sum(v[j] for v in losses) for j in range(3)]
    targets=sum(counts)
    return {'locus_key':key,'group_id':key,'page_id':key,'fold':0,'tokens':counts[0],'units':sum(counts[:3]),
            'targets':targets,'loss_bits_order0_order1_order2':total,
            'gain01_bits_per_target':(total[0]-total[1])/targets,
            'gain12_bits_per_target':(total[1]-total[2])/targets,
            'unseen_order1_context_targets':0,'unseen_order2_context_targets':0,'roles':roles}


def reference_fixture():
    rows=[{'key':f'f{i+1}r.1','page':f'f{i+1}r','group':f'g{i}','segments':[['a','b'],['a']]}
          for i in range(5)]
    alphabet=(c.EOS,'a','b')
    qs=[(F(17,43),F(77,129),F(283,387)),(F(9,43),F(79,258),F(287,774)),
        (F(17,43),F(111,215),F(659,1075)),(F(17,43),F(77,129),F(283,387)),
        (F(17,43),F(37,86),F(39,86))]
    losses=[-math.fsum(math.log2(float(q[j])) for q in qs) for j in range(3)]
    counts={'alphabet':list(alphabet),'target_counts':[[c.EOS,8],['a',8],['b',4]],
            'first_counts':[[c.BOS,'a',8],['a',c.EOS,4],['a','b',4],['b',c.EOS,4]],
            'second_counts':[[c.BOS,c.BOS,'a',8],[c.BOS,'a',c.EOS,4],[c.BOS,'a','b',4],['a','b',c.EOS,4]]}
    def population(n):
        return {'loci':n,'tokens':2*n,'units':3*n,'targets':5*n,
                'loss_bits_order0_order1_order2':[n*v for v in losses],
                'pooled_gain01_bits_per_target':(losses[0]-losses[1])/5,
                'pooled_gain12_bits_per_target':(losses[1]-losses[2])/5,
                'locus_macro_gain01_bits_per_target':(losses[0]-losses[1])/5,
                'locus_macro_gain12_bits_per_target':(losses[1]-losses[2])/5,
                'unseen_order1_context_targets':0,'unseen_order2_context_targets':0}
    scores=[];folds=[];groups=[]
    for i,row in enumerate(rows):
        scores.append({'locus_key':row['key'],'page_id':row['page'],'group_id':row['group'],'fold':i,
                       **{k:v for k,v in population(1).items() if not k.startswith('pooled_')
                          and not k.startswith('locus_macro_') and k!='loci'},
                       'gain01_bits_per_target':population(1)['pooled_gain01_bits_per_target'],
                       'gain12_bits_per_target':population(1)['pooled_gain12_bits_per_target']})
        folds.append({'fold':i,'training_loci':4,'training_targets':20,
                      'training_group_ids':[f'g{j}' for j in range(5) if j!=i],'scoring_group_ids':[f'g{i}'],
                      'fitted_counts_sha256':c.sha(c.compact(counts)),'training_target_counts':counts['target_counts'],
                      'observed_order1_contexts':3,'observed_order2_contexts':3,**population(1)})
        groups.append({'group_id':f'g{i}','fold':i,**population(1)})
    summary={**population(5),'groups':5,'group_macro_gain01_bits_per_target':population(1)['pooled_gain01_bits_per_target'],
             'group_macro_gain12_bits_per_target':population(1)['pooled_gain12_bits_per_target'],
             'positive_order2_fold_count':5,'fixed_second_order_preference':True}
    return rows,{f'g{i}':i for i in range(5)},alphabet,{'loci':scores,'folds':folds,'groups':groups,'summary':summary}


class SymbolEventAccountingTests(unittest.TestCase):
    def test_roles_are_exhaustive_at_one_two_and_longer_tokens(self):
        all_events=[e for units in [['a'],['a','b'],['a','b','c']] for e in c.events(units)]
        self.assertEqual(Counter(e[3] for e in all_events),{'initial_unit':3,'second_unit':2,'later_unit':1,'termination':3})
        self.assertEqual(c.events(['a']),[(c.BOS,c.BOS,'a','initial_unit'),(c.BOS,'a',c.EOS,'termination')])
        self.assertEqual(c.events(['a','b','c'])[-2:], [('a','b','c','later_unit'),('b','c',c.EOS,'termination')])
        for units in [[],[c.BOS],[c.EOS]]:
            with self.assertRaises(ValueError):c.events(units)

    def test_literal_case_longest_match_does_not_cross_tokens(self):
        self.assertEqual(c.segment('YchIin',['ch','iin','in']),['Y','ch','I','in'])
        self.assertEqual(c.segment('iiin',['iin','iiin','in']),['iiin'])
        self.assertEqual(c.segment('c',['ch']),['c'])
        self.assertEqual(c.segment('h',['ch']),['h'])
        for token in ['','a?','é']:
            with self.assertRaises(ValueError):c.segment(token,[])

    def test_manual_rational_probabilities_and_role_loss_sums(self):
        model=c.fit([{'segments':[['a','b'],['a']]}],(c.EOS,'a','b'))
        self.assertEqual(c.probabilities(model,c.BOS,'a','b'),(F(3,13),F(61,234),F(605,2106)))
        row={'key':'f1r.1','page':'f1r','group':'u','segments':[['a','b']]}
        scored=c.score_row(row,model,0,{})
        self.assertEqual([r['targets'] for r in scored['roles']],[1,1,0,1])
        self.assertIsNone(scored['roles'][2]['mean_gain12_bits_per_target'])
        self.assertEqual(scored['roles'][2]['gain12_bits'],0)
        expected=[(F(5,13),F(53,117),F(541,1053)),(F(3,13),F(61,234),F(605,2106)),
                  (F(5,13),F(93,221),F(1709,3757))]
        for j in range(3):
            self.assertAlmostEqual(scored['loss_bits_order0_order1_order2'][j],
                -math.fsum(math.log2(float(p[j])) for p in expected))
        self.assertEqual(scored['targets'],scored['tokens']+scored['units'])

    def test_unequal_roles_groups_and_empty_classes_use_original_denominators(self):
        small=arbitrary_row('small',[1,0,0,1],[[2,2,1],[0,0,0],[0,0,0],[2,2,2]])
        big=arbitrary_row('big',[1,1,1,1],[[2,2,2],[2,2,2],[3,3,1],[2,1,2]])
        summary=c.aggregate([small,big]);groups=[c.aggregate([small]),c.aggregate([big])]
        c.add_group_contributions(summary,groups)
        self.assertAlmostEqual(summary['pooled_gain12_bits_per_target'],1/3)
        terms=[r['equal_group_contribution12_bits_per_target'] for r in summary['roles']]
        self.assertEqual(terms,[.25,0,.25,-.125])
        self.assertEqual(sum(terms),.375)
        self.assertEqual(summary['roles'][2]['groups_with_no_role_targets'],1)
        self.assertEqual(summary['roles'][2]['mean_gain12_bits_per_target'],2)
        self.assertIsNone(groups[0]['roles'][2]['mean_gain12_bits_per_target'])

    def test_all_folds_and_full_reference_fields_match_independent_hand_fixture(self):
        rows,assignments,alphabet,reference=reference_fixture()
        result=c.evaluate(rows,assignments,alphabet,reference)
        self.assertEqual(len(result['loci']),5)
        self.assertEqual(result['summary']['targets'],25)
        self.assertEqual([r['targets'] for r in result['summary']['roles']],[10,5,0,10])
        for f in result['folds']:
            self.assertFalse(set(f['training_group_ids'])&set(f['scoring_group_ids']))
        before=c.counts_record(c.fit([r for r in rows if assignments[r['group']]!=2],alphabet))
        rows[2]['segments']=[['b']]
        self.assertEqual(before,c.counts_record(c.fit([r for r in rows if assignments[r['group']]!=2],alphabet)))
        self.assertNotEqual(before,c.counts_record(c.fit([r for r in rows if assignments[r['group']]!=0],alphabet)))

    def test_reference_count_digest_loss_and_membership_drift_are_rejected(self):
        rows,assignments,alphabet,reference=reference_fixture()
        for mode in ['digest','loss','count','membership']:
            changed=deepcopy(reference)
            if mode=='digest':changed['folds'][0]['fitted_counts_sha256']='0'*64
            elif mode=='loss':changed['loci'][0]['loss_bits_order0_order1_order2'][1]+=.1
            elif mode=='count':changed['loci'][0]['targets']+=1
            else:changed['folds'][0]['scoring_group_ids']=['other']
            with self.subTest(mode=mode),self.assertRaises(ValueError):c.evaluate(rows,assignments,alphabet,changed)

    def test_fixed_plan_helper_and_reference_drift_stop_before_processing(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for path in c.PINS:
                (root/path).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(c.ROOT/path,root/path)
            (root/c.PLAN).write_bytes((root/c.PLAN).read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError,'fixed accounting plan'):c.validate_inputs(root)
            shutil.copyfile(c.ROOT/c.PLAN,root/c.PLAN)
            manifest=json.loads((root/c.INPUTS).read_text())
            for path in manifest['input_pins']:
                (root/path).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(c.ROOT/path,root/path)
            c.validate_inputs(root)
            helper=root/'scripts/ivtff.py';helper.write_bytes(helper.read_bytes()+b'\n# synthetic drift\n')
            with patch.object(c.parent,'make_report') as producer,self.assertRaisesRegex(ValueError,'reference input/helper'):
                c.build_report(root/'unused-reference',root)
            producer.assert_not_called()
            report=root/'reference';report.write_bytes(b'synthetic wrong reference')
            with self.assertRaisesRegex(ValueError,'numeric reference report'):c.load_reference(report,{'reference_report_sha256':'0'*64})
            with patch.object(c,'validate_inputs',side_effect=ValueError('input/helper drift')),\
                    patch.object(c.parent,'make_report') as producer,self.assertRaises(ValueError):c.build_report(report,root)
            producer.assert_not_called()

    def test_full_component_retains_unselected_transitive_leaf_and_canvases(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            canvases=[{'explicit_folio_sides':f'{i}r','canvas_uri':f'single:{i}'} for i in range(1,95)]
            canvases.extend([{'explicit_folio_sides':'2r;3r','canvas_uri':'bridge:23'},
                             {'explicit_folio_sides':'3v;4r','canvas_uri':'bridge:34'}])
            components=[{'group_id':'yale-leaves:2+3+4' if i==2 else f'yale-leaves:{i}',
                         'folio_ids':['2','3','4'] if i==2 else [str(i)]} for i in range(1,95) if i not in [3,4]]
            leaf_groups={leaf:comp['group_id'] for comp in components for leaf in comp['folio_ids']}
            by_leaf={str(i):{f'single:{i}'} for i in range(1,95)}
            by_leaf['2'].add('bridge:23');by_leaf['3'].update(['bridge:23','bridge:34']);by_leaf['4'].add('bridge:34')
            selected=[i for i in range(1,95) if i not in [3,94]]
            mapping={f'f{i}r.1':{'page_id':f'f{i}r'} for i in selected}
            image={'dependency_components':components,'indexed_canvas_ids_by_leaf':{k:sorted(v) for k,v in by_leaf.items()},
                   'pages':[{'page_id':f'f{i}r','side_reference_status':'side_references_matched','dependency_group':leaf_groups[str(i)]}
                            for i in selected]}
            declarations=[]
            for comp in components:
                leaves=comp['folio_ids'];pages=[f'f{i}r' for i in selected if str(i) in leaves]
                if not pages:continue
                g=comp['group_id']
                fold=int.from_bytes(hashlib.sha256(c.compact(['grouped-symbol-prediction-v1',20261012,g])).digest(),'big')%5
                declarations.append({'group_id':g,'fold':fold,'folio_ids':leaves,'source_page_ids':sorted(pages),
                    'locus_keys':sorted(page+'.1' for page in pages),
                    'canvas_ids':sorted({uri for leaf in leaves for uri in by_leaf[leaf]})})
            declarations.sort(key=lambda v:v['group_id'])
            ref={'folds':{'group_assignments':declarations,'manifest_sha256':c.sha(c.compact(declarations))}}
            path=root/'research/image-index/canvases.csv';path.parent.mkdir(parents=True)
            with path.open('w') as stream:
                writer=csv.DictWriter(stream,fieldnames=['explicit_folio_sides','canvas_uri']);writer.writeheader();writer.writerows(canvases)
            path=root/'research/folio-alignment/transcription-image-coverage.json';path.parent.mkdir(parents=True)
            path.write_bytes(c.encoded(image))
            assignments,pages,actual=c.derive_groups(sorted(mapping),mapping,root,ref)
            self.assertEqual(len(assignments),91);self.assertEqual(actual,declarations)
            self.assertEqual(pages['f2r'],pages['f4r'])
            joined=next(v for v in actual if v['group_id']=='yale-leaves:2+3+4')
            self.assertEqual(joined['folio_ids'],['2','3','4']);self.assertIn('single:3',joined['canvas_ids'])
            self.assertNotIn('f3r.1',joined['locus_keys'])
            bad=deepcopy(ref);bad['folds']['group_assignments'][0]['canvas_ids']=[]
            with self.assertRaises(ValueError):c.derive_groups(sorted(mapping),mapping,root,bad)

    def test_strict_json_and_lossless_gzip_have_no_filename_timestamp_or_optional_fields(self):
        data=c.encoded({'known':'synthetic','value':.125});raw=c.packed(data)
        self.assertEqual(c.unpack(raw),data)
        self.assertEqual(raw,c.packed(data))
        self.assertEqual(raw[3],0);self.assertEqual(raw[4:8],b'\0'*4)
        modified=bytearray(raw);modified[3]=8
        with self.assertRaises(ValueError):c.unpack(bytes(modified))
        for bad in ['{"x":1,"x":2}','{"x":NaN}','{"x":Infinity}']:
            with self.assertRaises(ValueError):c.load_split_json(bad)

    def test_existing_output_refused_before_build_and_new_output_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);reference=root/'ref';reference.write_bytes(b'synthetic numeric reference')
            output=root/'new';output.write_bytes(b'preserved synthetic input')
            argv=['account','--reference-report',str(reference),'--output',str(output)]
            with patch('sys.argv',argv),patch.object(c,'build_report') as build,\
                    redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):c.main()
            build.assert_not_called();self.assertEqual(output.read_bytes(),b'preserved synthetic input')
            output.unlink()
            result={'reference_report_sha256':c.sha(reference.read_bytes()),'implementation_sha256':c.sha(Path(c.__file__).read_bytes())}
            with patch('sys.argv',argv),patch.object(c,'build_report',return_value=result),\
                    patch.object(c,'validate_inputs'),redirect_stdout(io.StringIO()):c.main()
            self.assertEqual(c.unpack(output.read_bytes()),c.encoded(result))

    def test_late_symlink_and_hardlink_output_aliases_preserve_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);reference=root/'ref';reference.write_bytes(b'synthetic numeric reference')
            source=root/'source';source.write_bytes(b'preserved synthetic input')
            for kind in ['symlink','hardlink']:
                output=root/kind
                def build(*args):
                    if kind=='symlink':output.symlink_to(source)
                    else:output.hardlink_to(source)
                    return {'reference_report_sha256':c.sha(reference.read_bytes()),'implementation_sha256':c.sha(Path(c.__file__).read_bytes())}
                with patch('sys.argv',['account','--reference-report',str(reference),'--output',str(output)]),\
                        patch.object(c,'build_report',side_effect=build),patch.object(c,'validate_inputs'),\
                        redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):c.main()
                self.assertEqual(source.read_bytes(),b'preserved synthetic input')


if __name__=='__main__':unittest.main()
