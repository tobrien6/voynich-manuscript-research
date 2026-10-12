# Fixed-cohort encoding-unit sensitivity result

The locus-initial encoded-length contrast remains positive under all three
declared counting policies on the parent's exact 2,964-locus cohort. Its
numerical size changes: the grouped-policy contrasts range from **0.3903 to
0.4993**, compared with ASCII contrasts of **0.4380 to 0.4772**. This establishes
sensitivity of the count-based measure under these policies, with persistence
of its observed sign. It does not establish manuscript glyph length.

## Method and prospective record

The [measurement protocol](EVA_UNIT_PROTOCOL.md) and
[literal mapping settings](eva-unit-protocol.json) were committed in `52d68b1`
before these grouping outputs were computed. This follow-up was chosen after
seeing the [parent result](LOCUS_POSITION_RESULTS.md), so it is explicitly
post-result exploratory sensitivity. The parent cohort, source/spacing variants,
original token boundaries, case, and every conditional token-index draw are
unchanged. No new exclusions were introduced.

The mappings use exact literal substrings, left-to-right longest-match
precedence, and single-letter fallback. The emitted segment strings concatenate
to the original encoded token. Counting segments loses information by itself;
the original token inputs and complete mapping remain pinned. This is not a
complete conversion to a historical alphabet.

The alphabet creator's [reference](https://voynich.nu/hist/gabriel/eva2_reference.pdf),
pages 4 and 6–7, motivates the selected connected sequences and minim clusters.
Its internal update is July 2004. Its older annotation conventions are not used
for current IVTFF parsing. The protocol records its URL, exact PDF digest,
literal spellings, source scope, and unlisted connected examples.

## Observed contrasts

Each entry is the equal-locus mean of initial-token count minus the mean
remaining-token count, measured in the column's declared units. These are
numerical comparisons across operational count definitions, not physical
length differences in one common glyph unit.

| Source / spacing | ASCII letters | Bench segments | Bench and minim segments |
| --- | ---: | ---: | ---: |
| IT2a / split | +0.4380 | +0.4740 | +0.3903 |
| IT2a / join | +0.4380 | +0.4740 | +0.3903 |
| ZL3b / split | +0.4421 | +0.4793 | +0.3961 |
| ZL3b / join | +0.4772 | +0.4993 | +0.4046 |

All twelve observed contrasts exceed their positive conditional reference
limits, which range from roughly +0.0543 to +0.0715. The reference fixes token
multisets and chooses a token uniformly for first position within each locus.
It is not a language or text-production model, and these exploratory interval
comparisons are not confirmatory hypothesis tests.

## Paired numerical changes from ASCII

The same token index is chosen under each counting policy in every replicate.
Thus the difference distribution is paired; it is not constructed by subtracting
independent null draws.

| Source / spacing | Bench change | Its paired null range | Bench/minim change | Its paired null range |
| --- | ---: | --- | ---: | --- |
| IT2a / split | +0.0360 | −0.0278 to +0.0275 | −0.0477 | −0.0317 to +0.0339 |
| IT2a / join | +0.0360 | −0.0276 to +0.0270 | −0.0477 | −0.0339 to +0.0332 |
| ZL3b / split | +0.0372 | −0.0280 to +0.0283 | −0.0460 | −0.0323 to +0.0329 |
| ZL3b / join | +0.0221 | −0.0284 to +0.0290 | −0.0726 | −0.0341 to +0.0348 |

The ZL join-mode bench change lies **inside** its paired reference range. The
other reported changes exceed their corresponding reference bounds. Preserve
that exception; do not summarize all changes as equally separated from the
reference. None of these comparisons selects a preferred or correct unit map.

## Record and verification

[eva-unit-results.json](eva-unit-results.json) contains all twelve policy outputs,
all paired differences, 2,000 draws per output, exact conditional standard
deviations, original token counts, emitted segment counts, pattern hits,
uppercase fallbacks, unlisted-example occurrence counts, and parent/input/
mapping/implementation fingerprints. Raw draws and statistics are rounded to
twelve decimals for publication; paired differences are calculated before
that rounding, so subtraction of published rounded values can differ at the
last decimal.

The ASCII control reproduces the parent exactly, including all null draws.
Every original token is retained under every policy. All twelve observed means
were independently checked with exact rational arithmetic. Nine focused
synthetic tests cover literal case, longest-match precedence, unchanged token
boundaries, lossless segment reconstruction, fallback scope, paired finite
nulls, and exact parent-control reproduction.

From the repository root:

```sh
python3 scripts/eva_token_adapter.py --uncertain-spaces split --output /tmp/voynich-unit-split.json
python3 scripts/eva_token_adapter.py --uncertain-spaces join --output /tmp/voynich-unit-join.json
python3 scripts/eva_unit_sensitivity.py \
  --split /tmp/voynich-unit-split.json \
  --join /tmp/voynich-unit-join.json \
  --check research/baselines/eva-unit-results.json
python3 -m unittest discover -s tests -p 'test_eva_unit_sensitivity.py' -v
```

The checker pins the parent result, parent implementation, source token packets,
cohort, and measurement settings. Changed inputs require review rather than
silent corpus replacement. The complete cohort and exclusion ledger remain
in the parent result, avoiding a second, drifting selection definition.

## Limits and next test

The selected groupings do not exhaust connected or capitalized forms and do
not adjudicate manuscript glyphs. Single-letter fallbacks and partial matches
inside unlisted forms are explicit. The cohort remains biased toward the
parent's conservative, readable records and has known whole-corpus exposure.
No untouched evaluation set or independent source replication is claimed.

The result supports keeping unit definitions explicit when a future mechanism
is evaluated against encoded-length patterns. Independent image-based
paleographic review and additional predeclared representations are needed
before connecting this numerical effect to manuscript glyph length, language,
or plaintext. All three policies are retained without choosing a winner from
their results.
