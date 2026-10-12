# Source paragraph-marker pairing and membership plan

## Question and exposure

How many complete encoded paragraph units have exactly the same ordered locus
membership in pinned ZL3b and IT2a? Differences in start/end marks do not by
themselves quantify differences in paragraph-level sampling units.

Record this plan before computing the pairing and membership report. The
source corpus, previous annotation audits, and six manuscript images have
already been inspected. This is a descriptive metadata analysis of exposed
sources, not a new untouched evaluation or a decipherment hypothesis.

## Fixed method

- Select exactly the accepted ZL3b and IT2a sources, verify their bytes through
  the catalog loader, and use the shared IVTFF reader and annotation helper.
  Require unique non-interlinear locus keys.
- Process present generic-P loci in original source order on each encoded
  page, including every P subtype. Detect `<%>` and `<$>` only outside free
  comments. Record marker-bearing non-P loci separately without assigning
  them to paragraph units.
- Check pairing/order only. A start requires no open unit; an end requires an
  open unit on the same encoded page. One start followed by one end on a
  single locus is a valid one-locus unit. Repeated marks and end-before-start
  within the same locus are unsupported. A unit still open at page end is
  incomplete. Do not check glyph readings or full IVTFF conformance.
- Retain every anomaly with source identifiers and physical file line
  numbers. Withhold membership assignments for the entire affected page,
  preserving all of its P loci as unassigned. Do not synthesize boundaries,
  repair ordering, cross page boundaries, or keep a favorable subset of an
  anomalous page.
- On pages with balanced marker order, publish each complete unit's start/end
  keys and ordered member keys, plus its membership digest. Preserve leading
  and trailing unmarked P loci as unassigned. A page with no paragraph marks
  has unknown grouping; do not infer a single paragraph.
- Compare the intersection of present generic-P keys in both sources. Retain
  all per-source exclusions and any counterpart kind/presence metadata.
  Classify every shared locus as: same ordered unit members; different ordered
  members; grouped only in ZL; grouped only in IT; ungrouped in both; or
  ineligible because either page has anomalous marker order.
- For different grouped memberships, disclose whether either unit contains
  a key outside the shared generic-P intersection. This separates missing or
  differently typed source records from a difference solely in boundaries.
- Compare complete units by exact ordered member-key tuple. Report matched
  and unmatched unit counts in each source without counting paired sources,
  adjacent units, or multiple panels as independent manuscript samples.

## Evidence and limits

The publisher's IVTFF definition, section 6.9, defines alternating start/end
marks on the same page and assigns paragraph definitions to the transcriber.
All resulting units are source annotations, not verified physical paragraphs.
The source page `fRos` and foldout identifiers retain their native conventions;
this analysis makes no image alias or physical-leaf assignment.

No native token text, glyph mapping, image correction, statistical significance,
language identification, decoding, or translation is produced. A later
paragraph-level experiment must declare which source grouping or common-unit
cohort it uses and preserve the unassigned and anomalous denominators.

## Role and publication

Continue as owner/maintainer for this focused contribution under the user's
ongoing request. Verified GitHub login and upstream owner are `tobrien6`, with
admin/maintain/push permission. This work uses the isolated checkout and a topic
branch from accepted main. The established maintainer workflow handles merges;
no self-approval, reviewer assignment, or protection bypass is performed.
