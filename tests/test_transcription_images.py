import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.audit_transcription_images import audit, make_report, page_reference, split_dependency_errors
from scripts.index_yale_manifest import build, serialize
from scripts.ivtff import parse_ivtff
from tests.test_yale_image_index import canvas, encoded


def sources(text):
    document = parse_ivtff(text)
    return [(dict(id=sid, sha256="0" * 64, url="https://example.org/" + sid, alphabet="Eva-"), document)
            for sid in ("ZL3b", "IT2a")]


def report(text, canvases):
    indexed = build(encoded(canvases), "2026-10-11")
    return make_report(sources(text), indexed["canvases.csv"], {})


class TranscriptionImageTests(unittest.TestCase):
    def test_convention_is_explicit_and_does_not_repair_unknown_names(self):
        self.assertEqual(page_reference("f67r1")["folio_sides"], ["67r"])
        self.assertEqual(page_reference("fRos")["folio_sides"], ["85v", "86r"])
        self.assertEqual(page_reference("f86v6")["folio_sides"], ["86v"])
        for page in ("f67r3", "f1r1", "f86v1", "fRos.1", " f67r1", "F67R1"):
            self.assertEqual(page_reference(page)["kind"], "unsupported_convention")

    def test_partial_views_are_retained_and_panel_region_stays_unresolved(self):
        result = report("#=IVTFF Eva- 2.0 M\n<f70v1>\n<f70v1.1,@P0> ab\n",
                        [canvas("70v (part)", 1), canvas("70v (part)", 2)])
        page = result["pages"][0]
        self.assertEqual(page["page_id"], "f70v1")
        self.assertEqual(page["strict_folio_lookup_status"], "unsupported_identifier")
        self.assertEqual(page["side_reference_status"], "side_references_matched")
        self.assertEqual(page["panel_region_status"], "unresolved")
        self.assertEqual([match["image_oid"] for match in page["canvas_matches"]], ["1", "2"])

    def test_rosettes_deduplicates_shared_canvas_and_preserves_both_sides(self):
        result = report("#=IVTFF Eva- 2.0 M\n<fRos>\n<fRos.1,@P0> ab\n",
                        [canvas("85v and 86r (foldout)", 1)])
        page = result["pages"][0]
        self.assertEqual(len(page["canvas_matches"]), 1)
        self.assertEqual(page["canvas_matches"][0]["requested_folio_sides"], ["85v", "86r"])
        self.assertEqual(page["dependency_group"], "yale-leaves:85+86")

    def test_absent_label_is_visible_and_does_not_become_a_historical_alias(self):
        result = report("#=IVTFF Eva- 2.0 M\n<f117v>\n<f117v.1,@P0> ab\n",
                        [canvas("116v", 1)])
        page = result["pages"][0]
        self.assertEqual(page["side_reference_status"], "label_unmatched")
        self.assertEqual(page["unmatched_folio_sides"], ["117v"])
        self.assertEqual(page["canvas_matches"], [])
        self.assertIsNone(page["dependency_group"])

    def test_leaf_dependencies_include_both_sides_and_transitive_spreads(self):
        text = ("#=IVTFF Eva- 2.0 M\n<f88r>\n<f88r.1,@P0> ab\n"
                "<f90v1>\n<f90v1.1,@P0> cd\n")
        result = report(text, [canvas("88r", 1), canvas("88v and 89r", 2),
                               canvas("89v (part) and 90r", 3), canvas("90v (part)", 4)])
        self.assertEqual([p["dependency_group"] for p in result["pages"]],
                         ["yale-leaves:88+89+90"] * 2)

    def test_nonexistent_loci_and_empty_page_headers_remain_in_denominators(self):
        text = ("#=IVTFF Eva- 2.0 M\n<f1r>\n<f1r.1,@P0> ab\n"
                "<f1r.2,!P0> cd\n<f1r.3,@L0> ef\n<f1v>\n")
        result = report(text, [canvas("1r", 1), canvas("1v", 2)])
        counts = result["pages"][0]["source_counts"][0]
        self.assertEqual((counts["loci"], counts["present_loci"], counts["present_p0_loci"]), (3, 2, 1))
        self.assertEqual(result["pages"][1]["source_counts"][0]["loci"], 0)
        self.assertEqual(result["sources"][0]["page_headers"], 2)

    def test_other_editions_cannot_silently_change_the_pair(self):
        selected = sources("#=IVTFF Eva- 2.0 M\n<f1r>\n<f1r.1,@P0> ab\n")
        rows = build(encoded([canvas("1r", 1)]), "2026-10-11")["canvases.csv"]
        expected = make_report(selected, rows, {})
        extra = (dict(selected[0][0], id="GC2a"), selected[0][1])
        self.assertEqual(make_report(selected + [extra], rows, {}), expected)
        with self.assertRaisesRegex(ValueError, "exactly one"):
            make_report(selected[:1], rows, {})

    def test_manifest_and_generated_index_are_checked_against_the_pin(self):
        raw = encoded([canvas("1r", 1)])
        indexed = build(raw, "2026-10-11")
        text = "#=IVTFF Eva- 2.0 M\n<f1r>\n<f1r.1,@P0> ab\n"
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            index_dir = root / "research/image-index"
            index_dir.mkdir(parents=True)
            for filename, content in serialize(indexed).items():
                (index_dir / filename).write_text(content)
            (root / "data/raw").mkdir(parents=True)
            catalog = {"sources": []}
            for sid in ("ZL3b", "IT2a"):
                path = "data/raw/" + sid + ".txt"
                (root / path).write_text(text)
                catalog["sources"].append(dict(id=sid, path=path, alphabet="Eva-", url="https://example.org",
                    sha256=hashlib.sha256(text.encode()).hexdigest(), bytes=len(text.encode())))
            (root / "data/transliterations.json").write_text(json.dumps(catalog))
            self.assertEqual(audit(raw, root)["distinct_page_ids"], 1)
            with self.assertRaisesRegex(ValueError, "manifest differs"):
                audit(raw + b"\n", root)
            (index_dir / "canvases.csv").write_text("changed\n")
            with self.assertRaisesRegex(ValueError, "does not reproduce"):
                audit(raw, root)

    def test_split_cannot_hide_transitive_dependencies_by_omitting_canvas_or_group(self):
        text = ("#=IVTFF Eva- 2.0 M\n<f88r>\n<f88r.1,@P0> ab\n"
                "<f90v1>\n<f90v1.1,@P0> cd\n")
        result = report(text, [canvas("88r", 1), canvas("88v and 89r", 2),
                               canvas("89v (part) and 90r", 3), canvas("90v (part)", 4)])
        split = {"units": [
            {"unit_id": "a", "folio_ids": ["88"], "dependency_groups": ["arbitrary-a"], "canvas_ids": []},
            {"unit_id": "b", "folio_ids": ["90"], "dependency_groups": ["arbitrary-b"], "canvas_ids": []},
        ]}
        errors = split_dependency_errors(split, result)
        self.assertTrue(any("multiple units" in error for error in errors))
        self.assertTrue(any("missing derived dependency group" in error for error in errors))
        self.assertTrue(any("missing indexed canvas" in error for error in errors))

    def test_combined_split_unit_with_complete_references_passes(self):
        result = report("#=IVTFF Eva- 2.0 M\n<fRos>\n<fRos.1,@P0> ab\n",
                        [canvas("85v and 86r (foldout)", 1)])
        split = {"units": [{"unit_id": "rosettes", "folio_ids": ["85", "86"],
                           "dependency_groups": ["yale-leaves:85+86"],
                           "canvas_ids": [result["pages"][0]["canvas_matches"][0]["canvas_uri"]]}]}
        self.assertEqual(split_dependency_errors(split, result), [])
        split["units"][0]["folio_ids"] = ["117"]
        self.assertTrue(any("no supported" in error for error in split_dependency_errors(split, result)))


if __name__ == "__main__":
    unittest.main()
