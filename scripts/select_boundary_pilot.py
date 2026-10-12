#!/usr/bin/env python3
"""Resolve the documented pilot targets against Yale's IIIF v3 manifest.

Uses only Python's standard library. Downloads metadata, never image files.
"""

import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path


MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
TARGETS = (
    ("1r", "I"), ("66r", "I"), ("67r", "II"), ("73r", "II"),
    ("75r", "III"), ("84r", "III"), ("86r", "IV"),
    ("87r", "V"), ("102r", "V"), ("103r", "VI"),
)


def resolve(raw):
    manifest = json.loads(raw)
    if manifest.get("id") != MANIFEST_URL or manifest.get("type") != "Manifest":
        raise ValueError("Expected Yale's IIIF v3 manifest for object 2002046")
    canvases = manifest["items"]
    entries = []
    for target, part in TARGETS:
        candidates = []
        for index, canvas in enumerate(canvases):
            labels = [label for values in canvas["label"].values() for label in values]
            if len(labels) != 1:
                raise ValueError("Multiple canvas labels require manual review")
            label = labels[0]
            if target == "86r":
                matches = label == "85v and 86r (foldout)"
            else:
                matches = bool(re.search(r"(?<![\w])" + re.escape(target) + r"(?![\w])", label))
            if matches:
                candidates.append((index, canvas, label))
        if not candidates:
            raise ValueError(f"No matching canvas for {target}")
        exact = [candidate for candidate in candidates if candidate[2] == target]
        index, canvas, label = (exact or candidates)[0]
        annotations = [a for page in canvas["items"] for a in page["items"]
                       if a.get("motivation") == "painting"]
        if len(annotations) != 1 or annotations[0]["body"].get("type") != "Image":
            raise ValueError(f"Unexpected image arrangement for {target}")
        body = annotations[0]["body"]
        entries.append({
            "target_folio": target,
            "catalog_part": part,
            "canvas_index": index,
            "canvas_label": label,
            "canvas_id": canvas["id"],
            "image_id": body["id"],
            "image_service": body["service"][0]["@id"],
            "width": body["width"],
            "height": body["height"],
        })
    return {
        "manifest_url": MANIFEST_URL,
        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
        "manifest_canvas_count": len(canvases),
        "selection_protocol": "research/boundary-pilot/PROTOCOL.md",
        "entries": entries,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, help="Read a saved manifest instead of downloading")
    parser.add_argument("--output", type=Path, help="Write the selection JSON to this path")
    parser.add_argument("--check", type=Path, help="Fail if selection differs from saved JSON")
    args = parser.parse_args()
    if args.manifest:
        raw = args.manifest.read_bytes()
    else:
        with urllib.request.urlopen(MANIFEST_URL, timeout=60) as response:
            raw = response.read()
    selection = resolve(raw)
    if args.check:
        if selection != json.loads(args.check.read_text()):
            raise SystemExit("Selection or manifest fingerprint changed; review before updating")
        print("Verified all 10 target mappings and manifest fingerprint")
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(selection, indent=2) + "\n")
    if not args.output and not args.check:
        print(json.dumps(selection, indent=2))


if __name__ == "__main__":
    main()
