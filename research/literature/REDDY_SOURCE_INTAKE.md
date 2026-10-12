# Recoverable inputs for Reddy and Knight's 2011 comparison

A public repository under Sravana Reddy's account associates its data and code
with [Reddy and Knight (2011)](https://aclanthology.org/W11-1511/). Its four
Voynich files match all of the paper's reported full/B population counts and
agree internally at every native page. Every B annotated record also matches
the full file. This supplies a concrete input candidate for a later
letter-prediction comparison, closing the register's source-recovery gap while
leaving the original 2011 preprocessing and Table 2 procedure unresolved.

The [separate literal H/Reddy envelope audit](../historical/REDDY_ENVELOPES.md)
now accounts for the native release's extra normalized-empty H record. All
5,213 shared keys retain the same order and fallback-retained token counts;
listed-code deletion changes eight counts. This nominal correspondence does
not establish equivalent notation, text or original-author corpus bytes.

## Source identity, exposure and chronology

The [source manifest](reddy-source-manifest.json) pins commit
[`643b881`](https://github.com/sravanareddy/deciphervoynich/tree/643b881b2937bae8193814d8ff5d6e99a48bf7c5),
tree `4e529b53db765deb6c243a38731c947e7ab25e92`, every one of its 12 blobs,
and SHA-256/byte/Git-blob identities for six locally retrieved files. The
repository's [README](https://github.com/sravanareddy/deciphervoynich/blob/643b881b2937bae8193814d8ff5d6e99a48bf7c5/README.md)
associates them with the paper. Its six visible commits have author dates on
2015-07-30; neither that later Git history nor matching totals authenticate a
contemporaneous 2011 execution receipt.

The [fixed intake plan](REDDY_SOURCE_PLAN.md), manifest and producer with six
synthetic tests were published in PR #117 at
[`8171ec8`](https://github.com/tobrien6/voynich-manuscript-research/commit/8171ec86c3aa87ebd08d3231fd8d62f293d2757a)
before full-file counts or agreement checks. The paper/register, README,
complete small script and two leading format lines per file had already been
inspected. This is a descriptive audit of exposed sources, without an untouched
evaluation or a newly tested decipherment hypothesis. Plan and producer bytes
remain unchanged from that published commit.

The primary PDF has SHA-256
`842e285c544bffefc1eefa58704cbde6a5e93f0706542dc6a67d374f2c7da599`.
Complete PDF pages 2–4, printed 79–81, were visually inspected for input counts,
notation and letter-prediction definitions. Its cited `voynich.now` URL names a
historical source; this contribution does not recover that source's 2011
snapshot or a documented transformation from it to these repository files.

## Fixed parsing and complete results

The original constructor in
[`basic_stats.py`](https://github.com/sravanareddy/deciphervoynich/blob/643b881b2937bae8193814d8ff5d6e99a48bf7c5/basic_stats.py)
splits decoded text on whitespace. The original audit preserves that token
rule, case, asterisks and all other source symbols. Annotated files keep their
four native header fields; only the subsequent token bodies enter counts.
No corpus filter, repair or outcome-dependent choice is introduced.

| Population | Native records | Paged lines | Token occurrences | Token types | Distinct notation characters |
| --- | ---: | ---: | ---: | ---: | ---: |
| Full `voy.ann/paged.wds` | 5,213 | 225 | 37,919 | 8,114 | 36 |
| B `voy.b.ann/paged.wds` | 1,999 | 43 | 17,597 | 3,920 | 35 |

The paper reports the first three population measures for the full text and
all four for B; every reported count matches exactly. The full 36-character
count is this audit's additional notation observation, not a contradictory
paper estimate. These are Unicode-codepoint/token counts of the supplied
notation, not verified physical glyphs or lexical words.

The [complete report](reddy-source-intake.json) retains every one of the 225
full and 43 B page comparisons, native identifiers, record counts, token-stream
hashes, all character frequencies and every placement/source-tag count. All
268 annotated-to-paged token vectors match. All 1,999 B records have identical
native headers and token vectors in the full file, with order preserved; all
43 B page streams likewise match. No missing or unequal case is suppressed.
The full annotated file has no blank physical lines; the B annotated file has
one, recorded separately. Neither paged file has a blank line.

All native record tags are literal `H`. The header also retains labels and
other placement categories alongside `P`/`P1`–`P4`. This audit does not identify
the meaning of that tag, equate it with a modern IVTFF edition, or replace the
paper's reported Currier alphabet with current GC2a. Native page identifiers
and file-line counts are not a new Yale image alignment or physical foliation.

## What the recovered code supports

Static inspection records imports from `__future__.division`,
`collections.Counter/defaultdict`, `codecs`, `math.log` and `string`. The file
defines `log2`, `build_unigrams`, `entropy` and `CorpusStats` methods for
initialization, word-length distributions, unigram entropy and `get_bestsub`.
Its main block reads `data/voy.b.paged.wds` into that class. No author code was
executed or ported in this contribution.

The inspected Python file does not implement the Table 2 unigram/bigram
predictor, ten-fold assignments or its reported output. The enumerated tree
contains no other Python source file or explicitly named predictor/fold/report
artifact. This is a bounded recovery observation about this snapshot, not a
claim about every author archive. The paper's VMS B accuracies, 14.65% unigram
and 40.02% bigram, remain published results that have not been reproduced here.

## Reproduction and remaining comparison

Retrieve the six manifest-selected files from the pinned repository into a
local reference directory, preserving their relative paths. The producer makes
no network request and verifies size, SHA-256 and Git-blob identities before
parsing:

```sh
python3 scripts/audit_reddy_sources.py --reference LOCAL_SOURCE_DIRECTORY --check
PYTHONPATH=tests python3 -m unittest test_reddy_source_intake -v
# Optional new file; existing files and symlink/hardlink aliases are rejected:
python3 scripts/audit_reddy_sources.py --reference LOCAL_SOURCE_DIRECTORY --output NEW_REPORT.json
```

All six synthetic tests and complete report regeneration pass. Independent
delimiter/groupby parsing, without the production parser, verifies both whole
populations, character tables, all 268 page comparisons, 1,999 B record matches,
43 B/full page matches, header-category counts, blank accounting and every
reported-count difference. Fingerprints, published plan/producer identities,
relative links, strict JSON and whitespace pass. Raw author code, corpus payloads,
PDF and extracted text remain local; comparator language files were not fetched.
No license file is present in the pinned tree and GitHub's license field is
null, so this contribution redistributes original code and metadata only.

The [advertised-history audit](REDDY_HISTORY_INTAKE.md) now extends the bounded
code search across all six reachable commits and both Python versions, with
complete tree reconstruction and unchanged native input blob identities.
Neither source version contains the Table 2 predictor; other archives remain
outside that search.

Next recover the original predictor/preprocessing if available, or separately
freeze an explicit operationalization with complete type folds, word-boundary
handling, tie/fallback rules and aggregation. Keep such a run distinct from
historical reproduction and from modern-notation sensitivity. Matching totals
does not prove every token was used identically in 2011. This intake supplies no
language, cipher mapping, physical glyph equivalence, validated decipherment or
translation; it makes a later source-grounded test possible.
