"""Verify the manuscript input boundary while keeping historical pins intact."""

import copy
from contextlib import redirect_stderr, redirect_stdout
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import run_locus_position_baseline as engine
from scripts import verify_locus_position_baseline as verifier
from scripts.audit_eva_token_coverage import encoded, load_json
from scripts.eva_token_adapter import build


class BaselineVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packets = {policy: build(policy) for policy in ("split", "join")}
        cls.raw = {policy: encoded(packet) for policy, packet in cls.packets.items()}
        cls.raw.update(protocol=engine.PROTOCOL.read_bytes(), baseline=verifier.BASELINE.read_bytes())
        cls.recorded = load_json(cls.raw["baseline"])
        cls.science = {key: value for key, value in cls.recorded.items()
                       if key not in ("input_sha256", "implementation_sha256")}

    def test_changed_tokens_and_missing_exclusions_fail_before_analysis(self):
        for alteration in ("token", "missing_exclusion"):
            data = copy.deepcopy(self.packets)
            if alteration == "token":
                row = next(row for row in data["split"]["records"] if row["eligible"])
                row["tokens"][0] = "z" * len(row["tokens"][0])
            else:
                target = next(row for row in data["split"]["records"] if not row["eligible"])
                for packet in data.values():
                    row = next(row for row in packet["records"]
                               if (row["source_id"], row["locus_key"]) ==
                               (target["source_id"], target["locus_key"]))
                    packet["records"].remove(row)
                    packet["summary"]["records"] -= 1
                    packet["summary"]["excluded_records"] -= 1
                    for reason in row["exclusion_reasons"]:
                        counts = packet["summary"]["exclusion_reason_record_counts"]
                        counts[reason] -= 1
                        if not counts[reason]:
                            del counts[reason]
            raw = dict(self.raw, **{policy: encoded(packet) for policy, packet in data.items()})
            # These packets still pass the historical structure/protocol check.
            for policy, packet in data.items():
                engine.read_packet(packet, policy, load_json(self.raw["protocol"]))
            with self.subTest(alteration=alteration), patch.object(engine, "build_report") as analyze:
                with self.assertRaisesRegex(ValueError, "differs from the pinned producer"):
                    verifier.verify(raw)
                analyze.assert_not_called()

    def test_duplicate_cache_keys_are_not_silently_resolved(self):
        raw = dict(self.raw)
        raw["split"] = raw["split"].replace(b'{\n', b'{\n  "schema_version": 1,\n', 1)
        with patch.object(engine, "build_report") as analyze:
            with self.assertRaisesRegex(ValueError, "Duplicate JSON object key"):
                verifier.verify(raw)
            analyze.assert_not_called()

    def test_reformatted_cache_records_content_and_byte_identity_separately(self):
        raw = dict(self.raw)
        raw["split"] = encoded(self.packets["split"]).replace(b'  ', b'    ')
        with patch.object(engine, "build_report", return_value=self.science):
            original = verifier.verify(self.raw)
            reformatted = verifier.verify(raw)
        self.assertEqual(original["canonical_adapter_snapshot_sha256"],
                         reformatted["canonical_adapter_snapshot_sha256"])
        self.assertEqual(original["verified_scientific_report_sha256"],
                         reformatted["verified_scientific_report_sha256"])
        self.assertTrue(original["input_bytes_match_recorded_baseline"]["split"])
        self.assertFalse(reformatted["input_bytes_match_recorded_baseline"]["split"])
        self.assertNotEqual(original["input_sha256"]["split"], reformatted["input_sha256"]["split"])

    def test_historical_engine_protocol_and_changed_result_guards(self):
        for alteration, message in (("engine", "Historical engine bytes"),
                                    ("protocol", "Protocol bytes differ"),
                                    ("science", "baseline science differs")):
            raw = dict(self.raw)
            recorded = copy.deepcopy(self.recorded)
            if alteration == "engine":
                recorded["implementation_sha256"]["run_locus_position_baseline.py"] = "0" * 64
            elif alteration == "protocol":
                raw["protocol"] += b'\n'
            else:
                recorded["cohort"]["count"] += 1
            raw["baseline"] = encoded(recorded)
            with self.subTest(alteration=alteration), patch.object(engine, "build_report", return_value=self.science) as analyze:
                with self.assertRaisesRegex(ValueError, message):
                    verifier.verify(raw)
                if alteration != "science":
                    analyze.assert_not_called()

    def test_cli_receipt_cannot_replace_baseline_packets_or_sources(self):
        with tempfile.TemporaryDirectory() as temporary:
            paths = {name: Path(temporary) / (name + ".json") for name in self.raw}
            for name, path in paths.items():
                path.write_bytes(self.raw[name])
            targets = list(paths.values()) + [verifier.ROOT / "data/transliterations.json",
                                             verifier.ROOT / "data/raw/ZL3b-n.txt"]
            for destination in targets:
                before = destination.read_bytes()
                with self.subTest(destination=destination.name), patch.object(verifier, "verify") as replay:
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as errors:
                        status = verifier.main([argument for name, path in paths.items()
                                                for argument in ("--" + name, str(path))]
                                               + ["--output", str(destination)])
                self.assertEqual(status, 1)
                self.assertIn("must not replace", errors.getvalue())
                replay.assert_not_called()
                self.assertEqual(destination.read_bytes(), before)

    def test_cli_receipt_replays_and_rejects_changed_receipt(self):
        with tempfile.TemporaryDirectory() as temporary:
            paths = {name: Path(temporary) / (name + ".json") for name in self.raw}
            for name, path in paths.items():
                path.write_bytes(self.raw[name])
            arguments = [argument for name, path in paths.items() for argument in ("--" + name, str(path))]
            destination = Path(temporary) / "receipt.json"
            with patch.object(engine, "build_report", return_value=self.science), redirect_stdout(io.StringIO()):
                self.assertEqual(verifier.main(arguments + ["--output", str(destination)]), 0)
                self.assertEqual(verifier.main(arguments + ["--check", str(destination)]), 0)
                receipt = load_json(destination.read_bytes())
                receipt["cohort_locus_count"] += 1
                destination.write_bytes(encoded(receipt))
                with redirect_stderr(io.StringIO()) as errors:
                    self.assertEqual(verifier.main(arguments + ["--check", str(destination)]), 1)
            self.assertIn("receipt differs", errors.getvalue())

    def test_receipt_rejects_script_targets_and_hardlink_input_aliases(self):
        with tempfile.TemporaryDirectory() as temporary:
            paths = {name: Path(temporary) / (name + ".json") for name in self.raw}
            for name, path in paths.items():
                path.write_bytes(self.raw[name])
            arguments = [argument for name, path in paths.items() for argument in ("--" + name, str(path))]
            protected = [*paths.values(), verifier.ROOT / "data/transliterations.json",
                         verifier.ROOT / "data/raw/ZL3b-n.txt", verifier.ROOT / "scripts/ivtff.py"]
            targets = [verifier.ROOT / "scripts/run_locus_position_baseline.py"]
            for index, source in enumerate(protected):
                alias = Path(temporary) / f"hardlink-{index}.json"
                os.link(source, alias)
                targets.append(alias)
            for destination in targets:
                before = destination.read_bytes()
                with self.subTest(destination=destination.name), patch.object(verifier, "verify") as replay:
                    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                        status = verifier.main(arguments + ["--output", str(destination)])
                self.assertEqual(status, 1)
                replay.assert_not_called()
                self.assertEqual(destination.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
