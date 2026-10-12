import json
from pathlib import Path
import tempfile
import unittest

from scripts.audit_transliterations import ROOT, audit, load_sources, summarize
from scripts.ivtff import parse_ivtff


class SourceAuditTests(unittest.TestCase):
    def test_pinned_sources_and_inspected_nonexistent_record(self):
        result = audit()
        sources = {source['id']: source for source in result['sources']}
        zl, it = sources['ZL3b'], sources['IT2a']
        self.assertEqual((zl['records'], zl['present_records']), (5385, 5385))
        self.assertEqual((it['records'], it['present_records']), (5215, 5214))
        self.assertEqual(it['explicitly_nonexistent_loci'], ['f89v2.26,!Lf'])
        self.assertEqual(result['comparisons'][0]['shared_present_loci'], 5214)

    def test_changed_source_bytes_are_rejected_before_analysis(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'data/raw').mkdir(parents=True)
            catalog = json.loads((ROOT / 'data/transliterations.json').read_text())
            catalog['sources'] = catalog['sources'][:1]
            (root / 'data/transliterations.json').write_text(json.dumps(catalog))
            (root / catalog['sources'][0]['path']).write_bytes(b'corrupted')
            with self.assertRaisesRegex(ValueError, 'source bytes do not match'):
                load_sources(root)

    def test_annotation_counts_exclude_comments_and_nonexistent_records(self):
        doc = parse_ivtff('#=IVTFF Eva- 2.0 M\n<f1r>\n'
                          '<f1r.1,@P0> a,b.[c:d]???<! , [e:f] ?>\n'
                          '<f1r.2,!L0> a,b.[e:f]?\n')
        report = summarize({'id': 'fixture', 'sha256': 'synthetic'}, doc)
        counts = report['annotation_counts_in_present_loci']
        self.assertEqual(counts['uncertain_spaces'], 1)
        self.assertEqual(counts['alternative_groups'], 1)
        self.assertEqual(counts['illegible_question_marks'], 3)


if __name__ == '__main__':
    unittest.main()
