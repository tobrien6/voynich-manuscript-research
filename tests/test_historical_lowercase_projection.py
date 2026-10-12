import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import audit_historical_lowercase_projection as module
from scripts.audit_historical_interlinear import parse_historical
from scripts.ivtff import parse_ivtff
from tests.test_historical_modern_pages import fixture_root


def compare(historical, modern):
    return module.compare_projections(parse_historical(historical.encode())[0], parse_ivtff(modern))


OLD = "<f1r> {}\n## <f1r.P> {}\n<f1r.P.1;H> a-\n<f1r.P.2;H> b=\n"
NEW = "#=IVTFF EvaT 2.0 M\n<f1r>\n<f1r.1,@P0> a.b\n"


class HistoricalLowercaseProjectionTests(unittest.TestCase):
    def test_identical_projection_does_not_preserve_record_boundaries_or_spacing(self):
        profile = compare(OLD, NEW)["page_profiles"][0]
        self.assertTrue(profile["lowercase_streams_equal"])
        self.assertEqual(profile["historical_H"]["selected_records"], 2)
        self.assertEqual(profile["modern_IT2a_present"]["selected_records"], 1)
        self.assertEqual(profile["historical_H"]["omitted_characters_outside_human_comments"], {"-": 1, "=": 1})
        self.assertEqual(profile["modern_IT2a_present"]["omitted_characters_outside_human_comments"], {".": 1})

    def test_unknown_sign_changes_are_disclosed_despite_equal_projection(self):
        profile = compare(OLD.replace("a-", "a**-"), NEW.replace("a.b", "a?.b"))["page_profiles"][0]
        self.assertTrue(profile["lowercase_streams_equal"])
        self.assertEqual(profile["historical_H"]["omitted_characters_outside_human_comments"]["*"], 2)
        self.assertEqual(profile["modern_IT2a_present"]["omitted_characters_outside_human_comments"]["?"], 1)

    def test_equal_frequencies_do_not_establish_sequence_identity(self):
        report = compare(OLD, NEW.replace("a.b", "b.a"))
        self.assertFalse(report["page_profiles"][0]["lowercase_streams_equal"])
        self.assertTrue(report["page_profiles"][0]["lowercase_frequencies_equal"])
        self.assertEqual(report["summary"]["same_frequencies_different_stream_page_ids"], ["f1r"])

    def test_source_specific_comments_and_metadata_are_excluded(self):
        old = OLD.replace("a-", "a{xyz}-")
        new = NEW.replace("a.b", "<@H=z>a<!xyz>.b")
        profile = compare(old, new)["page_profiles"][0]
        self.assertTrue(profile["lowercase_streams_equal"])
        self.assertEqual(profile["historical_H"]["removed_human_comment_occurrences"], 1)
        self.assertEqual(profile["modern_IT2a_present"]["removed_human_comment_occurrences"], 1)
        self.assertEqual(profile["modern_IT2a_present"]["removed_modern_text_metadata_tags"], 1)
        self.assertEqual(profile["modern_IT2a_present"]["omitted_characters_outside_human_comments"]["z"], 1)

    def test_empty_and_unmatched_pages_cannot_supply_equality(self):
        empty = compare(OLD.replace("a-", "*-").replace("b=", "%%="), NEW.replace("a.b", "?"))
        self.assertIsNone(empty["page_profiles"][0]["lowercase_streams_equal"])
        self.assertEqual(empty["summary"]["shared_empty_projection_page_ids"], ["f1r"])
        unmatched = compare(OLD.replace("f1r", "f1r1"), NEW)
        self.assertEqual(unmatched["summary"]["comparable_nonempty_page_ids"], 0)
        self.assertEqual(unmatched["summary"]["shared_record_bearing_page_ids"], 0)
        self.assertEqual(unmatched["summary"]["historical_only_page_ids"], ["f1r1"])
        self.assertEqual(unmatched["summary"]["modern_only_page_ids"], ["f1r"])
        self.assertTrue(all(p["lowercase_streams_equal"] is None for p in unmatched["page_profiles"]))

    def test_nonexistent_records_and_other_transcribers_do_not_enter_projection(self):
        report = compare(OLD + "<f1r.P.1;C> xyz=\n", NEW + "<f1r.2,!Lf> xyz\n")
        profile = report["page_profiles"][0]
        self.assertTrue(profile["lowercase_streams_equal"])
        self.assertEqual(profile["modern_IT2a_present"]["projected_lowercase_symbols"], 2)
        inventory = report["modern_nonexistent_projection_inventory"][0]
        self.assertFalse(inventory["used_in_primary_comparison"])
        self.assertEqual(inventory["projection"]["projected_lowercase_symbols"], 3)
        self.assertFalse(report["declared_envelope_diagnostics"][0]["including_nonexistent_lowercase_stream_equals_historical"])

    def test_cli_input_protection_and_failure_preserve_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = fixture_root(root)
            output = root / "output.json"
            output.write_text("preserved")
            check = root / "check.json"
            check.write_text("{}")
            for arguments in (["audit", "--output", str(sources[0])],
                              ["audit", "--check", str(check), "--output", str(output)]):
                before = sources[0].read_bytes()
                with patch.object(module, "ROOT", root), patch("sys.argv", arguments):
                    with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                        module.main()
                    self.assertEqual(error.exception.code, 1)
                self.assertEqual(sources[0].read_bytes(), before)
                self.assertEqual(output.read_text(), "preserved")

    def test_hardlink_outputs_preserve_synthetic_inputs_and_reader(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = fixture_root(root)
            inputs = module.load_inputs(root)
            reader = root / "synthetic-reader.py"
            reader.write_text("synthetic protected reader")
            inputs[-1].add(reader)
            targets = (*sources, root / "data/historical/interlinear-16e6.json",
                       root / "data/transliterations.json", reader)
            before = {path: path.read_bytes() for path in targets}
            with patch.object(module, "ROOT", root), patch.object(module, "load_inputs", return_value=inputs):
                for index, target in enumerate(targets):
                    alias = root / f"alias-{index}.json"
                    alias.hardlink_to(target)
                    with patch("sys.argv", ["audit", "--output", str(alias)]):
                        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                            module.main()
                        self.assertEqual(error.exception.code, 1)
                    self.assertEqual({path: path.read_bytes() for path in targets}, before)


if __name__ == "__main__":
    unittest.main()
