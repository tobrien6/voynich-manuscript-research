"""Audit generated group rows without treating initialization as a prediction.

This reads local bytes only. It neither executes the generator nor equates its
group strings with IVTFF loci or independently verified manuscript glyphs.
"""

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import re


FIELDS = ('data_row_1_based', 'physical_file_line_1_based', 'origin',
          'notation_characters', 'group_occurrences', 'row_sha256')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def analyze(raw, initial_text):
    """Retain physical lines and literal spaces; reject unsupported data rows."""
    try:
        text = raw.decode('ascii')
    except UnicodeDecodeError as error:
        raise ValueError('generated file must be ASCII for this notation-count audit') from error
    if not isinstance(initial_text, str) or not re.fullmatch(r'[a-z]+(?: [a-z]+)*', initial_text):
        raise ValueError('initial text must use nonempty lowercase ASCII groups and literal spaces')
    crlf = b'\r\n' in raw
    if crlf and b'\n' in raw.replace(b'\r\n', b'') or '\r' in text.replace('\r\n', ''):
        raise ValueError('mixed or unsupported line endings')
    lines = text.split('\r\n' if crlf else '\n')
    if lines[-1] == '':
        lines.pop()  # a final terminator is not an additional physical line
    rows, comments, blanks = [], [], []
    for number, line in enumerate(lines, 1):
        if line.startswith('#'):
            comments.append(number)
        elif line == '':
            blanks.append(number)
        else:
            if not re.fullmatch(r'[a-z]+(?: [a-z]+)*', line):
                raise ValueError(f'unsupported or empty group slot at physical line {number}')
            rows.append(dict(zip(FIELDS, (
                len(rows) + 1, number, 'initialization' if not rows else 'generated',
                len(line), len(line.split(' ')), digest(line.encode('ascii'))))))
    if not rows:
        raise ValueError('no data rows')
    generated = rows[1:]
    summary = {
        'bytes': len(raw), 'sha256': digest(raw), 'physical_file_lines': len(lines),
        'line_ending': 'CRLF' if crlf else 'LF', 'final_line_terminator': text.endswith('\n'),
        'comment_file_lines_1_based': comments, 'blank_file_lines_1_based': blanks,
        'data_rows_including_initialization': len(rows),
        'group_occurrences_including_initialization': sum(row['group_occurrences'] for row in rows),
        'newly_generated_rows': len(generated),
        'newly_generated_group_occurrences': sum(row['group_occurrences'] for row in generated),
        'initial_input': {'sha256': digest(initial_text.encode('ascii')),
                          'notation_characters': len(initial_text),
                          'group_occurrences': len(initial_text.split(' '))},
        'stored_initial_row': rows[0],
        'stored_initial_row_equals_initial_input': rows[0]['row_sha256'] == digest(initial_text.encode('ascii')),
        'generated_row_notation_character_range':
            [min(row['notation_characters'] for row in generated),
             max(row['notation_characters'] for row in generated)] if generated else None,
        'unit': 'space-delimited ASCII group strings, not internal generator segments or verified glyphs',
    }
    return summary, rows


def ledger_bytes(rows):
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode('ascii')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('generated_file', type=Path)
    parser.add_argument('--configuration', type=Path, required=True)
    parser.add_argument('--new-record', type=Path, required=True)
    parser.add_argument('--new-ledger', type=Path, required=True)
    args = parser.parse_args()
    try:
        outputs = (args.new_record, args.new_ledger)
        if any(path.exists() or path.is_symlink() for path in outputs):
            raise ValueError('output paths must be new, preserving existing files and symlinks')
        if outputs[0].resolve() == outputs[1].resolve():
            raise ValueError('record and ledger must have distinct output paths')
        config = args.configuration.read_bytes()
        values = [line.partition('=')[2] for line in config.decode('ascii').splitlines()
                  if line.startswith('text.initial_line=')]
        if len(values) != 1:
            raise ValueError('require exactly one literal text.initial_line configuration key')
        summary, rows = analyze(args.generated_file.read_bytes(), values[0])
        ledger = ledger_bytes(rows)
        record = {'schema_version': 1, 'method': 'literal self-citation row accounting v1',
                  'configuration_sha256': digest(config), 'output': summary,
                  'ledger_sha256': digest(ledger), 'glyph_alignment_verified': False,
                  'scope': 'counts and row fingerprints; no manuscript mechanism evaluation or translation'}
        with args.new_record.open('xb') as destination:
            destination.write((json.dumps(record, indent=2) + '\n').encode('ascii'))
        with args.new_ledger.open('xb') as destination:
            destination.write(ledger)
    except (OSError, UnicodeError, ValueError) as error:
        parser.exit(1, f'Row audit failed: {error}\n')
    print('New row record and ledger written; initialization remains input, not a prediction.')


if __name__ == '__main__':
    main()
