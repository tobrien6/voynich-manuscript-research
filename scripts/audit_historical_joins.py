"""Trace every equal native-record join in the frozen approximate H streams."""

from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path

try:
    from .audit_historical_interlinear import parse_historical, read_pinned_archive
    from .reconstruct_historical_tokens import reconstruct, encoded, normalize_body
    from .historical_repeated_types import FROZEN_PATHS as GLOBAL_INPUTS
    from .global_repeated_types import counts, boundary_diagnostics
except ImportError:
    from audit_historical_interlinear import parse_historical, read_pinned_archive
    from reconstruct_historical_tokens import reconstruct, encoded, normalize_body
    from historical_repeated_types import FROZEN_PATHS as GLOBAL_INPUTS
    from global_repeated_types import counts, boundary_diagnostics


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = "research/historical/join-provenance-plan.json"
HUMAN_PLAN = "research/historical/JOIN_PROVENANCE_PLAN.md"
GLOBAL_REPORT = "research/historical/repeated-types.json"
FROZEN_PATHS = (*GLOBAL_INPUTS, "scripts/global_repeated_types.py", "scripts/historical_repeated_types.py",
                "research/historical/repeated-types-plan.json", "research/historical/REPEATED_TYPES_PLAN.md", GLOBAL_REPORT)
CLASSES = ("same_page_same_unit", "same_page_different_unit", "different_page")
ADJACENCIES = ("consecutive_selected_H", "spans_empty_H_records")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique_object)


def strict_content(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, allow_nan=False, separators=(",", ":"))


def load_plan(root):
    plan = read_json(root / PLAN_PATH)
    if (type(plan.get("plan_version")) is not int or plan["plan_version"] != 1
            or plan.get("include_all_parser_variants") is not True or plan.get("retain_asterisks") is not True
            or plan.get("selection") != "Every equal-token native-record joining event, in source order"
            or plan.get("edge_scope") != "Consecutive nonempty retained native H records in the all-N-1 flat-stream edge population"
            or type(plan.get("h_ordinal_base")) is not int or plan["h_ordinal_base"] != 0
            or type(plan.get("physical_file_line_base")) is not int or plan["physical_file_line_base"] != 1
            or set(plan.get("dependency_hashes", {})) != set(FROZEN_PATHS)):
        raise ValueError("unsupported native-join provenance plan")
    for name in FROZEN_PATHS:
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != plan["dependency_hashes"][name]:
            raise ValueError(f"frozen join-provenance dependency differs: {name}")
    return plan


