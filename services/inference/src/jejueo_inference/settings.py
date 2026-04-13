from __future__ import annotations

from collections.abc import Mapping
import os
from dataclasses import dataclass
from pathlib import PurePosixPath

from jejueo_shared import DEFAULT_MODEL_ALIAS


@dataclass(slots=True)
class InferenceSettings:
    auth_token: str = ""
    model_alias: str = DEFAULT_MODEL_ALIAS
    model_path: str = ""
    model_filename: str = ""
    model_volume_name: str = "jejueo-translator-models"
    model_volume_mount_path: str = "/models"
    modal_app_name: str = "jejueo-translator-inference"
    modal_secret_name: str = "jejueo-translator-inference"
    modal_min_containers: int = 0
    modal_scaledown_window: int = 0
    n_ctx: int = 2048
    max_tokens: int = 256
    temperature: float = 0.4
    top_p: float = 0.9
    repeat_penalty: float = 1.1
    n_threads: int = 4
    n_gpu_layers: int = 0

    @property
    def uses_model_volume(self) -> bool:
        return not self.model_path and bool(self.model_filename)

    @property
    def resolved_model_path(self) -> str:
        if self.model_path:
            return self.model_path
        if self.model_filename:
            return str(PurePosixPath(self.model_volume_mount_path) / self.model_filename)
        return ""

    @classmethod
    def from_mapping(cls, env: Mapping[str, object]) -> "InferenceSettings":
        return cls(
            auth_token=_env_str(env, "INFERENCE_AUTH_TOKEN", ""),
            model_alias=_env_str(env, "MODEL_ALIAS", DEFAULT_MODEL_ALIAS),
            model_path=_env_str(env, "MODEL_PATH", ""),
            model_filename=_env_str(env, "MODEL_FILENAME", ""),
            model_volume_name=_env_str(env, "MODEL_VOLUME_NAME", "jejueo-translator-models"),
            model_volume_mount_path=_env_str(env, "MODEL_VOLUME_MOUNT_PATH", "/models"),
            modal_app_name=_env_str(env, "MODAL_APP_NAME", "jejueo-translator-inference"),
            modal_secret_name=_env_str(env, "MODAL_SECRET_NAME", "jejueo-translator-inference"),
            modal_min_containers=_env_int(env, "MODAL_MIN_CONTAINERS", "0"),
            modal_scaledown_window=_env_int(env, "MODAL_SCALEDOWN_WINDOW", "0"),
            n_ctx=_env_int(env, "MODEL_N_CTX", "2048"),
            max_tokens=_env_int(env, "MODEL_MAX_TOKENS", "256"),
            temperature=_env_float(env, "MODEL_TEMPERATURE", "0.4"),
            top_p=_env_float(env, "MODEL_TOP_P", "0.9"),
            repeat_penalty=_env_float(env, "MODEL_REPEAT_PENALTY", "1.1"),
            n_threads=_env_int(env, "MODEL_N_THREADS", "4"),
            n_gpu_layers=_env_int(env, "MODEL_N_GPU_LAYERS", "0"),
        )

    @classmethod
    def from_env(cls) -> "InferenceSettings":
        return cls.from_mapping(os.environ)

    def deploy_validation_errors(self) -> list[str]:
        errors: list[str] = []
        if not self.auth_token.strip() or self.auth_token.strip() == "replace-me":
            errors.append("INFERENCE_AUTH_TOKEN must be set to a real non-placeholder value")
        if not self.model_path and not self.model_filename:
            errors.append("Set either MODEL_PATH or MODEL_FILENAME so the model can load")
        if self.uses_model_volume:
            if not self.model_volume_name.strip():
                errors.append("MODEL_VOLUME_NAME must be set when using MODEL_FILENAME")
            mount_path = self.model_volume_mount_path.strip()
            if not mount_path:
                errors.append("MODEL_VOLUME_MOUNT_PATH must be set when using MODEL_FILENAME")
            elif not mount_path.startswith("/"):
                errors.append("MODEL_VOLUME_MOUNT_PATH must be an absolute POSIX path")
        if self.modal_min_containers < 0:
            errors.append("MODAL_MIN_CONTAINERS must be >= 0")
        if self.modal_scaledown_window < 0:
            errors.append("MODAL_SCALEDOWN_WINDOW must be >= 0")
        return errors

    def deploy_validation_warnings(self) -> list[str]:
        warnings: list[str] = []
        if self.model_path and self.model_filename:
            warnings.append("MODEL_PATH is set, so MODEL_FILENAME and Modal Volume settings are ignored")
        if self.modal_min_containers == 0:
            warnings.append("MODAL_MIN_CONTAINERS=0 allows cold starts during demos")
        if self.uses_model_volume and not self.model_filename.endswith(".gguf"):
            warnings.append("MODEL_FILENAME does not end with .gguf; verify the deployed artifact name")
        return warnings


def _env_str(env: Mapping[str, object], key: str, default: str) -> str:
    value = env.get(key, default)
    if value is None:
        return default
    if isinstance(value, str):
        return value
    return str(value)


def _env_int(env: Mapping[str, object], key: str, default: str) -> int:
    return int(_env_str(env, key, default))


def _env_float(env: Mapping[str, object], key: str, default: str) -> float:
    return float(_env_str(env, key, default))
