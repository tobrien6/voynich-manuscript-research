# Decipherment and translation evaluation protocol

This protocol turns the project's goal of decoding and translating the Voynich manuscript into reviewable contributions. It defines a research method, not a claim that the text has been decoded.

## Keep the stages separate

- **Transcription:** represent visible manuscript glyphs in a documented notation. A transcription alphabet is not evidence of an underlying language or plaintext.
- **Decoding:** apply explicit rules to derive a proposed reading or representation. Explain segmentation, glyph combinations, abbreviations, context dependencies, and exceptions.
- **Translation:** render a supported reading into English. Distinguish a literal rendering from interpretation and identify the evidence for vocabulary and grammar.

Candidates that do not posit language can still be tested as explanations of text production. They do not yield a linguistic translation unless that additional claim is supported.

## Register a candidate before testing

Create a versioned record under `research/hypotheses/` when an actual candidate is ready. Include:

1. **Claim and scope:** the proposed mechanism, language if applicable, folios or sections covered, and what would refute it.
2. **Inputs:** source identifiers, folio and line references, image links, transcription edition and version, reuse terms, and normalization rules. Preserve original data and record ambiguous alternatives.
3. **Rules:** the complete mapping and procedure, including all context rules and exceptions. Provide code where practical or a worked procedure another researcher can follow without choosing readings by intuition.
4. **Development and evaluation sets:** commit the folio split before fitting rules. Explain sampling and prior exposure; reserve complete folios to reduce overlap from adjacent lines. Keep repeated passages or closely related material together where possible.
5. **Predictions and failure conditions:** state what the frozen candidate predicts on reserved material, how it will be scored, and what result would reject or limit the claim. Do not choose a threshold after seeing the outcome.
6. **Comparisons:** specify controls appropriate to the claim and explain why they are comparable. Record candidate complexity and the number of alternatives tried.

Commit the record before running the evaluation. If no objective prediction or check can yet be specified, label the candidate exploratory and describe the evidence needed to make it testable.

Use the [evaluation split record format](evaluation/SPLIT_FORMAT.md) to document
sampling units, related folios/panels, input identity, and prior exposure. The
offline checker catches inconsistent declarations and dependency leakage; a
passing result does not certify untouched material or replace review of the
actual pre-fit commit. Distinguish material excluded from fitting from a
stronger claim that it was previously unseen.

## Run and report the evaluation

Freeze the candidate rules and preprocessing. Apply them to the reserved folios without tuning to those folios. Report all evaluated passages, failures, excluded material, and the reasons for exclusions.

Depending on the claim, useful measurements may include glyph and token coverage, unresolved or ambiguous readings, exception counts, consistency of repeated forms, and accuracy of preregistered structural or linguistic predictions. Define each measurement and its denominator. Coverage measures how much a method processes; it does not by itself establish that the readings are correct.

Use several relevant controls where warranted: token shuffles for order claims, shuffles that preserve line structure for positional claims, documented language samples for linguistic claims, and synthetic encodings for proposed cipher mechanisms. Match preprocessing and sample sizes where possible; explain differences. Beating one weak control is not sufficient validation.

Repeat promising tests across documented transcription alternatives and, later, additional sections. Record whether conclusions change. If inspecting an evaluation set leads to new rules, that set becomes development material; version the candidate and reserve new material for the next test. Record all attempted candidates so selective reporting is visible.

## Publish a candidate passage

For every proposed translation, provide the following together:

| Field | Required content |
| --- | --- |
| Source | Source ID, stable image reference, folio, and line or region |
| Transcription | Edition and version, glyph notation, and ambiguous alternatives |
| Decoding | Candidate version and intermediate steps from glyphs to reading |
| Proposed reading | Underlying text or representation, with unresolved portions marked |
| Literal English | Translation tied to the proposed reading, retaining gaps |
| Interpretation | Optional contextual explanation, clearly separate from literal English |
| Evidence and uncertainty | Vocabulary and grammar sources, alternatives, contradictions, and basis for confidence |
| Evaluation status | Exploratory, tested with stated outcome, or independently reproduced |

Do not assign numerical confidence without a defined calibration method. Illustration matches can motivate predictions, but cannot supply missing words or substitute for testing the decoding rules.

## Independent review and progression

A reviewer should reproduce the procedure from the committed inputs and frozen rules, report disagreements, and distinguish reproduction of an output from evidence that the output is correct. For stronger validation, have an independent researcher evaluate the rules on additional material not used to build or revise them.

Publish partial results with their folio coverage and limitations. Expand a successful candidate progressively; the project's manuscript-wide goal remains open until its rules and translation have been tested across the surviving text. Preserve negative results and unresolved questions as part of the research record.
