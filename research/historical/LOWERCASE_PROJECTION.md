# Lossy lowercase notation comparison

Of 223 exact page identifiers shared by historical H and modern IT2a, **183
have identical lowercase-only streams** under the diagnostic below. The other
40 differ; **39 of those still have identical lowercase symbol frequencies**.
Neither result establishes full text identity. The projection deliberately
erases record boundaries, spacing, unknown/rare signs, case and other notation.

This follows the [page-envelope audit](MODERN_PAGE_ENVELOPES.md), which found
equal global counts despite local count differences and unmatched page names.
The [complete report](lowercase-projection.json) records every page's retained
symbol frequencies and stream digest, plus the omitted-character inventory.
Original input bytes remain unchanged.

## Sources, selection and explicit losses

Inputs are the pinned [historical 1.6e6 candidate](../../data/historical/interlinear-16e6.json)
and [IT2a catalog entry](../../data/transliterations.json). They retain credit
to Jorge Stolfi, the original interlinear contributors and Takeshi Takahashi,
with the modern export hosted by René Zandbergen. Source and derived-data terms
remain those in the [historical data note](../../data/historical/README.md);
the repository's code license does not replace them. The report records exact
archive/member/source identities and both catalog digests.

The [script](../../scripts/audit_historical_lowercase_projection.py) reuses the
accepted readers and source-pin checks. Historical H retains all native
envelopes, including padding-only records. Modern IT2a includes present loci;
its explicitly nonexistent locus stays excluded from the primary comparison.
Page names must match exactly. The two unmatched identifiers per source remain
separate, without truncation, alias application or inferred panel alignment.

For each selected body:

1. Remove balanced historical curly comments or modern IVTFF human comments
   using the accepted source-specific routines.
2. Remove defined modern `<@X=value>` text metadata tags. These are metadata,
   including when a value itself is lowercase.
3. Retain only ASCII `a` through `z` and concatenate in native source order
   within each exact page identifier, without separators between records.
4. Retain every omitted character's count outside human comments, plus comment
   and metadata-tag occurrence counts. Preserve the native record denominator.

This is a deliberately non-injective projection: distinct source bodies can
produce the same retained stream. Unknown/rare signs are disclosed in the
omitted inventory, not converted into matched glyphs or removed from the
original corpus. Symbols retained as ASCII letters are encoded notation units,
not established manuscript glyphs or phonetic values. Empty projections supply
null equality fields rather than a positive match.

The source comments have different grammars: historical curly braces hold
comments, while modern IVTFF curly braces may carry ligatures. No shared curly
brace rule is applied. The pinned [publisher descriptions](https://voynich.nu/transcr.html)
and [historical release](https://www.ic.unicamp.br/~stolfi/EXPORT/00-EXPORT/98-12-28-interln16e6/)
supply edition context; they do not validate a row correspondence.

## Count-discrepancy pages

| Exact page | H projected symbols | IT2a present projected symbols | Same stream | Same frequencies |
| --- | ---: | ---: | --- | --- |
| `f46v` | 549 | 549 | Yes | Yes |
| `f75v` | 1,678 | 1,678 | No | Yes |
| `f89v2` | 842 | 839 | No | No |
| `f106r` | 2,338 | 2,338 | Yes | Yes |

The first and last cases illustrate that erasing boundaries and padding can
conceal unequal envelope counts. On `f75v`, equal symbol frequencies do not
establish equal sequence order. This diagnostic does not attribute differences
to a particular split, merge, reordering or correction of source records.

`f89v2` is the sole differing-frequency page. Its native H count retains
`f89v2.L3.3a;H`, whose lowercase projection is `dso`; modern IT2a declares
`f89v2.26,!Lf`, also projecting to `dso`, but marks it nonexistent. H minus
IT2a present has one additional `d`, `s` and `o`.

The report separately inventories that excluded modern envelope. A clearly
labelled declared-envelope diagnostic includes it only to inspect source
notation: the resulting 842-symbol page stream equals the H projection.
The primary comparison still excludes it. This does not adjudicate whether
writing exists on the manuscript, equate the two source locators, or authorize
using a nonexistent locus as ordinary analysis content. Unknown-sign notation
and presence declarations remain separate evidence.

## Chronology, reproduction and limits

A preliminary ad-hoc lowercase-only comparison was run after seeing the
envelope discrepancies and before this implementation/report. It revealed the
183/40 split, and later targeted inspection motivated the declared-envelope
diagnostic for `f89v2`. This is exposed-data exploration, not preregistered
validation or a held-out mechanism test. No new significance test is performed.

Python 3.10 or later, standard library only; no downloads or archive extraction:

```sh
python3 scripts/audit_historical_lowercase_projection.py --output research/historical/lowercase-projection.json
python3 scripts/audit_historical_lowercase_projection.py --check research/historical/lowercase-projection.json
python3 -m unittest tests.test_historical_lowercase_projection -v
```

Eight synthetic tests demonstrate boundary/spacing loss, unequal unknown signs
under equal projections, equal frequencies under different sequences,
source-specific comment/metadata handling, empty/unmatched pages, source
selection and nonexistent-envelope isolation, failed-check output preservation,
and hardlink input/reader protection using only temporary fixtures. The report
contains counts and hashes rather than projected text bodies.

Do not use this projection as a replacement transcription or a token/spacing
analysis input. It cannot identify word boundaries, resolve unknown signs,
align physical rows, prove historical paper-input identity, supply independent
source confirmation, or support readings and translations. A later content
crosswalk needs source-specific notation transformations and region evidence,
with ambiguous, split, merged and nonexistent records preserved explicitly.
