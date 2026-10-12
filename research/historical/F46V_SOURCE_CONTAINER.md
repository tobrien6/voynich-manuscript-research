# f46v: one historical envelope, two modern locus kinds

Historical `f46v.P.7;H` has a 61-letter lowercase projection equal to the
concatenation of modern IT2a `f46v.7,+P0` (30 letters) and `f46v.8,=Pt`
(31 letters), in native source order. The modern default P0/P1 adapter selects
the first envelope and excludes the second by kind. This concrete source case
explains how matching page-level notation can conceal different analysis units.

The [source extract](f46v-source-container.json) preserves all three unmodified
reader bodies, original locators/source-file lines, source pins, calculation
dependencies, the publisher definitions and both default adapter treatments.
It supplies **no verified historical/modern/image crosswalk**, physical-row
alignment, correction, glyph/word reading or statistical evaluation.

## Selection and original records

The exact [published record-audit snapshot in PR #135](https://github.com/tobrien6/voynich-manuscript-research/pull/135)
at `f17218e729f27948baa4df70f626adfb84549b7b` identifies `f46v` as the sole exact
shared page with an equal joined lowercase stream but unequal nonempty record
bags. This note retains **every one-sided projection group** on that page: one
H envelope and two present IT2a envelopes. It does not select only a successful
pair from a larger unmatched set. The packet pins that report's exact checksum;
it references a fixed submitted artifact without assuming its final disposition.
Both the classification and these bodies were inspected before writing this
note, so it is exposed-data exploration.

| Source native envelope | Source-file line | Projected letters | Native annotation | Default IT2a P0/P1 treatment |
| --- | ---: | ---: | --- | --- |
| H `f46v.P.7;H` | 10665 in the historical member | 61 | Historical unit `P`; its body includes dash separators, `{plant}`, `{&S}` and `!` alignment fillers | Not this modern adapter's source or kind scheme |
| IT2a `f46v.7,+P0` | 1227 in the modern export | 30 | Present P0 locus below the previous item | Eligible, seven native tokens under split and join |
| IT2a `f46v.8,=Pt` | 1228 in the modern export | 31 | Present Pt locus with the `=` relative-position code | Explicit `unselected_locus_kind`, tokens/count null under both policies |

The credited [historical catalog](../../data/historical/interlinear-16e6.json)
preserves Stolfi, the interlinear contributors and Takahashi; the
[modern catalog](../../data/transliterations.json) preserves the specific IT2a
export and Zandbergen's hosting. Original source/derived-data terms remain those
in the [historical data note](../../data/historical/README.md). The code license
does not replace them, and the historical paper's processed input is unverified.

## What the comparison does and does not establish

The [IVTFF specification](https://www.voynich.nu/software/ivtt/IVTFF_format.pdf),
document issue 2.0.2, Table 8 on printed p.21, defines `=` as a locus on the
preceding item's line with intervening white space. Table 9 on p.22 defines
`Pt` as a right-justified, title-like item on that line. Both complete pages and
table rows were rendered and inspected. These are **source encoding conventions**;
no manuscript image was inspected for this note and no title meaning, exact
region or physical line relation is independently adjudicated.

Use the [accepted lowercase projection](LOWERCASE_PROJECTION.md) separately on
each body, including the source-specific comment grammar. Concatenate only the
two modern projections without adding a separator. The result has exactly the
H projection's 61 letters and digest. This operation erases the historical
fillers/comments and all within-body boundaries; it does not equate full native
bodies or establish that historical record 7 is the same physical row as either
modern record. The original bodies and all annotations remain available.

The [default adapter](../transliteration/TOKEN_ADAPTER.md) selects P0/P1 and keeps
the present Pt record visible as an exclusion. It does not delete the Pt source
text or judge it unreadable/nonexistent. Including historical unit P records and
modern P0/P1 records consequently does not guarantee equivalent source coverage.
Any comparison of endpoint, length, repetition or paragraph statistics needs its
own explicit unit/selection reconciliation. No accepted cohort or statistic is
changed by this note; adding Pt would require a separately declared analysis.

## Reproduce the extract

From the repository root, standard-library Python:

```sh
python3 - <<'PY'
import hashlib, json
from pathlib import Path
from scripts.audit_historical_modern_pages import load_inputs
from scripts.audit_historical_lowercase_projection import project_body
from scripts.eva_token_adapter import build
p = json.loads(Path('research/historical/f46v-source-container.json').read_text())
h, modern, pins, _ = load_inputs(Path.cwd())
assert pins == p['inputs']
old = next(r for r in h if r.locator == 'f46v.P.7;H')
new = [l for l in modern.loci if l.key in {'f46v.7', 'f46v.8'}]
assert [l.identifier for l in new] == ['f46v.7,+P0', 'f46v.8,=Pt']
assert old.body == p['native_records'][0]['reader_native_text']
assert [l.text for l in new] == [r['reader_native_text'] for r in p['native_records'][1:]]
a = project_body(old.body, True)[0]
b = [project_body(l.text, False)[0] for l in new]
assert a == ''.join(b) and [len(a), *map(len, b)] == [61, 30, 31]
for record, stream in zip(p['native_records'], [a, *b]):
    assert hashlib.sha256(stream.encode('ascii')).hexdigest() == record['projection']['sha256']
for policy in ('split', 'join'):
    rows = {r['locus_key']: r for r in build(policy, source_ids=('IT2a',))['records']}
    assert rows['f46v.7']['eligible'] and rows['f46v.7']['token_count'] == 7
    assert rows['f46v.8']['exclusion_reasons'] == ['unselected_locus_kind']
    assert rows['f46v.8']['tokens'] is None and rows['f46v.8']['token_count'] is None
assert not p['usable_as_verified_locus_crosswalk'] and not p['image_region_verified']
print('Three source envelopes, 61=30+31 and both default kind exclusions verified.')
PY
```

The original raw archive/export lines also reproduce every extracted body,
locator and source-file line. The selection snapshot reproduces all three
one-sided groups and no others. The exact format-PDF bytes match the recorded
checksum. No executable changes or software tests are added by this source note.
