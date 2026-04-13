# Implementation Checklist

Use this as your hands-on build tracker. Check each item only when the acceptance criteria is met.

## 1) Shared Contract

- [x] Create `packages/shared`
- [x] Freeze request/response schema for `POST /api/translate`
- [x] Document v1 error taxonomy

Acceptance criteria:

- Schema matches [`docs/api-spec.md`](/Users/nathanhuh/Documents/Documents - Nathan’s MacBook Pro/Personal_Repos/jejueo-translator/docs/api-spec.md)
- Success and error shapes are stable enough for parallel frontend/backend work

Current note:

- The shared package now contains request/response models, prompt construction, JSON parsing, and validation helpers for the frozen v1 contract.

## 2) Evaluation Harness

- [x] Create `packages/eval`
- [x] Add fixed evaluation set for both directions
- [x] Add local evaluation workflow for provisional `Q4_K_M`
- [x] Record later `Q5_K_M` promotion criteria

Acceptance criteria:

- Local evaluation output records latency and quality notes for the chosen launch quant
- Evaluation set covers formatting, proper nouns, and ambiguous phrasing

Current note:

- `llama-cpp-python` is installed, but the verified local path currently uses `llama-completion` with `--device none` because Metal backend initialization failed during smoke testing.
- The eval builder and runner exist, but checked-in benchmark evidence for beta signoff is still incomplete.
- Before launch, reconcile the actual eval-set category mix and publish one real reviewed benchmark run with latency notes.

## 3) Inference Service (`services/inference`)

- [x] Create service scaffold
- [x] Add `GET /health`
- [x] Add `POST /translate`
- [x] Enforce secret-authenticated upstream access
- [x] Add FastAPI / Modal runtime entrypoints
- [ ] Load chosen GGUF with `llama-cpp-python` in a verified service run
- [ ] Mount model weights from a Modal Volume

Acceptance criteria:

- `/health` returns model-ready state
- Authenticated requests succeed
- Direct unauthenticated requests fail

Current note:

- The repo now has tested ASGI, FastAPI, and Modal entry scaffolding with request IDs, upstream auth checks, and a lazy `llama-cpp-python` translator adapter.
- Model-path resolution now supports either `MODEL_PATH` or `MODEL_VOLUME_MOUNT_PATH` + `MODEL_FILENAME`.
- The Modal image now preinstalls `build-essential` and `cmake`, and the repo includes `services/inference/scripts/check_modal_readiness.py` for pre-deploy env validation.
- A dependency-backed runtime verification still needs FastAPI, Modal, and `llama-cpp-python` installed in the target environment.

## 4) Edge Proxy (`apps/web` Pages Function)

- [x] Implement `POST /api/translate`
- [x] Validate `sourceText`, `sourceLang`, and `targetLang`
- [ ] Verify Turnstile
- [ ] Apply rate limiting
- [x] Forward to Modal with secret header
- [x] Normalize success and error responses

Acceptance criteria:

- Browser never calls Modal directly
- `400`, `413`, `429`, and `503` responses match the API spec
- Every response includes `requestId`

Current note:

- `apps/web` now exists with a tested Pages Function proxy that validates the frozen request contract, forwards authenticated inference requests, and normalizes upstream failures.
- Server-side Turnstile verification is scaffolded behind the shared `429` response shape, and the client widget flow now fetches `TURNSTILE_SITE_KEY` from a Pages Function config endpoint before forwarding `cf-turnstile-response`.
- Cloudflare-managed rate limiting and live Turnstile key verification are still pending external setup.

## 5) Frontend UI

- [x] Create `apps/web` UI scaffold
- [x] Add input text area
- [x] Add source/target toggle (`ko`, `ko-jeju`)
- [x] Add submit button
- [x] Add output area and error area
- [x] Add copy output, clear input, and example phrases
- [x] Preserve line breaks in output rendering

Acceptance criteria:

- UI renders and accepts user input without JS/runtime errors.

Current note:

- The current UI is a static MVP shell intended for deployment, not just a placeholder for later replacement.
- The shell now includes local validation, example phrases, copy output, request-ID display, and clearer error/status messaging.
- The static shell is the intended MVP frontend for now; any React + TypeScript rewrite is deferred until after deployment proves stable.

## 6) Observability

- [x] Generate `requestId` for every request
- [x] Log request direction, char length, latency, and status
- [x] Avoid logging raw translation text by default
- [x] Track Cloudflare and Modal timing separately

Acceptance criteria:

- Production errors can be traced from edge to inference by `requestId`

Current note:

- The edge proxy now forwards `x-request-id` to inference, and inference reuses that ID in its response/logging path.
- Both edge and inference now emit structured request logs with direction, character length, status, and latency fields while avoiding raw source/translation text.
- Live dashboarding and platform-specific verification still need deployment-side setup.

## 7) Manual Test Matrix

- [x] Valid short sentence
- [x] Empty input
- [x] Unsupported language pair
- [x] Same source/target language
- [x] Long input rejected with `413`
- [x] Failed Turnstile / rate-limit path
- [x] Simulated Modal timeout

Acceptance criteria:

- Each case has expected UI and API behavior documented.

Current note:

- Expected API and UI behavior is now documented in `docs/manual-test-matrix.md`.
- Automated coverage exists for the core proxy validation paths, abuse-protection shape, and simulated upstream timeout path.

## 8) Portfolio Launch Docs

- [ ] Update README with chosen quant and latency numbers
- [x] Publish architecture and evaluation docs
- [ ] Ensure no raw dataset files are committed to the public repo

Acceptance criteria:

- Public-facing docs describe architecture, benchmarks, and protections clearly

## 9) Repo Hygiene And Release Engineering

- [x] Land `apps/web`, `services/inference`, `packages/shared`, and `packages/eval` as the canonical tracked repo state
- [x] Retire or archive legacy frontend surfaces outside `apps/web`
- [x] Make the documented Python verification path runnable from a clean environment
- [x] Add CI coverage for the Python and Node test paths
- [x] Record one reproducible beta-validation workflow in docs

Acceptance criteria:

- A fresh clone can run the documented verification commands after following the repo setup instructions
- The intended MVP app lives in one canonical frontend path
- CI fails when the core proxy or inference contract regresses

Current note:

- The repo now includes `requirements-dev.txt` plus a GitHub Actions workflow for the Python and web test paths.
- A local `.venv` install succeeded and the documented Python test command passed.

## Return-To-Review Notes (Fill before coming back)

- Quant chosen: `Q4_K_M` (provisional MVP default)
- File structure summary: `packages/shared`, `services/inference`, and `apps/web` now exist; the web app is currently a richer static shell plus Pages Function proxy scaffold.
- What deviated from `api-spec.md` (if anything): the current inference skeleton also uses an internal `401 unauthorized` response for missing/invalid upstream auth.
- Top 4 blockers: dependency-backed `llama-cpp-python` service verification, Cloudflare protections, deployment-side eval/latency proof, and launch licensing/attribution signoff.
