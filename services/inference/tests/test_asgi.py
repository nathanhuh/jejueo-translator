from __future__ import annotations

import asyncio
import json

from jejueo_inference.asgi import create_app
from jejueo_inference.settings import InferenceSettings


class FakeTranslator:
    def __init__(self, ready: bool = True) -> None:
        self.ready = ready

    def is_ready(self) -> bool:
        return self.ready

    def translate(self, source_lang: str, target_lang: str, source_text: str) -> tuple[str, int]:
        return f"{target_lang}:{source_text}", 12


async def invoke(app, method: str, path: str, body: bytes = b"", headers: list[tuple[bytes, bytes]] | None = None):
    messages = [
        {"type": "http.request", "body": body, "more_body": False},
    ]
    sent: list[dict[str, object]] = []

    async def receive():
        return messages.pop(0)

    async def send(message):
        sent.append(message)

    await app(
        {"type": "http", "method": method, "path": path, "headers": headers or []},
        receive,
        send,
    )
    return sent


def response_headers(sent) -> dict[str, str]:
    return {
        key.decode("utf-8"): value.decode("utf-8")
        for key, value in sent[0]["headers"]
    }


def test_health_reports_degraded_without_model() -> None:
    app = create_app(InferenceSettings(auth_token="secret"), translator=FakeTranslator(ready=False))
    sent = asyncio.run(invoke(app, "GET", "/health"))

    response = json.loads(sent[1]["body"])
    assert sent[0]["status"] == 200
    assert response["status"] == "degraded"
    assert response["modelLoaded"] is False


def test_translate_requires_auth() -> None:
    app = create_app(InferenceSettings(auth_token="secret"), translator=FakeTranslator())
    body = json.dumps(
        {"sourceText": "안녕하세요", "sourceLang": "ko", "targetLang": "ko-jeju"}
    ).encode("utf-8")
    sent = asyncio.run(invoke(app, "POST", "/translate", body=body))

    response = json.loads(sent[1]["body"])
    assert sent[0]["status"] == 401
    assert response["error"] == "unauthorized"


def test_translate_returns_normalized_payload() -> None:
    app = create_app(InferenceSettings(auth_token="secret"), translator=FakeTranslator())
    body = json.dumps(
        {"sourceText": "안녕하세요", "sourceLang": "ko", "targetLang": "ko-jeju"}
    ).encode("utf-8")
    sent = asyncio.run(
        invoke(
            app,
            "POST",
            "/translate",
            body=body,
            headers=[(b"x-inference-auth", b"secret")],
        )
    )

    response = json.loads(sent[1]["body"])
    assert sent[0]["status"] == 200
    assert response["translation"] == "ko-jeju:안녕하세요"
    assert response["latencyMs"] == 12
    assert response["model"] == "alan-llm-jeju-dialect-v1-4b-q4km"


def test_translate_rejects_invalid_pair() -> None:
    app = create_app(InferenceSettings(auth_token="secret"), translator=FakeTranslator())
    body = json.dumps(
        {"sourceText": "안녕하세요", "sourceLang": "ko", "targetLang": "ko"}
    ).encode("utf-8")
    sent = asyncio.run(
        invoke(
            app,
            "POST",
            "/translate",
            body=body,
            headers=[(b"x-inference-auth", b"secret")],
        )
    )

    response = json.loads(sent[1]["body"])
    assert sent[0]["status"] == 400
    assert response["error"] == "invalid_input"


def test_translate_reuses_forwarded_request_id() -> None:
    app = create_app(InferenceSettings(auth_token="secret"), translator=FakeTranslator())
    body = json.dumps(
        {"sourceText": "안녕하세요", "sourceLang": "ko", "targetLang": "ko-jeju"}
    ).encode("utf-8")
    sent = asyncio.run(
        invoke(
            app,
            "POST",
            "/translate",
            body=body,
            headers=[
                (b"x-inference-auth", b"secret"),
                (b"x-request-id", b"edge-request-123"),
            ],
        )
    )

    response = json.loads(sent[1]["body"])
    headers = response_headers(sent)
    assert response["requestId"] == "edge-request-123"
    assert headers["x-request-id"] == "edge-request-123"
