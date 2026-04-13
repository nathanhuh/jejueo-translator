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


def test_uses_model_volume_only_when_model_filename_is_active() -> None:
    explicit_path = InferenceSettings(
        model_path="/custom/model.gguf",
        model_filename="ignored.gguf",
    )
    volume_only = InferenceSettings(model_filename="alan-q4km.gguf")

    assert explicit_path.uses_model_volume is False
    assert volume_only.uses_model_volume is True


def test_from_env_reads_modal_scaling_controls(monkeypatch) -> None:
    monkeypatch.setenv("MODAL_MIN_CONTAINERS", "1")
    monkeypatch.setenv("MODAL_SCALEDOWN_WINDOW", "300")

    settings = InferenceSettings.from_env()

    assert settings.modal_min_containers == 1
    assert settings.modal_scaledown_window == 300


def test_from_mapping_reads_non_env_mappings() -> None:
    settings = InferenceSettings.from_mapping(
        {
            "INFERENCE_AUTH_TOKEN": "secret",
            "MODEL_FILENAME": "alan.gguf",
            "MODEL_VOLUME_NAME": "jejueo-models",
            "MODAL_MIN_CONTAINERS": "1",
        }
    )

    assert settings.auth_token == "secret"
    assert settings.model_filename == "alan.gguf"
    assert settings.model_volume_name == "jejueo-models"
    assert settings.modal_min_containers == 1


def test_deploy_validation_errors_require_real_auth_and_model_source() -> None:
    settings = InferenceSettings(auth_token="replace-me")

    errors = settings.deploy_validation_errors()

    assert "INFERENCE_AUTH_TOKEN must be set to a real non-placeholder value" in errors
    assert "Set either MODEL_PATH or MODEL_FILENAME so the model can load" in errors


def test_deploy_validation_errors_require_absolute_volume_mount_path() -> None:
    settings = InferenceSettings(
        auth_token="secret",
        model_filename="alan.gguf",
        model_volume_mount_path="models",
    )

    errors = settings.deploy_validation_errors()

    assert "MODEL_VOLUME_MOUNT_PATH must be an absolute POSIX path" in errors
