# Literal native H / Reddy record correspondence

The recovered paper-associated Reddy full annotation has the same literal keys,
order and fallback-retained token counts as every nonempty selected H record in
the native 1.6e6 release. The 5,214/5,213 record gap is the H-only envelope
`f106r.P.29;H`, which normalizes to zero tokens. This resolves the **nominal
record/count gap** without establishing text or alphabet equivalence.

## Sources, rule and exposure

The [native catalog](../../data/historical/interlinear-16e6.json) fixes the
[publisher's 1.6e6 ZIP](https://www.ic.unicamp.br/~stolfi/EXPORT/00-EXPORT/98-12-28-interln16e6/text16e6.zip)
and its `L16+H-EV/TEXT16E6.EVT` member. The
[Reddy manifest](../literature/reddy-source-manifest.json) fixes commit
[`643b881`](https://github.com/sravanareddy/deciphervoynich/tree/643b881b2937bae8193814d8ff5d6e99a48bf7c5),
tree `4e529b53db765deb6c243a38731c947e7ab25e92`, and six selected local
files. The full annotated input is `data/voy.ann.wds`, SHA-256
`a3a1fb64a8f227e0fb0b81e7fe6aecec719888a4efeb5c1f7df5e2539c91d1d4`.
The [accepted intake](../literature/REDDY_SOURCE_INTAKE.md) records its association
with [Reddy and Knight (2011)](https://aclanthology.org/W11-1511/), later Git
chronology, reported Currier notation and absence of an original execution receipt.

Join the literal four-field Reddy header to native H's
`(page, unit, line, transcriber)`. Preserve case, suffixes, units and source tags;
do not introduce aliases, page pairing, alphabet conversion or token-string
matching. All union records retain separate source ordinals and physical file
lines. The display array sorts keys only for reproducibility; the order test
uses each source's original shared-key sequence.

The [human plan](REDDY_ENVELOPES_PLAN.md) and
[machine parameters](reddy-envelopes-plan.json) were committed at
[`6b912d0`](https://github.com/tobrien6/voynich-manuscript-research/commit/6b912d0)
and the synthetic-tested producer at
[`5d98ff5`](https://github.com/tobrien6/voynich-manuscript-research/commit/5d98ff5).
Both were pushed before the new full-source comparison. Both parent inventories,
historical parsing counts, source material and two leading header formats were
already exposed. This is a descriptive source audit, not untouched evaluation.

Before comparison, the producer verifies eleven frozen dependency hashes, all
six local reference byte/SHA-256/Git-blob identities, and complete replay of the
accepted Reddy intake, native intake and historical parsing reports. It does not
execute author code. Both H count stages use the unchanged accepted normalizer:
empty listed-code set retains fallbacks; the accepted listed-code set deletes
them. Neither stage applies any manual exclusion variant. Reddy tokens retain
their original whitespace split and notation.

## Complete results

The [complete report](reddy-envelopes.json) retains all 5,214 union records and
225 page summaries, with both H count stages, Reddy counts, source ordinals/file
lines, body/vector hashes, signed deltas and order results. Raw bodies and token
strings are not included.

| Stream | Records | Empty normalized records | Tokens | Shared records with unequal counts versus Reddy |
| --- | ---: | ---: | ---: | ---: |
| H, fallback retained | 5,214 | 1 | 37,919 | 0 of 5,213 |
| H, listed-code deletion before manual exclusions | 5,214 | 3 | 37,896 | 8 of 5,213 |
| Reddy full annotation | 5,213 | 0 | 37,919 | — |

There are 5,213 shared keys, one H-only key and zero Reddy-only keys. All shared
keys occur in exactly the same order; their ordered-key digest is
`894836c3d1bbecb8b29769f285dff8c480589ba0f13f331a84cc35a8c66415cb`.
Every shared fallback-retained record has exactly Reddy's token count: both
positive and negative discrepancy sums are zero. Equal global counts therefore
hide no record-count cancellation under this fixed stage.

The sole unmatched H record `f106r.P.29;H` has selected-H ordinal **4,422**
(zero based), physical member file line **35,353** (one based), and a 68-byte
parsed body whose SHA-256 is
`3431ff50b3cbe33b94cc8e35230da30886d086542c0600f77e8f9dc3379067ef`.
Its normalized token vector is empty under both rules. The source reader strips
outer line whitespace and the envelope separator before this body hash; it is
not a hash of the complete raw physical line. No record was dropped to achieve
the match.

All listed-code count changes are retained below. Differences are H minus
Reddy; the fallback-retained H count equals Reddy in every row.

| Native H envelope | Reddy / H fallback tokens | H code-deleted tokens | Difference |
| --- | ---: | ---: | ---: |
| `f1r.P2.7;H` | 11 | 10 | −1 |
| `f1r.P3.11;H` | 9 | 8 | −1 |
| `f38v.P.7;H` | 9 | 8 | −1 |
| `f57v.R2.1;H` | 69 | 54 | −15 |
| `f57v.R3.1;H` | 31 | 30 | −1 |
| `f57v.R4.1;H` | 33 | 31 | −2 |
| `f66r.M.23;H` | 1 | 0 | −1 |
| `f66r.M.27;H` | 1 | 0 | −1 |

The code-deletion stage has eight negative differences summing to −23, zero
positive differences and absolute discrepancy 23. The two f66r records become
empty under this stage; the H-only record was already empty. These comparisons
do not infer how the Reddy notation was generated or whether its symbols encode
the historical fallbacks.

## Reproduce and validation

Python 3.10 or later, standard library only. Retrieve the six selected reference
files using the accepted intake's pinned-source instructions and keep them local.
Run from the repository root:

```sh
python3 -m unittest tests.test_historical_reddy_envelopes -v
python3 scripts/audit_historical_reddy_envelopes.py --reference /path/to/local/reference --check research/historical/reddy-envelopes.json
python3 scripts/audit_historical_reddy_envelopes.py --reference /path/to/local/reference --output /tmp/reddy-envelopes.json
cmp /tmp/reddy-envelopes.json research/historical/reddy-envelopes.json
```

Eleven focused tests cover count cancellation, unmatched/empty populations,
literal case/unit/suffix/tag distinctions, changed shared order, both fixed
normalizations, duplicate/malformed headers, ordinal/file-line/count failures,
all eleven dependency pins, strict complete-parent comparisons, replay failures
before new measurement, and output failure preservation. One hundred temporary
direct/symlink/hardlink alias cases cover all twenty protected files, including
aliases introduced during computation. Inputs, plans and producer remain
unchanged in every case. Nonfinite JSON and a failed report comparison preserve
an existing output.

The report reproduces byte for byte. A separate scanner of raw ZIP member and
annotated headers, without importing the accepted readers/normalizer or this
producer, independently checked all 5,214 union descriptors, both normalized
vector hashes/counts, body hashes, Reddy vector hashes/counts, original order,
eight code-deletion discrepancies and the single unmatched identity. Report
SHA-256: `f40fbd503206498249370baa3e232992813079d11a565113cd460b1468e4ec75`.

## Interpretation, rights and next work

This is evidence of matching nominal envelopes, order and per-record token
counts under one declared historical normalization. It supplies a concrete
boundary/count constraint for a separately frozen notation comparison. It does
not prove identical word strings, glyphs, alphabet conversion, physical rows,
correct transcription, historically used preprocessing or original-author
2011/2013 corpus bytes. The H/IT2a projected-order work uses different sources
and a lossy projection. No linguistic, statistical-tail, decipherment or
translation claim is made here.

Native H reuse credits Jorge Stolfi, Gabriel Landini, Jim Reeds, Takeshi Takahashi
and the original transcribers credited in the unmodified member. Its publisher
permits copying, use, modification and republication with credit and without
additional conditions/copyrights; the repository MIT license does not replace
those terms. No license was found in the pinned Reddy tree, so its raw corpus
and author program remain local. This contribution publishes metadata and
original audit code only.

Any notation comparison must declare its mapping and unresolved symbols before
evaluating them, retain every record and contradiction, and distinguish string
conversion from verified manuscript glyph readings. The exposed full-source
correspondence supplies no reserved evaluation set.
