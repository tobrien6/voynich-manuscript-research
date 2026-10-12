"""Synthetic entropy accounting on one finite sequence, without manuscript data."""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

try:
    from .representation_entropy_demo import empirical_entropy
except ImportError:
    from representation_entropy_demo import empirical_entropy


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "research/representation/ENTROPY_EDGES_PLAN.md"
SOURCES = ROOT / "research/literature/entropy-methods.json"
EXAMPLES = ("ab", "aab", "aba", "abba", "aaaa", "abcabc")


def count_entropy(counts):
    """Empirical entropy of one explicitly supplied count population."""
    values = list(counts.values())
    if not values or any(type(value) is not int or value <= 0 for value in values):
        raise ValueError("a nonempty population of positive integer counts is required")
    total = sum(values)
    return -math.fsum(value / total * math.log2(value / total) for value in values)


def edge_summary(sequence):
    """Retain all unit/edge counts; the final unit has no outgoing edge."""
    if not isinstance(sequence, (str, list, tuple)) or len(sequence) < 2:
        raise ValueError("at least two atomic units are required")
    units = tuple(sequence)
    if any(not isinstance(unit, str) or not unit for unit in units):
        raise ValueError("atomic units must be nonempty string labels")
    full = Counter(units)
    pairs = Counter(zip(units[:-1], units[1:]))
    predecessors = Counter()
    for (left, _), count in pairs.items():
        predecessors[left] += count
    full_entropy = count_entropy(full)
    pair_entropy = count_entropy(pairs)
    predecessor_entropy = count_entropy(predecessors)
    conditional = empirical_entropy(units, order=1)
    chain_difference = pair_entropy - predecessor_entropy
    if not math.isclose(conditional, chain_difference, abs_tol=1e-12):
        raise ValueError("conditional entropy and matching-marginal chain rule disagree")
    return {
        "units": list(units), "unit_count": len(units), "edge_count": len(units) - 1,
        "last_unit_without_successor": units[-1],
        "full_unit_counts": [{"unit": unit, "count": full[unit]} for unit in sorted(full)],
        "predecessor_counts_from_edges": [
            {"unit": unit, "count": predecessors[unit]} for unit in sorted(predecessors)],
        "directed_pair_counts": [
            {"predecessor": left, "successor": right, "count": count}
            for (left, right), count in sorted(pairs.items())],
        "successor_mass_using_full_unit_denominator": [
            {"unit": unit, "outgoing_count": predecessors[unit], "full_count": full[unit],
             "row_mass": round(predecessors[unit] / full[unit], 12)} for unit in sorted(full)],
        "bits": {
            "full_unit_entropy": round(full_entropy, 12),
            "pair_entropy": round(pair_entropy, 12),
            "edge_predecessor_entropy": round(predecessor_entropy, 12),
            "pair_minus_full_unit_entropy": round(pair_entropy - full_entropy, 12),
            "pair_minus_edge_predecessor_entropy": round(chain_difference, 12),
            "conditional_successor_entropy_on_edges": round(conditional, 12),
            "difference_from_using_full_marginal": round(predecessor_entropy - full_entropy, 12),
        },
    }


def make_report():
    pins = [PLAN, SOURCES, Path(__file__), ROOT / "scripts/representation_entropy_demo.py"]
    return {
        "schema_version": 1, "method": "finite-sequence-entropy-edge-accounting-v1",
        "data_kind": "invented_atomic_labels_only", "manuscript_data_used": False,
        "boundary_rule": "one finite sequence per example; no padding, wraparound or concatenation",
        "unit_definition": "one supplied label; displayed ASCII examples use one letter per label",
        "log_base": 2, "estimator": "unsmoothed empirical counts; no bias correction",
        "interpretation": "matching-marginal conditional entropy is bits per observed successor edge; pair-minus-full uses different count populations",
        "source_comparison": "read-only algebra audit, not execution of external R/package behavior or publication replication",
        "input_pins": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                       for path in pins},
        "examples": [{"example": example, **edge_summary(example)} for example in EXAMPLES],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        protected = {PLAN.resolve(), SOURCES.resolve(), Path(__file__).resolve(),
                     (ROOT / "scripts/representation_entropy_demo.py").resolve()}
        if args.output and args.output.resolve() in protected:
            raise ValueError("output must not overwrite the plan, method sources or implementation")
        report = make_report()
        if args.check and report != json.loads(args.check.read_text(encoding="utf-8")):
            raise ValueError("recorded entropy-edge report differs from replay")
        rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        elif not args.check:
            print(rendered, end="")
        if args.check:
            print("PASS: synthetic counts, matching-marginal identities and input pins reproduce")
    except (ValueError, OSError) as error:
        parser.exit(1, f"entropy-edge accounting failed: {error}\n")


if __name__ == "__main__":
    main()
