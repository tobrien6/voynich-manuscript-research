"""Create or strictly check the frozen default seven-record 67r checklist.

The accepted collector and report format remain unchanged. This companion
refuses protected output paths and creates new reports exclusively.
"""

import argparse
import json
from pathlib import Path
import unicodedata

try:
    from . import audit_transliterations as audit
    from . import build_67r_review as producer
    from . import ivtff
    from . import validate_evaluation_split as strict_json
except ImportError:
    import audit_transliterations as audit
    import build_67r_review as producer
    import ivtff
    import validate_evaluation_split as strict_json


CONTEXT = (
    'data/transliterations.json',
    'research/panel-regions/f67r-proposal.json',
    'research/panel-regions/f67r-p0-review.json',
)
ENGINES = (
    'scripts/build_67r_review.py',
    'scripts/write_67r_review.py',
    'scripts/audit_transliterations.py',
    'scripts/ivtff.py',
    'scripts/validate_evaluation_split.py',
)


def protected_inputs():
    """Retain both declared paths and their current resolved destinations."""
    root = producer.ROOT
    catalog = strict_json.load_split_json((root / CONTEXT[0]).read_text(encoding='utf-8'))
    paths = [root / name for name in (*CONTEXT, *ENGINES)]
    paths.extend(root / source['path'] for source in catalog['sources'])
    paths.extend(Path(module.__file__) for module in (producer, audit, ivtff, strict_json))
    paths.append(Path(__file__))
    return tuple(path for source in paths for path in (source, source.resolve()))


def protected_directories():
    return tuple((producer.ROOT / name).resolve() for name in ('data', 'scripts'))


def protect_output(output, inputs, directories):
    resolved = output.resolve()
    if any(resolved.is_relative_to(directory) or (
            directory.exists() and any(parent.exists() and parent.samefile(directory)
                                       for parent in resolved.parents))
           for directory in directories):
        raise ValueError('new report must be outside the data and scripts directories')
    for source in inputs:
        same_named_entry = (
            unicodedata.normalize('NFC', resolved.name).casefold()
            == unicodedata.normalize('NFC', source.name).casefold()
            and resolved.parent.exists() and source.parent.exists()
            and resolved.parent.samefile(source.parent))
        if resolved == source.resolve() or same_named_entry or (
                output.exists() and source.exists() and output.samefile(source)):
            raise ValueError('new report aliases an input, accepted checklist or executing module')
    if output.exists() or output.is_symlink():
        raise ValueError('new report destination already exists, including symbolic links')


def rendered(report):
    # Preserve the frozen collector's field order, indentation and final newline.
    return (json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')


def typed_identity(report):
    # JSON encoding distinguishes True/1 and 1/1.0, unlike Python equality.
    return json.dumps(report, sort_keys=True, ensure_ascii=False, allow_nan=False,
                      separators=(',', ':'))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--new-report', type=Path, help='create a new file; never replace a destination')
    mode.add_argument('--check', type=Path, help='compare every field and JSON type without writing')
    args = parser.parse_args(argv)
    try:
        entry_inputs = protected_inputs()
        entry_directories = protected_directories()
        if args.new_report:
            protect_output(args.new_report, entry_inputs, entry_directories)
        report = producer.build(root=producer.ROOT)
        payload = rendered(report)
        if args.check:
            recorded = strict_json.load_split_json(args.check.read_text(encoding='utf-8'))
            if typed_identity(recorded) != typed_identity(report):
                raise ValueError('complete typed 67r checklist differs from source replay')
            print('PASS: source pins and complete typed seven-record 67r checklist reproduce')
        else:
            # Calculation and serialization are complete. Keep the entry snapshots
            # even when the catalog or a symlink changes, and add current paths.
            protect_output(args.new_report, (*entry_inputs, *protected_inputs()),
                           (*entry_directories, *protected_directories()))
            with args.new_report.open('xb') as stream:
                stream.write(payload)
            print('Wrote a new seven-record 67r checklist through the guarded companion')
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
        parser.exit(1, f'67r checklist writer failed: {error}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
