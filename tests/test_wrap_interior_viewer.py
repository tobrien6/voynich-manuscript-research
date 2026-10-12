"""Check literal certificate preservation, independent of the score producer."""

from html.parser import HTMLParser
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts import build_wrap_interior_viewer as viewer


class VisibleRecord(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = {key: [] for key in ('interior', 'full', 'half', 'conditional', 'raw',
                                         'stream-values', 'stream-probability')}
        self.capture = None
        self.tables, self.completed_tables = [], []
        self.case_ids, self.orders, self.streams, self.tokens = [], [], [], []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get('class', '').split()
        if tag == 'section' and 'case' in classes:
            self.case_ids.append(attrs['id'])
        if tag == 'details' and 'order-detail' in classes:
            self.orders.append((attrs['data-case'], int(attrs['data-order'])))
        if tag == 'details' and 'stream-order' in classes:
            self.streams.append(int(attrs['data-order']))
        if tag == 'span' and 'token' in classes:
            self.tokens.append(attrs)
        if tag in ('span', 'code'):
            matching = set(classes) & set(self.values)
            if matching:
                self.capture = (tag, matching.pop(), [])
        if tag == 'table':
            self.tables.append({'caption': [], 'rows': [], 'in_caption': False, 'row': [], 'cell': None})
        if self.tables:
            table = self.tables[-1]
            if tag == 'caption':
                table['in_caption'] = True
            if tag == 'tr':
                table['row'] = []
            if tag == 'td':
                table['cell'] = []

    def handle_data(self, data):
        if self.capture:
            self.capture[2].append(data)
        if self.tables:
            table = self.tables[-1]
            if table['in_caption']:
                table['caption'].append(data)
            if table['cell'] is not None:
                table['cell'].append(data)

    def handle_endtag(self, tag):
        if self.capture and tag == self.capture[0]:
            self.values[self.capture[1]].append(''.join(self.capture[2]))
            self.capture = None
        if not self.tables:
            return
        table = self.tables[-1]
        if tag == 'caption':
            table['in_caption'] = False
        elif tag == 'td':
            table['row'].append(''.join(table['cell'] or []))
            table['cell'] = None
        elif tag == 'tr' and table['row']:
            table['rows'].append(table['row'])
        elif tag == 'table':
            self.completed_tables.append(self.tables.pop())


class WrappingViewerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.declaration, cls.record, cls.settings = viewer.load_inputs()
        cls.template = (viewer.ROOT / viewer.VIEWER / 'template.html').read_text()
        cls.raw = viewer.render(cls.declaration, cls.record, cls.settings, cls.template)
        cls.visible = VisibleRecord()
        cls.visible.feed(cls.raw.decode())
        cls.ordered = [order for case in cls.record['cases'] for order in case['orders']]

    def test_all_fixed_values_and_events_are_visible(self):
        parser = self.visible
        self.assertEqual(parser.case_ids, [c['id'] for c in self.record['cases']])
        self.assertEqual(parser.orders, [(c['id'], i) for c in self.record['cases'] for i in range(len(c['orders']))])
        self.assertEqual(len(self.ordered), 173)
        self.assertEqual(parser.values['interior'], [viewer.array(o['interior']) for o in self.ordered])
        for visible, source in (('conditional', 'conditional_probability'), ('raw', 'event_weight_given_first')):
            self.assertEqual(parser.values[visible], [o[source] for o in self.ordered])
        event_tables = [t for t in parser.completed_tables if ''.join(t['caption']) == 'Every recorded incoming-width event']
        self.assertEqual([t['rows'] for t in event_tables],
                         [[[str(e['width']), 'Yes' if e['closes_selected_row'] else 'No', e['event_weight_given_first']]
                           for e in o['next_width_events']] for o in self.ordered])

    def test_every_score_stream_trace_and_tail_is_preserved(self):
        streams = self.record['stream_fixture']['orders']
        self.assertEqual(self.visible.streams, list(range(9)))
        self.assertEqual(self.visible.values['stream-values'], [viewer.array(o['stream']) for o in streams])
        self.assertEqual(self.visible.values['stream-probability'], [o['iid_stream_probability'] for o in streams])
        for visible, source in (('full', 'full_centered'), ('half', 'half_centered')):
            expected = [o[source] if o[source] is not None else 'Unscored' for o in self.ordered]
            expected += [o['equal_row_' + source] for o in streams]
            self.assertEqual(self.visible.values[visible], expected)
        html = self.raw.decode()
        self.assertEqual(html.count('Exactly full final tail'), 9)
        self.assertEqual(html.count('Capacity equality alone does not close this row.'), 9)
        self.assertEqual(html.count('causes overflow and is carried unchanged'), 18)
        self.assertEqual(html.count('0–4 (zero-based)'), 9)
        self.assertEqual(html.count('5–9 (zero-based)'), 9)
        self.assertEqual(html.count('starts at token position 10'), 9)
        expected_widths = [w for c in self.record['cases'] for o in c['orders'] for w in [c['first'], *o['interior'], c['last']]]
        expected_widths += [w for c in self.record['cases'] if not c['orders'] for w in [c['first'], *c['interior_bag'], c['last']]]
        expected_widths += [w for o in streams for r in [*o['completed_rows'], o['unclosed_tail']] for w in r['lengths']]
        self.assertEqual([t['title'].split(', width ')[1] for t in self.visible.tokens], list(map(str, expected_widths)))

    def test_half_classes_and_all_negative_conditions_remain(self):
        tables = self.visible.completed_tables
        halves = [t for t in tables if ''.join(t['caption']) == 'Every recorded half-bag class']
        self.assertEqual([t['rows'] for t in halves],
                         [[[viewer.array(h['early_bag']), viewer.array(h['late_bag']), str(h['unique_orders']),
                            h['conditional_order_probability'], h['mean_half_centered']] for h in c['half_classes']]
                          for c in self.record['cases'] if c['half_classes']])
        overview = next(t for t in tables if ''.join(t['caption']) == 'All eight accepted fixed conditions')
        self.assertEqual(overview['rows'][-3][2:], ['1', '1', 'Unscored', 'Unscored'])
        self.assertEqual([r[2:] for r in overview['rows'][-2:]], [['0', 'Undefined', 'Undefined', 'Undefined']] * 2)
        self.assertEqual(overview['rows'][3][2:], ['1', '1', '0', '0'])
        html = self.raw.decode()
        self.assertIn('<noscript>', html)
        self.assertNotIn('<section class="case" hidden', html)
        self.assertIn('scoring requires at least five', html)
        self.assertIn('Capacity is fixed and at least the largest supported width', html)
        self.assertNotIn('fetch(', html)
        self.assertNotIn('localStorage', html)
        self.assertNotIn('src="http', html)

    def test_pinned_blobs_and_template_drift_are_rejected(self):
        with patch.object(viewer.subprocess, 'check_output', return_value=b'changed'):
            with self.assertRaisesRegex(ValueError, 'archived input changed'):
                viewer.load_inputs()
        for changed in (self.template.replace('@@CASES@@', ''), self.template + '@@CASES@@'):
            with self.assertRaisesRegex(ValueError, 'missing or duplicated'):
                viewer.render(self.declaration, self.record, self.settings, changed)
        self.assertNotIn(b'@@', self.raw)

    def test_reproduction_and_output_preservation(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'viewer.html'
            viewer.write_new(output, self.raw)
            self.assertEqual(output.read_bytes(), self.raw)
            with self.assertRaisesRegex(ValueError, 'new unlinked'):
                viewer.write_new(output, b'replacement')
            link = Path(temporary) / 'alias.html'
            link.symlink_to(output)
            with self.assertRaises(ValueError):
                viewer.write_new(link, b'replacement')
            hardlink = Path(temporary) / 'hardlink.html'
            os.link(output, hardlink)
            with self.assertRaises(ValueError):
                viewer.write_new(hardlink, b'replacement')
            self.assertEqual(output.read_bytes(), self.raw)
            real_open = Path.open
            def install_late_alias(path, *args, **kwargs):
                os.link(output, path)
                return real_open(path, *args, **kwargs)
            with patch.object(Path, 'open', autospec=True, side_effect=install_late_alias):
                with self.assertRaises(FileExistsError):
                    viewer.write_new(Path(temporary) / 'late.html', b'replacement')
            self.assertEqual(output.read_bytes(), self.raw)
            self.assertEqual((Path(temporary) / 'late.html').read_bytes(), self.raw)
        self.assertEqual(self.raw, viewer.render(self.declaration, self.record, self.settings, self.template))


if __name__ == '__main__':
    unittest.main()
