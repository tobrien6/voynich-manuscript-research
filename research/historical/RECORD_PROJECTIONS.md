# Native record boundaries under the lossy lowercase comparison

On **223 exact shared page IDs**, historical H and modern IT2a have equal
nonempty lowercase record-projection multisets on **211** pages. Of these,
**182** also have the same nonempty record order and **29** have a different
order. On `f46v`, a matching joined stream instead conceals different record
projections. Page-level string or frequency equality therefore does not settle
native record order or segmentation.

This is an exposed-data source diagnostic. It creates **no verified locus
crosswalk**, image-region association, source correction, glyph equivalence,
source-accuracy ranking, statistical evaluation, decipherment or translation.

## Fixed sources, selection and losses

The [plan](RECORD_PROJECTION_PLAN.md) was committed at
`b5e27aa` before this computation. The [parent lowercase diagnostic](LOWERCASE_PROJECTION.md)
and its 183/40 page split, count discrepancies and selected source bodies were
already known. This follow-up has no untouched or preregistered-test claim.

Reuse the credited [historical 1.6e6 catalog](../../data/historical/interlinear-16e6.json)
and [IT2a export catalog](../../data/transliterations.json), preserving Jorge
Stolfi, the interlinear contributors, Takeshi Takahashi and modern publisher
René Zandbergen's source attribution. Source and derived-data terms remain those
in the [data note](../../data/historical/README.md); the code license does not
replace them. Historical-paper input identity remains unproven.

Historical H retains all **5,214 native envelopes**, including padding-only
and otherwise empty lowercase projections. Modern IT2a retains **5,214 present
loci**; the explicit nonexistent `f89v2.26,!Lf` is listed separately and never
enters a record group. Each side has 225 record-bearing page IDs. Historical
`f101r1`/`f101v2` and modern `f101r`/`f101v` remain unmatched strings, without
truncation or inferred aliases.

Apply the parent's source-specific projection independently to each body:
remove balanced historical human comments or modern IVTFF human comments and
defined text tags, then retain only ASCII a–z. Boundaries, spaces, unknown/rare
signs, case and other notation are still lost **within each record**. Exact
projected strings are compared before hashing; a digest collision between
distinct strings fails. The original source bodies are unchanged.

For each exact page, compare the ordered list of **nonempty** projections, its
multiset including multiplicities, its joined stream, and symbol frequencies.
Keep every empty-projection locator with its source-file line, native unit/kind
and original page-order index. Empty projections never supply positive matches;
comparison fields are null if either side has no nonempty records.

## Results and native record groups

| Comparison on the 223 shared pages | Pages |
| --- | ---: |
| Equal nonempty record-projection multiset | 211 |
| Equal nonempty record-projection order | 182 |
| Equal multiset, different record order | 29 |
| Equal joined stream, different record multiset | 1 (`f46v`) |

Equal multisets with different order mean a permutation of the nonempty
**lossy projections** can reconcile those lists. This does not establish a
unique original-record permutation when projections repeat, or identical native
bodies/physical rows. The 29 pages are a subset of the parent's 40 different
joined-stream pages; their ordering difference suffices to explain the mismatch
at this projection level. The other cases are not silently attributed to a
correction, split or merge.

The [complete report](record-projections.json) inventories **5,104 shared
nonempty projection groups** within exact shared pages. **5,076** contain exactly
one historical and one modern record; **28** have multiple possible records on
at least one side. Shared groups contain 5,149 H records and 5,150 present IT2a
records, including those multiplicities. These counts are not rates of glyph
accuracy or independent source agreement.

Every group contains its lowercase length/digest and all original locators,
source-file lines, historical unit or modern kind, and page-order indices. A
one-to-one group is equality of this projection uniquely within that page;
it is **not an accepted alias**. Ambiguous groups retain complete many-to-many
possibilities without pairing by order. One-sided groups and unmatched pages
remain visible. The report copies no projected text bodies.

| Exact page | H native / nonempty records | IT2a present / nonempty records | Joined stream equal | Record multiset equal | Nonempty record order equal |
| --- | ---: | ---: | --- | --- | --- |
| `f46v` | 12 / 12 | 13 / 13 | Yes | No | No |
| `f75v` | 69 / 69 | 70 / 70 | No | No | No |
| `f89v2` | 28 / 28 | 27 / 27 | No | No | No |
| `f106r` | 47 / 46 | 46 / 46 | Yes | Yes | Yes |

On `f106r`, the empty historical `f106r.P.29;H` is retained outside the nonempty
comparison, so equality does not erase the unequal native denominator. The
other empty projections are six records per edition on `f49v` and two per
edition on `f66r`; an empty projection is not a physical absence assertion.
`f89v2` preserves the parent's separate nonexistent-envelope discrepancy.
The [source annotation note](../transcriptions/NONEXISTENT_LOCUS.md) and
[provisional image context in PR #129](https://github.com/tobrien6/voynich-manuscript-research/pull/129) do not establish
an exact historical/modern/image locator mapping.

## Reproduction and validation

Python 3.10 or later, standard library only, from the repository root:

```sh
python3 scripts/audit_historical_record_projections.py --check research/historical/record-projections.json
python3 scripts/audit_historical_record_projections.py --output /tmp/record-projections.json
python3 -m unittest tests.test_historical_record_projections -v
```

The calculation verifies catalog/archive/member/export pins and complete
parent-report content before using it. The report pins its plan, parent bytes
and calculation dependencies. Checking compares complete content with JSON
numeric/Boolean distinctions and rejects duplicate keys. Output protection
rejects source, catalog, parent, plan and implementation paths and their
symlink/hardlink aliases before calculation. A failed check preserves a separate
output destination.

Ten tests cover record permutation, multiplicities, split/merge boundary loss,
empty denominators, source-specific comments/metadata, unmatched page names,
nonexistent/non-H exclusions, invalid inputs/digest collisions, 24 temporary
direct/symlink/hardlink output aliases, numeric-type/duplicate-key checks and
complete real-input replay. A separate raw-envelope scanner, using neither the
production readers nor projection function, independently reconstructed all
**10,428 selected records**, every group/descriptor across 227 union pages and
all order/multiset/stream/frequency flags.

Any later crosswalk needs full source-specific notation and region evidence,
with empty, ambiguous, split/merged and nonexistent cases preserved. Reusing
these exposed projections supplies no independent validation or word boundaries.
