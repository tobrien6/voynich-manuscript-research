"""Paired, previously exposed interior-order sensitivity to declared EVA units."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import platform
import sys

try:
    from .audit_transliterations import load_sources
    from . import interior_length_order as original
    from . import interior_half_controls as half
    from .half_control_invariance import classify
    from .eva_unit_sensitivity import ordered_patterns, segment
    from .validate_evaluation_split import load_split_json
except ImportError:
    from audit_transliterations import load_sources
    import interior_length_order as original
    import interior_half_controls as half
    from half_control_invariance import classify
    from eva_unit_sensitivity import ordered_patterns, segment
    from validate_evaluation_split import load_split_json


ROOT = Path(__file__).resolve().parents[1]
METHOD = "paired-interior-eva-unit-controls-v1"
PLAN = "research/transliteration/INTERIOR_UNITS_PLAN.md"
SETTINGS = "research/baselines/eva-unit-protocol.json"
FULL_REPORT = "research/transliteration/interior_length_order.json"
HALF_REPORT = "research/transliteration/interior_half_controls.json"
SEED, TRIALS = 20261011, 999
PINS = {
    FULL_REPORT: "d3ada06de64c80f315ea6fa38f71f25158857cdf0d2a34728d1c6fc6ad7b6a6c",
    HALF_REPORT: "6b239d3a7b52018f6f71bffb07f40df9347bf3c1bf964387378e8c926ce94d6c",
    SETTINGS: "a2ded6526829759169d9462708ea00f969ebe47127acf5c90e2f0b1e7e2fc3ec",
    "data/transliterations.json": "13f5692b57259e50c575f841eb96e351945abf19f94a0c035668dda4c96a5b27",
    "scripts/eva_unit_sensitivity.py": "4a780a8c2d26380951c34bd219d27bd9995ab8c451617dbc68c3bb8feddff4f8",
    "scripts/interior_length_order.py": "729e8a774a889b6370196ab09b56d228f7b3fe4c747f169a5217488453d28c3a",
    "scripts/interior_half_controls.py": "c4f3dfae8540a1aa5bfbf197e62054340bd8ac45c24c1479c66ef9e9882cd583",
    "scripts/half_control_invariance.py": "deb4b167e144b2c8b42348e1fcfbb7b14d2088b027c57b0482aed0c9959e9c0e",
    "scripts/shuffle_token_lines.py": "917b590cde2d190207464ce7a12cfd5e647f4b105cd7648ef57fce5afe957c4f",
    "scripts/eva_token_adapter.py": "71e24940506d1d8ccc7864b9a519fa0aeab8e935ece52bff4a445d47f270aebf",
    "scripts/audit_transliterations.py": "780d3a5e3f36edf61444be1b7c4006dfa84ba4e64c1ec25c3b919fb478a27d5b",
    "scripts/ivtff.py": "8f90c7c90cb7008b8477a8a7b2a093848acf3b36e112d99925e55c023bd59b65",
    "scripts/token_baselines.py": "9a87478647284744d64ba1bf7a7d15bd0bffd2416c5000c396a2d193e2ba532f",
    "scripts/validate_evaluation_split.py": "f967f3ead88326870905fec2e64582b711246bc1bb3e057aba786dfaff5e172d",
}


def corpus_digest(rows):
    return hashlib.sha256(original.compact(rows)).hexdigest()


def pinned_inputs(root=ROOT):
    raw = {}
    for name, expected in PINS.items():
        raw[name] = (root / name).read_bytes()
        if hashlib.sha256(raw[name]).hexdigest() != expected:
            raise ValueError(f"pinned input changed: {name}")
    return {name: load_split_json(raw[name].decode()) for name in
            (FULL_REPORT, HALF_REPORT, SETTINGS, "data/transliterations.json")}


def convert_rows(token_rows, policies, examples):
    """Preserve original token strings/slots; only count interior segments."""
    if not token_rows or len({key for _, key, _ in token_rows}) != len(token_rows):
        raise ValueError("nonempty unique token rows required")
    if [p["id"] for p in policies] != ["ascii_letters", "bench_sequences", "bench_and_minim_sequences"]:
        raise ValueError("exactly the three accepted policies required")
    if policies[0]["patterns"]:
        raise ValueError("ASCII control cannot group letters")
    patterns = [ordered_patterns(p["patterns"]) for p in policies]
    if not set(patterns[1]) <= set(patterns[2]):
        raise ValueError("minim policy must retain bench patterns")
    variants = []
    for policy, matches in zip(policies, patterns):
        rows, hits, uppercase = [], Counter({p: 0 for p in matches}), Counter()
        unlisted = Counter({example: 0 for example in examples})
        letters = segments = tokens = 0
        for page, key, native in token_rows:
            if not isinstance(native, (list, tuple)):
                raise ValueError("original token boundaries require a sequence of tokens")
            # Also checks every endpoint is a valid original plain-Eva token.
            original.interior_lengths(native)
            lengths = []
            for token in native[1:-1]:
                pieces = segment(token, matches)
                if "".join(pieces) != token:
                    raise ValueError("segmentation changed native text")
                lengths.append(len(pieces))
                hits.update(piece for piece in pieces if len(piece) > 1)
                uppercase.update(piece for piece in pieces if len(piece) == 1 and piece.isupper())
                unlisted.update({example: token.count(example) for example in examples})
                tokens += 1
                letters += len(token)
                segments += len(pieces)
            rows.append((page, key, lengths))
        variants.append({"policy_id": policy["id"], "unit": policy["unit"],
                         "matching_precedence": list(matches), "rows": rows,
                         "length_corpus_sha256": corpus_digest(rows),
                         "scope_audit": {"scope": "selected original interior tokens only",
                             "tokens": tokens, "native_ascii_letters": letters, "emitted_segments": segments,
                             "pattern_hits": dict(sorted(hits.items())),
                             "uppercase_single_letter_fallback_counts": dict(sorted(uppercase.items())),
                             "unlisted_example_substring_counts": dict(sorted(unlisted.items()))}})
    return variants


def moments(rows):
    full_effect = original.mean_score(rows)
    full_expectation = math.fsum(original.uncentered_expectation(x) for _, _, x in rows) / len(rows)
    half_exact = sum((half.exact_half_expectation(x) for _, _, x in rows), Fraction(0)) / len(rows)
    shift = float(sum((half.expected_parent_centered(x) for _, _, x in rows), Fraction(0)) / len(rows))
    return {"mean_uncentered_association": full_effect + full_expectation,
            "exact_unrestricted_null_expectation": full_expectation,
            "exact_half_null_expectation": float(half_exact),
            "half_expectation_rational": {"numerator": str(half_exact.numerator), "denominator": str(half_exact.denominator)},
            "unrestricted_centered_association": full_effect,
            "half_centered_association": full_effect - shift,
            "half_minus_unrestricted_expectation": shift}


def apply_indices(rows, indices):
    if len(rows) != len(indices):
        raise ValueError("permutation row count changed")
    result = []
    for (page, key, values), (index_page, index_key, order) in zip(rows, indices):
        if ((page, key) != (index_page, index_key) or any(type(j) is not int for j in order)
                or sorted(order) != list(range(len(values)))):
            raise ValueError("permutation identities or token indices changed")
        result.append((page, key, [values[j] for j in order]))
    return result


def control_summary(observed, controls):
    if not controls:
        raise ValueError("nonempty controls required")
    mean = math.fsum(controls) / len(controls)
    count = sum(abs(value) >= abs(observed) - 1e-12 for value in controls)
    return {"observed_centered_association": observed, "exact_centered_null_expectation": 0.0,
            "control_mean": mean, "control_population_standard_deviation": math.sqrt(
                math.fsum((x - mean) ** 2 for x in controls) / len(controls)),
            "control_statistics": controls, "two_sided_tail_count": count,
            "exploratory_two_sided_tail": (1 + count) / (1 + len(controls))}


def paired_change(grouped, ascii_result):
    if len(grouped["control_statistics"]) != len(ascii_result["control_statistics"]):
        raise ValueError("paired control counts differ")
    observed = grouped["observed_centered_association"] - ascii_result["observed_centered_association"]
    controls = [g - a for g, a in zip(grouped["control_statistics"], ascii_result["control_statistics"])]
    return {"comparison": "grouped minus ASCII; identical token-index permutations",
            **control_summary(observed, controls)}


def analyze(variants, ascii_digest, trials=TRIALS, seed=SEED, progress=None):
    if type(trials) is not int or trials < 1 or type(seed) is not int or seed < 0:
        raise ValueError("positive trials and nonnegative seed required")
    if len(variants) != 3 or corpus_digest(variants[0]["rows"]) != ascii_digest:
        raise ValueError("ASCII draw context does not match the original vectors")
    rows = [v["rows"] for v in variants]
    identities = [[(p, key, len(x)) for p, key, x in items] for items in rows]
    if any(identities[0] != identity for identity in identities[1:]):
        raise ValueError("grouping changed selected identities or slot counts")
    inputs = [moments(items) for items in rows]
    # Generate one original token-index order for all three count policies.
    index_rows = [(page, key, list(range(len(values)))) for page, key, values in rows[0]]
    controls = [{"unrestricted": [], "half": []} for _ in rows]
    for scope, generator in (("unrestricted", original.control_rows), ("half", half.control_rows)):
        for trial in range(trials):
            indices = generator(index_rows, ascii_digest, seed, trial)
            for i, items in enumerate(rows):
                shift = inputs[i]["half_minus_unrestricted_expectation"] if scope == "half" else 0.0
                controls[i][scope].append(original.mean_score(apply_indices(items, indices)) - shift)
            if progress and (trial + 1) % 250 == 0:
                progress(f"{scope}: {trial + 1}/{trials} paired controls")
        if progress:
            progress(f"{scope}: all {trials} paired controls complete")
    results = []
    for i, items in enumerate(rows):
        by_page = defaultdict(list)
        for row in items:
            by_page[row[0]].append(row)
        result = {**inputs[i], "loci": len(items), "source_page_ids": len(by_page),
                  "interior_tokens": sum(len(x) for _, _, x in items),
                  "interior_adjacent_pairs": sum(len(x) - 1 for _, _, x in items),
                  "constant_interior_loci": sum(len(set(x)) == 1 for _, _, x in items),
                  "newly_constant_from_ascii": [key for (_, key, x), (_, _, a) in zip(items, rows[0])
                                                if len(set(x)) == 1 and len(set(a)) > 1],
                  "exact_half_invariance": classify(items),
                  "unrestricted": control_summary(inputs[i]["unrestricted_centered_association"], controls[i]["unrestricted"]),
                  "half": control_summary(inputs[i]["half_centered_association"], controls[i]["half"]),
                  "per_page_descriptive": [{"page_id": page, "loci": len(selected),
                                             **moments(selected)} for page, selected in sorted(by_page.items())]}
        if i:
            result["paired_change_from_ascii"] = {scope: paired_change(result[scope], results[0][scope])
                                                   for scope in ("unrestricted", "half")}
        results.append(result)
    return results


def verify_ascii(result, full, halves):
    if result["loci"] != full["loci"] or result["loci"] != halves["loci"]:
        raise ValueError("ASCII denominator changed")
    for scope, old, observed_key in (("unrestricted", full, "mean_centered_association"),
                                     ("half", halves, "half_centered_association")):
        checks = {"observed_centered_association": old[observed_key],
                  **{name: old[name] for name in ("control_statistics", "control_mean",
                    "control_population_standard_deviation", "two_sided_tail_count", "exploratory_two_sided_tail")}}
        for name, expected in checks.items():
            if result[scope][name] != expected:
                raise ValueError(f"ASCII {scope} reproduction differs: {name}")
    for name in ("mean_uncentered_association", "exact_unrestricted_null_expectation",
                 "exact_half_null_expectation", "half_minus_unrestricted_expectation"):
        if result[name] != halves[name]:
            raise ValueError(f"ASCII exact moment differs: {name}")


def report(progress=None):
    pinned = pinned_inputs()
    full, halves, settings = [pinned[name] for name in (FULL_REPORT, HALF_REPORT, SETTINGS)]
    sources = load_sources()
    if Counter(s["id"] for s, _ in sources if s["id"] in original.SOURCE_IDS) != Counter(original.SOURCE_IDS):
        raise ValueError("exactly one of each paired source required")
    treatments, accepted, selection = original.prepare(sources)
    if selection != full["selection"] or any(selection[key] != value for key, value in halves["selection"].items()):
        raise ValueError("original cohort or exclusion ledger changed")
    provenance = {s["id"]: s for s, _ in sources}
    old_full = {(t["source_id"], t["spacing"]): t for t in full["treatments"]}
    old_half = {(t["source_id"], t["spacing"]): t for t in halves["treatments"]}
    if set(treatments) != set(old_full) or set(treatments) != set(old_half):
        raise ValueError("original treatment inventory changed")
    prepared = []
    for (sid, spacing), mapping in treatments.items():
        token_rows = [(mapping[key]["page_id"], key, mapping[key]["tokens"]) for key in accepted]
        ascii_rows = [(page, key, original.interior_lengths(tokens)) for page, key, tokens in token_rows]
        half.verify_parent(old_full[sid, spacing], provenance[sid], spacing, ascii_rows)
        for name in ("loci", "length_corpus_sha256", "interior_tokens", "interior_adjacent_pairs", "constant_interior_loci"):
            if old_full[sid, spacing][name] != old_half[sid, spacing][name]:
                raise ValueError("original half-control input differs")
        variants = convert_rows(token_rows, settings["policies"], settings["fallback_examples_not_grouped"])
        prepared.append((sid, spacing, variants))
    cache, results = {}, []
    for sid, spacing, variants in prepared:
        ascii_digest = variants[0]["length_corpus_sha256"]
        cache_key = tuple(v["length_corpus_sha256"] for v in variants)
        if cache_key not in cache:
            callback = (lambda message: progress(f"{sid}/{spacing}: {message}")) if progress else None
            cache[cache_key] = analyze(variants, ascii_digest, progress=callback)
        analyzed = cache[cache_key]
        verify_ascii(analyzed[0], old_full[sid, spacing], old_half[sid, spacing])
        results.append({"source_id": sid, "spacing": spacing, "source_sha256": provenance[sid]["sha256"],
                        "source_url": provenance[sid]["url"], "ascii_draw_context_sha256": ascii_digest,
                        "ascii_original_reports_reproduced": True,
                        "unit_policies": [{**{k: v for k, v in converted.items() if k != "rows"}, **measured}
                                          for converted, measured in zip(variants, analyzed)]})
    return {"schema_version": 1, "method": METHOD,
            "status": "post-result unit sensitivity; full corpus and mappings previously exposed",
            "python_version": platform.python_version(), "input_pins": PINS,
            "plan_sha256": hashlib.sha256((ROOT / PLAN).read_bytes()).hexdigest(),
            "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "source_reference": settings["source"], "primary_treatment": "ZL3b/split",
            "selection": {"loci": len(accepted), "cohort_sha256": selection["retained_locus_keys_sha256"]},
            "controls": {"seed": SEED, "trials": TRIALS, "paired_original_token_index_permutations": True,
                         "draw_digest": "original ASCII vectors, not grouped-policy vectors", "tail_resolution_floor": 1 / (TRIALS + 1)},
            "treatments": results}


def protect_output(path, root=ROOT):
    resolved = path.resolve()
    protected = {root / name for name in PINS} | {root / PLAN, Path(__file__).resolve()}
    catalog = root / "data/transliterations.json"
    protected.add(catalog)
    protected.update(root / source["path"] for source in load_split_json(catalog.read_text())["sources"])
    if (resolved.is_relative_to((root / "data").resolve()) or resolved.is_relative_to((root / "scripts").resolve())
            or any(resolved == item.resolve() or (path.exists() and item.exists() and path.samefile(item))
                   for item in protected)):
        raise ValueError("output must not overwrite sources, code, pinned inputs or plan")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--output", type=Path)
    destination.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        if args.output:
            protect_output(args.output, root=ROOT)
        result = report(lambda message: print(message, file=sys.stderr))
        if args.check and result != load_split_json(args.check.read_text()):
            raise ValueError("saved unit-sensitivity report differs from complete replay")
        if args.output:
            protect_output(args.output, root=ROOT)
            args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f"interior unit sensitivity failed: {error}\n")
    print("All 24 paired unit/control combinations verified." if args.check else "All 24 paired unit/control combinations saved.")


if __name__ == "__main__":
    main()
