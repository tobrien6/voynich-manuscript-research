"""Run the frozen matched-edge native-record-conditioned historical H assay."""

from collections import Counter
from fractions import Fraction
import argparse
import hashlib
import json
from pathlib import Path

try:
    from .historical_repeated_types import FROZEN_PATHS as GLOBAL_INPUTS, EDGE_SCOPE
    from .reconstruct_historical_tokens import reconstruct, encoded
    from .global_repeated_types import counts, boundary_diagnostics, exact_record, ratio
    from .record_conditioned_repeated_types import exact_record_means, record_controls
    from .shuffle_token_lines import ALGORITHM
except ImportError:
    from historical_repeated_types import FROZEN_PATHS as GLOBAL_INPUTS, EDGE_SCOPE
    from reconstruct_historical_tokens import reconstruct, encoded
    from global_repeated_types import counts, boundary_diagnostics, exact_record, ratio
    from record_conditioned_repeated_types import exact_record_means, record_controls
    from shuffle_token_lines import ALGORITHM


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = "research/historical/record-conditioned-plan.json"
AMENDMENT_PATH = "research/historical/record-conditioned-amendment-1.json"
AMENDMENT_NOTE = "research/historical/RECORD_CONDITIONED_AMENDMENT_1.md"
GLOBAL_REPORT = "research/historical/repeated-types.json"
FROZEN_PATHS = (*GLOBAL_INPUTS, "scripts/global_repeated_types.py", "scripts/historical_repeated_types.py",
                "research/historical/repeated-types-plan.json", "research/historical/REPEATED_TYPES_PLAN.md", GLOBAL_REPORT)


def load_plan(root):
    raw = (root / PLAN_PATH).read_bytes()
    plan = json.loads(raw)
    if (type(plan.get("plan_version")) is not int or plan["plan_version"] != 1
            or type(plan.get("seed")) is not int or plan["seed"] < 0
            or type(plan.get("trials")) is not int or plan["trials"] != 10
            or plan.get("algorithm") != ALGORITHM or plan.get("shuffle_frame") != "historical-native-record-v1"
            or plan.get("edge_scope") != EDGE_SCOPE
            or plan.get("metrics") != ["equal_pair_events_A", "distinct_self_repeating_types_B"]
            or plan.get("condition_on") != "Independent uniform permutation of every surviving native-record token bag"
            or plan.get("retain_asterisks") is not True or plan.get("include_all_parser_variants") is not True
            or set(plan.get("dependency_hashes", {})) != set(FROZEN_PATHS)):
        raise ValueError("unsupported native-record-conditioned assay plan")
    plan_digest = hashlib.sha256(raw).hexdigest()
    amendment = json.loads((root / AMENDMENT_PATH).read_bytes())
    replacements = amendment.get("replacement_dependencies", {})
    if (type(amendment.get("amendment_version")) is not int or amendment["amendment_version"] != 1
            or amendment.get("original_plan_sha256") != plan_digest
            or amendment.get("reason") != "Output alias protection only; scientific input, edges, metrics, null and trials unchanged"
            or set(replacements) != {"scripts/historical_repeated_types.py", GLOBAL_REPORT}):
        raise ValueError("unsupported output-protection amendment")
    effective = dict(plan["dependency_hashes"])
    for name, replacement in replacements.items():
        if (set(replacement) != {"original_sha256", "repaired_sha256"}
                or replacement["original_sha256"] != plan["dependency_hashes"][name]):
            raise ValueError("amendment does not retain an original registered dependency")
        effective[name] = replacement["repaired_sha256"]
    for name in FROZEN_PATHS:
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != effective[name]:
            raise ValueError(f"frozen conditional dependency differs: {name}")
    global_payload = json.loads((root / GLOBAL_REPORT).read_bytes())
    global_payload.pop("runner_sha256")
    if hashlib.sha256(encoded(global_payload)).hexdigest() != amendment["global_payload_excluding_runner_sha256"]:
        raise ValueError("amended global report changed more than its runner fingerprint")
    return plan, plan_digest, amendment, effective


