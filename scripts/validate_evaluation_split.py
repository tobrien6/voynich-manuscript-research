#!/usr/bin/env python3
"""Check declared evaluation splits, dependencies, exposure, and freeze chronology.

This validates declarations, not whether exposure/grouping/history is truthful.
It uses only the standard library and makes no network requests.
"""

import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re


PARTITIONS = {"development", "evaluation"}


def validate(split, input_bytes=None, require_frozen=False):
    errors, warnings = [], []

    def need(condition, message):
        if not condition:
            errors.append(message)

    def nonempty(value):
        return isinstance(value, str) and bool(value.strip())

    def timestamp(value, field, optional=False):
        if value is None and optional:
            return None
        try:
            if not isinstance(value, str):
                raise ValueError()
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                raise ValueError()
            return parsed
        except ValueError:
            errors.append(f"{field}: require an ISO timestamp with a timezone")
            return None

    def string_list(value, field, required=True):
        if not isinstance(value, list) or (required and not value):
            errors.append(f"{field}: require {'a nonempty' if required else 'a'} list")
            return []
        if any(not nonempty(v) for v in value):
            errors.append(f"{field}: all identifiers must be nonempty strings")
            return []
        need(all(v == v.strip() for v in value), f"{field}: identifiers must not have surrounding whitespace")
        need(len(value) == len(set(value)), f"{field}: duplicate identifiers")
        return value

    if not isinstance(split, dict):
        return {"errors": ["Split must be a JSON object"], "warnings": []}
    need(type(split.get("schema_version")) is int and split["schema_version"] == 1,
         "Unsupported or missing schema_version")
    for field in ["created_at", "frozen_at", "fit_started_at", "input", "units", "expected_counts"]:
        need(field in split, f"{field}: required field is missing")
    for field in ["split_id", "candidate_version"]:
        need(nonempty(split.get(field)), f"{field}: require a versioned identifier")
    status = split.get("status")
    need(isinstance(status, str) and status in {"draft", "frozen"}, "status: require draft or frozen")
    need(not require_frozen or status == "frozen", "The requested split is not frozen")
    claim = split.get("evaluation_claim")
    need(isinstance(claim, str) and claim in {"excluded_from_fitting", "unseen_material"},
         "evaluation_claim: require excluded_from_fitting or unseen_material")
    created = timestamp(split.get("created_at"), "created_at")
    frozen = timestamp(split.get("frozen_at"), "frozen_at", optional=status == "draft")
    fitting = timestamp(split.get("fit_started_at"), "fit_started_at", optional=True)
    need(status != "draft" or frozen is None, "A draft must not declare a freeze timestamp")
    if created and frozen:
        need(created <= frozen, "Freeze timestamp precedes split creation")
    if fitting:
        need(status == "frozen" and frozen is not None,
             "Fitting is recorded without a frozen split")
        if frozen:
            need(frozen < fitting, "Split must be frozen strictly before fitting begins")
    input_record = split.get("input", {})
    if not isinstance(input_record, dict):
        input_record = {}
    for field in ["edition", "source"]:
        need(nonempty(input_record.get(field)), f"input.{field}: require a description")
    digest = input_record.get("sha256", "")
    need(isinstance(digest, str) and bool(re.fullmatch(r"[0-9a-f]{64}", digest)),
         "input.sha256: require a SHA-256 digest")
    if input_bytes is not None:
        need(hashlib.sha256(input_bytes).hexdigest() == digest,
             "Input bytes differ from the pinned SHA-256")
    else:
        warnings.append("Input bytes were not supplied; the checksum was not verified.")
    need(not require_frozen or input_bytes is not None,
         "--require-frozen requires input bytes to verify the pin")
    counts = split.get("expected_counts", {})
    if not isinstance(counts, dict):
        counts = {}
    need(set(counts) == PARTITIONS and all(type(v) is int and v > 0 for v in counts.values()),
         "expected_counts: require positive integer development and evaluation counts")
    units = split.get("units", [])
    if not isinstance(units, list) or not units:
        errors.append("units: require a nonempty list")
        units = []
    actual = Counter()
    seen_ids = set()
    folio_units, canvas_units, group_partitions = defaultdict(set), defaultdict(set), defaultdict(set)
    for index, unit in enumerate(units):
        prefix = f"units[{index}]"
        if not isinstance(unit, dict):
            errors.append(f"{prefix}: require an object")
            continue
        uid = unit.get("unit_id")
        if not nonempty(uid):
            errors.append(f"{prefix}.unit_id: require an identifier")
            uid = prefix
        need(uid == uid.strip(), f"{prefix}.unit_id: remove surrounding whitespace")
        need(uid not in seen_ids, f"{uid}: duplicate unit identifier")
        seen_ids.add(uid)
        part = unit.get("partition")
        valid_part = isinstance(part, str) and part in PARTITIONS
        need(valid_part, f"{uid}: invalid partition")
        if valid_part:
            actual[part] += 1
        folios = string_list(unit.get("folio_ids"), f"{uid}.folio_ids")
        for folio in folios:
            need(bool(re.fullmatch(r"[1-9][0-9]*", folio)),
                 f"{uid}: folio_ids must be canonical leaf numbers without side/panel suffixes")
            folio_units[folio].add(uid)
        need("canvas_ids" in unit, f"{uid}.canvas_ids: declare a list, even if unresolved and empty")
        canvases = string_list(unit.get("canvas_ids", []), f"{uid}.canvas_ids", required=False)
        for canvas in canvases:
            canvas_units[canvas].add(uid)
        groups = string_list(unit.get("dependency_groups"), f"{uid}.dependency_groups")
        for group in groups:
            if valid_part:
                group_partitions[group].add(part)
        string_list(unit.get("source_refs"), f"{uid}.source_refs")
        exposure = unit.get("prior_exposure", {})
        if not isinstance(exposure, dict):
            exposure = {}
        state = exposure.get("state")
        need(isinstance(state, str) and state in {"known", "none_reported", "unknown"},
             f"{uid}: invalid exposure state")
        for field in ["note", "declared_by"]:
            need(nonempty(exposure.get(field)), f"{uid}.prior_exposure.{field}: require a declaration")
        recorded = timestamp(exposure.get("recorded_at"), f"{uid}.prior_exposure.recorded_at")
        if frozen and recorded:
            need(recorded <= frozen, f"{uid}: exposure declaration postdates the freeze")
        used = exposure.get("used_for_development")
        need("used_for_development" in exposure, f"{uid}: declare development use explicitly, or null if unresolved")
        need(used is None or type(used) is bool, f"{uid}: used_for_development must be boolean or null")
        if part == "evaluation":
            if state == "unknown" or used is None:
                message = f"{uid}: evaluation exposure/development use remains unresolved"
                (errors if status == "frozen" or require_frozen else warnings).append(message)
            need(used is not True, f"{uid}: evaluation material was used for development")
            if claim == "unseen_material":
                need(state != "known", f"{uid}: known exposure contradicts unseen_material")
    need(dict(actual) == counts, f"Unit counts {dict(actual)} differ from expected_counts {counts}")
    for field, mapping in [("physical folio", folio_units), ("canvas", canvas_units)]:
        for identifier, members in mapping.items():
            need(len(members) == 1,
                 f"{field} {identifier}: belongs to multiple units {sorted(members)}; combine related sides/panels")
    for group, partitions in group_partitions.items():
        need(len(partitions) <= 1, f"Dependency group {group}: crosses development/evaluation")
    warnings.append("Declarations do not prove unseen material, complete dependency grouping, or historical freeze order.")
    return {"errors": errors, "warnings": warnings, "status": status, "counts": dict(actual)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("split", type=Path)
    parser.add_argument("--input", type=Path, help="Verify the pinned input bytes")
    parser.add_argument("--require-frozen", action="store_true")
    args = parser.parse_args()
    try:
        split = json.loads(args.split.read_text(encoding="utf-8"))
        result = validate(split, args.input.read_bytes() if args.input else None, args.require_frozen)
    except (OSError, json.JSONDecodeError) as error:
        parser.exit(1, f"FAIL: {error}\n")
    for error in result["errors"]:
        print("FAIL:", error)
    for warning in result["warnings"]:
        print("NOTE:", warning)
    if not result["errors"]:
        print(f"PASS: declared {result['status']} split is structurally consistent; counts={result['counts']}")
    return bool(result["errors"])


if __name__ == "__main__":
    raise SystemExit(main())
