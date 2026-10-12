"""Coverage regressions: scientific scope, foldouts, queue claims and replay."""

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = Path("scripts/build_manuscript_coverage.py")
spec = importlib.util.spec_from_file_location("manuscript_coverage", ROOT / SCRIPT)
coverage = importlib.util.module_from_spec(spec)
spec.loader.exec_module(coverage)


class ManuscriptCoverageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        report = coverage.build(ROOT)
        for relative in [SCRIPT, *report["input_sha256"]]:
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, destination)

    def registry(self, filename, mutate):
        path = self.root / "research/coverage" / filename
        data = json.loads(path.read_text())
        mutate(data)
        path.write_text(json.dumps(data) + "\n")

    def cli(self, mode):
        return subprocess.run([sys.executable, str(self.root / SCRIPT), mode],
                              capture_output=True, text=True)

    def test_denominators_and_shared_rosette_are_not_independent_pages(self):
        report = coverage.build(self.root)
        summary = report["summary"]
        self.assertEqual(summary["indexed_folio_sides"], 204)
        self.assertEqual(summary["indexed_canvases"], 213)
        self.assertEqual(summary["non_numbered_views"], 9)
        self.assertEqual(summary["transcription_page_ids"], 227)
        self.assertEqual(summary["unresolved_transcription_panel_ids"], 43)
        self.assertEqual(sum(p["page_id"] == "fRos" for p in report["transcription_pages"]), 1)
        sides = {r["folio_side"]: r for r in report["folio_sides"]}
        for side in ("85v", "86r"):
            self.assertIn("fRos", sides[side]["transcription_page_ids"])
            self.assertIn("yale-leaves:85+86", sides[side]["dependency_groups"])
            self.assertFalse(sides[side]["full_image_text_review_recorded"])
        self.assertEqual(sides["85v"]["canvases"], sides["86r"]["canvases"])
        self.assertEqual(len(sides["70v"]["canvases"]), 2)
        self.assertIn("f116v", sides["116v"]["transcription_page_ids"])
        self.assertNotIn("117v", sides)

    def test_existing_partial_reviews_do_not_claim_completion_or_independence(self):
        report = coverage.build(self.root)
        self.assertEqual(report["summary"]["full_image_text_reviews_recorded"], 0)
        self.assertEqual(report["summary"]["active_owned_tasks"], 0)
        sides = {r["folio_side"]: r for r in report["folio_sides"]}
        self.assertEqual(sides["76r"]["stages"]["image_text_alignment"], "partial")
        self.assertEqual(sides["76r"]["stages"]["independent_review"], "not_recorded")
        self.assertTrue(all(r["stages"]["validated_translation"] == "not_recorded"
                            for r in report["folio_sides"]))

    def test_done_task_does_not_complete_a_scientific_stage(self):
        self.registry("tasks.json", lambda d: d["tasks"][0].update(status="done"))
        report = coverage.build(self.root)
        self.assertEqual(report["summary"]["full_image_text_reviews_recorded"], 0)
        row = next(r for r in report["folio_sides"] if r["folio_side"] == "67r")
        self.assertEqual(row["stages"]["image_text_alignment"], "partial")

    def test_selected_regions_cannot_be_declared_whole_folio_complete(self):
        self.registry("evidence.json", lambda d: d["entries"][0].update(status="complete"))
        with self.assertRaisesRegex(ValueError, "cannot complete"):
            coverage.build(self.root)

    def test_independent_stage_requires_an_explicit_independence_statement(self):
        self.registry("evidence.json", lambda d: d["entries"][0].update(stage="independent_review"))
        with self.assertRaisesRegex(ValueError, "independence statement"):
            coverage.build(self.root)

    def test_explicit_whole_folio_evidence_can_record_a_completed_review(self):
        def complete(data):
            template = data["entries"][0].copy()
            for stage in ("image_text_alignment", "independent_review"):
                data["entries"].append(dict(template, id="test-" + stage, stage=stage,
                                            status="complete", scope="whole_folio",
                                            independence_statement="Synthetic test declaration only."))
        self.registry("evidence.json", complete)
        report = coverage.build(self.root)
        self.assertEqual(report["summary"]["full_image_text_reviews_recorded"], 1)

    def test_active_task_needs_an_owner(self):
        self.registry("tasks.json", lambda d: d["tasks"][0].update(status="in_progress"))
        with self.assertRaisesRegex(ValueError, "needs an owner"):
            coverage.build(self.root)

    def test_unknown_sides_and_duplicate_tasks_are_rejected(self):
        self.registry("tasks.json", lambda d: d["tasks"][0].update(folio_sides=["117v"]))
        with self.assertRaisesRegex(ValueError, "unknown side"):
            coverage.build(self.root)
        self.registry("tasks.json", lambda d: d["tasks"][0].update(folio_sides=["67r"]))
        self.registry("tasks.json", lambda d: d["tasks"].append(d["tasks"][0].copy()))
        with self.assertRaisesRegex(ValueError, "unique"):
            coverage.build(self.root)

    def test_missing_or_external_evidence_is_rejected(self):
        self.registry("evidence.json", lambda d: d["entries"][0].update(references=["../outside.json"]))
        with self.assertRaisesRegex(ValueError, "inside the repository"):
            coverage.build(self.root)
        self.registry("evidence.json", lambda d: d["entries"][0].update(references=["research/not-present.json"]))
        with self.assertRaises(FileNotFoundError):
            coverage.build(self.root)

    def test_generated_reports_cannot_be_used_as_evidence(self):
        self.assertEqual(self.cli("--write").returncode, 0)
        self.registry("evidence.json", lambda d: d["entries"][0].update(
            references=["research/coverage/coverage.json"]))
        with self.assertRaisesRegex(ValueError, "cannot be evidence"):
            coverage.build(self.root)

    def test_offline_replay_and_stale_detection_include_evidence_bytes(self):
        self.assertEqual(self.cli("--write").returncode, 0)
        self.assertEqual(self.cli("--check").returncode, 0)
        evidence = self.root / "research/pilot/f76r-second-row-check.json"
        evidence.write_text(evidence.read_text() + "\n")
        stale = self.cli("--check")
        self.assertNotEqual(stale.returncode, 0)
        self.assertIn("Stale", stale.stderr)
        self.assertEqual(self.cli("--write").returncode, 0)
        self.assertEqual(self.cli("--check").returncode, 0)
        # Both human and machine outputs must be checked.
        status = self.root / "research/coverage/STATUS.md"
        status.write_text(status.read_text() + "edited\n")
        self.assertNotEqual(self.cli("--check").returncode, 0)

    def test_write_rejects_output_symlink_to_evidence_without_overwriting_input(self):
        source = self.root / "research/pilot/f76r-anchor-review.json"
        before = source.read_bytes()
        for output in coverage.OUTPUTS:
            (self.root / output).symlink_to(source)
        self.assertNotEqual(self.cli("--write").returncode, 0)
        self.assertEqual(source.read_bytes(), before)

    def test_write_replaces_unrelated_output_symlinks_without_following_them(self):
        target = self.root / "unrelated.txt"
        target.write_text("preserve this file")
        for output in coverage.OUTPUTS:
            (self.root / output).symlink_to(target)
        self.assertEqual(self.cli("--write").returncode, 0)
        self.assertEqual(target.read_text(), "preserve this file")
        self.assertTrue(all(not (self.root / output).is_symlink() for output in coverage.OUTPUTS))


if __name__ == "__main__":
    unittest.main()
