import contextlib
import copy
from dataclasses import replace
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import build_fros_review as module
from scripts.ivtff import parse_ivtff


TEXT = ('<fRos>\n<fRos.112,@L0> <!left>o{ckh}y\n'
        '<fRos.113,=Cc> <!above><!08:00>sar.ody,or\n'
        '<fRos.114,+Ca> <!below>[a:?].dar\n<fRos.115,=L0> y\n')


class RosetteReviewTests(unittest.TestCase):
    def proposal(self):
        root = module.ROOT
        return json.loads((root / module.PROPOSAL).read_text()), (root / module.PLAN).read_bytes()

    def test_full_native_text_annotations_kinds_and_physical_lines_are_preserved(self):
        document = parse_ivtff('#=IVTFF Eva- 2.0 M\n' + TEXT)
        rows = module.select_loci(document)
        self.assertEqual([r['identifier'] for r in rows], list(module.TARGETS))
        self.assertEqual(rows[0]['native_text'], '<!left>o{ckh}y')
        self.assertEqual(rows[1]['native_text'], '<!above><!08:00>sar.ody,or')
        self.assertEqual(rows[2]['native_text'], '<!below>[a:?].dar')
        self.assertEqual([r['source_physical_line'] for r in rows], [3, 4, 5, 6])
        self.assertEqual([r['kind'] for r in rows], ['L0', 'Cc', 'Ca', 'L0'])
        alternate = parse_ivtff('#=IVTFF v101 2.0 M\n' + TEXT.replace('sar.ody,or', 'say.a89m.oy'))
        self.assertNotEqual(module.select_loci(alternate)[1]['native_text'], rows[1]['native_text'])

    def test_missing_nonexistent_duplicate_or_changed_kind_is_rejected(self):
        for text in (TEXT.replace('<fRos.114,+Ca> <!below>[a:?].dar\n', ''),
                     TEXT.replace('114,+Ca', '114,!Ca'), TEXT.replace('114,+Ca', '114,+Cc')):
            with self.subTest(text=text), self.assertRaises(ValueError):
                module.select_loci(parse_ivtff('#=IVTFF Eva- 2.0 M\n' + text))
        doc = parse_ivtff('#=IVTFF Eva- 2.0 M\n' + TEXT)
        with self.assertRaises(ValueError):
            module.select_loci(replace(doc, loci=doc.loci + (doc.loci[0],)))

    def test_targets_plan_and_unverified_status_cannot_be_silently_changed(self):
        proposal, plan = self.proposal()
        module.validate_proposal(proposal, plan)
        for key, value in (('targets', list(module.TARGETS[:-1])), ('apply_to_statistics', True),
                           ('verified_locus_crosswalk', {}), ('independent_glyph_review', 'approved')):
            with self.subTest(key=key), self.assertRaises(ValueError):
                module.validate_proposal({**proposal, key: value}, plan)
        with self.assertRaises(ValueError):
            module.validate_proposal(proposal, plan + b' changed')
        changed = copy.deepcopy(proposal)
        changed['target_layout_assessments'][0]['glyph_alignment'] = 'verified'
        with self.assertRaises(ValueError):
            module.validate_proposal(changed, plan)

    def test_region_must_be_bounded_and_consistent_in_both_coordinate_systems(self):
        proposal, plan = self.proposal()
        for key, value in (('x', -1), ('width', 7926), ('height', 0), ('y', 6000.0)):
            changed = copy.deepcopy(proposal)
            changed['image_region_pixels'][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                module.validate_proposal(changed, plan)
        for value in (float('nan'), float('inf'), proposal['image_region_normalized']['x'] + 0.01):
            changed = copy.deepcopy(proposal)
            changed['image_region_normalized']['x'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                module.validate_proposal(changed, plan)

    def test_shared_carrier_and_both_source_editions_remain_in_the_real_checklist(self):
        report = module.report()
        self.assertEqual(report['dependency_group'], 'yale-leaves:85+86')
        self.assertFalse(report['apply_to_statistics'])
        self.assertIsNone(report['verified_locus_crosswalk'])
        self.assertEqual({s['id']: s['alphabet'] for s in report['editions']}, module.EDITIONS)
        for edition in report['editions']:
            self.assertEqual([r['identifier'] for r in edition['loci']], list(module.TARGETS))

    def test_image_request_must_describe_the_declared_original_resolution_region(self):
        proposal, plan = self.proposal()
        for key, value in (('url', 'https://example.org/other-image.jpg'),
                           ('width', 550), ('sha256', 'unverified'), ('bytes', 0)):
            changed = copy.deepcopy(proposal)
            changed['image_inspection_order'][1][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                module.validate_proposal(changed, plan)
        changed = copy.deepcopy(proposal)
        changed['image_inspection_order'].reverse()
        with self.assertRaises(ValueError):
            module.validate_proposal(changed, plan)

    def test_cli_rejects_drift_and_preserves_inputs_including_linked_source(self):
        root = module.ROOT
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            check, output = folder / 'check.json', folder / 'output.json'
            check.write_text('{}')
            output.write_text('preserve this')
            with patch('sys.argv', ['review', '--check', str(check), '--output', str(output)]), \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                module.main()
            self.assertEqual(output.read_text(), 'preserve this')
            link = folder / 'linked-source.json'
            link.hardlink_to(root / 'data/raw/ZL3b-n.txt')
            for path in (root / module.PROPOSAL, root / module.PLAN, link):
                before = path.read_bytes()
                with self.subTest(path=path.name), \
                        patch('sys.argv', ['review', '--output', str(path)]), \
                        contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    module.main()
                self.assertEqual(path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