def audit_variant(summary, corpus, baseline, native, normalized):
    records, flat = corpus["records"], corpus["flat_tokens_with_provenance"]
    if len(records) != len(native) or len(native) != len(normalized) or len({r.locator for r in native}) != len(native):
        raise ValueError("native H record inventory differs")
    prior_file_line = 0
    offsets, offset = [], 0
    for row, source, original in zip(records, native, normalized, strict=True):
        indices = row["original_token_indices"]
        if (row["locator"] != source.locator or source.transcriber != "H"
                or type(source.physical_line) is not int or source.physical_line <= prior_file_line
                or len(indices) != len(row["tokens"])
                or any(type(i) is not int or not 0 <= i < len(original) for i in indices)
                or any(b <= a for a, b in zip(indices, indices[1:]))
                or [original[i] for i in indices] != row["tokens"]
                or row["exclusion_reasons"] and row["tokens"]):
            raise ValueError("native record order or retained endpoint provenance differs")
        prior_file_line = source.physical_line
        offsets.append(offset)
        offset += len(row["tokens"])
    derived_flat = [{"token": token, "locator": row["locator"], "original_token_index": i}
                    for row in records for token, i in zip(row["tokens"], row["original_token_indices"], strict=True)]
    if derived_flat != flat:
        raise ValueError("record and flat token provenance differ")
    for key, data in (("flat_corpus_sha256", flat), ("record_corpus_sha256", records)):
        if hashlib.sha256(encoded(data)).hexdigest() != summary[key] or baseline[key] != summary[key]:
            raise ValueError("join-provenance corpus digest differs")
    observed = counts([r["token"] for r in flat])
    diagnostics = boundary_diagnostics(flat)
    identity = (summary["ring_policy"], summary["f66r_column_unit"])
    if (identity != (baseline["ring_policy"], baseline["f66r_column_unit"])
            or strict_content(observed) != strict_content(baseline["observed"])
            or strict_content(diagnostics) != strict_content(baseline["observed_boundary_diagnostics"])
            or type(baseline["tokens"]) is not int or type(baseline["distinct_types"]) is not int
            or len(flat) != baseline["tokens"] or len({r["token"] for r in flat}) != baseline["distinct_types"]):
        raise ValueError("accepted global input/observed edge population differs")
    within_types = {a for row in records for a, b in zip(row["tokens"], row["tokens"][1:]) if a == b}

    def descriptor(index, endpoint=None):
        row, source, original = records[index], native[index], normalized[index]
        result = {"native_locator": source.locator, "native_page": source.page, "native_unit": source.unit,
                  "native_line": source.line, "selected_H_ordinal": index, "physical_source_file_line": source.physical_line,
                  "raw_body_sha256": hashlib.sha256(source.body.encode("latin-1")).hexdigest(),
                  "normalized_tokens_before_manual_exclusions": len(original), "retained_tokens": len(row["tokens"]),
                  "exclusion_reasons": row["exclusion_reasons"]}
        if not row["tokens"]:
            result["empty_status"] = ("whole_record_excluded" if row["exclusion_reasons"] else
                                      "normalized_empty" if not original else "manual_token_deletion_left_empty")
        if endpoint is not None:
            result["endpoint_retained_index"] = endpoint
            result["endpoint_normalized_index"] = row["original_token_indices"][endpoint]
        return result

    nonempty = [i for i, row in enumerate(records) if row["tokens"]]
    population_class, equal_class = Counter(dict.fromkeys(CLASSES, 0)), Counter(dict.fromkeys(CLASSES, 0))
    population_adj, equal_adj = Counter(dict.fromkeys(ADJACENCIES, 0)), Counter(dict.fromkeys(ADJACENCIES, 0))
    cases = []
    for join_index, (left, right) in enumerate(zip(nonempty, nonempty[1:])):
        a, b = native[left], native[right]
        category = ("different_page" if a.page != b.page else
                    "same_page_different_unit" if a.unit != b.unit else "same_page_same_unit")
        adjacency = "consecutive_selected_H" if right == left + 1 else "spans_empty_H_records"
        population_class[category] += 1
        population_adj[adjacency] += 1
        token = records[left]["tokens"][-1]
        if token != records[right]["tokens"][0]:
            continue
        equal_class[category] += 1
        equal_adj[adjacency] += 1
        cases.append({"joining_edge_ordinal": join_index, "flat_left_token_index": offsets[right] - 1,
                      "token": token, "native_join_class": category, "selected_H_adjacency": adjacency,
                      "type_also_repeats_within_records": token in within_types,
                      "left": descriptor(left, len(records[left]["tokens"]) - 1), "right": descriptor(right, 0),
                      "intervening_empty_H_records": [descriptor(i) for i in range(left + 1, right)]})
    joining_types = {case["token"] for case in cases}
    if (sum(population_class.values()) != diagnostics["cross_record_joining_edges"]
            or sum(population_adj.values()) != diagnostics["cross_record_joining_edges"]
            or len(cases) != diagnostics["cross_record_pair_events"]
            or len(joining_types) != diagnostics["cross_record_repeating_types"]
            or len(joining_types & within_types) != diagnostics["types_repeating_in_both_scopes"]):
        raise ValueError("native-join census does not reconcile with accepted diagnostics")
    return {"ring_policy": identity[0], "f66r_column_unit": identity[1],
            "flat_corpus_sha256": summary["flat_corpus_sha256"], "record_corpus_sha256": summary["record_corpus_sha256"],
            "selected_H_records": len(records), "tokens": len(flat), "nonempty_H_records": len(nonempty),
            "observed": observed, "observed_boundary_diagnostics": diagnostics,
            "joining_edges_by_native_class": dict(population_class), "equal_joins_by_native_class": dict(equal_class),
            "joining_edges_by_selected_H_adjacency": dict(population_adj), "equal_joins_by_selected_H_adjacency": dict(equal_adj),
            "distinct_joining_types": sorted(joining_types), "joining_types_also_repeating_within_records": sorted(joining_types & within_types),
            "all_equal_join_events": cases}


