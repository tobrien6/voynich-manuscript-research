"""Exact moments of the ideal occurrence-permuted interior-half ensemble."""

import argparse
from collections import Counter
from decimal import Context, Decimal, ROUND_HALF_EVEN, localcontext
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path

try:
    from .audit_transliterations import ROOT, load_sources
    from . import interior_length_order as parent
    from .interior_half_controls import exact_centered_score, exact_half_expectation, verify_parent
except ImportError:
    from audit_transliterations import ROOT, load_sources
    import interior_length_order as parent
    from interior_half_controls import exact_centered_score, exact_half_expectation, verify_parent


METHOD = "ideal-half-occurrence-subset-moments-v1"
IMPLEMENTATION_PATH = Path(__file__)
PARENT_NAME = "research/transliteration/interior_length_order.json"
HALF_NAME = "research/transliteration/interior_half_controls.json"
INVARIANCE_NAME = "research/transliteration/half_control_invariance.json"
PLAN_NAME = "research/transliteration/HALF_MOMENTS_PLAN.md"
CATALOG_NAME = "data/transliterations.json"
INPUT_PINS = {
    PARENT_NAME: "d3ada06de64c80f315ea6fa38f71f25158857cdf0d2a34728d1c6fc6ad7b6a6c",
    HALF_NAME: "6b239d3a7b52018f6f71bffb07f40df9347bf3c1bf964387378e8c926ce94d6c",
    INVARIANCE_NAME: "a3e598134b374c50f18b9e5b6027eb54436e7f142bb64a52f21b99c16392f36f",
    PLAN_NAME: "dbe9a87dac8b05f048bc17f0922e2d4c2d77af86570dfe5f8faa3e2b00de2bed",
    CATALOG_NAME: "13f5692b57259e50c575f841eb96e351945abf19f94a0c035668dda4c96a5b27",
    "scripts/audit_transliterations.py": "780d3a5e3f36edf61444be1b7c4006dfa84ba4e64c1ec25c3b919fb478a27d5b",
    "scripts/eva_token_adapter.py": "71e24940506d1d8ccc7864b9a519fa0aeab8e935ece52bff4a445d47f270aebf",
    "scripts/ivtff.py": "8f90c7c90cb7008b8477a8a7b2a093848acf3b36e112d99925e55c023bd59b65",
    "scripts/interior_length_order.py": "729e8a774a889b6370196ab09b56d228f7b3fe4c747f169a5217488453d28c3a",
    "scripts/interior_half_controls.py": "c4f3dfae8540a1aa5bfbf197e62054340bd8ac45c24c1479c66ef9e9882cd583",
    "scripts/shuffle_token_lines.py": "917b590cde2d190207464ce7a12cfd5e647f4b105cd7648ef57fce5afe957c4f",
    "scripts/token_baselines.py": "9a87478647284744d64ba1bf7a7d15bd0bffd2416c5000c396a2d193e2ba532f",
    "scripts/repetition_moments.py": "e758237cc966a4723e3613b8d7cce96e96f685ba682cdc1668558cf153749370",
}


def block_moment(values, exponents):
    """Product moment at distinct block positions, sampling occurrences uniformly.

    The subset coefficient sums injective assignments to labelled positions.
    Updates use the previous occurrence's states, never an in-place state.
    """
    if any(type(value) is not int for value in values):
        raise ValueError("block values must be integers")
    if (any(type(power) is not int or power < 1 for power in exponents)
            or sum(exponents) > 4 or len(exponents) > len(values)):
        raise ValueError("distinct-position exponents must have degree at most four and fit the block")
    count = len(exponents)
    weights = [0] * (1 << count)
    weights[0] = 1
    for value in values:
        previous = weights
        weights = previous.copy()
        powers = [value ** power for power in exponents]
        for mask, weight in enumerate(previous):
            if not weight:
                continue
            for index, power in enumerate(powers):
                bit = 1 << index
                if not mask & bit:
                    weights[mask | bit] += weight * power
    return Fraction(weights[-1], math.prod(range(len(values) - count + 1, len(values) + 1)))


@lru_cache(maxsize=128)
def edge_patterns(size):
    """Immutable multiplicities for edges and ordered pairs of chain edges."""
    if type(size) is not int or size < 3:
        raise ValueError("at least three interior positions required")
    split = (size + 1) // 2

    def signature(positions):
        degrees = Counter(positions)
        return (tuple(sorted(degree for index, degree in degrees.items() if index < split)),
                tuple(sorted(degree for index, degree in degrees.items() if index >= split)))

    edges = [(index, index + 1) for index in range(size - 1)]
    means = Counter(signature(edge) for edge in edges)
    seconds = Counter(signature(left + right) for left in edges for right in edges)
    return tuple(sorted(means.items())), tuple(sorted(seconds.items()))


