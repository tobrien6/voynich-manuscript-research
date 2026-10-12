"""Explore interior Eva notation-length order with endpoint-fixed controls."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

try:
    from .audit_transliterations import ROOT, load_sources
    from .eva_token_adapter import adapt
    from .shuffle_token_lines import ALGORITHM, HashDraws, shuffle
except ImportError:
    from audit_transliterations import ROOT, load_sources
    from eva_token_adapter import adapt
    from shuffle_token_lines import ALGORITHM, HashDraws, shuffle


METHOD = "locus-interior-notation-lengths-v1"
SOURCE_IDS = ("ZL3b", "IT2a")
SPACING = ("split", "join")
SEED = 20261011
REPETITIONS = 999


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def components(lengths):
    """Return exact integer covariance numerator and denominator plus null mean."""
    if len(lengths) < 3 or any(type(x) is not int or x < 1 for x in lengths):
        raise ValueError("at least three positive integer interior lengths required")
    m, total = len(lengths), sum(lengths)
    deviations = [m * x - total for x in lengths]
    squared = sum(x * x for x in deviations)
    adjacent = sum(a * b for a, b in zip(deviations, deviations[1:]))
    return m, squared, adjacent


def score(lengths):
    """Centered adjacent association: exact permutation expectation is zero."""
    m, squared, adjacent = components(lengths)
    return (m * adjacent + squared) / ((m - 1) * squared) if squared else 0.0


def exact_score(lengths):
    m, squared, adjacent = components(lengths)
    return Fraction(m * adjacent + squared, (m - 1) * squared) if squared else Fraction(0)


def uncentered_expectation(lengths):
    m, squared, _ = components(lengths)
    return -1 / (m - 1) if squared else 0.0


def interior_lengths(tokens):
    if len(tokens) < 5 or any(not isinstance(t, str) or not t.isascii()
                             or not t.isalpha() for t in tokens):
        raise ValueError("at least five plain ASCII Eva token strings required")
    return [len(token) for token in tokens[1:-1]]


def mean_score(rows):
    if not rows:
        raise ValueError("empty analysis cohort")
    return math.fsum(score(lengths) for _, _, lengths in rows) / len(rows)


def control_rows(rows, digest, seed, trial):
    if type(seed) is not int or seed < 0 or type(trial) is not int or trial < 0:
        raise ValueError("seed and trial must be nonnegative integers")
    output = []
    for page, key, lengths in rows:
        parameters = [ALGORITHM, digest, METHOD, seed, trial, [page, key]]
        draws = HashDraws(hashlib.sha256(compact(parameters)).digest())
        output.append((page, key, shuffle(lengths, draws)))
    return output


def prepare(sources):
    """Pair the same conservative P0 cohort across all four treatments."""
    available = {source["id"]: (source, document) for source, document in sources}
    if any(source_id not in available for source_id in SOURCE_IDS):
        raise ValueError("both pinned ZL3b and IT2a inputs are required")
    common = set.intersection(*[
        {locus.key for locus in available[source_id][1].loci
         if locus.present and locus.kind == "P0"} for source_id in SOURCE_IDS])
    if not common:
        raise ValueError("no shared present P0 loci")
    treatments = {}
    for source_id in SOURCE_IDS:
        source, document = available[source_id]
        for spacing in SPACING:
            records = adapt(source, document, spacing, kinds=("P0",))
            treatments[(source_id, spacing)] = {r["locus_key"]: r for r in records
                                               if r["locus_key"] in common}
    rejected, reasons, accepted = [], Counter(), []
    after_adapter, after_drawing = 0, 0
    for key in sorted(common):
        exclusions = set()
        records = [mapping[key] for mapping in treatments.values()]
        for treatment, mapping in treatments.items():
            for reason in mapping[key]["exclusion_reasons"]:
                exclusions.add(f"{treatment[0]}/{treatment[1]}:{reason}")
        adapter_ok = all(r["eligible"] for r in records)
        after_adapter += adapter_ok
        drawing_ok = adapter_ok and all(r["drawing_interruption_count"] == 0 for r in records)
        after_drawing += drawing_ok
        if adapter_ok:
            for treatment, mapping in treatments.items():
                if mapping[key]["drawing_interruption_count"]:
                    exclusions.add(f"{treatment[0]}/{treatment[1]}:drawing_interruption")
                if mapping[key]["token_count"] < 5:
                    exclusions.add(f"{treatment[0]}/{treatment[1]}:fewer_than_five_tokens")
        if exclusions:
            rejected.append({"locus_key": key, "reasons": sorted(exclusions)})
            reasons.update(exclusions)
        else:
            accepted.append(key)
    if not accepted:
        raise ValueError("no common eligible loci after exclusions")
    return treatments, accepted, {
        "shared_present_P0_loci": len(common),
        "eligible_in_all_adapters": after_adapter,
        "eligible_after_drawing_exclusion": after_drawing,
        "eligible_after_minimum_token_exclusion": len(accepted),
        "excluded_loci": len(rejected),
        "reason_counts_may_overlap": dict(sorted(reasons.items())),
        "exclusions": rejected,
        "retained_locus_keys": accepted,
        "retained_locus_keys_sha256": hashlib.sha256(compact(accepted)).hexdigest(),
    }


def summarize(mapping, accepted, repetitions, seed):
    if type(repetitions) is not int or repetitions < 1:
        raise ValueError("repetitions must be a positive integer")
    rows = [(mapping[key]["page_id"], key, interior_lengths(mapping[key]["tokens"]))
            for key in accepted]
    digest = hashlib.sha256(compact(rows)).hexdigest()
    observed = mean_score(rows)
    nulls = [mean_score(control_rows(rows, digest, seed, trial)) for trial in range(repetitions)]
    null_mean = math.fsum(nulls) / repetitions
    tail_count = sum(abs(value) >= abs(observed) - 1e-12 for value in nulls)
    expectation = math.fsum(uncentered_expectation(lengths) for _, _, lengths in rows) / len(rows)
    by_page = defaultdict(list)
    for row in rows:
        by_page[row[0]].append(row)
    return {
        "length_corpus_sha256": digest,
        "loci": len(rows),
        "source_page_ids": len(by_page),
        "interior_tokens": sum(len(lengths) for _, _, lengths in rows),
        "interior_adjacent_pairs": sum(len(lengths) - 1 for _, _, lengths in rows),
        "constant_interior_loci": sum(len(set(lengths)) == 1 for _, _, lengths in rows),
        "mean_uncentered_association": observed + expectation,
        "exact_uncentered_null_expectation": expectation,
        "mean_centered_association": observed,
        "exact_centered_null_expectation": 0.0,
        "control_mean": null_mean,
        "control_population_standard_deviation": math.sqrt(
            math.fsum((value - null_mean) ** 2 for value in nulls) / repetitions),
        "two_sided_tail_count": tail_count,
        "exploratory_two_sided_tail": (1 + tail_count) / (repetitions + 1),
        "control_statistics": nulls,
        "per_page_descriptive": [{"page_id": page, "loci": len(page_rows),
                                  "mean_centered_association": mean_score(page_rows)}
                                 for page, page_rows in sorted(by_page.items())],
    }


def report(repetitions=REPETITIONS, seed=SEED):
    sources = load_sources()
    treatments, accepted, selection = prepare(sources)
    provenance = {source["id"]: source for source, _ in sources}
    results = []
    # Reuse identical numerical inputs; IT split/join controls are identical
    # when its spacing policies supply the same length corpus.
    cache = {}
    for (source_id, spacing), mapping in treatments.items():
        rows = [(mapping[key]["page_id"], key, interior_lengths(mapping[key]["tokens"]))
                for key in accepted]
        digest = hashlib.sha256(compact(rows)).hexdigest()
        if digest not in cache:
            cache[digest] = summarize(mapping, accepted, repetitions, seed)
        results.append({"source_id": source_id, "source_sha256": provenance[source_id]["sha256"],
                        "source_url": provenance[source_id]["url"], "spacing": spacing,
                        "source_currier_metadata": dict(sorted(Counter(
                            mapping[key]["variables"].get("L", "unset") for key in accepted).items())),
                        **cache[digest]})
    return {"schema_version": 1, "method": METHOD,
            "analysis_status": "exploratory; previously exposed full corpus",
            "plan_path": "research/transliteration/INTERIOR_ORDER_PLAN.md",
            "primary_treatment": "ZL3b/split", "selection": selection,
            "controls": {"algorithm": ALGORITHM, "seed": seed,
                         "trial_start": 0, "trial_end_inclusive": repetitions - 1,
                         "repetitions": repetitions, "scope": "within locus interior; endpoints fixed"},
            "treatments": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    try:
        if args.output and args.output.resolve() in {(ROOT / source["path"]).resolve()
                                                    for source, _ in load_sources()}:
            raise ValueError("output must not overwrite a pinned source")
        result = report()
        if args.check and result != json.loads(args.check.read_text()):
            raise ValueError("committed interior-order report differs from replay")
        rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            args.output.write_text(rendered)
        elif not args.check:
            print(rendered, end="")
    except (ValueError, OSError) as error:
        parser.exit(1, f"interior-order analysis failed: {error}\n")
    if args.check:
        print("Pinned inputs and committed interior-order report verified.")


if __name__ == "__main__":
    main()
