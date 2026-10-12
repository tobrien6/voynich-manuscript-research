"""Previously exposed grouped exact-slot count prediction with matched weights."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import gzip
import hashlib
import json
import math
from pathlib import Path
import platform

try:
    from . import grouped_length_prediction as coarse
except ImportError:
    import grouped_length_prediction as coarse

ROOT = Path(__file__).resolve().parents[1]
PLAN = 'research/baselines/EXACT_SLOT_LENGTH_PLAN.md'
PINS = 'research/baselines/exact-slot-length-pins.json'
PARENT = 'research/baselines/grouped-length-prediction.json'
PIN_SHA256 = '3c31d97b437e3f0b37be9dbc2ca19d8189945e72c71618eb1bb997574940305f'
MODELS = ['Q0', 'Q1', 'F0', 'F1']
CONTRASTS = {'previous_at_exact_slot': ('F1', 'F0'), 'position_refinement': ('F0', 'Q0'),
             'combined_model_difference': ('F1', 'Q1')}


def same(a, b):
    return json.dumps(a, sort_keys=True, allow_nan=False) == json.dumps(b, sort_keys=True, allow_nan=False)


def events(row):
    coarse.transitions(row)  # Validate original class, label and length conventions.
    values = [coarse.length_class(v) for v in row['lengths']]
    return [((row['label'], len(values), j), values[j-1], values[j]) for j in range(1, len(values))]


def fit(rows):
    if not rows or len({r['key'] for r in rows}) != len(rows):
        raise ValueError('nonempty unique training loci required')
    targets, pairs = defaultdict(Counter), defaultdict(Counter)
    for row in rows:
        for context, x, y in events(row):
            targets[context][y] += 1
            pairs[context, x][y] += 1
    model = {'coarse': coarse.fit(rows), 'targets': dict(targets), 'pairs': dict(pairs)}
    validate_model(model)
    return model


def probabilities(model, context, previous, target):
    label, size, slot = context
    if (not isinstance(label, str) or not label or type(size) is not int or size < 3 or type(slot) is not int or not 1 <= slot < size
            or any(type(v) is not int or not 1 <= v <= 10 for v in (previous, target))):
        raise ValueError('valid exact slot and original count classes required')
    c = label, int(slot >= (size + 1) // 2)
    prior_counts = model['coarse']['targets'].get(c, {})
    prior = Fraction(prior_counts.get(target, 0) + 1, sum(prior_counts.values()) + 10)
    targets = model['targets'].get(context, {})
    pairs = model['pairs'].get((context, previous), {})
    n, nx = sum(targets.values()), sum(pairs.values())
    f0 = (targets.get(target, 0) + 10 * prior) / (n + 10)
    f1 = (Fraction(n * pairs.get(target, 0), nx) + 10 * prior) / (n + 10) if nx else f0
    return f0, f1


def model_record(model):
    return [{'source_label': c[0], 'interior_size': c[1], 'target_slot': c[2],
             'target_counts': [model['targets'][c].get(y, 0) for y in range(1, 11)],
             'previous_target_counts': [[model['pairs'].get((c, x), {}).get(y, 0) for y in range(1, 11)]
                                       for x in range(1, 11)]} for c in sorted(model['targets'])]


def validate_model(model):
    for context, targets in model['targets'].items():
        n = sum(targets.values())
        previous = {x: sum(model['pairs'].get((context, x), {}).values()) for x in range(1, 11)}
        if not n or sum(previous.values()) != n:
            raise ValueError('fine target/previous totals differ')
        for x in range(1, 11):
            probs = [probabilities(model, context, x, y) for y in range(1, 11)]
            if (sum(p[0] for p in probs) != 1 or sum(p[1] for p in probs) != 1
                    or any(p[0] <= 0 or p[1] <= 0 for p in probs)):
                raise ValueError('fine probabilities not normalized')
        for y in range(1, 11):
            mixture = sum((Fraction(nx, n) * probabilities(model, context, x, y)[1]
                           for x, nx in previous.items() if nx), Fraction())
            if mixture != probabilities(model, context, 1, y)[0]:
                raise ValueError('training previous-frequency mixture differs from F0')


def score_row(row, model, fold):
    losses = {m: [] for m in MODELS}
    receipts = []
    for context, x, y in events(row):
        c = context[0], int(context[2] >= (context[1] + 1) // 2)
        q0, q1 = coarse.probabilities(model['coarse'], c, x, y)
        f0, f1 = probabilities(model, context, x, y)
        for name, p in zip(MODELS, (q0, q1, f0, f1)):
            losses[name].append(-math.log2(float(p)))
        n = sum(model['targets'].get(context, {}).values())
        nx = sum(model['pairs'].get((context, x), {}).values())
        previous_classes = [a for a in range(1, 11) if sum(model['pairs'].get((context, a), {}).values())]
        constant = len(previous_classes) == 1
        if constant and f0 != f1:
            raise ValueError('constant previous class changed probability')
        receipts.append({'target_slot': context[2], 'previous_class': x, 'target_class': y,
                         'fine_training_transitions': n, 'previous_training_transitions': nx,
                         'coarse_training_transitions': sum(model['coarse']['targets'].get(c, {}).values()),
                         'constant_previous_context': constant,
                         'F0': [str(f0.numerator), str(f0.denominator)],
                         'F1': [str(f1.numerator), str(f1.denominator)]})
    return {'locus_key': row['key'], 'page_id': row['page'], 'group_id': row['group'],
            'source_label': row['label'], 'fold': fold, 'interior_size': len(row['lengths']),
            'transitions': len(receipts), 'loss_bits': {name: math.fsum(v) for name, v in losses.items()},
            'transition_receipts': receipts}


def aggregate(rows):
    if not rows:
        raise ValueError('nonempty scored rows required')
    count = sum(r['transitions'] for r in rows)
    losses = {m: math.fsum(r['loss_bits'][m] for r in rows) for m in MODELS}
    return {'loci': len(rows), 'transitions': count, 'loss_bits': losses,
            'contrasts': {tag: {'gain_bits': losses[b] - losses[a],
                              'micro_gain_bits_per_transition': (losses[b] - losses[a]) / count,
                              'locus_macro_gain_bits_per_transition': math.fsum(
                                  (r['loss_bits'][b] - r['loss_bits'][a]) / r['transitions'] for r in rows) / len(rows)}
                          for tag, (a, b) in CONTRASTS.items()},
            'support': {name: sum(condition(t) for r in rows for t in r['transition_receipts']) for name, condition in {
                'unseen_coarse_context': lambda t: t['coarse_training_transitions'] == 0,
                'unseen_fine_context': lambda t: t['fine_training_transitions'] == 0,
                'seen_fine_unseen_previous': lambda t: t['fine_training_transitions'] > 0 and t['previous_training_transitions'] == 0,
                'constant_previous_context': lambda t: t['constant_previous_context']}.items()}}


def evaluate(rows, assignments, parent_result):
    original = coarse.evaluate(rows, assignments)
    if not same(original, {k: parent_result[k] for k in ('summary', 'folds', 'groups', 'loci')}):
        raise ValueError('complete original coarse predictor differs')
    folds, scored = [], []
    for fold in range(5):
        train = [r for r in rows if assignments[r['group']] != fold]
        test = [r for r in rows if assignments[r['group']] == fold]
        model = fit(train)
        tables = model_record(model)
        scores = [score_row(r, model, fold) for r in test]
        scored.extend(scores)
        folds.append({'fold': fold, 'training_loci': len(train),
                      'training_transitions': sum(len(events(r)) for r in train),
                      'training_group_ids': sorted({r['group'] for r in train}),
                      'scoring_group_ids': sorted({r['group'] for r in test}),
                      'coarse_fitted_counts_sha256': hashlib.sha256(coarse.parent.compact(coarse.model_record(model['coarse']))).hexdigest(),
                      'fine_fitted_counts_sha256': hashlib.sha256(coarse.parent.compact(tables)).hexdigest(),
                      'fine_fitted_counts': tables, **aggregate(scores)})
    if Counter(r['locus_key'] for r in scored) != Counter(r['key'] for r in rows):
        raise ValueError('not every original locus scored once')
    old_rows = {r['locus_key']: r for r in original['loci']}
    for r in scored:
        if r['loss_bits']['Q0'] != old_rows[r['locus_key']]['baseline_loss_bits'] or r['loss_bits']['Q1'] != old_rows[r['locus_key']]['transition_loss_bits']:
            raise ValueError('original locus losses changed')
    by_group = defaultdict(list)
    for r in scored:
        by_group[r['group_id']].append(r)
    groups = [{'group_id': g, 'fold': assignments[g], **aggregate(v)} for g, v in sorted(by_group.items())]
    summary = aggregate(scored)
    summary['groups'] = len(groups)
    for tag, values in summary['contrasts'].items():
        values['group_macro_gain_bits_per_transition'] = math.fsum(g['contrasts'][tag]['micro_gain_bits_per_transition'] for g in groups) / len(groups)
        values['positive_fold_count'] = sum(f['contrasts'][tag]['micro_gain_bits_per_transition'] > 0 for f in folds)
        values['positive_group_count'] = sum(g['contrasts'][tag]['micro_gain_bits_per_transition'] > 0 for g in groups)
        values['fixed_diagnostic_preference'] = (values['micro_gain_bits_per_transition'] > 0 and
            values['group_macro_gain_bits_per_transition'] > 0 and values['positive_fold_count'] >= 4) if tag == 'previous_at_exact_slot' else None
    return {'summary': summary, 'folds': folds, 'groups': groups, 'loci': sorted(scored, key=lambda r: r['locus_key'])}


def inputs():
    raw = (ROOT / PINS).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN_SHA256:
        raise ValueError('frozen exact-slot manifest changed')
    pins = json.loads(raw)
    for name, expected in pins.items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError('frozen exact-slot input changed: ' + name)
    return json.loads((ROOT / PARENT).read_text()), pins


def report(progress=None):
    previous, pins = inputs()
    prepared, assignments, manifest, provenance, selection = coarse.inputs()
    variants = [(s, p) for s in ('ZL3b', 'IT2a') for p in ('split', 'join')]
    if ([(s, p) for s, p, _, _ in prepared] != variants
            or [(t['source_id'], t['spacing']) for t in previous['treatments']] != variants):
        raise ValueError('complete four-treatment family required')
    if not same(manifest, previous['folds']['group_assignments']):
        raise ValueError('original group/fold manifest changed')
    results = []
    for (sid, spacing, rows, digest), old in zip(prepared, previous['treatments']):
        if (sid, spacing, digest) != (old['source_id'], old['spacing'], old['length_corpus_sha256']):
            raise ValueError('original treatment identity changed')
        results.append({'source_id': sid, 'spacing': spacing, 'source_sha256': provenance[sid]['sha256'],
                        'length_corpus_sha256': digest, **evaluate(rows, assignments, old)})
        if progress:
            progress(sid + '/' + spacing + ': all original and exact-slot fits verified')
    return {'schema_version': 1, 'method': 'grouped-exact-slot-matched-weight-length-prediction-v1',
            'status': 'previously exposed corpus; dependency-group parameter-fit exclusion only',
            'python_version': platform.python_version(), 'input_pins': pins, 'pin_manifest_sha256': PIN_SHA256,
            'implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'selection': previous['selection'], 'folds': previous['folds'],
            'models': MODELS, 'contrasts': {k: list(v) for k, v in CONTRASTS.items()},
            'fixed_prior_strength': 10, 'previous_training_frequency_mixture_equals_F0': True,
            'all_treatments_meet_primary_preference': all(r['summary']['contrasts']['previous_at_exact_slot']['fixed_diagnostic_preference'] for r in results),
            'original_coarse_report_reproduced_completely': True, 'treatments': results}


def protect(path):
    raw = (ROOT / PINS).read_bytes()
    if hashlib.sha256(raw).hexdigest() != PIN_SHA256:
        raise ValueError('frozen exact-slot manifest changed before output guard')
    pins = json.loads(raw)
    protected = [ROOT / n for n in pins] + [ROOT / PINS, Path(__file__).resolve()]
    protected.extend(ROOT / s['path'] for s in json.loads((ROOT / 'data/transliterations.json').read_text())['sources'])
    if (any(path.resolve().is_relative_to((ROOT / n).resolve()) for n in ('data', 'scripts')) or
        any(path.resolve() == p.resolve() or (path.exists() and p.exists() and path.samefile(p)) for p in protected)):
        raise ValueError('output aliases exact-slot inputs, native sources, code or plan')


def serialize(value, compressed):
    raw = (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()
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
            raise ValueError('new report destination exists')
        value = report(progress=lambda m: print(m, flush=True))
        payload = serialize(value, path.suffix == '.gz')
        if args.check:
            if path.read_bytes() != payload:
                raise ValueError('complete exact-slot byte replay differs')
        else:
            protect(path)
            with path.open('xb') as out:
                out.write(payload)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'Exact-slot length prediction failed: {error}\n')
    print('All four grouped exact-slot treatments verified.' if args.check else 'All four grouped exact-slot treatments saved.')


if __name__ == '__main__':
    main()
