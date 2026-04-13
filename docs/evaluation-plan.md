# Evaluation Plan

## Objectives

- Verify that the provisional launch quant is acceptable and support later quant upgrades through repeatable evaluation.
- Catch translation regressions before release.
- Verify translation-only behavior, formatting preservation, and latency.

## Evaluation Structure

1. Quant benchmark
- Use the fixed evaluation workflow to validate the chosen launch quant.
- When a formal quant comparison is run later, use the same prompt, decoding baseline, hardware/runtime setup, and fixed evaluation set for both.

Current verified local execution path:

- `llama-completion` with `--device none`
- `Q4_K_M` GGUF
- fixed eval-set CSV derived from the Kakao Brain Jejueo corpus

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

Benchmark notes must record the exact decode settings used for each run.

## Evaluation Set Composition

Target size: `180` examples total.

Category mix:

- `60` everyday `ko -> ko-jeju`
- `60` everyday `ko-jeju -> ko`
- `20` proper noun preservation cases
- `15` line-break and formatting preservation cases
- `15` honorifics and politeness cases
- `10` ambiguous dialect phrasing cases

Set rules:

- Freeze the v1 evaluation set before quant benchmarking begins.
- Do not add or remove cases while comparing quants in any later formal benchmark.
- Keep a stable case ID for every example so benchmark results can be compared over time.
- Preserve the original direction label for every sample: `ko -> ko-jeju` or `ko-jeju -> ko`.
- Mark formatting-sensitive cases explicitly so line-break failures are visible during review.
- Store public-repo artifacts in a license-safe way if raw examples cannot be redistributed.

Suggested repo layout once implementation starts:

- `packages/eval/data/eval-set.csv` or equivalent metadata file
- `packages/eval/results/YYYY-MM-DD-<quant>.md` for benchmark summaries
- `docs/benchmarks.md` for the quant decision memo

Current repo note:

- A fixed eval set now exists in `packages/eval/data/eval-set.csv`.
- Before beta signoff, audit the checked-in set against the target category mix
  above and publish one real reviewed benchmark run with latency notes.

## Scoring Rubric

Score every reviewed example on the dimensions below.

### Meaning Preservation

- `Pass`: core meaning is preserved with no material omission or distortion.
- `Fail`: wrong meaning, major omission, or materially misleading wording.

### Dialect Naturalness

- `Pass`: output reads as natural target-language phrasing for the task.
- `Borderline`: understandable but awkward, overly literal, or weak in register.
- `Fail`: unnatural enough to reduce usefulness or suggest the wrong variety/register.

### Formatting Preservation

- `Pass`: line breaks, list structure, and punctuation-sensitive layout are preserved where expected.
- `Fail`: line breaks collapse, ordering changes, or formatting cues are lost.

### Translation-Only Compliance

- `Pass`: output contains translation text only.
- `Fail`: output adds explanation, notes, labels, or meta commentary.

### Hallucination Detection

- `Pass`: no added content beyond what is needed for translation.
- `Fail`: output introduces unsupported information, invented details, or gratuitous additions.

## Failure Taxonomy

Use one primary label per failed sample:

- `wrong_meaning`
- `omission`
- `hallucination`
- `formatting_loss`
- `register_mismatch`
- `unnecessary_paraphrase`
- `non_translation_output`

## Release Gates

- `100%` translation-only compliance on the fixed v1 test set
- `0` tolerated failures for `wrong_meaning`, `hallucination`, or `non_translation_output` in the release review sample
- No more than `3%` failures for `formatting_loss` across the reviewed sample
- No more than `5%` borderline-or-fail results for dialect naturalness across the reviewed sample
- No material regression in meaning preservation or format preservation versus the previous accepted build
- Warm latency remains within the published SLO targets

## Quant Selection Rule

- MVP default: use `Q4_K_M` as the provisional launch quant.
- Post-MVP promotion rule: switch to `Q5_K_M` only if it shows materially better dialect quality or meaning preservation on the fixed evaluation workflow.

For later quant comparison, treat "materially better" as:

- no increase in `wrong_meaning`, `hallucination`, or `non_translation_output`
- a noticeable improvement in meaning preservation or dialect naturalness
- no meaningful deterioration in formatting preservation or latency posture

## Human Review Workflow

Reviewer model for v1:

- Primary reviewer: Nathan
- Optional secondary reviewer: trusted fluent speaker or domain advisor if available

Review minimums:

- For MVP launch on `Q4_K_M`: manually review enough of the fixed set to validate the prompt and output behavior, with full-set review preferred when feasible
- For later formal `Q4_K_M` vs `Q5_K_M` comparison: review all `180` fixed evaluation examples for both quants
- For prompt-only revisions after quant is chosen: rerun the full fixed set, with manual review of at least `60` samples covering both directions and all special categories
- Before public launch: manually review the full fixed set on the chosen prompt + quant combination

Review process:

1. Run the chosen quant with the same prompt and decode settings across the fixed set.
2. Score each sampled output for meaning preservation, dialect naturalness, formatting preservation, translation-only compliance, and hallucination.
3. Record one primary failure taxonomy label for every failed case.
4. Record latency summary separately from quality notes.
5. Block release or quant promotion if any release-gate threshold is missed.

Review artifact:

- Maintain one benchmark review sheet per run with case ID, direction, model/quant, pass/fail decisions, failure label, and reviewer notes.
- Keep raw generated artifacts out of git unless they are intentionally curated for documentation.

## Production Monitoring Inputs

- request count
- success/error rate
- edge latency
- Modal inference latency
- cold-start incidence

## Evaluation Cadence

- On every prompt or model revision: rerun the fixed regression set
- Before any later quant switch: run the full benchmark corpus on both candidate quants
- Before launch: publish chosen quant, eval set size, and latency numbers in docs

## Current Decisions Locked By This Document

- v1 benchmark comparisons use a fixed `180`-example evaluation set
- Nathan is the required primary reviewer for benchmark signoff
- `Q4_K_M` is the provisional launch quant
- Any later quant switch should be justified by the same fixed evaluation workflow
- `wrong_meaning`, `hallucination`, and `non_translation_output` are hard blockers for release
