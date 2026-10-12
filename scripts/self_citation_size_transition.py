"""Verify the declared parent serialization transition without running snapshots."""
import ast
import gzip
import hashlib
import json
from pathlib import Path

RECORD='research/literature/self-citation-size-amendment-1.json'
PARENT='research/literature/self-citation-interior.json'
SIZE='research/literature/self-citation-size-conditioned.json'


def sha(raw):return hashlib.sha256(raw).hexdigest()


def canonical(value):
    normalized=json.loads(json.dumps(value,ensure_ascii=False,allow_nan=False))
    return json.dumps(normalized,ensure_ascii=False,allow_nan=False,sort_keys=True,separators=(',',':'))


def changed_fields(before,after,allowed):
    if set(before)!=set(after):raise ValueError('transition changed report field inventory')
    changed={key for key in before if canonical(before[key])!=canonical(after[key])}
    if not changed<=set(allowed):raise ValueError('transition changed non-allowlisted scientific or provenance fields')
    return sorted(changed)


def original_bytes(root,record,name):
    entry=record['original_artifacts'][name];raw=(root/entry['archive_path']).read_bytes()
    if sha(raw)!=entry['archive_sha256']:raise ValueError('first artifact archive identity changed')
    result=gzip.decompress(raw)
    if sha(result)!=entry['uncompressed_sha256']:raise ValueError('first artifact decompressed identity changed')
    return result


def functions(raw):
    return {node.name:ast.dump(node,include_attributes=False) for node in ast.parse(raw).body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))}


def verify_functions(before,after,changed,added):
    old,new=functions(before),functions(after)
    if set(new)!=set(old)|set(added):raise ValueError('transition changed source function inventory')
    if any(old[name]!=new[name] for name in old if name not in changed):
        raise ValueError('transition changed a protected scientific/source function')
    return True


def verify_inputs(root):
    record=json.loads((root/RECORD).read_text())
    first=(root/record['original_pin_manifest_path']).read_bytes()
    if sha(first)!=record['original_pin_manifest_sha256']:raise ValueError('original pre-score manifest changed')
    if sha((root/'research/literature/SELF_CITATION_SIZE_PLAN.md').read_bytes())!=record['original_size_plan_sha256']:
        raise ValueError('original pre-score plan changed')
    for name in record['original_artifacts']:original_bytes(root,record,name)
    for name,expected in record['effective_parent_artifact_sha256'].items():
        if sha((root/name).read_bytes())!=expected:raise ValueError('accepted effective parent identity changed')
    old=json.loads(original_bytes(root,record,PARENT));new=json.loads((root/PARENT).read_text())
    if changed_fields(old,new,record['allowed_parent_report_changed_fields'])!=['implementation_sha256']:
        raise ValueError('accepted parent transition must change only producer fingerprint')
    producer='scripts/self_citation_interior.py';checker='scripts/verify_self_citation_interior_math.py'
    verify_functions(original_bytes(root,record,producer),(root/producer).read_bytes(),record['parent_formatting_functions_changed'],record['parent_formatting_functions_added'])
    verify_functions(original_bytes(root,record,checker),(root/checker).read_bytes(),record['parent_independent_parser_changed'],record['parent_independent_parser_added'])
    child='scripts/self_citation_size_conditioned.py'
    verify_functions(original_bytes(root,record,child),(root/child).read_bytes(),['load_inputs','main'],[])
    for name in (producer,checker,child):
        tree=ast.parse((root/name).read_bytes())
        if any(isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='set_int_max_str_digits' for node in ast.walk(tree)):
            raise ValueError('effective modules must not change global integer-string limits')
    return record


def verify_result(result,root):
    record=verify_inputs(root)
    original=json.loads(original_bytes(root,record,SIZE))
    return changed_fields(original,result,record['allowed_size_report_changed_fields'])
