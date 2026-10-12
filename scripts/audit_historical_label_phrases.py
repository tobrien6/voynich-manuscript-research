"""Locate published label phrases in every native historical transcription.

This is a literal source lookup, not a corpus normalizer or glyph adjudication.
"""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import zipfile

try:
    from .audit_historical_interlinear import ROOT, parse_historical, read_pinned_archive, remove_comments
except ImportError:
    from audit_historical_interlinear import ROOT, parse_historical, read_pinned_archive, remove_comments


def literal_string(body):
    payload, _ = remove_comments(body)
    payload = payload.replace("!", "").replace("%", "")
    return " ".join(re.sub(r"[.,=\-]", " ", payload).split())


def body_digest(record):
    return hashlib.sha256(record.body.encode("latin-1")).hexdigest()


def lookup(records, phrases):
    if not isinstance(phrases, (list, tuple)) or not phrases:
        raise ValueError("query phrases must be a nonempty sequence")
    if any(not isinstance(p, str) or not p or p != " ".join(p.split()) for p in phrases):
        raise ValueError("query phrases must be exact strings with canonical spacing")
    if len(phrases) != len(set(phrases)):
        raise ValueError("query phrases must be unique")
    readings = {r.locator: literal_string(r.body) for r in records}
    if len(readings) != len(records):
        raise ValueError("duplicate native locators in lookup input")
    matches, keys = [], set()
    for phrase in phrases:
        hits = [r for r in records if readings[r.locator] == phrase]
        keys.update((r.page, r.unit, r.line) for r in hits)
        matches.append({
            "phrase": phrase,
            "matches_by_transcriber": dict(sorted(Counter(r.transcriber for r in hits).items())),
            "records": [{"locator": r.locator, "transcriber": r.transcriber,
                         "body_sha256": body_digest(r)} for r in hits],
        })
    grouped = defaultdict(list)
    for r in records:
        key = (r.page, r.unit, r.line)
        if key in keys:
            grouped[key].append({"locator": r.locator, "transcriber": r.transcriber,
                                 "literal_string": readings[r.locator], "body_sha256": body_digest(r)})
    return {
        "native_records_searched": len(records),
        "matches": matches,
        "native_key_readings": [
            {"page": page, "unit": unit, "line": line, "readings": grouped[(page, unit, line)]}
            for page, unit, line in sorted(keys)
        ],
    }


def audit(root=ROOT):
    catalog = json.loads((root / "data/historical/interlinear-16e6.json").read_text())
    plan_bytes = (root / "research/historical/parser-plan.json").read_bytes()
    plan = json.loads(plan_bytes)
    if (catalog.get("schema_version") != 1 or plan.get("plan_version") != 1
            or catalog["id"] != plan["source_id"]
            or any(catalog[k] != plan[k] for k in ("archive_sha256", "member_sha256"))):
        raise ValueError("label query source identity differs from the parser plan")
    records, _ = parse_historical(read_pinned_archive((root / catalog["path"]).read_bytes(), catalog))
    return {
        "audit_version": 1,
        "scope": "Exact complete-record label phrase lookup across all native codes; no glyph mapping or parser revision",
        "source": {key: catalog[key] for key in ("id", "credit", "archive_url", "archive_sha256",
            "member_sha256", "permission")},
        "query_plan_sha256": hashlib.sha256(plan_bytes).hexdigest(),
        "supplement_sha256": plan["supplement_sha256"],
        "lookup_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "reader_sha256": hashlib.sha256(Path(__file__).with_name("audit_historical_interlinear.py").read_bytes()).hexdigest(),
        "rendering": "Remove balanced curly comments and !/% fillers; map comma/period/hyphen/equals to boundaries; collapse whitespace. Preserve case, coded fallback characters and all other residual notation. Match the whole record only.",
        **lookup(records, plan["figure_label_phrases"]),
        "limits": "Native key agreement is not an image-adjudicated alignment; matches do not identify the authors' processed input or justify mixing transcribers",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        catalog_path = ROOT / "data/historical/interlinear-16e6.json"
        catalog = json.loads(catalog_path.read_text())
        protected = {catalog_path.resolve(), (ROOT / catalog["path"]).resolve(),
                     (ROOT / "research/historical/parser-plan.json").resolve(), Path(__file__).resolve()}
        if args.output and args.output.resolve() in protected:
            raise ValueError("lookup output must not overwrite inputs or script")
        result = audit(ROOT)
        if args.check and result != json.loads(args.check.read_text()):
            raise ValueError("historical label lookup differs from committed report")
        if args.output:
            args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        elif not args.check:
            print(json.dumps(result, indent=2))
    except (ValueError, KeyError, OSError, zipfile.BadZipFile) as error:
        parser.exit(1, f"historical label audit failed: {error}\n")
    if args.check:
        print("historical label lookup reproduces")


if __name__ == "__main__":
    main()
