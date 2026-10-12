"""Count distinct maximum index pairings without interpreting source correctness."""

import argparse
from collections import Counter
from fractions import Fraction
from pathlib import Path
import zipfile

try:
    from .audit_historical_record_order import (
        IMPLEMENTATIONS as ORDER_IMPLEMENTATIONS, READS as ORDER_READS,
        build as parent_build, load_inputs, projection_records, digest)
    from .audit_eva_token_coverage import encoded, load_json
    from .paragraph_token_corpus import protect_outputs
except ImportError:
    from audit_historical_record_order import (
        IMPLEMENTATIONS as ORDER_IMPLEMENTATIONS, READS as ORDER_READS,
        build as parent_build, load_inputs, projection_records, digest)
    from audit_eva_token_coverage import encoded, load_json
    from paragraph_token_corpus import protect_outputs

ROOT = Path(__file__).resolve().parents[1]
PARENT = Path('research/historical/record-order.json')
PARENT_SHA256 = '0f053fd9a3bdeb2e92ae95da9d9c352cdf908b3a8be4aaec75b52c9a99211365'
PLAN = Path('research/historical/PAIRING_COUNTS_PLAN.md')
REPORT = Path('research/historical/pairing-counts.json')
READS = (PARENT, PLAN, REPORT, *ORDER_READS)
IMPLEMENTATIONS = (*ORDER_IMPLEMENTATIONS, 'audit_historical_pairing_counts.py')


def count_pairings(left, right):
    """Count longest paths through equal index pairs, with no skip-path counting."""
    if any(type(s) is not str or not s for s in (*left, *right)):
        raise ValueError('sequence elements must be nonempty exact strings')
    nodes = [(i, j) for i, a in enumerate(left) for j, b in enumerate(right) if a == b]
    forward, fw = [0]*len(nodes), [0]*len(nodes)
    backward, bw = [0]*len(nodes), [0]*len(nodes)
    for u, (i, j) in enumerate(nodes):
        best, ways = 0, 1
        for k, (x, y) in enumerate(nodes[:u]):
            if x < i and y < j:
                if forward[k] > best:
                    best, ways = forward[k], fw[k]
                elif forward[k] == best:
                    ways += fw[k]
        forward[u], fw[u] = best+1, ways
    for u in range(len(nodes)-1, -1, -1):
        i, j = nodes[u]; best, ways = 0, 1
        for k in range(u+1, len(nodes)):
            x, y = nodes[k]
            if x > i and y > j:
                if backward[k] > best:
                    best, ways = backward[k], bw[k]
                elif backward[k] == best:
                    ways += bw[k]
        backward[u], bw[u] = best+1, ways
    length = max(forward, default=0)
    total = sum(fw[u] for u in range(len(nodes)) if forward[u] == length) if length else 1
    pairs = []
    sums = [0]*length
    for u, (i, j) in enumerate(nodes):
        if forward[u]+backward[u]-1 != length:
            continue
        through = fw[u]*bw[u]; rank = forward[u]
        sums[rank-1] += through
        pairs.append({'historical_nonempty_index':i, 'modern_nonempty_index':j,
                      'matched_rank_one_based':rank,
                      'mandatory_in_every_maximum_pairing':through == total,
                      'maximum_pairings_through_pair':through})
    if any(value != total for value in sums):
        raise ValueError('maximum-pairing rank counts do not sum to the total')
    return {'maximum_order_preserving_pairs':length, 'maximum_pairing_count':total,
            'candidate_pairs':pairs, 'rank_pairing_count_sums':sums}


def ratio(value):
    return {'numerator':str(value.numerator), 'denominator':str(value.denominator)}


