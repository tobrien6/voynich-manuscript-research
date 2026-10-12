"""Frozen-output self-citation interior diagnostic; no Java execution or fitting."""

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import platform
import re
import sys

try:
    from . import self_citation_prefix_profile as prefix
    from . import interior_length_order as original
    from . import interior_half_controls as half
    from .half_control_invariance import classify
    from .eva_unit_sensitivity import ordered_patterns, segment
    from .validate_evaluation_split import load_split_json
except ImportError:
    import self_citation_prefix_profile as prefix
    import interior_length_order as original
    import interior_half_controls as half
    from half_control_invariance import classify
    from eva_unit_sensitivity import ordered_patterns, segment
    from validate_evaluation_split import load_split_json


ROOT = Path(__file__).resolve().parents[1]
METHOD = 'fixed-self-citation-interior-order-v1'
PLAN = 'research/literature/SELF_CITATION_INTERIOR_PLAN.md'
PINS = 'research/literature/self-citation-interior-pins.json'
PARENT = 'research/literature/self-citation-prefix-profile.json'
SETTINGS = 'research/baselines/eva-unit-protocol.json'
SEEDS = list(range(1, 32))
POLICIES = ['ascii_letters', 'bench_sequences', 'bench_and_minim_sequences']
SCOPES = ['unrestricted', 'half']
PIN_MANIFEST_SHA256 = '8d1b9e97d61ce0052b6e0d15e764f5e46007652ef81fa05d22f1f347d10a9d6e'

# Exact means can have many-digit denominators. All model/source bytes are
# checksum-verified before these bounded finite sums are evaluated.
if hasattr(sys, 'set_int_max_str_digits'):
    sys.set_int_max_str_digits(0)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()


def same_json(left, right):
    """Complete JSON identity, including boolean/integer/float scalar types."""
    def canonical(value):
        normalized = json.loads(json.dumps(value, ensure_ascii=False, allow_nan=False))
        return json.dumps(normalized, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(',', ':'))
    return canonical(left) == canonical(right)


def packed(value):
    if value is None:
        return None
    return {'numerator': str(value.numerator), 'denominator': str(value.denominator), 'mean': float(value)}


def unpack(value):
    return Fraction(int(value['numerator']), int(value['denominator'])) if value is not None else None


def load_inputs(root=ROOT):
    pin_bytes = (root / PINS).read_bytes()
    if sha(pin_bytes) != PIN_MANIFEST_SHA256:
        raise ValueError('frozen pin manifest changed')
    pins = load_split_json(pin_bytes.decode())
    raw = {}
    for name, expected in pins.items():
        raw[name] = (root / name).read_bytes()
        if sha(raw[name]) != expected:
            raise ValueError(f'frozen artifact/helper changed: {name}')
    if (pins[PARENT] != '140731ba67ca1a9bd2bb35460a4f6a19b5cff671627c4020f9f76f9362191ca9'
            or pins[SETTINGS] != 'a2ded6526829759169d9462708ea00f969ebe47127acf5c90e2f0b1e7e2fc3ec'):
        raise ValueError('parent or accepted map identity changed')
    return load_split_json(raw[PARENT].decode()), load_split_json(raw[SETTINGS].decode()), pins, sha(pin_bytes)


