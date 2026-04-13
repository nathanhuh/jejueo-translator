# MVP Decision Record

## Purpose

This document is the source of truth for finalized MVP decisions for the Jejueo translator.

## Status

- Version: `v10`
- Date: `2026-03-22`
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
- Decision: work in hands-off mode by default.
- Decision: assistant implements directly unless the user needs to make a real product, architecture, or environment decision.
- Decision: user intervention is reserved for meaningful decisions and external actions.
- Rationale: keep the project collaborative and educational without blocking implementation momentum.

## Impact on Current Plans

- Architecture: Cloudflare is the public edge; Modal is the inference backend.
- Implementation: benchmark existing quants before building outward-facing features.
- Evaluation: release gates emphasize translation-only output, meaning preservation, and latency.
- Launch mode: portfolio demo with controlled distribution of artifacts.
- Workflow: hands-off implementation is now allowed, with user involvement focused on real decisions and external setup.

## Linked Planning Artifacts

- `docs/architecture.md`
- `docs/implementation-plan.md`
- `docs/evaluation-plan.md`
- `docs/open-questions.md`

## Change Control

- Any change to these MVP decisions should be appended in this file under a new version section (`v2`, `v3`, ...).

## Version `v5`

- Date: `2026-03-16`

### Change

3. Quantization strategy
- Decision: launch on existing GGUF `Q4_K_M` as the provisional MVP quant.
- Decision: defer formal `Q4_K_M` vs `Q5_K_M` comparison until after MVP unless a quality blocker appears earlier.
- Decision: allow promotion to `Q5_K_M` later only if the fixed evaluation workflow shows materially better translation quality.

### Rationale

- Prioritizes MVP speed and a working public demo over pre-launch optimization.
- Keeps the launch quant decision reversible without reopening product scope.
- Preserves the evaluation framework so a later quant switch can still be evidence-based.

### Impact

- Implementation can proceed with `Q4_K_M` as the default runtime target.
- Quant benchmarking is downgraded from a pre-MVP gate to a post-MVP validation task.
- Portfolio evidence is still possible later, but no longer blocks the first release.

## Version `v8`

- Date: `2026-03-19`

### Change

2. Model hosting and local validation posture
- Decision: keep `llama-cpp-python` / `llama.cpp` as the intended service-side runtime target.
- Decision: treat `llama-completion` with `--device none` as the currently verified local smoke-test path for `Q4_K_M`.

### Rationale

- The service runtime target and the currently working local validation path are not the same thing.
- Separating those two ideas keeps the docs accurate without blocking implementation momentum on Metal issues.

### Impact

- Local validation can proceed immediately on the CLI fallback path.
- Service implementation can still target `llama-cpp-python`.
- Docs should not imply that Metal-backed Python inference is already the verified local path.

## Version `v6`

- Date: `2026-03-19`

### Change

10. Collaboration mode for learning
- Decision: the user will implement the core application logic by default.
- Decision: assistant work should bias toward testing, evaluation tooling, review, documentation, and other non-core support work unless explicitly asked to implement core logic.

### Rationale

- Strengthens the learning goal by keeping product-critical logic in the user's hands.
- Preserves assistant usefulness by focusing on the surrounding work that still accelerates delivery.

### Impact

- Future plans and tickets should prefer assistant-owned testing and validation work.
- Core service and frontend logic should not be assumed to be assistant-owned implementation tasks.

## Version `v7`

- Date: `2026-03-19`

### Change

10. Collaboration mode for learning
- Decision: keep core MVP implementation tasks visible in plans and tickets normally.
- Decision: user ownership of core logic affects who implements the work by default, not whether that work appears in planning artifacts.

### Rationale

- Hiding core implementation tasks from plans makes the roadmap less accurate.
- The user still benefits from seeing the full queue even when they want to write the code personally.

### Impact

- Plans and tickets should continue to reflect the full MVP implementation path.
- Assistant execution should still respect the user’s ownership of core logic unless explicit coding permission is given.

## Version `v9`

- Date: `2026-03-22`

### Change

10. Collaboration mode for learning
- Decision: switch to hands-off mode as the active repo working style.
- Decision: assistant may implement core MVP work directly.
- Decision: user intervention should be required only for meaningful decisions or external actions.

### Rationale

- Removes process friction that was blocking implementation momentum.
- Keeps the user in the loop where judgment matters while allowing execution to move forward.

### Impact

- AGENTS and planning docs should no longer describe the repo as planning-only or code-blocked.
- Tickets and implementation docs should reflect actual shipped scaffolding work.

## Version `v10`

- Date: `2026-03-22`

### Change

4. Frontend posture for MVP
- Decision: keep the current static `apps/web` shell as the intended MVP frontend through initial deployment.
- Decision: defer any React + TypeScript rewrite until after the deployed MVP proves stable.

### Rationale

- The current frontend surface area is small and already covered by the working static shell.
- The main remaining MVP risks are deployment-side inference verification and abuse protection, not frontend framework limitations.
- Deferring a rewrite avoids adding build complexity before the riskiest deployment work is complete.

### Impact

- React + TypeScript is no longer a pre-deployment MVP requirement.
- The frontend blocker list should focus on Turnstile, rate limiting, deployment verification, and launch documentation.
- A richer framework-based frontend can be evaluated later for portfolio polish once the deployed MVP is stable.
