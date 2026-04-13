from __future__ import annotations

import json
import logging

import pytest

from jejueo_inference.service import InferenceService
from jejueo_inference.settings import InferenceSettings
from jejueo_shared import ApiError


class FakeTranslator:
    def is_ready(self) -> bool:
        return True

    def translate(self, source_lang: str, target_lang: str, source_text: str) -> tuple[str, int]:
        return f"{target_lang}:{source_text}", 17


def build_service(logger_name: str) -> InferenceService:
    logger = logging.getLogger(logger_name)
    logger.handlers = []
    logger.propagate = True
    return InferenceService(InferenceSettings(auth_token="secret"), FakeTranslator(), logger=logger)


def test_resolve_request_id_prefers_forwarded_value() -> None:
    service = build_service("test.resolve_request_id")
    assert service.resolve_request_id("edge-123") == "edge-123"


def test_translate_logs_structured_metadata(caplog) -> None:
    service = build_service("test.translate_logs")
    body = json.dumps(
        {"sourceText": "안녕하세요", "sourceLang": "ko", "targetLang": "ko-jeju"}
    ).encode("utf-8")

    with caplog.at_level(logging.INFO, logger="test.translate_logs"):
        service.translate(body, "request-1")

    record = json.loads(caplog.records[-1].message)
    assert record["event"] == "inference_translate"
    assert record["requestId"] == "request-1"
    assert record["direction"] == "ko->ko-jeju"
    assert record["charLength"] == 5
    assert record["latencyMs"] == 17
    assert "sourceText" not in record


def test_translate_logs_invalid_input_without_raw_text(caplog) -> None:
    service = build_service("test.translate_invalid_logs")
    body = json.dumps(
        {"sourceText": "   ", "sourceLang": "ko", "targetLang": "ko-jeju"}
    ).encode("utf-8")

    with caplog.at_level(logging.WARNING, logger="test.translate_invalid_logs"):
        with pytest.raises(ApiError):
            service.translate(body, "request-2")

    record = json.loads(caplog.records[-1].message)
    assert record["event"] == "inference_translate"
    assert record["status"] == 400
    assert record["error"] == "invalid_input"
    assert record["charLength"] == 3
    assert "sourceText" not in record


def test_authorize_logs_invalid_upstream_auth(caplog) -> None:
    service = build_service("test.authorize_logs")

    with caplog.at_level(logging.WARNING, logger="test.authorize_logs"):
        with pytest.raises(ApiError):
            service.authorize("wrong", "request-3")

    record = json.loads(caplog.records[-1].message)
    assert record["event"] == "inference_auth"
    assert record["requestId"] == "request-3"
    assert record["status"] == 401
    assert record["error"] == "unauthorized"
