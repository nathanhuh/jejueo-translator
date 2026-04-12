from __future__ import annotations

from jejueo_inference.settings import InferenceSettings


def test_resolved_model_path_prefers_explicit_model_path() -> None:
    settings = InferenceSettings(
        model_path="/custom/model.gguf",
        model_filename="ignored.gguf",
        model_volume_mount_path="/models",
    )

    assert settings.resolved_model_path == "/custom/model.gguf"


def test_resolved_model_path_uses_volume_mount_and_filename() -> None:
    settings = InferenceSettings(
        model_filename="alan-q4km.gguf",
        model_volume_mount_path="/models",
    )

    assert settings.resolved_model_path == "/models/alan-q4km.gguf"


def test_from_env_reads_modal_scaling_controls(monkeypatch) -> None:
    monkeypatch.setenv("MODAL_MIN_CONTAINERS", "1")
    monkeypatch.setenv("MODAL_SCALEDOWN_WINDOW", "300")

    settings = InferenceSettings.from_env()

    assert settings.modal_min_containers == 1
    assert settings.modal_scaledown_window == 300
