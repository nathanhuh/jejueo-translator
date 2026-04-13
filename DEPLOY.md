# Deploy Guide

This document covers the remaining external blockers for launching the MVP and gives a practical estimate for resolving each one.

## Current Local State

Already complete locally:

- shared request/response contract
- evaluation tooling and fixed eval set
- inference ASGI/FastAPI/Modal scaffolding
- edge proxy validation and response normalization
- structured request logging with forwarded `requestId`
- static MVP frontend shell
- checked-in Cloudflare Pages config in `apps/web/wrangler.toml`
- local Pages env template in `apps/web/.dev.vars.example`
- Turnstile sitekey config endpoint plus browser token submission flow
- inference deploy env template in `services/inference/.env.example`
- deployed inference smoke-check script in `services/inference/scripts/smoke_check.py`
- targeted Python and Node test coverage

Still blocked on external systems:

- real Modal runtime verification with the GGUF model
- real Modal Volume setup
- Cloudflare Pages deployment and bindings
- Cloudflare Turnstile configuration
- Cloudflare rate limiting configuration
- launch-side licensing / attribution review

## Repo-Side Blockers Before Beta

These are not Cloudflare or Modal setup tasks, but they still block a credible
beta release:

- the repo has eval tooling and a fixed eval set, but it still lacks checked-in
  benchmark evidence and real deployed latency numbers for launch signoff

The old root/frontend prototype surfaces have been removed. `apps/web` is now
the only intended frontend path for beta.

The repo now includes:

- a root `requirements-dev.txt` for the core Python test surface
- a GitHub Actions workflow that runs the Python and Node verification paths
- a documented clean-checkout setup flow in `README.md`

Treat these as release blockers alongside the external platform setup items.

## External Blockers

### 1. Modal runtime verification

What is blocked:

- installing and validating `fastapi`, `modal`, and `llama-cpp-python` in the real deploy environment
- confirming the GGUF actually loads through the service path
- collecting first real `/health` and `/translate` checks on the intended stack

Why it is external:

- depends on Modal account/project setup, secrets, installed runtime packages, and access to the actual GGUF model file

How to resolve:

1. Create or select the target Modal app and authenticate the local CLI.
2. Install the server/runtime dependencies in the deployment environment.
3. Upload or attach the chosen GGUF through a Modal Volume.
4. Set environment variables and secret names to match `services/inference/src/jejueo_inference/settings.py`.
5. Deploy the Modal app and verify:
   - `/health` returns `modelLoaded: true`
   - authenticated `/translate` succeeds
   - unauthenticated direct requests fail

Estimated effort:

- happy path: `0.5-1 day`
- if `llama-cpp-python` or native build issues recur: `1-2 days`

Main risks:

- native dependency incompatibility
- model path or Volume mount mismatches
- cold-start behavior worse than expected

### 2. Modal Volume setup

What is blocked:

- proving that `MODEL_VOLUME_MOUNT_PATH` + `MODEL_FILENAME` works with the real deployed model artifact

Why it is external:

- requires a real Modal Volume and the actual model file uploaded there

How to resolve:

1. Create the Volume in Modal.
2. Upload the GGUF to the chosen path.
3. Set:
   - `MODEL_VOLUME_NAME`
   - `MODEL_VOLUME_MOUNT_PATH`
   - `MODEL_FILENAME`
4. Re-deploy and verify the service loads without relying on `MODEL_PATH`.

Estimated effort:

- `1-3 hours` if the model file is already available

Main risks:

- wrong filename or mount path
- large upload time for the model artifact

### 3. Cloudflare Pages deployment

What is blocked:

- deploying the static shell and Pages Function together in the real Cloudflare environment
- configuring environment bindings for the inference base URL and auth token

Why it is external:

- requires Cloudflare project setup, Pages bindings, and a live upstream service URL

How to resolve:

1. Create the Pages project.
2. Point the static asset root to `apps/web/public`.
3. Ensure the Pages Functions routing includes `apps/web/functions`.
4. Add environment variables:
   - `INFERENCE_BASE_URL`
   - `INFERENCE_AUTH_TOKEN`
   - later `TURNSTILE_SITE_KEY`
   - later `TURNSTILE_SECRET_KEY`
