from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.audit_eva_token_coverage import encoded
from scripts.build_msi_viewer import (
    ROOT, SETTINGS, TEMPLATE, SCRIPT, INPUTS, load_inputs, packet_bytes,
    protect_output, write_packet, check_packet,
)
from scripts.check_msi_intake import sha


class MSIViewerTests(unittest.TestCase):
    def test_pinned_parent_and_git_blobs_match_with_literal_pending_status(self):
        settings,record=load_inputs()
        self.assertEqual(set(settings['input_sha256']),set(INPUTS))
        self.assertEqual(settings['parent_status_at_creation'],'pending review')
        self.assertEqual(len(record['selected_images']),6)
        bad=deepcopy(settings);bad['input_sha256'][INPUTS[0]]='0'*64
        with patch('scripts.build_msi_viewer.strict_json',return_value=bad),self.assertRaisesRegex(ValueError,'pinned'):
            load_inputs()
        bad=deepcopy(settings);bad['schema_version']=True
        with patch('scripts.build_msi_viewer.strict_json',return_value=bad),self.assertRaises(ValueError):load_inputs()

    def make_sources(self,cache):
        settings,record=load_inputs();record=deepcopy(record)
        for i,row in enumerate(record['selected_images']+record['yale_references']):
            raw=f'Synthetic unchanged image container {i}'.encode()
            (cache/row['local_filename']).write_bytes(raw);row['metadata']['sha256']=sha(raw)
        return settings,record

    def test_packet_keeps_exact_originals_and_only_declared_files(self):
        with tempfile.TemporaryDirectory() as directory:
            cache=Path(directory);settings,record=self.make_sources(cache)
            (cache/'unrelated-private-input.txt').write_text('test placeholder; must stay outside packet')
            with patch('scripts.build_msi_viewer.load_inputs',return_value=(settings,record)), \
                    patch('scripts.build_msi_viewer.verify') as verifier:
                files=packet_bytes(cache)
            self.assertEqual(len(files),11)
            self.assertNotIn('unrelated-private-input.txt',str(files.keys()))
            for row in record['selected_images']+record['yale_references']:
                self.assertEqual(files['assets/'+row['local_filename']],(cache/row['local_filename']).read_bytes())
            verifier.assert_called_once_with(record,cache=cache,root=ROOT)
            manifest=json.loads(files['packet.json']);self.assertEqual(manifest['files'],
                {name:sha(raw) for name,raw in sorted(files.items()) if name!='packet.json'})
            self.assertIn(b'Processed folder',files['index.html']);self.assertIn(b'RGB folder',files['index.html'])

    def test_json_model_escapes_markup_and_source_mutation_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            cache=Path(directory);settings,record=self.make_sources(cache)
            record['selected_images'][0]['name']='</script><b>test</b>'
            with patch('scripts.build_msi_viewer.load_inputs',return_value=(settings,record)),patch('scripts.build_msi_viewer.verify'):
                files=packet_bytes(cache)
                self.assertNotIn(b'</script><b>test',files['index.html'])
                self.assertIn(b'\\u003c/script\\u003e',files['index.html'])
                (cache/record['selected_images'][0]['local_filename']).write_bytes(b'changed')
                with self.assertRaisesRegex(ValueError,'changed during packet'):packet_bytes(cache)

    def test_output_rejects_checkout_cache_ancestors_nonempty_and_symbolic_links(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);cache=base/'cache';cache.mkdir();out=base/'out'
            for target in (ROOT,ROOT/'viewer-output',cache,cache/'child',base):
                with self.assertRaises(ValueError):protect_output(target,cache)
            out.mkdir();(out/'already').write_text('preserve')
            with self.assertRaises(ValueError):protect_output(out,cache)
            link=base/'linked';link.symlink_to(cache,target_is_directory=True)
            with self.assertRaises(ValueError):protect_output(link,cache)

    def test_late_directory_alias_is_rejected_after_all_serialization(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);cache=base/'cache';cache.mkdir();marker=cache/'original';marker.write_bytes(b'unchanged')
            out=base/'out'
            def computed(*args):
                out.symlink_to(cache,target_is_directory=True)
                return {'index.html':b'local output'}
            with patch('scripts.build_msi_viewer.packet_bytes',side_effect=computed),self.assertRaises(ValueError):write_packet(out,cache)
            self.assertEqual(marker.read_bytes(),b'unchanged')
            self.assertFalse((cache/'index.html').exists())

    def test_complete_packet_replay_rejects_changes_extra_files_and_links(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);cache=base/'cache';cache.mkdir();out=base/'output'
            files={'index.html':b'index','viewer.js':b'code','assets/example.jpg':b'original','packet.json':b'{}'}
            with patch('scripts.build_msi_viewer.packet_bytes',return_value=files):
                write_packet(out,cache);check_packet(out,cache)
                (out/'index.html').write_bytes(b'changed')
                with self.assertRaises(ValueError):check_packet(out,cache)
                (out/'index.html').write_bytes(b'index');(out/'extra').write_bytes(b'test')
                with self.assertRaises(ValueError):check_packet(out,cache)
                (out/'extra').unlink();(out/'index.html').unlink();(out/'index.html').symlink_to(out/'viewer.js')
                with self.assertRaises(ValueError):check_packet(out,cache)


if __name__=='__main__':unittest.main()
