"""Write the frozen repeating-type mean with guards around calculation/serialization.

The original producer and its scientific fingerprints are unchanged.
"""

import argparse
from pathlib import Path

try:
    from . import repeating_types as producer
except ImportError:
    import repeating_types as producer


def protected_inputs():
    catalog = producer.ROOT / 'data/transliterations.json'
    paths = [catalog, producer.ROOT / producer.PLAN, producer.ROOT / producer.BASELINE,
             *(producer.ROOT / path for path in producer.ENGINES),
             producer.ROOT / 'scripts/write_repeating_types.py',
             Path(__file__), Path(producer.__file__)]
    paths.extend(producer.ROOT / source['path']
                 for source in producer.load_split_json(catalog.read_text())['sources'])
    return tuple(paths)


def protect_output(output, inputs):
    for source in inputs:
        if output.resolve() == source.resolve() or (
                output.exists() and source.exists() and output.samefile(source)):
            raise ValueError('mean output aliases a source, baseline, plan, producer or writer')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--output', type=Path)
    mode.add_argument('--check', type=Path)
    args = parser.parse_args(argv)
    try:
        original_inputs = protected_inputs() if args.output else ()
        if args.output:
            protect_output(args.output, original_inputs)
        result = producer.report()
        payload = producer.encoded(result)
        if args.check:
            if producer.encoded(producer.load_split_json(args.check.read_text())) != payload:
                raise ValueError('recorded repeating-type mean differs from complete producer replay')
            print('Frozen repeating-type mean and all accepted diagnostics verified.')
        else:
            # Keep entry paths even if the catalog changes during calculation,
            # and include current declared paths. Serialization is already done.
            protect_output(args.output, (*original_inputs, *protected_inputs()))
            args.output.write_bytes(payload)
            print('Wrote repeating-type mean through the guarded companion.')
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'repeating-type mean writer failed: {error}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
