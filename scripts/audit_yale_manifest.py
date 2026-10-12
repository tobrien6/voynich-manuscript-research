#!/usr/bin/env python3
"""Audit numbered references in a saved Yale IIIF Presentation 3 manifest.

This reads image labels, not manuscript text or physical collation.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re


FOLIO_REFERENCE = re.compile(r"(?<![A-Za-z0-9])(\d+)([rv])(?=$|[^A-Za-z0-9])")


def label_text(label):
    """Choose one language value without merging alternative translations."""
    if not isinstance(label, dict) or not label:
        raise ValueError("Canvas label must be a nonempty IIIF language map")
    language = next((key for key in ("none", "en") if key in label), sorted(label)[0])
    values = label[language]
    if not isinstance(values, list) or len(values) != 1 or not isinstance(values[0], str):
        raise ValueError("Expected exactly one string in the selected label language")
    return values[0]


def audit(raw, retrieved_at):
    manifest = json.loads(raw)
    if manifest.get("type") != "Manifest" or not isinstance(manifest.get("items"), list):
        raise ValueError("Expected a IIIF Presentation 3 Manifest with an items array")
    canvases = manifest["items"]
    rows = []
    for index, canvas in enumerate(canvases):
        if canvas.get("type") != "Canvas":
            raise ValueError(f"Manifest item {index} is not a Canvas")
        label = label_text(canvas["label"])
        references = [(int(number), side) for number, side in FOLIO_REFERENCE.findall(label)]
        rows.append({
            "canvas_index": index,
            "canvas_uri": canvas["id"],
            "label": label,
            "folio_references": [f"{number}{side}" for number, side in references],
        })

    numbered = [row for row in rows if row["folio_references"]]
    numbers = sorted({int(reference[:-1]) for row in numbered for reference in row["folio_references"]})
    sides = {reference for row in numbered for reference in row["folio_references"]}
    highest = max(numbers, default=0)
    partial = [row for row in numbered if "(part)" in row["label"]]
    combined = [row for row in numbered if len(row["folio_references"]) > 1]
    return {
        "manifest_url": manifest["id"],
        "retrieved_at_utc": retrieved_at,
        "manifest_sha256": hashlib.sha256(raw).hexdigest(),
        "method": "Parse explicit number+r/v references in canvas labels; count distinct references, never infer physical leaves from images.",
        "canvas_count": len(rows),
        "numbered_canvas_count": len(numbered),
        "unnumbered_canvas_count": len(rows) - len(numbered),
        "distinct_folio_number_count": len(numbers),
        "distinct_folio_side_reference_count": len(sides),
        "lowest_folio_number": min(numbers, default=None),
        "highest_folio_number": highest or None,
        "numbers_without_label_references_within_observed_range": sorted(set(range(min(numbers, default=1), highest + 1)) - set(numbers)),
        "partial_canvas_count": len(partial),
        "combined_canvas_count": len(combined),
        "partial_canvases": partial,
        "combined_canvases": combined,
        "terminal_numbered_canvases": [row for row in numbered if f"{highest}r" in row["folio_references"] or f"{highest}v" in row["folio_references"]],
        "unnumbered_canvases": [row for row in rows if not row["folio_references"]],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--retrieved-at", required=True, help="UTC retrieval time of the supplied file (ISO 8601)")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(audit(args.manifest.read_bytes(), args.retrieved_at), indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")


if __name__ == "__main__":
    main()
