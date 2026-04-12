from __future__ import annotations

import json
from typing import Any

from pydantic import ValidationError

from .constants import INPUT_CHAR_LIMIT, INPUT_TOO_LONG, INVALID_INPUT, SUPPORTED_LANGS
from .errors import ApiError
from .models import TranslationRequest


def parse_request_json(raw_body: bytes) -> dict[str, Any]:
    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ApiError(400, INVALID_INPUT, "Request body must be valid UTF-8 JSON") from exc
    except json.JSONDecodeError as exc:
        raise ApiError(400, INVALID_INPUT, "Malformed JSON request body") from exc

    if not isinstance(payload, dict):
        raise ApiError(400, INVALID_INPUT, "Request body must be a JSON object")
    return payload


def validate_translation_request(payload: dict[str, Any]) -> TranslationRequest:
    try:
        request = TranslationRequest.model_validate(payload)
    except ValidationError as exc:
        errors = exc.errors()
        first_error = errors[0] if errors else {}
        field = ".".join(str(part) for part in first_error.get("loc", []))
        message = f"Invalid request field: {field}" if field else "Invalid request body"
        raise ApiError(400, INVALID_INPUT, message) from exc

    if not request.sourceText.strip():
        raise ApiError(400, INVALID_INPUT, "Input text must not be empty")
    if request.sourceLang not in SUPPORTED_LANGS or request.targetLang not in SUPPORTED_LANGS:
        raise ApiError(400, INVALID_INPUT, "Unsupported language pair")
    if request.sourceLang == request.targetLang:
        raise ApiError(400, INVALID_INPUT, "Source and target languages must differ")
    if len(request.sourceText) > INPUT_CHAR_LIMIT:
        raise ApiError(
            413,
            INPUT_TOO_LONG,
            f"Input exceeds the v1 limit of {INPUT_CHAR_LIMIT} characters",
        )

    return request
