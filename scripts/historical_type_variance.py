"""Extend the frozen historical native-record B mean with exact covariance."""

import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path

try:
    from . import historical_record_conditioned as parent
    from .reconstruct_historical_tokens import reconstruct, encoded
    from .global_repeated_types import counts, boundary_diagnostics, exact_record
    from .record_repeated_type_variance import exact_type_variance, spread_diagnostics
except ImportError:
    import historical_record_conditioned as parent
    from reconstruct_historical_tokens import reconstruct, encoded
    from global_repeated_types import counts, boundary_diagnostics, exact_record
    from record_repeated_type_variance import exact_type_variance, spread_diagnostics


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = "research/historical/type-variance-plan.json"
HUMAN_PLAN = "research/historical/TYPE_VARIANCE_PLAN.md"
MEAN_REPORT = "research/historical/record-conditioned.json"
FROZEN_PATHS = (*parent.FROZEN_PATHS, "scripts/record_conditioned_repeated_types.py", "scripts/historical_record_conditioned.py",
                "research/historical/record-conditioned-plan.json", "research/historical/RECORD_CONDITIONED_PLAN.md",
                "research/historical/record-conditioned-amendment-1.json", "research/historical/RECORD_CONDITIONED_AMENDMENT_1.md", MEAN_REPORT)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def read_json(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique_object)


def strict(value):
    return json.dumps(value, sort_keys=True, allow_nan=False, separators=(",", ":"))


def load_plan(root):
    plan = read_json(root / PLAN_PATH)
    if (type(plan.get("plan_version")) is not int or plan["plan_version"] != 1
            or plan.get("statistic") != "distinct_self_repeating_types_B"
            or plan.get("include_all_parser_variants") is not True or plan.get("retain_asterisks") is not True
            or type(plan.get("new_controls")) is not int or plan["new_controls"] != 0
            or type(plan.get("decimal_precision")) is not int or plan["decimal_precision"] != 50
            or plan.get("calibrated_tail_claim") is not False
            or plan.get("edge_scope") != parent.EDGE_SCOPE
            or plan.get("condition_on") != "Independent uniform permutation of every surviving native-record token bag"
            or set(plan.get("dependency_hashes", {})) != set(FROZEN_PATHS)):
        raise ValueError("unsupported historical type-variance plan")
    for name in FROZEN_PATHS:
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != plan["dependency_hashes"][name]:
            raise ValueError(f"frozen type-variance dependency differs: {name}")
    return plan


def assay_variant(summary, corpus, reference, plan):
    rows, flat = corpus["records"], corpus["flat_tokens_with_provenance"]
    for key, data in (("record_corpus_sha256", rows), ("flat_corpus_sha256", flat)):
        if hashlib.sha256(encoded(data)).hexdigest() != summary[key] or reference[key] != summary[key]:
            raise ValueError("variance/parent corpus digest differs")
    rebuilt = [{"token": token, "locator": row["locator"], "original_token_index": index}
               for row in rows for token, index in zip(row["tokens"], row["original_token_indices"], strict=True)]
    if strict(rebuilt) != strict(flat):
        raise ValueError("variance record/flat slots differ")
    tokens = [r["token"] for r in flat]
    observed, diagnostics = counts(tokens), boundary_diagnostics(flat)
    identity = (summary["ring_policy"], summary["f66r_column_unit"])
    if (identity != (reference["ring_policy"], reference["f66r_column_unit"])
            or type(reference["tokens"]) is not int or reference["tokens"] != len(tokens)
            or type(reference["distinct_types"]) is not int or reference["distinct_types"] != len(set(tokens))
            or strict(observed) != strict(reference["observed"])
            or strict(diagnostics) != strict(reference["observed_boundary_diagnostics"])):
        raise ValueError("variance observed input/edge population differs")
    result = exact_type_variance([row["tokens"] for row in rows])
    mean = parent.fraction_from_record(reference["exact_conditional_null_means"]["B"])
    if (result["mean_B"] != mean or result["distinct_types"] != reference["distinct_types"]
            or result["nonempty_records"] != reference["nonempty_records"]
            or result["forced_repeating_types"] != reference["forced_repeating_types_under_conditional_null"]):
        raise ValueError("variance indicator means/populations differ from accepted parent")
    exact_names = ("mean_B", "marginal_variance_sum", "type_pair_covariance_sum", "twice_covariance_adjustment", "variance_B")
    return {"ring_policy": identity[0], "f66r_column_unit": identity[1],
            "record_corpus_sha256": summary["record_corpus_sha256"], "flat_corpus_sha256": summary["flat_corpus_sha256"],
            "tokens": len(tokens), "observed": observed, "observed_boundary_diagnostics": diagnostics,
            "exact_moments": {name: exact_record(result[name]) for name in exact_names},
            "indicator_support_accounting": {name: value for name, value in result.items() if name not in exact_names},
            "existing_ten_control_B_values": [row["distinct_repeating_types_B"] for row in reference["all_ten_controls"]],
            "spread_diagnostics": spread_diagnostics(result["variance_B"], Fraction(observed["distinct_repeating_types_B"]) - mean,
                                                     plan["decimal_precision"])}


