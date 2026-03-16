# Evaluation Plan

## Objectives

- Choose the launch quant through repeatable benchmarking.
- Catch translation regressions before release.
- Verify translation-only behavior, formatting preservation, and latency.

## Evaluation Structure

1. Quant benchmark
- Compare existing GGUF `Q4_K_M` and `Q5_K_M`.
- Use the same prompt and decoding baseline for both.

2. Human-scored quality set
- Meaning preserved
- Dialect naturalness
- Format preserved
- No added explanation
- No hallucinated content

3. Regression checks
- Fixed examples for both directions
- Empty input handling
- Long-input rejection
- Timeout and upstream failure behavior

## Baseline Inference Settings

Start with the model-card defaults:

- `temperature=0.4`
- `repetition_penalty=1.1`
- optional `top_p=0.9`

Only tighten decoding if the eval set shows better translation-only compliance.

## Evaluation Set Composition

Target size: `150-250` examples split across:

- everyday Korean -> Jejueo
- Jejueo -> Korean
- proper nouns
- line breaks
- honorifics and politeness
- ambiguous dialect phrasing

## Release Gates

- `100%` translation-only compliance on the fixed v1 test set
- No critical failures for wrong meaning or hallucinated content in the reviewed sample
- No material regression in meaning preservation or format preservation versus the previous accepted build
- Warm latency remains within the published SLO targets

## Quant Selection Rule

- Choose `Q4_K_M` if quality is effectively tied and latency is materially better.
- Choose `Q5_K_M` if it shows noticeably better dialect quality or meaning preservation.

## Human Review Workflow

1. Score each sampled output for meaning preservation, dialect naturalness, and formatting.
2. Mark whether the output added explanation, notes, or hallucinated content.
3. Record failure categories:
- wrong meaning
- omission
- hallucination
- formatting loss
- register mismatch
- unnecessary paraphrase
4. Block release if a fixed-threshold regression is exceeded.

## Production Monitoring Inputs

- request count
- success/error rate
- edge latency
- Modal inference latency
- cold-start incidence

## Evaluation Cadence

- On every prompt or model revision: rerun the fixed regression set
- Before quant selection: run the full benchmark corpus on both quants
- Before launch: publish chosen quant, eval set size, and latency numbers in docs
