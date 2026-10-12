"""Fixed exact-slot performance on exposed old controls and independent positions."""
import argparse
import gzip
import hashlib
import importlib
import json
import math
from pathlib import Path
import platform

ROOT = Path(__file__).resolve().parents[1]
PLAN = 'research/baselines/EXACT_SLOT_CONTROL_PLAN.md'
PINS = 'research/baselines/exact-slot-control-pins.json'
PIN_SHA256 = 'f927c977aeeae4892505cd3b3b97223786e8358d33c48eab8b77ec55ba302660'
OLD = 'research/baselines/grouped-predictor-controls.json'
METHOD = 'exact-slot-known-process-controls-v1'
SEED, REPLICATES = 20261012, 64
NEW_CASE = 'independent_alternating_positions'
CASES = ['independent_uniform', 'persistence_quarter', 'persistence_three_quarters', NEW_CASE]
MODELS = ['Q0', 'Q1', 'F0', 'F1']
CONTRASTS = ['previous_at_exact_slot', 'position_refinement', 'combined_model_difference']


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def same(a, b):
    return canonical(a) == canonical(b)


def module(name):
    return importlib.import_module((__package__ + '.' if __package__ else '') + name)


def load_inputs():
    raw = (ROOT/PINS).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN_SHA256:
        raise ValueError('frozen exact-slot controls manifest changed')
    pins = json.loads(raw)
    for name, sha in pins.items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != sha:
            raise ValueError('frozen control input changed: ' + name)
    compatibility = module('verify_grouped_predictor_controls')
    old, identities = compatibility.verified_inputs(ROOT)
    generator = module('grouped_predictor_controls')
    fine = module('exact_slot_length_prediction')
    templates, assignments = generator.layout_from_report(json.loads((ROOT/generator.PARENT).read_bytes()))
    expected = {'source_treatment': 'ZL3b/split', 'templates': templates,
                'group_assignments': assignments, 'sha256': generator.digest([templates, assignments])}
    if not same(expected, old['layout']) or old['total_datasets'] != 192 or old['replicates_per_case'] != REPLICATES:
        raise ValueError('complete original primary layout/cases changed')
    if [c['case'] for c in old['cases']] != CASES[:3]:
        raise ValueError('complete original control cases required')
    if any([r['replicate'] for r in c['replicates']] != list(range(REPLICATES)) for c in old['cases']):
        raise ValueError('all original ordered replicate records required')
    return old, pins, identities, generator, fine


def alternating_sequence(size, draws):
    if type(size) is not int or size < 3:
        raise ValueError('at least three synthetic slots required')
    return [10 if draws.below(4) < (1 if i % 2 == 0 else 3) else 1 for i in range(size)]


def generate(templates, replicate, case, generator):
    if type(replicate) is not int or replicate not in range(REPLICATES) or case not in CASES:
        raise ValueError('fixed case/replicate required')
    if case != NEW_CASE:
        return generator.simulate(templates, replicate, case)
    rows = []
    for row in templates:
        key = hashlib.sha256(generator.estimator.parent.compact([METHOD, SEED, replicate, case, row['key']])).digest()
        rows.append({name: row[name] for name in ('key', 'page', 'group', 'label')}
                    | {'lengths': alternating_sequence(row['interior_size'], generator.HashDraws(key))})
    return rows


def alternating_oracle(rows):
    gains = []
    favorable = 0
    for row in rows:
        if len(row['lengths']) < 3 or any(type(v) is not int or v not in (1, 10) for v in row['lengths']):
            raise ValueError('alternating oracle needs binary class support')
        for j in range(1, len(row['lengths'])):
            p_high = .25 if j % 2 == 0 else .75
            p = p_high if row['lengths'][j] == 10 else 1-p_high
            favorable += p == .75
            gains.append(math.log2(2*p))
    count, gain = len(gains), math.fsum(gains)
    if not count:
        raise ValueError('alternating oracle needs scored transitions')
    return {'transitions': count, 'favorable_position_classes': favorable, 'binary_uniform_loss_bits': float(count),
            'known_position_loss_bits': count-gain, 'gain_bits': gain, 'gain_bits_per_transition': gain/count}


def compact_fine(value):
    return {'summary': value['summary'], 'folds': [{k: v for k, v in f.items() if k != 'fine_fitted_counts'} for f in value['folds']],
            'groups': value['groups']}


def evaluate_dataset(templates, assignments, replicate, case, old_record, generator, fine):
    rows = generate(templates, replicate, case, generator)
    original = generator.estimator.evaluate(rows, assignments)
    if case == NEW_CASE:
        oracle = alternating_oracle(rows)
        old_digest = None
    else:
        oracle = generator.oracle_score(rows, generator.CASES[case])
        reproduced = {'replicate': replicate, 'sequence_sha256': generator.digest(rows), 'oracle': oracle,
                      **generator.compact_evaluation(original)}
        if not same(reproduced, old_record):
            raise ValueError('original full coarse dataset differs before new fine fit')
        old_digest = digest(old_record)
    value = fine.evaluate(rows, assignments, original)
    return {'replicate': replicate, 'sequence_sha256': generator.digest(rows),
            'original_control_record_sha256': old_digest, 'oracle': oracle,
            'complete_coarse_evaluation_sha256': digest(original), 'complete_fine_evaluation_sha256': digest(value),
            **compact_fine(value)}


