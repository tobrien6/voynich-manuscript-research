"""Cross-component checks; all source and manifest fixtures are synthetic."""

from collections import Counter, defaultdict
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.align_folio_canvases import align
from scripts.eva_token_adapter import adapt
from scripts.ivtff import parse_ivtff
from scripts.shuffle_token_lines import make_control


ROOT = Path(__file__).resolve().parents[1]
SOURCE = """#=IVTFF Eva- 2.0 M
<f1r>
<f1r.1,@P0> ab,cd.ef
<f1r.2,+P0> [x:y].a
<f2r>
<f2r.1,@P0> a.b.b
<f67r1>
<f67r1.1,@P0> x.y.z
<f117v>
<f117v.1,@P0> aa.bb
"""


def manifest_fixture():
    # Yale-shaped metadata tests the accepted parser, without claiming real views.
    canvases = []
    for index, label in enumerate(("1r (part)", "1r (part)", "2r and 3v"), 1):
        oid = str(index)
        uri = f"https://collections.library.yale.edu/manifests/oid/2002046/canvas/{oid}"
        service = f"https://collections.library.yale.edu/iiif/2/{oid}"
        canvases.append({
            "id": uri, "type": "Canvas", "label": {"none": [label]},
            "items": [{"items": [{"motivation": "painting", "target": uri, "body": {
                "type": "Image", "id": service + "/full/full/0/default.jpg",
                "service": [{"@id": service}], "width": 100, "height": 200,
            }}]}],
        })
    return json.dumps({"id": "https://collections.library.yale.edu/manifests/2002046",
                       "type": "Manifest", "items": canvases}).encode()


def corpus_fixture(records, matches, spacing):
    """Assemble declared test input, not a new production exporter or mapper."""
    lines, associations = [], {}
    for record in records:
        entry = matches[record["page_id"]]
        if not record["eligible"] or entry["status"] != "matched":
            continue
        lines.append({"folio_side": entry["canonical_folio_side"],
                      "line_id": record["locus_identifier"], "tokens": record["tokens"],
                      "context": f"Synthetic source {record['source_id']}; original page {record['page_id']}"})
        associations[record["page_id"]] = entry["matches"]
    return {
        "schema_version": 1, "corpus_id": "synthetic-adapter-resolver-controls",
        "provenance": {"kind": "synthetic", "description": "Cross-component API fixture; no manuscript transcription or image mapping",
                       "tokenization": f"Conservative adapter with {spacing} uncertain spaces; whole excluded loci omitted explicitly",
                       "unit_definition": "Each retained row is an IVTFF locus, not a reconstructed physical line",
                       "source_id": "fixture", "image_associations": associations},
        "lines": lines,
    }


class TokenPipelineContractTests(unittest.TestCase):
    def test_adapter_resolver_and_controls_preserve_identity_and_every_view(self):
        for spacing in ("split", "join"):
            records = adapt({"id": "fixture"}, parse_ivtff(SOURCE), spacing, ("P0",))
            pages = list(dict.fromkeys(record["page_id"] for record in records))
            joined = align(manifest_fixture(), pages, "2026-10-11")
            matches = {entry["requested_identifier"]: entry for entry in joined["entries"]}
            self.assertEqual(matches["f67r1"]["status"], "unsupported_identifier")
            self.assertEqual(matches["f117v"]["status"], "label_unmatched")
            self.assertEqual(len(matches["f1r"]["matches"]), 2)
            self.assertTrue(all(view["partial_view"] for view in matches["f1r"]["matches"]))
            self.assertTrue(matches["f2r"]["matches"][0]["combined_view"])
            corpus = corpus_fixture(records, matches, spacing)
            self.assertEqual([line["line_id"] for line in corpus["lines"]], ["f1r.1,@P0", "f2r.1,@P0"])
            for scope in ("line", "folio-side"):
                control = make_control(json.dumps(corpus).encode(), scope, 1729, 0)
                self.assertEqual(control["provenance"], corpus["provenance"])
                self.assertEqual([(line["folio_side"], line["line_id"]) for line in control["lines"]],
                                 [(line["folio_side"], line["line_id"]) for line in corpus["lines"]])
                for original, permuted in zip(corpus["lines"], control["lines"]):
                    self.assertEqual(Counter(original["tokens"]), Counter(permuted["tokens"]))

    def test_whole_locus_exclusion_is_not_a_single_masked_slot(self):
        records = adapt({"id": "fixture"}, parse_ivtff(SOURCE), "split", ("P0",))
        excluded = records[1]
        self.assertFalse(excluded["eligible"])
        self.assertIsNone(excluded["tokens"])
        joined = align(manifest_fixture(), ["f1r"], "2026-10-11")
        matches = {entry["requested_identifier"]: entry for entry in joined["entries"]}
        corpus = corpus_fixture(records[:2], matches, "split")
        bad = copy.deepcopy(corpus)
        bad["lines"].append({"folio_side": "1r", "line_id": excluded["locus_identifier"], "tokens": excluded["tokens"]})
        with self.assertRaisesRegex(ValueError, "Tokens must be a list"):
            make_control(json.dumps(bad).encode(), "line", 1729, 0)

    def test_declared_slot_masks_and_side_multisets_survive_both_control_scopes(self):
        records = adapt({"id": "fixture"}, parse_ivtff(SOURCE), "split", ("P0",))
        joined = align(manifest_fixture(), ["f1r", "f2r"], "2026-10-11")
        matches = {entry["requested_identifier"]: entry for entry in joined["entries"]}
        corpus = corpus_fixture([records[0], records[2]], matches, "split")
        # Current conservative adapter excludes whole uncertain loci. These are
        # explicitly introduced synthetic slots for the controller's gap contract.
        corpus["provenance"]["tokenization"] = "Synthetic eligible slots with explicitly fixed null exclusions"
        corpus["lines"][0]["tokens"].insert(1, None)
        corpus["lines"].append({"folio_side": "1r", "line_id": "synthetic-extra-locus", "tokens": ["g", None, "h"]})
        def bags(lines):
            result = defaultdict(Counter)
            for line in lines:
                result[line["folio_side"]].update(token for token in line["tokens"] if token is not None)
            return result
        for scope in ("line", "folio-side"):
            control = make_control(json.dumps(corpus).encode(), scope, 1729, 0)
            self.assertEqual(bags(control["lines"]), bags(corpus["lines"]))
            for original, permuted in zip(corpus["lines"], control["lines"]):
                self.assertEqual([token is None for token in original["tokens"]], [token is None for token in permuted["tokens"]])
                self.assertEqual(len(original["tokens"]), len(permuted["tokens"]))

    def test_fresh_package_import_and_cli_use_the_same_resolver(self):
        imported = subprocess.run([sys.executable, "-c", "from scripts.align_folio_canvases import align; assert callable(align)"],
                                  cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(imported.returncode, 0, imported.stderr)
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.json"
            manifest.write_bytes(manifest_fixture())
            result = subprocess.run([sys.executable, str(ROOT / "scripts" / "align_folio_canvases.py"), str(manifest),
                                     "f1r", "--access-date", "2026-10-11"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), align(manifest_fixture(), ["f1r"], "2026-10-11"))
            packaged = subprocess.run([sys.executable, "-m", "scripts.align_folio_canvases", str(manifest),
                                        "f1r", "--access-date", "2026-10-11"], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(packaged.returncode, 0, packaged.stderr)
            self.assertEqual(json.loads(packaged.stdout), json.loads(result.stdout))


if __name__ == "__main__":
    unittest.main()
