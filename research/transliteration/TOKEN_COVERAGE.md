# Conservative adapter coverage and provenance audit

This audit supplies source-specific denominators and reproducible native-key
cohorts for consumers of the accepted [Eva token adapter](TOKEN_ADAPTER.md).
It reuses `scripts.eva_token_adapter.build` and the pinned
[source catalog](../../data/transliterations.json); it defines no new tokenizer.

The [machine-readable report](token_adapter_coverage.json) keeps source versions,
selected types, policy-specific eligible/excluded counts, token totals, overlapping
exclusion reasons, and SHA-256 identities of both complete adapter snapshots.
It contains no token text. The report's source hashes identify manuscript
transliteration bytes; snapshot hashes identify derived adapter JSON. Neither
hash establishes the correctness of a reading.

## Observations from the pinned P0/P1 inputs

| Source | Declared loci | Selected present P0/P1 | Eligible | Excluded after selection | Eligible tokens, split | Eligible tokens, join |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| ZL3b | 5,385 | 3,957 | 3,012 | 945 | 25,681 | 23,847 |
| IT2a | 5,215 | 3,956 | 3,894 | 62 | 33,141 | 33,141 |

The adapter's pooled **6,906 eligible source records** are 3,012 + 3,894.
They are not 6,906 independent manuscript loci. Only **2,997 native locus keys**
are eligible in every source/policy combination. Requiring at least two tokens
in every combination leaves **2,993 keys**. Both cohorts span 203 native page
names, including the source's panel conventions; this is not a count of physical
leaves. No type or locator differences were recorded between sources on the
shared eligible keys. Image/physical-line alignment is not established here.

The whole-locus exclusion policy removes different portions of the editions.
ZL preserves alternatives, extended notation, and ligatures that trigger this
adapter's exclusions. These exclusions are processing choices, not evidence
that those loci are incorrect. Reason counts can overlap: sum them neither as
an excluded-locus total nor as an error rate. Differences in token totals under
split/join also do not create new manuscript samples or linguistic readings.

## Generate and verify

From the repository root with Python 3.10 or later:

```sh
python3 scripts/audit_eva_token_coverage.py \
  --check research/transliteration/token_adapter_coverage.json \
  --keys-output /tmp/eva-selection-manifest.json
python3 -m unittest discover -s tests -p 'test_eva_token_coverage.py' -v
```

The audit checks that declared source records, selection, eligibility, exclusions,
and the producer's summary reconcile. It also checks that native record metadata
and identities remain identical between spacing policies. Multiple transcribers
at one source-tagged native key are rejected rather than silently collapsed into
one paired observation. Source-specific type/locator differences on shared keys
are reported, not remapped.

Repeat `--source` or `--kind` to choose another explicit adapter selection;
record those choices before an analysis. `--output PATH` writes a compact report.
The original source catalog and raw-input directory are protected from audit
output. The full key manifest is generated locally so consumers can freeze the
exact subset they use without duplicating all source-key arrays in this PR.

## Exact native-key contract

The optional selection manifest has schema version 1 and these fields:

| Field | Meaning |
| --- | --- |
| `sources` | Source IDs, URLs, alphabets, paths, and exact transcription hashes |
| `adapter_snapshot_sha256` | Canonical producer-output digest for each spacing policy |
| `selected_locus_types` | Explicit adapter selection, default P0/P1 |
| `source_key_sets` | Declared, present, and selected-present native keys by source |
| `policy_key_sets` | Eligible, excluded, excluded-after-selection, and at-least-two-token keys by policy and source |
| `shared_cohort_key_sets` | Intersections across every declared source/policy, with and without the two-token requirement |
| `key_sets` | Complete sorted native-key arrays, stored once per distinct digest |

Each set reference contains `native_locus_count` and `sorted_native_keys_sha256`.
Resolve the complete array with
`manifest["key_sets"][reference["sorted_native_keys_sha256"]]`. The digest is
SHA-256 of UTF-8 `key + "\n"` for every lexically sorted key; an empty set hashes
empty bytes. Keys are exact `locus_key` strings, such as `f1r.1`. Source and policy
are separate dimensions; stripping panel suffixes or introducing foliation
aliases is outside this contract.

The set with a two-token requirement is a diagnostic option for consumers whose
measurement needs it, not a frozen experimental choice. A consumer must specify
its inclusion rule and store the selected manifest/digest before evaluation.

An experiment may additionally restrict locus types or locators, require an
available original boundary slot, or require interior tokens. Record its complete
predicate, source/policy configuration, parent key-set digest, and final selected
key-set digest. A smaller experiment cohort can follow from these extra filters;
it is not automatically a source mismatch. Do not replace an experiment's stated
denominator with this audit's general eligible count or force different studies
onto one cohort without recording a new selection.

## Verify cached adapter records

```sh
python3 scripts/eva_token_adapter.py --uncertain-spaces split --output /tmp/eva-split.json
python3 scripts/audit_eva_token_coverage.py --verify-adapter /tmp/eva-split.json
```

Cache verification regenerates the complete adapter output from its recorded
source IDs, types, and policy using the pinned source files. Tokens, source
metadata, exclusions, and totals must all match; a self-reported checksum or a
plausible count is insufficient. Object-key order and JSON formatting may differ,
but value types, array order, and content may not. Duplicate JSON object keys are
rejected. Verification makes no network requests and does not replace the cache.

The canonical snapshot serialization is UTF-8 JSON with indentation 2, sorted
object keys, `ensure_ascii=False`, no nonfinite numbers, and one final newline.
This digest is independent of a cache file's presentation formatting. Shuffle
controls should separately freeze the exact corpus bytes they actually receive.

## Limits and next use

This is a preprocessing/accounting replay, not independent glyph adjudication or
a claim that cached tokens are linguistically correct. It establishes no physical
folio mapping, untouched evaluation set, candidate mechanism, or translation.
The common native-key cohort supports later documented comparisons, while each
consumer remains responsible for its unit definition, exposure history, split,
and statistic. Follow the [evaluation protocol](../DECIPHERMENT_PROTOCOL.md).
