#!/usr/bin/env python3
"""Check the pilot's selection and source metadata against a Yale IIIF manifest.

This verifies identifiers, not the accuracy of visual observations. Uses only
the Python standard library and does not modify the inventory.
"""

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path


RANGES = [(1, 66, 2), (67, 73, 2), (75, 84, 2), (87, 102, 2), (103, 117, 1)]


def label(canvas):
    return canvas["label"]["none"][0]


def select(canvases):
    selected = []
    for lower, upper, count in RANGES:
        eligible = []
        for canvas in canvases:
            match = re.fullmatch(r"([0-9]+)r", label(canvas))
            if match and lower <= int(match[1]) <= upper:
                eligible.append((int(match[1]), canvas))
        eligible.sort(key=lambda pair: pair[0])
        if len(eligible) < count:
            raise ValueError(f"Insufficient recto canvases in {lower}-{upper}")
        numbers = [number for number, _ in eligible]
        if len(numbers) != len(set(numbers)):
            raise ValueError(f"Ambiguous duplicate recto labels in {lower}-{upper}")
        selected.extend(canvas for _, canvas in eligible[:count])
    foldouts = [c for c in canvases if label(c) == "85v and 86r (foldout)"]
    if len(foldouts) != 1:
        raise ValueError("Expected one exact 85v and 86r foldout label")
    selected.insert(6, foldouts[0])
    return selected


def verify_image_bytes(records, directory):
    """Retain the superseded pilot validator's optional local JPEG check."""
    for record in records:
        image_id = record["image_id"]
        if not re.fullmatch(r"[0-9]+", image_id):
            raise ValueError("Invalid image ID for local checksum verification")
        digest = hashlib.sha256((directory / f"{image_id}.jpg").read_bytes()).hexdigest()
        if digest != record["inspection_sha256"]:
            raise ValueError(f"{record['target']}: inspected JPEG checksum differs")


def write_inventory_csv(records, output):
    """Export the canonical records, retaining structured fields as JSON cells."""
    fields = list(records[0])
    if any(set(record) != set(fields) for record in records):
        raise ValueError("Inventory records have inconsistent fields")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for record in records:
        writer.writerow({key: json.dumps(value, ensure_ascii=False)
                         if isinstance(value, (dict, list)) else value
                         for key, value in record.items()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--inventory", type=Path,
                        default=Path(__file__).resolve().parents[1] / "research/pilot/inventory.json")
    parser.add_argument("--images", type=Path,
                        help="Optionally verify local IMAGE_ID.jpg inspection bytes")
    parser.add_argument("--csv", action="store_true",
                        help="Write canonical inventory CSV to stdout; status goes to stderr")
    args = parser.parse_args()
    manifest_bytes = args.manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    inventory = json.loads(args.inventory.read_text())
    chosen = select(manifest["items"])
    records = inventory["records"]
    if len(records) != 10:
        raise ValueError(f"Expected 10 records, found {len(records)}")
    if [r["yale_label"] for r in records] != [label(c) for c in chosen]:
        raise ValueError("Inventory labels/order differ from the selection rule")
    seen_ids = set()
    for record, canvas in zip(records, chosen):
        body = canvas["items"][0]["items"][0]["body"]
        oid = canvas["id"].rsplit("/", 1)[1]
        service = body["service"][0]["@id"]
        expected = {
            "image_id": oid,
            "canvas_uri": canvas["id"],
            "catalog_image_url": f"https://collections.library.yale.edu/catalog/2002046?child_oid={oid}",
            "full_image_url": body["id"],
            "inspection_image_url": f"{service}/full/!1800,1800/0/default.jpg",
            "source_width": body["width"],
            "source_height": body["height"],
        }
        for key, value in expected.items():
            if record[key] != value:
                raise ValueError(f"{record['target']}: {key} differs from manifest")
        if oid in seen_ids:
            raise ValueError(f"Duplicate image ID: {oid}")
        seen_ids.add(oid)
        if not re.fullmatch(r"[a-f0-9]{64}", record["inspection_sha256"]):
            raise ValueError(f"{record['target']}: invalid inspection checksum")
        for key in ("observed_text_layout", "observed_illustration", "uncertainties"):
            if not record[key]:
                raise ValueError(f"{record['target']}: empty {key}")
    if args.images:
        verify_image_bytes(records, args.images)
    if args.csv:
        write_inventory_csv(records, sys.stdout)
    status = sys.stderr if args.csv else sys.stdout
    digest = hashlib.sha256(manifest_bytes).hexdigest()
    print("PASS: 10 selected canvases; labels, identifiers, URLs, dimensions, and required observation fields agree.", file=status)
    print(f"Manifest SHA-256: {digest}", file=status)
    if digest != inventory["manifest_sha256"]:
        print("NOTE: Manifest bytes differ from the inspected version; selected metadata still agrees.", file=status)
    if args.images:
        print("PASS: all ten local JPEG checksums match the recorded inspection bytes.", file=status)
    else:
        print("Image-file checksums were not checked; use --images for local verification.", file=status)
    print("Visual descriptions still require separate inspection.", file=status)


if __name__ == "__main__":
    main()
