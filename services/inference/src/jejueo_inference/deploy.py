from __future__ import annotations

import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

from .settings import InferenceSettings


@dataclass(slots=True)
class DeployReadinessReport:
    settings: InferenceSettings
    errors: list[str]
    warnings: list[str]
    modal_cli_path: str | None

    @property
    def ready(self) -> bool:
        return not self.errors


def classify_model_source(settings: InferenceSettings) -> str:
    if settings.model_path:
        return "model_path"
    if settings.uses_model_volume:
        return "modal_volume"
    return "unset"


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"Invalid env line {line_number}: expected KEY=VALUE")
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def detect_modal_cli() -> str | None:
    cli_path = shutil.which("modal")
    if cli_path:
        return cli_path
    sibling = Path(sys.executable).with_name("modal")
    if sibling.exists():
        return str(sibling)
    return None


def resolve_env_file(path: Path, *, default_path: Path) -> Path | None:
    if path.exists():
        return path
    if path == default_path:
        return None
    raise FileNotFoundError(f"Env file not found: {path}")


def build_deploy_readiness_report(
    *,
    env_file: Path | None = None,
    require_modal_cli: bool = True,
) -> DeployReadinessReport:
    env = dict(os.environ)
    if env_file is not None:
        env.update(parse_env_file(env_file))
    settings = InferenceSettings.from_mapping(env)
    errors = settings.deploy_validation_errors()
    warnings = settings.deploy_validation_warnings()
    modal_cli_path = detect_modal_cli()
    if require_modal_cli and modal_cli_path is None:
        errors.append(
            "modal CLI is not installed or not on PATH; install services/inference[server] in your active Python environment"
        )
    return DeployReadinessReport(
        settings=settings,
        errors=errors,
        warnings=warnings,
        modal_cli_path=modal_cli_path,
    )
