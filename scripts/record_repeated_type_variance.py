"""Exact deduplicated B variance with native-record joining state preserved."""

from collections import Counter, defaultdict
from decimal import Context, Decimal, localcontext, MAX_EMAX, MIN_EMIN
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import comb, isfinite

try:
    from .record_conditioned_repeated_types import validate_rows, run_no_repeat
except ImportError:
    from record_conditioned_repeated_types import validate_rows, run_no_repeat


@lru_cache(maxsize=8192, typed=True)
def two_type_endpoints(m, ca, cb):
    """No AA/BB internal event; retain first/last U/A/B categories exactly."""
    if any(type(v) is not int for v in (m, ca, cb)) or m < 1 or min(ca, cb) < 0 or ca + cb > m:
        raise ValueError("require integer record length m>=1 and feasible two-type counts")
    sizes = (m - ca - cb, ca, cb)
    if m == 1:
        return tuple(tuple(Fraction(int(a == b and sizes[a] == 1)) for b in range(3)) for a in range(3))
    if ca <= 1 and cb <= 1:
        return tuple(tuple(Fraction(sizes[a] * (sizes[b] - int(a == b)), m * (m - 1))
                           for b in range(3)) for a in range(3))
    if ca > m - ca + 1 or cb > m - cb + 1:
        return tuple((Fraction(0),) * 3 for _ in range(3))
    states = {(0, 0, -1, -1): 1}
    for processed in range(m):
        following = defaultdict(int)
        for (a, b, first, last), count in states.items():
            used = (processed - a - b, a, b)
            for color in range(3):
                if used[color] >= sizes[color] or color != 0 and last == color:
                    continue
                key = (a + int(color == 1), b + int(color == 2), color if first == -1 else first, color)
                following[key] += count
        states = following
    denominator = comb(m, ca) * comb(m - ca, cb)
    entries = Counter()
    for (a, b, first, last), count in states.items():
        if (a, b) == (ca, cb):
            entries[first, last] += count
    return tuple(tuple(Fraction(entries[a, b], denominator) for b in range(3)) for a in range(3))


@lru_cache(maxsize=8192)
def _joint_run(shape):
    previous = (Fraction(1), Fraction(0), Fraction(0))
    for m, ca, cb in shape:
        matrix = two_type_endpoints(m, ca, cb)
        total = sum(previous, Fraction(0))
        previous = tuple(total * sum((matrix[a][b] for a in range(3)), Fraction(0))
                         - previous[1] * matrix[1][b] - previous[2] * matrix[2][b] for b in range(3))
        if not any(previous):
            return Fraction(0)
    result = sum(previous, Fraction(0))
    if not 0 <= result <= 1:
        raise ValueError("joint no-event transfer probability is invalid")
    return result


def joint_no_repeat(shape):
    if not isinstance(shape, (list, tuple)):
        raise ValueError("provide a sequence of nonempty record length/count triples")
    for row in shape:
        if (not isinstance(row, (list, tuple)) or len(row) != 3 or any(type(v) is not int for v in row)
                or row[0] < 1 or min(row[1:]) < 0 or sum(row[1:]) > row[0]):
            raise ValueError("invalid joint record shape")
    shape = tuple(tuple(row) for row in shape)
    swapped = tuple((m, b, a) for m, a, b in shape)
    return _joint_run(min(shape, swapped))


def single_type_runs(bags):
    lengths = [sum(bag.values()) for bag in bags]
    domains = defaultdict(list)
    for i, bag in enumerate(bags):
        for token, c in bag.items():
            domains[token].append((i, lengths[i], c))
    runs, absent = {}, {}
    membership = [{} for _ in bags]
    for token, entries in domains.items():
        parts, pending = [], []
        previous_index = -2
        for entry in entries:
            if pending and entry[0] != previous_index + 1:
                parts.append(pending)
                pending = []
            pending.append(entry)
            previous_index = entry[0]
        parts.append(pending)
        runs[token] = []
        absent[token] = Fraction(1)
        for index, part in enumerate(parts):
            q = run_no_repeat(tuple((m, c) for _, m, c in part))
            runs[token].append({"start": part[0][0], "end": part[-1][0], "q": q})
            absent[token] *= q
            for row_index, _, _ in part:
                membership[row_index][token] = index
    return lengths, runs, absent, membership


