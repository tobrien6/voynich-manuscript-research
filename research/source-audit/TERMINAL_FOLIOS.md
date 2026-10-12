# Terminal-folio intake: writing rows and source records

## Question and scope

What can be established about the manuscript's final numbered recto/verso and
adjacent flyleaf while the older Yale catalog's `117v` reference is unresolved?

The [plan](TERMINAL_FOLIO_PLAN.md) was committed at `6449488` before this image
pass. It fixes Yale labels `116r`, `116v`, and `[Back flyleaf recto]`; the flyleaf
acquires no numbered transcription page. Source coverage and the publisher's
description were read before image inspection. Previous source files and
terminal-image observations were already exposed, so this is not blind review.

The [intake report](terminal-folio-intake.json) reuses the accepted IVTFF reader,
source-pin verifier, page-summary helper and alias lookup. It checks all five
[accepted source editions](../../data/transliterations.json), preserving their
alphabets, original identifiers and native subtype definitions. Image labels
are checked against the [existing Yale index](../image-index/README.md).
The alias remains blocked; no source file or numbering convention is changed.

## Native source coverage

| Edition | f116r present records | f116v header | f116v present records | f116v P0/P1 records |
| --- | ---: | --- | --- | ---: |
| ZL3b | 50 P0 | present | 1 Lx | 0 |
| IT2a | 50 P0 | absent | none | 0 |
| GC2a | 50 P0 | absent | none | 0 |
| RF1b-full | 50 P0 | present | 1 Lx | 0 |
| RF1b-basic | 50 P0 | present | 1 Lx | 0 |

All five files have no exact `f117v` page header. These are observations of
the pinned editions, not evidence that a physical leaf is missing. An absent
header is distinct from a present header with no present loci; both states are
retained by the audit. Nonexistent loci would remain explicit rather than being
counted as present text.

For `f116v`, ZL and both RF exports retain the native payload `oror.sheey`
outside free comments. ZL additionally has an inline free comment; the RF
exports do not. The audit records that difference without treating comment
content as native-script text or supplying a new reading. The two RF versions
are related derived exports, not independent manuscript observations. See the
[source credits and reuse terms](../transcriptions/SOURCES.md).

The publisher's [locus-type inventory](https://voynich.nu/extra/sp_transcr.html)
defines `Lx` as marginal, possibly external pieces of writing. It is a label
subtype rather than an ordinary paragraph line. Neither a page header nor one
stored Lx record promises complete coverage of all writing on its image.

## Image observations

[Observation records](terminal-folio-observations.json) bind this image pass to
the intake report's byte hash. They retain the five inspected derivative hashes,
original dimensions, links and native-pixel region coordinates. Pixels stay
local; the contribution publishes original observations and links. These are
one observer's initial layout judgments, not new Voynich glyph readings.

**Recto.** [Yale image 1006276, label 116r](https://collections.library.yale.edu/catalog/2002046?child_oid=1006276)
is 2,559 × 3,787 pixels. The
[upper-right numeral region](https://collections.library.yale.edu/iiif/2/1006276/1820,100,460,210/full/0/default.jpg)
appears to read `116`. Dense paragraph-like writing covers most of the surface;
star-like marks occur along the left margin of the upper part. The 50 records
in the table are source counts, not an independent census of physical rows.

**Verso.** [Yale image 1006277, label 116v](https://collections.library.yale.edu/catalog/2002046?child_oid=1006277)
is 2,686 × 3,697 pixels. The
[upper writing region](https://collections.library.yale.edu/iiif/2/1006277/550,160,1900,510/full/0/default.jpg)
shows four apparent horizontal rows: one relatively high short row and three
lower rows. Three small drawn forms appear in the left margin; most of the
lower surface lacks a dense text block. The four-row observation excludes
smaller or possible marginal marks elsewhere.

René Zandbergen's [Folio 116 description, f116v/Text](https://voynich.nu/q20/index.html)
separately describes four writing rows and a native-script word pair at the
beginning of the last row, counted as one locus. This supports keeping source
record counts apart from visible writing-row counts; the present audit does
not independently adjudicate that word pair's glyphs or region alignment.

**Flyleaf.** [Yale image 1037113, label Back flyleaf recto](https://collections.library.yale.edu/catalog/2002046?child_oid=1037113)
is 2,570 × 3,787 pixels. The distinct pale surface is largely blank at the
inspected scale, with creases and faint marks. No comparable upper four-row
writing block is apparent. Its unnumbered label supplies no native page ID,
material determination or `117` assignment.

## Consequence for the unresolved legacy reference

The [older Yale catalog](https://pre1600ms.beinecke.library.yale.edu/docs/pre1600.ms408.HTM),
Part VI, describes a three-line presumed key at `117v`. A four-row group at
current `116v` cannot by itself prove or refute correspondence: the older
description could refer to a subset, but that interpretation is not established
here. No purported key, language identification or catalog error is validated.

The existing [alias decision](../folio-aliases/README.md) remains unresolved.
The complementary [historical-numbering contribution, PR #57](https://github.com/tobrien6/voynich-manuscript-research/pull/57),
compares different page-counter schemes and preserves their identifiers. Those
counters, physical writing rows, and native Lx records must remain distinct.
That contribution is linked as related work; this PR makes no registry edit.

Before assigning an alias, obtain an explicit documentary correspondence or
independent scholarly review. Before using the terminal side for decipherment,
define the intended writing region and source coverage. Matching image labels,
equal source payloads or an attractive layout resemblance cannot perform either
step automatically. The investigation remains open in
[issue #13](https://github.com/tobrien6/voynich-manuscript-research/issues/13).

## Reproduce and validate

Python 3.10 or later, standard library only. The script fetches no images.

```sh
python3 scripts/audit_terminal_folios.py --check research/source-audit/terminal-folio-intake.json \
  --observations research/source-audit/terminal-folio-observations.json
PYTHONPATH=tests python3 -m unittest test_terminal_folios
```

Tests distinguish absent/empty headers and nonexistent loci, retain Lx payload
outside comments, preserve the unnumbered flyleaf, reject changed aliases and
nonunique/partial/combined image references, require the declared five editions,
and reproduce pinned coverage. Adversarial observation checks reject missing
views, a numbered flyleaf, changed byte binding and wrong region URLs. Automated
checks validate metadata and the unverified scope, not the four-row judgment,
numeral interpretation, physical losses, glyph readings or translation. Reopen
the linked images for those observations.
