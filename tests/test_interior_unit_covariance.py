import contextlib
from decimal import getcontext,localcontext,ROUND_FLOOR
from fractions import Fraction
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts import interior_unit_covariance as m


class UnitCovarianceTests(unittest.TestCase):
    def test_equal_locus_covariance_keeps_constant_rows_in_denominator(self):
        _,matrix=m.joint.policy_matrix([[1,2,3,4],[4,1,2,2],[1,3,2,1]],'half')
        zero=[[Fraction()]*3 for _ in range(3)]
        aggregated=m.covariance_of_mean([matrix,zero])
        self.assertEqual(aggregated,[[value/4 for value in row] for row in matrix])
        with self.assertRaises(ValueError):m.covariance_of_mean([])

    def test_empirical_population_covariance_retains_negative_and_dependent_cases(self):
        means,cov=m.empirical_covariance([[1.,2.,3.,4.],[3.,5.,7.,9.],[-1.,-2.,-3.,-4.]])
        self.assertEqual(means,[2.5,6.,-2.5]);self.assertEqual(cov,[[1.25,2.5,-1.25],[2.5,5.,-2.5],[-1.25,-2.5,1.25]])
        self.assertEqual(cov[1][1]+cov[0][0]-2*cov[0][1],1.25)
        for invalid in (([],[],[]),([1.],[1.,2.],[1.]),([True],[1.],[1.]),([float('nan')],[1.],[1.])):
            with self.assertRaises(ValueError):m.empirical_covariance(invalid)

    def test_zero_variance_and_nonzero_difference_states_are_not_conflated(self):
        self.assertEqual(m.paired_diagnostic(Fraction(),Fraction())['variance_status'],'zero_variance_zero_difference')
        self.assertEqual(m.paired_diagnostic(Fraction(1),Fraction())['variance_status'],'zero_variance_nonzero_difference')
        self.assertIsNone(m.paired_diagnostic(Fraction(1),Fraction())['observed_over_ideal_sd_approx'])
        self.assertEqual(m.paired_diagnostic(Fraction(2),Fraction(4))['observed_over_ideal_sd_approx'],1.)
        with self.assertRaises(ValueError):m.paired_diagnostic(Fraction(1),Fraction(-1))

    def test_large_exact_fraction_roundtrips_without_ambient_context_or_digit_limit_changes(self):
        before=sys.get_int_max_str_digits() if hasattr(sys,'get_int_max_str_digits') else None
        value=Fraction(10**9000+1,10**9001+3)
        expected=m.large(value)
        with localcontext() as context:
            context.prec=1;context.rounding=ROUND_FLOOR
            actual=m.large(value);self.assertEqual(actual,expected);self.assertEqual(m.unpack(actual),value)
            self.assertEqual(context.prec,1);self.assertEqual(context.rounding,ROUND_FLOOR)
        if before is not None:self.assertEqual(sys.get_int_max_str_digits(),before)
        self.assertEqual(json.loads(m.serialize({'large':actual,'small':m.small(Fraction(-2,3))})),{'large':actual,'small':['-2','3']})

    def test_changed_manifest_or_input_blocks_source_reconstruction(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);pin=root/m.PINS;pin.parent.mkdir(parents=True)
            source=root/'fixture.txt';source.write_text('changed');pin.write_text(json.dumps({'fixture.txt':m.sha(b'original')}))
            with patch.object(m,'ROOT',root),patch.object(m,'PIN_SHA256',m.sha(pin.read_bytes())),patch.object(m,'prepare') as prepare:
                with self.assertRaisesRegex(ValueError,'input changed'):m.report()
                prepare.assert_not_called()
            with patch.object(m,'ROOT',root),self.assertRaisesRegex(ValueError,'manifest changed'):m.load_inputs()

    def test_direct_symlink_and_hardlink_inputs_code_and_plan_are_protected(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);pin=root/m.PINS;pin.parent.mkdir(parents=True)
            source=root/'source.json';source.write_text('preserve');plan=root/m.PLAN;plan.write_text('preserve')
            pin.write_text(json.dumps({'source.json':m.sha(source.read_bytes()),m.PLAN:m.sha(plan.read_bytes())}))
            with patch.object(m,'ROOT',root),patch.object(m.unit,'protect_output'):
                for i,original in enumerate((source,plan,pin,Path(m.__file__))):
                    symbolic=root/f's-{i}';symbolic.symlink_to(original);hard=root/f'h-{i}';hard.hardlink_to(original)
                    for alias in (original,symbolic,hard):
                        with self.subTest(alias=alias.name),self.assertRaises(ValueError):m.protect_output(alias)
                m.protect_output(root/'new.json')

    def test_existing_new_report_is_rejected_before_calculation(self):
        with tempfile.TemporaryDirectory() as folder:
            output=Path(folder)/'report.json';output.write_text('preserve')
            with patch.object(m,'protect_output'),patch.object(m,'report') as calculate, \
                    patch('sys.argv',['cov','--new-report',str(output)]),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):m.main()
            calculate.assert_not_called();self.assertEqual(output.read_text(),'preserve')

    def test_alias_created_during_serialization_is_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);pin=root/m.PINS;pin.parent.mkdir(parents=True);source=root/m.PLAN;source.write_text('preserve')
            pin.write_text(json.dumps({m.PLAN:m.sha(source.read_bytes())}));output=root/'out.json'
            def serialize(_):
                output.hardlink_to(source)
                return '{}\n'
            with patch.object(m,'ROOT',root),patch.object(m.unit,'protect_output'),patch.object(m,'report',return_value={}), \
                    patch.object(m,'serialize',side_effect=serialize),patch('sys.argv',['cov','--new-report',str(output)]), \
                    contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):m.main()
            self.assertEqual(source.read_text(),'preserve');self.assertEqual(output.read_text(),'preserve')

    def test_saved_report_scalar_types_are_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            saved=Path(folder)/'report.json';saved.write_text('{"count":false}')
            with patch.object(m,'protect_output'),patch.object(m,'report',return_value={'count':0}), \
                    patch('sys.argv',['cov','--check',str(saved)]),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):m.main()


if __name__=='__main__':unittest.main()
