# Jejueo Translator Planning Docs

This folder contains planning artifacts and status documents for building a public Jejueo translator focused on Korean <-> Jejueo text translation.

Current operating posture: ship a narrow, production-style portfolio demo first, then optimize.

## Documents

- `architecture.md`: Cloudflare Pages + Modal architecture, request flow, and security boundaries.
- `implementation-plan.md`: Phase-by-phase delivery plan for the translation-only v1.
- `evaluation-plan.md`: Local `Q4_K_M` validation and later quant-comparison plan.
- `open-questions.md`: Remaining decisions that still matter before or during implementation.
- `mvp-decision-record.md`: Current source of truth for scope, hosting, and quality priorities.
- `phase-0-checklist.md`: Phase 0 tasks for freezing contracts, prompts, and eval rules.
- `risk-register.md`: Main delivery, quality, and abuse risks for v1.
- `data-licensing.md`: Model/data/license checklist for a public portfolio deployment.
- `api-spec.md`: Stable `POST /api/translate` contract.
- `implementation-checklist.md`: Build tracker aligned to the new monorepo and hosting layout.
- `manual-test-matrix.md`: Expected API/UI behavior for smoke testing and release review.

## Scope

- v1 is translation-only: `ko -> ko-jeju` and `ko-jeju -> ko`.
- Non-goals for v1: chat, QA, retrieval augmentation, user accounts, document upload, and browser-direct access to model infrastructure.

## Current Notes

- `Q4_K_M` is the provisional MVP quant.
- The verified local evaluation path currently uses `llama-completion` with `--device none`.
- `llama-cpp-python` remains the intended service-side runtime target, but it is not the only documented local validation path.
- `packages/shared` now contains the shared API contract and validation helpers.
- `services/inference` now contains tested ASGI/FastAPI/Modal entry scaffolding, env-based model-volume path resolution, and structured request logging with forwarded request IDs.
- `apps/web` now contains a tested Pages Function proxy scaffold and a richer static UI shell for manual checks.
- `apps/web` is now the single intended frontend surface for beta; older root/mock frontend artifacts have been removed.
- The repo now includes a root Python dev dependency file plus CI for the shared/inference Python tests and the web test path.
- The static shell is the intended MVP frontend for now; any React/TypeScript rewrite is deferred until after stable deployment.
- Remaining deployment-specific work is live dependency verification, Cloudflare rate limiting, and optional Turnstile widget wiring.
