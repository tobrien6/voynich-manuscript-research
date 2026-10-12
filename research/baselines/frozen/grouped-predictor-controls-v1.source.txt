"""Known-process simulations for the fixed, previously exposed grouped estimator."""

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import sys

try:
    from . import grouped_length_prediction as estimator
    from .shuffle_token_lines import HashDraws
except ImportError:
    import grouped_length_prediction as estimator
    from shuffle_token_lines import HashDraws


ROOT = Path(__file__).resolve().parents[1]
METHOD = "grouped-predictor-synthetic-controls-v1"
SEED = 20261012
REPLICATES = 64
CASES = {"independent_uniform": 0, "persistence_quarter": 1,
         "persistence_three_quarters": 3}
PARENT = "research/baselines/grouped-length-prediction.json"
PLAN = "research/baselines/GROUPED_CONTROL_PLAN.md"
PINS = {
    PARENT: "d271a627a4f37f4916f032fd5021cf6e14bcc9c0817337a6aeeccb1f29cc9810",
    "scripts/grouped_length_prediction.py": "3a987a939fb389d25a75dfaf6494b5c3a97467f0bf5fcf846edca7d3eca69fd3",
    "scripts/shuffle_token_lines.py": "917b590cde2d190207464ce7a12cfd5e647f4b105cd7648ef57fce5afe957c4f",
    "scripts/interior_length_order.py": "729e8a774a889b6370196ab09b56d228f7b3fe4c747f169a5217488453d28c3a",
}


def digest(value):
    return hashlib.sha256(estimator.parent.compact(value)).hexdigest()


def layout_from_report(data):
    if data["method"] != "grouped-length-prediction-v1" or data["folds"]["count"] != 5:
        raise ValueError("unsupported parent layout")
    primary = [t for t in data["treatments"] if (t["source_id"], t["spacing"]) == ("ZL3b", "split")]
    if len(primary) != 1:
        raise ValueError("exactly one primary treatment required")
    templates, keys, assignments, members = [], set(), {}, {}
    for group in data["folds"]["group_assignments"]:
        name, fold = group["group_id"], group["fold"]
        if (name in assignments or type(fold) is not int or fold not in range(5)
                or not group["locus_keys"] or len(set(group["locus_keys"])) != len(group["locus_keys"])):
            raise ValueError("invalid group/fold declaration")
        assignments[name] = fold
        for key in group["locus_keys"]:
            if key in members:
                raise ValueError("overlapping group membership")
            members[key] = (name, fold, set(group["source_page_ids"]))
    for row in primary[0]["loci"]:
        key, group, fold = row["locus_key"], row["group_id"], row["fold"]
        count, label, page = row["transitions"], row["source_label"], row["page_id"]
        declared = members.get(key)
        if (key in keys or type(count) is not int or count < 2 or type(fold) is not int
                or not isinstance(label, str) or not label or declared is None
                or declared[:2] != (group, fold) or page not in declared[2]):
            raise ValueError("invalid or inconsistent locus layout")
        keys.add(key)
        templates.append({"key": key, "page": page, "group": group, "label": label,
                          "interior_size": count + 1})
    if (keys != set(members) or len(keys) != data["selection"]["loci"]
            or set(assignments.values()) != set(range(5))):
        raise ValueError("incomplete layout or empty fold")
    return sorted(templates, key=lambda row: row["key"]), assignments


def load_layout(root=ROOT):
    raw = {}
    for path, expected in PINS.items():
        raw[path] = (root / path).read_bytes()
        if hashlib.sha256(raw[path]).hexdigest() != expected:
            raise ValueError(f"pinned input changed: {path}")
    templates, assignments = layout_from_report(json.loads(raw[PARENT]))
    if (len(templates) != 2165 or len(assignments) != 86
            or sum(row["interior_size"] - 1 for row in templates) != 13713):
        raise ValueError("primary layout dimensions changed")
    return templates, assignments


def sequence(size, quarters, draws):
    if type(size) is not int or size < 3 or type(quarters) is not int or quarters not in CASES.values():
        raise ValueError("require at least three classes and one fixed persistence case")
    values = [draws.below(10) + 1]
    for _ in range(size - 1):
        event, candidate = draws.below(4), draws.below(10) + 1
        values.append(values[-1] if event < quarters else candidate)
    return values


def simulate(templates, replicate, case):
    if type(replicate) is not int or replicate not in range(REPLICATES) or case not in CASES:
        raise ValueError("replicate or case is outside the fixed plan")
    rows = []
    for template in templates:
        parameters = [METHOD, SEED, replicate, case, template["key"]]
        key = hashlib.sha256(estimator.parent.compact(parameters)).digest()
        rows.append({name: template[name] for name in ("key", "page", "group", "label")}
                    | {"lengths": sequence(template["interior_size"], CASES[case], HashDraws(key))})
    return rows


