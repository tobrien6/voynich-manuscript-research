"""Exact regular language for one declared concatenation/greedy reversal model."""

import argparse
from collections import Counter, deque
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
PLAN = 'research/transliteration/currier-roundtrip-plan.json'
CATALOG = 'research/transliteration/currier-conversion-source.json'
PLAN_SHA256 = 'f0a1c410f9205b3305586fdc32b6e9ff635fbd700275be5719c6e3ee18d357e2'
REJECT = 'reject'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(',', ':'), allow_nan=False)


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result

    def invalid(value):
        raise ValueError('nonfinite JSON number: ' + value)

    return json.loads(path.read_text(), object_pairs_hook=pairs, parse_constant=invalid)


def validate_rules(rules):
    if (not rules or any(type(k) is not int or k <= 0 or not isinstance(v, str) or not v
                         for k, v in rules.items()) or len(set(rules.values())) != len(rules)):
        raise ValueError('rule identities and nonempty right strings must be unique')


def advance(pending, incoming, rules):
    """Delay a possible longer match; irrevocably reject unequal emitted identities."""
    queue = pending + (incoming,)
    buffer = ''.join(rules[k] for k in queue)
    while buffer:
        if any(word.startswith(buffer) and len(word) > len(buffer) for word in rules.values()):
            if len(queue) >= max(map(len, rules.values())):
                raise ValueError('finite pending-queue bound violated')
            return queue
        matches = [k for k, word in rules.items() if buffer.startswith(word)]
        match = max(matches, key=lambda k: len(rules[k]), default=None)
        if match is None or match != queue[0]:
            return None
        buffer = buffer[len(rules[match]):]
        queue = queue[1:]
    return ()


def eof_accepts(pending, rules):
    buffer = ''.join(rules[k] for k in pending)
    for expected in pending:
        matches = [k for k, word in rules.items() if buffer.startswith(word)]
        match = max(matches, key=lambda k: len(rules[k]), default=None)
        if match != expected:
            return False
        buffer = buffer[len(rules[match]):]
    return not buffer


def graph(rules):
    validate_rules(rules)
    alphabet = sorted(rules)
    queues, numbers, paths, todo = [()], {(): 0}, {(): ()}, deque([()])
    edges, reject_path = {}, None
    while todo:
        pending = todo.popleft()
        targets = []
        for incoming in alphabet:
            target = advance(pending, incoming, rules)
            if target is None and reject_path is None:
                reject_path = paths[pending] + (incoming,)
            if target is not None and target not in numbers:
                numbers[target] = len(queues)
                queues.append(target)
                paths[target] = paths[pending] + (incoming,)
                todo.append(target)
            targets.append(REJECT if target is None else numbers[target])
        edges[numbers[pending]] = targets
    states = [{'id': numbers[q], 'pending_rule_lines': list(q),
               'pending_encoded_length': sum(len(rules[k]) for k in q),
               'state_sha256': sha(canonical(q).encode()),
               'shortest_reaching_rule_lines': list(paths[q]),
               'eof_accepts': eof_accepts(q, rules),
               'transitions': [{'input_rule_line': k, 'target': t}
                               for k, t in zip(alphabet, edges[numbers[q]], strict=True)]}
              for q in queues]
    states.append({'id': REJECT, 'pending_rule_lines': None, 'pending_encoded_length': None,
                   'state_sha256': sha(REJECT.encode()),
                   'shortest_reaching_rule_lines': list(reject_path) if reject_path is not None else None,
                   'eof_accepts': False,
                   'transitions': [{'input_rule_line': k, 'target': REJECT} for k in alphabet]})
    return {'alphabet_rule_lines': alphabet, 'initial_state': 0, 'states': states,
            'maximum_reachable_pending_codes': max(map(len, queues)),
            'maximum_reachable_pending_encoded_length': max(s['pending_encoded_length'] for s in states[:-1])}


def decisions(machine, sequence):
    by_id = {s['id']: s for s in machine['states']}
    state = 0
    columns = {k: i for i, k in enumerate(machine['alphabet_rule_lines'])}
    for incoming in sequence:
        state = by_id[state]['transitions'][columns[incoming]]['target']
    return by_id[state]['eof_accepts']


