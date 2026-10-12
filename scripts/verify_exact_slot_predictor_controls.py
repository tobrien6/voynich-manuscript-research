"""Independent stream reconstruction and separate fine-model control verification."""
import argparse
import gzip
import hashlib
import importlib
import json
import math
from pathlib import Path
import platform

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'research/baselines/exact-slot-control-pins.json'
MANIFEST_SHA = 'f927c977aeeae4892505cd3b3b97223786e8358d33c48eab8b77ec55ba302660'
CALIBRATOR_SHA = '999659bec8888f11afaeb720d7eaf36f18a7e8229f4d7912dd65b387468a5073'
METHOD = 'exact-slot-known-process-controls-v1'
CASES = ['independent_uniform', 'persistence_quarter', 'persistence_three_quarters', 'independent_alternating_positions']
CONTRASTS = ['previous_at_exact_slot', 'position_refinement', 'combined_model_difference']


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


class ByteStream:
    def __init__(self, key):
        self.key, self.index = key, 0
    def below(self, bound):
        assert bound in (4, 10)
        while True:
            byte = hashlib.sha256(self.key + self.index.to_bytes(16, 'big')).digest()[0]
            self.index += 1
            if byte < (256 if bound == 4 else 250):
                return byte % bound


def rows_for(templates, case, replicate):
    rows = []
    for t in templates:
        namespace = METHOD if case == CASES[3] else 'grouped-predictor-synthetic-controls-v1'
        args = [namespace, 20261012, replicate, case, t['key']]
        key = hashlib.sha256(json.dumps(args, ensure_ascii=False, separators=(',', ':')).encode()).digest()
        stream = ByteStream(key)
        if case == CASES[3]:
            counts = []
            for j in range(t['interior_size']):
                u = stream.below(4)
                counts.append(10 if u < (3 if j % 2 else 1) else 1)
        else:
            k = {'independent_uniform': 0, 'persistence_quarter': 1, 'persistence_three_quarters': 3}[case]
            counts = [1+stream.below(10)]
            for _ in range(t['interior_size']-1):
                event = stream.below(4)
                innovation = 1+stream.below(10)
                counts.append(counts[-1] if event < k else innovation)
        rows.append({field: t[field] for field in ('key', 'page', 'group', 'label')} | {'lengths': counts})
    return rows


def oracle(rows, case):
    gains, equal, favorable = [], 0, 0
    k = {'independent_uniform': 0, 'persistence_quarter': 1, 'persistence_three_quarters': 3}.get(case)
    for row in rows:
        for j in range(1, len(row['lengths'])):
            if k is None:
                high = .75 if j % 2 else .25
                p = high if row['lengths'][j] == 10 else 1-high
                favorable += p == .75
                gains.append(math.log2(2*p))
            else:
                equal += row['lengths'][j-1] == row['lengths'][j]
                rho = k/4
                p = rho+(1-rho)/10 if row['lengths'][j-1] == row['lengths'][j] else (1-rho)/10
                gains.append(math.log2(10*p))
    count, gain = len(gains), math.fsum(gains)
    if k is None:
        return {'transitions': count, 'favorable_position_classes': favorable,
                'binary_uniform_loss_bits': float(count), 'known_position_loss_bits': count-gain,
                'gain_bits': gain, 'gain_bits_per_transition': gain/count}
    baseline = count*math.log2(10)
    return {'transitions': count, 'equal_adjacent_classes': equal, 'uniform_loss_bits': baseline,
            'known_process_loss_bits': baseline-gain, 'gain_bits': gain, 'gain_bits_per_transition': gain/count}


def case_summary(records):
    assert [r['replicate'] for r in records] == list(range(64))
    result = {'replicates': 64, 'primary_fixed_criterion_hits': sum(
        r['summary']['contrasts'][CONTRASTS[0]]['fixed_diagnostic_preference'] for r in records), 'contrasts': {}}
    for c in CONTRASTS:
        data = [r['summary']['contrasts'][c] for r in records]
        result['contrasts'][c] = {}
        for field in ('micro_gain_bits_per_transition', 'group_macro_gain_bits_per_transition', 'locus_macro_gain_bits_per_transition'):
            series = [r[field] for r in data]
            result['contrasts'][c][field] = {'mean': math.fsum(series)/64, 'min': min(series), 'max': max(series)}
        result['contrasts'][c]['positive_pooled_replicates'] = sum(r['micro_gain_bits_per_transition'] > 0 for r in data)
        result['contrasts'][c]['positive_equal_group_replicates'] = sum(r['group_macro_gain_bits_per_transition'] > 0 for r in data)
    series = [r['oracle']['gain_bits_per_transition'] for r in records]
    result['oracle_gain_bits_per_transition'] = {'mean': math.fsum(series)/64, 'min': min(series), 'max': max(series)}
    return result