def process_probabilities(quarters):
    if type(quarters) is not int or quarters not in CASES.values():
        raise ValueError("unknown fixed process")
    rho = quarters / 4
    return rho + (1 - rho) / 10, (1 - rho) / 10


def ideal_gain(quarters):
    diagonal, off_diagonal = process_probabilities(quarters)
    return diagonal * math.log2(10 * diagonal) + 9 * off_diagonal * math.log2(10 * off_diagonal)


def oracle_score(rows, quarters):
    diagonal, off_diagonal = process_probabilities(quarters)
    gains = []
    matches = 0
    for row in rows:
        values = row["lengths"]
        if len(values) < 3 or any(type(x) is not int or x not in range(1, 11) for x in values):
            raise ValueError("oracle requires generated class sequences")
        for a, b in zip(values, values[1:]):
            matches += a == b
            gains.append(math.log2(10 * (diagonal if a == b else off_diagonal)))
    if not gains:
        raise ValueError("oracle requires transitions")
    count, gain = len(gains), math.fsum(gains)
    baseline = count * math.log2(10)
    return {"transitions": count, "equal_adjacent_classes": matches,
            "uniform_loss_bits": baseline, "known_process_loss_bits": baseline - gain,
            "gain_bits": gain, "gain_bits_per_transition": gain / count}


def compact_evaluation(result):
    # Preserve all fold/group summaries; complete sequences and fitted tables
    # replay from their hashes without repeating them in 192 data sets.
    folds = [{key: value for key, value in fold.items() if key != "fitted_counts"}
             for fold in result["folds"]]
    return {"summary": result["summary"], "folds": folds, "groups": result["groups"]}


def summarize_replicates(records):
    identifiers = [record["replicate"] for record in records]
    if not records or len(set(identifiers)) != len(identifiers):
        raise ValueError("nonempty unique replicates required")
    fields = ("micro_gain_bits_per_transition", "group_macro_gain_bits_per_transition",
              "locus_macro_gain_bits_per_transition")
    result = {"replicates": len(records), "fixed_criterion_hits": sum(
        record["summary"]["fixed_diagnostic_preference"] for record in records)}
    for field in fields:
        values = [record["summary"][field] for record in records]
        result[field] = {"mean": math.fsum(values) / len(values), "min": min(values), "max": max(values)}
    oracle = [record["oracle"]["gain_bits_per_transition"] for record in records]
    result["oracle_gain_bits_per_transition"] = {"mean": math.fsum(oracle) / len(oracle),
                                                "min": min(oracle), "max": max(oracle)}
    return result


def report(progress=None):
    templates, assignments = load_layout()
    cases = []
    for case, quarters in CASES.items():
        records = []
        for replicate in range(REPLICATES):
            rows = simulate(templates, replicate, case)
            evaluated = estimator.evaluate(rows, assignments)
            records.append({"replicate": replicate, "sequence_sha256": digest(rows),
                            "oracle": oracle_score(rows, quarters), **compact_evaluation(evaluated)})
        cases.append({"case": case, "persistence_quarters": quarters,
                      "ideal_stationary_gain_bits_per_transition": ideal_gain(quarters),
                      "summary": summarize_replicates(records), "replicates": records})
        if progress:
            progress(f"Completed {case}: all {REPLICATES} replicates retained")
    return {"schema_version": 1, "method": METHOD, "seed": SEED,
            "status": "synthetic known-process diagnostic; manuscript layout previously exposed",
            "python_version": platform.python_version(), "input_pins": PINS,
            "plan_sha256": hashlib.sha256((ROOT / PLAN).read_bytes()).hexdigest(),
            "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "layout": {"source_treatment": "ZL3b/split", "templates": templates,
                       "group_assignments": assignments, "sha256": digest([templates, assignments])},
            "replicates_per_case": REPLICATES, "total_datasets": len(CASES) * REPLICATES,
            "cases": cases}


def protect_output(path, root=ROOT):
    resolved = path.resolve()
    protected = {root / name for name in PINS} | {root / PLAN, Path(__file__).resolve()}
    if (resolved.is_relative_to((root / "data").resolve())
            or resolved.is_relative_to((root / "scripts").resolve())
            or any(resolved == source.resolve() or
                   (path.exists() and source.exists() and path.samefile(source)) for source in protected)):
        raise ValueError("output must not overwrite data, scripts, parent inputs or plan")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--output", type=Path)
    destination.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        if args.output:
            protect_output(args.output)
        result = report(lambda message: print(message, file=sys.stderr))
        if args.check and result != json.loads(args.check.read_text()):
            raise ValueError("committed synthetic benchmark differs from complete replay")
        if args.output:
            args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f"grouped synthetic controls failed: {error}\n")
    print("All 192 fixed synthetic datasets generated and checked." if args.check
          else "All 192 fixed synthetic datasets saved.")


if __name__ == "__main__":
    main()
