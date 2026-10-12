# Exploratory locus-initial encoded-length result

On the fixed **2,964-locus common cohort**, the initial encoded token is longer
than the mean remaining token by **0.4380–0.4772 ASCII letters**, depending on
edition and spacing policy. Each observed contrast exceeds its conditioned
token-order reference interval. This is a reproducible property of the selected
encoded records; language, glyph units, and plaintext remain unresolved.

## Prospective method and inputs

The [protocol](LOCUS_POSITION_PROTOCOL.md) and
[machine-readable settings](locus-position-protocol.json) were committed in
`d75d935` before this chat computed token-level results. It is a local
prospective record, not an independently timestamped preregistration. The
analysis follows its fixed metric, cohort, and 2,000-replicate null settings.

Inputs are the pinned ZL3b and IT2a files in
[the source catalog](../../data/transliterations.json), processed by the
[conservative adapter](../transliteration/TOKEN_ADAPTER.md). Use the exact
source hashes and distinct alphabet identifiers. The adapter verifies the
source bytes; the analysis runner validates the adapter's declared hashes
against the protocol and records the exact input JSON checksums. It does not
independently reconstruct or authenticate an arbitrary supplied token packet.

The cohort is the intersection of eligible **P0/P1** loci with `@`, `+`, or `*` locators
and at least two tokens in every source/policy combination. Every included key
and every excluded key/reason is in
[locus-position-results.json](locus-position-results.json). The sorted cohort
has SHA-256 `b54e90732d33e3d656499a7cc7769a9904cbdbaf57d2760b1196a1d4dbbfe40b`.

## Results

Each locus contributes equally to the mean contrast. The reference holds each
locus's encoded-token multiset and count fixed, then chooses the first token
uniformly. Its exact mean is zero. The interval below is the empirical 2.5%–97.5%
range of the conditional null, not an uncertainty interval for the manuscript
or a confirmatory test.

| Edition / comma policy | Encoded tokens | Distinct strings | Hapax strings | Initial-minus-rest mean | Conditional null range |
| --- | ---: | ---: | ---: | ---: | --- |
| IT2a / split | 24,941 | 5,271 | 3,509 | +0.4380 | −0.0585 to +0.0635 |
| IT2a / join | 24,941 | 5,271 | 3,509 | +0.4380 | −0.0605 to +0.0620 |
| ZL3b / split | 25,322 | 5,237 | 3,497 | +0.4421 | −0.0680 to +0.0682 |
| ZL3b / join | 23,520 | 5,996 | 4,233 | +0.4772 | −0.0698 to +0.0715 |

Lengths count case-preserving ASCII letters. In this measure `ch` has length
two; no manuscript-glyph segmentation is inferred. Hapax strings occur once
within the particular source/policy/cohort. The editions are paired source
representations, not independent replication of a historical claim.

IT2a's token sequences and observed statistic are identical under the two comma
policies because that edition records no uncertain-space commas. Its simulated
intervals differ slightly because the fixed draw context includes policy.
ZL3b's observed sign persists under both treatments; joining uncertain spaces
changes token counts and string vocabulary while keeping the same loci.

The full JSON includes all 2,000 draws per variant, exact conditional standard
deviations, length histograms, frequency summaries, input/implementation hashes,
and exclusion groups. Exclusion reason counts can overlap; each source record
is accounted for exactly once as included or excluded in a variant. The
analysis excludes 2,251 of 5,215 IT2a records and 2,421 of 5,385 ZL3b records per
policy. These totals include unselected locus classes, not just difficult text.

## Verification and reproduction

The observed contrasts were independently checked using exact rational
arithmetic on the retained token lengths. Seventeen focused synthetic checks
cover finite nulls, equal locus weighting, common-cohort selection, changed
metadata, duplicate records, source/policy mismatches, and visible exclusions.
The adapter and boundary grammar checks were also run before the corpus analysis.

From the repository root:

```sh
python3 scripts/audit_transliterations.py --check research/transliteration/coverage_audit.json
python3 scripts/eva_token_adapter.py --uncertain-spaces split --output /tmp/voynich-position-split.json
python3 scripts/eva_token_adapter.py --uncertain-spaces join --output /tmp/voynich-position-join.json
python3 scripts/run_locus_position_baseline.py \
  --split /tmp/voynich-position-split.json \
  --join /tmp/voynich-position-join.json \
  --check research/baselines/locus-position-results.json
python3 -m unittest discover -s tests -p 'test_locus_position_*.py' -v
```

The comparison includes cohort membership, all exclusions, the null draws and
summary, and provenance. A changed source/adapter/implementation requires
investigation before replacing the recorded result. The runner performs no
network requests and prevents its output from overwriting an input.

## Limits and next test

This is exploratory whole-corpus analysis with known prior source and selected
image exposure. It creates no untouched evaluation set. Conservative exclusions
can bias the cohort toward easier readings. Locus metadata has not been checked
against physical line boundaries; the finding is **locus-initial**, not a
manuscript-line or paragraph-initial conclusion.

The null conditions on encoded tokens and randomizes their order; it is not a
language model or a model of manuscript production. Exceeding that reference
does not select among language, cipher, or nonlinguistic mechanisms. Future
candidates can be checked for this encoding-level position effect under the
same declared preprocessing, together with additional controls and independent
image/line review. A new confirmatory candidate needs its own frozen evaluation
plan and exposure declaration.
