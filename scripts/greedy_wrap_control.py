"""Exact and sampled synthetic line wrapping; no manuscript parameters or text."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import sys

try:
    from .locus_position_baseline import contrast, null_variance, uniform_index
except ImportError:
    from locus_position_baseline import contrast, null_variance, uniform_index


ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = ROOT / "research/line-wrap/parameters.json"
PROTOCOL = ROOT / "research/line-wrap/PROTOCOL.md"
HELPERS = ("greedy_wrap_control.py", "locus_position_baseline.py", "shuffle_token_lines.py")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def protect_output(destination, inputs):
    """Reject both path and inode aliases before opening any output file."""
    for source in inputs:
        require(destination.resolve() != source.resolve(), "Output cannot overwrite an input or helper")
        if destination.exists() and source.exists():
            require(not destination.samefile(source), "Output aliases an input or helper inode")


def validate_law(support, capacity, separator):
    require(isinstance(support, list) and support and
            all(type(value) is int and value > 0 for value in support)
            and support == sorted(set(support)), "Require unique ascending positive integer lengths")
    require(type(separator) is int and separator >= 0 and type(capacity) is int
            and capacity >= 2 * max(support) + separator,
            "Analysis capacity must guarantee at least two tokens per closed row")


def row_kernel(support, capacity, separator=1):
    """Marginalize fitting paths by occupancy/count; carry each overflow length."""
    validate_law(support, capacity, separator)
    probability = Fraction(1, len(support))
    kernel, rewards, token_count_laws = [], [], []
    for first in support:
        states = defaultdict(Fraction, {(first, 1): Fraction(1)})
        transitions = [Fraction(0) for _ in support]
        reward, count_law = Fraction(0), defaultdict(Fraction)
        for used in range(first, capacity + 1):
            for count in range(1, capacity // min(support) + 1):
                state_probability = states[(used, count)]
                if not state_probability:
                    continue
                for index, incoming in enumerate(support):
                    path_probability = state_probability * probability
                    next_used = used + separator + incoming
                    if next_used <= capacity:
                        states[(next_used, count + 1)] += path_probability
                    else:
                        require(count >= 2, "Unscorable singleton closed row")
                        transitions[index] += path_probability
                        total_letters = used - separator * (count - 1)
                        reward += path_probability * Fraction(count * first - total_letters, count - 1)
                        count_law[count] += path_probability
        require(sum(transitions) == 1 and sum(count_law.values()) == 1, "Incomplete row-path accounting")
        kernel.append(transitions)
        rewards.append(reward)
        token_count_laws.append(dict(sorted(count_law.items())))
    return kernel, rewards, token_count_laws


def communicating_classes(kernel):
    size = len(kernel)
    require(size and all(len(row) == size and all(value >= 0 for value in row)
            and sum(row) == 1 for row in kernel), "Invalid stochastic kernel")
    edges = [{j for j, value in enumerate(row) if value > 0} for row in kernel]
    reach = []
    for start in range(size):
        visited, todo = {start}, [start]
        while todo:
            current = todo.pop()
            for target in edges[current] - visited:
                visited.add(target)
                todo.append(target)
        reach.append(visited)
    classes, remaining = [], set(range(size))
    while remaining:
        first = min(remaining)
        group = {other for other in remaining if other in reach[first] and first in reach[other]}
        classes.append(sorted(group))
        remaining -= group
    closed = [group for group in classes if all(edges[node] <= set(group) for node in group)]
    return classes, closed


def stationary(kernel):
    classes, closed = communicating_classes(kernel)
    require(len(closed) == 1, "Multiple recurrent classes require a declared initial mixture")
    require(any(kernel[index][index] > 0 for index in closed[0]),
            "No recurrent self-transition certificate for this bounded experiment")
    size = len(kernel)
    matrix = [[Fraction(kernel[j][i]) - Fraction(i == j) for j in range(size)] + [Fraction(0)]
              for i in range(size - 1)]
    matrix.append([Fraction(1) for _ in range(size)] + [Fraction(1)])
    for column in range(size):
        pivot = next((row for row in range(column, size) if matrix[row][column]), None)
        require(pivot is not None, "Stationary equations are singular")
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        divisor = matrix[column][column]
        matrix[column] = [value / divisor for value in matrix[column]]
        for row in range(size):
            if row != column:
                factor = matrix[row][column]
                matrix[row] = [left - factor * right for left, right in zip(matrix[row], matrix[column])]
    law = [row[-1] for row in matrix]
    require(sum(law) == 1 and all(value >= 0 for value in law), "Invalid stationary probabilities")
    require(all(sum(law[i] * kernel[i][j] for i in range(size)) == law[j] for j in range(size)),
            "Stationarity equations do not hold exactly")
    require({i for i, value in enumerate(law) if value > 0} == set(closed[0]),
            "Stationary support differs from the unique recurrent class")
    return law, {"communicating_classes_indices": classes, "closed_classes_indices": closed,
                 "stationary_support_indices": [i for i, value in enumerate(law) if value > 0],
                 "aperiodicity_certified_by_recurrent_self_transition": True}


def exact(support, capacity, separator=1):
    kernel, rewards, count_laws = row_kernel(support, capacity, separator)
    law, graph = stationary(kernel)
    expected = sum(weight * reward for weight, reward in zip(law, rewards))
    count_law = defaultdict(Fraction)
    for weight, current in zip(law, count_laws):
        for count, probability in current.items():
            count_law[count] += weight * probability
    return {"state_first_lengths": support,
            "transition_kernel_exact": [[str(value) for value in row] for row in kernel],
            "conditional_equal_row_contrasts_exact": [str(value) for value in rewards],
            "stationary_first_length_probabilities_exact": [str(value) for value in law],
            "stationary_row_token_count_probabilities_exact": {str(key): str(value) for key, value in sorted(count_law.items())},
            "stationary_equal_row_contrast_exact": str(expected),
            "stationary_equal_row_contrast_decimal": round(float(expected), 12),
            "transition_graph": graph}


def wrap(lengths, capacity, separator=1):
    require(type(capacity) is int and capacity > 0 and type(separator) is int and separator >= 0,
            "Invalid row geometry")
    rows, current, used = [], [], 0
    for value in lengths:
        require(type(value) is int and 0 < value <= capacity, "Invalid or overlong token")
        if current and used + separator + value > capacity:
            rows.append(current)
            current, used = [], 0
        if current:
            used += separator
        current.append(value)
        used += value
    return rows, current


def measure(rows):
    require(rows and all(len(row) >= 2 for row in rows), "Need completed rows with at least two tokens")
    count = len(rows)
    return {"completed_rows": count, "retained_token_count": sum(map(len, rows)),
            "row_token_count_frequency": dict(sorted(Counter(map(len, rows)).items())),
            "retained_length_frequency": dict(sorted(Counter(value for row in rows for value in row).items())),
            "first_length_frequency": dict(sorted(Counter(row[0] for row in rows).items())),
            "observed_equal_row_contrast": round(math.fsum(contrast(row) for row in rows) / count, 12),
            "uniform_within_row_conditional_expectation": 0,
            "uniform_within_row_conditional_standard_deviation": round(
                math.sqrt(math.fsum(null_variance(row) for row in rows)) / count, 12),
            "conditional_variance_limit": "Independent within-row index choices; not generative wrapping sampling variance"}


def build(settings):
    require(settings["schema_version"] == 1 and settings["analysis_id"] == "synthetic-greedy-wrapping-control-v1"
            and settings["status"] == "exploratory synthetic control; no manuscript fit", "Unknown control protocol")
    fixed_semantics = {
        "overflow": "append if used + separator + token <= capacity; otherwise close row and carry the same token unchanged",
        "overlong_token": "reject", "minimum_tokens_per_closed_row": 2,
        "final_row": "exclude any row not closed by overflow, including an exactly full final row",
        "weighting": "equal completed row; first token length minus mean other token lengths",
        "seed": "voynich-synthetic-greedy-wrap-v1-2026-10-12",
        "generator": "shared HashDraws uniform_index(len(support), context, zero_based_token_index)",
        "context": "ASCII JSON [seed, law_id] with separators comma and colon",
        "stream_digest": "SHA256 of ASCII JSON length array with separators comma and colon",
        "exact_prediction": "stationary row-boundary Markov kernel and exact rational equal-row reward",
    }
    require(all(settings[key] == value for key, value in fixed_semantics.items()),
            "Version-one mechanism or generator semantics differ")
    require(settings["separator_width"] == 1 and settings["token_count_per_law"] == 100000
            and settings["fixed_chunk_sizes"] == [3, 4, 5], "Version-one run settings differ")
    require(settings["laws"] == [{"id": "two-length", "uniform_support": [2, 3]},
                                   {"id": "five-length", "uniform_support": [2, 3, 4, 5, 6]}],
            "Version-one length laws differ")
    require([(case["id"], case["law_id"], case["capacity"]) for case in settings["cases"]] ==
            [("two-capacity-7", "two-length", 7), ("two-capacity-8", "two-length", 8),
             ("five-capacity-18", "five-length", 18), ("five-capacity-24", "five-length", 24),
             ("five-capacity-30", "five-length", 30)], "All five declared cases must remain")
    calibration = exact([2, 3], 8, settings["separator_width"])
    check = settings["finite_check"]
    require(check["law"] == [2, 3] and check["capacity"] == 8, "Known calibration inputs differ")
    require(calibration["transition_kernel_exact"] == check["transition_kernel"] and
            calibration["stationary_first_length_probabilities_exact"] == check["stationary_start_probabilities"] and
            calibration["conditional_equal_row_contrasts_exact"] == check["conditional_contrasts"] and
            calibration["stationary_equal_row_contrast_exact"] == check["equal_row_contrast"],
            "Known finite calibration differs")
    report = {"schema_version": 1, "analysis_id": settings["analysis_id"], "status": settings["status"],
              "parameters": settings, "streams": [], "cases": [], "fixed_count_controls": []}
    streams = {}
    for law in settings["laws"]:
        ident, support = law["id"], law["uniform_support"]
        context = json.dumps([settings["seed"], ident], ensure_ascii=True, separators=(",", ":")).encode("ascii")
        stream = [support[uniform_index(len(support), context, index)]
                  for index in range(settings["token_count_per_law"])]
        streams[ident] = stream
        report["streams"].append({"law_id": ident, "count": len(stream),
            "context_ascii": context.decode("ascii"),
            "sha256": hashlib.sha256(json.dumps(stream, separators=(",", ":")).encode("ascii")).hexdigest(),
            "length_frequency": dict(sorted(Counter(stream).items())),
            "initial_length": stream[0], "initialization": "First row starts with stream[0]; no burn-in or forced stationary start"})
        for size in settings["fixed_chunk_sizes"]:
            complete_count = len(stream) // size
            rows = [stream[start:start+size] for start in range(0, complete_count * size, size)]
            report["fixed_count_controls"].append({"law_id": ident, "chunk_size": size,
                "exact_iid_equal_row_expectation": "0", "excluded_trailing_lengths": stream[complete_count*size:],
                **measure(rows)})
    for case in settings["cases"]:
        support = next(law["uniform_support"] for law in settings["laws"] if law["id"] == case["law_id"])
        prediction = exact(support, case["capacity"], settings["separator_width"])
        stream = streams[case["law_id"]]
        rows, trailing = wrap(stream, case["capacity"], settings["separator_width"])
        require([value for row in rows for value in row] + trailing == stream, "Wrapping changed the incoming stream")
        sampled = measure(rows)
        sampled["excluded_unclosed_final_lengths"] = trailing
        sampled["observed_minus_stationary_prediction"] = round(
            sampled["observed_equal_row_contrast"] - float(Fraction(prediction["stationary_equal_row_contrast_exact"])), 12)
        report["cases"].append({**case, "exact": prediction, "finite_simulation": sampled})
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parameters", type=Path, default=PARAMETERS)
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--output", type=Path)
    destination.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        protected = {args.parameters, PROTOCOL}
        protected.update(ROOT / "scripts" / name for name in HELPERS)
        if args.output:
            protect_output(args.output, protected)
        raw = args.parameters.read_bytes()
        report = build(json.loads(raw))
        report["input_sha256"] = {"parameters": hashlib.sha256(raw).hexdigest(),
                                  "protocol": hashlib.sha256(PROTOCOL.read_bytes()).hexdigest()}
        report["implementation_sha256"] = {name: hashlib.sha256((ROOT / "scripts" / name).read_bytes()).hexdigest()
                                             for name in HELPERS}
        # Canonical JSON makes integer frequency keys identical on write and replay.
        report = json.loads(json.dumps(report))
        if args.check:
            require(report == json.loads(args.check.read_bytes()), "Synthetic report does not reproduce")
            print("PASS: exact kernels, recurrent classes, streams and all finite controls reproduce")
        else:
            protect_output(args.output, protected)
            args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print("Wrote all five synthetic wrapping cases and six fixed-count controls")
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
