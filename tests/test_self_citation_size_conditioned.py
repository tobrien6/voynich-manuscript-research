import contextlib
from copy import deepcopy
from fractions import Fraction
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import self_citation_size_conditioned as m


def policies():
    return json.loads((m.ROOT/m.parent.SETTINGS).read_text())['policies']


def simple_profiles(value):
    return [m.pack_profile(pid,[value]*5) for pid in m.parent.POLICIES]


def targets(value):
    return [{'source_id':s,'spacing':p,'policies':simple_profiles(value)} for s,p in m.VARIANTS]


def cases():
    return [{'seed':seed,'standardized':targets(Fraction(seed,31))} for seed in m.parent.SEEDS]


class SizeConditionedTests(unittest.TestCase):
    def test_exact_size_is_original_group_count_under_every_unit_policy(self):
        rows=[('row',['left','ch','a','sh','right'])]
        cells=m.cell_profiles(rows,policies(),[5,6])
        self.assertEqual([(c['original_group_count'],c['rows']) for c in cells],[(5,1),(6,0)])
        self.assertEqual([p['interior_groups'] for p in cells[0]['policies']],[3,3,3])
        self.assertEqual([p['constant_interiors'] for p in cells[0]['policies']],[0,1,1])
        self.assertTrue(all(p['scores']['half'] is None for p in cells[1]['policies']))

    def test_rational_weighting_uses_target_counts_not_model_cell_frequencies(self):
        rows=[('five',['x','a','aa','aaa','x']),('six',['x','a','aa','aaa','aaaa','x'])]
        cells=m.cell_profiles(rows,policies(),[5,6])
        result=m.weighted(cells,{5:2,6:1})
        self.assertEqual(m.parent.unpack(result['policies'][0]['scores']['unrestricted']),Fraction(5,9))
        self.assertEqual(m.parent.unpack(result['policies'][0]['scores']['half']),Fraction(19,60))
        self.assertEqual([m.parent.unpack(w['weight']) for w in result['weights']],[Fraction(2,3),Fraction(1,3)])

    def test_cell_decomposition_reassembles_every_parent_mean_with_constants_retained(self):
        rows=[('five',['x','a','aa','aaa','x']),('constant',['x','a','b','c','d','e','x'])]
        cells=m.cell_profiles(rows,policies(),[5,7]);expected=m.parent.measure(rows,policies())
        self.assertTrue(m.verify_reassembly(cells,expected))
        result=m.weighted(cells,{5:1,7:1})
        self.assertEqual(m.parent.unpack(result['policies'][0]['scores']['unrestricted']),Fraction(1,4))
        altered=deepcopy(expected);altered[0]['scores']['half']=m.parent.packed(Fraction(0))
        with self.assertRaisesRegex(ValueError,'reassemble'):m.verify_reassembly(cells,altered)

    def test_missing_required_size_preserves_weight_and_undefined_values(self):
        cells=m.cell_profiles([('five',['x','a','aa','aaa','x'])],policies(),[5,6])
        result=m.weighted(cells,{5:9,6:1})
        self.assertFalse(result['all_required_sizes_supported'])
        self.assertEqual(result['missing_required_sizes'][0]['original_group_count'],6)
        self.assertEqual(m.parent.unpack(result['missing_required_sizes'][0]['target_weight']),Fraction(1,10))
        self.assertTrue(all(p['scores']=={'unrestricted':None,'half':None} for p in result['policies']))

    def test_empty_target_weights_remain_explicitly_undefined(self):
        result=m.weighted([],{});self.assertEqual(result['target_rows'],0)
        self.assertFalse(result['all_required_sizes_supported'])
        self.assertTrue(all(m.values(p)==[None]*5 for p in result['policies']))

    def test_common_support_is_count_only_all_seeds_and_all_source_variants(self):
        sources={variant:[('a',['x']*5),('b',['x']*5)] for variant in m.VARIANTS}
        sources['IT2a','join'][1]=('b',['x']*6)
        counts=[{'seed':seed,'counts':{5:10,6:1}} for seed in m.parent.SEEDS]
        counts[-1]['counts']={5:9}
        selection=m.common_support(sources,counts)
        self.assertEqual(selection['common_generator_sizes'],[5]);self.assertEqual(selection['selected_keys'],['a'])
        self.assertEqual(selection['excluded_keys'][0]['reasons'],[{'source_id':'IT2a','spacing':'join','original_group_count':6,'missing_model_seeds':[31]}])
        self.assertEqual(m.parent.unpack(selection['coverage']),Fraction(1,2))
        with self.assertRaises(ValueError):m.common_support(sources,counts[:-1])
        changed=deepcopy(counts);changed[0]['counts'][5]=False
        with self.assertRaises(ValueError):m.common_support(sources,changed)

    def test_no_common_model_size_preserves_empty_common_source_cohort(self):
        sources={variant:[('a',['x']*5)] for variant in m.VARIANTS}
        counts=[{'seed':seed,'counts':{5 if seed<31 else 6:1}} for seed in m.parent.SEEDS]
        selected=m.common_support(sources,counts)
        self.assertEqual(selected['selected_keys'],[])
        self.assertEqual(m.parent.unpack(selected['coverage']),Fraction(0))

    def test_unique_native_keys_positive_weights_and_complete_policy_cells_required(self):
        for rows in ([('a',['x']*5),('a',['x']*5)],[('a',['x']*4)]):
            with self.assertRaises(ValueError):m.histogram(rows)
        for weights in ({5:True},{4:1},{5:0},{5:-1}):
            with self.assertRaises(ValueError):m.weighted([],weights)
        with self.assertRaises(ValueError):m.weighted([{'original_group_count':5,'rows':1,'policies':[]}],{5:1})
        with self.assertRaises(ValueError):m.cell_profiles([('a',['x']*5)],policies(),[6])

    def test_all24_exact_ranges_and_endpoint_membership(self):
        result=m.comparisons(targets(Fraction(1)),cases())
        self.assertEqual(len(result['comparisons']),24)
        self.assertTrue(result['all_target_points_within_fixed_seed_ranges'])
        points=targets(Fraction(1));points[0]['policies'][0]['scores']['half']=m.parent.packed(Fraction(3,2))
        result=m.comparisons(points,cases());miss=result['comparisons'][1]
        self.assertFalse(miss['within_fixed_seed_range'])
        self.assertEqual(m.parent.unpack(miss['outside_range_gap']),Fraction(1,2))
        self.assertFalse(result['all_target_points_within_fixed_seed_ranges'])

    def test_undefined_seed_is_not_dropped_and_global_criterion_is_null(self):
        models=cases();models[5]['standardized'][2]['policies'][1]['scores']['half']=None
        result=m.comparisons(targets(Fraction(1)),models)
        self.assertEqual(len(models),31)
        self.assertIsNone(result['all_target_points_within_fixed_seed_ranges'])
        self.assertEqual(sum(c['within_fixed_seed_range'] is None for c in result['comparisons']),1)
        for invalid in (models[:-1],models+models[:1],list(reversed(models))):
            with self.assertRaises(ValueError):m.comparisons(targets(Fraction(1)),invalid)

    def test_changed_pin_fails_before_parent_replay_or_new_measurement(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);pins=root/m.PINS;pins.parent.mkdir(parents=True)
            (root/'fixture.txt').write_text('changed');pins.write_text(json.dumps({'fixture.txt':m.parent.sha(b'original')}))
            with patch.object(m,'ROOT',root),patch.object(m,'PIN_SHA256',m.parent.sha(pins.read_bytes())),patch.object(m.parent,'report') as replay:
                with self.assertRaisesRegex(ValueError,'input changed'):m.report(root/'runs')
                replay.assert_not_called()
            with patch.object(m,'ROOT',root),self.assertRaisesRegex(ValueError,'manifest changed'):m.load_inputs()

    def test_new_inputs_plan_and_code_direct_symlink_and_hardlink_aliases(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);pins=root/m.PINS;pins.parent.mkdir(parents=True)
            inputs=[root/'parent.json',root/m.PLAN]
            for path in inputs:path.write_text('synthetic')
            pins.write_text(json.dumps({str(path.relative_to(root)):m.parent.sha(path.read_bytes()) for path in inputs}))
            with patch.object(m,'ROOT',root),patch.object(m.parent,'protect_output'):
                for i,source in enumerate(inputs+[pins,Path(m.__file__)]):
                    hard=root/f'hard-{i}';hard.hardlink_to(source);symbolic=root/f'symbolic-{i}';symbolic.symlink_to(source)
                    for path in (source,hard,symbolic):
                        with self.subTest(path=path.name),self.assertRaises(ValueError):m.protect_output(path,root/'runs')
                m.protect_output(root/'new.json',root/'runs')

    def test_writer_refuses_existing_output_before_analysis_and_preserves_late_alias(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);pins=root/m.PINS;pins.parent.mkdir(parents=True)
            source=root/m.PLAN;source.write_text('preserve')
            pins.write_text(json.dumps({m.PLAN:m.parent.sha(source.read_bytes())}))
            output=root/'result.json';output.write_text('existing')
            with patch.object(m,'ROOT',root),patch.object(m.parent,'protect_output'),patch.object(m,'report') as calculate, \
                    patch('sys.argv',['size','--runs',folder,'--new-report',str(output)]),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
                m.main()
            calculate.assert_not_called();self.assertEqual(output.read_text(),'existing');output.unlink()
            def calculate(_):
                output.hardlink_to(source)
                return {}
            error=io.StringIO()
            with patch.object(m,'ROOT',root),patch.object(m.parent,'protect_output'),patch.object(m,'report',side_effect=calculate), \
                    patch.object(m.transition,'verify_result',return_value=[]) as transition, \
                    patch('sys.argv',['size','--runs',folder,'--new-report',str(output)]),contextlib.redirect_stderr(error),self.assertRaises(SystemExit) as exit_error:
                m.main()
            transition.assert_called_once_with({},root)
            self.assertEqual(exit_error.exception.code,1)
            self.assertIn('output aliases size-standardization inputs',error.getvalue())
            self.assertEqual(source.read_text(),'preserve');self.assertEqual(output.read_text(),'preserve')

    def test_cli_saved_report_scalar_types_are_not_coerced(self):
        with tempfile.TemporaryDirectory() as folder:
            saved=Path(folder)/'report.json';saved.write_text('{"count":false}')
            error=io.StringIO()
            with patch.object(m,'report',return_value={'count':0}),patch('sys.argv',['size','--runs',folder,'--check',str(saved)]), \
                    patch.object(m.transition,'verify_result',return_value=[]) as transition, \
                    contextlib.redirect_stderr(error),self.assertRaises(SystemExit) as exit_error:m.main()
            transition.assert_called_once_with({'count':0},m.ROOT)
            self.assertEqual(exit_error.exception.code,1)
            self.assertIn('complete size-conditioned report differs from replay',error.getvalue())
            self.assertEqual(saved.read_text(),'{"count":false}')

    def test_cli_accepts_valid_typed_cache_after_transition_validation(self):
        expected={'count':0,'mean':1.0}
        with tempfile.TemporaryDirectory() as folder:
            saved=Path(folder)/'report.json';raw=json.dumps(expected,sort_keys=True);saved.write_text(raw)
            with patch.object(m,'report',return_value=expected),patch('sys.argv',['size','--runs',folder,'--check',str(saved)]), \
                    patch.object(m.transition,'verify_result',return_value=[]) as transition,contextlib.redirect_stdout(io.StringIO()):
                m.main()
            transition.assert_called_once_with(expected,m.ROOT)
            self.assertEqual(saved.read_text(),raw)


if __name__=='__main__':
    unittest.main()
