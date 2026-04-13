# Implementation Plan

## Product Scope

Build a public, translation-only web app for:

- `ko -> ko-jeju`
- `ko-jeju -> ko`

Non-goals for v1:

- no chat mode
- no QA mode
- no user accounts
- no document upload
- no batch translation
- no browser-direct calls to model infrastructure

## Final Architecture Decision

- Model: `est-ai/alan-llm-jeju-dialect-v1-4b`
- Launch quantization: existing GGUF `Q4_K_M` as the provisional MVP default
- Inference engine target: `llama-cpp-python` on `llama.cpp`
- Backend hosting: Modal
- Frontend + edge API proxy: Cloudflare Pages + Pages Functions
- Abuse protection: Cloudflare Turnstile + Cloudflare Rate Limiting

Current local validation note:

- The verified local smoke-test path uses `llama-completion` with `--device none`.
- `llama-cpp-python` is still the intended service-side integration target.

## Current Implementation Snapshot

- Phase 0 is effectively complete except for launch-side legal and observability follow-through.
- Phase 1 deliverables exist in `packages/eval`.
- `packages/shared` now implements the frozen contract and validation layer.
- `services/inference` now implements tested ASGI/FastAPI/Modal runtime scaffolding with shared request IDs, structured logs, upstream auth checks, `/health`, and `/translate`.
- `apps/web` now implements a tested Pages Function proxy scaffold and a richer static UI shell.
- The static shell is the intended MVP frontend for now; any React/TypeScript rewrite is deferred until after stable deployment.
- Remaining deployment work is dependency-backed runtime verification, Cloudflare rate limiting, and optional Turnstile widget wiring.

## Success Criteria

- Warm translation latency: `p50 < 2.5s` for short inputs
- Warm translation latency: `p95 < 5s`
- Cold-start experience: first response under `10s`
- Output compliance: translation-only on the evaluation set
- Quant choice made through repeatable evaluation, not intuition
- Public demo has no unprotected direct model endpoint
- Normal portfolio traffic fits free-tier budgets

## Monorepo Layout

```text
jeju-translator/
  apps/
    web/
  services/
    inference/
  packages/
    eval/
    shared/
  docs/
```

## Phase 0: Define the Contract

Deliverables:

- product brief
- translation API schema
- prompt contract
- evaluation rubric

Tasks:

- Lock supported directions to exactly `ko -> ko-jeju` and `ko-jeju -> ko`.
- Freeze one response shape for the client.
- Decide now that the backend returns translation text only.
- Set a hard input cap for v1 instead of building chunking.

Acceptance criteria:

- API schema frozen in `packages/shared`
- one prompt template committed
- one error taxonomy documented

## Phase 1: Local Validation and Quant Posture

Deliverables:

- local benchmark script or lightweight local test workflow
- prompt template
- evaluation set
- provisional quant note

Tasks:

- Start MVP with `Q4_K_M` as the provisional default quant.
- Start from the model-card decoding baseline: `temperature=0.4`, `repetition_penalty=1.1`, optional `top_p=0.9`.
- Build the fixed evaluation set covering both directions, proper nouns, line breaks, honorifics, and ambiguous dialect phrasing.
- Verify that `Q4_K_M` is usable for the MVP path on the local machine.
- Use the working local path first, even if that means `llama-completion` CPU fallback during initial smoke testing.
- Defer full `Q4_K_M` vs `Q5_K_M` comparison until after MVP if translation quality concerns appear or time permits.

Acceptance criteria:

- `Q4_K_M` is recorded as the provisional launch quant in docs
- local test workflow for the chosen quant is documented
- prompt template fixed
- v1 input cap set
- one verified local smoke-test path exists for `Q4_K_M`

Decision rule:

- Launch on `Q4_K_M` to minimize MVP scope and preserve latency headroom.
- Promote `Q5_K_M` later only if the fixed evaluation workflow shows materially better meaning preservation or dialect quality.

## Phase 2: Inference Service on Modal

Deliverables:

- deployed Modal app
- `/health`
- `/translate`
- model stored in a Modal Volume
- cold-start mitigation enabled

Tasks:

- Build a thin Python translation service.
- Load the GGUF via `llama-cpp-python` for the service runtime.
- Keep the API translation-specific; do not expose generic chat completions.
- Use a secret header so only the edge proxy can call the service.
- Add Memory Snapshots after the service is stable.

Current status:

- The thin service layer and auth boundary are implemented locally.
- The remaining work is deployable runtime integration rather than first-pass endpoint design.

Acceptance criteria:

- backend handles `20` sequential requests without restart
- `/health` reports model-ready state
- authenticated proxy requests succeed
- unauthenticated direct requests fail
- basic latency benchmark recorded

## Phase 3: Edge Proxy and Frontend

Deliverables:

- public frontend
- secure `/api/translate`
- Turnstile integration
- rate limiting
- polished translation UX

Tasks:

- Build a minimal static frontend shell for MVP on Cloudflare Pages.
- Pages Function validates the request, verifies Turnstile, applies rate limiting, forwards to Modal, and normalizes the response.
- Ship source/target toggle, copy output, clear input, example phrases, line-break preservation, and clear `429`/`503` states.
- Keep dev-only latency surfacing out of the public production UI.

Acceptance criteria:

- browser never talks to Modal directly
- Turnstile is required for public use
- rate limiting returns `429`
- static assets remain CDN-fast
- app works on desktop and mobile

## Phase 4: Observability and Quality Gates

Deliverables:

- logging dashboard
- request metrics
- evaluation runbook
- release checklist

Tasks:

- Use Cloudflare logs and metrics for request counts, errors, and duration.
- Track Modal-side timings separately.
- Add regression coverage for known examples, formatting preservation, empty input, long-input rejection, and upstream timeout.
- Re-run evaluation on every prompt or model change.

Acceptance criteria:

- every production error includes a request ID
- metrics are visible in one place
- release is blocked on material evaluation regressions

## Phase 5: Launch and Portfolio Polish

Deliverables:

- public URL
- README
- architecture diagram
- benchmark write-up
- resume bullets

Tasks:

- Launch on the platform-provided domain first.
- Publish `architecture.md`, `benchmarks.md`, and `evaluation.md`.
- Add one screenshot and one short demo clip.
- Put hard numbers in the README: chosen quant, warm `p50/p95`, cold-start result, evaluation set size, and protection layers.

## Phase 6: Post-Launch Improvements

Do only after v1 is live:

- run a formal `Q4_K_M` vs `Q5_K_M` comparison on the fixed evaluation set
- reproduce quantization locally
- benchmark prompt variants
- add thumbs up/down feedback
- add proper-noun preservation mode
- optionally move to a Next.js shell later if resume positioning benefits from it

## Recommended Build Order

1. API contract + eval set
2. Validate local MVP path on `Q4_K_M`
3. Modal inference service
4. Cloudflare edge proxy
5. Frontend UI
6. Observability
7. Launch docs
8. Only then `Q5_K_M` comparison, custom quantization, and extra polish
