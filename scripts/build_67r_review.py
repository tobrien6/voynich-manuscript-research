"""Build a source-pinned review checklist for provisional 67r horizontal rows.

Encoded source agreement is not glyph verification or a decoded reading.
"""

import argparse
import json
from pathlib import Path

try:
    from .audit_transliterations import ROOT, load_sources
except ImportError:
    from audit_transliterations import ROOT, load_sources


KEYS = [f"f67r1.{n}" for n in range(1, 5)] + [f"f67r2.{n}" for n in range(72, 75)]


def build(root=ROOT):
    selected = [(source, document) for source, document in load_sources(root)
                if source["id"] in {"ZL3b", "IT2a"}]
    if sorted(source["id"] for source, _ in selected) != ["IT2a", "ZL3b"]:
        raise ValueError("require exactly one pinned ZL3b and IT2a source")
    selected.sort(key=lambda item: {"ZL3b": 0, "IT2a": 1}[item[0]["id"]])
    records = []
    for key in KEYS:
        readings = []
        for source, document in selected:
            matches = [locus for locus in document.loci if locus.key == key]
            if len(matches) != 1 or not matches[0].present or matches[0].kind != "P0":
                raise ValueError(f"{source['id']}: expected one present P0 record at {key}")
            locus = matches[0]
            readings.append({"source_id": source["id"], "locus_identifier": locus.identifier,
                             "source_file_line": locus.line_number, "native_text": locus.text})
        records.append({"locus_key": key, "proposed_region":
            "left panel, upper horizontal block" if key.startswith("f67r1.") else
            "right panel, lower horizontal block",
            "image_glyph_verification": "pending", "readings": readings,
            "native_record_text_identical": readings[0]["native_text"] == readings[1]["native_text"]})
    equal = sum(record["native_record_text_identical"] for record in records)
    return {"schema_version": 1, "method": "67r-provisional-p0-review-v1",
            "proposal": "research/panel-regions/f67r-proposal.json",
            "usable_as_verified_corpus_join": False, "normalization": "none; preserve native reader text and annotations",
            "sources": [{"source_id": source["id"], "sha256": source["sha256"],
                         "alphabet": source["alphabet"], "url": source["url"]} for source, _ in selected],
            "locations": len(records), "identical_native_record_text": equal,
            "different_native_record_text": len(records) - equal,
            "source_file_line_scope": "physical file line, not a reconstructed manuscript line",
            "limits": "Related editions are not independent witnesses; native-text equality does not establish glyph identity or image placement.",
            "records": records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        result = build()
        if args.check and result != json.loads(args.check.read_text()):
            raise ValueError("committed 67r review checklist differs")
        if args.output:
            args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        elif not args.check:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        if args.check:
            print("PASS: source pins and all seven native P0 review records reproduce")
    except (ValueError, OSError) as error:
        parser.exit(1, f"FAIL: {error}\n")


if __name__ == "__main__":
    main()
