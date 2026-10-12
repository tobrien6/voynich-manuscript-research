import contextlib
from copy import deepcopy
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from scripts import plot_generator_interior_comparison as m

FIGURES=m.ROOT/'research/literature/figures/generator-interior-comparison'


class GeneratorInteriorFigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prior,cls.sized=[m.load_split_json((m.ROOT/name).read_text()) for name in m.INPUTS]

    def test_all48_points_and24_undefined_ranges_preserve_exact_memberships(self):
        data=m.figure_data(self.prior,self.sized)
        self.assertEqual((len(data['prior_plotted_comparisons']),len(data['supported_plotted_comparisons']),len(data['primary_undefined_comparisons'])),(24,24,24))
        self.assertEqual((data['prior_source_loci'],data['common_source_loci']),(1590,1426))
        self.assertEqual([v['complete_seeds'] for v in data['primary_seeds_with_complete_size_support']],[3,12,9,9])
        self.assertEqual(sum(p['within_fixed_seed_range'] for p in data['prior_plotted_comparisons']),0)
        self.assertEqual([(p['source_id'],p['spacing'],p['policy_id'],p['scope']) for p in data['supported_plotted_comparisons'] if p['within_fixed_seed_range']],
                         [('ZL3b','join','bench_sequences','unrestricted'),('ZL3b','join','bench_sequences','half')])
        for item in data['prior_plotted_comparisons']+data['supported_plotted_comparisons']:
            for field in ('target','seed_minimum','seed_maximum'):
                self.assertLess(data['shared_x_limits'][0],float(m.unpack(item[field])))
                self.assertGreater(data['shared_x_limits'][1],float(m.unpack(item[field])))

    def test_missing_comparison_or_fixed_seed_is_not_silently_omitted(self):
        for mutation in ('prior_point','supported_point','prior_seed','supported_seed'):
            prior,sized=deepcopy(self.prior),deepcopy(self.sized)
            if mutation=='prior_point':prior['comparisons'].pop()
            elif mutation=='supported_point':sized['supported_common']['comparisons'].pop()
            elif mutation=='prior_seed':prior['cases'].pop()
            else:sized['supported_common']['cases'].pop()
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):m.figure_data(prior,sized)

    def test_changed_exact_endpoint_membership_and_scalar_types_are_rejected(self):
        for mutation in ('endpoint','membership','boolean_mean','boolean_schema'):
            prior=deepcopy(self.prior)
            if mutation=='endpoint':prior['comparisons'][0]['seed_maximum']={'numerator':'0','denominator':'1','mean':0.0}
            elif mutation=='membership':prior['comparisons'][0]['within_fixed_seed_range']=True
            elif mutation=='boolean_mean':prior['comparisons'][0]['target']['mean']=True
            else:prior['schema_version']=True
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):m.figure_data(prior,self.sized)

    def test_undefined_full_family_cannot_be_painted_as_a_failure_or_numeric_range(self):
        for mutation in ('false_criterion','numeric_range','missing_support_score','source_point'):
            sized=deepcopy(self.sized);full=sized['primary']
            if mutation=='false_criterion':full['all_target_points_within_fixed_seed_ranges']=False
            elif mutation=='numeric_range':full['comparisons'][0]['seed_minimum']={'numerator':'0','denominator':'1','mean':0.0}
            elif mutation=='missing_support_score':full['cases'][1]['standardized'][0]['policies'][0]['scores']['half']={'numerator':'0','denominator':'1','mean':0.0}
            else:full['comparisons'][0]['target']={'numerator':'0','denominator':'1','mean':0.0}
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):m.figure_data(self.prior,sized)

    def test_wrong_common_denominator_and_display_mean_fail(self):
        sized=deepcopy(self.sized);sized['supported_common']['targets'][0]['target_rows']=True
        with self.assertRaises(ValueError):m.figure_data(self.prior,sized)
        with self.assertRaises(ValueError):m.unpack({'numerator':'1','denominator':'3','mean':0.334})

    def test_pinned_input_failure_precedes_rendering(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);output=root/'exports'
            for name in m.INPUTS:
                p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('{}')
            with patch.object(m,'ROOT',root),patch.object(m,'render') as render, \
                    patch('sys.argv',['figure','--new-output-dir',str(output)]),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):m.main()
            render.assert_not_called();self.assertFalse(output.exists())

    def test_existing_output_directory_is_refused_before_any_source_read(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(m,'read_data') as read,patch.object(m,'render') as render, \
                    patch('sys.argv',['figure','--new-output-dir',folder]),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):m.main()
            read.assert_not_called();render.assert_not_called()

    def test_late_symlink_hardlink_aliases_leave_input_and_other_outputs_unchanged(self):
        for kind in ('symlink','hardlink'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as folder:
                root=Path(folder);source=root/'source.json';source.write_text('preserve');output=root/'exports'
                def renderer(_):
                    output.mkdir();alias=output/(m.STEM+'.svg')
                    if kind=='symlink':alias.symlink_to(source)
                    else:alias.hardlink_to(source)
                    return {'png':b'synthetic','svg':b'synthetic','json':b'{}'}
                with patch.object(m,'read_data',return_value={}),patch.object(m,'render',side_effect=renderer), \
                        patch.object(m,'verify_export_transition',return_value=True), \
                        patch('sys.argv',['figure','--new-output-dir',str(output)]),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):m.main()
                self.assertEqual(source.read_text(),'preserve')
                self.assertFalse((output/(m.STEM+'.png')).exists());self.assertFalse((output/(m.STEM+'.json')).exists())

    def test_late_parent_symlink_redirect_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);parent=root/'parent';parent.mkdir();other=root/'other';other.mkdir();output=parent/'exports'
            def renderer(_):
                parent.rmdir();parent.symlink_to(other,target_is_directory=True)
                return {'png':b'synthetic','svg':b'synthetic','json':b'{}'}
            with patch.object(m,'read_data',return_value={}),patch.object(m,'render',side_effect=renderer), \
                        patch.object(m,'verify_export_transition',return_value=True), \
                    patch('sys.argv',['figure','--new-output-dir',str(output)]),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):m.main()
            self.assertFalse((other/'exports').exists())

    def test_failed_render_leaves_no_output_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'exports'
            with patch.object(m,'read_data',return_value={}),patch.object(m,'render',side_effect=ValueError('synthetic failure')), \
                    patch('sys.argv',['figure','--new-output-dir',str(output)]),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):m.main()
            self.assertFalse(output.exists())

    def test_exports_actual_artist_positions_hashes_dimensions_and_svg_references(self):
        provenance=json.loads((FIGURES/(m.STEM+'.json')).read_text())
        data=m.figure_data(self.prior,self.sized)
        for key,value in data.items():self.assertEqual(provenance[key],value)
        self.assertEqual(len(provenance['artist_positions']),48)
        for artist in provenance['artist_positions']:
            identity=tuple(artist[k] for k in ('source_id','spacing','policy_id','scope'))
            item=next(p for p in data[artist['family']] if tuple(p[k] for k in ('source_id','spacing','policy_id','scope'))==identity)
            y=m.POLICIES.index(artist['policy_id'])*2+m.SCOPES.index(artist['scope'])
            self.assertEqual(artist['source_xy'],[float(m.unpack(item['target'])),y])
            self.assertEqual(artist['range_x'],[float(m.unpack(item['seed_minimum'])),float(m.unpack(item['seed_maximum']))])
            self.assertEqual(artist['range_y'],[y,y])
        for ext in ('png','svg'):
            self.assertEqual(hashlib.sha256((FIGURES/(m.STEM+'.'+ext)).read_bytes()).hexdigest(),provenance['output_sha256'][ext])
        png=(FIGURES/(m.STEM+'.png')).read_bytes()
        self.assertEqual(png[:8],bytes([137,80,78,71,13,10,26,10]));self.assertEqual(struct.unpack('>II',png[16:24]),(2720,1856))
        raw=(FIGURES/(m.STEM+'.svg')).read_text();tree=ET.fromstring(raw)
        self.assertNotIn('/Users/',raw);self.assertNotIn('file://',raw)
        self.assertFalse(any(node.tag.endswith('image') or node.tag.endswith('script') for node in tree.iter()))
        self.assertTrue(all(not key.endswith('href') or value.startswith('#') for node in tree.iter() for key,value in node.attrib.items()))
        text=' '.join(tree.itertext())
        for phrase in ('all 24 seed ranges undefined','3/31','12/31','2/24 points inside range','Bench+minim / half'):
            self.assertIn(phrase,text)
        self.assertEqual(provenance['renderer']['script_sha256'],hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest())

    def test_long_fraction_parser_does_not_change_global_integer_guard(self):
        from scripts.self_citation_interior import packed
        before=sys.get_int_max_str_digits()
        value=Fraction(10**21000+17,10**21001+31)
        self.assertEqual(m.unpack(packed(value)),value)
        self.assertEqual(sys.get_int_max_str_digits(),before)

    def test_first_figure_transition_rejects_pixel_artist_environment_or_identity_drift(self):
        output={ext:(FIGURES/(m.STEM+'.'+ext)).read_bytes() for ext in ('png','svg','json')}
        self.assertTrue(m.verify_export_transition(output))
        for mutation in ('png','svg','artist','environment','input'):
            changed=dict(output)
            if mutation in ('png','svg'):changed[mutation]+=b'changed'
            else:
                data=json.loads(changed['json'])
                if mutation=='artist':data['artist_positions'][0]['source_xy'][0]=0.
                elif mutation=='environment':data['renderer']['python']='different'
                else:data['input_report_sha256']={}
                changed['json']=json.dumps(data).encode()
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):m.verify_export_transition(changed)


if __name__=='__main__':unittest.main()
