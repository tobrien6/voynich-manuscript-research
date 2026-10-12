# Conservative native-Eva token adapter

This adapter provides a versioned preprocessing interface for the separately owned baseline, shuffle-control, and evaluation-split work. It reuses the pinned source catalog and `scripts.ivtff` reader. It produces **encoded transcription strings**, not decoded words, manuscript glyph units, or physical-line segments.

For eligible plain-text loci it also reuses the native token grammar in
`scripts.token_baselines`. Ambiguous loci are flagged and excluded before that
lexer's first-alternative path is reached. This keeps boundary handling shared
while making the new whole-locus eligibility policy explicit.

Boundary structure is checked after removing comments/tags and interpreting
drawing interruptions, **before** commas are split or joined. Leading, trailing,
and consecutive separators remain invalid under either policy; comma joining
cannot turn a malformed source record into an eligible one.

## Explicit processing choices

Run from the repository root with Python 3.10 or later:

```sh
python3 scripts/eva_token_adapter.py --uncertain-spaces split --output /tmp/eva-split.json
python3 scripts/eva_token_adapter.py --uncertain-spaces join --output /tmp/eva-join.json
python3 -m unittest tests.test_eva_token_adapter -v
```

The uncertain-space policy is required. Defaults select **ZL3b and IT2a**, with **P0 and P1** locus types. Repeat `--source` or `--kind` to make a different selection. Record those choices in the analysis plan. The full output includes every locus in each selected source, with explicit exclusions for unselected kinds and nonexistent records. Source bytes are checked before preprocessing.

| Notation / case | Policy |
| --- | --- |
| Period | Token separator |
| Comma | Separator under `split`; removed without a separator under `join` |
| `<->` and `<~>` | Separator under both policies; interruption count retained |
| Formatting whitespace | Removed; it does not define a manuscript space |
| Free comments and text tags | Removed from the token text; inherited variables remain in the locus record |
| Paragraph markers | Removed from tokens; source records remain traceable for later paragraph analysis |
| Bracketed alternatives, unreadable material, high-ASCII escapes, or ligature braces | Entire selected locus excluded, with reasons; no preferred alternative is selected |
| Empty boundary, unsupported notation, or non-letter token | Locus excluded; no silent boundary repair |
| Native v101 source | Rejected by this adapter; define an explicit unit mapping or separate adapter before comparison |

The spacing and notation distinctions follow [the IVTFF specification](https://voynich.nu/software/ivtt/IVTFF_format.pdf), sections 5.6 and 6.4-6.7. The conservative exclusion rule is **this project's processing choice**, not a claim that those source loci are incorrect. Case is preserved; capitalized Eva conventions are still encoded notation, so token length is an ASCII-string measure rather than a manuscript-glyph measure.

## JSON interface, version 1

The root contains `schema_version: 1`, `adapter_version: "plain-eva-v1"`, `analysis_unit: "transcription_locus"`, a `sources` list with IDs/checksums/alphabets/URLs/paths, the selected processing policies, exclusion summaries, and `records`.

Each record contains:

| Field | Meaning |
| --- | --- |
| `source_id` | Pinned edition/export identifier from `data/transliterations.json` |
| `page_id` | Original transcription page name, including foldout suffixes |
| `locus_key` | Page plus locus number, suitable for cross-source pairing |
| `locus_identifier` | Complete identifier, including locator/type/transcriber |
| `locus_type`, `locator`, `transcriber` | Original record metadata |
| `source_line_number` | Physical file line for source lookup; not a manuscript-line number |
| `variables` | Inherited page/text variables from the shared reader |
| `eligible` | Whether this record satisfies the selected adapter policy |
| `tokens`, `token_count` | Encoded strings and count, or JSON null when excluded |
| `exclusion_reasons` | Zero or more explicit reasons; reason totals can overlap |
| `uncertain_space_count`, `drawing_interruption_count` | Counts after removing comments/tags, or null for unprocessed nonexistent/unselected records |

A synthetic selected record `ab,cd.ef` yields `["ab", "cd", "ef"]` under split and `["abcd", "ef"]` under join. A selected record containing `[x:y]` remains in the output with `eligible: false`, `tokens: null`, and `alternative_reading` in its reasons. The adapter does not manufacture a token for the uncertain group.

`page_id` is a transcription unit, not an inferred physical-leaf identity. `locus_key` is a locus, not automatically a complete manuscript line. In particular, `=` can mark another item on the same line. Image-panel mapping and leakage groups belong to the crosswalk/split interfaces; this adapter assigns no aliases or physical-line numbers.

## Joining policies and sources for a baseline

Pair by `locus_key` after retaining `source_id`, locus type, and the chosen spacing policy. Require eligibility in every source/policy combination specified by the analysis. If a measurement requires at least two tokens, apply that requirement in **every** combination before freezing the common cohort. Do not fit a filter separately after seeing a result.

Do not count source versions as independent manuscript samples. Keep each record's page identity available for grouped resampling and split checks. A downstream shuffle tool may treat a locus's token list as its unit, but must state that choice rather than implying physical-line reconstruction.

Any token-length result from this adapter concerns native Eva ASCII string length with preserved case. It must not be labeled phonetic length, glyph count, or decoded word length. Excluded uncertain, extended, and ligature-braced loci can systematically differ from included loci, so a later result needs its exclusion denominator and a separately specified sensitivity study.

## Validation and scope

Tests cover split/join behavior, formatting whitespace, drawing boundaries, comments/tags, ambiguity and unreadable exclusions, empty-boundary rejection, retained identities, nonexistent records, and rejection of v101-as-Eva input. The integration check accounts for all **10,600** ZL3b/IT2a locus records under each policy; **6,906** are eligible with default P0/P1 selection in each run. Equal eligibility totals do not mean equal tokens, word counts, or linguistic content.

This is a preprocessing replay on already inspected inputs. It defines no corpus split, computes no shuffle comparison or token-frequency result, and establishes no untouched evaluation set. Record this exposure and adapter version before a later mechanism test. A stronger claim requires a prospectively reserved set and a frozen analysis plan under the [evaluation protocol](../DECIPHERMENT_PROTOCOL.md).

Next, use the stable records to implement the registered baseline and shuffle controls, with a common eligible cohort and appropriate folio/panel grouping. Any relaxation of the exclusion rule should receive a new adapter version and an explicit comparison against this conservative output.

The [coverage/provenance audit](TOKEN_COVERAGE.md) separates source denominators,
exports exact selected/eligible/excluded native-key sets with cohort digests, and
verifies cached adapter JSON against a complete pinned-producer replay.
