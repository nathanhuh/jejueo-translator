from __future__ import annotations

import os
from pathlib import Path

import pytest

from jejueo_inference.deploy import (
    build_deploy_readiness_report,
    classify_model_source,
    parse_env_file,
    resolve_env_file,
)
from jejueo_inference.settings import InferenceSettings


def test_parse_env_file_reads_assignments(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "INFERENCE_AUTH_TOKEN=secret\nMODEL_FILENAME=alan.gguf\n",
        encoding="utf-8",
    )

    payload = parse_env_file(env_file)

    assert payload["INFERENCE_AUTH_TOKEN"] == "secret"
    assert payload["MODEL_FILENAME"] == "alan.gguf"


def test_parse_env_file_rejects_invalid_lines(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("INVALID_LINE\n", encoding="utf-8")

    with pytest.raises(ValueError, match="expected KEY=VALUE"):
        parse_env_file(env_file)


def test_resolve_env_file_allows_missing_default_path(tmp_path: Path) -> None:
    default_env = tmp_path / ".env"

    resolved = resolve_env_file(default_env, default_path=default_env)

    assert resolved is None


def test_resolve_env_file_rejects_missing_explicit_path(tmp_path: Path) -> None:
    default_env = tmp_path / ".env"
    explicit_env = tmp_path / "custom.env"

    with pytest.raises(FileNotFoundError, match="Env file not found"):
        resolve_env_file(explicit_env, default_path=default_env)


def test_classify_model_source_distinguishes_path_volume_and_unset() -> None:
    assert classify_model_source(InferenceSettings(model_path="/models/alan.gguf")) == "model_path"
    assert classify_model_source(InferenceSettings(model_filename="alan.gguf")) == "modal_volume"
    assert classify_model_source(InferenceSettings()) == "unset"


def test_build_deploy_readiness_report_uses_env_file_without_modal_cli_requirement(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "INFERENCE_AUTH_TOKEN=secret",
                "MODEL_FILENAME=alan.gguf",
                "MODEL_VOLUME_NAME=jejueo-models",
                "MODEL_VOLUME_MOUNT_PATH=/models",
            ]
        ),
        encoding="utf-8",
    )

    report = build_deploy_readiness_report(
        env_file=env_file,
        require_modal_cli=False,
    )

    assert report.ready is True
    assert report.settings.uses_model_volume is True
    assert report.settings.resolved_model_path == "/models/alan.gguf"


def test_build_deploy_readiness_report_flags_missing_modal_cli(monkeypatch) -> None:
    monkeypatch.delenv("INFERENCE_AUTH_TOKEN", raising=False)
    monkeypatch.setattr("jejueo_inference.deploy.detect_modal_cli", lambda: None)
    monkeypatch.setenv("INFERENCE_AUTH_TOKEN", "secret")
    monkeypatch.setenv("MODEL_FILENAME", "alan.gguf")
    monkeypatch.setenv("MODEL_VOLUME_NAME", "jejueo-models")
    monkeypatch.setenv("MODEL_VOLUME_MOUNT_PATH", "/models")

    report = build_deploy_readiness_report()

    assert report.ready is False
    assert any("modal CLI is not installed" in item for item in report.errors)
