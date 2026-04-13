from __future__ import annotations

from typing import Any

from .asgi import create_app as create_asgi_app
from .settings import InferenceSettings


def _missing_dependency(package_name: str, extra_name: str) -> RuntimeError:
    return RuntimeError(
        f"{package_name} runtime is not installed. Install services/inference[{extra_name}] to use this entrypoint."
    )


def create_fastapi_app(
    settings: InferenceSettings | None = None,
    translator: Any | None = None,
) -> Any:
    try:
        from fastapi import FastAPI
    except ImportError as exc:  # pragma: no cover - exercised via dedicated dependency test
        raise _missing_dependency("FastAPI", "server") from exc

    app = FastAPI(
        title="Jejueo Translator Inference",
        version="0.1.0",
        docs_url="/docs",
        redoc_url=None,
        openapi_url="/openapi.json",
    )
    app.mount("/", create_asgi_app(settings=settings, translator=translator))
    return app


def create_modal_app(settings: InferenceSettings | None = None) -> Any:
    try:
        import modal
    except ImportError as exc:  # pragma: no cover - exercised via dedicated dependency test
        raise _missing_dependency("Modal", "server") from exc

    resolved_settings = settings or InferenceSettings.from_env()
    app = modal.App(resolved_settings.modal_app_name)

    image = modal.Image.debian_slim(python_version="3.11")
    if hasattr(image, "apt_install"):
        image = image.apt_install(
            "build-essential",
            "cmake",
        )
    image = image.pip_install(
        "fastapi>=0.116.0",
        "uvicorn>=0.35.0",
        "modal>=1.0.0",
        "llama-cpp-python>=0.2.90",
        "pydantic>=2.12.0",
    )
    if hasattr(image, "add_local_python_source"):
        image = image.add_local_python_source("jejueo_inference", "jejueo_shared")

    function_kwargs: dict[str, Any] = {"image": image}
    if resolved_settings.uses_model_volume and resolved_settings.model_volume_name:
        volume = modal.Volume.from_name(
            resolved_settings.model_volume_name,
            create_if_missing=False,
        )
        function_kwargs["volumes"] = {
            resolved_settings.model_volume_mount_path: volume,
        }
    if resolved_settings.modal_secret_name and hasattr(modal, "Secret"):
        function_kwargs["secrets"] = [modal.Secret.from_name(resolved_settings.modal_secret_name)]
    if resolved_settings.modal_min_containers > 0:
        function_kwargs["min_containers"] = resolved_settings.modal_min_containers
    if resolved_settings.modal_scaledown_window > 0:
        function_kwargs["scaledown_window"] = resolved_settings.modal_scaledown_window

    @app.function(**function_kwargs)
    @modal.asgi_app()
    def fastapi_app() -> Any:
        return create_fastapi_app(settings=resolved_settings)

    return app
