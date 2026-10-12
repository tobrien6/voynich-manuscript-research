"""Retain a fixed new B-control block and both inclusive finite-rank scores."""

from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from decimal import Context, Decimal, localcontext, MAX_EMAX, MIN_EMIN, ROUND_HALF_EVEN
from fractions import Fraction
import argparse
import hashlib
import json
import multiprocessing
from pathlib import Path

try:
    from . import historical_record_conditioned as parent
    from .reconstruct_historical_tokens import reconstruct, encoded
    from .global_repeated_types import counts, boundary_diagnostics, exact_record
    from .record_conditioned_repeated_types import record_controls
except ImportError:
    import historical_record_conditioned as parent
    from reconstruct_historical_tokens import reconstruct, encoded
    from global_repeated_types import counts, boundary_diagnostics, exact_record
    from record_conditioned_repeated_types import record_controls


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = "research/historical/type-tails-plan.json"
HUMAN_PLAN = "research/historical/TYPE_TAILS_PLAN.md"
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


def display_fraction(value, precision=50):
    if type(precision) is not int or precision != 50:
        raise ValueError("use the declared 50-digit display precision")
    value = Fraction(value)
    with localcontext(Context(prec=precision, rounding=ROUND_HALF_EVEN, Emax=MAX_EMAX, Emin=MIN_EMIN)):
        decimal = Decimal(value.numerator) / Decimal(value.denominator)
    return {**exact_record(value), "decimal_50_digits": str(decimal)}


def tail_summary(observed, mean, values, precision=50):
    if (type(observed) is not int or observed < 0 or not isinstance(mean, (int, Fraction)) or type(mean) is bool
            or not isinstance(values, (list, tuple)) or not values or any(type(v) is not int or v < 0 for v in values)):
        raise ValueError("require nonnegative integer B observations/controls and an exact mean")
    mean = Fraction(mean)
    if mean < 0:
        raise ValueError("B's exact mean must be nonnegative")
    distance = abs(Fraction(observed) - mean)
    upper = sum(value >= observed for value in values)
    centered = sum(abs(Fraction(value) - mean) >= distance for value in values)
    total = len(values)
    sample_mean = Fraction(sum(values), total)
    sample_variance = ((Fraction(sum(v * v for v in values), 1) - total * sample_mean * sample_mean) / (total - 1)
                       if total > 1 else None)
    def score(exceedances, ties):
        return {"inclusive_exceedances": exceedances, "ties_at_observed_score": ties,
                "raw_frequency": display_fraction(Fraction(exceedances, total), precision),
                "plus_one_rank_score": display_fraction(Fraction(exceedances + 1, total + 1), precision)}
    return {"new_trials": total, "observed_B": observed, "exact_parent_mean_B": display_fraction(mean, precision),
            "absolute_observed_minus_parent_mean": display_fraction(distance, precision),
            "upper_tail": score(upper, sum(v == observed for v in values)),
            "centered_two_sided": score(centered, sum(abs(Fraction(v) - mean) == distance for v in values)),
            "new_control_mean_B": display_fraction(sample_mean, precision),
            "new_unbiased_sample_variance_B": display_fraction(sample_variance, precision) if sample_variance is not None else None,
            "B_histogram": {str(v): count for v, count in sorted(Counter(values).items())},
            "minimum_plus_one_score": display_fraction(Fraction(1, total + 1), precision)}


def load_plan(root):
    plan = read_json(root / PLAN_PATH)
    integers = {"plan_version": 1, "seed": 20261012, "new_trials": 1000, "first_new_trial": 10,
                "last_new_trial": 1009, "process_workers": 4, "decimal_precision": 50}
    if (any(type(plan.get(k)) is not int or plan[k] != v for k, v in integers.items())
            or plan.get("include_all_parser_variants") is not True or plan.get("retain_asterisks") is not True
            or plan.get("tail_definitions") != ["B_control >= B_observed", "abs(B_control - exact_parent_mean) >= abs(B_observed - exact_parent_mean)"]
            or plan.get("rank_score") != "(inclusive_exceedances + 1) / (new_trials + 1)"
            or plan.get("shuffle_frame") != "historical-native-record-v1" or plan.get("algorithm") != parent.ALGORITHM
            or plan.get("edge_scope") != parent.EDGE_SCOPE or plan.get("adaptive_stopping") is not False
            or plan.get("significance_threshold", "missing") is not None or plan.get("depend_on_variance_report") is not False
            or set(plan.get("dependency_hashes", {})) != set(FROZEN_PATHS)):
        raise ValueError("unsupported fixed-block historical tail plan")
    for name in FROZEN_PATHS:
        if hashlib.sha256((root / name).read_bytes()).hexdigest() != plan["dependency_hashes"][name]:
            raise ValueError(f"frozen tail-study dependency differs: {name}")
    return plan


