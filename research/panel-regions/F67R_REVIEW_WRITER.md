# Guarded writer for the accepted 67r checklist

Question: can researchers reproduce the seven provisional horizontal-row
records without replacing a source or accepting a cache with different JSON
types? The [companion](../../scripts/write_67r_review.py) provides this route
while preserving the collector pinned by the upper- and lower-row studies.
It adds no glyph reading, image placement or corpus join.

## Concrete defects and correction

The frozen `build_67r_review.py --output` opens its destination for replacement
after calculation. In disposable synthetic copies, symbolic and hard links to
the proposal, ZL source and collector itself all let that CLI overwrite the
target: six cases. Its `--check` compares Python dictionaries, which consider
`True == 1`, `False == 0` and `7.0 == 7`. A cache with `schema_version: true`,
`usable_as_verified_corpus_join: 0` or `locations: 7.0` therefore passes despite
changing the declared types. These are implementation defects, not new
manuscript observations. The destructive reproductions use only synthetic
temporary trees.

The companion uses the unchanged collector's default `build` function and
source-pin checks. Its two mutually exclusive modes are:

- `--new-report PATH`: refuse existing files and symbolic links, calculate and
  serialize the complete report, check protected paths again, then create the
  file exclusively. It never deliberately replaces an existing destination.
- `--check PATH`: reproduce the complete report and compare every field and
  JSON type. Object-member order and whitespace may differ; array order, native
  text, fields and types must match. The shared strict JSON reader rejects
  duplicate members and non-JSON numeric constants; canonical comparison also
  rejects floating overflow to infinity.

Output guards include the catalog, every catalog-declared source path, the
proposal, accepted checklist, canonical collector/writer/audit/IVTFF/JSON-reader
paths and their actual imported module paths. They retain entry paths and
resolved destinations, then add current paths after calculation and
serialization. They also exclude the resolved `data` and `scripts` directories,
including destinations reached through a parent link. Existing ancestor
directory identities also detect case variants on case-insensitive filesystems.
A source removed from
the catalog during calculation remains protected by the entry snapshot; a new
declaration is covered by the final check.

## Reproduce

From the repository root, Python 3.10 or later, standard library only:

```sh
python3 scripts/write_67r_review.py --check research/panel-regions/f67r-p0-review.json
```

Create a new file in an existing directory outside `data` and `scripts`; choose
a name that does not already exist:

```sh
python3 -m scripts.write_67r_review --new-report /tmp/f67r-review-new.json
python3 scripts/write_67r_review.py --check /tmp/f67r-review-new.json
```

The script and package entry points produce exactly the accepted 5,716 bytes:

| Preserved file | SHA-256 |
| --- | --- |
| `scripts/build_67r_review.py` | `07e071abd5ceb469c23aa3a16175ae5967b8c9c6d63fb5e47d64d01c3725085f` |
| `research/panel-regions/f67r-p0-review.json` | `13063b8994b342b97721e2fe6c01c6d976736fff23a8959e33c26a4f55b57a0e` |

The original collector, accepted checklist, proposal, image-inspection records,
plans and source files are unchanged. In the accepted checklist only
`f67r2.72` has identical native text in both editions; all seven records still
say glyph verification is pending and the verified-join flag remains false.
The [layout proposal](README.md), [upper rows](F67R_UPPER_ROWS.md) and
[lower rows](F67R_LOWER_ROWS.md) retain their original evidence and limitations.
Historical commands using the frozen collector remain available with its known
overwrite and Python-equality limitations. Use the companion for guarded
creation and strict cache comparison.

## Validation and limits

```sh
python3 -m unittest tests.test_write_67r_review tests.test_panel_review -v
```

The tests run both copied CLIs in synthetic temporary trees, preserve the six
legacy overwrite reproductions and demonstrate their refusal by the companion.
They check direct/symbolic/hard aliases at entry, aliases introduced during
calculation or serialization, catalog removal and addition, resolved directory
links and case variants, actual module paths, source-pin drift, existing/dangling destinations
and a destination appearing between the final guard and exclusive open.
Complete cache checks retain reordered-object compatibility while rejecting
equal-valued type substitutions, missing/extra/changed fields, reordered arrays,
duplicate nested members and nonfinite numbers. Native replay is byte-identical
to the accepted checklist.

The guards and exclusive leaf creation are not a filesystem transaction. A
concurrent parent-directory or link mutation after the last check is outside
this guarantee; write failures may leave a partial new file. The snapshots
protect paths, not a full execution or input-mutation attestation. They do not
make the catalog's history or any image/glyph claim independently verified.
The wrapper covers the default seven-record checklist, not the collector's
other programmatic scopes or other legacy writers.

Next test: a separate reviewer should reproduce the copied-CLI defects, guarded
failures and native byte identity before adopting this companion. Independent
glyph and region review remains necessary before a verified 67r crosswalk.
