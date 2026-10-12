"""Display all frozen native maximizing partners; no new entropy calculation."""
import argparse
from copy import deepcopy
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import io
import json
from pathlib import Path
import platform

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'research/literature/native-substitution-normalizations.json'
REPORT_SHA = '07ebfc89fc44aefc95aa7dda2d399010ccbd0a7a707c563c9a2bed1954ac453d'
STEM = 'native-substitution-rankings'
METRICS = ('subset', 'whole')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def figure_data(record):
    alphabet = record['native_alphabet']
    if (type(record['schema_version']) is not int or record['schema_version'] != 1
            or record['method'] != 'complete native B substitution normalizations v1'
            or alphabet != sorted(set(alphabet)) or len(alphabet) != 35
            or any(not isinstance(c, str) or len(c) != 1 for c in alphabet)
            or type(record['token_occurrences']) is not int or record['token_occurrences'] != 17597
            or type(record['native_word_types']) is not int or record['native_word_types'] != 3920):
        raise ValueError('complete frozen native population required')
    expected = [(source, metric) for source in alphabet for metric in METRICS]
    if [(r['source_symbol'], r['metric']) for r in record['rankings']] != expected:
        raise ValueError('all70 ordered maximizing records required')
    pairs = {tuple(p['symbols']): p for p in record['pairs']}
    if len(record['pairs']) != 595 or set(pairs) != {
            (a, b) for a in alphabet for b in alphabet if a < b}:
        raise ValueError('all595 unique pair records required')
    comparisons = record['normalization_comparisons']
    if [r['source_symbol'] for r in comparisons] != alphabet:
        raise ValueError('all35 ordered normalization comparisons required')
    rows = []
    for index, source in enumerate(alphabet):
        plots = {}
        for metric in METRICS:
            saved = record['rankings'][2 * index + METRICS.index(metric)]
            candidates = {other: pairs[tuple(sorted((source, other)))] for other in alphabet if other != source}
            if type(saved['candidate_count']) is not int or saved['candidate_count'] != 34:
                raise ValueError('complete candidate denominator required')
            if any(not isinstance(pair[metric + '_score_bits_decimal_80digits'], str) for pair in candidates.values()):
                raise ValueError('recorded decimal strings required')
            scores = {other: Decimal(pair[metric + '_score_bits_decimal_80digits']) for other, pair in candidates.items()}
            if any(not score.is_finite() or score < 0 for score in scores.values()):
                raise ValueError('finite nonnegative recorded scores required')
            maximum = max(scores.values())
            if not isinstance(saved['maximum_bits_20dp'], str) or saved['maximum_bits_20dp'] != format(maximum, '.20f'):
                raise ValueError('displayed maximum differs from recorded pair scores')
            leader = min(other for other, score in scores.items() if score == maximum)
            signatures = {other: tuple((p['prime'], Fraction(p['exponent'], pair['selected_occurrences'] if metric == 'subset' else pair['all_occurrences']))
                                      for p in pair['information_prime_exponents']) for other, pair in candidates.items()}
            ties = sorted(other for other, signature in signatures.items() if signature == signatures[leader])
            with localcontext() as context:
                context.prec = 80
                possible = sorted(other for other, score in scores.items() if abs(maximum - score) <= Decimal('1e-60'))
            if any(signatures[other] != signatures[leader] for other in possible):
                raise ValueError('unresolved maximum needs a new display version')
            status = 'resolved_positive' if maximum else 'no_positive_optimum'
            positive = ties if maximum else []
            if saved['status'] != status or saved['positive_maximizers'] != positive or saved['possible_maximizers'] != ties:
                raise ValueError('maximizing partners or zero-optimum state differs')
            winners = []
            for target in positive:
                pair = candidates[target]
                winners.append({'partner': target, 'affected_occurrences': pair['selected_occurrences'],
                                'all_occurrences': pair['all_occurrences'],
                                'score_bits_decimal_80digits': pair[metric + '_score_bits_decimal_80digits']})
            plots[metric] = {'ranking': deepcopy(saved), 'score_x': float(maximum), 'winners': winners}
        changed = plots['subset']['ranking']['positive_maximizers'] != plots['whole']['ranking']['positive_maximizers']
        comparison = comparisons[index]
        if (comparison['different_positive_maximizer_sets'] is not changed
                or any(comparison[metric + '_positive_maximizers'] != plots[metric]['ranking']['positive_maximizers'] for metric in METRICS)):
            raise ValueError('normalization comparison differs from complete rankings')
        rows.append({'source_symbol': source, 'source_codepoint': f'U+{ord(source):04X}',
                     'maximizing_sets_differ': changed, **plots})
    maximum = max(row[metric]['score_x'] for row in rows for metric in METRICS)
    return {'schema_version': 1, 'input_report_sha256': REPORT_SHA,
            'token_occurrences': record['token_occurrences'], 'native_word_types': record['native_word_types'],
            'native_symbols': len(alphabet), 'pair_records': len(pairs),
            'changed_maximizing_sets': sum(r['maximizing_sets_differ'] for r in rows),
            'rows': rows, 'shared_x_limits': [0.0, maximum * 1.48],
            'scope': '70 existing maxima over35 notation codepoints; no new corpus measurement, physical mapping or decipherment'}


