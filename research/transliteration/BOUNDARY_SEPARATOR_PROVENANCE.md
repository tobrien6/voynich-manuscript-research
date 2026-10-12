# Native notation behind disputed encoded cuts

Which source notation creates a disputed cut, and why does its disagreement
change when uncertain commas are joined? The accepted
[boundary concordance](TOKEN_BOUNDARY_CONCORDANCE.md) establishes identical
encoded strings but retains only whole-locus comma/drawing counts. This
[complete source-provenance ledger](boundary_separator_provenance.json) locates
the native notation at every offset where either spacing policy has a
source-only cut. It helps target later segmentation review without reading
manuscript pixels or deciding physical word boundaries.

## Scope and sources

The [published plan](BOUNDARY_SEPARATOR_PLAN.json) was committed and pushed at
`a7b2611` before these new measurements. The tracer and nine synthetic/guard
tests were published at `566f01a` before running on the native files. Both
commits descend from accepted main `af12c0ab25bc1520aff486fc2b2348b5c515a9d3`.
All source text, accepted analysis, prior source/image work and the pending
span/viewer contributions were already exposed; this is descriptive development.

The frozen input is the accepted 2,940-key cohort from 3,884 shared present P0
candidates, with 944 joint exclusions. All original eligible locators, singleton
loci and same-line fragments remain included. Exactly 2,054 paired chains are
identical; the other 886 are retained as unaligned keys. No folio, readability,
agreement or uncertainty-count filter is added.

The [source catalog](../../data/transliterations.json) retains credits, editions
and CC0 terms: Zandbergen–Landini ZL3b (`Eva-`) and Takahashi IT2a (`EvaT`, the
specified Landini–Stolfi extraction). Their source fingerprints are
`bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc`
and `7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5`.
The catalog, complete parent report and seven implementation dependencies are
checked against both frozen SHA-256 pins and actual base-commit blobs. The
native file blobs are checked too; complete parent replay precedes tracing.

The [IVTFF specification](https://voynich.nu/software/ivtt/IVTFF_format.pdf),
Tables 10–11 and section 6.7, distinguishes apparent spaces (`.`), uncertain
apparent spaces (`,`), drawing interruptions (`<->`) and drawing interruptions
with vertical misalignment (`<~>`). These report a transcriber's notation,
without independently validating the manuscript. The previously pinned document
is issue 2.0.2, 8 July 2025, SHA-256
`7ac9c4a82064763cac8767cca6f661cc4e1b4503ab9342acc03032ddb6939d49`;
printed pages 23–25 were rendered locally and visually checked. PDF and rendered
pages remain local. [Reference identities](comparator_documentation.json)
separate this document issue from native file versions.

## Complete offset accounting

The ledger has **1,458 distinct disputed ASCII offsets across 970 native loci**.
Every row preserves both sources' marker or explicit absence, native logical-text
range, neighboring letter positions, original identifier, first physical source
line, logical-text hash, and the cut flags for both spacing policies.

| ZL3b native marker | IT2a native marker | Disagreement policies | Offsets |
| --- | --- | --- | ---: |
| `,` | no separator | split only | 409 |
| no separator | `.` | split and join | 223 |
| `.` | no separator | split and join | 52 |
| `<->` | no separator | split and join | 1 |
| `,` | `.` | join only | 772 |
| `,` | `<->` | join only | 1 |

Thus 409 offsets disagree only under split, 773 only under join, and 276 under
both. The policy totals are 685 split exclusive cuts (462 ZL, 223 IT) and 1,049
join cuts (53 ZL, 996 IT). They retain the parent's 562 split and 767 join
disagreement loci. A locus can disagree under both policies at different offsets;
276 persistent offsets and 359 persistent loci use different units.

Among identical chains, 1,182 ZL commas account for all policy-dependent
changes: 409 create a ZL-only split cut, while 773 coincide with an IT separator
and cease to agree after joining. This does not say which transcription better
represents the manuscript. The remaining 617 of the cohort's 1,799 ZL commas
occur on different chains and receive no paired-offset classification.

Source-internal validation traces all 5,880 source records and reconstructs all
11,760 source/policy token arrays against the accepted adapter. It also checks
the complete native marker counts: ZL has 19,991 periods, 1,799 commas, 501 `<->`
and two `<~>`; IT has 21,408 periods, no commas, 507 `<->` and no `<~>`.
Zero exclusive `<~>` cuts does not mean that notation is absent from ZL.

## Cases and coordinates

The previously exposed cases remain interpretable without new image inspection.
At `f67r1.1` offset 45 and `f102r1.14` offset 38, ZL has a period and IT has no
separator. At `f102r1.15` offset 39, the direction reverses. At `f100r.24`,
ZL's offset-28 comma creates the split-only cut, while IT's offset-37 period
creates its persistent cut; opposing local count differences can cancel.

Every drawing-involved disputed offset is retained: `f13v.8` offset 30 pairs a
ZL comma with IT `<->` and disagrees only under join; `f75r.44` offset 48 pairs
ZL `<->` with no IT separator and disagrees under both policies. These are source
annotations, without a new image-region claim or priority/readability selection.

The encoded offset counts case-preserved ASCII letters from zero. Raw ranges
are half-open character positions in the exact parsed logical locus text after
file-continuation assembly and outer whitespace stripping. They are neither
physical-file byte offsets nor image coordinates. The current pinned records
have no continuation lines, but the field's logical-text meaning is retained.
For example, the ZL period at `f67r1.1` chain offset 45 occupies raw range
`[55,56)`, between letters at raw positions 54 and 56. The other source's absence
has a null separator range; formatting whitespace or ignored annotations need
not be absent between its neighboring letters.

## Reproduce and validate

```sh
python3 scripts/boundary_separator_provenance.py --check research/transliteration/boundary_separator_provenance.json
python3 scripts/boundary_separator_provenance.py --output /tmp/boundary-separator-provenance.json
python3 -m unittest tests.test_boundary_separator_provenance -v
```

The native tracer accepts the selected plain-letter grammar only, preserves case
and ignores formatting whitespace, free comments, text tags and paragraph tags.
It rejects unsupported forms and empty/consecutive/trailing separators. All
four native markers create split cuts; only commas cease to cut under join.
Different strings are never aligned. Full serialization finishes before the
final output-alias check, immediately ahead of writing; source, parent, plan and
implementation paths are protected. This is not an atomic filesystem guarantee.

Thirteen focused tests include all 341 marker sequences of one through five
pieces, all 25 marker/absence pairs, ignored annotations, malformed forms,
different-chain rejection, frozen input/blob drift, dropped dependencies,
initial/late temporary alias cases, full replay, native examples and all 2,916
source-side raw ranges/neighbors. A separate author-run raw regex/block scanner
imports no production reader, adapter or new producer. It constructs all native
token arrays, checks the four complete source/policy token totals, and exactly
matches every published offset record, identity, range, neighbor, flag, key set
and marker counter. This is a second implementation check, without an
independent-review or untouched-evaluation claim.

This accepted-parent follow-up does not modify the pending span inventory's
unresolved separator/glyph fields or depend on its merge. Native markers and
policy effects remain related, exposed source evidence. No physical word
assignment, source preference/correction, verified corpus join, new statistical
test, language, decipherment or translation is established. A separately frozen
image-review protocol could next adjudicate selected physical regions while
retaining these original alternatives.