def counts(machine, lengths):
    by_id = {s['id']: s for s in machine['states']}
    mass, result = Counter({0: 1}), []
    for n in range(max(lengths) + 1):
        accepted = sum(v for s, v in mass.items() if by_id[s]['eof_accepts'])
        total = len(machine['alphabet_rule_lines']) ** n
        if sum(mass.values()) != total:
            raise ValueError('count mass is not conserved')
        if n in lengths:
            fraction = Fraction(accepted, total)
            result.append({'source_codes': n, 'total': total, 'accepted': accepted,
                           'rejected': total - accepted,
                           'accepted_fraction': {'numerator': fraction.numerator, 'denominator': fraction.denominator},
                           'state_counts': [{'state': s['id'], 'count': mass[s['id']]} for s in machine['states']]})
        if n == max(lengths):
            break
        next_mass = Counter()
        for state, amount in mass.items():
            for edge in by_id[state]['transitions']:
                next_mass[edge['target']] += amount
        mass = next_mass
    return result


def reference_decode(text, rules):
    """Separate whole-word reference: sorted definitions, no streaming state."""
    ordered = sorted(rules.items(), key=lambda item: (-len(item[1]), item[0]))
    output, unmatched, position = [], [], 0
    while position < len(text):
        for identity, word in ordered:
            if text.startswith(word, position):
                output.append(identity)
                position += len(word)
                break
        else:
            output.append(None)
            unmatched.append({'encoded_offset_0based': position,
                              'character_sha256': sha(text[position].encode())})
            position += 1
    return tuple(output), unmatched


def witness(sequence, rules):
    encoded = ''.join(rules[k] for k in sequence)
    returned, unmatched = reference_decode(encoded, rules)
    return {'input_rule_lines': list(sequence), 'returned_rule_lines': list(returned),
            'source_codes': len(sequence), 'encoded_codepoints': len(encoded),
            'encoded_sha256': sha(encoded.encode()), 'unmatched': unmatched,
            'exact_roundtrip': not unmatched and returned == tuple(sequence)}


def exhaustive(machine, rules, maximum):
    ledger_hash, rows, pair_failures = hashlib.sha256(), [], []
    for n in range(maximum + 1):
        accepted, total = 0, 0
        for sequence in itertools.product(sorted(rules), repeat=n):
            encoded = ''.join(rules[k] for k in sequence)
            returned, unmatched = reference_decode(encoded, rules)
            expected = not unmatched and returned == sequence
            observed = decisions(machine, sequence)
            if observed != expected:
                raise ValueError('whole-word reference and machine decision disagree')
            accepted += expected
            total += 1
            ledger_hash.update((canonical([sequence, expected, observed]) + '\n').encode())
            if n == 2 and not expected:
                pair_failures.append(list(sequence))
        rows.append({'source_codes': n, 'total': total, 'accepted': accepted, 'rejected': total - accepted})
    return {'all_decisions_agree': True, 'cases': sum(r['total'] for r in rows),
            'ordered_decision_ledger_sha256': ledger_hash.hexdigest(), 'by_length': rows,
            'all_two_code_failures': pair_failures}


def load_inputs(reference, root=ROOT):
    if sha((root / PLAN).read_bytes()) != PLAN_SHA256:
        raise ValueError('machine plan identity changed')
    plan = read_json(root / PLAN)
    for name, expected in plan['dependency_hashes'].items():
        if sha((root / name).read_bytes()) != expected:
            raise ValueError('frozen dependency changed: ' + name)
    if sha((root / plan['human_plan']).read_bytes()) != plan['human_plan_sha256']:
        raise ValueError('human plan changed')
    catalog = read_json(root / CATALOG)
    if canonical(plan['reference_artifacts']) != canonical(catalog['artifacts']):
        raise ValueError('artifact catalog changed')
    for entry in plan['reference_artifacts']:
        raw = (reference / entry['reference_name']).read_bytes()
        if len(raw) != entry['bytes'] or sha(raw) != entry['sha256']:
            raise ValueError('local primary artifact changed: ' + entry['reference_name'])
    raw = (reference / 'Curr-Eva_def.bit').read_bytes()
    if b'\r' in raw or not raw.endswith(b'\n'):
        raise ValueError('unexpected definition line endings')
    lines = raw.decode('ascii').splitlines()
    if len(lines) != 42 or sha(lines[0].encode()) != catalog['rule_structure']['header_sha256']:
        raise ValueError('definition envelope changed')
    rules, left, metadata = {}, {}, []
    for n in plan['source_rule_lines']:
        fields = lines[n - 1].split()
        if len(fields) != 2 or len(fields[0]) != 1:
            raise ValueError('unexpected rule row')
        a, b = fields
        rules[n], left[n] = b, a
        metadata.append({'physical_file_line': n, 'left_sha256': sha(a.encode()), 'right_sha256': sha(b.encode()),
                         'left_codepoints': len(a), 'right_codepoints': len(b),
                         'raw_line_sha256': sha(lines[n - 1].encode())})
    validate_rules(rules)
    if len(set(left.values())) != 38 or max(map(len, rules.values())) - 1 != plan['maximum_pending_codes']:
        raise ValueError('unexpected source alphabet or finite bound')
    if canonical(metadata) != canonical(catalog['all_rule_metadata']):
        raise ValueError('rule metadata mismatch')
    return plan, catalog, rules, left


