"""Independent native cohort, union-find groups, tables and exact-slot scores."""
import argparse
from collections import Counter, defaultdict
import csv
from fractions import Fraction
import gzip
import hashlib
import json
import math
from pathlib import Path
import platform

try:
    from .eva_token_adapter import build
except ImportError:
    from eva_token_adapter import build

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'research/baselines/exact-slot-length-pins.json'
MANIFEST_SHA = '3c31d97b437e3f0b37be9dbc2ca19d8189945e72c71618eb1bb997574940305f'
PRODUCER_SHA = 'f299d79d49555b312651658e71289b77c97f5e2aac9067fa6594bfd1a9e2632f'
VARIANTS = [(s, p) for s in ('ZL3b', 'IT2a') for p in ('split', 'join')]
MODELS = ['Q0', 'Q1', 'F0', 'F1']
CONTRASTS = {'previous_at_exact_slot': ('F1', 'F0'), 'position_refinement': ('F0', 'Q0'),
             'combined_model_difference': ('F1', 'Q1')}


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()


def compare(expected, saved):
    if json.dumps(expected, sort_keys=True, allow_nan=False) != json.dumps(saved, sort_keys=True, allow_nan=False):
        raise ValueError('complete typed independent exact-slot reconstruction differs')


def cohort(mappings):
    common = set.intersection(*(set(records) for records in mappings.values()))
    common = {k for k in common if all(r[k]['locus_type'] == 'P0' and
              'nonexistent_locus' not in r[k]['exclusion_reasons'] for r in mappings.values())}
    keys, exclusions, reason_counts = [], [], Counter()
    after_adapter = after_drawing = 0
    for key in sorted(common):
        valid = all(r[key]['eligible'] for r in mappings.values())
        after_adapter += valid
        after_drawing += valid and all(r[key]['drawing_interruption_count'] == 0 for r in mappings.values())
        reasons = set()
        for (sid, spacing), records in mappings.items():
            r = records[key]
            reasons.update(sid + '/' + spacing + ':' + reason for reason in r['exclusion_reasons'])
            if valid:
                if r['drawing_interruption_count']:
                    reasons.add(sid + '/' + spacing + ':drawing_interruption')
                if r['token_count'] < 5:
                    reasons.add(sid + '/' + spacing + ':fewer_than_five_tokens')
        if reasons:
            exclusions.append({'locus_key': key, 'reasons': sorted(reasons)})
            reason_counts.update(reasons)
        else:
            keys.append(key)
    return {'shared_present_P0_loci': len(common), 'eligible_in_all_adapters': after_adapter,
            'eligible_after_drawing_exclusion': after_drawing, 'eligible_after_minimum_token_exclusion': len(keys),
            'excluded_loci': len(exclusions), 'reason_counts_may_overlap': dict(sorted(reason_counts.items())),
            'exclusions': exclusions, 'retained_locus_keys': keys,
            'retained_locus_keys_sha256': hashlib.sha256(compact(keys)).hexdigest()}


def union_groups(canvases):
    parents, images = {}, defaultdict(set)
    def find(x):
        while parents[x] != x:
            x = parents[x]
        return x
    for row in canvases:
        leaves = sorted({s[:-1] for s in row['explicit_folio_sides'].split(';') if s}, key=int)
        for leaf in leaves:
            parents.setdefault(leaf, leaf)
            images[leaf].add(row['canvas_uri'])
        for leaf in leaves[1:]:
            parents[find(leaf)] = find(leaves[0])
    components = defaultdict(list)
    for leaf in parents:
        components[find(leaf)].append(leaf)
    records = [{'group_id': 'yale-leaves:' + '+'.join(sorted(v, key=int)), 'folio_ids': sorted(v, key=int)}
               for v in components.values()]
    records.sort(key=lambda r: int(r['folio_ids'][0]))
    return records, {k: sorted(v) for k, v in images.items()}


