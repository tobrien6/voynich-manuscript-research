import contextlib
from copy import deepcopy
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

from scripts import plot_native_substitution_rankings as m

FIGURES=m.ROOT/'research/literature/figures/native-substitution-rankings'


class NativeRankingFigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record=json.loads(m.REPORT.read_text())

    def test_all35_sources_70_rankings_and_winner_specific_masses_retained(self):
        data=m.figure_data(self.record)
        self.assertEqual(len(data['rows']),35)
        self.assertEqual(data['changed_maximizing_sets'],21)
        for row in data['rows']:
            for metric in m.METRICS:
                original=next(r for r in self.record['rankings'] if r['source_symbol']==row['source_symbol'] and r['metric']==metric)
                self.assertEqual(row[metric]['ranking'],original)
                for winner in row[metric]['winners']:
                    pair=next(p for p in self.record['pairs'] if set(p['symbols'])=={row['source_symbol'],winner['partner']})
                    self.assertEqual(winner['affected_occurrences'],pair['selected_occurrences'])
                    self.assertEqual(winner['score_bits_decimal_80digits'],pair[metric+'_score_bits_decimal_80digits'])
                    self.assertEqual(winner['all_occurrences'],17597)
        b=next(r for r in data['rows'] if r['source_symbol']=='B')
        self.assertEqual([(b[k]['winners'][0]['partner'],b[k]['winners'][0]['affected_occurrences']) for k in m.METRICS],[('P',3304),('F',5972)])

    def test_no_positive_optimum_retains_zero_scores_without_a_chosen_partner(self):
        row=next(r for r in m.figure_data(self.record)['rows'] if r['source_symbol']=='1')
        for metric in m.METRICS:
            self.assertEqual(row[metric]['winners'],[])
            self.assertEqual(row[metric]['score_x'],0)
            self.assertEqual(len(row[metric]['ranking']['possible_maximizers']),34)
        self.assertFalse(row['maximizing_sets_differ'])

    def test_missing_pair_ranking_or_source_comparison_fails(self):
        for field in ('pairs','rankings','normalization_comparisons'):
            altered=deepcopy(self.record);altered[field].pop()
            with self.subTest(field=field),self.assertRaises(ValueError):m.figure_data(altered)

    def test_wrong_scalar_display_winner_or_change_flag_fails(self):
        for mutation in ('schema','population','decimal_type','score','winner','changed'):
            altered=deepcopy(self.record)
            if mutation=='schema':altered['schema_version']=True
            elif mutation=='population':altered['native_word_types']=3920.0
            elif mutation=='decimal_type':altered['pairs'][0]['subset_score_bits_decimal_80digits']=False
            elif mutation=='score':altered['rankings'][0]['maximum_bits_20dp']='0.00000000000000000000'
            elif mutation=='winner':altered['rankings'][0]['positive_maximizers']=[]
            else:altered['normalization_comparisons'][0]['different_positive_maximizer_sets']=False
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):m.figure_data(altered)

    def test_pin_failure_precedes_render_and_export_directory_creation(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);source=root/'report.json';source.write_text('{}');output=root/'exports'
            with patch.object(m,'REPORT',source),patch.object(m,'render') as render,patch('sys.argv',['figure','--new-output-dir',str(output)]),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):m.main()
            render.assert_not_called();self.assertFalse(output.exists())

    def test_existing_or_protected_directory_fails_before_input_read(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(m,'read_data') as read,patch('sys.argv',['figure','--new-output-dir',folder]),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):m.main()
            read.assert_not_called()
            with patch.object(m,'ROOT',Path(folder)),self.assertRaises(ValueError):m.guard(Path(folder)/'data/new',Path(folder)/'data/new')

    def test_late_alias_or_parent_redirect_preserves_sources_and_other_outputs(self):
        for kind in ('symlink','hardlink','parent_redirect'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as folder:
                root=Path(folder);source=root/'source.json';source.write_text('preserve');parent=root/'parent';parent.mkdir();output=parent/'exports';other=root/'other';other.mkdir()
                def render(_):
                    if kind=='parent_redirect':parent.rmdir();parent.symlink_to(other,target_is_directory=True)
                    else:
                        output.mkdir();alias=output/(m.STEM+'.svg')
                        if kind=='symlink':alias.symlink_to(source)
                        else:alias.hardlink_to(source)
                    return {'png':b'synthetic','svg':b'synthetic','json':b'{}'}
                with patch.object(m,'read_data',return_value={}),patch.object(m,'render',side_effect=render),patch('sys.argv',['figure','--new-output-dir',str(output)]),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):m.main()
                self.assertEqual(source.read_text(),'preserve')
                self.assertFalse((output/(m.STEM+'.png')).exists());self.assertFalse((other/'exports').exists())

    def test_failed_render_leaves_no_export_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'exports'
            with patch.object(m,'read_data',return_value={}),patch.object(m,'render',side_effect=ValueError('synthetic failure')),patch('sys.argv',['figure','--new-output-dir',str(output)]),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):m.main()
            self.assertFalse(output.exists())

    def test_actual_artists_export_hashes_dimensions_and_local_svg_references(self):
        provenance=json.loads((FIGURES/(m.STEM+'.json')).read_text())
        data=m.figure_data(self.record)
        for key,value in data.items():self.assertEqual(provenance[key],value)
        self.assertEqual(len(provenance['artist_positions']),70)
        for artist in provenance['artist_positions']:
            index=self.record['native_alphabet'].index(artist['source_symbol']);row=data['rows'][index][artist['metric']]
            self.assertEqual(artist['bar_center_y'],index)
            self.assertEqual(artist['bar_x'],row['score_x'])
            self.assertEqual(artist['positive_partners'],row['ranking']['positive_maximizers'])
        for ext in ('png','svg'):
            self.assertEqual(hashlib.sha256((FIGURES/(m.STEM+'.'+ext)).read_bytes()).hexdigest(),provenance['output_sha256'][ext])
        png=(FIGURES/(m.STEM+'.png')).read_bytes();self.assertEqual(struct.unpack('>II',png[16:24]),(2480,2304))
        raw=(FIGURES/(m.STEM+'.svg')).read_text();tree=ET.fromstring(raw)
        self.assertNotIn('/Users/',raw);self.assertNotIn('file://',raw)
        self.assertFalse(any(node.tag.endswith('script') or node.tag.endswith('image') for node in tree.iter()))
        self.assertTrue(all(not key.endswith('href') or value.startswith('#') for node in tree.iter() for key,value in node.attrib.items()))
        text=' '.join(tree.itertext())
        for phrase in ('70 maxima from 595 pairs','no positive optimum','different character pairs','T=3,304','T=5,972'):
            self.assertIn(phrase,text)
        self.assertEqual(provenance['renderer']['script_sha256'],hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest())


if __name__=='__main__':unittest.main()
