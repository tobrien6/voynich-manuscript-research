"""Run the frozen exploratory whole-text A/B assay on approximate H streams."""

from collections import Counter
from fractions import Fraction
import argparse
import hashlib
import json
from pathlib import Path

try:
    from .reconstruct_historical_tokens import reconstruct, encoded
    from .global_repeated_types import counts, exact_means, exact_record, ratio, boundary_diagnostics, whole_text_control
    from .shuffle_token_lines import ALGORITHM
except ImportError:
    from reconstruct_historical_tokens import reconstruct, encoded
    from global_repeated_types import counts, exact_means, exact_record, ratio, boundary_diagnostics, whole_text_control
    from shuffle_token_lines import ALGORITHM


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = "research/historical/repeated-types-plan.json"
EDGE_SCOPE = "All N-1 adjacent edges in each surviving flat stream, including native-record joins"
FROZEN_PATHS = (
    "data/historical/interlinear-16e6.json", "data/historical/text16e6.zip",
    "scripts/audit_historical_interlinear.py", "scripts/reconstruct_historical_tokens.py",
    "research/historical/parser-plan.json", "research/historical/parsing.json",
    "scripts/shuffle_token_lines.py",
)


def load_plan(root):
    raw = (root / PLAN_PATH).read_bytes()
    plan = json.loads(raw)
    if (plan.get("plan_version") != 1 or type(plan.get("seed")) is not int or plan["seed"] < 0
            or type(plan.get("trials")) is not int or plan["trials"] != 10
            or plan.get("algorithm") != ALGORITHM
            or plan.get("shuffle_frame") != "historical-whole-text-v1"
            or plan.get("edge_scope") != EDGE_SCOPE
            or plan.get("metrics") != ["equal_pair_events_A", "distinct_self_repeating_types_B"]
            or plan.get("retain_asterisks") is not True or plan.get("include_all_parser_variants") is not True
            or set(plan.get("dependency_hashes", {})) != set(FROZEN_PATHS)):
        raise ValueError("unsupported repeated-type assay plan")
    for name in FROZEN_PATHS:
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != plan["dependency_hashes"][name]:
            raise ValueError(f"frozen assay dependency differs: {name}")
    return plan, hashlib.sha256(raw).hexdigest()


def assay_variant(summary, corpus, plan):
    flat = corpus["flat_tokens_with_provenance"]
    if hashlib.sha256(encoded(flat)).hexdigest() != summary["flat_corpus_sha256"]:
        raise ValueError("reconstructed flat corpus digest differs")
    if hashlib.sha256(encoded(corpus["records"])).hexdigest() != summary["record_corpus_sha256"]:
        raise ValueError("reconstructed record corpus digest differs")
    tokens = [entry["token"] for entry in flat]
    observed = counts(tokens)
    diagnostics = boundary_diagnostics(flat)
    if (observed["equal_pair_events_A"] != diagnostics["within_record_pair_events"] + diagnostics["cross_record_pair_events"]
            or observed["distinct_repeating_types_B"] != diagnostics["within_record_repeating_types"]
            + diagnostics["cross_record_repeating_types"] - diagnostics["types_repeating_in_both_scopes"]):
        raise ValueError("observed edge/type diagnostics do not reconcile")
    means = exact_means(tokens)
    trials = []
    for trial in range(plan["trials"]):
        control = whole_text_control(tokens, summary["flat_corpus_sha256"], summary["ring_policy"],
                                     summary["f66r_column_unit"], plan["seed"], trial)
        trials.append({"trial": trial, **counts(control)})
    sampled_a = Fraction(sum(t["equal_pair_events_A"] for t in trials), len(trials))
    sampled_b = Fraction(sum(t["distinct_repeating_types_B"] for t in trials), len(trials))
    return {
        "ring_policy": summary["ring_policy"], "f66r_column_unit": summary["f66r_column_unit"],
        "flat_corpus_sha256": summary["flat_corpus_sha256"], "record_corpus_sha256": summary["record_corpus_sha256"],
        "tokens": len(tokens), "distinct_types": len(Counter(tokens)),
        "frequency_classes": {str(c): m for c, m in means["frequency_classes"].items()},
        "forced_repeating_types": means["forced_repeating_types"],
        "observed": observed, "observed_boundary_diagnostics": diagnostics,
        "exact_global_null_means": {"A": exact_record(means["A"]), "B": exact_record(means["B"])},
        "observed_over_exact_mean": {"A": ratio(observed["equal_pair_events_A"], means["A"]),
                                      "B": ratio(observed["distinct_repeating_types_B"], means["B"])},
        "all_ten_controls": trials,
        "ten_control_means": {"A": exact_record(sampled_a), "B": exact_record(sampled_b)},
        "observed_over_ten_control_mean": {"A": ratio(observed["equal_pair_events_A"], sampled_a),
                                            "B": ratio(observed["distinct_repeating_types_B"], sampled_b)},
    }


