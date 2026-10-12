# The original 1921 lecture behind Newbold's physical description

The earlier source credited in the [1928 book record](NEWBOLD_TERMINAL_SOURCE.md)
is now inspected in a pinned, publicly downloadable journal scan. Newbold's
printed pp. 461–462 contain the final-number claim **116** and the Part V
folio ranges **103–108, 111–116** found in the later book. This closes the
original-lecture access gap for those statements. It supplies historical
source context, not the legacy Yale `117v` to current `116v` correspondence.

## Identity and representation

William Romaine Newbold, *The Voynich Roger Bacon Manuscript: The Mary Scott
Newbold Lecture, Lecture V*, appears in *Transactions of the College of
Physicians of Philadelphia*, third series, volume 43 (1921), pp. 431–474.
The [public archive record](https://archive.org/details/transactionsofco3431coll)
and [download](https://archive.org/download/transactionsofco3431coll/transactionsofco3431coll.pdf)
identify the inspected representation. PDF page 7 visibly gives the series,
volume, Philadelphia printing and year; page 11's contents list separates
Voynich's preceding historical sketch (p. 415) from Newbold's lecture (p. 431).
The lecture opening, PDF page 519, names Newbold and its footnote gives
**20 April 1921** as the reading date. That opening has no visible printed
page number; the contents and following printed p. 432 supply its locator.

The downloaded Text PDF is **52,867,297 bytes, 652 PDF pages**, SHA-256
`b661753be6315f0b0d5147acc73bb1d8d314fd5d8dc4c43413c9d4e4730dca65`.
These identify one digital derivative, not an authenticated physical copy,
the original lecture performance, or completeness of the digitization chain.
The volume's publication notice separates its contributors' statements from
the College's responsibility. No endorsement of Newbold's claims follows
from journal publication or archive preservation.

## Directly inspected locators

| Printed page / PDF page | Bounded observation |
| --- | --- |
| 454 / 542, opening paragraph and note 26 | Newbold attributes a proposed name reading to alphabets derived from the final-page key. The note displays a short opening, removes designated elements to obtain a proposed Latin sentence, and assigns values to other elements. These are Newbold's reported operations, not verified glyph readings. |
| 459–460 / 547–548, bracketed note | Describes slides in the second part of the lecture and says printing cost prevents its complete reproduction. The note discusses unresolved reading operations and limits confidence in exact wording. The printed article is not a complete record of every exhibited slide or explanation. |
| 461 / 549, opening physical description | Reports the last leaf's number as **116**, eight missing leaves and equivalent-page totals; calls the final page a key. The number is not printed as `116v` in this sentence. The key, dating and authorship claims remain historical assertions. |
| 462 / 550, paragraph and note 34 table | Describes 23 text pages plus a last page called a key. Part V gives **ff. 103–108, 111–116**, 12 leaves and 24 text pages; missing ff. 109–110 contribute four further pages to the reported total 28. These counters retain their own meanings and are not current canvas counts. |
| 463–474 / 551–562 | Contains the slide list and reproduced Plates I–V, with captions naming Newbold. These inspected pages do not reproduce the final short-text material. This bounded observation does not establish its absence from uninspected parts of the volume or other editions. |

The complete credited range **461–474** was visually inspected, including
all five plates, captions, footnotes, headers and page boundaries. Additional
identity and nearby context pages are individually listed in the
[ledger](newbold-1921-lecture.json). Neither the full 44-page lecture nor the
whole journal was visually audited. A page-index file and local text extraction
were navigation aids; every cited printed locator was checked against pixels.
No global numeric offset is used to assert uninspected correspondences.

## Relationship to the 1928 book

The later editor's note, printed p. 44 / PDF p. 78 of S009, credits pp. 461–474
of the 1921 *Transactions* and says some material from pp. 464–465 was used in
other chapters. Direct comparison of the opening physical-description
paragraphs and Part V rows supports the specific retained facts above.
It is not an assertion of exact identity between the complete chapters,
their typography, all wording, or their illustrations.

The short printed opening in 1921 note 26 agrees in its word sequence with
the opening displayed on the 1928 book's printed p. 73 / PDF p. 117. The
1921 note's proposed Latin extraction and alphabet assignments are described
in their own context. The later book's printed p. 109 / PDF p. 158 displays
an expanded three-line proposal and further assignments. Historical proposed
renderings, different rule descriptions and editorial explanations must stay
separate if the proposal is evaluated under the
[decipherment protocol](../DECIPHERMENT_PROTOCOL.md). This follow-up creates
no manuscript glyph transcription and adopts no historical reading.

S009's original JSON ledger remains byte-identical to accepted
[PR #190](https://github.com/tobrien6/voynich-manuscript-research/pull/190): its
`original_lecture_inspected: false` describes that earlier snapshot. S010 is
the subsequent inspection, rather than a rewrite of the prior exposure record.
The accepted correction to S009 also remains intact: the editor describes
papers and charts of varying kinds, without establishing their different dates.

## Extraction discrepancy and access limits

At printed p. 461 / PDF p. 549, local `pdftotext -layout` produces `116V` where
the scan visibly prints **116,**. The added character is an extraction error,
not evidence of a historical verso designation. This is one observed occurrence,
not an assessment of the entire OCR layer's accuracy.

The first canonical download timed out after transferring a partial file;
its resume returned HTTP 500. Anonymous public archive metadata supplied the
storage-server route used to finish that same file. Only after the downloaded
size matched the public file metadata, the PDF signature parsed and Poppler
reported 652 pages was the file inspected as the recorded representation.
An earlier Google Books download returned HTTP 429 and was not retried through
different accounts or client identities; no Google PDF contents are claimed.
The potentially confusing Google record title/length is not used to identify
this archive volume or conflate Voynich's sketch with Newbold's lecture.

The PDF, full extraction, page index, retrieval receipts and rendered pages
remain local. Only selected source facts, links, fingerprints and our inspection
notes are published; no scan redistribution or blanket reuse license is asserted.

## Validation and remaining question

The alias registry remains SHA-256
`627ae452e40b2ea176ac50a641c1fb31c58fcbbcfa5fffddd4ed87415995dfc8`.
Existing alias tests and registry validation pass; the actual legacy `117v`
lookup still exits 1 with `mapping_allowed: false` and a null target. No
checker, tests, native corpus, statistical input or original source ledger is
changed. Validation of these records does not validate Newbold's reading.

The actual Kennedy/Churchill reference 7 remains uninspected. Finding this
matching historical description does not identify that endnote or its edition.
An explicit custodial correction or documented correspondence to the current
final recto/verso is still required for
[issue #13](https://github.com/tobrien6/voynich-manuscript-research/issues/13).
Historical final-leaf numbering, a reported key and a plausible subject match
do not authorize a foliation alias, dating conclusion or translation.