def locus_moments(lengths):
    """Exact Q and normalized-association moments; no invariant classifier used."""
    size, squared, _ = parent.components(lengths)
    total = sum(lengths)
    deviations = [size * value - total for value in lengths]
    split = (size + 1) // 2
    blocks = (deviations[:split], deviations[split:])
    cache = {}

    def moment(signature):
        product = Fraction(1)
        for block, powers in enumerate(signature):
            key = block, powers
            if key not in cache:
                cache[key] = block_moment(blocks[block], powers)
            product *= cache[key]
        return product

    means, seconds = edge_patterns(size)
    numerator_mean = sum((count * moment(signature) for signature, count in means), Fraction())
    numerator_second = sum((count * moment(signature) for signature, count in seconds), Fraction())
    numerator_variance = numerator_second - numerator_mean ** 2
    if numerator_variance < 0:
        raise ValueError("negative exact numerator variance")
    scale = Fraction(size, (size - 1) * squared) if squared else Fraction()
    association_mean = scale * numerator_mean
    if association_mean != exact_half_expectation(lengths):
        raise ValueError("exact first moment differs from accepted half expectation")
    return {
        "interior_size": size, "early_size": split, "late_size": size - split,
        "squared_deviation_sum": squared,
        "numerator_mean": numerator_mean,
        "numerator_second_moment": numerator_second,
        "numerator_variance": numerator_variance,
        "association_mean": association_mean,
        "association_variance": scale ** 2 * numerator_variance,
    }


def mean_variance(variances):
    """Exact equal-locus variance under independent locus permutations."""
    if not variances or any(value < 0 for value in variances):
        raise ValueError("nonempty nonnegative locus variances required")
    return sum(variances, Fraction()) / len(variances) ** 2


def fraction_record(value):
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def aggregate_fraction_record(value):
    # Exact hex integers avoid changing Python's process-wide decimal digit limit.
    with localcontext(Context(prec=60, rounding=ROUND_HALF_EVEN)):
        decimal = str(Decimal(value.numerator) / Decimal(value.denominator))
    return {"encoding": "base16-integer-strings",
            "numerator": format(value.numerator, "x"),
            "denominator": format(value.denominator, "x"),
            "decimal_60_significant_digits_approx": decimal}


def summarize(rows):
    if not rows or len({(page, key) for page, key, _ in rows}) != len(rows):
        raise ValueError("nonempty unique page/locus identities required")
    per_locus, invariant, variances, means = [], [], [], []
    for page, key, lengths in rows:
        moments = locus_moments(lengths)
        variance = moments["association_variance"]
        variances.append(variance)
        means.append(moments["association_mean"])
        identity = {"page_id": page, "locus_key": key}
        if not variance:
            invariant.append(identity)
        per_locus.append({**identity,
                          **{name: fraction_record(value) if isinstance(value, Fraction) else value
                             for name, value in moments.items()},
                          "exact_invariant": variance == 0})
    aggregate = mean_variance(variances)
    return {
        "loci": len(rows), "accepted_effect_denominator": len(rows),
        "length_corpus_sha256": hashlib.sha256(parent.compact(rows)).hexdigest(),
        "exact_zero_variance_loci": len(invariant), "invariant_identifiers": invariant,
        "exact_mean_uncentered_association": fraction_record(sum(means, Fraction()) / len(rows)),
        "exact_half_centered_ensemble_mean": fraction_record(Fraction()),
        "exact_ideal_mean_variance": aggregate_fraction_record(aggregate),
        "ideal_mean_standard_deviation_approx": math.sqrt(float(aggregate)),
        "per_locus": per_locus,
    }


