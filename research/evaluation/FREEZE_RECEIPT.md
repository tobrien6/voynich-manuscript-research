# Checking the artifacts in an evaluation freeze commit

The [split validator](SPLIT_FORMAT.md) checks declarations and input hashes,
but cannot tell whether a claimed freeze commit contains the declared rules
or preprocessing. The artifact audit adds that check to the
[decipherment protocol](../DECIPHERMENT_PROTOCOL.md). It binds a pre-fit split,
its input, and the listed rules/preprocessing files to actual Git blobs, then
compares their exact bytes with the current files and optionally a later run
commit. A changed rule file cannot pass merely by retaining its version name.

This checks declared artifacts and Git ancestry. It does not prove when a
person fitted a candidate, whether exposure declarations are honest, whether
every dependency is listed, or whether the candidate is a valid decipherment.
It does not choose a real split or execute candidate code.

## Receipt and checks

Receipt schema version `1` has exactly four top-level fields:

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer `1`. |
| `candidate_version` | Nonempty identifier matching the frozen split. |
| `freeze_commit` | Full lowercase Git commit object ID, resolvable locally. |
| `artifacts` | Exactly `split`, `input`, `rules`, and `preprocessing`. |

`split` and `input` are individual `{ "path": ..., "sha256": ... }` records.
`rules` and `preprocessing` are nonempty lists of those records, allowing a
procedure to span several files. Paths are literal relative repository paths;
absolute paths, dot components, `.git`, backslashes, and duplicate paths within
one role are rejected. A file serving more than one role can be declared in
each. List helper code, mapping tables, dependency/version declarations, and
other files affecting behavior; the checker does not discover omitted files.

The auditor obtains regular-file objects with
[`git ls-tree`](https://git-scm.com/docs/git-ls-tree) and reads their blob bytes
with [`git cat-file`](https://git-scm.com/docs/git-cat-file), rather than trusting
the current files to describe the freeze. It disables
[object replacements](https://git-scm.com/docs/git-replace) and rejects legacy
graft overrides so those mechanisms cannot substitute a different tree or
history under the recorded object ID. For each artifact it verifies:

1. The file exists as a regular tracked file in the freeze commit. Symlink,
   directory, and missing entries fail.
2. The recorded SHA-256 matches those committed bytes.
3. The current regular file matches the committed bytes. Symlinks in its
   working path and missing files fail.
4. If a run commit is supplied, it is a strict descendant of the freeze commit
   and contains the same bytes for every artifact. The ancestor test uses
   [`git merge-base --is-ancestor`](https://git-scm.com/docs/git-merge-base).

The committed split must also pass the existing frozen-split validator with
the committed input bytes, match the receipt's candidate identifier, and have
`fit_started_at: null`. This is the pre-fit split snapshot. Record later fitting
times in a separate run record without changing that snapshot. Duplicate JSON
members and non-JSON numeric constants are rejected for receipts and splits.
`--repo` must be the repository root; the default is this script's repository.

## Before fitting and before a run

Commit the split, exact input, complete declared rules, and preprocessing
artifacts. Obtain that full commit ID and create a receipt from its blobs:

```sh
task_freeze_commit="$(git rev-parse HEAD)"
python3 scripts/audit_evaluation_freeze.py record \
  --commit "$task_freeze_commit" \
  --split PATH_TO_PRE_FIT_SPLIT.json --input PATH_TO_PINNED_INPUT \
  --rules PATH_TO_RULES PATH_TO_RULE_HELPER \
  --preprocessing PATH_TO_PREPROCESSING PATH_TO_DEPENDENCY_VERSIONS \
  --output PATH_TO_NEW_RECEIPT.json
python3 scripts/audit_evaluation_freeze.py check PATH_TO_NEW_RECEIPT.json
```

The output must be new and cannot overwrite a pinned artifact. The receipt
is created after its target commit to avoid a self-referential hash. Preserve
it and the referenced commit in the research record. Run the check immediately
before executing a candidate. After committing a later run record, also use
`check PATH_TO_RECEIPT.json --run-commit FULL_RUN_COMMIT_ID`. The check reads
artifacts only; it does not itself run fitting or evaluation.

If artifacts change, stop treating the result as the old frozen version.
Record a new candidate/split version and exposure history. Rewriting or
squashing history may make a referenced commit unavailable or remove its
ancestry relationship; preserve the original freeze commit rather than
silently substituting a new commit ID. A later descendant commit supports
repository order, not an independently authenticated clock or execution log.

## Synthetic reproduction

The committed fixtures contain no manuscript material. From a commit containing
these fixtures, the following records and checks their identity:

```sh
task_freeze_commit="$(git rev-parse HEAD)"
python3 scripts/audit_evaluation_freeze.py record \
  --commit "$task_freeze_commit" \
  --split research/evaluation/examples/synthetic-freeze-split.json \
  --input research/evaluation/examples/synthetic-input.txt \
  --rules research/evaluation/examples/synthetic-rules.md \
  --preprocessing research/evaluation/examples/synthetic-preprocessing.md \
  --output /tmp/synthetic-freeze-receipt.json
python3 scripts/audit_evaluation_freeze.py check /tmp/synthetic-freeze-receipt.json
PYTHONPATH=tests python3 -m unittest test_evaluation_freeze test_evaluation_split -v
```

Use a fresh output path if the receipt already exists. The synthetic dates
and exposure declarations are test data. Tests create temporary Git histories
and exercise changed rules, preprocessing, source bytes, declared hashes,
candidate identifiers, unrelated histories, changes present only in the run
commit, unresolved exposure, and symlink/path errors. Passing these tests or
the receipt audit verifies reproducibility of listed bytes, not the correctness
of a reading, its translation, or its research history.
