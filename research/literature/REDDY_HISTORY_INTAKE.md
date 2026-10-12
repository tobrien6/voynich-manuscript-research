# The advertised author history does not recover the Table 2 predictor

Question: did an earlier reachable version of the paper-associated author
repository contain the predictor missing from the final source snapshot?

The [prior intake](REDDY_SOURCE_INTAKE.md) inspected the final
[`sravanareddy/deciphervoynich` snapshot](https://github.com/sravanareddy/deciphervoynich/tree/643b881b2937bae8193814d8ff5d6e99a48bf7c5).
This follow-up inventories every commit reachable from that advertised master
head, the captured advertised branches/tags, every recursive tree, and both
Python source versions. It narrows the recovery gap without substituting a
new predictor for the historical procedure. The separate explicit prediction
comparison is [PR #147](https://github.com/tobrien6/voynich-manuscript-research/pull/147).

## Captured history and static observations

The 2026-10-12 capture has one advertised branch, `master`, at
`643b881b2937bae8193814d8ff5d6e99a48bf7c5`, and no advertised tags. Its complete
parent chain contains six commits, ending at a root with no parents. Every
recorded Git author date is July 30, 2015; these are commit metadata, not proof
of when the analysis was first developed. The
[complete report](reddy-history-intake.json) retains full commit/parent/tree
identities, literal paths, modes, API blob sizes, blob identities, both source
fingerprints, parsed definition/import inventories and capture receipts.

| Commit, oldest first | UTC author time from API | File blobs | Named program |
| --- | --- | ---: | --- |
| `d483622` | 18:43:41 | 1 | None |
| `45cc018` | 18:51:26 | 4 | None |
| `e162685` | 19:22:00 | 7 | None |
| `7e446cc` | 19:41:45 | 10 | None |
| `03ed8aa` | 20:09:04 | 11 | `basic_stats.py`, 668 bytes |
| `643b881` | 21:53:10 | 12 | `basic_stats.py`, 2,466 bytes |

Only `basic_stats.py` has a program suffix under the explicitly enumerated
suffix rule (`.py`, `.ipynb`, `.r`, `.m`, `.java`, `.c`, `.cpp`, `.sh`, `.pl`,
`.rb`, `.jl`, case-insensitive). The other literal filenames are `.gitignore`, `README.md` and
`.wds` data files. The report retains every filename, rather than treating the
suffix rule as a proof about all possible file contents.

The [earlier source](https://github.com/sravanareddy/deciphervoynich/blob/03ed8aa41458c9968767a75576e4df9454345056/basic_stats.py)
has one function that reads a supplied filename, splits on whitespace and
counts token/type word-length distributions. Its Git blob is
`0d68aa25c6b155b9f6ac5c43acbd07d04b196036`, with SHA-256
`a18f815627e25ef45c8195d1b99d10bec9b1190fc66bfeeb69bc6b12a2ddb151`.
It contains no held-out letter predictor or fold procedure.

The [later source](https://github.com/sravanareddy/deciphervoynich/blob/643b881b2937bae8193814d8ff5d6e99a48bf7c5/basic_stats.py)
adds a corpus class, word unigram/entropy functions and a character-substitution
word-entropy comparison. Its seven definitions and literal B input path agree
with the prior source intake. Its Git blob is
`d78b72f164ca76258fef7eb29001ffad2ec071dd`, with SHA-256
`12102b9c290838ebe0c60580f62cb449759cb71d13949dbcf5c23c82d1aa4ccc`.
It also contains no Table 2 predictor, fold assignments or letter-accuracy
report. Both complete small source files were statically read and parsed;
neither was imported or executed.

The full annotated Voynich input appears at the root and has one unchanged
Git blob across all six snapshots. The B annotated, B paged and full paged
inputs first appear at `45cc018` and each have one unchanged blob across their
five snapshots. This is a file-identity observation within the recovered 2015
chain. It does not establish 2011 preprocessing or historical input identity.
No comparator-language payload was fetched in this follow-up.

## Integrity checks and reproduction

The producer reads a local capture, makes no network call and never executes
author code. It requires the fixed complete commit chain and tree identities,
rejects truncated trees, and reconstructs all six root and six directory Git
tree objects from literal paths, modes and child identities. This verifies
tree contents against Git hashes; blob sizes remain API metadata unless the
blob was fetched. Both Python files additionally match their exact size,
SHA-256 and Git blob hashes. JSON duplicate keys and non-finite numbers fail.

To reconstruct the capture with GitHub CLI, use the authorized account in the
[contribution guide](../../CONTRIBUTING.md). Save the paginated `--slurp`
responses from these public API paths as `commits.json`, `branches.json` and
`tags.json` inside a local reference directory:

```text
repos/sravanareddy/deciphervoynich/commits?sha=643b881b2937bae8193814d8ff5d6e99a48bf7c5&per_page=100
repos/sravanareddy/deciphervoynich/branches?per_page=100
repos/sravanareddy/deciphervoynich/tags?per_page=100
```

For each full tree identity in the report, save the non-paginated response
from `repos/sravanareddy/deciphervoynich/git/trees/TREE_SHA?recursive=1`
as `COMMIT_SHA.tree.json`. Retrieve only the two program blobs using
`repos/sravanareddy/deciphervoynich/git/blobs/BLOB_SHA`, decode their Base64
content locally and save as `BLOB_SHA.py`. No corpus or comparator blob is
needed. API response bytes are fingerprinted as capture receipts; a future
provider formatting or metadata change can alter those receipts without
changing a Git tree, so retain the original capture for an exact replay.

```sh
PYTHONPATH=tests python3 -m unittest test_reddy_history test_reddy_source_intake -v
python3 scripts/audit_reddy_history.py --reference LOCAL_CAPTURE --check
# Inspect a newly retrieved capture without replacing the saved receipt:
python3 scripts/audit_reddy_history.py --reference NEW_CAPTURE --output NEW_REPORT.json
```

Ten focused history/intake tests pass. Synthetic cases cross-check tree
reconstruction against native Git, exercise directory sorting, reject omitted,
duplicate, changed and truncated entries, reject incomplete chains and strict
JSON failures, and confirm that source inventory does not execute source code.
The local report replays completely; a separate native Git reconstruction
also verifies all twelve captured root/directory tree occurrences (ten distinct
tree objects) and both program blob identities. Raw API payloads and author code remain local. Published fields
contain original analysis and public identity metadata, with no contact fields.

## Remaining recovery gap

No earlier Table 2 implementation was recovered from this complete advertised
master chain. This search excludes deleted/unreachable references, forks,
other repositories, institutional archives and private author files. It does
not claim that the original predictor never existed. A later archive search
or an authorized author inquiry could recover it; no inquiry was sent here.

The existing prediction discrepancy therefore remains unresolved. This audit
adds source provenance for future baseline or decoding tests; it supplies no
language, glyph interpretation, decipherment or translation. Matching source
populations or stable later blobs cannot replace a recovered method or the
project's [decipherment evaluation protocol](../DECIPHERMENT_PROTOCOL.md).
