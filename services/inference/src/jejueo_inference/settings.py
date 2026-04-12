from __future__ import annotations

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
    def resolved_model_path(self) -> str:
        if self.model_path:
            return self.model_path
        if self.model_filename:
            return str(PurePosixPath(self.model_volume_mount_path) / self.model_filename)
        return ""

    @classmethod
    def from_env(cls) -> "InferenceSettings":
        return cls(
            auth_token=os.getenv("INFERENCE_AUTH_TOKEN", ""),
            model_alias=os.getenv("MODEL_ALIAS", DEFAULT_MODEL_ALIAS),
            model_path=os.getenv("MODEL_PATH", ""),
            model_filename=os.getenv("MODEL_FILENAME", ""),
            model_volume_name=os.getenv("MODEL_VOLUME_NAME", "jejueo-translator-models"),
            model_volume_mount_path=os.getenv("MODEL_VOLUME_MOUNT_PATH", "/models"),
            modal_app_name=os.getenv("MODAL_APP_NAME", "jejueo-translator-inference"),
            modal_secret_name=os.getenv("MODAL_SECRET_NAME", "jejueo-translator-inference"),
            modal_min_containers=int(os.getenv("MODAL_MIN_CONTAINERS", "0")),
            modal_scaledown_window=int(os.getenv("MODAL_SCALEDOWN_WINDOW", "0")),
            n_ctx=int(os.getenv("MODEL_N_CTX", "2048")),
            max_tokens=int(os.getenv("MODEL_MAX_TOKENS", "256")),
            temperature=float(os.getenv("MODEL_TEMPERATURE", "0.4")),
            top_p=float(os.getenv("MODEL_TOP_P", "0.9")),
            repeat_penalty=float(os.getenv("MODEL_REPEAT_PENALTY", "1.1")),
            n_threads=int(os.getenv("MODEL_N_THREADS", "4")),
            n_gpu_layers=int(os.getenv("MODEL_N_GPU_LAYERS", "0")),
        )