def grouped_rows(mappings, selection, image, canvases):
    components, indexed = union_groups(canvases)
    compare(components, image['dependency_components'])
    compare(indexed, image['indexed_canvas_ids_by_leaf'])
    leaves = {leaf: r['group_id'] for r in components for leaf in r['folio_ids']}
    pages = {}
    for page in image['pages']:
        if page['side_reference_status'] == 'side_references_matched':
            choices = {leaves[s[:-1]] for s in page['reference']['folio_sides']}
            assert choices == {page['dependency_group']}
            pages[page['page_id']] = page['dependency_group']
    rows = {}
    for identity, records in mappings.items():
        rows[identity] = []
        for key in selection['retained_locus_keys']:
            r = records[key]
            assert r['page_id'] in pages
            values = [len(t) for t in r['tokens'][1:-1]]
            rows[identity].append({'key': key, 'page': r['page_id'], 'label': r['variables'].get('L', 'unset'),
                                   'values': values, 'group': pages[r['page_id']]})
    chosen = defaultdict(list)
    for row in rows[VARIANTS[0]]:
        chosen[row['group']].append(row)
    members = {r['group_id']: r['folio_ids'] for r in components}
    manifest, assignments = [], {}
    for group, selected in sorted(chosen.items()):
        fold = int.from_bytes(hashlib.sha256(compact(['grouped-length-prediction-v1', 20261012, group])).digest(), 'big') % 5
        assignments[group] = fold
        manifest.append({'group_id': group, 'fold': fold, 'folio_ids': members[group],
                         'source_page_ids': sorted({r['page'] for r in selected}),
                         'locus_keys': sorted(r['key'] for r in selected),
                         'canvas_ids': sorted({uri for leaf in members[group] for uri in indexed[leaf]})})
    assert set(assignments.values()) == set(range(5))
    return rows, assignments, manifest


