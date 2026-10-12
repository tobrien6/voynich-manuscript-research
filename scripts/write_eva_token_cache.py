"""Write conservative Eva caches while preserving pinned source inputs.

The historical adapter script remains unchanged for accepted code-hash pins.
This companion calls its existing producer without changing preprocessing.
"""

import argparse
import json
from pathlib import Path

try:
    from .eva_token_adapter import ROOT, DEFAULT_KINDS, DEFAULT_SOURCES, build
except ImportError:
    from eva_token_adapter import ROOT, DEFAULT_KINDS, DEFAULT_SOURCES, build


def protect_output(output, root=ROOT):
    """Keep generated caches separate from every cataloged input and raw data."""
    catalog_path = root / "data/transliterations.json"
    catalog = json.loads(catalog_path.read_text())
    inputs = [catalog_path, *(root / source["path"] for source in catalog["sources"])]
    resolved = output.resolve()
    if (resolved.is_relative_to((root / "data/raw").resolve()) or
            any(resolved == source.resolve() or
                (output.exists() and source.exists() and output.samefile(source))
                for source in inputs)):
        raise ValueError("cache output must not overwrite the source catalog, pinned inputs, or raw-data directory")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--uncertain-spaces", required=True, choices=("split", "join"))
    parser.add_argument("--source", action="append", help="Repeat to select pinned source IDs; default ZL3b and IT2a")
    parser.add_argument("--kind", action="append", help="Repeat for complete locus types; default P0 and P1")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        protect_output(args.output, root=ROOT)
        result = build(args.uncertain_spaces, args.source or DEFAULT_SOURCES,
                       args.kind or DEFAULT_KINDS, root=ROOT)
        rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
        protect_output(args.output, root=ROOT)
        args.output.write_text(rendered)
    except (ValueError, OSError) as error:
        parser.exit(1, f"token cache writer failed: {error}\n")
    print(f"Wrote {result['summary']['records']} locus records; "
          f"{result['summary']['eligible_records']} eligible under {args.uncertain_spaces} policy.")


if __name__ == "__main__":
    main()
