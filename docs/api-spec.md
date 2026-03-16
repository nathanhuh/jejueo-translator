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

### Validation

- Reject empty or whitespace-only input.
- Reject unsupported language pairs.
- Reject `sourceLang === targetLang`.
- Reject inputs above the configured hard cap for v1.
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

```json
{
  "error": "invalid_input",
  "message": "Unsupported language pair",
  "requestId": "uuid"
}
```

### `413 Payload Too Large`

```json
{
  "error": "input_too_long",
  "message": "Input exceeds the v1 length limit",
  "requestId": "uuid"
}
```

### `429 Too Many Requests`

Use `429` for either rate-limiting or failed Turnstile verification.

```json
{
  "error": "rate_limited",
  "message": "Request rejected by abuse protection",
  "requestId": "uuid"
}
```

### `503 Service Unavailable`

```json
{
  "error": "upstream_unavailable",
  "message": "Translation service unavailable",
  "requestId": "uuid"
}
```

## Internal Service Contract

The edge proxy should forward the same language fields to Modal and add server-side authentication headers. The browser must never see or send the Modal secret.

## SLO Targets

- Warm `p50 < 2.5s` for short inputs
- Warm `p95 < 5s`
- Cold-start first response under `10s`

## Versioning Policy

- Keep additive, backward-compatible changes in `v1`.
- Use a new path version only for breaking changes.