def summaries(records):
    if [r['replicate'] for r in records] != list(range(REPLICATES)):
        raise ValueError('all64 original ordered replicate indices required')
    result = {'replicates': len(records), 'primary_fixed_criterion_hits': sum(
        r['summary']['contrasts']['previous_at_exact_slot']['fixed_diagnostic_preference'] for r in records), 'contrasts': {}}
    for contrast in CONTRASTS:
        values = [r['summary']['contrasts'][contrast] for r in records]
        fields = ['micro_gain_bits_per_transition', 'group_macro_gain_bits_per_transition', 'locus_macro_gain_bits_per_transition']
        result['contrasts'][contrast] = {field: {'mean': math.fsum(v[field] for v in values)/len(values),
                                               'min': min(v[field] for v in values), 'max': max(v[field] for v in values)} for field in fields}
        result['contrasts'][contrast]['positive_pooled_replicates'] = sum(v[fields[0]] > 0 for v in values)
        result['contrasts'][contrast]['positive_equal_group_replicates'] = sum(v[fields[1]] > 0 for v in values)
    gains = [r['oracle']['gain_bits_per_transition'] for r in records]
    result['oracle_gain_bits_per_transition'] = {'mean': math.fsum(gains)/len(gains), 'min': min(gains), 'max': max(gains)}
    return result


def report(progress=None):
    old, pins, identities, generator, fine = load_inputs()
    templates, assignments = old['layout']['templates'], old['layout']['group_assignments']
    old_cases = {c['case']: c for c in old['cases']}
    cases = []
    for case in CASES:
        records = []
        for replicate in range(REPLICATES):
            source = old_cases[case]['replicates'][replicate] if case != NEW_CASE else None
            records.append(evaluate_dataset(templates, assignments, replicate, case, source, generator, fine))
            if progress and (replicate+1) % 8 == 0:
                progress(f'{case}: {replicate+1}/{REPLICATES} complete evaluations retained')
        cases.append({'case': case, 'original_datasets_reused': case != NEW_CASE,
                      'persistence_quarters': generator.CASES[case] if case != NEW_CASE else None,
                      'oracle_reference': 'uniform ten-class marginal' if case != NEW_CASE else 'uniform binary support {1,10}',
                      'ideal_oracle_gain_bits_per_transition': generator.ideal_gain(generator.CASES[case]) if case != NEW_CASE else
                          .75*math.log2(1.5)+.25*math.log2(.5), 'summary': summaries(records), 'replicates': records})
    return {'schema_version': 1, 'method': METHOD, 'status': 'fixed exposed-layout known-process performance; no native probability calibration',
            'python_version': platform.python_version(), 'seed': SEED, 'input_pins': pins, 'pin_manifest_sha256': PIN_SHA256,
            'implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'fine_producer_sha256': pins['scripts/exact_slot_length_prediction.py'],
            'original_coarse_producer_sha256': old['input_pins']['scripts/grouped_length_prediction.py'],
            'current_coarse_producer_sha256': identities['scripts/grouped_length_prediction.py'],
            'coarse_scientific_ast_matches_original_outside_reviewed_cli_guard': True,
            'layout': old['layout'], 'replicates_per_case': REPLICATES, 'total_datasets': len(CASES)*REPLICATES,
            'complete_evaluation_digest_encoding': 'sorted-key compact UTF8 JSON; allow_nan=False', 'cases': cases}


def protect(path):
    raw = (ROOT/PINS).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN_SHA256:
        raise ValueError('control manifest changed before output guard')
    protected = [ROOT/n for n in json.loads(raw)] + [ROOT/PINS, Path(__file__).resolve()]
    catalog = ROOT/'data/transliterations.json'
    if catalog.exists():
        protected.append(catalog)
        protected.extend(ROOT/s['path'] for s in json.loads(catalog.read_bytes())['sources'])
    if (any(path.resolve().is_relative_to((ROOT/n).resolve()) for n in ('data', 'scripts')) or
            any(path.resolve() == p.resolve() or (path.exists() and p.exists() and path.samefile(p)) for p in protected)):
        raise ValueError('output aliases control/code/source/plan/parent inputs')


def serialize(value, compressed):
    raw = (json.dumps(value, indent=2, allow_nan=False)+'\n').encode()
    return gzip.compress(raw, mtime=0) if compressed else raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--new-report', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        path = args.new_report or args.check
        protect(path)
        if args.new_report and (path.exists() or path.is_symlink()):
            raise ValueError('new control report already exists')
        value = report(progress=lambda m: print(m, flush=True))
        payload = serialize(value, path.suffix == '.gz')
        if args.check:
            if path.read_bytes() != payload:
                raise ValueError('complete control byte replay differs')
        else:
            protect(path)
            with path.open('xb') as output:
                output.write(payload)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'Exact-slot controls failed: {error}\n')
    print('All256 fixed control datasets verified.' if args.check else 'All256 fixed control datasets saved.')


if __name__ == '__main__':
    main()
