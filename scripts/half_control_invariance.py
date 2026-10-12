"""Classify exact statistic invariance under the accepted interior-half controls."""

import argparse
from collections import Counter
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

try:
    from .audit_transliterations import ROOT, load_sources
    from . import interior_length_order as parent
    from .interior_half_controls import halves, verify_parent, PARENT_SHA256
except ImportError:
    from audit_transliterations import ROOT, load_sources
    import interior_length_order as parent
    from interior_half_controls import halves, verify_parent, PARENT_SHA256


METHOD = "half-control-adjacent-swap-feasibility-v1"
HALF_SHA256 = "6b239d3a7b52018f6f71bffb07f40df9347bf3c1bf964387378e8c926ce94d6c"
PARENT_PATH = ROOT / "research/transliteration/interior_length_order.json"
HALF_PATH = ROOT / "research/transliteration/interior_half_controls.json"
PLAN_PATH = ROOT / "research/transliteration/HALF_DEGENERACY_PLAN.md"


def variation_witness(lengths):
    """Return two permitted arrangements with different scores, or None.

    Adjacent within-block swaps generate the full allowed permutation set.
    Every feasible neighboring-value assignment is checked with multiplicities.
    A missing neighbor contributes zero to the adjacent-product change.
    """
    m, squared, _ = parent.components(lengths)
    if not squared:
        return None
    total = sum(lengths)
    deviations = [m * x - total for x in lengths]
    split = (m + 1) // 2
    block_counts = [Counter(block) for block in halves(deviations)]

    def owner(position):
        if not 0 <= position < m:
            return None
        return int(position >= split)

    for block, (start, end) in enumerate(((0, split), (split, m))):
        for a, b in combinations(sorted(block_counts[block]), 2):
            remaining = [bag.copy() for bag in block_counts]
            remaining[block].subtract((a, b))
            for position in range(start, end - 1):
                neighbors = (position - 1, position + 2)
                owners = [owner(index) for index in neighbors]
                choices = [[0] if which is None else sorted(
                    value for value, count in remaining[which].items() if count > 0)
                    for which in owners]
                for left, right in product(*choices):
                    if left == right:
                        continue
                    needed = [Counter(), Counter()]
                    for which, value in zip(owners, (left, right)):
                        if which is not None:
                            needed[which][value] += 1
                    if any(count > remaining[which][value]
                           for which, bag in enumerate(needed)
                           for value, count in bag.items()):
                        continue
                    arranged = [None] * m
                    arranged[position:position + 2] = (a, b)
                    for index, which, value in zip(neighbors, owners, (left, right)):
                        if which is not None:
                            arranged[index] = value
                    for which, (lo, hi) in enumerate(((0, split), (split, m))):
                        unused = remaining[which] - needed[which]
                        values = iter(sorted(unused.elements()))
                        for index in range(lo, hi):
                            if arranged[index] is None:
                                arranged[index] = next(values)
                    before = [(value + total) // m for value in arranged]
                    after = before.copy()
                    after[position], after[position + 1] = after[position + 1], after[position]
                    # Verify the complete numerator, not just its local formula.
                    if parent.components(before)[2] == parent.components(after)[2]:
                        raise ValueError("internal witness did not change the statistic")
                    return before, after
    return None


def classify(rows):
    if not rows or len({(page, key) for page, key, _ in rows}) != len(rows):
        raise ValueError("nonempty rows with unique page/locus identities required")
    invariant, narrow, additional = [], [], []
    invariant_sizes, additional_sizes = Counter(), Counter()
    for page, key, lengths in rows:
        witness = variation_witness(lengths)
        both_constant = all(len(set(block)) == 1 for block in halves(lengths))
        item = {"page_id": page, "locus_key": key}
        if both_constant:
            narrow.append(item)
            if witness is not None:
                raise ValueError("constant-half statistic has a variation witness")
        if witness is None:
            invariant.append(item)
            invariant_sizes[len(lengths)] += 1
            if not both_constant:
                additional.append(item)
                additional_sizes[len(lengths)] += 1
    return {
        "loci": len(rows),
        "length_corpus_sha256": hashlib.sha256(parent.compact(rows)).hexdigest(),
        "both_half_constant_loci": len(narrow),
        "exact_invariant_loci": len(invariant),
        "additional_invariant_loci": len(additional),
        "varying_loci_with_verified_witness": len(rows) - len(invariant),
        "invariant_identifiers": invariant,
        "additional_invariant_identifiers": additional,
        "invariant_interior_size_counts": {str(size): count for size, count in sorted(invariant_sizes.items())},
        "additional_invariant_interior_size_counts": {str(size): count for size, count in sorted(additional_sizes.items())},
        "accepted_effect_denominator": len(rows),
    }


def pinned_json(path, digest):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError("pinned report changed; review and version this diagnostic")
    return json.loads(data)


def report():
    original = pinned_json(PARENT_PATH, PARENT_SHA256)
    half = pinned_json(HALF_PATH, HALF_SHA256)
    sources = load_sources()
    treatments, accepted, selection = parent.prepare(sources)
    if selection != original["selection"]:
        raise ValueError("parent selection or exclusions changed")
    if any(value != selection[key] for key, value in half["selection"].items()):
        raise ValueError("half-control selection changed")
    provenance = {source["id"]: source for source, _ in sources}
    originals = {(t["source_id"], t["spacing"]): t for t in original["treatments"]}
    halves_report = {(t["source_id"], t["spacing"]): t for t in half["treatments"]}
    if set(originals) != set(treatments) or set(halves_report) != set(treatments):
        raise ValueError("pinned treatment inventory changed")
    # Verify every treatment before inspecting classifications on source material.
    prepared = []
    for treatment, mapping in treatments.items():
        source_id, spacing = treatment
        rows = [(mapping[key]["page_id"], key, parent.interior_lengths(mapping[key]["tokens"]))
                for key in accepted]
        verify_parent(originals[treatment], provenance[source_id], spacing, rows)
        for key in ("loci", "length_corpus_sha256", "interior_tokens",
                    "interior_adjacent_pairs", "constant_interior_loci"):
            if originals[treatment][key] != halves_report[treatment][key]:
                raise ValueError(f"half-control input differs: {key}")
        prepared.append((treatment, rows))
    cache, results = {}, []
    for treatment, rows in prepared:
        digest = hashlib.sha256(parent.compact(rows)).hexdigest()
        if digest not in cache:
            cache[digest] = classify(rows)
        diagnostic = cache[digest]
        if diagnostic["both_half_constant_loci"] != halves_report[treatment]["both_half_constant_loci"]:
            raise ValueError("accepted narrow count differs from replay")
        source_id, spacing = treatment
        results.append({"source_id": source_id, "source_sha256": provenance[source_id]["sha256"],
                        "spacing": spacing, **diagnostic})
    return {
        "schema_version": 1, "method": METHOD,
        "analysis_status": "exploratory diagnostic; unchanged exposed source cohort",
        "plan_sha256": hashlib.sha256(PLAN_PATH.read_bytes()).hexdigest(),
        "parent_report_sha256": PARENT_SHA256, "half_report_sha256": HALF_SHA256,
        "retained_locus_keys_sha256": selection["retained_locus_keys_sha256"],
        "cohort_loci": len(accepted),
        "statistical_results_changed": False, "new_null_draws": 0,
        "treatments": results,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        catalog = ROOT / "data/transliterations.json"
        protected = {PARENT_PATH.resolve(), HALF_PATH.resolve(), PLAN_PATH.resolve(), catalog.resolve()}
        protected.update((ROOT / source["path"]).resolve()
                         for source in json.loads(catalog.read_text())["sources"])
        if args.output and args.output.resolve() in protected:
            raise ValueError("output must not overwrite a pinned input or plan")
        result = report()
        if args.check and result != json.loads(args.check.read_text()):
            raise ValueError("invariance diagnostic differs from committed report")
        rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.write_text(rendered, encoding="utf-8")
        elif not args.check:
            print(rendered, end="")
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f"half-control invariance audit failed: {error}\n")
    if args.check:
        print("Exact half-control invariance diagnostic reproduces.")


if __name__ == "__main__":
    main()