def run_audit(root=ROOT):
    plan = load_plan(root)
    parsed, corpus = reconstruct(root)
    if strict_content(parsed) != strict_content(read_json(root / "research/historical/parsing.json")):
        raise ValueError("frozen parser report does not replay")
    baseline = read_json(root / GLOBAL_REPORT)
    if any(len(rows) != 4 for rows in (parsed["variants"], corpus["variants"], baseline["variants"])):
        raise ValueError("retain all four source/global variants")
    catalog = read_json(root / "data/historical/interlinear-16e6.json")
    raw = read_pinned_archive((root / catalog["path"]).read_bytes(), catalog)
    native = [r for r in parse_historical(raw)[0] if r.transcriber == "H"]
    parser_plan = read_json(root / "research/historical/parser-plan.json")
    normalized = [normalize_body(r.body, set(parser_plan["special_codes"]))[0] for r in native]
    results = []
    for summary, variant, global_result in zip(parsed["variants"], corpus["variants"], baseline["variants"], strict=True):
        if (summary["ring_policy"], summary["f66r_column_unit"]) != (variant["ring_policy"], variant["f66r_column_unit"]):
            raise ValueError("source variant identity/order differs")
        results.append(audit_variant(summary, variant, global_result, native, normalized))
    return {"audit_version": 1, "scope": plan["scope"],
            "plan_sha256": hashlib.sha256((root / PLAN_PATH).read_bytes()).hexdigest(),
            "human_plan_sha256": hashlib.sha256((root / HUMAN_PLAN).read_bytes()).hexdigest(),
            "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "frozen_dependency_hashes": plan["dependency_hashes"], "global_repaired_head": plan["global_repaired_head"],
            "source_credit": catalog["credit"], "source_permission": catalog["permission"],
            "archive_url": catalog["archive_url"], "archive_sha256": catalog["archive_sha256"],
            "member": catalog["member"], "member_sha256": catalog["member_sha256"],
            "selected_H_ordinal_base": 0, "physical_source_file_line_base": 1, "variants": results,
            "limits": "Source-defined join provenance on exposed approximate streams; no physical-line continuity, image/glyph alignment, modern crosswalk, null/tail or decipherment"}


def protect_output(path):
    protected = [ROOT / n for n in (*FROZEN_PATHS, PLAN_PATH, HUMAN_PLAN)] + [Path(__file__)]
    if any(path.resolve() == source.resolve() or path.exists() and source.exists() and path.samefile(source) for source in protected):
        raise ValueError("join-provenance output aliases a frozen input, plan or producer")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        if args.output:
            protect_output(args.output)
        result = run_audit(ROOT)
        if args.check and strict_content(result) != strict_content(read_json(args.check)):
            raise ValueError("complete native-join provenance report differs")
        if args.output:
            payload = json.dumps(result, indent=2, allow_nan=False) + "\n"
            protect_output(args.output)
            args.output.write_text(payload, encoding="utf-8")
        elif not args.check:
            print(json.dumps(result, indent=2, allow_nan=False))
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"native-join provenance audit failed: {error}\n")
    if args.check:
        print("complete native-join provenance report reproduces")


if __name__ == "__main__":
    main()
