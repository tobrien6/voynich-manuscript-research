import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from scripts import audit_historical_modern_pages as module
from scripts.audit_historical_interlinear import parse_historical
from scripts.ivtff import parse_ivtff


HISTORICAL = (b"<f1r> {}\n## <f1r.P> {}\n<f1r.P.1;H> a-\n<f1r.P.2;H> b=\n"
              b"<f1r.P.1;C> c-\n<f2r> {}\n## <f2r.t> {}\n<f2r.t.0a;H> d=\n")
MODERN = ("#=IVTFF EvaT 2.0 M\n<f1r>\n<f1r.1,@P0> a.b\n"
          "<f2r>\n<f2r.1,@L0> c\n<f2r.2,@L0> d\n<f2r.3,!Lf> ?\n")


def fixture_root(root):
    source = root / "data/historical/source.zip"
    source.parent.mkdir(parents=True)
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as archive:
        archive.writestr("fixture.evt", HISTORICAL)
    data = stream.getvalue()
    source.write_bytes(data)
    historical = {"schema_version": 1, "id": "synthetic", "selected_transcriber": "H",
                  "path": "data/historical/source.zip", "archive_bytes": len(data),
                  "archive_sha256": hashlib.sha256(data).hexdigest(), "member": "fixture.evt",
                  "member_bytes": len(HISTORICAL), "member_sha256": hashlib.sha256(HISTORICAL).hexdigest()}
    (root / module.HISTORICAL_CATALOG).write_text(json.dumps(historical))
    raw = MODERN.encode("ascii")
    modern_source = root / "data/modern.txt"
    modern_source.write_bytes(raw)
    modern = {"schema_version": 1, "sources": [{"id": "IT2a", "path": "data/modern.txt",
               "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw), "alphabet": "EvaT",
               "url": "https://example.invalid/synthetic"}]}
    (root / module.MODERN_CATALOG).write_text(json.dumps(modern))
    return source, modern_source


class HistoricalModernPagesTests(unittest.TestCase):
    def comparison(self, old=HISTORICAL, new=MODERN):
        return module.compare_pages(parse_historical(old)[0], parse_ivtff(new))

    def test_equal_totals_preserve_cancelling_page_count_differences(self):
        report = self.comparison()
        self.assertTrue(report["summary"]["global_counts_equal"])
        self.assertEqual(report["summary"]["historical_H_records"], 3)
        self.assertEqual(report["summary"]["modern_declared_loci"], 4)
        self.assertEqual([(p["page_id"], p["difference"]) for p in report["different_count_pages"]],
                         [("f1r", -1), ("f2r", 1)])
        self.assertEqual(report["different_count_pages"][1]["historical_locators_in_source_order"],
                         ["f2r.t.0a;H"])

    def test_nonexistent_loci_remain_declared_but_not_present(self):
        report = self.comparison()
        profile = report["page_profiles"][1]
        self.assertEqual(profile["modern_declared_loci"], 3)
        self.assertEqual(profile["modern_present_loci"], 2)
        self.assertEqual(profile["modern_nonexistent_loci"], ["f2r.3,!Lf"])
        self.assertEqual(sum(profile["modern_present_kinds"].values()), 2)

    def test_panel_suffixes_are_not_truncated_into_aliases(self):
        report = self.comparison(HISTORICAL.replace(b"f1r", b"f1r1"))
        self.assertEqual(report["summary"]["shared_exact_page_ids"], 1)
        self.assertEqual(report["summary"]["historical_only_record_page_ids"], ["f1r1"])
        self.assertEqual(report["summary"]["modern_only_present_page_ids"], ["f1r"])
        self.assertIsNone(report["page_profiles"][0]["modern_present_minus_historical_native_count"])

    def test_empty_headers_and_nonexistent_only_pages_are_retained(self):
        report = self.comparison(new=MODERN + "<f3r>\n<f3r.1,!Lf> ?\n<f4r>\n")
        self.assertEqual(report["summary"]["modern_pages_without_present_loci"], ["f3r", "f4r"])
        self.assertEqual([p["status"] for p in report["page_profiles"][-2:]],
                         ["modern_nonexistent_only", "modern_header_only"])

    def test_order_and_native_identifiers_remain_visible(self):
        records, _ = parse_historical(HISTORICAL)
        left = module.compare_pages(records, parse_ivtff(MODERN))
        right = module.compare_pages(records[::-1], parse_ivtff(MODERN))
        self.assertNotEqual(left["summary"]["historical_ordered_locator_sha256"],
                            right["summary"]["historical_ordered_locator_sha256"])
        self.assertNotEqual(left["page_profiles"][0]["historical_ordered_locator_sha256"],
                            right["page_profiles"][0]["historical_ordered_locator_sha256"])

    def test_interlinear_modern_input_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "single-source"):
            self.comparison(new=MODERN.replace("f1r.1,@P0>", "f1r.1,@P0;H>"))

    def test_padding_only_diagnostic_preserves_unknown_glyphs_and_native_counts(self):
        old = HISTORICAL.replace(b"a-", b"%%%!-{comment with a glyph *}").replace(b"b=", b"*!=")
        report = self.comparison(old=old)
        padding = report["summary"]["historical_padding_only_records"]
        self.assertEqual(len(padding), 1)
        self.assertEqual(padding[0]["locator"], "f1r.P.1;H")
        self.assertEqual(padding[0]["percent_fillers"], 3)
        self.assertEqual(padding[0]["exclamation_fillers"], 1)
        self.assertEqual(report["summary"]["historical_H_records"], 3)
        self.assertEqual(report["page_profiles"][0]["historical_padding_only_locators"], ["f1r.P.1;H"])

    def test_both_source_pins_fail_before_changed_payloads_are_parsed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, modern = fixture_root(root)
            self.assertEqual(module.audit(root)["summary"]["historical_H_records"], 3)
            for target, message in ((source, "archive bytes"), (modern, "modern source bytes")):
                original = target.read_bytes()
                target.write_bytes(original + b"changed")
                with self.assertRaisesRegex(ValueError, message):
                    module.audit(root)
                target.write_bytes(original)

    def test_catalog_escape_and_duplicate_selection_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fixture_root(root)
            path = root / module.MODERN_CATALOG
            catalog = json.loads(path.read_text())
            catalog["sources"].append(catalog["sources"][0].copy())
            path.write_text(json.dumps(catalog))
            with self.assertRaisesRegex(ValueError, "exactly one"):
                module.audit(root)
            catalog["sources"] = catalog["sources"][:1]
            catalog["sources"][0]["path"] = "../outside-source.txt"
            path.write_text(json.dumps(catalog))
            with self.assertRaisesRegex(ValueError, "repository"):
                module.audit(root)

    def test_cli_protects_source_and_preserves_output_on_check_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = fixture_root(root)
            output = root / "report.json"
            output.write_text("untouched")
            check = root / "wrong.json"
            check.write_text("{}")
            cases = [["audit", "--output", str(source)] for source in sources]
            cases += [["audit", "--output", str(root / module.MODERN_CATALOG)],
                      ["audit", "--output", str(output), "--check", str(check)]]
            for arguments in cases:
                before = [path.read_bytes() for path in sources]
                with patch.object(module, "ROOT", root), patch("sys.argv", arguments):
                    with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                        module.main()
                    self.assertEqual(error.exception.code, 1)
                self.assertEqual([path.read_bytes() for path in sources], before)
                self.assertEqual(output.read_text(), "untouched")


if __name__ == "__main__":
    unittest.main()
