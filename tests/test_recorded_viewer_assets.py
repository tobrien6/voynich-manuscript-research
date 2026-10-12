import hashlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from scripts import fetch_recorded_viewer_assets as subject


class Response(io.BytesIO):
    status = 200
    def __init__(self, raw, url):
        super().__init__(raw)
        self.url = url
    def geturl(self):
        return self.url


class Opener:
    def __init__(self, payloads):
        self.payloads, self.requests = payloads, []
    def open(self, request, timeout):
        self.requests.append((request, timeout))
        payload = self.payloads[request.full_url]
        if isinstance(payload, Exception):
            raise payload
        return Response(payload, request.full_url)


def resource(name='image.jpg', raw=b'fixture pixels', size=True):
    return {'name': name, 'url': 'https://collections.library.yale.edu/iiif/2/1006210/full/full/0/default.jpg',
            'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw) if size else None}


class RecordedAssetsTests(unittest.TestCase):
    def test_all_three_actual_archival_inventories_are_exact(self):
        for name, count in [('f76r', 5), ('y-lookup', 17), ('immediate-repeat', 13)]:
            with self.subTest(name=name):
                source, assets = subject.load_source(name)
                self.assertEqual(len(assets), count)
                self.assertEqual(len({a['name'] for a in assets}), count)
                self.assertEqual(len(source['record_sha256']), 64)
        _, repeat = subject.load_source('immediate-repeat')
        self.assertEqual(sum(x['name'].endswith('.jpg') for x in repeat), 10)
        self.assertTrue(any('wide-detail' in x['name'] for x in repeat))

    def test_wrong_source_blob_is_rejected_before_network(self):
        with patch.object(subject.subprocess, 'check_output', return_value=b'changed record'):
            with self.assertRaisesRegex(subject.ReceiptError, 'fingerprint'):
                subject.load_source('f76r')

    def test_public_service_urls_reject_credentials_queries_and_redirect_provider_changes(self):
        subject.validate_url('https://voynich.nu/img/extra/eva01.gif')
        for url in ('http://collections.library.yale.edu/iiif/2/1/info.json',
                    'https://user:secret@collections.library.yale.edu/iiif/2/1/info.json',
                    'https://collections.library.yale.edu/iiif/2/1/info.json?token=fixture',
                    'https://example.test/private.jpg'):
            with self.subTest(url=url), self.assertRaises(subject.ReceiptError):
                subject.validate_url(url)
        redirect = subject.RecordedRedirects()
        from urllib.request import Request
        with self.assertRaisesRegex(subject.ReceiptError, 'provider'):
            redirect.redirect_request(Request(resource()['url']), None, 302, 'redirect', {},
                                      'https://voynich.nu/img/extra/eva01.gif')

    def test_verified_download_cache_reuse_and_unrelated_files_are_preserved(self):
        asset = resource()
        opener = Opener({asset['url']: b'fixture pixels'})
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            private = directory / 'unrelated-fixture.txt'
            private.write_bytes(b'unchanged unrelated fixture')
            with patch.object(subject, 'load_source', return_value=({'id': 'f76r'}, [asset])):
                report, path = subject.fetch_assets('f76r', directory, opener=opener)
                self.assertEqual(report['resources'][0]['status'], 'downloaded_verified')
                self.assertEqual((directory / asset['name']).read_bytes(), b'fixture pixels')
                self.assertEqual((directory / asset['name']).stat().st_nlink, 1)
                self.assertTrue(path.is_file())
                second, _ = subject.fetch_assets('f76r', directory, opener=opener)
                self.assertEqual(second['resources'][0]['status'], 'reused_verified')
                self.assertEqual(len(opener.requests), 1)
            self.assertEqual(private.read_bytes(), b'unchanged unrelated fixture')
            request = opener.requests[0][0]
            self.assertIsNone(request.get_header('Authorization'))
            self.assertIsNone(request.get_header('Cookie'))

    def test_partial_response_hash_mismatch_and_http_failure_leave_no_asset(self):
        for payload in (b'fixture', b'wrong response', HTTPError(resource()['url'], 503, 'unavailable', {}, None)):
            with self.subTest(payload=type(payload).__name__), tempfile.TemporaryDirectory() as folder:
                directory = Path(folder)
                asset = resource()
                with patch.object(subject, 'load_source', return_value=({'id': 'f76r'}, [asset])):
                    report, path = subject.fetch_assets('f76r', directory, opener=Opener({asset['url']: payload}))
                self.assertFalse(report['complete_successful_selection'])
                self.assertEqual(report['resources'][0]['status'], 'failed')
                self.assertFalse((directory / asset['name']).exists())
                self.assertEqual(json.loads(path.read_text()), report)

    def test_mixed_success_and_failure_remain_separate_in_receipt(self):
        good, bad = resource('good.jpg'), resource('bad.jpg')
        bad['url'] = 'https://collections.library.yale.edu/iiif/2/1006210/1,1,2,2/full/0/default.jpg'
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(subject, 'load_source', return_value=({'id': 'f76r'}, [good, bad])):
                report, _ = subject.fetch_assets('f76r', Path(folder), opener=Opener({good['url']: b'fixture pixels', bad['url']: b'bad'}))
            self.assertEqual([x['status'] for x in report['resources']], ['downloaded_verified', 'failed'])
            self.assertTrue((Path(folder) / 'good.jpg').exists())
            self.assertFalse((Path(folder) / 'bad.jpg').exists())

    def test_existing_mismatch_symlink_and_hardlink_are_not_overwritten(self):
        for kind in ('mismatch', 'symlink', 'hardlink'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as folder:
                directory, asset = Path(folder), resource()
                original = directory / 'copied-original.txt'
                original.write_bytes(b'original synthetic input')
                target = directory / asset['name']
                if kind == 'mismatch': target.write_bytes(b'original synthetic input')
                elif kind == 'symlink': target.symlink_to(original)
                else: os.link(original, target)
                opener = Opener({})
                with patch.object(subject, 'load_source', return_value=({'id': 'f76r'}, [asset])):
                    report, _ = subject.fetch_assets('f76r', directory, opener=opener)
                self.assertEqual(report['resources'][0]['status'], 'failed')
                self.assertEqual(len(opener.requests), 0)
                self.assertEqual(original.read_bytes(), b'original synthetic input')
                self.assertEqual(target.read_bytes(), b'original synthetic input')

    def test_late_alias_during_fetch_is_preserved_and_staging_files_cleaned(self):
        with tempfile.TemporaryDirectory() as folder:
            directory, asset = Path(folder), resource()
            original = directory / 'copied-input.txt'
            original.write_bytes(b'unchanged input fixture')
            target = directory / asset['name']
            def late(*args):
                os.link(original, target)
                return b'fixture pixels'
            with patch.object(subject, 'load_source', return_value=({'id': 'f76r'}, [asset])), \
                    patch.object(subject, 'retrieve', side_effect=late):
                report, _ = subject.fetch_assets('f76r', directory)
            self.assertEqual(report['resources'][0]['status'], 'failed')
            self.assertEqual(original.read_bytes(), b'unchanged input fixture')
            self.assertEqual(list(directory.glob('.recorded-resource-*')), [])

    def test_output_git_checkouts_ancestors_and_unrecorded_requests_are_rejected(self):
        for path in (subject.ROOT / 'local-assets', subject.ROOT.parent):
            with self.subTest(path=path), self.assertRaises(subject.ReceiptError):
                subject.protect_directory(path)
        with tempfile.TemporaryDirectory() as folder:
            directory = Path(folder)
            repo = directory / 'other-checkout'
            (repo / '.git').mkdir(parents=True)
            with self.assertRaisesRegex(subject.ReceiptError, 'Git checkouts'):
                subject.protect_directory(repo / 'assets')
            with self.assertRaisesRegex(subject.ReceiptError, 'recorded resource'):
                subject.fetch_assets('f76r', directory, only=['unrecorded.jpg'])


if __name__ == '__main__':
    unittest.main()