5. Deploy and smoke-test `/api/translate`.

Estimated effort:

- `0.5 day`

Main risks:

- binding/config mismatch between preview and production
- wrong function routing for static asset + function coexistence
- forgetting to expose `TURNSTILE_SITE_KEY` to the frontend config route

### 4. Turnstile

What is blocked:

- real challenge widget/sitekey setup and live verification against Cloudflare

Why it is external:

- requires Turnstile sitekey and secret creation in Cloudflare

How to resolve:

1. Create the Turnstile widget.
2. Add `TURNSTILE_SITE_KEY` and `TURNSTILE_SECRET_KEY` to Pages bindings.
4. Submit the token through the current edge request flow.
5. Verify success and failure paths both map to the public `429` shape.

Estimated effort:

- `2-4 hours`

Main risks:

- token field naming drift between frontend and edge
- false negatives during preview/staging testing

Local prep now committed:

- `apps/web/functions/api/config.js` exposes `TURNSTILE_SITE_KEY` to the static shell without hardcoding it into `public/`.
- `apps/web/public/app.js` now loads the Turnstile widget when that sitekey exists and forwards the token as `cf-turnstile-response`.

### 5. Cloudflare rate limiting

What is blocked:

- real request throttling in front of the deployed endpoint

Why it is external:

- depends on Cloudflare dashboard or ruleset configuration

How to resolve:

1. Define a first-pass rate policy suitable for a portfolio demo.
2. Apply the rule to `/api/translate`.
3. Confirm that rejected requests still produce the shared `429 rate_limited` public response.
4. Watch logs for accidental over-blocking during smoke testing.

Estimated effort:

- `1-3 hours`

Main risks:

- rate limits that are too strict for demos
- policy defined in the dashboard but not mirrored in written docs

### 6. Licensing / attribution signoff

What is blocked:

- confirming the public repo and deployed app have safe attribution wording for the model and any derived evaluation artifacts

Why it is external:

- this depends on reviewing the actual license chain and deciding on public wording

How to resolve:

1. Review [data-licensing.md](docs/data-licensing.md).
2. Decide on exact attribution wording for:
   - repo README
   - app footer or about text
   - deploy notes if needed
3. Reconfirm that no raw dataset files are exposed in the public repo.

Estimated effort:

- `0.5 day`

Main risks:

- uncertainty around whether derived eval artifacts are safe to publish
- delayed launch because wording is not approved early

## Recommended Deployment Order

1. Modal Volume + model upload
2. Modal runtime verification
3. Cloudflare Pages deployment with inference bindings
4. Turnstile wiring
5. Cloudflare rate limiting
6. Final eval evidence, launch docs, and attribution

## Overall Estimate

If the runtime behaves normally:

- about `1.5-3 days` of focused work

If native/runtime or policy tuning issues appear:

- about `3-5 days`

## Suggested Definition Of Done For Deployment

- `/health` reports `modelLoaded: true` in the deployed service
- authenticated end-to-end translation succeeds through Cloudflare
- direct unauthenticated inference requests fail
- Turnstile failures and rate-limited requests both return `429 rate_limited`
- timeouts or upstream failures return `503 upstream_unavailable`
- request tracing works through the same `requestId` at edge and inference
- benchmark and latency notes are updated with real values
- deploy docs, README notes, and attribution are updated with real values

## Repo-Side Deployment Helpers

Use the checked-in helpers before or during live setup:

1. Copy `apps/web/.dev.vars.example` to `apps/web/.dev.vars` for local Pages dev.
2. Copy `services/inference/.env.example` into your preferred local secret source before running Modal deploys.
3. After the Modal service is live, run:

```bash
PYTHONPATH='packages/shared/src:services/inference/src' \
python services/inference/scripts/smoke_check.py \
  --base-url 'https://<your-modal-endpoint>' \
  --auth-token '<your-inference-token>'
```

This verifies the deploy guide's first backend checks:

- `/health` returns `200`
- authenticated `/translate` works
- unauthenticated direct `/translate` fails with `401`
