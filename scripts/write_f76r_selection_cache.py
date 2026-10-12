"""Safely copy a reproduced frozen f76r selection without changing its producer.

This entry point protects generated writes. The historical selector's direct
--output behavior remains unchanged to preserve its pre-inspection code pin.
"""

import argparse
import json
from pathlib import Path
import sys

try:
    from . import select_f76r_anchors as selector
    from . import write_eva_token_cache as cache_writer
except ImportError:
    import select_f76r_anchors as selector
    import write_eva_token_cache as cache_writer


ROOT = selector.ROOT
SNAPSHOT = "research/pilot/f76r-anchor-selection.json"
REVIEW = "research/pilot/f76r-anchor-review.json"


def protected_paths(root, frozen):
    paths = {root / item["path"] for item in frozen["inputs"].values()}
    paths.update(root / "scripts" / name for name in frozen["implementation_sha256"])
    paths.update(root / relative for relative in [SNAPSHOT, REVIEW,
        "scripts/repetition_moments.py", "scripts/write_eva_token_cache.py",
        "scripts/eva_token_adapter.py", "scripts/write_f76r_selection_cache.py"])
    # Also protect the actual imported modules when a caller supplies another root.
    paths.update([Path(__file__), Path(selector.__file__), Path(cache_writer.__file__)])
    return paths


def protect(output, root, frozen):
    cache_writer.protect_output(output, root=root)  # All cataloged sources and raw data.
    for path in protected_paths(root, frozen):
        if output.resolve() == path.resolve() or (output.exists() and path.exists() and output.samefile(path)):
            raise ValueError("selection cache output aliases protected metadata, code, or a frozen record")


def main(argv=None, root=ROOT):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        original = (root / SNAPSHOT).read_bytes()
        frozen = json.loads(original)
        protect(args.output, root, frozen)
        produced = selector.selection(root=root)
        rendered = (json.dumps(produced, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        if rendered != original:
            raise ValueError("current selection differs from frozen bytes; review inputs instead of replacing the record")
        protect(args.output, root, frozen)
        args.output.write_bytes(rendered)
    except (ValueError, OSError, KeyError, TypeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("Wrote byte-identical frozen f76r selection cache; original inputs and records are preserved")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
