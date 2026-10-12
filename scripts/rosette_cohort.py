"""Check modern rosette metadata cohorts without certifying glyph/region identity."""

from collections import Counter

try:
    from .ivtff import LOCUS
except ImportError:
    from ivtff import LOCUS


MODERN_IDS = ("ZL3b", "IT2a", "GC2a", "RF1b-full", "RF1b-basic")


def selected_page(report, source_id, page_id):
    sources = [source for source in report["modern_sources"] if source["id"] == source_id]
    if len(sources) != 1:
        raise ValueError("require one record for each selected modern export")
    pages = [page for page in sources[0]["pages"] if page["page_id"] == page_id]
    if len(pages) != 1:
        raise ValueError("require one exact native-page summary per selected export")
    page = pages[0]
    if type(page["header_present"]) is not bool or type(page["present_loci"]) is not int or page["present_loci"] < 0:
        raise ValueError("invalid native-page presence/count metadata")
    identifiers = page["present_locus_identifiers"]
    if not isinstance(identifiers, list) or len(identifiers) != page["present_loci"]:
        raise ValueError("present-locus count differs from its identifier list")
    keys, kinds = {}, Counter()
    for identifier in identifiers:
        match = LOCUS.fullmatch("<" + identifier + ">") if isinstance(identifier, str) else None
        if match is None or match[6]:
            raise ValueError("invalid present native-locus identifier")
        named_page, number, locator, kind, transcriber, _ = match.groups()
        if named_page != page_id or locator == "!" or transcriber is not None:
            raise ValueError("wrong-page, nonexistent or interlinear identifier in modern present cohort")
        key = f"{named_page}.{number}"
        if key in keys:
            raise ValueError("duplicate native key in modern present cohort")
        keys[key] = (kind, locator)
        kinds[kind] += 1
    if not page["header_present"] and keys:
        raise ValueError("present native keys without a page header")
    declared_kinds = page["present_loci_by_kind"]
    if not isinstance(declared_kinds, dict) or any(type(value) is not int or value <= 0 for value in declared_kinds.values()):
        raise ValueError("invalid native kind-count metadata")
    if dict(kinds) != declared_kinds:
        raise ValueError("native kind counts differ from present identifiers")
    return page, keys


def check(report, left, right, page_id="fRos"):
    if left not in MODERN_IDS or right not in MODERN_IDS:
        raise ValueError("unknown modern export selection")
    if left == right:
        raise ValueError("require two distinct modern export identifiers")
    left_page, a = selected_page(report, left, page_id)
    right_page, b = selected_page(report, right, page_id)
    order = lambda key: int(key.rsplit(".", 1)[1])
    shared = sorted(a.keys() & b.keys(), key=order)
    left_only = sorted(a.keys() - b.keys(), key=order)
    right_only = sorted(b.keys() - a.keys(), key=order)
    kind_differences = [key for key in shared if a[key][0] != b[key][0]]
    locator_differences = [key for key in shared if a[key][1] != b[key][1]]
    errors = []
    for sid, page, keys in ((left, left_page, a), (right, right_page, b)):
        if not page["header_present"]:
            errors.append(f"{sid}: absent exact native-page header")
        elif not keys:
            errors.append(f"{sid}: empty present native-key cohort")
    if left_only or right_only:
        errors.append(f"native key sets differ: {len(left_only)} only in {left}; {len(right_only)} only in {right}")
    if kind_differences or locator_differences:
        errors.append(f"shared metadata differs: {len(kind_differences)} kinds; {len(locator_differences)} locators")
    return {"left": left, "right": right, "page_id": page_id, "shared_key_count": len(shared),
            "left_only_keys": left_only, "right_only_keys": right_only,
            "shared_kind_disagreements": kind_differences, "shared_locator_disagreements": locator_differences,
            "errors": errors,
            "scope": "equal nonempty modern key/kind/locator cohorts only; no glyph, region, historical-key or source-independence certification"}
