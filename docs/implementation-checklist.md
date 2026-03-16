# Implementation Checklist

Use this as your hands-on build tracker. Check each item only when the acceptance criteria is met.

## 1) Shared Contract

- [ ] Create `packages/shared`
- [ ] Freeze request/response schema for `POST /api/translate`
- [ ] Document v1 error taxonomy

Acceptance criteria:

- Schema matches [`docs/api-spec.md`](/Users/nathanhuh/Documents/Documents - Nathan’s MacBook Pro/Personal_Repos/jejueo-translator/docs/api-spec.md)
- Success and error shapes are stable enough for parallel frontend/backend work

## 2) Evaluation Harness

- [ ] Create `packages/eval`
- [ ] Add fixed evaluation set for both directions
- [ ] Add benchmark script for `Q4_K_M` and `Q5_K_M`
- [ ] Record quant decision criteria

Acceptance criteria:

- Benchmark output records latency and quality notes for both quants
- Evaluation set covers formatting, proper nouns, and ambiguous phrasing

## 3) Inference Service (`services/inference`)

- [ ] Create Modal app scaffold
- [ ] Add `GET /health`
- [ ] Add `POST /translate`
- [ ] Load chosen GGUF with `llama-cpp-python`
- [ ] Mount model weights from a Modal Volume
- [ ] Enforce secret-authenticated upstream access

Acceptance criteria:

- `/health` returns model-ready state
- Authenticated requests succeed
- Direct unauthenticated requests fail

## 4) Edge Proxy (`apps/web` Pages Function)

- [ ] Implement `POST /api/translate`
- [ ] Validate `sourceText`, `sourceLang`, and `targetLang`
- [ ] Verify Turnstile
- [ ] Apply rate limiting
- [ ] Forward to Modal with secret header
- [ ] Normalize success and error responses

Acceptance criteria:

- Browser never calls Modal directly
- `400`, `413`, `429`, and `503` responses match the API spec
- Every response includes `requestId`

## 5) Frontend UI

- [ ] Create `apps/web` UI scaffold
- [ ] Add input text area
- [ ] Add source/target toggle (`ko`, `ko-jeju`)
- [ ] Add submit button
- [ ] Add output area and error area
- [ ] Add copy output, clear input, and example phrases
- [ ] Preserve line breaks in output rendering

Acceptance criteria:

- UI renders and accepts user input without JS/runtime errors.

## 6) Observability

- [ ] Generate `requestId` for every request
- [ ] Log request direction, char length, latency, and status
- [ ] Avoid logging raw translation text by default
- [ ] Track Cloudflare and Modal timing separately

Acceptance criteria:

- Production errors can be traced from edge to inference by `requestId`

## 7) Manual Test Matrix

- [ ] Valid short sentence
- [ ] Empty input
- [ ] Unsupported language pair
- [ ] Same source/target language
- [ ] Long input rejected with `413`
- [ ] Failed Turnstile / rate-limit path
- [ ] Simulated Modal timeout

Acceptance criteria:

- Each case has expected UI and API behavior documented.

## 8) Portfolio Launch Docs

- [ ] Update README with chosen quant and latency numbers
- [ ] Publish architecture and evaluation docs
- [ ] Ensure no raw dataset files are committed to the public repo

Acceptance criteria:

- Public-facing docs describe architecture, benchmarks, and protections clearly

## Return-To-Review Notes (Fill before coming back)

- Quant chosen:
- File structure summary:
- What deviated from `api-spec.md` (if anything):
- Top 3 blockers:
