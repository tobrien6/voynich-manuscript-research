# Conservative common-cohort prefix plan

Commit these choices before computing the comparison. The full corpus and
preceding prefix results have already been exposed. This is an exploratory
selection-policy sensitivity check, not an untouched mechanism test.

## Question

Do the paragraph/source-group q/y patterns persist when every selected locus is
eligible under the accepted `plain-eva-v1` whole-locus exclusion policy?
This examines prefix features only and does not duplicate a token-length test.

## Frozen selection rule

- Call `scripts.eva_token_adapter.build` explicitly for ZL3b and IT2a, P0 only,
  under both split and join uncertain spaces. Verify each returned adapter
  version, analysis unit, processing policy, and source provenance.
- Retain a locus key only if it is present and eligible with at least two tokens
  in **all four source/spacing combinations**, and has locator `@`, `+`, or `*`
  in every combination. Choose no filter after viewing a prefix result.
- Record the complete selected-key list and digest, exclusions by source/policy,
  and counts removed by each eligibility condition. Do not label the resulting
  unit a physical line or independently inspected image region.
- On this same fixed cohort, compute literal q/y first- and last-slot contrasts
  using the accepted equal-locus-weight conditional controls, seed 20261011 and
  199 shuffles. Preserve the raw source metadata.
- Partition within each source by effective `L` label, including unset, and the
  source paragraph-start marker. Report all cohorts and both boundaries,
  including undefined estimates; keep all four source/spacing combinations.
- Publish the entire machine-readable result and compare directions/effect sizes
  with the preceding partial-token exclusion analysis. The sources, policies,
  and related analyses are dependent and are not independent replications.

## Limits

Whole-locus exclusion may systematically select particular sections, writing
conventions, or text shapes. Eligibility does not establish transcription
correctness. These remain literal encoded-prefix tests with source annotations;
they do not identify glyphs, languages, plaintext, or a cipher.
