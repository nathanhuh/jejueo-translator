# Open Questions and Decisions

This document tracks the few remaining decisions that still matter after the v1 architecture reset.

## Current Implementation Status

- `packages/shared` now exists and matches the frozen public API contract.
- `services/inference` now has tested ASGI/FastAPI/Modal scaffolding, request tracing, and structured logs for `/health` and `/translate`.
- `apps/web` now exists with a tested Pages Function proxy and a static MVP shell, and it is now the sole intended frontend surface for beta.
- The remaining gaps are repo landing/cleanup, deployment verification, Cloudflare protections, evaluation evidence, and launch-side licensing/attribution work.

## Decisions Already Locked

1. Product scope
- Decision: translation-only app for `ko -> ko-jeju` and `ko-jeju -> ko`.

2. Model and runtime
- Decision: `est-ai/alan-llm-jeju-dialect-v1-4b` via GGUF.
- Decision: target service runtime is `llama-cpp-python` / `llama.cpp`.
- Decision: verified local evaluation path currently uses `llama-completion` CPU fallback.

3. Hosting
- Decision: Cloudflare Pages + Pages Functions in front of Modal.

4. Abuse protection
- Decision: Turnstile + rate limiting + secret-authenticated upstream.

5. Output behavior
- Decision: translation-only responses, no explanations.

## Remaining Decisions

1. Demo posture for cold starts
- Decide when to accept scale-to-zero cold starts and when to temporarily use `min_containers=1`.

2. CI baseline for beta
- Decide the minimum required automated gate for beta:
  Python tests only when dependencies are present, or mandatory Python + Node verification on every change.

## Questions to Resolve Through Documentation, Not Guesswork

1. Model/data licensing details for the public demo
2. Exact attribution wording for README and app footer
3. Exact beta validation checklist and benchmark evidence to require before launch

## Recently Closed By Documentation

1. Human review process
- Decision: Nathan is the primary reviewer.
- Decision: quant selection and pre-launch signoff require review of the full fixed v1 evaluation set.

2. Benchmark corpus storage posture
- Decision: keep a fixed case-ID-based evaluation set and store public-repo artifacts in a license-safe way if raw examples cannot be redistributed.

3. Hard input cap
- Decision: v1 uses a hard cap of `500` Unicode characters.
- Decision: requests above that limit return `413`.

4. Canonical frontend path
- Decision: `apps/web` is the only intended frontend surface for beta.
- Decision: the older root/mock frontend artifacts have been removed from the repo.

5. Launch quant posture
- Decision: v1 launches on `Q4_K_M` as the provisional default quant.
- Decision: `Q5_K_M` can replace it later only if the fixed evaluation workflow shows materially better translation quality.
