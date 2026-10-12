"""Freeze first/lower-median/last regular P0 loci without interpreting images."""

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

try:
    from .audit_pilot_transcriptions import audit, require
    from .audit_transliterations import load_sources
    from .token_baselines import paired_sources
except ImportError:
    from audit_pilot_transcriptions import audit, require
    from audit_transliterations import load_sources
    from token_baselines import paired_sources


ROOT = Path(__file__).resolve().parents[1]
PAGE = "f76r"
PLAN = "research/pilot/F76R_ANCHOR_PLAN.md"
HELPERS = ("ivtff.py", "audit_transliterations.py", "token_baselines.py",
           "audit_pilot_transcriptions.py", "select_f76r_anchors.py")


def native(locus):
    return {"key": locus.key, "identifier": locus.identifier,
            "source_file_line": locus.line_number, "native_text": locus.text,
            "locator": locus.locator, "kind": locus.kind,
            "metadata": dict(sorted(locus.variables.items()))}


def select(documents, page=PAGE):
    require(set(documents) == {"ZL3b", "IT2a"}, "Require the two declared editions")
    by_source = {}
    for ident, document in documents.items():
        page_loci = [locus for locus in document.loci if locus.page == page]
        require(len({locus.key for locus in page_loci}) == len(page_loci), "Duplicate page locus key")
        by_source[ident] = {locus.key: locus for locus in page_loci}
    all_keys = set.union(*(set(loci) for loci in by_source.values()))
    numbers = {key: next(loci[key].number for loci in by_source.values() if key in loci)
               for key in all_keys}
    eligible, excluded = [], []
    for key in sorted(all_keys, key=lambda key: numbers[key]):
        reasons = []
        for ident in ["ZL3b", "IT2a"]:
            locus = by_source[ident].get(key)
            if locus is None:
                reasons.append(ident + ":absent")
            elif not locus.present:
                reasons.append(ident + ":nonexistent")
            elif locus.kind != "P0" or locus.locator not in {"@", "+", "*"}:
                reasons.append(ident + ":not_regular_P0")
        if reasons:
            excluded.append({"key": key, "reasons": reasons,
                "source_identifiers": {ident: loci[key].identifier if key in loci else None
                                       for ident, loci in sorted(by_source.items())}})
        else:
            eligible.append(key)
    require(len(eligible) >= 3, "Need at least three distinct regular shared loci")
    ranks = [0, (len(eligible) - 1) // 2, len(eligible) - 1]
    anchors = []
    for role, rank in zip(["first", "lower_median", "last"], ranks):
        key = eligible[rank]
        sources = {}
        for ident, loci in sorted(by_source.items()):
            ordered = sorted(loci, key=lambda candidate: numbers[candidate])
            index = ordered.index(key)
            sources[ident] = {"locus": native(loci[key]),
                "preceding": native(loci[ordered[index-1]]) if index else None,
                "following": native(loci[ordered[index+1]]) if index+1 < len(ordered) else None}
        anchors.append({"role": role, "eligible_rank_zero_based": rank,
                        "key": key, "sources": sources})
    return {"eligible_count": len(eligible), "eligible_keys_in_numeric_order": eligible,
            "excluded_page_keys": excluded, "anchors": anchors}


def selection(root=ROOT):
    readiness = audit(root)
    entry = next(entry for entry in readiness["entries"] if entry["target"] == "76r")
    require(entry["status"] == "exact_page_metadata_link", "f76r metadata link blocked")
    sources = paired_sources(load_sources(root))
    result = select({source["id"]: document for source, document in sources})
    with (root / "research/image-index/canvases.csv").open(newline="") as handle:
        row = next(row for row in csv.DictReader(handle)
                   if row["canvas_uri"] == entry["selected_canvas"]["canvas_uri"])
    image = {**entry["selected_canvas"],
             "service_url": row["image_service_url"], "full_image_url": row["full_image_url"],
             "native_width": int(row["image_width"]), "native_height": int(row["image_height"])}
    require(image["image_oid"] == "1006210" and image["yale_label"] == "76r"
            and image["explicit_label_sides"] == ["76r"] and not image["combined_view"],
            "Unexpected f76r image identity")
    report = {"schema_version": 1, "analysis_id": "f76r-three-native-locus-anchors-v1",
              "page": PAGE, "selection": result, "image": image,
              "manifest": readiness["manifest"],
              "sources": [{key: source[key] for key in ["id", "alphabet", "url", "path", "sha256"]}
                          for source, _ in sources],
              "exposure": {"prior_inventory": entry["image_exposure"],
                  "whole_corpus_text_exposure": True, "untouched_evaluation": False},
              "inputs": {**readiness["inputs"], "anchor_plan": {
                  "path": PLAN, "sha256": hashlib.sha256((root / PLAN).read_bytes()).hexdigest()}},
              "implementation_sha256": {name: hashlib.sha256((root / "scripts" / name).read_bytes()).hexdigest()
                                        for name in HELPERS},
              "limit": "Selection only; no image-region or glyph validation."}
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--output", type=Path)
    destination.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        report = selection()
        if args.check:
            require(report == json.loads(args.check.read_bytes()), "Frozen anchor selection differs")
            print("PASS: all selected/excluded loci, native contexts and input identities reproduce")
        else:
            protected = {ROOT / item["path"] for item in report["inputs"].values()}
            protected.update(ROOT / source["path"] for source in report["sources"])
            protected.update(ROOT / "scripts" / name for name in HELPERS)
            require(args.output.resolve() not in {path.resolve() for path in protected},
                    "Output cannot replace a source or implementation input")
            args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print("Selected: " + ", ".join(anchor["key"] for anchor in report["selection"]["anchors"]))
    except (ValueError, OSError, KeyError, TypeError, StopIteration) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