def compare(a, b):
    if canonical(a) != canonical(b):
        raise ValueError('complete independent control record differs')


def coarse_receipt(report, packed):
    cases = []
    for case in report['cases']:
        rows = []
        for ds in case['replicates']:
            s = ds['summary']
            pooled = (s['loss_bits']['Q0']-s['loss_bits']['Q1'])/s['transitions']
            group = math.fsum((g['loss_bits']['Q0']-g['loss_bits']['Q1'])/g['transitions'] for g in ds['groups'])/len(ds['groups'])
            positive = sum(f['loss_bits']['Q0'] > f['loss_bits']['Q1'] for f in ds['folds'])
            rows.append({'replicate': ds['replicate'], 'original_coarse_pooled_gain': pooled,
                         'original_coarse_equal_group_gain': group, 'original_coarse_positive_folds': positive,
                         'original_coarse_fixed_preference': pooled > 0 and group > 0 and positive >= 4})
        cases.append({'case': case['case'], 'replicates': rows,
                      'original_coarse_criterion_hits': sum(r['original_coarse_fixed_preference'] for r in rows),
                      'original_coarse_mean_pooled_gain': math.fsum(r['original_coarse_pooled_gain'] for r in rows)/64,
                      'original_coarse_mean_equal_group_gain': math.fsum(r['original_coarse_equal_group_gain'] for r in rows)/64})
    return {'schema_version': 1, 'status': 'post-result arithmetic display of the existing original coarse criterion; no new rule or fitted values',
            'source_report_gzip_sha256': hashlib.sha256(packed).hexdigest(),
            'source_report_json_sha256': hashlib.sha256(gzip.decompress(packed)).hexdigest(),
            'rule': 'originalQ1overQ0:positivepooled,positiveequalgroup,atleastfourpositivefolds', 'cases': cases}