def run_study(root=ROOT):
    plan, plan_digest = load_plan(root)
    parsed, corpora = reconstruct(root)
    if parsed != json.loads((root / "research/historical/parsing.json").read_text()):
        raise ValueError("frozen parsing report does not replay")
    if len(parsed["variants"]) != 4 or len(corpora["variants"]) != 4:
        raise ValueError("retain the complete four-variant reconstruction")
    results = []
    for summary, corpus in zip(parsed["variants"], corpora["variants"], strict=True):
        if (summary["ring_policy"], summary["f66r_column_unit"]) != (corpus["ring_policy"], corpus["f66r_column_unit"]):
            raise ValueError("reconstruction variant order/identity differs")
        results.append(assay_variant(summary, corpus, plan))
    catalog = json.loads((root / "data/historical/interlinear-16e6.json").read_text())
    return {
        "assay_version": 1, "scope": plan["scope"], "study_plan_sha256": plan_digest,
        "human_plan_sha256": hashlib.sha256((root / "research/historical/REPEATED_TYPES_PLAN.md").read_bytes()).hexdigest(),
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "metric_helper_sha256": hashlib.sha256(Path(__file__).with_name("global_repeated_types.py").read_bytes()).hexdigest(),
        "frozen_dependency_hashes": plan["dependency_hashes"],
        "source_credit": catalog["credit"], "source_permission": catalog["permission"],
        "seed": plan["seed"], "trials_per_variant": plan["trials"], "algorithm": ALGORITHM,
        "frame": plan["shuffle_frame"], "edge_scope": plan["edge_scope"], "variants": results,
        "limits": "Approximate exposed streams and one global null; no original-input equality, independent variant replication, calibrated tail, language identification or decipherment",
    }


def protect_output(path):
    protected = {ROOT / name for name in FROZEN_PATHS}
    protected.update((ROOT / PLAN_PATH, ROOT / "research/historical/REPEATED_TYPES_PLAN.md",
                      Path(__file__), Path(__file__).with_name("global_repeated_types.py")))
    if any(path.resolve() == source.resolve()
           or path.exists() and source.exists() and path.samefile(source) for source in protected):
        raise ValueError("assay output must not overwrite frozen inputs, plan or code")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        if args.output:
            protect_output(args.output)
        result = run_study(ROOT)
        if args.check and result != json.loads(args.check.read_text()):
            raise ValueError("repeated-type assay differs from recorded report")
        if args.output:
            payload = json.dumps(result, indent=2, allow_nan=False) + "\n"
            protect_output(args.output)
            args.output.write_text(payload, encoding="utf-8")
        elif not args.check:
            print(json.dumps(result, indent=2, allow_nan=False))
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"historical repeated-type assay failed: {error}\n")
    if args.check:
        print("historical repeated-type assay reproduces")


if __name__ == "__main__":
    main()
