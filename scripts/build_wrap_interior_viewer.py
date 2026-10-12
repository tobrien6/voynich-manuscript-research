"""Display the accepted IID wrapping certificates without recalculating scores."""

import argparse
import hashlib
from html import escape
import json
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
BASE = 'research/line-wrap/interior'
VIEWER = BASE + '/viewer'
INPUTS = tuple(BASE + '/' + name for name in
               ('certificates.json', 'settings.json', 'PROOF.md', 'RESULTS.md'))
LINK_ROOT = 'https://github.com/tobrien6/voynich-manuscript-research/blob/'
LABELS = ('Repeated interior bag', 'Distinct even interior bag',
          'Distinct odd bag, exactly full', 'Constant interior bag',
          'Unequal IID law', 'Two-token row: unscored',
          'No possible closing overflow', 'Over-capacity condition')
STATUSES = {'completed_eligible': 'Eligible, scored', 'completed_short': 'Completed, unscored',
            'zero_condition_no_overflow': 'No possible overflow',
            'zero_condition_exceeds_capacity': 'Exceeds capacity'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_inputs():
    declaration = json.loads((ROOT / VIEWER / 'inputs.json').read_bytes())
    require(declaration['schema_version'] == 1
            and declaration['viewer_id'] == 'iid-wrap-conditional-orbit-viewer-v1'
            and set(declaration['input_sha256']) == set(INPUTS), 'wrong viewer declaration')
    commit = declaration['accepted_input_commit']
    require(re.fullmatch('[0-9a-f]{40}', commit), 'require an exact accepted commit')
    blobs = {}
    for path in INPUTS:
        raw = subprocess.check_output(['git', 'show', commit + ':' + path], cwd=ROOT)
        require(sha(raw) == declaration['input_sha256'][path], 'archived input changed: ' + path)
        blobs[path] = raw
    record, settings = (json.loads(blobs[INPUTS[index]]) for index in (0, 1))
    require(record['analysis_id'] == settings['analysis_id'] == 'iid-greedy-wrap-interior-symmetry-v1'
            and len(record['cases']) == len(LABELS)
            and [case['id'] for case in record['cases']] == [case['id'] for case in settings['cases']]
            and settings['separator_width'] == 1, 'wrong accepted certificate domain')
    return declaration, record, settings


def text(value, missing='Undefined'):
    return escape(missing if value is None else str(value))


def array(values):
    return '[' + ', '.join(map(str, values)) + ']'


def table(headers, rows, caption, css=''):
    return ('<div class="table-scroll"><table class="' + css + '"><caption>'
            + escape(caption) + '</caption><thead><tr>'
            + ''.join('<th scope="col">' + escape(h) + '</th>' for h in headers)
            + '</tr></thead><tbody>'
            + ''.join('<tr>' + ''.join('<td>' + cell + '</td>' for cell in row) + '</tr>' for row in rows)
            + '</tbody></table></div>')


def diagram(widths, capacity, occupied, tail=False):
    """Add a schematic; width units and one-unit gaps are the accepted toy geometry."""
    count = len(widths) - 2
    early_end = 1 + (count + 1) // 2
    tokens = []
    for index, width in enumerate(widths):
        role = 'endpoint' if index in (0, len(widths) - 1) else ('early' if index < early_end else 'late')
        tokens.append('<span class="token ' + role + '" style="width:' + format(width * .8, 'g')
                      + 'rem" title="Position ' + str(index + 1) + ', width ' + str(width)
                      + '">' + str(width) + '</span>')
    return ('<div class="diagram-scroll"><div class="diagram" style="width:'
            + format(max(capacity, occupied) * .8, 'g') + 'rem"><div class="capacity" style="width:'
            + format(capacity * .8, 'g') + 'rem"><span>Capacity ' + str(capacity) + '</span></div>'
            + '<div class="tokens' + (' tail' if tail else '') + '">' + ''.join(tokens) + '</div></div></div>'
            + '<p class="small">Widths <code>' + array(widths) + '</code> · occupied '
            + str(occupied) + ' of ' + str(capacity) + '. '
            + ('Unclosed tail; excluded from scoring.' if tail else 'One unit between tokens.') + '</p>')


def case_html(case, label, law):
    cid = case['id']
    positive = case['conditional_order_probability'] is not None
    scored = case['status'] == 'completed_eligible'
    missing = 'Unscored' if positive and not scored else 'Undefined'
    summary = ('<dl class="facts"><div><dt>Retained orders</dt><dd>' + str(len(case['orders']))
               + '</dd></div><div><dt>Raw event weight per order, given first</dt><dd>'
               + text(case['per_order_event_weight_given_first'])
               + '</dd></div><div><dt>Conditional probability per order</dt><dd>'
               + text(case['conditional_order_probability'])
               + '</dd></div><div><dt>Full / half conditional means</dt><dd>'
               + text(case['mean_full_centered'], missing) + ' / '
               + text(case['mean_half_centered'], missing) + '</dd></div></dl>')
    law_text = ', '.join(str(w) + ': ' + p for w, p in zip(law['support'], law['probabilities']))
    rows = []
    for index, order in enumerate(case['orders']):
        events = table(('Next width', 'Closes selected row?', 'Raw event weight, given first'),
                       ((text(event['width']), 'Yes' if event['closes_selected_row'] else 'No',
                         text(event['event_weight_given_first'])) for event in order['next_width_events']),
                       'Every recorded incoming-width event')
        geometry = diagram([case['first'], *order['interior'], case['last']],
                           case['capacity'], case['occupied_width'])
        details = ('<details class="order-detail" data-case="' + cid + '" data-order="' + str(index)
                   + '"><summary><code class="interior">' + array(order['interior'])
                   + '</code> — width diagram and incoming events</summary>' + geometry + events + '</details>')
        rows.append((details, '<span class="full">' + text(order['full_centered'], missing) + '</span>',
                     '<span class="half">' + text(order['half_centered'], missing) + '</span>',
                     '<span class="conditional">' + text(order['conditional_probability']) + '</span>',
                     '<span class="raw">' + text(order['event_weight_given_first']) + '</span>'))
    order_table = table(('Interior order (all retained)', 'Full centered', 'Half centered',
                         'Conditional probability', 'Raw event weight, given first'), rows,
                        'Exact accepted values; raw weights and conditional probabilities use different conditions') if rows else ''
    halves = table(('Early bag', 'Late bag', 'Orders', 'Probability within half class', 'Half conditional mean'),
                   ((text(array(h['early_bag'])), text(array(h['late_bag'])), text(h['unique_orders']),
                     text(h['conditional_order_probability']), text(h['mean_half_centered']))
                    for h in case['half_classes']), 'Every recorded half-bag class') if case['half_classes'] else ''
    note = ''
    if not positive:
        note = ('<p class="notice">This event has probability zero. There is no conditional order distribution '
                'or score mean. The candidate bag is shown below; it is not a completed-row observation.</p>'
                + diagram([case['first'], *case['interior_bag'], case['last']], case['capacity'], case['occupied_width']))
    elif not scored:
        note = '<p class="notice">This positive two-token condition is retained. Scoring requires at least five tokens.</p>'
    return ('<section class="case" id="' + cid + '"><h2>' + escape(label) + '</h2><p class="small"><code>'
            + cid + '</code> · ' + escape(case['status']) + '</p><p>First ' + str(case['first']) + ', last '
            + str(case['last']) + ', interior bag <code>' + array(case['interior_bag'])
            + '</code>. IID width law: ' + escape(law_text) + '.</p>' + summary + note + order_table
            + ('<details><summary>Half-bag conditioning</summary>' + halves + '</details>' if halves else '') + '</section>')


def stream_html(stream):
    cards = []
    for index, order in enumerate(stream['orders']):
        original = order['stream'] == stream['original_stream']
        rows = []
        for row in order['completed_rows']:
            rows.append('<div class="closed-row"><h4>Overflow-closed row · token positions '
                        + str(row['start']) + '–' + str(row['end_exclusive'] - 1) + ' (zero-based)</h4>'
                        + diagram(row['lengths'], stream['capacity'], row['occupied_width'])
                        + '<p>Next width <strong>' + str(row['carried_next_first'])
                        + '</strong> causes overflow and is carried unchanged into the following row.</p></div>')
        tail = order['unclosed_tail']
        rows.append('<div class="unclosed"><h4>Exactly full final tail · starts at token position '
                    + str(tail['start']) + '</h4>' + diagram(tail['lengths'], stream['capacity'], tail['occupied_width'], True)
                    + '<p>End of input supplies no closing overflow. Capacity equality alone does not close this row.</p></div>')
        cards.append('<details class="stream-order" data-order="' + str(index) + '"'
                     + (' open' if original else '') + '><summary>Stream ' + str(index + 1)
                     + (' · original fixture' if original else '') + ' · full <span class="full">'
                     + text(order['equal_row_full_centered']) + '</span> · half <span class="half">'
                     + text(order['equal_row_half_centered']) + '</span></summary><p>IID stream probability '
                     + '<span class="stream-probability">' + text(order['iid_stream_probability'])
                     + '</span>; conditional orbit probability ' + text(stream['conditional_order_probability'])
                     + '.</p><p>Complete input <code class="stream-values">' + array(order['stream'])
                     + '</code>.</p>' + ''.join(rows) + '</details>')
    return ('<section id="stream"><h2>Nine streams, one preserved tail</h2><p>Two completed rows each receive one vote. '
            'Their original full / half centered scores are <strong>' + text(stream['original_equal_row_full_centered'])
            + ' / ' + text(stream['original_equal_row_half_centered']) + '</strong>. The full orbit has means '
            + text(stream['mean_full_centered']) + ' / ' + text(stream['mean_half_centered'])
            + '. Individual streams can still be nonzero.</p><p>All four joint half-class sizes remain '
            + text(array(stream['joint_half_class_sizes'])) + '; their accepted means are zero. '
            + 'This does not assert independence between rows.</p>' + ''.join(cards) + '</section>')


def render(declaration, record, settings, template):
    laws = {law['id']: law for law in record['laws']}
    options, summaries, cards = [], [], []
    for case, label in zip(record['cases'], LABELS):
        options.append('<option value="' + case['id'] + '">' + escape(label) + '</option>')
        missing = 'Unscored' if case['status'] == 'completed_short' else 'Undefined'
        summaries.append(('<a href="#' + case['id'] + '" class="case-link">' + escape(label) + '</a>',
                          text(STATUSES[case['status']]), text(len(case['orders'])), text(case['conditional_order_probability']),
                          text(case['mean_full_centered'], missing), text(case['mean_half_centered'], missing)))
        cards.append(case_html(case, label, laws[case['law_id']]))
    commit = declaration['accepted_input_commit']
    links = ''.join('<li><a href="' + LINK_ROOT + commit + '/' + path + '">' + escape(path.rsplit('/', 1)[-1])
                    + '</a> · SHA-256 <code>' + digest + '</code></li>'
                    for path, digest in declaration['input_sha256'].items())
    replacements = {'@@OPTIONS@@': ''.join(options), '@@CASES@@': ''.join(cards),
                    '@@OVERVIEW@@': table(('Fixed condition', 'Status', 'Retained orders', 'Conditional probability',
                                          'Full mean', 'Half mean'), summaries, 'All eight accepted fixed conditions'),
                    '@@STREAM@@': stream_html(record['stream_fixture']), '@@SOURCES@@': links,
                    '@@COMMIT@@': commit,
                    '@@LIMITS@@': ''.join('<li>' + escape(v) + '</li>' for v in record['limitations'])}
    for marker, value in replacements.items():
        require(template.count(marker) == 1, 'missing or duplicated template marker: ' + marker)
        template = template.replace(marker, value)
    require('@@' not in template, 'unresolved template marker')
    return template.encode('utf-8')


def write_new(path, raw):
    path = Path(path)
    require(not path.exists() and not path.is_symlink(), 'output must be a new unlinked file')
    with path.open('xb') as stream:
        stream.write(raw)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    outputs = parser.add_mutually_exclusive_group(required=True)
    outputs.add_argument('--output', type=Path, help='new standalone HTML file')
    outputs.add_argument('--check', type=Path, help='compare an existing HTML artifact without writing')
    args = parser.parse_args()
    try:
        declaration, record, settings = load_inputs()
        raw = render(declaration, record, settings, (ROOT / VIEWER / 'template.html').read_text())
        if args.check:
            require(args.check.read_bytes() == raw, 'viewer differs from accepted-input display')
            print('All accepted inputs and the complete viewer reproduce exactly.')
        else:
            write_new(args.output, raw)
            print('Wrote a standalone display of accepted synthetic certificates.')
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        parser.exit(1, str(error) + '\n')


if __name__ == '__main__':
    main()