def verify(path, progress=None):
    if not __debug__:
        raise ValueError('independent verification requires assertions')
    manifest = (ROOT/MANIFEST).read_bytes()
    assert hashlib.sha256(manifest).hexdigest() == MANIFEST_SHA
    pins = json.loads(manifest)
    for name, sha in pins.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == sha
    prefix = (__package__+'.') if __package__ else ''
    compat = importlib.import_module(prefix+'verify_grouped_predictor_controls')
    old, identities = compat.verified_inputs(ROOT)
    coarse = importlib.import_module(prefix+'grouped_length_prediction')
    engine = importlib.import_module(prefix+'verify_exact_slot_length_prediction')
    raw = path.read_bytes()
    report = json.loads(gzip.decompress(raw) if path.suffix == '.gz' else raw)
    assert report['input_pins'] == pins and report['pin_manifest_sha256'] == MANIFEST_SHA
    assert report['implementation_sha256'] == CALIBRATOR_SHA == hashlib.sha256((ROOT/'scripts/exact_slot_predictor_controls.py').read_bytes()).hexdigest()
    assert report['fine_producer_sha256'] == pins['scripts/exact_slot_length_prediction.py']
    assert report['original_coarse_producer_sha256'] == old['input_pins']['scripts/grouped_length_prediction.py']
    assert report['current_coarse_producer_sha256'] == identities['scripts/grouped_length_prediction.py']
    compare(report['layout'], old['layout'])
    assert [c['case'] for c in report['cases']] == CASES
    assert report['total_datasets'] == 256 and report['replicates_per_case'] == 64
    assert report['method'] == METHOD and report['seed'] == 20261012
    expected_header = {'schema_version': 1, 'method': METHOD,
        'status': 'fixed exposed-layout known-process performance; no native probability calibration',
        'python_version': platform.python_version(), 'seed': 20261012, 'input_pins': pins,
        'pin_manifest_sha256': MANIFEST_SHA, 'implementation_sha256': CALIBRATOR_SHA,
        'fine_producer_sha256': pins['scripts/exact_slot_length_prediction.py'],
        'original_coarse_producer_sha256': old['input_pins']['scripts/grouped_length_prediction.py'],
        'current_coarse_producer_sha256': identities['scripts/grouped_length_prediction.py'],
        'coarse_scientific_ast_matches_original_outside_reviewed_cli_guard': True,
        'layout': old['layout'], 'replicates_per_case': 64, 'total_datasets': 256,
        'complete_evaluation_digest_encoding': 'sorted-key compact UTF8 JSON; allow_nan=False'}
    compare(expected_header, {k: v for k, v in report.items() if k != 'cases'})
    old_index = {c['case']: c for c in old['cases']}
    templates, assignments = old['layout']['templates'], old['layout']['group_assignments']
    checked = 0
    for stored_case in report['cases']:
        case = stored_case['case']
        assert [r['replicate'] for r in stored_case['replicates']] == list(range(64))
        records = []
        for replicate in range(64):
            rows = rows_for(templates, case, replicate)
            source_sha = hashlib.sha256(json.dumps(rows, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
            original = coarse.evaluate(rows, assignments)
            reference = oracle(rows, case)
            if case != CASES[3]:
                previous = old_index[case]['replicates'][replicate]
                compact_old = {'replicate': replicate, 'sequence_sha256': source_sha, 'oracle': reference,
                               'summary': original['summary'], 'folds': [{k: v for k, v in f.items() if k != 'fitted_counts'} for f in original['folds']],
                               'groups': original['groups']}
                compare(compact_old, previous)
                old_sha = digest(previous)
            else:
                old_sha = None
            converted = [{k: v for k, v in r.items() if k != 'lengths'} | {'values': r['lengths']} for r in rows]
            fine = engine.evaluate(converted, assignments, original)
            expected = {'replicate': replicate, 'sequence_sha256': source_sha, 'original_control_record_sha256': old_sha,
                        'oracle': reference, 'complete_coarse_evaluation_sha256': digest(original),
                        'complete_fine_evaluation_sha256': digest(fine), 'summary': fine['summary'],
                        'folds': [{k: v for k, v in f.items() if k != 'fine_fitted_counts'} for f in fine['folds']], 'groups': fine['groups']}
            compare(expected, stored_case['replicates'][replicate])
            records.append(expected)
            checked += 1
            if progress and (replicate+1) % 8 == 0:
                progress(f'{case}: {replicate+1}/64 independent complete-evaluation digests matched')
        compare(case_summary(records), stored_case['summary'])
        if case == CASES[3]:
            assert stored_case['persistence_quarters'] is None and stored_case['original_datasets_reused'] is False
            assert stored_case['oracle_reference'] == 'uniform binary support {1,10}'
            ideal = .75*math.log2(1.5)+.25*math.log2(.5)
        else:
            k = {'independent_uniform': 0, 'persistence_quarter': 1, 'persistence_three_quarters': 3}[case]
            assert stored_case['persistence_quarters'] == k and stored_case['original_datasets_reused'] is True
            assert stored_case['oracle_reference'] == 'uniform ten-class marginal'
            rho = k/4
            d, o = rho+(1-rho)/10, (1-rho)/10
            ideal = d*math.log2(10*d)+9*o*math.log2(10*o)
        assert stored_case['ideal_oracle_gain_bits_per_transition'] == ideal
        compare({'case': case, 'original_datasets_reused': case != CASES[3],
                 'persistence_quarters': None if case == CASES[3] else k,
                 'oracle_reference': 'uniform binary support {1,10}' if case == CASES[3] else 'uniform ten-class marginal',
                 'ideal_oracle_gain_bits_per_transition': ideal, 'summary': case_summary(records), 'replicates': records}, stored_case)
    return {'datasets': checked, 'original_datasets_reproduced': 192, 'complete_fine_evaluation_digests': checked,
            'scored_transitions': checked*13713, 'exact_fine_probabilities': 2*checked*13713}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=ROOT/'research/baselines/exact-slot-predictor-controls.json.gz')
    parser.add_argument('--coarse-receipt', type=Path, default=ROOT/'research/baselines/exact-slot-control-coarse-receipt.json')
    args = parser.parse_args()
    try:
        result = verify(args.report, progress=lambda m: print(m, flush=True))
        packed = args.report.read_bytes()
        if args.report.suffix != '.gz':
            raise ValueError('coarse receipt binds the published gzip transport')
        compare(coarse_receipt(json.loads(gzip.decompress(packed)), packed), json.loads(args.coarse_receipt.read_text()))
    except (AssertionError, ValueError, OSError, EOFError, KeyError, TypeError) as error:
        parser.exit(1, f'Independent exact-slot control check failed: {error}\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
