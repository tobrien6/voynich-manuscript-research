"""Validate explicit foliation decisions; never apply an unresolved candidate.

Uses no network and does not infer aliases, strip prefixes, or assign panels.
"""

import argparse
import csv
import datetime
import hashlib
import json
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "research/folio-aliases/decisions.json"
CANVAS_PREFIX = "https://collections.library.yale.edu/manifests/oid/2002046/canvas/"
TARGET_SCHEME = "yale_2002046_canvas_label"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text_field(record, key):
    value = record.get(key)
    require(isinstance(value, str) and value.strip(), f"Missing text field: {key}")
    return value


def date_field(record, key):
    value = text_field(record, key)
    require(re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value), f"Invalid date: {key}")
    return datetime.date.fromisoformat(value)


def target_field(target):
    require(isinstance(target, dict), "Target must be an object")
    text_field(target, "label")
    uris = target.get("canvas_uris")
    require(isinstance(uris, list) and uris, "Target needs canvas_uris")
    require(all(isinstance(uri, str) and uri.startswith(CANVAS_PREFIX)
                and uri[len(CANVAS_PREFIX):].isdigit() for uri in uris),
            "Target has an invalid Yale canvas URI")
    require(len(set(uris)) == len(uris), "Duplicate target canvas URI")


def read_index(raw):
    """Read PR #8's canvas CSV without duplicating its manifest parser."""
    import io
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8")))
    require(reader.fieldnames is not None and {"canvas_uri", "yale_label"}
            <= set(reader.fieldnames), "Canvas index needs canvas_uri and yale_label")
    index = {}
    for row in reader:
        uri, label = text_field(row, "canvas_uri"), text_field(row, "yale_label")
        require(uri not in index, f"Duplicate index canvas URI: {uri}")
        index[uri] = label
    require(index, "Empty canvas index")
    return index


def validate_registry(registry, index=None, manifest_sha256=None):
    require(isinstance(registry, dict) and type(registry.get("schema_version")) is int
            and registry["schema_version"] == 1, "Expected registry schema_version 1")
    require(registry.get("target_scheme") == TARGET_SCHEME, "Unexpected target scheme")
    require(set(registry) <= {"schema_version", "target_scheme", "decisions"},
            "Unknown registry field")
    decisions = registry.get("decisions")
    require(isinstance(decisions, list), "decisions must be a list")
    keys, ids = set(), set()
    for decision in decisions:
        require(isinstance(decision, dict), "Decision must be an object")
        require(set(decision) <= {"decision_id", "source_scheme", "source_label", "status",
                "candidate_target", "verified_target", "review", "evidence", "rationale",
                "recorded_on", "issue_url"}, "Unknown decision field")
        ident = text_field(decision, "decision_id")
        key = (text_field(decision, "source_scheme"), text_field(decision, "source_label"))
        require(key[0] != TARGET_SCHEME, "An alias must name a distinct source scheme")
        require(ident not in ids and key not in keys, "Duplicate decision ID or source key")
        ids.add(ident)
        keys.add(key)
        require(decision.get("status") in {"unresolved", "verified", "rejected"},
                f"Unknown decision status: {ident}")
        text_field(decision, "rationale")
        date_field(decision, "recorded_on")
        evidence = decision.get("evidence")
        require(isinstance(evidence, list) and evidence, f"Missing evidence: {ident}")
        urls = set()
        for item in evidence:
            require(isinstance(item, dict), "Evidence must be an object")
            url = text_field(item, "url")
            require(url.startswith("https://"), "Evidence needs an HTTPS source URL")
            urls.add(url)
            text_field(item, "locator")
            text_field(item, "statement")
        for key_name in ("candidate_target", "verified_target"):
            target = decision.get(key_name)
            if target is not None:
                target_field(target)
                allowed = {"label", "canvas_uris"}
                if key_name == "verified_target":
                    allowed |= {"manifest_sha256", "mapping_scope"}
                require(set(target) <= allowed, "Unknown target field")
                if index is not None:
                    for uri in target["canvas_uris"]:
                        require(index.get(uri) == target["label"],
                                f"Target label/URI does not match canvas index: {ident}")
        if decision["status"] != "verified":
            require(decision.get("verified_target") is None and decision.get("review") is None,
                    f"Unverified decision cannot contain a verified target or review: {ident}")
            continue
        target, review = decision.get("verified_target"), decision.get("review")
        require(target is not None, f"Verified decision needs a target: {ident}")
        require(isinstance(review, dict), f"Verified decision needs review: {ident}")
        require(set(review) <= {"reviewer", "reviewed_on", "finding", "evidence_urls"},
                "Unknown review field")
        require(target.get("mapping_scope") == "canvas_reference_only",
                "Verified alias only establishes a canvas reference, not a panel or text region")
        text_field(review, "reviewer")
        require(date_field(review, "reviewed_on") >= date_field(decision, "recorded_on"),
                "Review date precedes the decision record")
        text_field(review, "finding")
        refs = review.get("evidence_urls")
        require(isinstance(refs, list) and refs and all(url in urls for url in refs),
                "Review must cite evidence already recorded in the decision")
        digest = target.get("manifest_sha256")
        require(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest),
                "Verified target needs a manifest SHA-256")
        require(index is not None and manifest_sha256 is not None,
                "Verified decisions require the canvas index and manifest checksum")
        require(digest == manifest_sha256, "Verified decision refers to a different manifest")
    return decisions


