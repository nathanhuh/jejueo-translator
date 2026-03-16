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
- Launch quantization: existing GGUF, benchmark `Q4_K_M` vs `Q5_K_M`
- Inference engine: `llama-cpp-python` on `llama.cpp`
- Backend hosting: Modal
- Frontend + edge API proxy: Cloudflare Pages + Pages Functions
- Abuse protection: Cloudflare Turnstile + Cloudflare Rate Limiting

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

## Phase 1: Local Benchmarking and Quant Selection

Deliverables:

- local benchmark script
- prompt template
- evaluation set
- quant choice memo

Tasks:

- Benchmark existing GGUF `Q4_K_M` and `Q5_K_M`.
- Start from the model-card decoding baseline: `temperature=0.4`, `repetition_penalty=1.1`, optional `top_p=0.9`.
- Build a small gold set covering both directions, proper nouns, line breaks, honorifics, and ambiguous dialect phrasing.
- Score meaning preservation, dialect naturalness, format preservation, translation-only compliance, and hallucination rate.

Acceptance criteria:

- benchmark report checked into `docs/benchmarks.md`
- chosen default quant recorded with reasons
- prompt template fixed
- v1 input cap set

Decision rule:

- Choose `Q4_K_M` if quality is effectively tied and latency is materially better.
- Choose `Q5_K_M` if it is noticeably better on the eval set.

## Phase 2: Inference Service on Modal

Deliverables:

- deployed Modal app
- `/health`
- `/translate`
- model stored in a Modal Volume
- cold-start mitigation enabled

Tasks:

- Build a thin Python translation service.
- Load the GGUF via `llama-cpp-python`.
- Keep the API translation-specific; do not expose generic chat completions.
- Use a secret header so only the edge proxy can call the service.
- Add Memory Snapshots after the service is stable.

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

- Build a minimal React + TypeScript + Tailwind SPA.
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

- reproduce quantization locally
- benchmark prompt variants
- add thumbs up/down feedback
- add proper-noun preservation mode
- optionally move to a Next.js shell later if resume positioning benefits from it

## Recommended Build Order

1. API contract + eval set
2. Local benchmark `Q4_K_M` vs `Q5_K_M`
3. Modal inference service
4. Cloudflare edge proxy
5. Frontend UI
6. Observability
7. Launch docs
8. Only then custom quantization and extra polish
