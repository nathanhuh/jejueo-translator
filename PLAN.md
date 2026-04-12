# MVP Plan

## Goal

Ship a translation-only MVP for:

- `ko -> ko-jeju`
- `ko-jeju -> ko`

## Current State

- API contract is frozen.
- Shared contract code exists in `packages/shared`.
- Fixed eval set exists.
- Provisional launch quant is `Q4_K_M`.
- Local `Q4_K_M` smoke testing works through `llama-completion` CPU fallback.
- Inference service now includes runtime entrypoints for ASGI, FastAPI, and Modal, with env-based model-volume path resolution.
- Edge and inference now share a forwarded `requestId` and emit structured logs without raw text by default.
- `apps/web` now exists with a tested Cloudflare Pages Function proxy for `POST /api/translate` and a richer static UI shell.
- The static `apps/web` shell is the intended MVP frontend for now; React/TypeScript is explicitly deferred until after stable deployment.
- Targeted validation tests exist for the shared contract and inference routes.

## Remaining Work

- [ ] Land the MVP monorepo implementation as the canonical tracked repo state
- [ ] Verify the inference runtime with installed `llama-cpp-python` / FastAPI / Modal dependencies and a real GGUF service run
- [ ] Add reproducible local setup and CI for the Python and web verification paths
- [ ] Finish abuse protection: live Turnstile verification + Cloudflare rate limiting
- [ ] Produce benchmark and latency evidence for the chosen beta build
- [ ] Close licensing and attribution path
- [ ] Prepare launch docs and portfolio polish

## Order

1. Core MVP scaffolding
2. Tests and validation
3. Deployment wiring
4. Launch docs and protections
5. Post-MVP `Q5_K_M` comparison if warranted

## Working Rule

- Core logic stays in the normal plan.
- Work in hands-off mode by default.
- Only require user intervention when a real product, architecture, or external-environment decision is needed.