def validate_rows(raw, ledger, expected_count):
    """Validate all original byte rows before excluding initialization/short rows."""
    if (type(expected_count) is not int or expected_count < 2 or not isinstance(ledger, list)
            or len(ledger) != expected_count):
        raise ValueError('ledger must contain every expected row')
    native, offset = [], 0
    for line_number, line in enumerate(raw.splitlines(keepends=True), 1):
        body = line.rstrip(b'\r\n')
        if body.strip() and not body.lstrip().startswith(b'#'):
            if not re.fullmatch(rb'[A-Za-z]+(?: [A-Za-z]+)*', body):
                raise ValueError('unsupported generated notation or spacing; no repair/exclusion allowed')
            native.append((line_number, offset, offset + len(body), body))
        offset += len(line)
    if len(native) != expected_count:
        raise ValueError('native output row count changed')
    eligible, excluded, hist = [], [], Counter()
    for index, (record, (line_number, start, end, body)) in enumerate(zip(ledger, native)):
        checks = {'generated_row_index': index, 'native_file_line_number': line_number,
                  'start_byte': start, 'end_byte_exclusive_without_line_ending': end,
                  'space_delimited_token_count': len(body.split(b' '))}
        if any(type(record.get(k)) is not int or record[k] != v for k, v in checks.items()):
            raise ValueError('row index, interval or group count changed')
        if record.get('row_sha256') != sha(body) or type(record.get('initialized_input_row')) is not bool:
            raise ValueError('row hash or initialization type changed')
        if record['initialized_input_row'] != (index == 0):
            raise ValueError('exactly the first original row must be initialization')
        for name in ('model_paragraph_initial', 'model_paragraph_final'):
            if (record.get(name) is not None if index == 0 else type(record.get(name)) is not bool):
                raise ValueError('invalid model context flag')
        for name in ('source_lines_in_page_pre_call', 'source_lines_in_paragraph_pre_call'):
            value = record.get(name)
            if (value is not None if index == 0 else type(value) is not int or value < 0):
                raise ValueError('invalid source-state counter')
        groups = body.decode('ascii').split(' ')
        if index == 0:
            excluded.append({'row_index': index, 'reason': 'initialized_input', 'groups': len(groups)})
        else:
            hist[len(groups)] += 1
            if len(groups) < 5:
                excluded.append({'row_index': index, 'reason': 'fewer_than_five_groups', 'groups': len(groups)})
            else:
                eligible.append((str(index), groups))
    return eligible, {'native_rows': expected_count, 'initialized_rows': 1,
                      'newly_generated_rows': expected_count - 1, 'eligible_rows': len(eligible),
                      'excluded_rows': excluded, 'generated_group_count_histogram': dict(sorted(hist.items()))}


def select_minimum(maps, parent_keys):
    if set(maps) != {(s, p) for s in prefix.SOURCE_IDS for p in prefix.SPACING}:
        raise ValueError('require all four native source/spacing variants')
    if not parent_keys or len(set(parent_keys)) != len(parent_keys):
        raise ValueError('unique nonempty parent keys required')
    selected, excluded = [], []
    for key in parent_keys:
        reasons = []
        for (sid, spacing), mapping in maps.items():
            if key not in mapping:
                raise ValueError('missing fixed parent key')
            if len(mapping[key]['tokens']) < 5:
                reasons.append(f'{sid}/{spacing}:fewer_than_five_tokens')
        if reasons:
            excluded.append({'locus_key': key, 'reasons': reasons})
        else:
            selected.append(key)
    return selected, excluded


def measure(token_rows, policies):
    if len({key for key, _ in token_rows}) != len(token_rows):
        raise ValueError('duplicate measurement unit')
    if [p['id'] for p in policies] != POLICIES:
        raise ValueError('exactly the accepted unit policies required')
    results = []
    for policy in policies:
        patterns = ordered_patterns(policy['patterns'])
        vectors, hits, uppercase, hist = [], Counter({p: 0 for p in patterns}), Counter(), Counter()
        for key, tokens in token_rows:
            if not isinstance(tokens, (list, tuple)):
                raise ValueError('original group boundaries required')
            original.interior_lengths(tokens)
            values = []
            for token in tokens[1:-1]:
                pieces = segment(token, patterns)
                if ''.join(pieces) != token:
                    raise ValueError('counting changed source text')
                values.append(len(pieces))
                hits.update(p for p in pieces if len(p) > 1)
                uppercase.update(p for p in pieces if len(p) == 1 and p.isupper())
            vectors.append(('encoded-unit', key, values));hist[len(tokens)] += 1
        n = len(vectors)
        raw_r, full_e, half_e, full_c, half_c = [], [], [], [], []
        for _, _, values in vectors:
            m, squared, adjacent = original.components(values)
            r = Fraction(m * adjacent, (m - 1) * squared) if squared else Fraction(0)
            e = Fraction(-1, m - 1) if squared else Fraction(0)
            h = half.exact_half_expectation(values)
            raw_r.append(r);full_e.append(e);half_e.append(h)
            full_c.append(r-e);half_c.append(r-h)
        mean = lambda xs: packed(sum(xs, Fraction(0)) / n) if n else None
        results.append({'policy_id': policy['id'], 'rows': n,
                        'interior_groups': sum(len(v) for _, _, v in vectors),
                        'interior_pairs': sum(len(v)-1 for _, _, v in vectors),
                        'vector_sha256': sha(compact(vectors)), 'original_group_count_histogram': dict(sorted(hist.items())),
                        'constant_interiors': sum(len(set(v)) == 1 for _, _, v in vectors),
                        'half_invariance': classify(vectors) if n else None,
                        'uncentered_mean': mean(raw_r), 'unrestricted_expectation': mean(full_e), 'half_expectation': mean(half_e),
                        'scores': {'unrestricted': mean(full_c), 'half': mean(half_c)},
                        'scope_audit': {'scope': 'eligible original interior groups only',
                                        'pattern_hits': dict(sorted(hits.items())),
                                        'uppercase_single_letter_fallback_counts': dict(sorted(uppercase.items()))}})
    return results


