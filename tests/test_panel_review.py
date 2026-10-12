from dataclasses import replace
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.audit_transliterations import load_sources
from scripts.build_67r_review import build as build67
from scripts.build_68r_review import build as build68


ROOT = Path(__file__).resolve().parents[1]


class PanelReviewTests(unittest.TestCase):
    def test_accepted_67r_report_is_unchanged_by_reusing_the_collector(self):
        self.assertEqual(build67(), json.loads((ROOT / "research/panel-regions/f67r-p0-review.json").read_text()))

    def test_68r_keeps_its_present_page_without_p0_records(self):
        report = build68()
        self.assertEqual(report["locations"], 9)
        self.assertEqual((report["identical_native_record_text"], report["different_native_record_text"]), (4, 5))
        third = report["page_audit"][2]
        self.assertEqual(third["page_id"], "f68r3")
        self.assertEqual(third["declared_p0_locations"], [])
        self.assertTrue(all(edition["header_present"] and edition["present_loci"] == 22
                            and edition["present_p0_locations"] == [] for edition in third["editions"]))
        self.assertTrue(all(record["image_glyph_verification"] == "pending" for record in report["records"]))

    def changed_sources(self, transform):
        sources = load_sources()
        return [(source, transform(document) if source["id"] == "ZL3b" else document)
                for source, document in sources]

    def test_absent_zero_p0_page_cannot_pass_as_an_empty_expected_set(self):
        def missing_header(document):
            pages = dict(document.pages)
            pages.pop("f68r3")
            return replace(document, pages=pages)
        with patch("scripts.build_68r_review.load_sources", return_value=self.changed_sources(missing_header)):
            with self.assertRaisesRegex(ValueError, "absent required page header"):
                build68()

    def test_invented_p0_record_on_third_page_is_refused(self):
        def changed_kind(document):
            loci = tuple(replace(locus, kind="P0") if locus.key == "f68r3.1" else locus for locus in document.loci)
            return replace(document, loci=loci)
        with patch("scripts.build_68r_review.load_sources", return_value=self.changed_sources(changed_kind)):
            with self.assertRaisesRegex(ValueError, "P0 cohort differs for f68r3"):
                build68()

    def test_missing_declared_row_and_removed_non_p0_writing_are_refused(self):
        for page, predicate, message in [
            ("f68r2", lambda locus: locus.key == "f68r2.5", "P0 cohort differs for f68r2"),
            ("f68r3", lambda locus: locus.page == "f68r3", "require present writing records"),
        ]:
            with self.subTest(page=page):
                changed = self.changed_sources(lambda document: replace(document, loci=tuple(
                    locus for locus in document.loci if not predicate(locus))))
                with patch("scripts.build_68r_review.load_sources", return_value=changed):
                    with self.assertRaisesRegex(ValueError, message):
                        build68()


if __name__ == "__main__":
    unittest.main()
