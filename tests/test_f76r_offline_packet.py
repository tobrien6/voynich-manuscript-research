"""Literal evidence preservation and isolated local packet copying."""

from copy import deepcopy
from html import escape
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import build_f76r_offline_packet as packet


class OfflinePacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.declared, cls.declared_raw, cls.canonical, cls.review = packet.load_inputs()

    def fixture(self, cache):
        cache.mkdir()
        review = deepcopy(self.review)
        for item in review['inspection_files']:
            raw = ('synthetic copy fixture: ' + item['local_filename']).encode()
            item['bytes'], item['sha256'] = len(raw), packet.sha(raw)
            (cache / item['local_filename']).write_bytes(raw)
        metadata = review['service_metadata']
        raw = packet.serialize({'@id': metadata['service_id'], 'width': metadata['width'], 'height': metadata['height']})
        metadata['sha256'] = packet.sha(raw)
        (cache / metadata['local_filename']).write_bytes(raw)
        (cache / 'unrelated-local-note.txt').write_text('preserve, never copy')
        return review

    def fixture_files(self, review, cache):
        with patch.object(packet, 'load_inputs', return_value=(self.declared, self.declared_raw, self.canonical, review)):
            return packet.packet_files(cache)

    def test_local_conversion_keeps_all_literal_evidence_and_hrefs(self):
        local = packet.local_page(self.canonical, self.review, self.declared, self.declared_raw).decode()
        old, new = packet.PageRecord(), packet.PageRecord()
        old.feed(self.canonical); new.feed(local)
        self.assertEqual(new.native, old.native)
        self.assertEqual(len(new.native), 14)
        self.assertTrue(set(old.links) <= set(new.links))
        images = self.review['inspection_files'][1:]
        self.assertEqual([i['src'] for i in new.images], ['assets/' + i['local_filename'] for i in images])
        for shown, expected in zip(new.images, images):
            self.assertEqual(shown['data-sha256'], expected['sha256'])
            self.assertEqual((int(shown['width']), int(shown['height'])), (expected['width'], expected['height']))
        for row in self.review['records']:
            for note in [*row['direct_observations'], *row['source_row_association']['basis'],
                         *row['source_row_association']['unresolved']]:
                self.assertIn(escape(note), local)
        self.assertIn('Provisional row associations', local)
        self.assertIn('/pull/60', local); self.assertIn('/pull/99', local)
        self.assertIn('<noscript>', local)
        self.assertIn('the browser does not recheck their byte hashes', local)
        self.assertIn('Local image could not load.', local)
        self.assertIn('packet.json', new.links)
        self.assertNotIn('src="https:', local)
        self.assertNotIn('fetch(', local)

    def test_complete_packet_copies_only_five_named_assets_and_replays(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); cache = root / 'cache'; review = self.fixture(cache)
            before = {p.name: p.read_bytes() for p in cache.iterdir()}
            files = self.fixture_files(review, cache)
            output = root / 'packet'
            packet.build_packet(output, files, cache)
            packet.check_packet(output, files)
            self.assertEqual(len(files), 7)
            self.assertEqual({p.name: p.read_bytes() for p in cache.iterdir()}, before)
            self.assertNotIn('assets/unrelated-local-note.txt', files)
            self.assertEqual(self.fixture_files(review, cache), files)
            manifest = json.loads(files['packet.json'])
            self.assertEqual(set(manifest['files']), set(files) - {'packet.json'})
            for name, identity in manifest['files'].items():
                self.assertEqual(identity, {'sha256': packet.sha(files[name]), 'bytes': len(files[name])})
            invalid = dict(files); invalid['../escaped-file'] = b'forbidden'
            with self.assertRaisesRegex(ValueError, 'exact seven'):
                packet.build_packet(root / 'invalid-packet', invalid, cache)
            self.assertFalse((root / 'invalid-packet').exists())
            self.assertFalse((root / 'escaped-file').exists())

    def test_missing_truncated_wrong_equal_size_and_service_metadata_fail(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); cache = root / 'cache'; review = self.fixture(cache)
            name = review['inspection_files'][0]['local_filename']; source = cache / name
            original = source.read_bytes()
            for bad in (original[:-1], b'x' * len(original)):
                source.write_bytes(bad)
                with self.assertRaisesRegex(ValueError, 'bytes|byte count'):
                    self.fixture_files(review, cache)
            source.unlink()
            with self.assertRaises(FileNotFoundError):
                self.fixture_files(review, cache)
            source.write_bytes(original)
            meta = review['service_metadata']
            raw = packet.serialize({'@id': 'wrong service', 'width': meta['width'], 'height': meta['height']})
            (cache / meta['local_filename']).write_bytes(raw); meta['sha256'] = packet.sha(raw)
            with self.assertRaisesRegex(ValueError, 'image-service identity'):
                self.fixture_files(review, cache)
            output = root / 'failed-packet'
            with patch.object(packet, 'load_inputs', return_value=(self.declared, self.declared_raw, self.canonical, review)), \
                    patch('sys.argv', ['build', '--image-directory', str(cache), '--output', str(output)]):
                with self.assertRaises(SystemExit) as exit_result:
                    packet.main()
                self.assertEqual(exit_result.exception.code, 1)
            self.assertFalse(output.exists())

    def test_cache_aliases_and_git_locations_are_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); cache = root / 'cache'; review = self.fixture(cache)
            image = cache / 'f76r-first.jpg'; alias = root / 'original-image'; image.rename(alias)
            image.symlink_to(alias)
            with self.assertRaisesRegex(ValueError, 'regular singly linked'):
                self.fixture_files(review, cache)
            image.unlink(); os.link(alias, image)
            with self.assertRaisesRegex(ValueError, 'regular singly linked'):
                self.fixture_files(review, cache)
            self.assertEqual(image.read_bytes(), alias.read_bytes())
            image.unlink(); image.write_bytes(alias.read_bytes())
            (root / '.git').mkdir()
            with self.assertRaisesRegex(ValueError, 'outside Git'):
                self.fixture_files(review, cache)

    def test_existing_linked_nested_and_git_outputs_are_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); cache = root / 'cache'; review = self.fixture(cache)
            files = self.fixture_files(review, cache)
            existing = root / 'existing'; existing.mkdir(); sentinel = existing / 'note'; sentinel.write_text('preserve')
            alias = root / 'alias'; alias.symlink_to(existing, target_is_directory=True)
            for output in (existing, alias):
                with self.assertRaisesRegex(ValueError, 'fresh unlinked'):
                    packet.build_packet(output, files, cache)
            with self.assertRaisesRegex(ValueError, 'separate'):
                packet.build_packet(cache / 'nested-packet', files, cache)
            git = root / 'checkout'; git.mkdir(); (git / '.git').write_text('gitdir: test')
            with self.assertRaisesRegex(ValueError, 'outside Git'):
                packet.build_packet(git / 'packet', files, cache)
            self.assertEqual(sentinel.read_text(), 'preserve')

    def test_complete_check_detects_missing_extra_changed_and_alias_members(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); cache = root / 'cache'; review = self.fixture(cache)
            files = self.fixture_files(review, cache); output = root / 'packet'
            packet.build_packet(output, files, cache)
            extra = output / 'extra-note'; extra.write_text('keep')
            with self.assertRaisesRegex(ValueError, 'inventory'):
                packet.check_packet(output, files)
            extra.unlink(); extra_dir = output / 'extra-empty'; extra_dir.mkdir()
            with self.assertRaisesRegex(ValueError, 'directory inventory'):
                packet.check_packet(output, files)
            extra_dir.rmdir()
            if hasattr(os, 'mkfifo'):
                special = output / 'extra-pipe'; os.mkfifo(special)
                with self.assertRaisesRegex(ValueError, 'non-regular'):
                    packet.check_packet(output, files)
                special.unlink()
            member = output / 'assets/f76r-first.jpg'; original = member.read_bytes(); member.unlink()
            with self.assertRaisesRegex(ValueError, 'inventory'):
                packet.check_packet(output, files)
            member.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'file bytes'):
                packet.check_packet(output, files)
            member.unlink(); member.symlink_to(cache / 'f76r-first.jpg')
            with self.assertRaisesRegex(ValueError, 'symbolic aliases'):
                packet.check_packet(output, files)
            member.unlink(); os.link(cache / 'f76r-first.jpg', member)
            with self.assertRaisesRegex(ValueError, 'file bytes or aliases'):
                packet.check_packet(output, files)
            self.assertEqual(member.read_bytes(), original)

    def test_late_collisions_preserve_existing_directory_and_input_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); cache = root / 'cache'; review = self.fixture(cache); files = self.fixture_files(review, cache)
            real_mkdir = Path.mkdir
            def late_directory(path, *args, **kwargs):
                real_mkdir(path)
                (path / 'original-note').write_text('preserve')
                return real_mkdir(path, *args, **kwargs)
            with patch.object(Path, 'mkdir', autospec=True, side_effect=late_directory):
                with self.assertRaises(FileExistsError):
                    packet.build_packet(root / 'late-directory', files, cache)
            self.assertEqual((root / 'late-directory/original-note').read_text(), 'preserve')
            source = cache / 'f76r-first.jpg'; original = source.read_bytes(); real_open = Path.open
            def late_member(path, *args, **kwargs):
                if path.name == 'f76r-first.jpg':
                    os.link(source, path)
                return real_open(path, *args, **kwargs)
            with patch.object(Path, 'open', autospec=True, side_effect=late_member):
                with self.assertRaises(FileExistsError):
                    packet.build_packet(root / 'late-member', files, cache)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual((root / 'late-member/assets/f76r-first.jpg').read_bytes(), original)

    def test_archived_input_and_conversion_drift_fail(self):
        with patch.object(packet.subprocess, 'check_output', return_value=b'changed'):
            with self.assertRaisesRegex(ValueError, 'archived packet input changed'):
                packet.load_inputs()
        for changed in (self.canonical.replace('  </header>', ''), self.canonical + '  </header>'):
            with self.assertRaisesRegex(ValueError, 'exactly once'):
                packet.local_page(changed, self.review, self.declared, self.declared_raw)


if __name__ == '__main__':
    unittest.main()
