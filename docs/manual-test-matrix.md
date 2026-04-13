# Manual Test Matrix

This document records the expected API and UI behavior for the MVP translator.

Use it for pre-deploy checks, smoke testing, and release review.

## Scope

- Public route: `POST /api/translate`
- Supported directions:
  - `ko -> ko-jeju`
  - `ko-jeju -> ko`
- Current frontend posture: static `apps/web` shell on Cloudflare Pages

## Cases

| Case | Example Input | Expected API Result | Expected UI Result | Current Local Coverage |
|---|---|---|---|---|
| Valid short sentence | `{"sourceText":"안녕하세요","sourceLang":"ko","targetLang":"ko-jeju"}` | `200` with `translation`, `model`, `latencyMs`, `requestId` | Output area shows translation, status shows success, copy button enables, request ID displays | Automated in `apps/web/tests/translate.test.js` |
| Empty input | `{"sourceText":"   ","sourceLang":"ko","targetLang":"ko-jeju"}` | `400 invalid_input` | Client-side validation blocks submit with clear error, or server returns `400` if bypassed | Shared validation tests + local shell validation |
| Unsupported language pair | `{"sourceText":"hello","sourceLang":"en","targetLang":"ko"}` | `400 invalid_input` | Error area explains unsupported pair, no stale translation remains visible | Local API validation path is implemented; manual browser check still useful |
| Same source/target language | `{"sourceText":"안녕하세요","sourceLang":"ko","targetLang":"ko"}` | `400 invalid_input` | Client-side validation blocks submit with clear error | Automated in `apps/web/tests/translate.test.js` |
| Long input rejected | `sourceText.length > 500` | `413 input_too_long` | Error area explains the v1 cap, no upstream call should be made | Automated in `apps/web/tests/translate.test.js` |
| Failed Turnstile | Valid request but missing/invalid Turnstile token when enabled | `429 rate_limited` | UI shows abuse-protection style error; browser never sees verification internals | Server-side scaffold tested; full browser verification requires Cloudflare config |
| Rate-limited request | Valid request rejected by rate-limit layer | `429 rate_limited` | UI shows abuse-protection style error and preserves input text for retry | Automated hook coverage in `apps/web/tests/translate.test.js`; full Cloudflare behavior requires deployment |
| Upstream timeout / Modal unavailable | Valid request but inference fetch rejects or times out | `503 upstream_unavailable` | UI shows translator-unavailable state and request ID | Automated in `apps/web/tests/translate.test.js`; deployed timeout thresholds still need staging validation |
| Upstream unauthenticated | Valid request reaches inference with wrong secret | Public edge should normalize to `503 upstream_unavailable` | UI shows unavailable state rather than leaking internal auth details | Automated in `apps/web/tests/translate.test.js` |
| Health degraded | `GET /health` while model is not ready | `200` with `status: "degraded"` and `modelLoaded: false` | Not shown in the public UI today; for operator checks only | Automated in `services/inference/tests/test_asgi.py` |

## Browser Smoke Checklist

Run this against the static shell before release:

1. Load the page on desktop and mobile-sized viewports.
2. Confirm example buttons populate the form correctly.
3. Confirm swapping source/target preserves the input text.
4. Confirm multiline input preserves line breaks in output rendering.
5. Confirm `Copy output` only enables after a successful translation.
6. Confirm the request ID appears on both success and failure responses.
7. Confirm input text remains available after `429` and `503` failures so the user can retry.

## Notes

- `429` intentionally hides whether Turnstile or rate limiting caused the rejection.
- Internal inference `401 unauthorized` responses are normalized by the edge into public `503 upstream_unavailable`.
- Request tracing should be checked end to end with the same `requestId` visible in edge logs, inference logs, and user-visible responses.