def train_tables(rows):
    coarse = defaultdict(lambda: [0] * 10)
    coarse_pairs = defaultdict(lambda: [[0] * 10 for _ in range(10)])
    fine = defaultdict(lambda: [0] * 10)
    fine_pairs = defaultdict(lambda: [[0] * 10 for _ in range(10)])
    for row in rows:
        values = [min(v, 10) for v in row['values']]
        for j in range(1, len(values)):
            c = row['label'], int(j >= (len(values) + 1) // 2)
            f = row['label'], len(values), j
            x, y = values[j-1] - 1, values[j] - 1
            coarse[c][y] += 1
            coarse_pairs[c][x][y] += 1
            fine[f][y] += 1
            fine_pairs[f][x][y] += 1
    return coarse, coarse_pairs, fine, fine_pairs


def probabilities(tables, f, x, y):
    coarse, coarse_pairs, fine, fine_pairs = tables
    c = f[0], int(f[2] >= (f[1] + 1) // 2)
    ct = coarse.get(c, [0] * 10)
    cp = coarse_pairs.get(c, [[0] * 10 for _ in range(10)])[x-1]
    ft = fine.get(f, [0] * 10)
    fp = fine_pairs.get(f, [[0] * 10 for _ in range(10)])[x-1]
    nc, n, nx = sum(ct), sum(ft), sum(fp)
    q0 = (ct[y-1] + 1) / (nc + 10)
    q1 = (cp[y-1] + 10 * q0) / (sum(cp) + 10)
    prior = Fraction(ct[y-1] + 1, nc + 10)
    weight = Fraction(n, n + 10)
    f0 = weight * Fraction(ft[y-1], n) + (1 - weight) * prior if n else prior
    f1 = weight * Fraction(fp[y-1], nx) + (1 - weight) * prior if nx else f0
    constant = sum(any(v for v in row) for row in fine_pairs.get(f, [])) == 1
    return (q0, q1, f0, f1), (nc, n, nx, constant)


def row_score(row, tables, fold):
    losses = {name: [] for name in MODELS}
    receipts = []
    for j in range(1, len(row['values'])):
        f = row['label'], len(row['values']), j
        x, y = min(row['values'][j-1], 10), min(row['values'][j], 10)
        probs, (nc, n, nx, constant) = probabilities(tables, f, x, y)
        for name, p in zip(MODELS, probs):
            losses[name].append(-math.log2(float(p)))
        a, b = probs[2:]
        assert not constant or a == b
        receipts.append({'target_slot': j, 'previous_class': x, 'target_class': y,
                         'fine_training_transitions': n, 'previous_training_transitions': nx,
                         'coarse_training_transitions': nc, 'constant_previous_context': constant,
                         'F0': [str(a.numerator), str(a.denominator)], 'F1': [str(b.numerator), str(b.denominator)]})
    return {'locus_key': row['key'], 'page_id': row['page'], 'group_id': row['group'], 'source_label': row['label'],
            'fold': fold, 'interior_size': len(row['values']), 'transitions': len(receipts),
            'loss_bits': {name: math.fsum(v) for name, v in losses.items()}, 'transition_receipts': receipts}


def totals(rows):
    count = sum(r['transitions'] for r in rows)
    loss = {name: math.fsum(r['loss_bits'][name] for r in rows) for name in MODELS}
    support = Counter({name: 0 for name in ('unseen_coarse_context', 'unseen_fine_context',
                                           'seen_fine_unseen_previous', 'constant_previous_context')})
    for row in rows:
        for t in row['transition_receipts']:
            support['unseen_coarse_context'] += t['coarse_training_transitions'] == 0
            support['unseen_fine_context'] += t['fine_training_transitions'] == 0
            support['seen_fine_unseen_previous'] += t['fine_training_transitions'] > 0 and t['previous_training_transitions'] == 0
            support['constant_previous_context'] += t['constant_previous_context']
    contrasts = {}
    for tag, (a, b) in CONTRASTS.items():
        contrasts[tag] = {'gain_bits': loss[b] - loss[a], 'micro_gain_bits_per_transition': (loss[b] - loss[a]) / count,
                          'locus_macro_gain_bits_per_transition': math.fsum(
                              (r['loss_bits'][b] - r['loss_bits'][a]) / r['transitions'] for r in rows) / len(rows)}
    return {'loci': len(rows), 'transitions': count, 'loss_bits': loss, 'contrasts': contrasts, 'support': dict(support)}


def evaluate(rows, assignments, old):
    folds, all_scores = [], []
    old_loci = {r['locus_key']: r for r in old['loci']}
    for fold in range(5):
        train = [r for r in rows if assignments[r['group']] != fold]
        test = [r for r in rows if assignments[r['group']] == fold]
        assert train and test and not ({r['group'] for r in train} & {r['group'] for r in test})
        tables = train_tables(train)
        ct, cp, ft, fp = tables
        coarse_profiles = [{'source_label': c[0], 'target_half': c[1], 'target_counts': ct[c],
                            'previous_target_counts': cp[c]} for c in sorted(ct)]
        compare(coarse_profiles, old['folds'][fold]['fitted_counts'])
        fine_profiles = [{'source_label': f[0], 'interior_size': f[1], 'target_slot': f[2],
                          'target_counts': ft[f], 'previous_target_counts': fp[f]} for f in sorted(ft)]
        for f in ft:
            n = sum(ft[f])
            previous = [sum(v) for v in fp[f]]
            for y in range(1, 11):
                baseline = probabilities(tables, f, 1, y)[0][2]
                mixture = sum((Fraction(nx, n) * probabilities(tables, f, x+1, y)[0][3]
                               for x, nx in enumerate(previous) if nx), Fraction())
                assert mixture == baseline
        scores = [row_score(r, tables, fold) for r in test]
        for score in scores:
            prior = old_loci[score['locus_key']]
            assert score['loss_bits']['Q0'] == prior['baseline_loss_bits']
            assert score['loss_bits']['Q1'] == prior['transition_loss_bits']
        all_scores.extend(scores)
        folds.append({'fold': fold, 'training_loci': len(train), 'training_transitions': sum(len(r['values'])-1 for r in train),
                      'training_group_ids': sorted({r['group'] for r in train}), 'scoring_group_ids': sorted({r['group'] for r in test}),
                      'coarse_fitted_counts_sha256': hashlib.sha256(compact(coarse_profiles)).hexdigest(),
                      'fine_fitted_counts_sha256': hashlib.sha256(compact(fine_profiles)).hexdigest(),
                      'fine_fitted_counts': fine_profiles, **totals(scores)})
    by_group = defaultdict(list)
    for score in all_scores:
        by_group[score['group_id']].append(score)
    groups = [{'group_id': g, 'fold': assignments[g], **totals(r)} for g, r in sorted(by_group.items())]
    summary = totals(all_scores)
    summary['groups'] = len(groups)
    for tag, record in summary['contrasts'].items():
        record['group_macro_gain_bits_per_transition'] = math.fsum(g['contrasts'][tag]['micro_gain_bits_per_transition'] for g in groups) / len(groups)
        record['positive_fold_count'] = sum(f['contrasts'][tag]['micro_gain_bits_per_transition'] > 0 for f in folds)
        record['positive_group_count'] = sum(g['contrasts'][tag]['micro_gain_bits_per_transition'] > 0 for g in groups)
        record['fixed_diagnostic_preference'] = (record['micro_gain_bits_per_transition'] > 0 and
            record['group_macro_gain_bits_per_transition'] > 0 and record['positive_fold_count'] >= 4) if tag == 'previous_at_exact_slot' else None
    return {'summary': summary, 'folds': folds, 'groups': groups, 'loci': sorted(all_scores, key=lambda r: r['locus_key'])}


def verify(path, progress=None):
    if not __debug__:
        raise ValueError('independent verification requires assertions')
    raw = (ROOT / MANIFEST).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == MANIFEST_SHA
    pins = json.loads(raw)
    for name, sha in pins.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == sha
    assert hashlib.sha256((ROOT/'scripts/exact_slot_length_prediction.py').read_bytes()).hexdigest() == PRODUCER_SHA
    old = json.loads((ROOT/'research/baselines/grouped-length-prediction.json').read_text())
    mappings = {identity: {r['locus_key']: r for r in build(identity[1], source_ids=(identity[0],), kinds=('P0',))['records']}
                for identity in VARIANTS}
    selection = cohort(mappings)
    compare(selection, json.loads((ROOT/'research/transliteration/interior_length_order.json').read_text())['selection'])
    image = json.loads((ROOT/'research/folio-alignment/transcription-image-coverage.json').read_text())
    with (ROOT/'research/image-index/canvases.csv').open() as source:
        canvases = list(csv.DictReader(source))
    rows, assignments, manifest = grouped_rows(mappings, selection, image, canvases)
    compare(manifest, old['folds']['group_assignments'])
    results = []
    for identity, previous in zip(VARIANTS, old['treatments']):
        vector = [(r['page'], r['key'], r['values']) for r in rows[identity]]
        digest = hashlib.sha256(compact(vector)).hexdigest()
        assert digest == previous['length_corpus_sha256']
        results.append({'source_id': identity[0], 'spacing': identity[1], 'source_sha256': previous['source_sha256'],
                        'length_corpus_sha256': digest, **evaluate(rows[identity], assignments, previous)})
        if progress:
            progress(identity[0]+'/'+identity[1]+': independent native counts, folds and all exact-slot records verified')
    expected = {'schema_version': 1, 'method': 'grouped-exact-slot-matched-weight-length-prediction-v1',
                'status': 'previously exposed corpus; dependency-group parameter-fit exclusion only',
                'python_version': platform.python_version(), 'input_pins': pins, 'pin_manifest_sha256': MANIFEST_SHA,
                'implementation_sha256': PRODUCER_SHA, 'selection': old['selection'], 'folds': old['folds'],
                'models': MODELS, 'contrasts': {k: list(v) for k, v in CONTRASTS.items()}, 'fixed_prior_strength': 10,
                'previous_training_frequency_mixture_equals_F0': True,
                'all_treatments_meet_primary_preference': all(t['summary']['contrasts']['previous_at_exact_slot']['fixed_diagnostic_preference'] for t in results),
                'original_coarse_report_reproduced_completely': True, 'treatments': results}
    payload = path.read_bytes()
    compare(expected, json.loads(gzip.decompress(payload) if path.suffix == '.gz' else payload))
    transitions = sum(t['summary']['transitions'] for t in results)
    return {'loci': len(selection['retained_locus_keys']), 'exclusions': len(selection['exclusions']),
            'groups': len(assignments), 'exact_transition_probabilities': 2*transitions,
            'transition_support_records': transitions, 'scored_locus_model_losses': 4*sum(t['summary']['loci'] for t in results),
            'fine_fitted_contexts': sum(len(f['fine_fitted_counts']) for t in results for f in t['folds'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=ROOT/'research/baselines/exact-slot-length-prediction.json.gz')
    args = parser.parse_args()
    try:
        result = verify(args.report, progress=lambda m: print(m, flush=True))
    except (AssertionError, ValueError, OSError, EOFError, KeyError, TypeError) as error:
        parser.exit(1, f'Independent exact-slot verification failed: {error}\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