def fraction_from_record(value):
    return Fraction(int(value["numerator_hex"], 16), int(value["denominator_hex"], 16))


def assay_variant(summary, corpus, global_result, plan):
    flat, records = corpus["flat_tokens_with_provenance"], corpus["records"]
    for key, value in (("flat_corpus_sha256", flat), ("record_corpus_sha256", records)):
        if hashlib.sha256(encoded(value)).hexdigest() != summary[key] or global_result[key] != summary[key]:
            raise ValueError(f"matched conditional/global corpus digest differs: {key}")
    derived_flat = [{"token": token, "locator": row["locator"], "original_token_index": index}
                    for row in records for token, index in zip(row["tokens"], row["original_token_indices"], strict=True)]
    if flat != derived_flat:
        raise ValueError("flat stream and retained record slots differ")
    tokens = [row["token"] for row in flat]
    observed, diagnostics = counts(tokens), boundary_diagnostics(flat)
    identity = (summary["ring_policy"], summary["f66r_column_unit"])
    if (identity != (global_result["ring_policy"], global_result["f66r_column_unit"])
            or len(tokens) != global_result["tokens"] or len(Counter(tokens)) != global_result["distinct_types"]
            or observed != global_result["observed"] or diagnostics != global_result["observed_boundary_diagnostics"]):
        raise ValueError("observed input/edge population differs from the global assay")
    rows, locators = [row["tokens"] for row in records], [row["locator"] for row in records]
    means = exact_record_means(rows)
    trials = []
    for trial in range(plan["trials"]):
        control = record_controls(rows, locators, summary["record_corpus_sha256"], *identity, plan["seed"], trial)
        flattened = [token for row in control for token in row]
        measured = counts(flattened)
        within = sum(counts(row)["equal_pair_events_A"] for row in control)
        trials.append({"trial": trial, **measured, "within_record_pair_events": within,
                       "cross_record_pair_events": measured["equal_pair_events_A"] - within})
    sampled = {name: Fraction(sum(t[field] for t in trials), len(trials))
               for name, field in (("A", "equal_pair_events_A"), ("B", "distinct_repeating_types_B"))}
    global_means = {name: fraction_from_record(global_result["exact_global_null_means"][name]) for name in ("A", "B")}
    return {
        "ring_policy": identity[0], "f66r_column_unit": identity[1],
        "flat_corpus_sha256": summary["flat_corpus_sha256"], "record_corpus_sha256": summary["record_corpus_sha256"],
        "tokens": len(tokens), "distinct_types": len(Counter(tokens)), "records_including_empty": len(rows),
        "nonempty_records": means["nonempty_records"], "type_record_incidence": means["type_record_incidence"],
        "observed": observed, "observed_boundary_diagnostics": diagnostics,
        "forced_repeating_types_under_conditional_null": means["forced_repeating_types"],
        "exact_conditional_null_means": {name: exact_record(means[name]) for name in ("A", "B")},
        "exact_A_scope_contributions": {"within_record": exact_record(means["A_within_record"]),
                                         "cross_record": exact_record(means["A_cross_record"])},
        "exact_global_null_means": global_result["exact_global_null_means"],
        "conditional_minus_global_mean": {name: exact_record(means[name] - global_means[name]) for name in ("A", "B")},
        "observed_minus_conditional_mean": {name: exact_record(Fraction(observed[field]) - means[name])
                                             for name, field in (("A", "equal_pair_events_A"), ("B", "distinct_repeating_types_B"))},
        "observed_over_exact_conditional_mean": {name: ratio(observed[field], means[name])
                                                for name, field in (("A", "equal_pair_events_A"), ("B", "distinct_repeating_types_B"))},
        "all_ten_controls": trials, "ten_control_means": {name: exact_record(sampled[name]) for name in ("A", "B")},
        "observed_over_ten_control_mean": {name: ratio(observed[field], sampled[name])
                                          for name, field in (("A", "equal_pair_events_A"), ("B", "distinct_repeating_types_B"))},
    }


