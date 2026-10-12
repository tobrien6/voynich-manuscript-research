#!/usr/bin/env python3
"""Check pilot identifiers and optional local Yale source files; no network I/O."""

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "research" / "pilot"
SECTION_RULES = [
    ("I", 1, 66, 2), ("II", 67, 73, 2), ("III", 75, 84, 2),
    ("IV", 85, 86, 1), ("V", 87, 102, 2), ("VI", 103, 117, 1),
]
METADATA_FIELDS = (
    "target_folio", "manifest_label", "canvas_index", "image_oid", "canvas_uri",
    "viewer_url", "image_url", "inspection_url", "source_width", "source_height",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest_selection(manifest):
    """Reapply SAMPLING.md to labels, without inspecting image content."""
    canvases = manifest["items"]
    selected = []
    for section, lower, upper, count in SECTION_RULES:
        if section == "IV":
            matches = [c for c in canvases
                       if c["label"].get("none") == ["85v and 86r (foldout)"]]
            require(len(matches) == 1, "Shared cosmological foldout label is missing or ambiguous")
            selected.append(matches[0])
            continue
        candidates = []
        for canvas in canvases:
            labels = canvas["label"].get("none", [])
            match = re.fullmatch(r"(\d+)r", labels[0]) if len(labels) == 1 else None
            if match and lower <= int(match[1]) <= upper:
                candidates.append((int(match[1]), canvas))
        candidates.sort(key=lambda pair: pair[0])
        require(len(candidates) >= count, f"Too few exactly labeled rectos in section {section}")
        chosen = candidates[:count]
        require(len({number for number, _ in chosen}) == count,
                f"Ambiguous recto labels in section {section}")
        selected.extend(canvas for _, canvas in chosen)
    return selected


def validate(args):
    with (PILOT / "inventory.csv").open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    provenance = json.loads((PILOT / "PROVENANCE.json").read_text(encoding="utf-8"))
    images = provenance["images"]
    require(len(rows) == len(images) == 10, "Expected exactly ten rows and ten provenance images")
    for field in ("target_folio", "image_oid", "canvas_uri"):
        require(len({row[field] for row in rows}) == 10, f"Duplicate {field}")
    require(Counter(row["section_id"] for row in rows) ==
            Counter({section: count for section, _, _, count in SECTION_RULES}),
            "Section allocation differs from the sampling protocol")
    for row, image in zip(rows, images):
        require(all(value.strip() for value in row.values()), f"Blank field in {row['target_folio']}")
        for field in METADATA_FIELDS:
            require(row[field] == str(image[field]), f"CSV/provenance mismatch: {row['target_folio']} {field}")
        oid = row["image_oid"]
        require(row["viewer_url"] == f"https://collections.library.yale.edu/catalog/2002046?child_oid={oid}",
                f"Unexpected viewer link for {oid}")
        require(re.fullmatch(r"[0-9a-f]{64}", image["inspection_sha256"]), f"Invalid JPEG hash for {oid}")
    require(re.fullmatch(r"[0-9a-f]{64}", provenance["manifest_sha256"]), "Invalid manifest hash")
    if args.manifest:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        if sha256(args.manifest) != provenance["manifest_sha256"]:
            print("NOTE: manifest bytes changed; checking selected metadata against the new response.")
        selected = manifest_selection(manifest)
        for row, canvas in zip(rows, selected):
            require(canvas["label"]["none"] == [row["manifest_label"]], f"Selection changed for {row['target_folio']}")
            require(canvas["id"] == row["canvas_uri"], f"Canvas changed for {row['target_folio']}")
            require(manifest["items"][int(row["canvas_index"])]["id"] == canvas["id"],
                    f"Canvas ordering changed for {row['target_folio']}")
            for axis in ("width", "height"):
                require(canvas[axis] == int(row[f"source_{axis}"]), f"Source {axis} changed for {row['target_folio']}")
            body = canvas["items"][0]["items"][0]["body"]
            require(body["id"] == row["image_url"], f"Image URL changed for {row['target_folio']}")
            service = body["service"][0]["@id"]
            require(row["inspection_url"] == service + "/full/!1800,1800/0/default.jpg",
                    f"Inspection URL mismatch for {row['target_folio']}")
    if args.images:
        for image in images:
            path = args.images / (image["image_oid"] + ".jpg")
            require(sha256(path) == image["inspection_sha256"], f"Inspected JPEG bytes differ: {path.name}")
    print("PASS: ten unique targets, six section allocations, and consistent CSV/provenance metadata.")
    if args.manifest:
        print("PASS: deterministic selection, canvas labels/order, source dimensions, and image URLs match manifest.")
    if args.images:
        print("PASS: all ten local JPEG checksums match the inspected derivatives.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, help="Optional downloaded Yale IIIF manifest")
    parser.add_argument("--images", type=Path, help="Optional directory containing IMAGE_OID.jpg files")
    args = parser.parse_args()
    try:
        validate(args)
    except (ValueError, KeyError, IndexError, OSError, TypeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