def ranges(targets, cases):
    if [c['seed'] for c in cases] != SEEDS or any(type(c['seed']) is not int for c in cases):
        raise ValueError('complete ordered fixed seed list required')
    if {(t['source_id'], t['spacing']) for t in targets} != {(s,p) for s in prefix.SOURCE_IDS for p in prefix.SPACING} or len(targets)!=4:
        raise ValueError('every source/spacing target required')
    out = []
    for target in targets:
        if [p['policy_id'] for p in target['policies']] != POLICIES:
            raise ValueError('target policy family incomplete')
        for i, policy in enumerate(target['policies']):
            for scope in SCOPES:
                values = []
                for case in cases:
                    if [p['policy_id'] for p in case['policies']] != POLICIES:
                        raise ValueError('seed policy family incomplete')
                    values.append(unpack(case['policies'][i]['scores'][scope]))
                point = unpack(policy['scores'][scope])
                defined = point is not None and all(v is not None for v in values)
                lo, hi = (min(values), max(values)) if defined else (None,None)
                inside = lo <= point <= hi if defined else None
                gap = max(lo-point,point-hi,Fraction(0)) if defined else None
                out.append({'source_id':target['source_id'],'spacing':target['spacing'],'policy_id':policy['policy_id'],
                            'scope':scope,'target':packed(point),'seed_minimum':packed(lo),'seed_maximum':packed(hi),
                            'all_fixed_seed_values_defined':defined,'within_fixed_seed_range':inside,'outside_range_gap':packed(gap)})
    return out


def verified_runs(runs, parent):
    if [c['seed'] for c in parent['cases']] != SEEDS or any(type(c['seed']) is not int for c in parent['cases']):
        raise ValueError('accepted parent seed list changed')
    prepared = []
    for case in parent['cases']:
        if case['accepted'] is not True or case['complete_control_observed_bytes_equal'] is not True:
            raise ValueError('failed parent case blocks comparison')
        folder = runs / f"seed-{case['seed']:02d}"
        outputs = {}
        for mode in ('control','observed'):
            process = case['processes'][mode]
            if process['returncode'] != 0 or process['timed_out'] is not False:
                raise ValueError('unsuccessful parent process')
            outputs[mode] = (folder/mode/'output/generated.txt').read_bytes()
            if sha(outputs[mode]) != case['output_sha256'][mode]:
                raise ValueError('generated output identity changed')
            if sha((folder/mode/'conf.properties').read_bytes()) != case['effective_configuration_sha256']:
                raise ValueError('complete configuration identity changed')
            for suffix in ('stdout','stderr'):
                log = (folder/mode/f'process.{suffix}').read_bytes()
                if sha(log) != process[suffix+'_sha256']:
                    raise ValueError('recorded process log identity changed')
        if outputs['control'] != outputs['observed']:
            raise ValueError('complete control/observed bytes differ')
        raw_ledger = (folder/'observed/ledger.json').read_bytes()
        if sha(raw_ledger) != case['row_ledger_sha256']:
            raise ValueError('row ledger identity changed')
        rows, audit = validate_rows(outputs['observed'], load_split_json(raw_ledger.decode()), case['total_output_rows'])
        prepared.append((case, rows, audit))
    return prepared