def lookup(registry, scheme, source_label, index=None, manifest_sha256=None):
    decisions = validate_registry(registry, index, manifest_sha256)
    for decision in decisions:
        if (decision["source_scheme"], decision["source_label"]) == (scheme, source_label):
            verified = decision["status"] == "verified"
            return {"source_scheme": scheme, "source_label": source_label,
                    "decision_id": decision["decision_id"], "status": decision["status"],
                    "mapping_allowed": verified,
                    "target": decision["verified_target"] if verified else None,
                    "candidate_target": decision.get("candidate_target"),
                    "rationale": decision["rationale"]}
    return {"source_scheme": scheme, "source_label": source_label,
            "status": "unregistered", "mapping_allowed": False, "target": None}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--canvas-index", type=Path)
    parser.add_argument("--index-audit", type=Path, help="PR #8 audit.json with manifest_sha256")
    parser.add_argument("--lookup", nargs=2, metavar=("SOURCE_SCHEME", "SOURCE_LABEL"))
    args = parser.parse_args(argv)
    try:
        require(bool(args.canvas_index) == bool(args.index_audit),
                "Supply --canvas-index and --index-audit together")
        raw = args.registry.read_bytes()
        index_raw = args.canvas_index.read_bytes() if args.canvas_index else None
        index = read_index(index_raw) if index_raw is not None else None
        audit = json.loads(args.index_audit.read_bytes()) if args.index_audit else None
        digest = audit.get("manifest_sha256") if isinstance(audit, dict) else None
        if audit is not None:
            require(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest),
                    "Index audit needs a valid manifest_sha256")
        registry = json.loads(raw)
        decisions = validate_registry(registry, index, digest)
        result = lookup(registry, *args.lookup, index=index, manifest_sha256=digest) if args.lookup else {
            "status": "valid_registry", "decision_count": len(decisions),
            "decision_statuses": {d["decision_id"]: d["status"] for d in decisions}}
        result["registry_sha256"] = hashlib.sha256(raw).hexdigest()
        result["canvas_index_sha256"] = hashlib.sha256(index_raw).hexdigest() if index_raw else None
        result["manifest_sha256"] = digest
        result["targets_checked_against_index"] = index is not None
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return int(bool(args.lookup) and not result["mapping_allowed"])
    except (ValueError, KeyError, TypeError, OSError, UnicodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
