from __future__ import annotations

import time
from dataclasses import dataclass
from threading import Lock
from typing import Protocol

from jejueo_shared import ApiError, UPSTREAM_UNAVAILABLE, build_translation_prompt

from .settings import InferenceSettings


class Translator(Protocol):
    def is_ready(self) -> bool: ...

    def translate(self, source_lang: str, target_lang: str, source_text: str) -> tuple[str, int]: ...


class UnavailableTranslator:
    def is_ready(self) -> bool:
        return False

    def translate(self, source_lang: str, target_lang: str, source_text: str) -> tuple[str, int]:
        raise ApiError(503, UPSTREAM_UNAVAILABLE, "Translation service unavailable")


@dataclass(slots=True)
class LlamaCppTranslator:
    settings: InferenceSettings

    def __post_init__(self) -> None:
        self._llm = None
        self._load_error: Exception | None = None
        self._lock = Lock()

    def _load_model(self) -> None:
        if self._llm is not None or self._load_error is not None:
            return
        model_path = self.settings.resolved_model_path
        if not model_path:
            self._load_error = RuntimeError("MODEL_PATH is not configured")
            return
        try:
            from llama_cpp import Llama
        except ImportError as exc:
            self._load_error = exc
            return

        try:
            self._llm = Llama(
                model_path=model_path,
                n_ctx=self.settings.n_ctx,
                n_threads=self.settings.n_threads,
                n_gpu_layers=self.settings.n_gpu_layers,
                verbose=False,
            )
        except Exception as exc:  # pragma: no cover - depends on local model/runtime state
            self._load_error = exc

    def is_ready(self) -> bool:
        with self._lock:
            self._load_model()
            return self._llm is not None

    def translate(self, source_lang: str, target_lang: str, source_text: str) -> tuple[str, int]:
        with self._lock:
            self._load_model()
            if self._llm is None:
                raise ApiError(503, UPSTREAM_UNAVAILABLE, "Translation service unavailable")
            prompt = build_translation_prompt(source_lang, target_lang, source_text)
            started = time.perf_counter()
            result = self._llm.create_completion(
                prompt=prompt,
                temperature=self.settings.temperature,
                top_p=self.settings.top_p,
                repeat_penalty=self.settings.repeat_penalty,
                max_tokens=self.settings.max_tokens,
                stop=["</s>", "\n\nSource ("],
            )
        latency_ms = round((time.perf_counter() - started) * 1000)
        translation = result["choices"][0]["text"].strip()
        return translation, latency_ms


def build_default_translator(settings: InferenceSettings) -> Translator:
    if not settings.resolved_model_path:
        return UnavailableTranslator()
    return LlamaCppTranslator(settings)
