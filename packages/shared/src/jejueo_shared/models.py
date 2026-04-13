from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from .constants import DEFAULT_MODEL_ALIAS, INPUT_CHAR_LIMIT, SUPPORTED_LANGS


class TranslationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)

    sourceText: str = Field(min_length=1)
    sourceLang: str
    targetLang: str


class TranslationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    translation: str
    model: str = DEFAULT_MODEL_ALIAS
    latencyMs: int = Field(ge=0)
    requestId: str


class ErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: str
    message: str
    requestId: str


class HealthResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: str
    model: str = DEFAULT_MODEL_ALIAS
    modelLoaded: bool
    requestId: str


def is_supported_lang(value: str) -> bool:
    return value in SUPPORTED_LANGS
