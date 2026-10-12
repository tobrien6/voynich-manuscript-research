from contextlib import redirect_stderr, redirect_stdout
from fractions import Fraction as F
import io
from pathlib import Path
import shutil
import string
import tempfile
import unittest
from unittest.mock import patch

from scripts import initial_context_shrinkage_control as c


class InitialContextControlTests(unittest.TestCase):
    def test_manual_probabilities_and_whole_alphabet_normalization(self):
        alphabet = sorted(set(string.ascii_letters) | {c.EOS})
        model = c.fit([{'units':['a']} for _ in range(4)], alphabet)
        self.assertEqual(c.probabilities(model,c.BOS,c.BOS,'a'),
                         (F(3,23),F(7,23),F(51,115),F(51,115)))
        self.assertEqual(c.probabilities(model,c.BOS,'a',c.EOS),
                         (F(3,23),F(7,23),F(51,115),F(51,115)))
        for x in [c.BOS,'a']:
            qs=[c.probabilities(model,c.BOS,x,y) for y in alphabet]
            self.assertEqual([sum(q[j] for q in qs) for j in range(4)],[1]*4)
            self.assertTrue(all(q[2]==q[3] for q in qs))
        self.assertEqual(c.effective_strength(4),F(64,9))

    def test_effective_strength_identity_over_general_count_cases(self):
        for n in range(1,21):
            for count in range(n+1):
                for prior in [F(1,3),F(2,3)]:
                    q1=c.smooth(count,n,prior)
                    q2=c.smooth(count,n,q1)
                    self.assertEqual(q2,c.smooth(count,n,prior,c.effective_strength(n)))

    def test_bos_eos_accounting_and_constant_older_label(self):
        self.assertEqual(c.events(['a']),[(c.BOS,c.BOS,'a'),(c.BOS,'a',c.EOS)])
        model=c.fit([{'units':['a']} for _ in range(4)],('a',c.EOS))
        self.assertEqual(model['total'],8)
        self.assertEqual(model['targets'],{'a':4,c.EOS:4})
        self.assertEqual({w for w,x,y in model['triples']},{c.BOS})
        self.assertNotIn(c.EOS,model['first_totals'])
        for units in [[],[c.BOS],[c.EOS]]:
            with self.assertRaises(ValueError):c.events(units)

    def test_reference_convention_boundaries(self):
        self.assertTrue(c.preference(.02,.1,[.1]*5))
        for a,b,f in [(.019,.1,[.1]*5),(.1,0,[.1]*5),(.1,.1,[.1]*4+[0])]:
            self.assertFalse(c.preference(a,b,f))
        with self.assertRaises(ValueError):c.preference(1,1,[1]*4)

    def test_complete_disjoint_folds_and_excluded_parameter_perturbation(self):
        rows=[{'group':f'toy-{i}','fold':i,'units':['a']} for i in range(5)]
        seen=[]
        for fold in range(5):
            train,test=c.fold_population(rows,fold)
            self.assertEqual(len(train),4)
            self.assertEqual(len(test),1)
            self.assertFalse({r['group'] for r in train}&{r['group'] for r in test})
            seen.extend(r['group'] for r in test)
        self.assertEqual(sorted(seen),[f'toy-{i}' for i in range(5)])
        alphabet=('a','b',c.EOS)
        before=c.counts_record(c.fit(c.fold_population(rows,2)[0],alphabet))
        rows[2]['units']=['b']
        self.assertEqual(before,c.counts_record(c.fit(c.fold_population(rows,2)[0],alphabet)))
        self.assertNotEqual(before,c.counts_record(c.fit(c.fold_population(rows,0)[0],alphabet)))
        rows[2]['fold']=True
        with self.assertRaises(ValueError):c.fold_population(rows,2)

    def test_fixed_inputs_and_strict_json_reject_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for p in c.PINS:
                (root/p).parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(c.ROOT/p,root/p)
            c.load_inputs(root)
            (root/c.PLAN).write_bytes((root/c.PLAN).read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError,'fixed input changed'):c.load_inputs(root)
        for raw in [b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":Infinity}']:
            with self.assertRaises(ValueError):c.strict_json(raw)

    def test_existing_output_refused_before_build_and_new_output_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'report';output.write_bytes(b'synthetic input')
            with patch('sys.argv',['control','--output',str(output)]),patch.object(c,'build_report') as build,\
                    redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):c.main()
            build.assert_not_called()
            self.assertEqual(output.read_bytes(),b'synthetic input')
            output.unlink()
            with patch('sys.argv',['control','--output',str(output)]),\
                    patch.object(c,'build_report',return_value={'implementation_sha256':c.digest(Path(c.__file__).read_bytes())}),\
                    redirect_stdout(io.StringIO()):c.main()
            self.assertTrue(output.exists())

    def test_late_symlink_and_hardlink_aliases_are_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source=root/'source';source.write_bytes(b'synthetic input')
            for kind in ['symlink','hardlink']:
                output=root/kind
                def build(_root):
                    if kind=='symlink':output.symlink_to(source)
                    else:output.hardlink_to(source)
                    return {'implementation_sha256':c.digest(Path(c.__file__).read_bytes())}
                with patch('sys.argv',['control','--output',str(output)]),patch.object(c,'build_report',side_effect=build),\
                        redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):c.main()
                self.assertEqual(source.read_bytes(),b'synthetic input')

    def test_report_check_preserves_exact_json_type(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'report';path.write_bytes(c.encoded({'schema_version':True}))
            with patch('sys.argv',['control','--check',str(path)]),patch.object(c,'build_report',return_value={'schema_version':1}),\
                    redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):c.main()


if __name__=='__main__':unittest.main()
