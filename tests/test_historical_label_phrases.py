import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile

from scripts.audit_historical_interlinear import HistoricalRecord
from scripts.audit_historical_label_phrases import audit, literal_string, lookup


def record(line, transcriber, body, page="f1r", unit="X"):
    return HistoricalRecord(f"{page}.{unit}.{line};{transcriber}", page, unit, line,
                            transcriber, body, 1)


class HistoricalLabelLookupTests(unittest.TestCase):
    def test_formatter_preserves_readings_case_and_coded_fallbacks(self):
        self.assertEqual(literal_string("a!b,{comment}cd-ef=G*{&138}%"), "ab cd ef G*")
        self.assertEqual(literal_string("a{&F}b="), "ab")
        with self.assertRaises(ValueError):
            literal_string("a{bad")

    def test_only_complete_exact_records_match(self):
        records = [record("1", "H", "a.b="), record("2", "F", "x.a.b="),
                   record("3", "U", "A.b="), record("4", "V", "a.b*=")]
        result = lookup(records, ["a b", "missing"])
        self.assertEqual([r["locator"] for r in result["matches"][0]["records"]], ["f1r.X.1;H"])
        self.assertEqual(result["matches"][1]["records"], [])

    def test_all_transcribers_and_repeated_strings_keep_their_identifiers(self):
        records = [record("1", "F", "a.b="), record("1", "H", "a.c="),
                   record("2", "H", "a.b=", page="f2r")]
        result = lookup(records, ["a b"])
        self.assertEqual(result["native_records_searched"], 3)
        self.assertEqual(result["matches"][0]["matches_by_transcriber"], {"F": 1, "H": 1})
        self.assertEqual(len(result["native_key_readings"]), 2)
        first = result["native_key_readings"][0]
        self.assertEqual([r["literal_string"] for r in first["readings"]], ["a b", "a c"])

    def test_native_key_grouping_does_not_merge_other_units_or_line_suffixes(self):
        records = [record("1", "F", "a.b="), record("1a", "H", "a.c="),
                   record("1", "H", "a.c=", unit="Y")]
        result = lookup(records, ["a b"])
        self.assertEqual(len(result["native_key_readings"]), 1)
        self.assertEqual(len(result["native_key_readings"][0]["readings"]), 1)

    def test_bad_queries_and_duplicate_locators_fail(self):
        for phrases in ([], ["a", "a"], [" a"], ["a  b"], [""], "word", [{}]):
            with self.subTest(phrases=phrases), self.assertRaises(ValueError):
                lookup([], phrases)
        with self.assertRaises(ValueError):
            lookup([record("1", "H", "a="), record("1", "H", "b=")], ["a"])

    def test_recovered_archive_search_covers_every_native_record(self):
        result = audit()
        self.assertEqual(result["native_records_searched"], 17357)
        queries = {m["phrase"]: m for m in result["matches"]}
        self.assertNotIn("H", queries["dar alocfhy"]["matches_by_transcriber"])
        self.assertNotIn("H", queries["otarodl shy orory"]["matches_by_transcriber"])
        self.assertEqual(queries["otarodl shy orory"]["matches_by_transcriber"], {"F": 1})

    def test_cli_preserves_all_five_inputs_through_direct_and_hardlink_outputs(self):
        root = Path(__file__).resolve().parents[1]
        protected = ("data/historical/interlinear-16e6.json", "data/historical/source.zip",
                     "research/historical/parser-plan.json", "scripts/audit_historical_label_phrases.py",
                     "scripts/audit_historical_interlinear.py")
        for name in protected:
            for linked in (False, True):
                with self.subTest(input=name, hardlink=linked), tempfile.TemporaryDirectory() as directory:
                    fixture = Path(directory).resolve()
                    (fixture / "scripts").mkdir()
                    (fixture / "data/historical").mkdir(parents=True)
                    (fixture / "research/historical").mkdir(parents=True)
                    for script in ("audit_historical_label_phrases.py", "audit_historical_interlinear.py"):
                        shutil.copyfile(root / "scripts" / script, fixture / "scripts" / script)
                    payload = b"<f1r> {}\n## <f1r.X> {}\n<f1r.X.1;H> a.b=\n"
                    buffer = io.BytesIO()
                    with zipfile.ZipFile(buffer, "w") as archive:
                        archive.writestr("fixture.evt", payload)
                    raw = buffer.getvalue()
                    (fixture / "data/historical/source.zip").write_bytes(raw)
                    catalog = {"schema_version": 1, "id": "fixture", "path": "data/historical/source.zip",
                               "archive_bytes": len(raw), "archive_sha256": hashlib.sha256(raw).hexdigest(),
                               "member": "fixture.evt", "member_bytes": len(payload),
                               "member_sha256": hashlib.sha256(payload).hexdigest(), "credit": "Invented fixture",
                               "archive_url": "https://example.org/synthetic.zip", "permission": {"synthetic": True}}
                    (fixture / "data/historical/interlinear-16e6.json").write_text(json.dumps(catalog))
                    plan = {"plan_version": 1, "source_id": "fixture",
                            "archive_sha256": catalog["archive_sha256"], "member_sha256": catalog["member_sha256"],
                            "supplement_sha256": "0" * 64, "figure_label_phrases": ["a b"]}
                    (fixture / "research/historical/parser-plan.json").write_text(json.dumps(plan))
                    target = fixture / name
                    output = fixture / "linked-output.json" if linked else target
                    if linked:
                        output.hardlink_to(target)
                    before = target.read_bytes()
                    result = subprocess.run([sys.executable, str(fixture / "scripts/audit_historical_label_phrases.py"),
                                             "--output", str(output)], cwd=fixture, capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("must not overwrite", result.stderr)
                    self.assertEqual(target.read_bytes(), before)
                    self.assertEqual(output.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
