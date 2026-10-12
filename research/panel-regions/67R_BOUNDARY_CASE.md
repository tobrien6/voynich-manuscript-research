# A source-boundary disagreement at f67r1.1

Question: does agreeing on a native locus and its encoded letter sequence
also establish the same apparent token boundaries?

The [case record](f67r1-1-boundary-case.json) extends the accepted
[67r layout/checklist](README.md). The source data establish a boundary
disagreement. The image detail is a provisional inspection aid; it does
**not** adjudicate a word boundary or assign a verified glyph region.

## Direct source observations

| Pinned source | Terminal encoded grouping | Retained tokens | Concatenated representation length |
| --- | --- | ---: | ---: |
| ZL3b | `epaiin.o.aiin` | 9 | 49 characters |
| IT2a | `epaiin.oaiin` | 8 | 49 characters |

The first seven token values match literally. Concatenating all retained token
values produces the same case-preserved representation string, while ZL has
an additional internal boundary after character offset **45**. The offset
is in that encoded string, not an image coordinate, manuscript glyph count,
phonetic unit, or decoded word position. No alphabet conversion is performed.

There are no uncertain commas, bracketed alternatives, or unreadable tokens
in this case. All tokens remain retained. Split/join uncertain commas and
exclude/first-choice alternatives therefore give the same nine-versus-eight
result in all four treatments. The explicit ZL period remains a separator;
joining commas does not remove it. This demonstrates a specific limit of
annotation-based sensitivity checks, not a failure of the shared lexer.

Agreement of locus identifiers, kinds, locators, or concatenated strings does
not establish token-topology agreement. A cross-source length, recurrence,
or position comparison needs its source-specific segmentation policy and
denominators even when the common locus cohort is fixed.

## Image detail and unresolved interpretation

On 12 October 2026 (America/New_York), inspected this
[Yale-provided detail](https://collections.library.yale.edu/iiif/2/1006194/1850,350,500,160/full/0/default.jpg)
from [image 1006194, 67r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006194).
The original-image viewing rectangle is `(1850, 350, 500, 160)`; the returned
detail is 500 by 160 pixels, 18,258 bytes, with SHA-256 recorded in the JSON.
This is a viewing rectangle, not an exact glyph/word mask or a verified locus
extent. The full image remains the context for the provisional row placement.

Direct observation: a closed oval/circular mark is followed by a short stroke
cluster to its right, separated by a visible blank gap without an obvious ink
connection at the inspected scale. Faint writing and another row's strokes
near the detail boundary limit the inspection. A visible gap alone does not
establish whether the writer intended one or two linguistic words, or which
encoded grouping is preferable.

The publisher's [Basic Eva forms, Table 3](https://voynich.nu/transcr.html)
were consulted privately for shape context. Its legacy punctuation examples
were not used for parsing: current processing follows the accepted IVTFF
lexer. No source pixels or font/reference-image binaries are redistributed.
Both source readings and the proposed row identity were known before this
detail inspection, so it is not a blinded or independent glyph review.

## Reproduce the data comparison

Python 3.10 or later, standard library only. The existing source loader checks
the catalog byte pins; the existing lexer preserves case and source notation.

```sh
python3 - <<'PY'
import json
from pathlib import Path
from scripts.audit_transliterations import load_sources
from scripts.token_baselines import tokenize
case = json.loads(Path('research/panel-regions/f67r1-1-boundary-case.json').read_text())
sources = {source['id']: (source, doc) for source, doc in load_sources()}
for expected in case['source_records']:
    source, doc = sources[expected['source_id']]
    assert source['sha256'] == expected['sha256']
    locus = next(l for l in doc.loci if l.key == case['locus_key'])
    assert locus.present and locus.kind == 'P0'
    assert locus.identifier == expected['locus_identifier']
    assert locus.line_number == expected['source_file_line']
    assert locus.text == expected['native_text']
    for treatment in expected['treatments']:
        tokens = tokenize(locus.text, treatment['uncertain_spaces'])
        assert all(not t.alternative and not t.unreadable for t in tokens)
        values = [t.value for t in tokens]
        position, boundaries = 0, []
        for value in values[:-1]:
            position += len(value)
            boundaries.append(position)
        assert values == treatment['token_values']
        assert len(values) == treatment['token_count']
        assert ''.join(values) == treatment['representation_chain']
        assert boundaries == treatment['internal_boundary_character_offsets']
print('Both source pins and all eight source/policy records reproduce.')
PY
```

Next, independently inspect the complete row and compare the disputed gap
with surrounding spacing under a declared image method. Keep both groupings
unless that review supports a documented source/segmentation decision.
No pinned source is edited, no reading is validated, and no decipherment,
translation, or untouched evaluation material is supplied by this case.
