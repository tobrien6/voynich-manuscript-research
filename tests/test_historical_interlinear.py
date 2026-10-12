import hashlib
import io
import contextlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from scripts import audit_historical_interlinear as module
from scripts.audit_historical_interlinear import (
    audit, parse_historical, read_pinned_archive, summarize,
)


FIXTURE = (b"## <f0.A> {}\r\n# Invented fixture\r\n<f1r> {$I=H}\r\n"
           b"## <f1r.P> {}\r\n<f1r.P.0a;H> a{comment !,* \xc5}.b!=-\r\n"
           b"<f1r.P.0a;C> x.y=\r\n## <f1r.t> {}\r\n<f1r.t.1;H> a*=\r\n")


def archive_fixture(payload=FIXTURE, extra=False):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("source.evt", payload)
        if extra:
            archive.writestr("other.evt", payload)
    data = buffer.getvalue()
    catalog = {
        "archive_bytes": len(data), "archive_sha256": hashlib.sha256(data).hexdigest(),
        "member": "source.evt", "member_bytes": len(payload),
        "member_sha256": hashlib.sha256(payload).hexdigest(),
    }
    return data, catalog


class HistoricalInterlinearTests(unittest.TestCase):
    def test_native_keys_include_unit_case_line_suffix_and_transcriber(self):
        records, counts = parse_historical(FIXTURE)
        self.assertEqual([r.locator for r in records],
                         ["f1r.P.0a;H", "f1r.P.0a;C", "f1r.t.1;H"])
        self.assertEqual(records[0].physical_line, 5)
        self.assertIn("\xc5", records[0].body)
        self.assertEqual(counts["physical_lines"], 8)
        self.assertEqual(counts["documentation_headers"], 1)
        self.assertEqual(counts["passive_unit_headers"], 2)

    def test_comment_punctuation_does_not_enter_notation_counts(self):
        records, counts = parse_historical(FIXTURE)
        profile = summarize(records, counts, "H")["selected"]
        self.assertEqual(profile["records"], 2)
        self.assertEqual(profile["record_logical_unit_count"], 2)
        self.assertEqual(profile["marker_occurrences_outside_comments"], {
            "asterisk": 1, "comma": 0, "equals": 2, "exclamation": 1,
            "hyphen": 1, "percent": 0, "period": 1,
        })
        self.assertEqual(profile["curly_comment_occurrences"], 1)
        self.assertEqual(profile["records_with_nonascii_in_raw_body"], 1)
        self.assertEqual(profile["records_with_nonascii_outside_comments"], 0)

    def test_unknown_wrapped_or_malformed_input_is_not_silently_dropped(self):
        cases = (FIXTURE + b"continued text\n",
                 FIXTURE.replace(b"a*=", b"a{bad="),
                 FIXTURE.replace(b"a*=", b"a{nested{bad}}="),
                 FIXTURE.replace(b"<f1r.t.1;H>", b"<f1r.t.1;HH>"),
                 FIXTURE.replace(b"<f1r.t.1;H>", b"<f1r.t.1f;H>"))
        for data in cases:
            with self.subTest(data=data[-50:]), self.assertRaises(ValueError):
                parse_historical(data)

    def test_duplicate_or_missing_context_is_rejected(self):
        for data in (FIXTURE + b"<f1r.t.1;H> q=\n",
                     FIXTURE.replace(b"## <f1r.t> {}\r\n", b""),
                     FIXTURE.replace(b"<f1r.t.1;H>", b"<f2r.t.1;H>")):
            with self.subTest(data=data[-50:]), self.assertRaises(ValueError):
                parse_historical(data)

    def test_archive_and_member_are_separately_pinned(self):
        data, catalog = archive_fixture()
        self.assertEqual(read_pinned_archive(data, catalog), FIXTURE)
        with self.assertRaisesRegex(ValueError, "archive bytes"):
            read_pinned_archive(data + b"changed", catalog)
        for key, value in (("member_sha256", "0" * 64), ("member_bytes", 1),
                           ("member", "unexpected.evt")):
            with self.subTest(key=key), self.assertRaises(ValueError):
                read_pinned_archive(data, {**catalog, key: value})
        data, catalog = archive_fixture(extra=True)
        with self.assertRaisesRegex(ValueError, "inventory"):
            read_pinned_archive(data, catalog)

    def test_empty_selection_fails_and_source_order_remains_observable(self):
        records, counts = parse_historical(FIXTURE)
        for code in ("Z", "h", "HH"):
            with self.subTest(code=code), self.assertRaises(ValueError):
                summarize(records, counts, code)
        self.assertNotEqual(
            summarize(records, counts, "H")["selected"]["ordered_locator_sha256"],
            summarize(records[::-1], counts, "H")["selected"]["ordered_locator_sha256"],
        )

    def test_pinned_archive_is_fully_accounted_for(self):
        report = audit()["structure"]
        lines = report["line_classification"]
        self.assertEqual(lines["physical_lines"],
                         sum(value for key, value in lines.items() if key != "physical_lines")
                         + report["all_native_records"])
        self.assertEqual(report["all_native_records"],
                         sum(report["records_by_transcriber"].values()))
        self.assertEqual(report["selected"]["records"], 5214)
        self.assertEqual(report["selected"]["record_page_count"], 225)

    def test_cli_drift_preserves_output_and_cannot_overwrite_inputs(self):
        data, catalog = archive_fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / "data/historical"
            folder.mkdir(parents=True)
            source = folder / "source.zip"
            source.write_bytes(data)
            catalog.update(schema_version=1, id="fixture", path="data/historical/source.zip",
                           selected_transcriber="H", historical_identity_status="synthetic")
            catalog_path = folder / "interlinear-16e6.json"
            catalog_path.write_text(json.dumps(catalog))
            output = root / "output.json"
            output.write_text("existing output")
            for protected in (source, catalog_path):
                before = protected.read_bytes()
                with patch.object(module, "ROOT", root), patch("sys.argv", ["audit", "--output", str(protected)]):
                    with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                        module.main()
                    self.assertEqual(error.exception.code, 1)
                self.assertEqual(protected.read_bytes(), before)
            source.write_bytes(data + b"drift")
            with patch.object(module, "ROOT", root), patch("sys.argv", ["audit", "--output", str(output)]):
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    module.main()
                self.assertEqual(error.exception.code, 1)
            self.assertEqual(output.read_text(), "existing output")


if __name__ == "__main__":
    unittest.main()
