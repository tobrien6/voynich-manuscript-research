# Explicitly nonexistent and undeclared locus envelopes

The sole exact key carrying an explicit nonexistent locator in the five pinned
modern exports is **`f89v2.26`**. IT2a and GC2a declare `f89v2.26,!Lf`; ZL3b and
both RF1b exports leave that key undeclared. All five declare page `f89v2` and
retain present records at exact keys `f89v2.25` and `f89v2.27`.

This is a source-annotation distinction. No source supplies a present locus at
the selected exact key, but the two declared placeholders and three omissions
are different records of absence. They do not establish whether manuscript
writing exists, identify a physical image region, or equate historical locators.

## Sources and scoped extract

The [manual extract](nonexistent-locus-extract.json) records exact source URLs,
hashes, native alphabets, page-header status, target records and numbered-key
context. The [catalog](../../data/transliterations.json) retains each export's
edition, credits and byte identity. Original source credits and the publisher's
CC0 terms remain recorded in the [source register](SOURCES.md).

| Export | Native alphabet | Exact key `f89v2.26` | Selected native identifier |
| --- | --- | --- | --- |
| ZL3b | Eva- | Undeclared locus | None |
| IT2a | EvaT | Explicitly nonexistent | `f89v2.26,!Lf` |
| GC2a | v101 | Explicitly nonexistent | `f89v2.26,!Lf` |
| RF1b full | Eva- | Undeclared locus | None |
| RF1b basic | Eva- | Undeclared locus | None |

The [IVTFF specification](https://www.voynich.nu/software/ivtt/IVTFF_format.pdf)
defines locator metadata; its 2.0.1 update adds a status for text judged
nonexistent by the publisher. This note queries locator metadata through the
existing reader rather than searching bodies for exclamation marks. A `!`
inside a v101 body can be an alphabet character, as the accepted
[comparator audit](../transliteration/COMPARATORS.md) explains.

The inspected PDF is document issue 2.0.2 (8 July 2025), describing format
2.0.1; relevant locators are section 1.2 and section 6.4/Table 8 (printed page
21). Its SHA-256 matches the accepted [documentation pin](../transliteration/comparator_documentation.json)
`7ac9c4a82064763cac8767cca6f661cc4e1b4503ab9342acc03032ddb6939d49`.
The five source files still declare `2.0`; documentation issue, format change
and each dataset's file header remain separate identifiers.

The two placeholder bodies are each six ASCII bytes in the reader's returned
value, at physical source-file lines 3,842 and 4,168 respectively. Those are
file positions and encoded-byte lengths, not manuscript row or glyph counts.
Their body digests identify the reader value after its existing whitespace and
continuation handling; they are not raw-file hashes. Different alphabets remain
separate, and no body conversion or cross-alphabet glyph comparison is made.

Keys 25 and 27 supply source-number context only. Their presence does not make
them image-adjacent regions or validate the gap as a physical missing label.
RF's two exports are related derived representations, not independent witnesses.

## Reproduce the source check

Run from the repository root with Python 3.10 or later. The accepted loader
checks all five source byte identities before parsing. This reconstructs the
saved source rows, including an absent page header versus an undeclared key
within a declared page:

```sh
python3 - <<'PY'
import hashlib, json
from pathlib import Path
from scripts.audit_transliterations import load_sources
saved = json.loads(Path('research/transcriptions/nonexistent-locus-extract.json').read_text())
assert hashlib.sha256(Path('data/transliterations.json').read_bytes()).hexdigest() == saved['catalog_sha256']
assert hashlib.sha256(Path('scripts/ivtff.py').read_bytes()).hexdigest() == saved['reader_sha256']
format_pin = next(d for d in json.loads(Path('research/transliteration/comparator_documentation.json').read_text())['documentation'] if d['id'] == 'TR-FORMAT')
assert (saved['format_reference']['url'], saved['format_reference']['sha256']) == (format_pin['url'], format_pin['sha256'])
sources = load_sources()
assert sorted({l.key for _, d in sources for l in d.loci if not l.present}) == saved['selected_keys'] == ['f89v2.26']
for expected, (source, document) in zip(saved['sources'], sources, strict=True):
    assert (source['id'], source['sha256'], source['url'], document.alphabet) == (expected['source_id'], expected['source_sha256'], expected['source_url'], expected['native_alphabet'])
    assert ('f89v2' in document.pages) == expected['page_header_declared']
    records = [l for l in document.loci if l.key == 'f89v2.26']
    assert len(records) <= 1
    record = records[0] if records else None
    status = 'explicitly_nonexistent' if record is not None and not record.present else 'present' if record is not None else 'undeclared_locus' if 'f89v2' in document.pages else 'undeclared_page'
    assert status == expected['target_status']
    details = None if record is None else {'identifier': record.identifier, 'locator': record.locator, 'kind': record.kind, 'physical_source_file_line': record.line_number, 'reader_body_ascii_bytes': len(record.text.encode('ascii')), 'reader_body_sha256': hashlib.sha256(record.text.encode('ascii')).hexdigest()}
    assert details == expected['target_record']
    context = [{'key': l.key, 'identifier': l.identifier, 'source_status': 'present' if l.present else 'explicitly_nonexistent'} for l in document.loci if l.key in {'f89v2.25', 'f89v2.27'}]
    assert context == expected['flanking_exact_keys']
print('Exact source annotations and saved envelope extract verified.')
PY
```

This verifies inspected metadata, not the interpretation or correctness of the
source declarations. The JSON is a manually selected source extract, not a new
corpus interface or a glyph adjudication. Original source files remain unchanged.

The [historical lowercase diagnostic](../historical/LOWERCASE_PROJECTION.md)
shows why a declared placeholder body can affect a notation-only comparison
when included diagnostically. It stays excluded from that primary comparison.
This note adds GC and the three undeclared-key cases without converting their
alphabets or reassigning the older H record.

## Limits and next test

This is an exploratory metadata inspection on previously exposed source files.
Matching source keys and annotations do not supply independent physical evidence.
Before adjudicating presence, establish documented panel/region conventions and
inspect the exact manuscript region, preserving source-specific placeholders
and omissions. No image/glyph reading, source correction, held-out evaluation,
decipherment, or translation is established here.