def verify_inputs():
    loaded = {}
    for name, digest in INPUT_PINS.items():
        raw = (ROOT / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError(f"pinned input changed: {name}")
        if name in (PARENT_NAME, HALF_NAME, INVARIANCE_NAME):
            loaded[name] = json.loads(raw)
    return loaded


def treatment_map(report, expected):
    rows = report["treatments"]
    mapping = {(row["source_id"], row["spacing"]): row for row in rows}
    if len(mapping) != len(rows) or set(mapping) != expected:
        raise ValueError("accepted treatment inventory changed")
    return mapping


def report():
    loaded = verify_inputs()
    original, half, invariance = (loaded[name] for name in (PARENT_NAME, HALF_NAME, INVARIANCE_NAME))
    sources = load_sources()
    treatments, accepted, selection = parent.prepare(sources)
    if selection != original["selection"] or any(
            value != selection[key] for key, value in half["selection"].items()):
        raise ValueError("accepted selection or exclusions changed")
    if (invariance["cohort_loci"] != len(accepted)
            or invariance["retained_locus_keys_sha256"] != selection["retained_locus_keys_sha256"]):
        raise ValueError("accepted invariant cohort changed")
    provenance = {source["id"]: source for source, _ in sources}
    originals, halves, invariants = (treatment_map(value, set(treatments))
                                     for value in (original, half, invariance))
    prepared = []
    # Verify every treatment before calculating any manuscript second moment.
    for treatment, mapping in treatments.items():
        source_id, spacing = treatment
        rows = [(mapping[key]["page_id"], key, parent.interior_lengths(mapping[key]["tokens"]))
                for key in accepted]
        verify_parent(originals[treatment], provenance[source_id], spacing, rows)
        for accepted_report in (halves[treatment], invariants[treatment]):
            for name in ("source_id", "source_sha256", "spacing", "loci", "length_corpus_sha256"):
                if accepted_report[name] != originals[treatment][name]:
                    raise ValueError(f"accepted half/invariance input differs: {name}")
        if invariants[treatment]["accepted_effect_denominator"] != len(rows):
            raise ValueError("accepted invariant denominator differs")
        observed = sum((exact_centered_score(lengths) for _, _, lengths in rows), Fraction()) / len(rows)
        if abs(float(observed) - halves[treatment]["half_centered_association"]) > 1e-12:
            raise ValueError("accepted half-centered observation differs")
        prepared.append((treatment, rows))
    cache, results = {}, []
    for treatment, rows in prepared:
        digest = hashlib.sha256(parent.compact(rows)).hexdigest()
        if digest not in cache:
            cache[digest] = summarize(rows)
        diagnostic = cache[digest]
        if (diagnostic["invariant_identifiers"] != invariants[treatment]["invariant_identifiers"]
                or diagnostic["exact_zero_variance_loci"] != invariants[treatment]["exact_invariant_loci"]):
            raise ValueError("exact zero-variance identifiers differ from accepted swap audit")
        mean = diagnostic["exact_mean_uncentered_association"]
        if abs(float(Fraction(int(mean["numerator"]), int(mean["denominator"])))
               - halves[treatment]["exact_half_null_expectation"]) > 1e-12:
            raise ValueError("exact cohort mean differs from accepted half expectation")
        sd = diagnostic["ideal_mean_standard_deviation_approx"]
        empirical = halves[treatment]["control_population_standard_deviation"]
        source_id, spacing = treatment
        results.append({"source_id": source_id, "spacing": spacing,
                        "source_sha256": provenance[source_id]["sha256"],
                        "source_url": provenance[source_id]["url"],
                        **diagnostic, "accepted_invariant_identifier_match": True,
                        "existing_control_repetitions": half["controls"]["repetitions"],
                        "existing_control_population_standard_deviation": empirical,
                        "empirical_to_ideal_sd_ratio_approx": empirical / sd if sd else None})
    return {
        "schema_version": 1, "method": METHOD,
        "analysis_status": "descriptive exact-moment audit; unchanged previously exposed cohort",
        "primary_treatment": "ZL3b/split", "cohort_loci": len(accepted),
        "retained_locus_keys_sha256": selection["retained_locus_keys_sha256"],
        "input_sha256": INPUT_PINS,
        "implementation_sha256": hashlib.sha256(IMPLEMENTATION_PATH.read_bytes()).hexdigest(),
        "ensemble": "independent ideal uniform occurrence permutations within each original early/late half",
        "variance_scope": "equal-locus mean; independent control permutations do not imply independent manuscript evidence",
        "new_null_draws": 0, "accepted_reports_changed": False, "new_tail_probabilities": 0,
        "finite_controls": "999 deterministic hash controls are a separate finite empirical measure",
        "treatments": results,
    }


def protected_paths(check=None):
    catalog = ROOT / CATALOG_NAME
    paths = [ROOT / name for name in INPUT_PINS]
    paths.extend(ROOT / source["path"] for source in json.loads(catalog.read_text())["sources"])
    paths.extend((catalog, IMPLEMENTATION_PATH))
    if check is not None:
        paths.append(check)
    return paths


def protect_output(output, check=None):
    if output is None:
        return
    resolved = output.resolve()
    for path in protected_paths(check):
        if resolved == path.resolve() or (output.exists() and path.exists() and output.samefile(path)):
            raise ValueError("output must not overwrite an input, implementation, or plan")


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        protect_output(args.output, args.check)
        output_bytes = encoded(report())
        if args.check and output_bytes != args.check.read_bytes():
            raise ValueError("exact-moment report differs from committed bytes")
        if args.output:
            protect_output(args.output, args.check)
            args.output.write_bytes(output_bytes)
        elif not args.check:
            print(output_bytes.decode("utf-8"), end="")
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f"half-control moment audit failed: {error}\n")
    if args.check:
        print("Pinned inputs, exact moments, invariant identifiers and report bytes verified.")


if __name__ == "__main__":
    main()