def sample_case(payload):
    summary, corpus, reference, plan = payload
    records, flat = corpus["records"], corpus["flat_tokens_with_provenance"]
    for key, content in (("record_corpus_sha256", records), ("flat_corpus_sha256", flat)):
        if hashlib.sha256(encoded(content)).hexdigest() != summary[key] or reference[key] != summary[key]:
            raise ValueError("tail/parent corpus digest differs")
    rebuilt = [{"token": token, "locator": row["locator"], "original_token_index": i}
               for row in records for token, i in zip(row["tokens"], row["original_token_indices"], strict=True)]
    if strict(rebuilt) != strict(flat):
        raise ValueError("tail record/flat provenance differs")
    tokens = [r["token"] for r in flat]
    observed, diagnostics = counts(tokens), boundary_diagnostics(flat)
    identity = (summary["ring_policy"], summary["f66r_column_unit"])
    if (identity != (reference["ring_policy"], reference["f66r_column_unit"])
            or type(reference["tokens"]) is not int or reference["tokens"] != len(tokens)
            or type(reference["distinct_types"]) is not int or reference["distinct_types"] != len(set(tokens))
            or strict(observed) != strict(reference["observed"]) or strict(diagnostics) != strict(reference["observed_boundary_diagnostics"])
            or [row["trial"] for row in reference["all_ten_controls"]] != list(range(10))):
        raise ValueError("tail input/edge population or original controls differ")
    if (any(type(plan[k]) is not int for k in ("new_trials", "first_new_trial", "last_new_trial", "seed"))
            or plan["new_trials"] < 1 or plan["first_new_trial"] < 10
            or plan["last_new_trial"] != plan["first_new_trial"] + plan["new_trials"] - 1):
        raise ValueError("new trial block must be complete and disjoint from original controls")
    rows, locators = [r["tokens"] for r in records], [r["locator"] for r in records]
    trials = []
    for trial in range(plan["first_new_trial"], plan["last_new_trial"] + 1):
        control = record_controls(rows, locators, summary["record_corpus_sha256"], *identity, plan["seed"], trial)
        control_tokens = [token for row in control for token in row]
        measured = counts(control_tokens)
        if measured["distinct_repeating_types_B"] < reference["forced_repeating_types_under_conditional_null"]:
            raise ValueError("control lost a mathematically forced repeated type")
        trials.append({"trial": trial, "flat_control_token_vector_sha256": hashlib.sha256(encoded(control_tokens)).hexdigest(), **measured})
    return {"ring_policy": identity[0], "f66r_column_unit": identity[1],
            "record_corpus_sha256": summary["record_corpus_sha256"], "flat_corpus_sha256": summary["flat_corpus_sha256"],
            "tokens": len(tokens), "distinct_types": len(set(tokens)), "observed": observed,
            "observed_boundary_diagnostics": diagnostics, "original_ten_controls": reference["all_ten_controls"],
            "all_new_control_trials": trials,
            "distinct_new_control_hashes": len({row["flat_control_token_vector_sha256"] for row in trials}),
            "tail_summary": tail_summary(observed["distinct_repeating_types_B"],
                                         parent.fraction_from_record(reference["exact_conditional_null_means"]["B"]),
                                         [row["distinct_repeating_types_B"] for row in trials], plan["decimal_precision"])}


def execute_cases(payloads, workers=4):
    if type(workers) is not int or workers not in (1, 4):
        raise ValueError("use serial validation or four fixed case workers")
    if workers == 1:
        return [sample_case(payload) for payload in payloads]
    with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("spawn")) as pool:
        return list(pool.map(sample_case, payloads))


def run_study(root=ROOT):
    plan = load_plan(root)
    reference = read_json(root / MEAN_REPORT)
    if strict(parent.run_study(root)) != strict(reference):
        raise ValueError("complete accepted mean/control report does not replay")
    parsed, corpus = reconstruct(root)
    if any(len(rows) != 4 for rows in (parsed["variants"], corpus["variants"], reference["variants"])):
        raise ValueError("retain all four parent/tail variants")
    payloads = []
    for summary, variant, prior in zip(parsed["variants"], corpus["variants"], reference["variants"], strict=True):
        if (summary["ring_policy"], summary["f66r_column_unit"]) != (variant["ring_policy"], variant["f66r_column_unit"]):
            raise ValueError("tail source variant identity/order differs")
        payloads.append((summary, variant, prior, plan))
    results = execute_cases(payloads, plan["process_workers"])
    return {"assay_version": 1, "scope": plan["scope"], "plan_sha256": hashlib.sha256((root / PLAN_PATH).read_bytes()).hexdigest(),
            "human_plan_sha256": hashlib.sha256((root / HUMAN_PLAN).read_bytes()).hexdigest(),
            "producer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "frozen_dependency_hashes": plan["dependency_hashes"], "parent_pr": plan["parent_pr"], "parent_commit": plan["parent_commit"],
            "source_credit": reference["source_credit"], "source_permission": reference["source_permission"],
            "seed": plan["seed"], "new_trials_per_variant": plan["new_trials"],
            "new_trial_range": [plan["first_new_trial"], plan["last_new_trial"]], "process_workers": plan["process_workers"],
            "algorithm": plan["algorithm"], "shuffle_frame": plan["shuffle_frame"], "edge_scope": plan["edge_scope"],
            "tail_definitions": plan["tail_definitions"], "method_reference": plan["method_reference"], "variants": results,
            "limits": "Exposed approximate inputs and deterministic pseudorandom controls; empirical frequencies/plus-one ranks, not exhaustive tails, verified ideal randomization, fresh discovery tests, independent variants, confidence, mechanism probabilities, physical glyphs or decipherment"}


def protect_output(path):
    sources = [ROOT / n for n in (*FROZEN_PATHS, PLAN_PATH, HUMAN_PLAN)] + [Path(__file__)]
    if any(path.resolve() == source.resolve() or path.exists() and source.exists() and path.samefile(source) for source in sources):
        raise ValueError("tail output aliases a frozen source, parent, plan or producer")


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
            raise ValueError("complete fixed-block historical tail report differs")
        if args.output:
            payload = json.dumps(result, indent=2, allow_nan=False) + "\n"
            protect_output(args.output)
            args.output.write_text(payload, encoding="utf-8")
        elif not args.check:
            print(json.dumps(result, indent=2, allow_nan=False))
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"historical tail study failed: {error}\n")
    if args.check:
        print("complete fixed-block historical tail report reproduces")


if __name__ == "__main__":
    main()
