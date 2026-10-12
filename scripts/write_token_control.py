"""Write token controls while protecting their corpus and calculation code.

The historical shuffle producer remains unchanged for accepted code-hash pins.
This companion calls its existing make_control without changing permutations.
"""

import argparse
import hashlib
import json
from pathlib import Path

try:
    from . import shuffle_token_lines as generator
except ImportError:
    import shuffle_token_lines as generator


def protect_output(output, corpus):
    """Reject existing aliases of the supplied corpus or actually used code."""
    protected = (corpus, Path(__file__), Path(generator.__file__))
    for source in protected:
        if output.resolve() == source.resolve() or (
                output.exists() and source.exists() and output.samefile(source)):
            raise ValueError('control output aliases its original corpus, writer, or shuffle producer')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('corpus', type=Path)
    parser.add_argument('--scope', choices=('line', 'folio-side'), required=True)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--trial', type=int, required=True)
    parser.add_argument('--expected-sha256')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        protect_output(args.output, args.corpus)
        raw = args.corpus.read_bytes()
        if args.expected_sha256 and hashlib.sha256(raw).hexdigest() != args.expected_sha256.lower():
            raise ValueError('input bytes do not match --expected-sha256')
        control = generator.make_control(raw, args.scope, args.seed, args.trial)
        encoded = (json.dumps(control, indent=2, ensure_ascii=False) + '\n').encode('utf-8')
        protect_output(args.output, args.corpus)
        args.output.write_bytes(encoded)
    except (ValueError, TypeError, KeyError, OSError) as error:
        parser.exit(1, f'token control writer failed: {error}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