def report(runs):
    parent, settings, pins, manifest_sha = load_inputs()
    prepared = verified_runs(runs, parent)  # Validate every model case before any measurement.
    sources = prefix.paired_sources(prefix.load_sources())
    payloads = [prefix.build(spacing, source_ids=prefix.SOURCE_IDS, kinds=('P0',)) for spacing in prefix.SPACING]
    rebuilt = prefix.select_target(sources,payloads)
    if not same_json(rebuilt, parent['target']):
        raise ValueError('complete original manuscript target does not reproduce')
    # Each spacing map comes only from its own packet.
    maps = {(sid,spacing):{r['locus_key']:r for r in payloads[i]['records'] if r['source_id']==sid}
            for i,spacing in enumerate(prefix.SPACING) for sid in prefix.SOURCE_IDS}
    selected, excluded = select_minimum(maps, rebuilt['selected_keys'])
    targets = [{'source_id':sid,'spacing':spacing,
                'policies':measure([(key,maps[sid,spacing][key]['tokens']) for key in selected],settings['policies'])}
               for sid in prefix.SOURCE_IDS for spacing in prefix.SPACING]
    cases=[]
    for case,rows,audit in prepared:
        cases.append({'seed':case['seed'],'generation_receipt':case,'eligibility':audit,'policies':measure(rows,settings['policies'])})
    comparisons=ranges(targets,cases)
    defined=all(c['all_fixed_seed_values_defined'] for c in comparisons)
    return {'schema_version':1,'method':METHOD,'status':'exploratory reused fixed-output encoded-row diagnostic; full prior exposure',
            'python_version':platform.python_version(),'input_pins':pins,'pin_manifest_sha256':manifest_sha,
            'plan_sha256':sha((ROOT/PLAN).read_bytes()),'implementation_sha256':sha(Path(__file__).read_bytes()),
            'parent_source_commit':parent['source_commit'],'parent_protocol_sha256':parent['protocol_sha256'],
            'runtime':parent['runtime'],'source_inventory':parent['source_inventory'],
            'selection':{'parent_keys':len(rebuilt['selected_keys']),'selected_keys':selected,'selected_keys_sha256':sha(compact(selected)),
                         'additional_minimum_size_exclusions':excluded},
            'targets':targets,'cases':cases,'comparisons':comparisons,'comparison_ranges_defined':defined,
            'all_target_points_within_fixed_seed_ranges':all(c['within_fixed_seed_range'] for c in comparisons) if defined else None,
            'new_generation_processes':0,'new_permutation_draws':0,'mechanism_or_translation_validated':False}


def protect_output(output,runs,root=ROOT):
    resolved=output.resolve()
    pins=load_split_json((root/PINS).read_text());catalog=load_split_json((root/'data/transliterations.json').read_text())
    protected={root/name for name in pins}|{root/PINS,root/PLAN,Path(__file__).resolve()}
    protected.update(root/s['path'] for s in catalog['sources'])
    protected.update(p for p in runs.rglob('*') if p.is_file())
    if (resolved.is_relative_to(runs.resolve()) or resolved.is_relative_to((root/'data').resolve()) or resolved.is_relative_to((root/'scripts').resolve())
            or any(resolved==p.resolve() or (output.exists() and p.exists() and output.samefile(p)) for p in protected)):
        raise ValueError('output aliases fixed inputs, run artifacts, code or plan')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--runs',required=True,type=Path)
    dest=parser.add_mutually_exclusive_group(required=True);dest.add_argument('--new-report',type=Path);dest.add_argument('--check',type=Path)
    args=parser.parse_args()
    try:
        if args.new_report:
            protect_output(args.new_report,args.runs)
            if args.new_report.exists() or args.new_report.is_symlink():raise ValueError('new report path must not already exist')
        result=report(args.runs)
        if args.check and not same_json(result,load_split_json(args.check.read_text())):raise ValueError('complete saved comparison differs from replay')
        if args.new_report:
            protect_output(args.new_report,args.runs)
            with args.new_report.open('x',encoding='utf-8') as out:out.write(json.dumps(result,indent=2)+'\n')
    except (ValueError,OSError,KeyError,TypeError) as error:parser.exit(1,f'Self-citation interior comparison failed: {error}\n')
    print('All fixed31 cases and24 target comparisons verified.' if args.check else 'All fixed31 cases and24 target comparisons saved.')


if __name__=='__main__':
    main()
