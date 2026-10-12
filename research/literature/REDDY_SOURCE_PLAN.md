# Intake plan for the Reddy/Knight source repository

Question: what recoverable input/code evidence does the paper-associated public
repository supply, and how closely do its Voynich files match the paper's
reported populations? This is a descriptive source audit, not a letter-prediction
replication or a decipherment experiment.

## Fixed artifacts and prior exposure

Pin `sravanareddy/deciphervoynich` at commit
`643b881b2937bae8193814d8ff5d6e99a48bf7c5`, tree
`4e529b53db765deb6c243a38731c947e7ab25e92`. Its README associates the repository
with Reddy and Knight (2011). The six visible commits date to 2015-07-30,
later than the paper; that history is not a contemporaneous 2011 receipt.

The [fixed source manifest](reddy-source-manifest.json) retains the complete
12-blob inventory and byte/Git-blob/SHA-256 identities for the selected README,
`basic_stats.py` and four `data/voy*.wds` files. These six files are downloaded
locally. No comparator language files, third-party source or corpus text will
be redistributed or executed. The tree supplies no license file, and GitHub's
license field is null; public availability does not establish reuse permission.

The existing paper/register, primary PDF pages 2–4 (printed 79–81), repository
README and complete statistics script have been inspected. Two leading format
lines per Voynich file were previewed to define the parser. Source headers,
Currier-style notation and reported totals are already exposed. The plan and
synthetic-tested producer will be published before the first new full-file
counts or agreement checks. No untouched evaluation is claimed.

## Fixed parsing and comparisons

1. Verify all six file sizes, Git blob identities and SHA-256 hashes before
   parsing. Use strict UTF-8 decoding, without changing case or any token.
2. For paged files, retain every native file-line position, including blank
   lines. Tokens are exactly Python whitespace splitting, as used by the
   inspected `CorpusStats` constructor. Count whole-file token occurrences,
   distinct token strings and non-whitespace characters. Retain the literal
   asterisk and any other source symbols; do not exclude unreadable strings.
3. For annotated files, require each nonblank record to have one `<...>` header
   with four whitespace-delimited fields followed by token content. Retain
   those fields verbatim as page, placement, native line identifier and source
   tag; do not equate a tag to a current IVTFF edition or classify its hand.
   Reject malformed records, duplicate headers and noncontiguous page returns
   rather than inventing a repair. Count tokens only in the body. Report blank
   physical lines separately.
4. Concatenate annotated bodies within each native page, preserving source
   order and token boundaries. Compare each page's complete token vector with
   the corresponding paged-file line. Report every match/mismatch, ordinal,
   count and canonical token-stream hash, without publishing token strings.
5. Check every B annotated record and page against the full annotated file,
   preserving native identifiers and order. Report missing/unequal cases;
   do not reselect the B cohort to make counts agree.
6. Compare the paged populations with the paper's reported full counts
   (225 pages, 37,919 tokens, 8,114 types) and B counts (43 pages, 17,597
   tokens, 3,920 types, 35 characters). Keep differences as results. Matching
   totals or internal streams do not authenticate 2011 byte identity.

## Code scope, checks and limits

Inspect the only Python file statically: record imports, function/method names
and its main-block input path. Do not execute, port or treat it as a Table 2
predictor. The complete tree bounds any observation that an implementation or
license was not recovered to this particular snapshot. Do not infer absence
from the whole project, other archives or the authors' original work.

Synthetic checks will cover native headers, token preservation, blank lines,
malformed/duplicate/noncontiguous records, page vector disagreements, B/full
membership, file identity drift and exclusive new-output creation. Regenerate
the full report and independently recompute token/character populations and
all annotation/page/B/full comparisons without the production parser.

Publish original code, public locators and metadata only. Corpus payloads,
paper PDF, author source and local extracted text remain excluded. This does
not reproduce letter prediction, establish physical glyph units, equate these
files to modern GC2a, create an evaluation split, infer a language, or translate
the manuscript. A later comparison needs a separately specified predictor,
folds, boundaries, tie/fallback rules and source/unit compatibility record.
