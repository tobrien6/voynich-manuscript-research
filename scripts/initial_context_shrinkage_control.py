"""Constructed constant-older-context control; no manuscript data or model fit."""
import argparse
from collections import Counter
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import string

ROOT = Path(__file__).resolve().parents[1]
PLAN = 'research/baselines/initial-context-control-plan.json'
NOTE = 'research/baselines/INITIAL_CONTEXT_CONTROL_PLAN.md'
PINS = {PLAN: 'c112afadf19e4a8a0a71cb8f679684ac7dac167b34dc95bacea8d620d0f69c4b',
        NOTE: '17d617603b493dd3e664d12e65087426087a09ea8b25060ffb521aa0f441e97e',
        'research/baselines/eva-unit-protocol.json': 'a2ded6526829759169d9462708ea00f969ebe47127acf5c90e2f0b1e7e2fc3ec'}
BOS, EOS = '<BOS>', '<EOS>'
STRENGTH = F(16)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('nonfinite JSON: ' + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()


def rational(value):
    return [value.numerator, value.denominator]


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load_inputs(root=ROOT):
    for name, pin in PINS.items():
        require(digest((root / name).read_bytes()) == pin, 'fixed input changed: ' + name)
    plan = strict_json((root / PLAN).read_bytes())
    settings = strict_json((root / plan['unit_protocol_path']).read_bytes())
    require([p['id'] for p in settings['policies']] ==
            ['ascii_letters', 'bench_sequences', 'bench_and_minim_sequences'], 'policy scope changed')
    return plan, settings['policies']


def events(units):
    require(isinstance(units, list) and units and all(isinstance(u, str) and u
            and u not in (BOS, EOS) for u in units), 'require nonempty units without reserved labels')
    values = [BOS, BOS, *units, EOS]
    return [tuple(values[i-2:i+1]) for i in range(2, len(values))]


def fit(rows, alphabet):
    require(rows and len(alphabet) == len(set(alphabet)) and EOS in alphabet and BOS not in alphabet,
            'nonempty rows and unique target alphabet required')
    triples = Counter(e for row in rows for e in events(row['units']))
    targets, pairs, first_totals, second_totals = Counter(), Counter(), Counter(), Counter()
    for (w, x, y), n in triples.items():
        require(y in alphabet, 'target outside alphabet')
        targets[y] += n
        pairs[x, y] += n
        first_totals[x] += n
        second_totals[w, x] += n
    return dict(targets=targets, pairs=pairs, triples=triples, first_totals=first_totals,
                second_totals=second_totals, total=sum(targets.values()), alphabet=tuple(alphabet))


def smooth(count, total, prior, strength=STRENGTH):
    require(type(count) is int and type(total) is int and 0 <= count <= total,
            'nonnegative integral counts required')
    require(isinstance(prior, F) and 0 <= prior <= 1 and strength > 0, 'valid rational prior required')
    return (count + strength * prior) / (total + strength)


def effective_strength(total):
    require(type(total) is int and total >= 0, 'nonnegative context total required')
    return STRENGTH ** 2 / (total + 2 * STRENGTH)


def probabilities(model, w, x, y):
    require(y in model['alphabet'], 'target outside alphabet')
    q0 = F(2*model['targets'][y]+1, 2*model['total']+len(model['alphabet']))
    q1 = smooth(model['pairs'][x, y], model['first_totals'][x], q0)
    q2 = smooth(model['triples'][w, x, y], model['second_totals'][w, x], q1)
    q1_eff = smooth(model['pairs'][x, y], model['first_totals'][x], q0,
                    effective_strength(model['first_totals'][x]))
    return q0, q1, q2, q1_eff


def counts_record(model):
    return {'targets': [[y,n] for y,n in sorted(model['targets'].items())],
            'first': [[x,y,n] for (x,y),n in sorted(model['pairs'].items())],
            'second': [[w,x,y,n] for (w,x,y),n in sorted(model['triples'].items())],
            'total_targets': model['total']}


def score(row, model):
    sequence = events(row['units'])
    qs = [probabilities(model, *event) for event in sequence]
    losses = [-math.fsum(math.log2(float(q[j])) for q in qs) for j in range(4)]
    return {'group': row['group'], 'fold': row['fold'], 'tokens': 1, 'units': len(row['units']),
            'targets': len(sequence), 'loss_bits_q0_q1_q2_q1_eff': losses,
            'constant_context_equivalence': all(q[2] == q[3] for q in qs),
            'gain12_bits_per_target': (losses[1]-losses[2])/len(sequence),
            'gain_q2_over_q1_eff_bits_per_target': (losses[3]-losses[2])/len(sequence)}


def preference(pooled, group, folds):
    require(len(folds) == 5, 'five fold gains required')
    return pooled >= .02 and group > 0 and all(gain > 0 for gain in folds)


def fold_population(rows, fold):
    require(len(rows) == 5 and len({r['group'] for r in rows}) == 5
            and {r['fold'] for r in rows} == set(range(5))
            and all(type(r['fold']) is int for r in rows), 'five distinct toy groups/folds required')
    require(type(fold) is int and fold in range(5), 'valid toy fold required')
    training = [r for r in rows if r['fold'] != fold]
    scoring = [r for r in rows if r['fold'] == fold]
    require(len(training) == 4 and len(scoring) == 1
            and not {r['group'] for r in training} & {r['group'] for r in scoring},
            'toy train/scoring separation failed')
    return training, scoring


def build_report(root=ROOT):
    plan, policies = load_inputs(root)
    rows = [{'group': f'toy-{i}', 'fold': i, 'units': ['a']} for i in range(5)]
    treatments = []
    for policy, expected in zip(policies, plan['expected_target_probabilities']):
        patterns = policy['patterns']
        require('a' not in patterns and all(len(p)>1 for p in patterns), 'toy segmentation changed')
        alphabet = sorted(set(string.ascii_letters) | set(patterns) | {EOS})
        require(len(alphabet) == expected['alphabet_size'], 'declared alphabet size changed')
        folds, distributions = [], None
        for fold in range(5):
            training, scoring = fold_population(rows, fold)
            model = fit(training, alphabet)
            require({e[0] for e in model['triples']} == {BOS}, 'older context is not constant')
            require(model['total'] == 8 and len(training) == 4 and len(scoring) == 1,
                    'toy fit/scoring frame changed')
            all_probabilities = []
            for x in (BOS, 'a'):
                qs = [probabilities(model, BOS, x, y) for y in alphabet]
                require(all(sum(q[j] for q in qs) == 1 for j in range(4)), 'distribution normalization failed')
                all_probabilities.append({'older': BOS, 'previous': x,
                    'effective_strength': rational(effective_strength(model['first_totals'][x])),
                    'full_alphabet_equivalence': all(q[2] == q[3] for q in qs),
                    'targets': [{'target': y, 'q0_q1_q2_q1_eff': [rational(p) for p in q]}
                                for y,q in zip(alphabet,qs)]})
            require(distributions is None or distributions == all_probabilities, 'toy folds differ unexpectedly')
            distributions = all_probabilities
            folds.append({'fold': fold, 'training_groups': [r['group'] for r in training],
                          'scoring_groups': [r['group'] for r in scoring],
                          'training_counts': counts_record(model),
                          'analytical_target_prediction_matches': all(
                              [rational(q) for q in probabilities(model, *event)[:3]] ==
                              [expected[k] for k in ('q0','q1','q2')] for event in events(['a'])),
                          'probabilities_sha256': digest(encoded(distributions)),
                          'scored_locus': score(scoring[0], model)})
        scores = [f['scored_locus'] for f in folds]
        targets = sum(s['targets'] for s in scores)
        losses = [math.fsum(s['loss_bits_q0_q1_q2_q1_eff'][j] for s in scores) for j in range(4)]
        pooled = (losses[1]-losses[2])/targets
        group = math.fsum(s['gain12_bits_per_target'] for s in scores)/len(scores)
        treatments.append({'unit_policy': policy['id'], 'target_alphabet': alphabet,
            'older_context_values': [BOS], 'all_context_probabilities': distributions, 'folds': folds,
            'summary': {'groups': 5, 'tokens': 5, 'units': 5, 'targets': targets,
                'loss_bits_q0_q1_q2_q1_eff': losses, 'pooled_gain12_bits_per_target': pooled,
                'equal_group_gain12_bits_per_target': group,
                'all_analytical_predictions_match': all(f['analytical_target_prediction_matches'] for f in folds),
                'full_alphabet_equivalence': all(c['full_alphabet_equivalence'] for c in distributions),
                'equivalent_loss_identity': losses[2] == losses[3],
                'gain_q2_over_q1_eff_bits_per_target': (losses[3]-losses[2])/targets,
                'fixed_second_order_preference': preference(pooled, group,
                    [s['gain12_bits_per_target'] for s in scores])}})
    require(load_inputs(root)[0] == plan, 'inputs changed during construction')
    return {'schema_version': 1, 'analysis_id': plan['analysis_id'], 'analysis_status': plan['analysis_status'],
            'input_pins': PINS, 'implementation_sha256': digest(Path(__file__).read_bytes()),
            'referenced_predictor': {k:plan[k] for k in plan if k.startswith('referenced_predictor_')},
            'synthetic_population': rows, 'models': ['Q0','Q1','Q2','Q1_eff'],
            'manuscript_fit': False, 'outcome_was_predicted_analytically': True,
            'fold_assignment_differs_from_manuscript_hash_groups': True, 'treatments': treatments,
            'limitations': ['Constructed possibility example, not a power or specificity calibration.',
                'No causal share of manuscript gain, preferred manuscript prior or extra context structure is estimated.',
                'No glyph meaning, language, decipherment or translation is established.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        if args.output:
            require(not args.output.exists() and not args.output.is_symlink(), 'output must be a new file')
        report = build_report(ROOT)
        raw = encoded(report)
        if args.check:
            strict_json(args.check.read_bytes())
            require(args.check.read_bytes() == raw, 'complete synthetic report differs from replay')
        else:
            load_inputs(ROOT)
            require(digest(Path(__file__).read_bytes()) == report['implementation_sha256'],
                    'producer changed during construction')
            with args.output.open('xb') as output:
                output.write(raw)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'initial-context control failed: {error}\n')
    print('Complete synthetic report verified.' if args.check else 'New synthetic report created.')


if __name__ == '__main__':
    main()
