# Jejueo Translator

Translation-only MVP for:

- `ko -> ko-jeju`
- `ko-jeju -> ko`

The current MVP stack is:

- frontend and edge proxy: Cloudflare Pages + Pages Functions
- inference backend: Modal
- inference runtime target: `llama-cpp-python` on `llama.cpp`
- provisional launch quant: `Q4_K_M`

## Current Status

- Real MVP implementation now exists locally in `apps/web`, `services/inference`, `packages/shared`, and `packages/eval`.
- The web layer is the most verified path today: the Pages Function proxy and config endpoint tests pass locally.
- The Python paths are implemented and source-reviewed, but full local verification still depends on installing the repo's Python test/runtime dependencies.
- `services/inference` has ASGI, FastAPI, and Modal entry scaffolding with structured request logging and forwarded request IDs.
- `services/inference` includes `.env.example` plus a deploy smoke-check script for the live Modal endpoint.
- `apps/web` has a tested Pages Function proxy, a static HTML/CSS/JS shell for MVP, and checked-in Pages config plus Turnstile client wiring.
- `apps/web` is now the only intended frontend surface for beta; the older root/mock frontend artifacts were removed.
- React/TypeScript is intentionally deferred until after the deployed MVP is stable.

## Readiness Snapshot

What works:

- shared request/response contract and validation
- fixed translation-only API shape for `ko <-> ko-jeju`
- static MVP translator UI
- Cloudflare Pages Function proxy with request validation and upstream normalization
- request ID forwarding and structured edge/inference logging
- eval-set builder plus local eval runner scaffolding

What is still missing before a beta deployment:

- commit and land the MVP monorepo implementation as the canonical repo state
- install and verify the Python test/runtime dependencies locally and in CI
- prove real Modal inference with the GGUF model, Volume mount, and auth boundary
- deploy Cloudflare Pages with real bindings, Turnstile, and rate limiting
- produce real benchmark and latency evidence for the chosen launch build
- close licensing, attribution, and launch-posture signoff

## Repo Layout

```text
apps/web                 Static MVP shell + Cloudflare Pages Function proxy
services/inference       Translation-specific inference service
packages/shared          Shared request/response models and validation
packages/eval            Local eval tooling and fixed eval set
docs                     Planning, architecture, evaluation, and test docs
```

## Local Verification

Python tests:

```bash
PYTHONPATH='packages/shared/src:services/inference/src' pytest packages/shared/tests services/inference/tests
```

Web tests:

```bash
cd apps/web
node --test tests/translate.test.js
```

Deployment prep:

```bash
cp apps/web/.dev.vars.example apps/web/.dev.vars
cp services/inference/.env.example services/inference/.env
```

## Key Docs

- [Architecture](docs/architecture.md)
- [Implementation Plan](docs/implementation-plan.md)
- [API Spec](docs/api-spec.md)
- [Evaluation Plan](docs/evaluation-plan.md)
- [Manual Test Matrix](docs/manual-test-matrix.md)
- [Deploy Guide](DEPLOY.md)

## Notes

- The currently verified local eval path uses `llama-completion --device none`.
- Deployment-specific latency numbers are still pending live Modal/Cloudflare verification.
- The checked-in docs describe the intended MVP architecture accurately, but the project is not beta-ready until the deployment, CI, evaluation, and licensing blockers above are closed.
- Raw training corpora should stay out of the public repo.
