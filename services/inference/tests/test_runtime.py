from __future__ import annotations

import sys
from types import ModuleType

from jejueo_inference.runtime import create_fastapi_app, create_modal_app
from jejueo_inference.settings import InferenceSettings


class FakeTranslator:
    def is_ready(self) -> bool:
        return True

    def translate(self, source_lang: str, target_lang: str, source_text: str) -> tuple[str, int]:
        return f"{target_lang}:{source_text}", 8


class FakeFastAPIApp:
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs
        self.mounts: list[tuple[str, object]] = []

    def mount(self, path: str, app: object) -> None:
        self.mounts.append((path, app))


class FakeModalApp:
    def __init__(self, name: str) -> None:
        self.name = name
        self.function_kwargs: dict[str, object] | None = None
        self.decorated_function = None

    def function(self, **kwargs):
        self.function_kwargs = kwargs

        def decorator(fn):
            self.decorated_function = fn
            return fn

        return decorator


class FakeImage:
    def __init__(self) -> None:
        self.packages: list[str] = []
        self.sources: tuple[str, ...] = ()

    def pip_install(self, *packages: str) -> "FakeImage":
        self.packages.extend(packages)
        return self

    def add_local_python_source(self, *sources: str) -> "FakeImage":
        self.sources = sources
        return self


class FakeVolume:
    @staticmethod
    def from_name(name: str, create_if_missing: bool = False) -> tuple[str, str, bool]:
        return ("volume", name, create_if_missing)


class FakeSecret:
    @staticmethod
    def from_name(name: str) -> tuple[str, str]:
        return ("secret", name)


def install_fake_fastapi(monkeypatch) -> None:
    module = ModuleType("fastapi")
    module.FastAPI = FakeFastAPIApp
    monkeypatch.setitem(sys.modules, "fastapi", module)


def install_fake_modal(monkeypatch, fake_apps: list[FakeModalApp]) -> None:
    module = ModuleType("modal")

    class ImageFactory:
        @staticmethod
        def debian_slim(python_version: str = "3.11") -> FakeImage:
            image = FakeImage()
            image.python_version = python_version
            return image

    def app_factory(name: str) -> FakeModalApp:
        app = FakeModalApp(name)
        fake_apps.append(app)
        return app

    def asgi_app():
        def decorator(fn):
            fn._is_modal_asgi = True
            return fn

        return decorator

    module.App = app_factory
    module.Image = ImageFactory
    module.Volume = FakeVolume
    module.Secret = FakeSecret
    module.asgi_app = asgi_app
    monkeypatch.setitem(sys.modules, "modal", module)


def test_create_fastapi_app_requires_fastapi() -> None:
    original = sys.modules.pop("fastapi", None)
    try:
        try:
            create_fastapi_app()
        except RuntimeError as exc:
            assert "FastAPI runtime is not installed" in str(exc)
        else:  # pragma: no cover - defensive
            raise AssertionError("Expected RuntimeError when fastapi is unavailable")
    finally:
        if original is not None:
            sys.modules["fastapi"] = original


def test_create_fastapi_app_mounts_existing_asgi(monkeypatch) -> None:
    install_fake_fastapi(monkeypatch)

    app = create_fastapi_app(
        InferenceSettings(auth_token="secret"),
        translator=FakeTranslator(),
    )

    assert isinstance(app, FakeFastAPIApp)
    assert app.kwargs["title"] == "Jejueo Translator Inference"
    assert app.mounts
    assert app.mounts[0][0] == "/"


def test_create_modal_app_requires_modal() -> None:
    original = sys.modules.pop("modal", None)
    try:
        try:
            create_modal_app()
        except RuntimeError as exc:
            assert "Modal runtime is not installed" in str(exc)
        else:  # pragma: no cover - defensive
            raise AssertionError("Expected RuntimeError when modal is unavailable")
    finally:
        if original is not None:
            sys.modules["modal"] = original


def test_create_modal_app_configures_image_volume_and_secret(monkeypatch) -> None:
    fake_apps: list[FakeModalApp] = []
    install_fake_modal(monkeypatch, fake_apps)

    create_modal_app(
        InferenceSettings(
            model_filename="alan.gguf",
            model_volume_name="jejueo-models",
            model_volume_mount_path="/models",
            modal_app_name="jejueo-inference",
            modal_secret_name="jejueo-secret",
            modal_min_containers=1,
            modal_scaledown_window=300,
        )
    )

    app = fake_apps[0]
    assert app.name == "jejueo-inference"
    assert app.function_kwargs is not None
    assert app.function_kwargs["volumes"] == {
        "/models": ("volume", "jejueo-models", False),
    }
    assert app.function_kwargs["secrets"] == [("secret", "jejueo-secret")]
    assert app.function_kwargs["min_containers"] == 1
    assert app.function_kwargs["scaledown_window"] == 300
    image = app.function_kwargs["image"]
    assert "fastapi>=0.116.0" in image.packages
    assert image.sources == ("jejueo_inference", "jejueo_shared")