def read_data():
    raw = REPORT.read_bytes()
    if digest(raw) != REPORT_SHA:
        raise ValueError('accepted native comparison report changed')
    return figure_data(json.loads(raw))


def render(data):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    import numpy
    import PIL
    colors = {'same': '#246C94', 'changed': '#B9630D', 'zero': '#687685'}
    artists = []
    with plt.rc_context({'font.family': 'DejaVu Sans', 'font.size': 10,
                         'svg.hashsalt': STEM, 'svg.fonttype': 'none'}):
        fig, axes = plt.subplots(1, 2, figsize=(15.5, 14.4), sharex=True, sharey=True)
        fig.subplots_adjust(left=.13, right=.98, top=.835, bottom=.11, wspace=.16)
        for column, metric in enumerate(METRICS):
            ax = axes[column]
            for y, row in enumerate(data['rows']):
                value = row[metric]; x = value['score_x']; winners = value['winners']
                color = colors['zero'] if not winners else colors['changed'] if row['maximizing_sets_differ'] else colors['same']
                bar = ax.barh(y, x, height=.42, color=color)[0]
                if winners:
                    label = '; '.join(f"'{w['partner']}' · {Decimal(w['score_bits_decimal_80digits']):.6f} · T={w['affected_occurrences']:,}" for w in winners)
                else:
                    ax.scatter([0], [y], marker='s', facecolors='none', edgecolors=color, s=28, clip_on=False)
                    label = 'no positive optimum'
                ax.text(x + data['shared_x_limits'][1] * .012, y, label, va='center', fontsize=9, color='#28333D')
                artists.append({'source_symbol': row['source_symbol'], 'metric': metric,
                                'bar_x': float(bar.get_width()), 'bar_center_y': float(bar.get_y() + bar.get_height() / 2),
                                'positive_partners': [w['partner'] for w in winners]})
            ax.set_xlim(*data['shared_x_limits']); ax.set_ylim(len(data['rows']) - .35, -.65)
            ax.set_yticks(range(len(data['rows'])), [f"'{r['source_symbol']}'  {r['source_codepoint']}" for r in data['rows']])
            ax.tick_params(axis='both', length=0, pad=7)
            ax.grid(axis='x', color='#E7EBEF', linewidth=.7); ax.set_axisbelow(True)
            for spine in ax.spines.values():
                spine.set_visible(False)
            ax.set_title('Conditional subset' if metric == 'subset' else 'Whole corpus', loc='left', fontsize=15, fontweight='bold', pad=14)
            ax.set_xlabel('Maximum word-entropy decrease (bits)', labelpad=12)
        fig.text(.045, .965, 'Entropy normalization changes maximizing partners', fontsize=21, fontweight='bold')
        fig.text(.045, .933, 'Recovered B notation · 35 codepoints · 70 maxima from 595 pairs · 21 maximizing sets change', fontsize=12)
        fig.text(.045, .904, 'Labels show partner, rounded score and affected mass T. Whole-corpus denominator N is 17,597 throughout.', fontsize=11)
        fig.legend(handles=[Line2D([0], [0], color=colors['changed'], lw=7, label='Partner set changes'),
                            Line2D([0], [0], color=colors['same'], lw=7, label='Partner set unchanged'),
                            Line2D([0], [0], color=colors['zero'], marker='s', markerfacecolor='none', ls='', label='No positive optimum')],
                   loc='upper left', bbox_to_anchor=(.039, .886), ncol=3, frameon=False, fontsize=11)
        fig.text(.045, .062, 'Scores use different populations; when partners differ, the bars also describe different character pairs.', fontsize=11)
        fig.text(.045, .039, 'Source labels are supplied notation codepoints, not adjudicated glyphs. Shared pair scores make these related comparisons.', fontsize=10.5)
        fig.text(.045, .018, 'Exposed later input; no authenticated 2011 procedure, physical case direction, language, glyph mapping or translation is inferred.', fontsize=10, color='#444B53')
        output = {}
        for ext, kwargs in [('png', {'dpi': 160, 'metadata': {'Software': 'Matplotlib'}}),
                            ('svg', {'metadata': {'Date': None, 'Creator': 'Voynich Manuscript Research / Matplotlib', 'Title': 'Native substitution maximizing partners'}})]:
            stream = io.BytesIO(); fig.savefig(stream, format=ext, **kwargs); output[ext] = stream.getvalue()
        plt.close(fig)
    output['svg'] = ('\n'.join(line.rstrip() for line in output['svg'].decode().splitlines()) + '\n').encode()
    provenance = dict(data, artist_positions=artists, renderer={
        'python': platform.python_version(), 'matplotlib': matplotlib.__version__, 'numpy': numpy.__version__, 'pillow': PIL.__version__,
        'freetype': matplotlib.ft2font.__freetype_version__,
        'dejavu_sans_sha256': digest((Path(matplotlib.get_data_path()) / 'fonts/ttf/DejaVuSans.ttf').read_bytes()),
        'script_sha256': digest(Path(__file__).read_bytes())}, output_sha256={ext: digest(raw) for ext, raw in output.items()})
    output['json'] = (json.dumps(provenance, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode()
    return output


def guard(directory, expected):
    if directory.exists() or directory.is_symlink() or directory.resolve() != expected:
        raise ValueError('output directory must be new and keep its resolved identity')
    if any(expected.is_relative_to((ROOT / name).resolve()) for name in ('data', 'scripts')):
        raise ValueError('output aliases source or code storage')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--new-output-dir', type=Path); mode.add_argument('--check-dir', type=Path)
    args = parser.parse_args()
    try:
        directory = args.new_output_dir or args.check_dir; expected = directory.resolve()
        if args.new_output_dir:
            guard(directory, expected)
        output = render(read_data())
        if args.check_dir:
            for ext, raw in output.items():
                if (directory / (STEM + '.' + ext)).read_bytes() != raw:
                    raise ValueError('complete deterministic export differs: ' + ext)
        else:
            guard(directory, expected); directory.mkdir(parents=True, exist_ok=False)
            for ext, raw in output.items():
                if directory.is_symlink() or directory.resolve() != expected:
                    raise ValueError('output directory changed before exclusive writing')
                with (directory / (STEM + '.' + ext)).open('xb') as out:
                    out.write(raw)
    except (ValueError, OSError, KeyError, TypeError, ImportError) as error:
        parser.exit(1, f'Native ranking figure failed: {error}\n')
    print('Verified all70 existing maxima.' if args.check_dir else 'Saved all70 existing maxima.')


if __name__ == '__main__':
    main()
