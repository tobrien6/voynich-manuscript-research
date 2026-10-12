# Historical label phrase provenance

Question: where do the published figure-label phrases occur in the recovered
interlinear, and do exact H strings identify every intended exclusion?

The [parsing reconstruction](PARSING.md) retained two unmatched phrases from
[Amancio et al.'s supplement](https://doi.org/10.1371/journal.pone.0067310.s007).
This [complete lookup](label-phrases.json) searches all 17,357 native records in
the pinned archive. It uses the same four phrases from the frozen parser plan,
without selecting a different reading or revising that parser.

## Direct source observations

| Phrase | Exact matches by native transcriber code |
| --- | --- |
| `okchdy` | H: 3; F: 2; V: 3; U: 3 |
| `dar alocfhy` | F: 1; U: 1; H: 0 |
| `dchedaly` | H: 1; F: 1; V: 1; U: 1 |
| `otarodl shy orory` | F: 1; H: 0 |

The two phrases without H matches occur at f78r.X.3 under F/U and f78r.X.5
under F. The source's transcriber-code comments identify H as Takahashi and F as
the First Study Group lineage; these labels do not independently validate a
manuscript reading. The corresponding native-key strings are:

| Native key | H | F | V | U |
| --- | --- | --- | --- | --- |
| f78r.X.2 | `okchdy` | No record | `okchdy` | `okchdy` |
| f78r.X.3 | `daraloikhy` | `dar alocfhy` | `dar aloifhy` | `dar alocfhy` |
| f78r.X.4 | `dchedaly` | `dchedaly` | `dchedaly` | `dchedaly` |
| f78r.X.5 | `otasodlory orory` | `otarodl shy orory` | `otaro dlery orary` | `otaro dlory orory` |

These are opaque transcription strings after the stated formatting removal,
not readings adjudicated against images or translations. Differences include
spacing as well as letter representations.

Identical strings also occur outside those f78r keys. H's other `okchdy` records
are f83v.Y.7 and f84v.Y.30. Other codes contain that string at f83v.Y.8,
f84v.Y.30 and f85v2.B2.6. The report preserves every locator and all readings
at each matching native key. It does not equate f83v.Y.7 with f83v.Y.8 or infer
that identical strings refer to the same pictured item.

## Method and validation

`scripts/audit_historical_label_phrases.py` reuses the verified archive/member
loader and native-envelope reader. It removes balanced curly comments and
exclamation/percent fillers, replaces comma/period/hyphen/equals with boundaries,
and collapses whitespace. Coded fallback characters, case, and every other
residual notation character remain unchanged. Only complete-record equality
matches; no substring, fuzzy, case-folded or preferred-transcriber search occurs.
This display/query operation is not a token corpus adapter.

The report pins source, query-plan, supplement, script and reader identity and
retains original source credit/permission metadata. All source-derived strings
remain subject to the terms in the [data note](../../data/historical/README.md).

Seven focused tests cover formatting boundaries, preserved case/fallbacks,
complete-record equality, repeated matches and transcriber identity, strict
native-key grouping, invalid/duplicate queries, complete pinned-input search, and
byte preservation when direct or hardlink outputs alias any of the five inputs.
The CLI protects the catalog, archive, query plan, lookup script and native reader.
The report replays exactly. Run from the repository root with Python 3.10+:

```sh
python3 scripts/audit_historical_label_phrases.py --output research/historical/label-phrases.json
python3 scripts/audit_historical_label_phrases.py --check research/historical/label-phrases.json
python3 -m unittest tests.test_historical_label_phrases -v
```

## Implication and limits

The published names are compatible with particular non-H strings in this
archive. That observation does not prove that the authors mixed transcribers or
identify their input version: names could describe locations using another
reading convention while their parser removes H records by location.

An exact-string deletion rule on H can miss such locations and can remove
matching strings elsewhere. A future locator-based alternative needs explicit
evidence for the intended regions, a new plan version, and retention of the
current negative reconstruction. Do not substitute F strings into H to make the
phrase list or token total agree.

No parser rule was changed here, and the four prior length discrepancies remain.
This source lookup supplies neither an image-adjudicated crosswalk nor a
published numerical replication, decipherment or translation. The full archive
is already exposed material; these additional strings must also be recorded as
prior exposure in any later evaluation design.
