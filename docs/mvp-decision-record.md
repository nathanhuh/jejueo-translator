# MVP Decision Record

## Purpose

This document is the source of truth for finalized MVP decisions for the Jejueo translator.

## Status

- Version: `v4`
- Date: `2026-02-21`
- Scope: planning and execution alignment for MVP

## Finalized Product Decisions

1. Translation direction priority
- Decision: ship both `ko -> ko-jeju` and `ko-jeju -> ko` in v1.
- Rationale: the selected model is purpose-built for both directions and the stronger portfolio story is a focused bidirectional translator.

2. Model hosting strategy
- Decision: deploy `est-ai/alan-llm-jeju-dialect-v1-4b` as a GGUF-backed inference service on Modal.
- Rationale: keeps the product translation-specific, supports low-latency local inference, and still preserves a fast launch path through existing quants.

3. Quantization strategy
- Decision: launch with an existing GGUF after benchmarking `Q4_K_M` vs `Q5_K_M`.
- Decision: defer self-quantization until after v1 is live.
- Rationale: fastest route to a measurable launch with evidence-based quant selection.

4. Frontend and edge hosting
- Decision: use Cloudflare Pages + Pages Functions as the public frontend and API proxy.
- Decision: use Turnstile and Cloudflare rate limiting for abuse protection.
- Rationale: edge-side protection and request normalization are part of the product story, not an afterthought.

5. Performance targets
- Decision: warm `p50 < 2.5s` for short inputs.
- Decision: warm `p95 < 5s`.
- Decision: cold-start first response under `10s`.
- Rationale: practical responsiveness target for a public portfolio demo with scale-to-zero inference.

6. Output contract
- Decision: the backend returns translation text only.
- Decision: no explanations, notes, confidence scores, or evidence payloads in v1.
- Rationale: the app is a translator, not a chat experience.

7. Product scope constraints
- Decision: v1 excludes chat mode, QA mode, RAG, accounts, document upload, and browser-direct model access.
- Rationale: narrow scope improves launch speed and keeps the evaluation problem tractable.

8. Quality gate priority
- Decision: translation-only compliance is a hard requirement.
- Decision: wrong meaning and hallucinated content are release blockers.
- Decision: quant choice must be supported by a fixed evaluation set.
- Rationale: portfolio value comes from measurable product behavior, not feature count.

9. Portfolio launch posture
- Decision: launch as portfolio/research demo first, not production service.
- Decision: do not redistribute raw training corpora in public repository.
- Decision: keep legal-risk exposure low via explicit attribution and demo-only disclaimer.
- Rationale: maximize hiring signal while minimizing operational/legal overhead.

10. Collaboration mode for learning
- Decision: assistant does not create or modify implementation code unless explicitly authorized by user in that turn.
- Decision: assistant may continue planning/docs updates without additional approval.
- Decision: assistant must ask for explicit permission before any code-generation step.
- Rationale: preserve hands-on learning for the project owner.

## Impact on Current Plans

- Architecture: Cloudflare is the public edge; Modal is the inference backend.
- Implementation: benchmark existing quants before building outward-facing features.
- Evaluation: release gates emphasize translation-only output, meaning preservation, and latency.
- Launch mode: portfolio demo with controlled distribution of artifacts.
- Workflow: user is primary implementer; assistant acts as planner/reviewer unless explicitly told to code.

## Linked Planning Artifacts

- `docs/architecture.md`
- `docs/implementation-plan.md`
- `docs/evaluation-plan.md`
- `docs/open-questions.md`

## Change Control

- Any change to these MVP decisions should be appended in this file under a new version section (`v2`, `v3`, ...).
