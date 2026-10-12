# Historical parsing reconstruction and discrepancies

Question: can an explicit application of the published parsing instructions
reconstruct the reported historical token stream?

The [parser plan](PARSER_PLAN.md) and [parameters](parser-plan.json) were committed
before computing processed-corpus counts. The complete [ledger](parsing.json)
retains every declared variant and manual exclusion. The plan's known target
length was not used to adjust selectors. This is an approximate reconstruction
from the recovered archive, not the authors' code or an exact replication.

## Observations

H has 5,214 native records. Comment/filler/separator normalization retaining coded
fallbacks yields 37,919 tokens. The declared special-code removal interpretation
reduces that to 37,896 tokens before manual exclusions.
The four planned variants produce:

| f57 ring interpretation | f66r excluded native unit | Retained tokens | Difference from reported 37,762 |
| --- | --- | ---: | ---: |
| Omit R2 | M: letters/symbols | 37,759 | −3 |
| Omit R2 | L: left-hand words | 37,776 | +14 |
| Remove one-character encoded tokens across R1–R4 | M | 37,713 | −49 |
| Remove one-character encoded tokens across R1–R4 | L | 37,730 | −32 |

None reproduces the reported length. The closest count does not establish the
same token content or order. All four remain unresolved alternatives.

The declared exact-record label rule matches `okchdy` at three H locators and
`dchedaly` at one. Two published phrases have no exact normalized H-record match.
The absent phrases also have no exact match when the coded fallback characters
are retained. No similar string was substituted, and no phrase was removed from
a larger record. These observations could reflect input differences, parsing
order or a different label-selection scope; they do not establish which caused
the discrepancy.

The f66r scan and native comments support distinct left-hand words, isolated
signs and main text, leaving the paper's column description ambiguous. The
single-character ring criterion counts encoded token length, not adjudicated
manuscript glyphs. Other selectors and deletion of one encoded fallback character
per listed code are likewise explicit operational interpretations.

## Implementation and provenance

`scripts/reconstruct_historical_tokens.py` reuses the native reader and pinned
archive verification. It normalizes every selected H record once, then applies
the complete two-by-two policy matrix. The ledger records source locators and
body hashes for excluded records, code-deletion offsets and characters, exact
label matches, ring-deletion indices, and reconciled token counts. Generic
comment/filler handling remains distinct from manual source exclusions.

The report pins machine-plan, parser and reader hashes, source/container/member
hashes, and the supplement identity. Digests for each record corpus and flat
token sequence use compact ASCII JSON with a final newline; the optional complete
export has a separate digest. Original token indices refer to the normalized
record **before manual exclusions**, not to raw byte positions or glyph indices.
Empty and excluded records remain in the exported record ledger.

The optional flat export preserves archive order and the native locator/index of
every surviving token. It retains record breaks separately. A later whole-text
adjacency statistic must state whether it includes edges across record breaks.
This contribution computes no repetition statistic or shuffle distribution.

Exported transcription strings carry original source credit and permission
metadata. They remain governed by the source terms described in the
[data note](../../data/historical/README.md). The committed report contains
counts, locators, hashes and deletion events; full token streams are generated
on request rather than duplicated in the repository.

## Reproduce

Python 3.10 or later, standard library only, from the repository root:

```sh
python3 scripts/reconstruct_historical_tokens.py --output research/historical/parsing.json
python3 scripts/reconstruct_historical_tokens.py --check research/historical/parsing.json
python3 scripts/reconstruct_historical_tokens.py --check research/historical/parsing.json \
  --corpus-output /tmp/historical-token-variants.json
python3 -m unittest tests.test_historical_reconstruction tests.test_historical_interlinear -v
```

Eleven parser tests cover code/comment ordering, all separator and filler policies,
unlisted/unreadable material, malformed notation, exact label matching, selective
unit/line removal, both ring and column policies, provenance/order, count and
digest reconciliation, source/output protection, and drift failure before writes. The eight native-intake
tests remain relevant. The report and optional export were replayed byte-for-byte.

## Limits and next test

The exact historic download, authors' parser, glyph interpretation and processed
sequence remain unverified. Recover those artifacts or clarify the ambiguous
exclusions before claiming numerical replication. In particular, investigate
label scope and segmentation without treating a matching total as success.
Any revised rule needs a new plan version and must retain this negative result.
The separately owned historical/IT2a identity audit can supply complementary
input evidence without implying a locus crosswalk.

All inspected source data and the f66r image are exposed material. This parser
does not supply a held-out evaluation, decoding rule, language identification,
or translation.
