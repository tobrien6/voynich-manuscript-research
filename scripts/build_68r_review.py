"""Review 68r's declared P0 locations without inventing records on its third page."""

import argparse
from collections import Counter
import json
from pathlib import Path

try:
    from .audit_transliterations import ROOT, load_sources
    from .build_67r_review import build as collect
except ImportError:
    from audit_transliterations import ROOT, load_sources
    from build_67r_review import build as collect


PAGE_KEYS = {"f68r1": [f"f68r1.{n}" for n in range(1, 5)],
             "f68r2": [f"f68r2.{n}" for n in range(1, 6)], "f68r3": []}
REGIONS = {"f68r1": "left field, upper horizontal writing",
           "f68r2": "middle field, upper horizontal writing"}


def build(root=ROOT):
    sources = load_sources(root)
    page_audit = []
    for page, expected in PAGE_KEYS.items():
        editions = []
        for source, document in sources:
            if source["id"] not in {"ZL3b", "IT2a"}:
                continue
            if page not in document.pages:
                raise ValueError(f"{source['id']}: absent required page header {page}")
            present = [locus for locus in document.loci if locus.page == page and locus.present]
            if not present:
                raise ValueError(f"{source['id']}: require present writing records on {page}")
            p0_keys = [locus.key for locus in present if locus.kind == "P0"]
            if p0_keys != expected:
                raise ValueError(f"{source['id']}: P0 cohort differs for {page}; retain declared zero-record pages")
            editions.append({"source_id": source["id"], "header_present": True,
                             "present_loci": len(present),
                             "present_loci_by_kind": dict(sorted(Counter(locus.kind for locus in present).items())),
                             "present_p0_locations": p0_keys})
        page_audit.append({"page_id": page, "declared_p0_locations": expected, "editions": editions})
    result = collect(root, sources=sources, keys=[key for keys in PAGE_KEYS.values() for key in keys],
                     regions=REGIONS, proposal="research/panel-regions/f68r-proposal.json",
                     method="68r-provisional-p0-review-v1")
    result["page_audit"] = page_audit
    result["zero_p0_page_scope"] = "f68r3 is present with non-P0 writing; an empty P0 list does not mean a blank image or absent page"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        result = build()
        if args.check and result != json.loads(args.check.read_text()):
            raise ValueError("committed 68r review checklist differs")
        if args.output:
            args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        elif not args.check:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        if args.check:
            print("PASS: all three native pages, nine P0 locations, and source pins reproduce")
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"FAIL: {error}\n")


if __name__ == "__main__":
    main()
