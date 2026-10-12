#!/usr/bin/env python3
"""Reconcile native-Eva adapter coverage and verify cached preprocessing outputs.

Reuses the accepted adapter and pinned source loader. No second tokenizer, image
mapping, statistic, or candidate fit is introduced. The report omits token text.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

try:
    from .eva_token_adapter import ROOT, DEFAULT_KINDS, DEFAULT_SOURCES, build
except ImportError:
    from eva_token_adapter import ROOT, DEFAULT_KINDS, DEFAULT_SOURCES, build


IDENTITY_FIELDS = ("source_id", "page_id", "locus_key", "locus_identifier",
                   "locus_type", "locator", "transcriber", "source_line_number", "variables")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False,
                       allow_nan=False) + "\n").encode("utf-8")


def load_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"Duplicate JSON object key: {key}")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique)


def verify_cached(raw, root=ROOT):
    """Verify full cached content against the pinned producer, not its own totals."""
    output = load_json(raw)
    require(isinstance(output, dict), "Cached adapter output must be an object")
    sources = output["sources"]
    require(isinstance(sources, list) and sources, "Cached source list must be nonempty")
    source_ids = tuple(source["id"] for source in sources)
    processing = output["processing"]
    expected = build(processing["uncertain_space_policy"], source_ids,
                     tuple(processing["selected_locus_types"]), root=root)
    # Canonical JSON also distinguishes true from 1 and 1.0 from 1.
    require(encoded(output) == encoded(expected),
            "Cached adapter content differs from the pinned producer; regenerate and review it")
    return output


def indexed(output):
    require(type(output.get("schema_version")) is int and output["schema_version"] == 1,
            "Coverage audit requires adapter schema version 1")
    require(output["adapter_version"] == "plain-eva-v1" and
            output["analysis_unit"] == "transcription_locus", "Unsupported adapter or sampling unit")
    ids = [source["id"] for source in output["sources"]]
    require(len(ids) == len(set(ids)), "Duplicate adapter source IDs")
    result = {ident: {} for ident in ids}
    reasons = Counter()
    eligible = 0
    for record in output["records"]:
        source, key = record["source_id"], record["locus_key"]
        require(source in result, "Record source is absent from adapter provenance")
        require(key not in result[source],
                f"Multiple records at {source}:{key}; resolve transcriber pairing before auditing cohorts")
        require(type(record["eligible"]) is bool, "Eligibility must be a boolean")
        flags = record["exclusion_reasons"]
        require(isinstance(flags, list) and all(isinstance(flag, str) and flag for flag in flags)
                and len(flags) == len(set(flags)), "Exclusion reasons must be unique nonempty strings")
        if record["eligible"]:
            tokens = record["tokens"]
            require(isinstance(tokens, list) and tokens and not flags and
                    type(record["token_count"]) is int and record["token_count"] == len(tokens),
                    "Eligible record has inconsistent tokens, count, or exclusions")
            eligible += 1
        else:
            require(record["tokens"] is None and record["token_count"] is None and flags,
                    "Excluded record must retain reasons and null tokens/count")
        result[source][key] = record
        reasons.update(flags)
    totals = {"records": len(output["records"]), "eligible_records": eligible,
              "excluded_records": len(output["records"]) - eligible,
              "exclusion_reason_record_counts": dict(sorted(reasons.items()))}
    require(encoded(totals) == encoded(output["summary"]), "Adapter summary does not reconcile with its records")
    return result


def cohort(keys, maps):
    ordered = sorted(keys)
    return {"native_locus_count": len(ordered),
            "sorted_native_keys_sha256": hashlib.sha256("".join(key + "\n" for key in ordered).encode("utf-8")).hexdigest(),
            "native_page_count": len({maps[key]["page_id"] for key in ordered})}


def summarize_outputs(outputs):
    require(set(outputs) == {"split", "join"}, "Supply both explicit spacing policies")
    split, join = outputs["split"], outputs["join"]
    require(encoded(split["sources"]) == encoded(join["sources"]), "Source provenance differs across spacing policies")
    expected_processing = dict(split["processing"], uncertain_space_policy="join")
    require(encoded(expected_processing) == encoded(join["processing"]), "Other processing choices differ across policies")
    require(split["processing"]["uncertain_space_policy"] == "split", "Incorrect split policy label")
    matrices = {policy: indexed(output) for policy, output in outputs.items()}
    source_ids = [source["id"] for source in split["sources"]]
    require(source_ids, "Select at least one source")
    selected_types = split["processing"]["selected_locus_types"]
    source_coverage, policy_coverage, eligible_sets = {}, {"split": {}, "join": {}}, []
    minimum_two_sets = []
    for source in source_ids:
        left, right = matrices["split"][source], matrices["join"][source]
        require(left.keys() == right.keys(), f"Record identities differ across policies for {source}")
        for key in left:
            require(encoded({field: left[key][field] for field in IDENTITY_FIELDS}) ==
                    encoded({field: right[key][field] for field in IDENTITY_FIELDS}),
                    f"Source metadata changed across policies at {source}:{key}")
        records = list(left.values())
        present = [record for record in records if record["locator"] != "!"]
        selected = [record for record in present if record["locus_type"] in selected_types]
        source_coverage[source] = {
            "declared_locus_records": len(records), "present_locus_records": len(present),
            "selected_present_locus_records": len(selected),
            "declared_records_by_kind": dict(sorted(Counter(record["locus_type"] for record in records).items())),
        }
        for policy in ("split", "join"):
            rows = list(matrices[policy][source].values())
            eligible = [row for row in rows if row["eligible"]]
            require(all(row["locator"] != "!" and row["locus_type"] in selected_types for row in eligible),
                    "Eligible records include nonexistent or unselected loci")
            policy_coverage[policy][source] = {
                "eligible_locus_records": len(eligible),
                "excluded_locus_records": len(rows) - len(eligible),
                "excluded_after_selected_present_filter": len(selected) - len(eligible),
                "eligible_token_count": sum(row["token_count"] for row in eligible),
                "eligible_records_by_kind": dict(sorted(Counter(row["locus_type"] for row in eligible).items())),
                "exclusion_reason_record_counts_may_overlap": dict(sorted(Counter(
                    reason for row in rows for reason in row["exclusion_reasons"]).items())),
            }
            eligible_sets.append({row["locus_key"] for row in eligible})
            minimum_two_sets.append({row["locus_key"] for row in eligible if row["token_count"] >= 2})
    common = set.intersection(*eligible_sets)
    common_two = set.intersection(*minimum_two_sets)
    first_map = matrices["split"][source_ids[0]]
    metadata_differences = {"locus_type": 0, "locator": 0}
    for key in common:
        for field in metadata_differences:
            metadata_differences[field] += len({matrices["split"][source][key][field] for source in source_ids}) > 1
    return {
        "schema_version": 1, "method": "native-eva adapter coverage audit v1",
        "adapter_version": split["adapter_version"], "analysis_unit": split["analysis_unit"],
        "sources": split["sources"], "selected_locus_types": selected_types,
        "adapter_snapshot_sha256": {policy: hashlib.sha256(encoded(output)).hexdigest()
                                    for policy, output in outputs.items()},
        "source_coverage": source_coverage, "policy_coverage": policy_coverage,
        "cohorts": {
            "eligible_in_every_source_and_policy": cohort(common, first_map),
            "at_least_two_tokens_in_every_source_and_policy": cohort(common_two, first_map),
            "cross_source_metadata_differences_in_shared_eligible_cohort": metadata_differences,
        },
        "count_semantics": "Source editions are counted separately; matching native locus keys are not independent manuscript samples or verified physical lines. Exclusion reasons may overlap.",
        "token_text_published": False,
    }


def selection_manifest(outputs):
    """Export complete native-key selections with deduplicated digest-addressed sets."""
    report = summarize_outputs(outputs)
    matrices = {policy: indexed(output) for policy, output in outputs.items()}
    key_sets, source_sets, policy_sets = {}, {}, {"split": {}, "join": {}}
    all_eligible, all_two = [], []

    def reference(keys):
        ordered = sorted(keys)
        digest = hashlib.sha256("".join(key + "\n" for key in ordered).encode("utf-8")).hexdigest()
        key_sets[digest] = ordered
        return {"native_locus_count": len(ordered), "sorted_native_keys_sha256": digest}

    kinds = report["selected_locus_types"]
    for source in (entry["id"] for entry in report["sources"]):
        rows = matrices["split"][source]
        declared = set(rows)
        present = {key for key, row in rows.items() if row["locator"] != "!"}
        selected = {key for key in present if rows[key]["locus_type"] in kinds}
        source_sets[source] = {"declared": reference(declared), "present": reference(present),
                               "selected_present": reference(selected)}
        for policy in ("split", "join"):
            current = matrices[policy][source]
            eligible = {key for key, row in current.items() if row["eligible"]}
            two = {key for key in eligible if current[key]["token_count"] >= 2}
            policy_sets[policy][source] = {
                "eligible": reference(eligible), "excluded": reference(declared - eligible),
                "excluded_selected_present": reference(selected - eligible),
                "at_least_two_eligible_tokens": reference(two),
            }
            all_eligible.append(eligible)
            all_two.append(two)
    return {
        "schema_version": 1, "manifest_method": "native-eva selection manifest v1",
        "adapter_version": report["adapter_version"], "analysis_unit": report["analysis_unit"],
        "sources": report["sources"], "selected_locus_types": kinds,
        "adapter_snapshot_sha256": report["adapter_snapshot_sha256"],
        "source_key_sets": source_sets, "policy_key_sets": policy_sets,
        "shared_cohort_key_sets": {
            "eligible_in_every_source_and_policy": reference(set.intersection(*all_eligible)),
            "at_least_two_tokens_in_every_source_and_policy": reference(set.intersection(*all_two)),
        },
        "key_sets": dict(sorted(key_sets.items())),
        "key_contract": "Each reference resolves via key_sets[sorted_native_keys_sha256]. Keys are sorted original locus_key strings, without source prefix or physical-folio aliases. Sources and policies remain separate dimensions.",
    }


def audit(source_ids=DEFAULT_SOURCES, kinds=DEFAULT_KINDS, root=ROOT):
    return summarize_outputs({policy: build(policy, source_ids, kinds, root=root)
                              for policy in ("split", "join")})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", action="append")
    parser.add_argument("--kind", action="append")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--keys-output", type=Path, help="Export exact selected, eligible, and excluded native-key sets")
    parser.add_argument("--verify-adapter", action="append", type=Path, help="Verify cached adapter JSON against its recorded policy and pinned sources")
    args = parser.parse_args()
    try:
        if args.verify_adapter:
            require(not any((args.source, args.kind, args.output, args.check, args.keys_output)),
                    "Cache verification uses each cache's recorded choices; run the coverage audit separately")
            for path in args.verify_adapter:
                verify_cached(path.read_bytes())
                print(f"PASS: {path.name} reproduces the pinned adapter output.")
            return
        outputs = {policy: build(policy, tuple(args.source or DEFAULT_SOURCES),
                                 tuple(args.kind or DEFAULT_KINDS)) for policy in ("split", "join")}
        report = summarize_outputs(outputs)
        if args.keys_output:
            require(not args.output or args.output.resolve() != args.keys_output.resolve(),
                    "Coverage and key-manifest output paths must differ")
            require(not args.check or args.check.resolve() != args.keys_output.resolve(),
                    "Key-manifest output must not replace the checked coverage report")
        for path in (args.output, args.keys_output):
            if path:
                resolved = path.resolve()
                require(resolved != (ROOT / "data/transliterations.json").resolve() and
                        not resolved.is_relative_to((ROOT / "data/raw").resolve()),
                        "Audit output must not replace the source catalog or a pinned raw input")
        if args.check:
            require(encoded(report) == encoded(load_json(args.check.read_bytes())), "Committed coverage audit differs from the recomputed report")
            print("PASS: source coverage, cohort identities, and adapter snapshots verified.")
        if args.output:
            args.output.write_bytes(encoded(report))
        elif not args.check:
            print(encoded(report).decode("utf-8"), end="")
        if args.keys_output:
            args.keys_output.write_bytes(encoded(selection_manifest(outputs)))
    except (ValueError, TypeError, KeyError, OSError) as error:
        parser.exit(1, f"adapter coverage audit failed: {error}\n")


if __name__ == "__main__":
    main()
