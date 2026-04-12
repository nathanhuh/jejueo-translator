# Architecture Plan

## Goal

Build a public web app for Korean <-> Jejueo translation with low-latency inference, repeatable evaluation, and basic abuse controls.

## Stack

- Model: `est-ai/alan-llm-jeju-dialect-v1-4b`
- Quant for launch: provisional `Q4_K_M`
- Inference runtime target: `llama-cpp-python` on `llama.cpp`
- Inference hosting: Modal
- Web frontend: Cloudflare Pages
- Edge API: Cloudflare Pages Functions
- Abuse controls: Cloudflare Turnstile + Cloudflare Rate Limiting

## Local Validation Note

- The currently verified local evaluation path uses `llama-completion` with `--device none`.
- Metal-backed local offload was not the verified smoke-test path on this machine.

## Current Implementation Status

- `packages/shared` exists and provides the shared contract, prompt builder, and validation helpers.
- `services/inference` now provides tested ASGI/FastAPI/Modal entry scaffolding for `/health` and `/translate`.
- The inference service now resolves its model path from either `MODEL_PATH` or a Modal Volume mount + filename.
- Edge and inference now share a forwarded request ID and emit structured logs without raw text by default.
- `apps/web` now provides a tested Cloudflare Pages Function proxy and a richer static UI shell.
- The static shell is the intended MVP frontend for now; any React/TypeScript rewrite is deferred until after stable deployment.
- Remaining platform work is live dependency verification, Cloudflare rate limiting, and optional Turnstile widget wiring.

## Design Principles

- Keep v1 translation-only.
- Do not expose the model service directly to browsers.
- Treat the edge proxy as the security and normalization boundary.
- Keep the inference service narrow: translation endpoints only.
- Prefer measurable latency and eval discipline over feature breadth.

## High-Level Components

1. `apps/web`
- Static HTML/CSS/JS shell for MVP on Cloudflare Pages.
- Source/target toggle, input/output panes, examples, copy, clear, and error states.
- React/TypeScript is explicitly deferred until after the deployed MVP proves stable.

2. `Pages Function /api/translate`
- Validates request body.
- Verifies Turnstile.
- Applies rate limiting.
- Forwards to Modal with a secret header.
- Normalizes JSON responses and error taxonomy.

3. `services/inference`
- Thin Python service on Modal.
- Loads the chosen GGUF from a Modal Volume.
- Exposes `/health` and `/translate`.
- Current repo status: the service layer, FastAPI/Modal entry scaffolding, and structured logging are implemented locally; live dependency verification is still pending.

4. `packages/eval`
- Offline evaluation harness.
- Local `Q4_K_M` validation now; formal later quant comparison if warranted.

## Request Flow

1. Browser submits `POST /api/translate` to Cloudflare.
2. Pages Function validates input and supported direction.
3. Pages Function verifies Turnstile and rate-limit policy.
4. Pages Function forwards the request to Modal using server-side credentials.
5. Modal runs translation inference and returns normalized JSON.
6. Pages Function returns the translation to the browser.

## Security Boundary

- The browser never calls Modal directly.
- CORS may still be restricted, but it is not treated as authentication.
- Modal accepts only secret-authenticated requests from the edge layer.
- Unsupported language pairs and oversized inputs are rejected before inference.

## Deployment Shape

- 1 Cloudflare Pages project for static assets and edge API
- 1 Modal app for translation inference
- 1 Modal Volume for model weights
- Optional Memory Snapshot after service stabilization

## API Contract Summary

See [`api-spec.md`](docs/api-spec.md) for the stable request/response contract.

## Non-Goals for v1

- chat or QA workflows
- retrieval augmentation
- browser-direct inference
- document or batch translation
- custom quantization before launch
