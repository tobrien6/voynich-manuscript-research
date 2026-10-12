# Exact common paragraph token corpus plan

## Question and prior exposure

Which exact common encoded paragraph units from the accepted membership audit
can be processed without dropping any member locus under the conservative
native-Eva adapter in both sources and both comma policies?

Commit these choices before computing corpus eligibility or token totals.
The source corpus, paragraph annotations, and image pilots are already exposed.
This is a processing interface and coverage audit, not a new untouched test,
candidate fit, source correction, or decipherment.

## Fixed construction

- Verify the accepted `paragraph_membership.json` by complete recomputation
  from the pinned ZL3b/IT2a sources before constructing candidate units.
  Record its exact bytes, source identities, and implementation fingerprints.
- Use every exact ordered member-key match in that report as a candidate
  paragraph. Preserve both original source-unit IDs and the complete ordered
  membership. Do not include unmatched groups or choose a source convention.
- Reuse the accepted native-Eva adapter. Explicitly select all generic P
  subtypes present in the paired sources; do not inherit the adapter's narrower
  P0/P1 defaults. Preserve native case, source identifiers, inherited variables,
  locators, drawing-interruption handling, and both split/join comma policies.
- A source/policy variant is locally eligible only when every member locus is
  adapter-eligible. A candidate belongs to the common corpus only when all four
  variants are locally eligible. Introduce no minimum token/row count or
  further locator, readability, paragraph-length, or section filter.
- Retain every candidate, with per-source/policy exclusions and original
  member-locus metadata. If any variant excludes any member, emit no token
  payload for that candidate in any variant. Do not concatenate surviving
  fragments, infer a token across locus boundaries, or expose a partial unit
  as an eligible paragraph.
- For common eligible candidates, preserve a separate native token list per
  locus in source order. Keep original row boundaries and locators; do not
  flatten them into a purported physical-line or manuscript-paragraph stream.
- Record the entire candidate/common/excluded ledger, all denominators,
  per-variant native token totals, canonical corpus fingerprints, and input
  pins. The committed coverage report omits native token payloads; the full
  corpus can be generated locally from the same producer.
- Cache verification must compare complete canonical content with fresh
  producer output, including types, tokens, row coverage, identities, and
  exclusions. Reject duplicate JSON members and non-JSON numeric constants.
  Output paths must not overwrite source inputs, implementation, either plan,
  or the parent membership report, including resolved or hardlink aliases.

## Limits and next step

These are source-defined units and encoded token strings, not verified physical
paragraphs, glyph counts, decoded words, or independently sampled observations.
Whole-unit exclusions can bias the retained corpus. Matching membership does
not establish identical text, tokenization, image alignment, or source accuracy.
Foldout/leaf dependencies and exposure must be resolved by a later experiment's
own declared grouping and split. No statistic, null model, or candidate score
is chosen here.

Use the verified `tobrien6` owner/maintainer contribution scope and isolated
checkout. Work starts from accepted main and uses a focused topic PR; the
established maintainer workflow handles acceptance. Preserve the accepted
adapter, membership producer, and their existing provenance records.
