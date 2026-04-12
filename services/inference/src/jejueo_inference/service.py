from __future__ import annotations

import json
import logging
from uuid import uuid4

from jejueo_shared import (
    ApiError,
    ErrorResponse,
    HealthResponse,
    TranslationResponse,
    UNAUTHORIZED,
    parse_request_json,
    validate_translation_request,
)

from .settings import InferenceSettings
from .translator import Translator


class InferenceService:
    def __init__(
        self,
        settings: InferenceSettings,
        translator: Translator,
        logger: logging.Logger | None = None,
    ) -> None:
        self.settings = settings
        self.translator = translator
        self.logger = logger or logging.getLogger("jejueo_inference")

    def make_request_id(self) -> str:
        return str(uuid4())

    def resolve_request_id(self, provided_request_id: str | None) -> str:
        if provided_request_id and provided_request_id.strip():
            return provided_request_id.strip()
        return self.make_request_id()

    def log_event(self, level: str, **fields: object) -> None:
        payload = {key: value for key, value in fields.items() if value is not None}
        log_method = getattr(self.logger, level, self.logger.info)
        log_method(json.dumps(payload, ensure_ascii=False, sort_keys=True))

    def authorize(self, provided_token: str | None, request_id: str | None = None) -> None:
        expected_token = self.settings.auth_token
        if not expected_token:
            return
        if provided_token != expected_token:
            self.log_event(
                "warning",
                event="inference_auth",
                requestId=request_id,
                status=401,
                error=UNAUTHORIZED,
            )
            raise ApiError(401, UNAUTHORIZED, "Missing or invalid upstream auth")

    def health(self, request_id: str) -> HealthResponse:
        ready = self.translator.is_ready()
        response = HealthResponse(
            status="ok" if ready else "degraded",
            model=self.settings.model_alias,
            modelLoaded=ready,
            requestId=request_id,
        )
        self.log_event(
            "info",
            event="inference_health",
            requestId=request_id,
            status=200,
            model=self.settings.model_alias,
            modelLoaded=ready,
        )
        return response

    def translate(self, raw_body: bytes, request_id: str) -> TranslationResponse:
        payload: dict[str, object] | None = None
        direction: str | None = None
        char_length: int | None = None

        try:
            payload = parse_request_json(raw_body)
            source_lang = payload.get("sourceLang")
            target_lang = payload.get("targetLang")
            source_text = payload.get("sourceText")

            if isinstance(source_lang, str) and isinstance(target_lang, str):
                direction = f"{source_lang}->{target_lang}"
            if isinstance(source_text, str):
                char_length = len(source_text)

            request = validate_translation_request(payload)
            translation, latency_ms = self.translator.translate(
                request.sourceLang,
                request.targetLang,
                request.sourceText,
            )
            response = TranslationResponse(
                translation=translation,
                model=self.settings.model_alias,
                latencyMs=latency_ms,
                requestId=request_id,
            )
            self.log_event(
                "info",
                event="inference_translate",
                requestId=request_id,
                status=200,
                direction=direction,
                charLength=char_length,
                latencyMs=latency_ms,
                model=self.settings.model_alias,
            )
            return response
        except ApiError as exc:
            self.log_event(
                "warning",
                event="inference_translate",
                requestId=request_id,
                status=exc.status_code,
                error=exc.error,
                direction=direction,
                charLength=char_length,
                model=self.settings.model_alias,
            )
            raise

    def error_response(self, error: ApiError, request_id: str) -> tuple[int, ErrorResponse]:
        return error.status_code, ErrorResponse(
            error=error.error,
            message=error.message,
            requestId=request_id,
        )
