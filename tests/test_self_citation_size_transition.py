from copy import deepcopy
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

from scripts import self_citation_size_conditioned as driver
from scripts import self_citation_size_transition as m


class SizeTransitionTests(unittest.TestCase):
    def test_preserved_archives_and_accepted_parent_transition_are_exact(self):
        record=m.verify_inputs(driver.ROOT)
        first=m.original_bytes(driver.ROOT,record,m.PARENT)
        self.assertEqual(hashlib.sha256(first).hexdigest(),'f23c65bc2b7830522fe4e24f710c266d2f81ad0ef69d46636106c1a5cb9c7b8d')
        size=m.original_bytes(driver.ROOT,record,m.SIZE)
        self.assertEqual(hashlib.sha256(size).hexdigest(),'df4b1f52137311083e6da69814ec6f6fc6f2d86b81251ffebf86cea9f46faf61')
        self.assertEqual(record['original_pin_manifest_sha256'],'65c9d900f34172c98a5ff38b780fc2612a7fed9c5412a91634859f4d3976e275')
        old=json.loads(first);new=json.loads((driver.ROOT/m.PARENT).read_text())
        self.assertEqual(m.changed_fields(old,new,record['allowed_parent_report_changed_fields']),['implementation_sha256'])

    def test_scientific_changes_and_scalar_type_substitution_are_rejected(self):
        original={'input_pins':{'first':'old'},'value':0,'scores':[1.,None],'count':1}
        repaired=deepcopy(original);repaired['input_pins']={'first':'new'}
        self.assertEqual(m.changed_fields(original,repaired,['input_pins']),['input_pins'])
        for key,value in (('value',False),('count',1.),('scores',[1.,0])):
            changed=deepcopy(repaired);changed[key]=value
            with self.subTest(key=key),self.assertRaises(ValueError):m.changed_fields(original,changed,['input_pins'])
        with self.assertRaises(ValueError):m.changed_fields(original,{**repaired,'new':1},['input_pins'])

    def test_archived_scientific_fields_reject_a_weight_or_undefined_range_edit(self):
        record=m.verify_inputs(driver.ROOT);old=json.loads(m.original_bytes(driver.ROOT,record,m.SIZE));new=deepcopy(old)
        new['input_pins']={'accepted':'updated'}
        self.assertEqual(m.changed_fields(old,new,record['allowed_size_report_changed_fields']),['input_pins'])
        new['primary']['comparisons'][0]['within_fixed_seed_range']=False
        with self.assertRaises(ValueError):m.changed_fields(old,new,record['allowed_size_report_changed_fields'])

    def test_ast_checks_preserve_scientific_functions_without_executing_source(self):
        old=b"raise RuntimeError('must not execute')\ndef scientific(x): return x+1\ndef packed(x): return x\n"
        new=b"raise RuntimeError('must not execute')\ndef scientific(x): return x+1\ndef packed(x): return str(x)\ndef local(x): return x\n"
        self.assertTrue(m.verify_functions(old,new,['packed'],['local']))
        with self.assertRaises(ValueError):m.verify_functions(old,new.replace(b'return x+1',b'return x+2'),['packed'],['local'])
        with self.assertRaises(ValueError):m.verify_functions(old,new,['packed'],[])

    def test_altered_archive_fails_before_decompression(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);raw=gzip.compress(b'{"public":1}',mtime=0);(root/'first.gz').write_bytes(raw)
            record={'original_artifacts':{'fixture':{'archive_path':'first.gz','archive_sha256':m.sha(raw),'uncompressed_sha256':m.sha(b'{"public":1}')}}}
            self.assertEqual(m.original_bytes(root,record,'fixture'),b'{"public":1}')
            (root/'first.gz').write_bytes(b'not gzip')
            with self.assertRaisesRegex(ValueError,'archive identity'):m.original_bytes(root,record,'fixture')

    def test_local_long_integer_conversion_leaves_global_guard_unchanged(self):
        before=sys.get_int_max_str_digits() if hasattr(sys,'get_int_max_str_digits') else None
        value=Fraction(10**21000+17,10**21001+31)
        encoded=driver.parent.packed(value)
        self.assertEqual(driver.parent.unpack(encoded),value)
        if before is not None:self.assertEqual(sys.get_int_max_str_digits(),before)


if __name__=='__main__':unittest.main()
