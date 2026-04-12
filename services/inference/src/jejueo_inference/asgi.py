from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from typing import Any

from jejueo_shared import ApiError, ErrorResponse

from .service import InferenceService
from .settings import InferenceSettings
from .translator import build_default_translator

Scope = dict[str, Any]
Message = dict[str, Any]
Receive = Callable[[], Awaitable[Message]]
Send = Callable[[Message], Awaitable[None]]


def _json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


async def _read_body(receive: Receive) -> bytes:
    body = bytearray()
    while True:
        message = await receive()
        body.extend(message.get("body", b""))
        if not message.get("more_body", False):
            return bytes(body)


async def _send_json(send: Send, status_code: int, payload: dict[str, Any]) -> None:
    body = _json_bytes(payload)
    headers = [
        (b"content-type", b"application/json; charset=utf-8"),
        (b"content-length", str(len(body)).encode("ascii")),
    ]
    request_id = payload.get("requestId")
    if isinstance(request_id, str) and request_id:
        headers.append((b"x-request-id", request_id.encode("utf-8")))
    await send({"type": "http.response.start", "status": status_code, "headers": headers})
    await send({"type": "http.response.body", "body": body})


def _header_value(scope: Scope, name: bytes) -> str | None:
    for key, value in scope.get("headers", []):
        if key.lower() == name:
            return value.decode("utf-8")
    return None


class InferenceASGIApp:
    def __init__(self, service: InferenceService) -> None:
        self.service = service

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await _send_json(send, 500, {"error": "unsupported_scope"})
            return

        method = scope["method"].upper()
        path = scope["path"]
        request_id = self.service.resolve_request_id(_header_value(scope, b"x-request-id"))

        try:
            if method == "GET" and path == "/health":
                payload = self.service.health(request_id).model_dump()
                await _send_json(send, 200, payload)
                return

            if method == "POST" and path == "/translate":
                self.service.authorize(_header_value(scope, b"x-inference-auth"), request_id)
                body = await _read_body(receive)
                payload = self.service.translate(body, request_id).model_dump()
                await _send_json(send, 200, payload)
                return

            error = ErrorResponse(
                error="not_found",
                message="Route not found",
                requestId=request_id,
            )
            self.service.log_event(
                "warning",
                event="inference_route",
                requestId=request_id,
                status=404,
                error="not_found",
                method=method,
                path=path,
            )
            await _send_json(send, 404, error.model_dump())
        except ApiError as exc:
            status_code, error = self.service.error_response(exc, request_id)
            await _send_json(send, status_code, error.model_dump())


def create_app(
    settings: InferenceSettings | None = None,
    translator: Any | None = None,
) -> InferenceASGIApp:
    resolved_settings = settings or InferenceSettings.from_env()
    resolved_translator = translator or build_default_translator(resolved_settings)
    service = InferenceService(resolved_settings, resolved_translator)
    return InferenceASGIApp(service)
