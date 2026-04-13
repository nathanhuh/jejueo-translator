# API Specification (MVP v1)

## Purpose

Define a stable contract between the frontend, edge proxy, and inference service.

## Public Endpoint

- `POST /api/translate`

## Request Schema

```json
{
  "sourceText": "대한민국은 사계절이 뚜렷합니다.",
  "sourceLang": "ko",
  "targetLang": "ko-jeju"
}
```

### Fields

- `sourceText` (`string`, required)
- `sourceLang` (`enum`, required): `ko`, `ko-jeju`
- `targetLang` (`enum`, required): `ko`, `ko-jeju`

### Input Cap

- v1 hard cap: `500` Unicode characters in `sourceText`
- Inputs above this cap must be rejected with `413 Payload Too Large`
- v1 does not support chunking or multi-part translation
- This cap may be revised later after benchmark and production-latency evidence is available

### Validation

- Reject empty or whitespace-only input.
- Reject unsupported language pairs.
- Reject `sourceLang === targetLang`.
- Reject inputs above `500` Unicode characters.
- Preserve internal line breaks.

## Success Response

```json
{
  "translation": "...",
  "model": "alan-llm-jeju-dialect-v1-4b-q4km",
  "latencyMs": 1420,
  "requestId": "uuid"
}
```

### Response Notes

- The API returns translation text only.
- No explanations, notes, confidence scores, or evidence payloads are returned in v1.
- `model` should identify the deployed quant alias, not an internal filesystem path.

## Error Responses

### `400 Bad Request`

Use `400` for malformed JSON, missing required fields, unsupported language pairs, same-language requests, or empty/whitespace-only input.

```json
{
  "error": "invalid_input",
  "message": "Unsupported language pair",
  "requestId": "uuid"
}
```

### `413 Payload Too Large`

Use `413` when `sourceText` exceeds the v1 cap of `500` Unicode characters.

```json
{
  "error": "input_too_long",
  "message": "Input exceeds the v1 limit of 500 characters",
  "requestId": "uuid"
}
```

### `429 Too Many Requests`

Use `429` for either rate-limiting or failed Turnstile verification in v1. These cases intentionally share one public error shape.

```json
{
  "error": "rate_limited",
  "message": "Request rejected by abuse protection",
  "requestId": "uuid"
}
```

### `503 Service Unavailable`

Use `503` when the upstream translation service is unavailable, times out, or fails health/readiness checks.

```json
{
  "error": "upstream_unavailable",
  "message": "Translation service unavailable",
  "requestId": "uuid"
}
```

## Internal Service Contract

The edge proxy should forward the same language fields to Modal and add server-side authentication headers. The browser must never see or send the Modal secret.

The edge proxy is responsible for:

- enforcing the `500`-character limit before upstream inference
- normalizing upstream failures into the public v1 error taxonomy
- keeping Turnstile and rate-limiting details behind the shared `429` response shape

## SLO Targets

- Warm `p50 < 2.5s` for short inputs
- Warm `p95 < 5s`
- Cold-start first response under `10s`

## Versioning Policy

- Keep additive, backward-compatible changes in `v1`.
- Use a new path version only for breaking changes.

## Current v1 Contract Decisions Locked

- `sourceText` is capped at `500` Unicode characters
- the public API returns translation text only
- failed Turnstile verification and rate limiting share the same `429` public response
- oversized input is rejected at the edge before inference
