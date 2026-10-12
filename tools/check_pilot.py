#!/usr/bin/env python3
"""Validate pilot selection and metadata against a saved Yale IIIF manifest.

Uses the standard library, makes no network requests, and does not verify the
semantic accuracy of visual descriptions. Optional image checks verify bytes.
"""

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"


def label(canvas):
    values = [value for group in canvas["label"].values() for value in group]
    if len(values) != 1:
        raise ValueError("Expected one unambiguous label per canvas")
    return values[0]


def select(manifest):
    if manifest["id"] != MANIFEST_URL:
        raise ValueError("Unexpected manuscript manifest")
    rectos = {}
    for canvas in manifest["items"]:
        match = re.fullmatch(r"(\d+)r", label(canvas))
        if match:
            number = int(match[1])
            if number in rectos:
                raise ValueError(f"Duplicate standalone recto: {number}")
            rectos[number] = canvas
    selected = []
    for part, low, high in [("I", 1, 66), ("II", 67, 73),
                            ("III", 75, 84), ("V", 87, 102)]:
        candidates = sorted(n for n in rectos if low <= n <= high)
        if len(candidates) < 2:
            raise ValueError(f"Missing boundary rectos in Part {part}")
        selected.extend([(part, rectos[candidates[0]]), (part, rectos[candidates[-1]])])
    foldouts = [c for c in manifest["items"] if label(c) == "85v and 86r (foldout)"]
    if len(foldouts) != 1:
        raise ValueError("Missing or ambiguous cosmological foldout")
    selected.insert(6, ("IV", foldouts[0]))
    final = sorted(n for n in rectos if 103 <= n <= 117)
    if not final:
        raise ValueError("Missing Part VI rectos")
    selected.append(("VI", rectos[final[0]]))
    return selected


def check(manifest_path, inventory_path, images):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    with inventory_path.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    if len(rows) != 10 or len({row["canvas_id"] for row in rows}) != 10:
        raise ValueError("Expected ten records with unique canvas identifiers")
    for row, (part, canvas) in zip(rows, select(manifest)):
        image = canvas["items"][0]["items"][0]["body"]
        oid = canvas["id"].rsplit("/", 1)[-1]
        service = image["service"][0]["@id"]
        expected = {
            "yale_label": label(canvas), "catalog_part": part,
            "image_oid": oid, "canvas_id": canvas["id"],
            "catalog_image_url": f"https://collections.library.yale.edu/catalog/2002046?child_oid={oid}",
            "full_image_url": image["id"],
            "inspection_image_url": service + "/full/!1600,1600/0/default.jpg",
            "source_width": str(canvas["width"]), "source_height": str(canvas["height"]),
            "section_source": "S002", "metadata_source": "S004",
            "observation_source": "S003 image " + oid,
        }
        for key, value in expected.items():
            if row.get(key) != value:
                raise ValueError(f"{label(canvas)}: {key} differs from selection/manifest")
        for key in ["inspected_on", "text_layout_observed", "illustration_observed",
                    "uncertainty", "interpretation"]:
            if not row.get(key, "").strip():
                raise ValueError(f"{label(canvas)}: missing {key}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", row["inspected_on"]):
            raise ValueError(f"{label(canvas)}: invalid inspection date format")
        if not re.fullmatch(r"[0-9a-f]{64}", row["inspection_sha256"]):
            raise ValueError(f"{label(canvas)}: invalid image digest format")
        if images:
            digest = hashlib.sha256((images / (oid + ".jpg")).read_bytes()).hexdigest()
            if digest != row["inspection_sha256"]:
                raise ValueError(f"{label(canvas)}: inspected JPEG digest differs")
    print("PASS: ten records match the selection rule and Yale manifest metadata.")
    if images:
        print("PASS: all ten inspected JPEG digests match.")
    print("Visual descriptions and live link availability require separate review.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--inventory", type=Path,
                        default=ROOT / "research/data/pilot-folios.csv")
    parser.add_argument("--images", type=Path, help="Directory of IMAGE_OID.jpg derivatives")
    args = parser.parse_args()
    try:
        check(args.manifest, args.inventory, args.images)
    except (ValueError, KeyError, TypeError, IndexError, OSError) as error:
        parser.exit(1, f"FAIL: {error}\n")
