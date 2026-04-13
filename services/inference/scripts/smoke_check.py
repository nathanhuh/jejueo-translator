from __future__ import annotations

import argparse
import json
import os
from typing import Any
from urllib import error, request


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Smoke-check a deployed Jejueo inference service."
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("INFERENCE_BASE_URL", ""),
        help="Deployed inference base URL, for example https://workspace--fastapi-app.modal.run",
    )
    parser.add_argument(
        "--auth-token",
        default=os.getenv("INFERENCE_AUTH_TOKEN", ""),
        help="Expected x-inference-auth token for authenticated requests.",
    )
    parser.add_argument("--source-text", default="안녕하세요")
    parser.add_argument("--source-lang", default="ko")
    parser.add_argument("--target-lang", default="ko-jeju")
    parser.add_argument(
        "--allow-degraded",
        action="store_true",
        help="Allow /health to report modelLoaded=false without failing the check.",
    )
    parser.add_argument(
        "--skip-unauth-check",
        action="store_true",
        help="Skip the direct unauthenticated /translate check.",
    )
    return parser.parse_args()


def request_json(
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    payload: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    body = None
    request_headers = {"accept": "application/json"}
    if headers:
        request_headers.update(headers)
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request_headers["content-type"] = "application/json"

    req = request.Request(url, data=body, headers=request_headers, method=method)

    try:
        with request.urlopen(req, timeout=30) as response:
            raw_body = response.read()
            return response.getcode(), json.loads(raw_body.decode("utf-8"))
    except error.HTTPError as exc:
        raw_body = exc.read()
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            payload = {"raw": raw_body.decode("utf-8", errors="replace")}
        return exc.code, payload
    except error.URLError as exc:
        raise SystemExit(f"Request failed for {url}: {exc.reason}") from exc


def print_result(name: str, status_code: int, payload: dict[str, Any]) -> None:
    print(f"[{name}] status={status_code}")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def main() -> int:
    args = parse_args()
    base_url = args.base_url.rstrip("/")
    require(bool(base_url), "--base-url or INFERENCE_BASE_URL is required")
    require(bool(args.auth_token), "--auth-token or INFERENCE_AUTH_TOKEN is required")

    health_status, health_payload = request_json(f"{base_url}/health")
    print_result("health", health_status, health_payload)
    require(health_status == 200, "Expected /health to return HTTP 200")
    if not args.allow_degraded:
        require(
            health_payload.get("modelLoaded") is True,
            "Expected /health to report modelLoaded=true",
        )

    translate_payload = {
        "sourceText": args.source_text,
        "sourceLang": args.source_lang,
        "targetLang": args.target_lang,
    }
    auth_status, auth_payload = request_json(
        f"{base_url}/translate",
        method="POST",
        headers={"x-inference-auth": args.auth_token},
        payload=translate_payload,
    )
    print_result("translate-auth", auth_status, auth_payload)
    require(auth_status == 200, "Expected authenticated /translate to return HTTP 200")
    require(
        isinstance(auth_payload.get("translation"), str) and bool(auth_payload["translation"].strip()),
        "Expected authenticated /translate to return a non-empty translation",
    )
    require(
        isinstance(auth_payload.get("requestId"), str) and bool(auth_payload["requestId"].strip()),
        "Expected authenticated /translate to return a requestId",
    )

    if not args.skip_unauth_check:
        unauth_status, unauth_payload = request_json(
            f"{base_url}/translate",
            method="POST",
            payload=translate_payload,
        )
        print_result("translate-unauth", unauth_status, unauth_payload)
        require(
            unauth_status == 401,
            "Expected unauthenticated direct /translate to return HTTP 401",
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
