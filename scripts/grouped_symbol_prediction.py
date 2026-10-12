"""Fixed within-token notation predictors with group-excluded parameter fits."""

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import string

try:
    from . import paired_symbol_entropy as parent
    from .audit_transcription_images import dependency_components, page_reference
except ImportError:
    import paired_symbol_entropy as parent
    from audit_transcription_images import dependency_components, page_reference


ROOT = Path(__file__).resolve().parents[1]
METHOD = 'grouped-symbol-prediction-v1'
PLAN = Path('research/baselines/grouped-symbol-plan.json')
NOTE = Path('research/baselines/GROUPED_SYMBOL_PLAN.md')
PARENT = Path('research/representation/paired_symbol_entropy.json')
IMAGE = Path('research/folio-alignment/transcription-image-coverage.json')
CANVASES = Path('research/image-index/canvases.csv')
BOS, EOS = '<BOS>', '<EOS>'
FOLDS, SEED = 5, 20261012
ALPHA, STRENGTH, MIN_GAIN = 0.5, 16, 0.02
PIN_PATHS = {
    'data/transliterations.json', 'research/baselines/eva-unit-protocol.json',
    'research/representation/paired-entropy-plan.json',
    'research/representation/PAIRED_ENTROPY_PLAN.md', str(PARENT), str(IMAGE), str(CANVASES),
    *('scripts/' + name + '.py' for name in (
        'audit_transliterations', 'ivtff', 'eva_token_adapter', 'token_baselines',
        'eva_unit_sensitivity', 'paired_symbol_entropy', 'audit_transcription_images',
        'index_yale_manifest', 'validate_evaluation_split')),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(compact(value)).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result

    def invalid(value):
        raise ValueError('nonfinite JSON value: ' + value)

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def load_plan(root):
    plan = strict_json((root / PLAN).read_bytes())
    fixed = {
        'schema_version': 1, 'analysis_id': METHOD,
        'analysis_status': 'exploratory; whole corpus previously exposed; group exclusion from parameter fits only',
        'source_ids': list(parent.SOURCE_IDS), 'spacing_policies': list(parent.SPACING),
        'unit_policy_ids': list(parent.UNIT_IDS),
        'boundary': 'reset each token; score all units plus one EOS target; two BOS context labels',
        'alphabet': '52 ASCII letters plus declared patterns plus EOS; no BOS target',
        'folds': FOLDS, 'fold_seed': SEED, 'root_pseudocount': ALPHA,
        'context_prior_strength': STRENGTH,
        'primary_treatment': ['ZL3b', 'split', 'ascii_letters'],
        'second_order_criterion': {'minimum_pooled_gain_bits_per_target': MIN_GAIN,
                                 'group_macro_gain_positive': True, 'positive_folds_required': FOLDS},
    }
    require(set(plan) == set(fixed) | {'input_pins'}, 'plan field scope changed')
    # Canonical serialization distinguishes booleans, ints and decimal choices.
    for key, value in fixed.items():
        require(compact(plan[key]) == compact(value), 'review changed plan before versioning: ' + key)
    require(set(plan['input_pins']) == PIN_PATHS, 'input pin scope changed')
    for path, expected in plan['input_pins'].items():
        require(hashlib.sha256((root / path).read_bytes()).hexdigest() == expected,
                'pinned input changed: ' + path)
    return plan


def alphabet_for(patterns):
    parent.ordered_patterns(patterns)
    return tuple(sorted(set(string.ascii_letters) | set(patterns) | {EOS}))


def events(units):
    require(isinstance(units, list) and units and all(
        isinstance(u, str) and u and u not in (BOS, EOS) for u in units),
        'nonempty emitted-unit list without reserved labels required')
    w = x = BOS
    for target in units + [EOS]:
        yield w, x, target
        w, x = x, target


def fit(rows, alphabet):
    require(rows and len(alphabet) == len(set(alphabet)) and EOS in alphabet and BOS not in alphabet,
            'nonempty training rows and unique target alphabet required')
    targets, first, second = Counter(), defaultdict(Counter), defaultdict(Counter)
    for row in rows:
        require(row['segments'], 'nonempty token population required')
        for units in row['segments']:
            for w, x, y in events(units):
                require(y in alphabet, 'emitted unit outside fixed alphabet')
                targets[y] += 1
                first[x][y] += 1
                second[w, x][y] += 1
    return {'alphabet': alphabet, 'targets': targets, 'first': dict(first), 'second': dict(second),
            'total': sum(targets.values()),
            'first_totals': {x: sum(c.values()) for x, c in first.items()},
            'second_totals': {c: sum(v.values()) for c, v in second.items()}}


def probabilities(model, w, x, y):
    require(y in model['alphabet'], 'target outside fixed alphabet')
    q0 = (model['targets'][y] + ALPHA) / (model['total'] + ALPHA * len(model['alphabet']))
    q1 = (model['first'].get(x, {}).get(y, 0) + STRENGTH * q0) / (
        model['first_totals'].get(x, 0) + STRENGTH)
    q2 = (model['second'].get((w, x), {}).get(y, 0) + STRENGTH * q1) / (
        model['second_totals'].get((w, x), 0) + STRENGTH)
    return q0, q1, q2


def model_record(model):
    return {
        'alphabet': list(model['alphabet']),
        'target_counts': [[y, n] for y, n in sorted(model['targets'].items())],
        'first_counts': [[x, y, n] for x, counts in sorted(model['first'].items())
                         for y, n in sorted(counts.items())],
        'second_counts': [[w, x, y, n] for (w, x), counts in sorted(model['second'].items())
                          for y, n in sorted(counts.items())],
    }


def score_row(row, model, fold, cache):
    losses = [[], [], []]
    unseen1 = unseen2 = 0
    for units in row['segments']:
        for w, x, y in events(units):
            key = w, x, y
            if key not in cache:
                cache[key] = tuple(-math.log2(q) for q in probabilities(model, w, x, y))
            for values, loss in zip(losses, cache[key]):
                values.append(loss)
            unseen1 += x not in model['first']
            unseen2 += (w, x) not in model['second']
    totals = [math.fsum(v) for v in losses]
    count = len(losses[0])
    require(count == sum(len(u) + 1 for u in row['segments']) and count > 0, 'target accounting changed')
    return {'locus_key': row['key'], 'page_id': row['page'], 'group_id': row['group'], 'fold': fold,
            'tokens': len(row['segments']), 'units': count - len(row['segments']), 'targets': count,
            'loss_bits_order0_order1_order2': totals,
            'gain01_bits_per_target': (totals[0] - totals[1]) / count,
            'gain12_bits_per_target': (totals[1] - totals[2]) / count,
            'unseen_order1_context_targets': unseen1, 'unseen_order2_context_targets': unseen2}


def aggregate(scores):
    require(scores, 'nonempty scoring rows required')
    count = sum(s['targets'] for s in scores)
    require(count > 0, 'nonzero target denominator required')
    losses = [math.fsum(s['loss_bits_order0_order1_order2'][j] for s in scores) for j in range(3)]
    result = {'loci': len(scores), 'tokens': sum(s['tokens'] for s in scores),
              'units': sum(s['units'] for s in scores), 'targets': count,
              'loss_bits_order0_order1_order2': losses}
    for name, lower, higher in [('01', 0, 1), ('12', 1, 2)]:
        result['pooled_gain' + name + '_bits_per_target'] = (losses[lower] - losses[higher]) / count
        result['locus_macro_gain' + name + '_bits_per_target'] = math.fsum(
            s['gain' + name + '_bits_per_target'] for s in scores) / len(scores)
    for order in (1, 2):
        field = f'unseen_order{order}_context_targets'
        result[field] = sum(s[field] for s in scores)
    return result


def second_order_preference(pooled_gain, group_gain, fold_gains):
    require(len(fold_gains) == FOLDS, 'five fold gains required')
    return pooled_gain >= MIN_GAIN and group_gain > 0 and all(gain > 0 for gain in fold_gains)


def evaluate(rows, assignments, alphabet):
    keys = [r['key'] for r in rows]
    require(rows and len(keys) == len(set(keys)), 'unique nonempty loci required')
    groups = {r['group'] for r in rows}
    require(set(assignments) == groups and set(assignments.values()) == set(range(FOLDS)) and
            all(type(f) is int for f in assignments.values()), 'all groups and five folds required')
    scored, folds = [], []
    for fold in range(FOLDS):
        train = [r for r in rows if assignments[r['group']] != fold]
        test = [r for r in rows if assignments[r['group']] == fold]
        train_groups, test_groups = {r['group'] for r in train}, {r['group'] for r in test}
        require(train and test and not train_groups & test_groups, 'empty fold or group leakage')
        model = fit(train, alphabet)
        cache = {}
        scores = [score_row(r, model, fold, cache) for r in test]
        scored.extend(scores)
        counts = model_record(model)
        folds.append({'fold': fold, 'training_loci': len(train), 'training_targets': model['total'],
                      'training_group_ids': sorted(train_groups), 'scoring_group_ids': sorted(test_groups),
                      'observed_order1_contexts': len(model['first']),
                      'observed_order2_contexts': len(model['second']),
                      'fitted_counts_sha256': digest(counts),
                      'training_target_counts': counts['target_counts'], **aggregate(scores)})
    require(Counter(s['locus_key'] for s in scored) == Counter(keys), 'locus scoring coverage changed')
    by_group = defaultdict(list)
    for score in scored:
        by_group[score['group_id']].append(score)
    group_results = [{'group_id': g, 'fold': assignments[g], **aggregate(v)}
                     for g, v in sorted(by_group.items())]
    summary = aggregate(scored)
    summary['groups'] = len(group_results)
    for name in ('01', '12'):
        summary['group_macro_gain' + name + '_bits_per_target'] = math.fsum(
            g['pooled_gain' + name + '_bits_per_target'] for g in group_results) / len(group_results)
    summary['positive_order2_fold_count'] = sum(f['pooled_gain12_bits_per_target'] > 0 for f in folds)
    summary['fixed_second_order_preference'] = second_order_preference(
        summary['pooled_gain12_bits_per_target'], summary['group_macro_gain12_bits_per_target'],
        [f['pooled_gain12_bits_per_target'] for f in folds])
    return {'summary': summary, 'folds': folds, 'groups': group_results,
            'loci': sorted(scored, key=lambda s: s['locus_key'])}


def fold_for(group):
    require(isinstance(group, str) and group, 'nonempty group identifier required')
    return int.from_bytes(hashlib.sha256(compact([METHOD, SEED, group])).digest(), 'big') % FOLDS


def declare_folds(rows, image, canvases):
    components = dependency_components(canvases)
    require(components == image['dependency_components'], 'full-index components differ from image receipt')
    leaves = {leaf: c['group_id'] for c in components for leaf in c['folio_ids']}
    members = {c['group_id']: c['folio_ids'] for c in components}
    by_side, by_leaf = defaultdict(set), defaultdict(set)
    for canvas in canvases:
        for side in filter(None, canvas['explicit_folio_sides'].split(';')):
            by_side[side].add(canvas['canvas_uri'])
            by_leaf[side[:-1]].add(canvas['canvas_uri'])
    require({k: sorted(v) for k, v in by_leaf.items()} == image['indexed_canvas_ids_by_leaf'],
            'full-index canvas membership differs from image receipt')
    pages = {p['page_id']: p for p in image['pages']}
    require(len(pages) == len(image['pages']), 'duplicate image page declarations')
    groups, page_groups, seen = defaultdict(list), {}, set()
    for row in rows:
        require(row['key'] not in seen, 'duplicate selected locus')
        seen.add(row['key'])
        page = row['page']
        sides = page_reference(page)['folio_sides']
        candidates = {leaves.get(s[:-1]) for s in sides}
        require(sides and all(by_side[s] for s in sides) and len(candidates) == 1 and
                None not in candidates, 'selected page has no complete supported component: ' + page)
        group = next(iter(candidates))
        require(page in pages and pages[page]['side_reference_status'] == 'side_references_matched' and
                pages[page]['dependency_group'] == group, 'selected page differs from image receipt')
        page_groups[page] = group
        groups[group].append(row)
    assignments = {g: fold_for(g) for g in sorted(groups)}
    require(set(assignments.values()) == set(range(FOLDS)), 'empty declared fold; do not replace seed')
    manifest = [{'group_id': g, 'fold': assignments[g], 'folio_ids': members[g],
                 'source_page_ids': sorted({r['page'] for r in selected}),
                 'locus_keys': sorted(r['key'] for r in selected),
                 'canvas_ids': sorted({uri for leaf in members[g] for uri in by_leaf[leaf]})}
                for g, selected in sorted(groups.items())]
    return assignments, manifest, page_groups


def make_report(root=ROOT):
    plan = load_plan(root)
    require((root / PARENT).read_bytes() == encoded(parent.make_report(root)),
            'complete paired entropy receipt differs from producer replay')
    parent_report = strict_json((root / PARENT).read_bytes())
    parent_plan, policies, _ = parent.load_plan(root)
    sources = parent.load_sources(root)
    maps, accepted, selection = parent.prepare(sources, parent_plan)
    require(selection == parent_report['selection'], 'parent cohort changed')
    initial = [{'key': k, 'page': maps['ZL3b', 'split'][k]['page_id']} for k in accepted]
    image = strict_json((root / IMAGE).read_bytes())
    canvases = list(csv.DictReader(io.StringIO((root / CANVASES).read_text(encoding='utf-8'))))
    assignments, manifest, page_groups = declare_folds(initial, image, canvases)
    treatments = []
    for sid in parent.SOURCE_IDS:
        for spacing in parent.SPACING:
            mapping = maps[sid, spacing]
            for policy in policies:
                patterns = parent.ordered_patterns(policy['patterns'])
                alphabet = alphabet_for(policy['patterns'])
                rows = []
                for key in accepted:
                    row = mapping[key]
                    pieces = [parent.segment(token, patterns) for token in row['tokens']]
                    require(all(''.join(u) == token for u, token in zip(pieces, row['tokens'])),
                            'segmentation fails exact rejoining')
                    rows.append({'key': key, 'page': row['page_id'], 'group': page_groups[row['page_id']],
                                 'segments': pieces})
                treatments.append({'source_id': sid, 'spacing': spacing, 'unit_policy': policy['id'],
                                   'target_alphabet': list(alphabet), 'segmented_rows_sha256': digest(rows),
                                   **evaluate(rows, assignments, alphabet)})
    # Recheck every declared artifact after scoring, before any output write.
    require(load_plan(root) == plan, 'pinned evidence changed during calculation')
    return {'schema_version': 1, 'method': METHOD, 'analysis_status': plan['analysis_status'],
            'plan_sha256': hashlib.sha256((root / PLAN).read_bytes()).hexdigest(),
            'plan_note_sha256': hashlib.sha256((root / NOTE).read_bytes()).hexdigest(),
            'implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'input_pins': plan['input_pins'], 'sources': parent_report['sources'],
            'selection': {'parent_selection_sha256': digest(selection),
                          **{k: selection[k] for k in ('shared_present_P0_loci', 'retained_loci',
                                                      'retained_locus_keys_sha256', 'excluded_loci',
                                                      'source_only_present_P0_keys')}},
            'primary_treatment': plan['primary_treatment'],
            'models': {k: plan[k] for k in ('boundary', 'alphabet', 'root_pseudocount',
                                           'context_prior_strength', 'second_order_criterion')},
            'folds': {'count': FOLDS, 'seed': SEED, 'group_assignments': manifest,
                      'manifest_sha256': digest(manifest)},
            'all_treatments_meet_second_order_criterion': all(
                t['summary']['fixed_second_order_preference'] for t in treatments),
            'treatments': treatments}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args()
    try:
        if args.output:
            require(not args.output.exists() and not args.output.is_symlink(), 'output must be a new file')
        report = make_report(ROOT)
        raw = encoded(report)
        if args.check:
            cached = args.check.read_bytes()
            strict_json(cached)
            require(cached == raw, 'report differs from complete pinned replay')
        else:
            with args.output.open('xb') as output:
                output.write(raw)
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'grouped symbol prediction failed: {error}\n')
    print('Complete grouped symbol report checked.' if args.check else 'New grouped symbol report created.')


if __name__ == '__main__':
    main()