def run_study(root=ROOT):
    plan = load_plan(root)
    reference = read_json(root / MEAN_REPORT)
    if strict(parent.run_study(root)) != strict(reference):
        raise ValueError("complete accepted conditional mean/control report does not replay")
    parsed, corpus = reconstruct(root)
    if any(len(rows) != 4 for rows in (parsed["variants"], corpus["variants"], reference["variants"])):
        raise ValueError("retain all four unchanged variance/parent variants")
    results = []
    for summary, variant, prior in zip(parsed["variants"], corpus["variants"], reference["variants"], strict=True):
        if (summary["ring_policy"], summary["f66r_column_unit"]) != (variant["ring_policy"], variant["f66r_column_unit"]):
            raise ValueError("variance source variant identity/order differs")
        results.append(assay_variant(summary, variant, prior, plan))
    return {"assay_version": 1, "scope": plan["scope"], "statistic": plan["statistic"],
            "plan_sha256": hashlib.sha256((root / PLAN_PATH).read_bytes()).hexdigest(),
            "human_plan_sha256": hashlib.sha256((root / HUMAN_PLAN).read_bytes()).hexdigest(),
            "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "metric_helper_sha256": hashlib.sha256(Path(__file__).with_name("record_repeated_type_variance.py").read_bytes()).hexdigest(),
            "frozen_dependency_hashes": plan["dependency_hashes"], "parent_pr": plan["parent_pr"], "parent_commit": plan["parent_commit"],
            "source_credit": reference["source_credit"], "source_permission": reference["source_permission"],
            "edge_scope": plan["edge_scope"], "condition_on": plan["condition_on"], "new_controls": 0, "variants": results,
            "limits": "Exact moments/conditional SD scale on exposed approximate H representations; no normal/calibrated tail, confidence, mechanism probability, physical-line identity, original-author replication, language or decipherment"}


def protect_output(path):
    sources = [ROOT / name for name in (*FROZEN_PATHS, PLAN_PATH, HUMAN_PLAN)]
    sources.extend((Path(__file__), Path(__file__).with_name("record_repeated_type_variance.py")))
    if any(path.resolve() == source.resolve() or path.exists() and source.exists() and path.samefile(source) for source in sources):
        raise ValueError("type-variance output aliases a frozen input, parent, plan or helper")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        if args.output:
            protect_output(args.output)
        result = run_study(ROOT)
        if args.check and strict(result) != strict(read_json(args.check)):
            raise ValueError("complete historical type-variance report differs")
        if args.output:
            payload = json.dumps(result, indent=2, allow_nan=False) + "\n"
            protect_output(args.output)
            args.output.write_text(payload, encoding="utf-8")
        elif not args.check:
            print(json.dumps(result, indent=2, allow_nan=False))
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"historical type-variance assay failed: {error}\n")
    if args.check:
        print("complete historical type-variance report reproduces")


if __name__ == "__main__":
    main()
