"""Explore interior notation order while preserving each locus's half profiles."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

try:
    from .audit_transliterations import ROOT, load_sources
    from . import interior_length_order as parent
    from .shuffle_token_lines import ALGORITHM, HashDraws, shuffle
except ImportError:
    from audit_transliterations import ROOT, load_sources
    import interior_length_order as parent
    from shuffle_token_lines import ALGORITHM, HashDraws, shuffle


METHOD = "locus-interior-half-blocks-v1"
PARENT_PATH = ROOT / "research/transliteration/interior_length_order.json"
PARENT_SHA256 = "d3ada06de64c80f315ea6fa38f71f25158857cdf0d2a34728d1c6fc6ad7b6a6c"
PLAN_PATH = ROOT / "research/transliteration/INTERIOR_HALVES_PLAN.md"


def halves(values):
    if len(values) < 3:
        raise ValueError("at least three interior lengths required")
    k = (len(values) + 1) // 2
    return values[:k], values[k:]


def exact_half_expectation(lengths):
    """Expected uncentered association under independent half permutations."""
    m, squared, _ = parent.components(lengths)
    if not squared:
        return Fraction(0)
    deviations = [m * x - sum(lengths) for x in lengths]
    early, late = halves(deviations)
    expected_adjacent = sum((Fraction(sum(block) ** 2 - sum(x * x for x in block), len(block))
                             for block in (early, late)), Fraction(0))
    expected_adjacent += Fraction(sum(early) * sum(late), len(early) * len(late))
    return Fraction(m, (m - 1) * squared) * expected_adjacent


def exact_centered_score(lengths):
    m, squared, adjacent = parent.components(lengths)
    if not squared:
        return Fraction(0)
    return Fraction(m * adjacent, (m - 1) * squared) - exact_half_expectation(lengths)


def expected_parent_centered(lengths):
    m, squared, _ = parent.components(lengths)
    return exact_half_expectation(lengths) + Fraction(1, m - 1) if squared else Fraction(0)


def control_rows(rows, digest, seed, trial):
    if type(seed) is not int or seed < 0 or type(trial) is not int or trial < 0:
        raise ValueError("seed and trial must be nonnegative integers")
    result = []
    for page, locus, lengths in rows:
        blocks = []
        for block_index, block in enumerate(halves(lengths)):
            params = [ALGORITHM, digest, METHOD, seed, trial, [page, locus, block_index]]
            draws = HashDraws(hashlib.sha256(parent.compact(params)).digest())
            blocks.append(shuffle(block, draws))
        result.append((page, locus, blocks[0] + blocks[1]))
    return result


def verify_parent(original, source, spacing, rows):
    """Fail before controls if the exact original treatment cannot be recreated."""
    checks = {
        "source_id": source["id"], "source_sha256": source["sha256"], "spacing": spacing,
        "loci": len(rows), "length_corpus_sha256": hashlib.sha256(parent.compact(rows)).hexdigest(),
        "interior_tokens": sum(len(x) for _, _, x in rows),
        "interior_adjacent_pairs": sum(len(x) - 1 for _, _, x in rows),
        "constant_interior_loci": sum(len(set(x)) == 1 for _, _, x in rows),
        "source_page_ids": len({page for page, _, _ in rows}),
    }
    for name, expected in checks.items():
        if original.get(name) != expected:
            raise ValueError(f"parent treatment mismatch: {name}")
    if abs(original["mean_centered_association"] - parent.mean_score(rows)) > 1e-12:
        raise ValueError("parent observed statistic mismatch")
    expectation = math.fsum(parent.uncentered_expectation(x) for _, _, x in rows) / len(rows)
    if abs(original["exact_uncentered_null_expectation"] - expectation) > 1e-12:
        raise ValueError("parent exact expectation mismatch")


def summarize(rows, repetitions=999, seed=20261011):
    if not rows or type(repetitions) is not int or repetitions < 1:
        raise ValueError("nonempty cohort and positive repetitions required")
    digest = hashlib.sha256(parent.compact(rows)).hexdigest()
    # Block moments, D, and the expectation are invariant under the controls;
    # compute their exact values once, before the trial loop.
    expectations = [exact_half_expectation(x) for _, _, x in rows]
    full_expectation = math.fsum(parent.uncentered_expectation(x) for _, _, x in rows) / len(rows)
    half_expectation = float(sum(expectations, Fraction(0)) / len(rows))
    parent_effect = parent.mean_score(rows)
    expectation_shift = float(sum((expected_parent_centered(x) for _, _, x in rows), Fraction(0)) / len(rows))
    observed = parent_effect - expectation_shift
    nulls = [parent.mean_score(control_rows(rows, digest, seed, trial)) - expectation_shift
             for trial in range(repetitions)]
    tail_count = sum(abs(x) >= abs(observed) - 1e-12 for x in nulls)
    null_mean = math.fsum(nulls) / repetitions
    by_page = defaultdict(list)
    for row, expectation in zip(rows, expectations):
        by_page[row[0]].append((row, expectation))
    page_results = []
    for page, items in sorted(by_page.items()):
        page_rows = [row for row, _ in items]
        page_shift = float(sum((expected_parent_centered(x) for _, _, x in page_rows), Fraction(0)) / len(items))
        page_results.append({"page_id": page, "loci": len(items),
                             "mean_half_centered_association": parent.mean_score(page_rows) - page_shift})
    sizes = Counter((len(halves(x)[0]), len(halves(x)[1])) for _, _, x in rows)
    return {
        "length_corpus_sha256": digest, "loci": len(rows), "source_page_ids": len(by_page),
        "interior_tokens": sum(len(x) for _, _, x in rows),
        "interior_adjacent_pairs": sum(len(x) - 1 for _, _, x in rows),
        "constant_interior_loci": sum(len(set(x)) == 1 for _, _, x in rows),
        "both_half_constant_loci": sum(all(len(set(b)) == 1 for b in halves(x)) for _, _, x in rows),
        "degeneracy_count_scope": "both halves individually constant; other invariant statistics may exist",
        "half_size_distribution": [{"early": a, "late": b, "loci": n} for (a, b), n in sorted(sizes.items())],
        "mean_uncentered_association": parent_effect + full_expectation,
        "exact_unrestricted_null_expectation": full_expectation,
        "exact_half_null_expectation": half_expectation,
        "unrestricted_centered_association": parent_effect,
        "half_centered_association": observed,
        "half_minus_unrestricted_expectation": expectation_shift,
        "exact_half_centered_null_expectation": 0.0,
        "control_mean": null_mean,
        "control_population_standard_deviation": math.sqrt(
            math.fsum((x - null_mean) ** 2 for x in nulls) / repetitions),
        "control_statistics": nulls, "two_sided_tail_count": tail_count,
        "exploratory_two_sided_tail": (1 + tail_count) / (repetitions + 1),
        "per_page_descriptive": page_results,
    }


def report():
    raw_parent = PARENT_PATH.read_bytes()
    if hashlib.sha256(raw_parent).hexdigest() != PARENT_SHA256:
        raise ValueError("pinned parent report changed; review and version the analysis")
    original = json.loads(raw_parent)
    sources = load_sources()
    treatments, accepted, selection = parent.prepare(sources)
    if selection != original["selection"]:
        raise ValueError("parent cohort or exclusions changed")
    provenance = {source["id"]: source for source, _ in sources}
    original_treatments = {(t["source_id"], t["spacing"]): t for t in original["treatments"]}
    if set(original_treatments) != set(treatments):
        raise ValueError("parent source/spacing treatments changed")
    # Verify every original input before executing any new control.
    prepared = []
    for (source_id, spacing), mapping in treatments.items():
        rows = [(mapping[key]["page_id"], key, parent.interior_lengths(mapping[key]["tokens"]))
                for key in accepted]
        verify_parent(original_treatments[(source_id, spacing)], provenance[source_id], spacing, rows)
        prepared.append((source_id, spacing, mapping, rows))
    cache, results = {}, []
    for source_id, spacing, mapping, rows in prepared:
        digest = hashlib.sha256(parent.compact(rows)).hexdigest()
        if digest not in cache:
            cache[digest] = summarize(rows)
        results.append({"source_id": source_id, "source_sha256": provenance[source_id]["sha256"],
                        "source_url": provenance[source_id]["url"], "spacing": spacing,
                        "source_currier_metadata": dict(sorted(Counter(
                            mapping[key]["variables"].get("L", "unset") for key in accepted).items())),
                        **cache[digest]})
    return {
        "schema_version": 1, "method": METHOD,
        "analysis_status": "exploratory follow-up; parent result and full corpus previously exposed",
        "primary_treatment": "ZL3b/split", "plan_sha256": hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest(),
        "parent_report_sha256": PARENT_SHA256,
        "selection": {k: selection[k] for k in ("shared_present_P0_loci", "eligible_after_minimum_token_exclusion",
                                                "excluded_loci", "retained_locus_keys", "retained_locus_keys_sha256")},
        "controls": {"algorithm": ALGORITHM, "seed": 20261011, "repetitions": 999,
                     "trial_start": 0, "trial_end_inclusive": 998,
                     "scope": "independent early/late interior-half permutations; endpoints fixed"},
        "treatments": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        protected = {PARENT_PATH.resolve(), PLAN_PATH.resolve(), (ROOT / "data/transliterations.json").resolve()}
        protected.update((ROOT / source["path"]).resolve() for source in json.loads(
            (ROOT / "data/transliterations.json").read_text())["sources"])
        if args.output and args.output.resolve() in protected:
            raise ValueError("output must not overwrite a pinned input or plan")
        result = report()
        if args.check and result != json.loads(args.check.read_text()):
            raise ValueError("committed half-position report differs from replay")
        rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.write_text(rendered)
        elif not args.check:
            print(rendered, end="")
    except (ValueError, OSError) as error:
        parser.exit(1, f"half-position analysis failed: {error}\n")
    if args.check:
        print("Pinned parent, unchanged cohort and full half-position report verified.")


if __name__ == "__main__":
    main()