def overlap_components(edges):
    neighbors = defaultdict(set)
    for a, b in edges:
        neighbors[0, a].add((1, b))
        neighbors[1, b].add((0, a))
    unseen = set(neighbors)
    components = []
    while unseen:
        pending = [min(unseen)]
        component = set()
        while pending:
            node = pending.pop()
            if node in component:
                continue
            component.add(node)
            unseen.discard(node)
            pending.extend(neighbors[node] - component)
        components.append(sorted(component))
    return components


def exact_type_variance(rows):
    validate_rows(rows)
    bags = [Counter(row) for row in rows if row]
    lengths, runs, absent, membership = single_type_runs(bags)
    variable = {token for token, q in absent.items() if 0 < q < 1}
    overlaps = defaultdict(set)
    for i, bag in enumerate(bags):
        for a, b in combinations(sorted(variable & bag.keys()), 2):
            overlaps[a, b].add((membership[i][a], membership[i][b]))
    marginal = sum((q * (1 - q) for q in absent.values()), Fraction(0))
    covariance_sum = Fraction(0)
    signs = Counter({"positive": 0, "negative": 0, "zero": 0})
    evaluated = skipped = 0
    for (a, b), edges in sorted(overlaps.items()):
        correction = Fraction(1)
        for component in overlap_components(edges):
            selected = [(color, runs[a if color == 0 else b][i]) for color, i in component]
            if any(all(run["q"] == 1 for owner, run in selected if owner == color) for color in (0, 1)):
                skipped += 1
                continue  # One indicator cannot repeat anywhere in this component.
            denominator = Fraction(1)
            for _, run in selected:
                denominator *= run["q"]
            if not denominator:
                raise ValueError("constant indicator entered variable pair calculation")
            start, end = min(run["start"] for _, run in selected), max(run["end"] for _, run in selected)
            shape = tuple((lengths[i], bags[i].get(a, 0), bags[i].get(b, 0)) for i in range(start, end + 1))
            correction *= joint_no_repeat(shape) / denominator
            evaluated += 1
        covariance = absent[a] * absent[b] * (correction - 1) if correction != 1 else Fraction(0)
        covariance_sum += covariance
        signs["positive" if covariance > 0 else "negative" if covariance < 0 else "zero"] += 1
    variance = marginal + 2 * covariance_sum
    if not 0 <= variance <= Fraction(len(variable) ** 2, 4):
        raise ValueError("deduplicated type variance is outside its possible range")
    return {"mean_B": sum((1 - q for q in absent.values()), Fraction(0)),
            "marginal_variance_sum": marginal, "type_pair_covariance_sum": covariance_sum,
            "twice_covariance_adjustment": 2 * covariance_sum, "variance_B": variance,
            "distinct_types": len(absent), "nonempty_records": len(bags),
            "zero_repeat_probability_types": sum(q == 1 for q in absent.values()),
            "forced_repeating_types": sum(q == 0 for q in absent.values()), "variable_indicator_types": len(variable),
            "all_variable_indicator_pairs": len(variable) * (len(variable) - 1) // 2,
            "variable_pairs_sharing_records": len(overlaps),
            "disjoint_record_variable_pairs": len(variable) * (len(variable) - 1) // 2 - len(overlaps),
            "positive_covariance_pairs": signs["positive"], "negative_covariance_pairs": signs["negative"],
            "zero_covariance_shared_pairs": signs["zero"],
            "joint_components_evaluated": evaluated, "components_with_inactive_side_skipped": skipped}


def spread_diagnostics(variance, centered, precision=50):
    variance, centered = Fraction(variance), Fraction(centered)
    if type(precision) is not int or precision != 50 or variance < 0 or variance == 0 and centered != 0:
        raise ValueError("invalid variance, constant-control contrast or diagnostic precision")
    with localcontext(Context(prec=precision, Emax=MAX_EMAX, Emin=MIN_EMIN)):
        value = Decimal(variance.numerator) / Decimal(variance.denominator)
        sd = value.sqrt()
        scaled = (Decimal(centered.numerator) / Decimal(centered.denominator) / sd) if variance else None
    def display(number):
        if number is None:
            return None
        candidate = float(number)
        return candidate if isfinite(candidate) and (candidate != 0 or number == 0) else None
    return {"zero_conditional_variance": variance == 0, "variance_decimal": str(value),
            "standard_deviation_decimal": str(sd), "centered_B_in_conditional_SD_decimal": str(scaled) if scaled is not None else None,
            "variance_approx": display(value), "standard_deviation_approx": display(sd),
            "centered_B_in_conditional_SD_approx": display(scaled), "decimal_precision": precision,
            "interpretation": "Conditional scale only; no normal tail, confidence, significance or mechanism probability"}
