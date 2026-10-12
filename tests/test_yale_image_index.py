"""Check ambiguous folio mappings and reject source arrangements we cannot resolve."""

import copy
import importlib.util
import json
from pathlib import Path
import unittest


SPEC = importlib.util.spec_from_file_location(
    "image_index", Path(__file__).resolve().parents[1] / "scripts" / "index_yale_manifest.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def canvas(label, oid):
    uri = f"{MODULE.MANIFEST_URL}/canvas/{oid}"
    service = f"https://collections.library.yale.edu/iiif/2/{oid}"
    return {
        "id": uri, "type": "Canvas", "label": {"none": [label]},
        "items": [{"items": [{"motivation": "painting", "target": uri, "body": {
            "type": "Image", "id": service + "/full/full/0/default.jpg",
            "service": [{"@id": service}], "width": 100, "height": 200,
        }}]}],
    }


def encoded(canvases):
    return json.dumps({"id": MODULE.MANIFEST_URL, "type": "Manifest", "items": canvases}).encode()


class MappingTests(unittest.TestCase):
    def test_shared_view_maps_to_both_sides_without_counting_two_canvases(self):
        output = MODULE.build(encoded([canvas("85v and 86r (foldout)", 1)]), "2026-10-11")
        self.assertEqual(output["audit.json"]["canvas_count"], 1)
        self.assertEqual([row["folio_side"] for row in output["folio-sides.csv"]], ["85v", "86r"])
        self.assertTrue(all(row["has_shared_view"] for row in output["folio-sides.csv"]))
        self.assertTrue(all(not row["has_exact_side_label"] for row in output["folio-sides.csv"]))

    def test_repeated_partial_labels_preserve_all_images(self):
        output = MODULE.build(encoded([canvas("70v (part)", 1), canvas("70v (part)", 2)]), "2026-10-11")
        side = output["folio-sides.csv"][0]
        self.assertEqual(side["canvas_count"], 2)
        self.assertEqual(side["image_oids"], "1;2")
        self.assertTrue(side["has_partial_view"])

    def test_foldout_number_range_does_not_invent_sides(self):
        self.assertEqual(MODULE.folio_sides("85r (part) (part of 85-86 foldout)"), ["85r"])
        self.assertEqual(MODULE.folio_sides("[Back flyleaf recto]"), [])
        self.assertEqual(MODULE.folio_sides("x85r 185r 85rx"), ["185r"])

    def test_exact_view_and_shared_view_both_retained(self):
        output = MODULE.build(encoded([
            canvas("89v (part) and 90r", 1), canvas("90r", 2), canvas("[Front cover]", 3)
        ]), "2026-10-11")
        side = next(row for row in output["folio-sides.csv"] if row["folio_side"] == "90r")
        self.assertEqual(side["image_oids"], "1;2")
        self.assertTrue(side["has_exact_side_label"])
        self.assertEqual(output["audit.json"]["non_numbered_views"][0]["image_oid"], "3")

    def test_duplicate_canvas_and_ambiguous_painting_fail(self):
        original = canvas("1r", 1)
        with self.assertRaisesRegex(ValueError, "Duplicate canvas"):
            MODULE.build(encoded([original, original]), "2026-10-11")
        changed = copy.deepcopy(original)
        changed["items"][0]["items"].append(changed["items"][0]["items"][0])
        with self.assertRaisesRegex(ValueError, "painting arrangement"):
            MODULE.build(encoded([changed]), "2026-10-11")

    def test_different_object_or_label_convention_requires_review(self):
        raw = json.loads(encoded([canvas("1r", 1)]))
        raw["id"] = "https://example.org/other-object"
        with self.assertRaisesRegex(ValueError, "Expected Yale"):
            MODULE.build(json.dumps(raw).encode(), "2026-10-11")
        changed = canvas("1r", 1)
        changed["label"] = {"en": ["1r"]}
        with self.assertRaisesRegex(ValueError, "language-map label"):
            MODULE.build(encoded([changed]), "2026-10-11")


if __name__ == "__main__":
    unittest.main()