def protected_files(reference, root=ROOT):
    return [root / PLAN, root / 'research/transliteration/CURRIER_ROUNDTRIP_PLAN.md',
            root / CATALOG, root / 'research/transliteration/CURRIER_CONVERSION_SOURCE.md',
            root / 'scripts/currier_roundtrip_language.py'] + [reference / n for n in
                ('Curr-Eva_def.bit', 'Bitrans_manual.pdf', '000_README.txt')]


def guard_output(output, protected):
    if output is not None and any(output.resolve() == p.resolve() or
                                 output.exists() and p.exists() and output.samefile(p) for p in protected):
        raise ValueError('output aliases a protected plan, dependency, producer or primary artifact')


def run_study(reference, root=ROOT):
    plan, catalog, rules, left = load_inputs(reference, root)
    machine = graph(rules)
    table = counts(machine, plan['count_lengths'])
    check = exhaustive(machine, rules, plan['primary_exhaustive_max_source_length'])
    if check['all_two_code_failures'] != [r['input_rule_lines'] for r in catalog['synthetic_roundtrip']['all_failed_cases']]:
        raise ValueError('accepted two-code failure ledger changed')
    for observed, expected in zip(check['by_length'], table, strict=False):
        if any(observed[k] != expected[k] for k in observed):
            raise ValueError('enumeration counts and dynamic programming disagree')
    pair_ledger = []
    for sequence in check['all_two_code_failures']:
        item = witness(sequence, rules)
        if item['unmatched']:
            raise ValueError('two-code comparison has an unmatched event')
        pair_ledger.append({'input_rule_lines': sequence,
                            'currier_input_sha256': sha(''.join(left[k] for k in sequence).encode()),
                            'eva_output_sha256': item['encoded_sha256'],
                            'currier_roundtrip_sha256': sha(''.join(left[k] for k in item['returned_rule_lines']).encode()),
                            'input_codepoints': len(sequence), 'eva_codepoints': item['encoded_codepoints'],
                            'roundtrip_codepoints': len(item['returned_rule_lines'])})
    if canonical(pair_ledger) != canonical(catalog['synthetic_roundtrip']['all_failed_cases']):
        raise ValueError('complete accepted pair descriptors disagree')
    rejecting, eof_failures = [], []
    for state in machine['states'][:-1]:
        prefix = state['shortest_reaching_rule_lines']
        if not state['eof_accepts']:
            eof_failures.append({'state': state['id'], 'witness': witness(prefix, rules)})
        for edge in state['transitions']:
            if edge['target'] == REJECT:
                rejecting.append({'from_state': state['id'], 'input_rule_line': edge['input_rule_line'],
                                  'witness': witness(prefix + [edge['input_rule_line']], rules)})
    if any(r['witness']['exact_roundtrip'] for r in rejecting + eof_failures):
        raise ValueError('rejecting graph witness round-trips')
    return {'schema_version': 1, 'scope': plan['scope'], 'machine_plan_sha256': PLAN_SHA256,
            'producer_sha256': sha((root / 'scripts/currier_roundtrip_language.py').read_bytes()),
            'dependency_hashes': plan['dependency_hashes'], 'reference_artifacts': plan['reference_artifacts'],
            'graph': machine, 'counts': table, 'primary_exhaustive_check': check,
            'complete_two_code_ledger_matches_accepted': True, 'rejecting_transitions': rejecting,
            'failed_eof_states': eof_failures, 'counting_measure': 'Uniform independent rule-code strings, not a manuscript distribution',
            'raw_primary_payload_redistributed': False, 'author_program_executed': False,
            'manuscript_input_used': False, 'full_bitrans_conformance_claimed': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args(argv)
    try:
        protected = protected_files(args.reference)
        guard_output(args.output, protected)
        result = run_study(args.reference)
        if args.check and canonical(result) != canonical(read_json(args.check)):
            raise ValueError('complete report differs')
        if args.output:
            guard_output(args.output, protected)
            args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
        print('Complete round-trip language report verified')
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
