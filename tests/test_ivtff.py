import unittest

from scripts.ivtff import parse_ivtff, without_free_comments


HEADER = "#=IVTFF Eva- 2.0 M\n"


class StructuralReaderTests(unittest.TestCase):
    def test_rosettes_and_nonsequential_foldout_panel_names_are_preserved(self):
        doc = parse_ivtff(HEADER + "<fRos>\n<fRos.1,@Cc> a\n"
                          "<f86v6>\n<f86v6.1,@L0> b\n")
        self.assertEqual([l.key for l in doc.loci], ['fRos.1', 'f86v6.1'])

    def test_continuation_is_one_locus_and_whitespace_is_not_word_space(self):
        doc = parse_ivtff(HEADER + "<f1r>\n<f1r.1,@P0> a. /\n/ b\n")
        self.assertEqual(len(doc.loci), 1)
        self.assertEqual(doc.loci[0].text, "a.b")
        self.assertEqual(doc.loci[0].line_number, 3)

    def test_tags_persist_and_reset_at_page_boundary(self):
        doc = parse_ivtff(HEADER + "<f1r> <! $H=@ $L=A>\n"
                          "<f1r.1,@P0> a<@H=2>\n<f1r.2,+P0> b\n"
                          "<f1r.3,+P0> c<@H=@>\n<f1v>\n<f1v.1,@P0> d\n")
        self.assertEqual([l.variables.get('H') for l in doc.loci], ['2', '2', None, None])
        self.assertEqual(doc.loci[0].variables['L'], 'A')
        self.assertNotIn('L', doc.loci[-1].variables)

    def test_transcribers_remain_separate_and_nonexistent_locus_is_flagged(self):
        doc = parse_ivtff(HEADER + "<f1r>\n<f1r.1,@P0;A> a\n"
                          "<f1r.1,@P0;B> b\n<f1r.2,!L0> c\n")
        self.assertEqual([l.transcriber for l in doc.loci], ['A', 'B', None])
        self.assertEqual(doc.loci[0].key, doc.loci[1].key)
        self.assertFalse(doc.loci[-1].present)

    def test_comments_do_not_create_tags_or_annotation_counts(self):
        doc = parse_ivtff(HEADER + "<f1r>\n<f1r.1,@P0> a<!@H=4 , [x:y] @254;>.b\n")
        self.assertEqual(doc.loci[0].variables, {})
        self.assertEqual(without_free_comments(doc.loci[0].text), 'a.b')

    def test_invalid_structure_fails_instead_of_silently_dropping_records(self):
        invalid = [
            "<f1r>\n<f1v.1,@P0> a\n",  # wrong current page
            "<f1r>\n<f1r.1,@P0> a\n<f1r.1,@P0> b\n",  # duplicate
            "<f1r>\n<f1r.2,@P0> a\n<f1r.1,+P0> b\n",  # reversed sequence
            "<f1r>\n<f1r>\n",  # duplicate page
            "<f1r>\n<f1r.1,@P0> a /\n# interrupted\n",  # broken wrap
            "<f1r>\n<f1r.1,@P0> a /\n",  # unfinished wrap
            "/ a\n",  # orphan wrap
            "<AA001> a\n",  # unsupported compact ID
            "<f1r> a\n",  # text in page header
            "<f1r>\n<f1r.1,@P0> <@H=2>a<@H=3>\n",  # conflicting tags
        ]
        for body in invalid:
            with self.subTest(body=body), self.assertRaises(ValueError):
                parse_ivtff(HEADER + body)
        with self.assertRaises(ValueError):
            parse_ivtff("#=IVTFF Eva- 1.7\n")


if __name__ == '__main__':
    unittest.main()