def inventory(old, new, parent):
    detailed, controls = [], []
    for p in (*parent['order_different_pages'], *parent['equal_order_controls']):
        page = p['page_id']
        a = [s for s,d in old[page] if s]; b = [s for s,d in new[page] if s]
        if Counter(a) != Counter(b) or not a or len(a) != p['nonempty_records_per_source']:
            raise ValueError('page differs from the accepted complete cohort')
        result = count_pairings(a,b); total = result['maximum_pairing_count']
        if result['maximum_order_preserving_pairs'] != p['maximum_order_preserving_pairs']:
            raise ValueError('maximum length differs from parent')
        common = {k:p[k] for k in ('page_id','nonempty_records_per_source',
                  'historical_empty_projection_records','modern_empty_projection_records')}
        if a == b:
            expected = [(i,i) for i in range(len(a))]
            actual = [(c['historical_nonempty_index'],c['modern_nonempty_index']) for c in result['candidate_pairs']]
            if total != 1 or actual != expected:
                raise ValueError('identity control differs from a unique complete pairing')
            controls.append({**common, 'maximum_order_preserving_pairs':len(a),
                             'maximum_pairing_count':'1', 'only_identity_index_pairs':True})
            continue
        base_pairs = [{k:v for k,v in c.items() if k != 'maximum_pairings_through_pair'}
                      for c in result['candidate_pairs']]
        if encoded(base_pairs) != encoded(p['candidate_pairs']) or (total == 1) is not p['maximum_pairing_unique']:
            raise ValueError('pair support/rank/mandatory/unique fields differ from parent')
        candidates = []
        fractions = []
        for candidate in result['candidate_pairs']:
            through = candidate['maximum_pairings_through_pair']
            share = Fraction(through,total)
            if not candidate['mandatory_in_every_maximum_pairing']:
                fractions.append(share)
            candidates.append({**candidate, 'maximum_pairings_through_pair':str(through),
                               'support_fraction':ratio(share)})
        detailed.append({**common, 'maximum_order_preserving_pairs':result['maximum_order_preserving_pairs'],
                         'minimum_unmatched_records_per_source':p['minimum_unmatched_historical_records'],
                         'maximum_pairing_count':str(total), 'maximum_pairing_unique':total == 1,
                         'descriptor_reference':'same page and nonempty indices in pinned parent descriptor lists',
                         'candidate_pairs':candidates,
                         'rank_pairing_count_sums':[str(v) for v in result['rank_pairing_count_sums']],
                         'nonmandatory_support_fraction_range':{'minimum':ratio(min(fractions)),
                             'maximum':ratio(max(fractions))} if fractions else None})
    if [p['page_id'] for p in detailed] != [p['page_id'] for p in parent['order_different_pages']]:
        raise ValueError('complete differing-order cohort changed')
    if [p['page_id'] for p in controls] != [p['page_id'] for p in parent['equal_order_controls']]:
        raise ValueError('complete identity-control cohort changed')
    counts = Counter(int(p['maximum_pairing_count']) for p in detailed)
    all_counts = counts + Counter({1:len(controls)})
    histogram = lambda c:[{'maximum_pairing_count':str(k),'page_count':v} for k,v in sorted(c.items())]
    return {'summary':{'selected_equal_multiset_pages':len(detailed)+len(controls),
                'order_different_pages':len(detailed),'equal_order_control_pages':len(controls),
                'excluded_union_pages':len(parent['excluded_pages']),
                'unique_maximum_pairing_pages':all_counts[1],
                'ambiguous_maximum_pairing_pages':sum(v for k,v in all_counts.items() if k>1),
                'order_different_count_histogram':histogram(counts),
                'selected_count_histogram':histogram(all_counts)},
            'order_different_pages':detailed, 'equal_order_controls':controls,
            'excluded_pages':parent['excluded_pages']}


def build(root=ROOT, loaded=None):
    loaded = loaded or load_inputs(root)
    raw = (root/PARENT).read_bytes()
    if digest(raw) != PARENT_SHA256:
        raise ValueError('accepted record-order parent bytes changed')
    parent = load_json(raw)
    if encoded(parent) != encoded(parent_build(root,loaded)):
        raise ValueError('accepted parent differs from complete source reconstruction')
    old = projection_records(loaded[0],True); new = projection_records(loaded[1].loci,False)
    return {'schema_version':1,'method':'exposed-maximum-index-pairing-counts-v1',
            'usable_as_verified_locus_crosswalk':False,'usable_for_statistical_evaluation':False,
            'inputs':{'sources':loaded[2], 'parent_report':{'path':str(PARENT),'sha256':digest(raw)},
                      'plan':{'path':str(PLAN),'sha256':digest((root/PLAN).read_bytes())},
                      'implementation_sha256':{'scripts/'+p:digest((root/'scripts'/p).read_bytes()) for p in IMPLEMENTATIONS}},
            'rules':{'unit':'distinct maximum ordered sequences of equal projected-string index pairs',
                     'weighting':'each distinct maximum index pairing counted once; not physical-row probability',
                     'support':'exact through-pair count divided by total; no selected witness',
                     'integer_serialization':'path counts and fraction components are exact decimal strings',
                     'empty_optimum':'one empty index pairing when maximum length is zero',
                     'duplicates':'different index sequences remain observationally indistinguishable',
                     'pages':'complete parent cohort; counts never pooled into a joint physical distribution'},
            'modern_nonexistent_loci_excluded':parent['modern_nonexistent_loci_excluded'],
            **inventory(old,new,parent)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path); parser.add_argument('--check',type=Path)
    args = parser.parse_args()
    try:
        loaded = load_inputs(ROOT)
        reads = [*loaded[3],*(ROOT/p for p in READS),*([args.check] if args.check else [])]
        outputs = [args.output] if args.output else []
        protect_outputs(outputs,reads,root=ROOT)
        if args.output and (args.output.exists() or args.output.is_symlink()):
            raise ValueError('output exists; choose a fresh record')
        result = build(ROOT,loaded)
        if args.check and encoded(load_json(args.check.read_bytes())) != encoded(result):
            raise ValueError('pairing-count report differs from complete typed replay')
        if args.output:
            raw = encoded(result)
            protect_outputs(outputs,reads,root=ROOT)
            if args.output.exists() or args.output.is_symlink():
                raise ValueError('output exists; choose a fresh record')
            with args.output.open('xb') as stream:
                stream.write(raw)
        elif not args.check:
            print(encoded(result).decode(),end='')
    except (ValueError,KeyError,OSError,UnicodeError,zipfile.BadZipFile) as error:
        parser.exit(1,f'pairing-count audit failed: {error}\n')
    if args.check or args.output:
        print(f"Verified {result['summary']['selected_equal_multiset_pages']} pages; index-pairing counts are not manuscript probabilities.")


if __name__ == '__main__':
    main()
