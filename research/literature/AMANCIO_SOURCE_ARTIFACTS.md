# Author source-bundle inventory for the 2013 study

Question: does the authors' public preprint source bundle supply the processed
Voynich input or statistical analysis implementation needed for replication?

The [arXiv record](https://arxiv.org/abs/1303.0347v1) identifies version 1,
submitted 2013-03-02, and links the related PLOS DOI. Its
[versioned TeX-source download](https://arxiv.org/src/1303.0347v1) was retrieved
and inspected on 2026-10-12. The [inventory](amancio-source-inventory.json) pins
the 1,277,841-byte archive and each of its seven regular members independently.

## Observed contents

| Members | Role observed in this bundle |
| --- | --- |
| Five PDFs | Precomputed figure assets referenced by the article |
| `voynich-preSubmission_DR.tex` | Article typesetting source |
| `voynich-preSubmission_DR.bbl` | Formatted bibliography |

There is no separate processed token-stream file or statistical analysis
program among these seven members. Poppler `pdfdetach` 24.04.0 reported zero
embedded files in each of the five PDFs. The TeX and bibliography were inspected
as text, without compiling or executing them. No original processed corpus or
analysis implementation was recovered from these inspected artifacts.

The TeX source's database block at lines 921–933 is commented out with leading
percent marks, including its sole `37,762` occurrence. That draft source text is
kept distinct from the published
[Supporting Information S1](https://doi.org/10.1371/journal.pone.0067310.s007),
which supplies the H selection and detailed parsing instructions used in the
[methods register](methods.json) and [historical reconstruction](../historical/PARSING.md).
The inspected preprint source has no transcription-selection/manual-parsing
section. Authoring source and precomputed results do not establish the input
bytes or the implementation that produced those results.

This is a bounded inventory of one versioned bundle and its PDF attachments.
It is not an exhaustive search or a claim that the authors never released data
elsewhere. The source endpoint's filename list and contents are evidence about
this retrieved artifact only.

## Reproduce the inventory

Download the exact version to a local path, then verify against the recorded
container and member hashes. Python 3.10+ and its standard library suffice for
identity checks. `--check-pdf-attachments` additionally requires Poppler's
`pdfdetach` command.

```sh
curl --fail --location https://arxiv.org/src/1303.0347v1 --output /tmp/amancio-source-v1.tar.gz
python3 scripts/verify_paper_source_archive.py --archive /tmp/amancio-source-v1.tar.gz
python3 scripts/verify_paper_source_archive.py --archive /tmp/amancio-source-v1.tar.gz \
  --check-pdf-attachments
python3 -m unittest tests.test_paper_source_archive -v
```

The verifier checks outer identity before tar inspection and requires the exact
regular-member inventory, order, lengths and hashes. It reads members in memory;
archive paths are never extracted. For requested attachment checks, verified PDF
bytes are staged under a fixed temporary filename for `pdfdetach`. No TeX,
bibliography, or analysis program is run.

Five synthetic tests cover member/attachment checks, outer drift, changed
order/size/digests, duplicate or ambiguous paths/nonregular members, and unexpected
PDF attachments. The real bundle passes all identity and five attachment checks.
The source-text observations are separately inspected evidence; the byte verifier
does not certify their interpretation or reproduce the experiment.

The record preserves the linked arXiv non-exclusive distribution license.
The raw source bundle, TeX, bibliography and figures remain local and are linked
rather than redistributed here. The contribution publishes file identities and
original observations.

## Remaining requirement

Recover an author-compatible processed token sequence and parser, or obtain
precise evidence for unresolved selectors and boundaries. Freeze any resulting
reconstruction separately, with source/version/output hashes and a locator-level
ledger, preserving the four prior length discrepancies. Source-bundle availability
alone does not close that gap or supply a decipherment.
