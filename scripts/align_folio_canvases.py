#!/usr/bin/env python3
"""Join explicit folio-side identifiers to all matching Yale IIIF canvas labels.

This is an image-reference join. It does not translate text, assign foldout panels,
or infer aliases between conflicting foliation systems.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re

from index_yale_manifest import build


FOLIO = re.compile(r"f?([1-9]\d*)([rv])", re.IGNORECASE)
def align(raw, requested, access_date):
    """Use the shared Yale index to resolve only explicit folio-side requests."""
    indexed = build(raw, access_date)
    index = {}
    for canvas in indexed["canvases.csv"]:
        references = canvas["explicit_folio_sides"].split(";") if canvas["explicit_folio_sides"] else []
        match = {
            "canvas_uri": canvas["canvas_uri"],
            "canvas_index": canvas["canvas_index_zero_based"],
            "canvas_label": canvas["yale_label"],
            "label_folio_references": references,
            "partial_view": canvas["has_partial_marker"],
            "combined_view": canvas["has_multiple_explicit_sides"],
            "image_oid": canvas["image_oid"],
            "catalog_image_url": canvas["catalog_image_url"],
            "image_urls": [canvas["full_image_url"]],
        }
        for reference in references:
            index.setdefault(reference, []).append(match)

    entries = []
    for identifier in requested:
        parsed = FOLIO.fullmatch(identifier.strip())
        if not parsed:
            entries.append({
                "requested_identifier": identifier,
                "canonical_folio_side": None,
                "status": "unsupported_identifier",
                "reason": "Expected an optional f prefix, positive folio number, and r/v. Panel and line suffixes require an explicit convention-specific mapping.",
                "matches": [],
            })
            continue
        canonical = f"{int(parsed[1])}{parsed[2].lower()}"
        matches = index.get(canonical, [])
        entries.append({
            "requested_identifier": identifier,
            "canonical_folio_side": canonical,
            "status": "matched" if matches else "label_unmatched",
            "matches": matches,
        })
    return {
        "manifest_url": indexed["audit.json"]["manifest_url"],
        "manifest_sha256": indexed["audit.json"]["manifest_sha256"],
        "access_date": indexed["audit.json"]["access_date"],
        "access_timezone": indexed["audit.json"]["access_timezone"],
        "image_index_generator": "scripts/index_yale_manifest.py",
        "identifier_normalization": "Trim surrounding whitespace, remove optional f prefix, lowercase r/v. No folio aliases or panel truncation.",
        "requested_count": len(entries),
        "matched_count": sum(entry["status"] == "matched" for entry in entries),
        "label_unmatched_count": sum(entry["status"] == "label_unmatched" for entry in entries),
        "unsupported_identifier_count": sum(entry["status"] == "unsupported_identifier" for entry in entries),
        "entries": entries,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("folios", nargs="+")
    parser.add_argument("--access-date", required=True, help="Date the supplied response was retrieved, YYYY-MM-DD")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--expected-sha256", help="Refuse to process input bytes that do not match this digest")
    parser.add_argument("--allow-incomplete", action="store_true", help="Exit successfully even when requested identifiers are unsupported or unmatched")
    args = parser.parse_args()
    raw = args.manifest.read_bytes()
    if args.expected_sha256 and hashlib.sha256(raw).hexdigest() != args.expected_sha256.lower():
        parser.error("Manifest bytes do not match --expected-sha256")
    try:
        result = align(raw, args.folios, args.access_date)
    except (ValueError, KeyError, TypeError, IndexError) as error:
        parser.error(str(error))
    output = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    if not args.allow_incomplete and result["matched_count"] != result["requested_count"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