def run_study(root=ROOT):
    plan, plan_digest, amendment, effective = load_plan(root)
    parsed, corpus = reconstruct(root)
    if parsed != json.loads((root / "research/historical/parsing.json").read_text()):
        raise ValueError("frozen parsing report does not replay")
    baseline = json.loads((root / GLOBAL_REPORT).read_text())
    if baseline["edge_scope"] != EDGE_SCOPE or any(len(rows) != 4 for rows in (parsed["variants"], corpus["variants"], baseline["variants"])):
        raise ValueError("retain the four matched global/conditional variants and identical edge scope")
    results = []
    for summary, variant, global_result in zip(parsed["variants"], corpus["variants"], baseline["variants"], strict=True):
        if (summary["ring_policy"], summary["f66r_column_unit"]) != (variant["ring_policy"], variant["f66r_column_unit"]):
            raise ValueError("reconstructed variant identity/order differs")
        results.append(assay_variant(summary, variant, global_result, plan))
    catalog = json.loads((root / "data/historical/interlinear-16e6.json").read_text())
    return {
        "assay_version": 1, "scope": plan["scope"], "study_plan_sha256": plan_digest,
        "human_plan_sha256": hashlib.sha256((root / "research/historical/RECORD_CONDITIONED_PLAN.md").read_bytes()).hexdigest(),
        "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "metric_helper_sha256": hashlib.sha256(Path(__file__).with_name("record_conditioned_repeated_types.py").read_bytes()).hexdigest(),
        "registered_dependency_hashes": plan["dependency_hashes"], "frozen_dependency_hashes": effective,
        "write_guard_amendment": {"version": 1,
                                  "machine_record_sha256": hashlib.sha256((root / AMENDMENT_PATH).read_bytes()).hexdigest(),
                                  "human_note_sha256": hashlib.sha256((root / AMENDMENT_NOTE).read_bytes()).hexdigest(),
                                  "repaired_global_commit": amendment["repaired_global_commit"]},
        "global_study_pr": plan["global_study_pr"],
        "global_study_commit": plan["global_study_commit"], "source_credit": catalog["credit"], "source_permission": catalog["permission"],
        "seed": plan["seed"], "trials_per_variant": plan["trials"], "algorithm": ALGORITHM,
        "frame": plan["shuffle_frame"], "edge_scope": EDGE_SCOPE, "condition_on": plan["condition_on"], "variants": results,
        "limits": "Matched exposed approximate inputs/edges; no causal attribution, verified physical-line identity, original-author replication, calibrated tail, language or decipherment",
    }


def protect_output(path):
    protected = {ROOT / name for name in FROZEN_PATHS}
    protected.update((ROOT / PLAN_PATH, ROOT / "research/historical/RECORD_CONDITIONED_PLAN.md",
                      ROOT / AMENDMENT_PATH, ROOT / AMENDMENT_NOTE,
                      Path(__file__), Path(__file__).with_name("record_conditioned_repeated_types.py")))
    if any(path.resolve() == source.resolve()
           or path.exists() and source.exists() and path.samefile(source) for source in protected):
        raise ValueError("conditional output must not overwrite frozen inputs, plans, amendments or code")


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
            raise ValueError("native-record-conditioned report differs")
        if args.output:
            payload = json.dumps(result, indent=2, allow_nan=False) + "\n"
            protect_output(args.output)
            args.output.write_text(payload, encoding="utf-8")
        elif not args.check:
            print(json.dumps(result, indent=2, allow_nan=False))
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"historical record-conditioned assay failed: {error}\n")
    if args.check:
        print("historical native-record-conditioned assay reproduces")


if __name__ == "__main__":
    main()
