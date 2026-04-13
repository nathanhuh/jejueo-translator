#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "packages/shared/src"))
sys.path.insert(0, str(REPO_ROOT / "services/inference/src"))

from jejueo_inference.deploy import (  # noqa: E402
    build_deploy_readiness_report,
    classify_model_source,
    resolve_env_file,
)


DEFAULT_ENV_FILE = Path("services/inference/.env")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate that local settings are ready for a real Modal inference deploy."
    )
    parser.add_argument(
        "--env-file",
        default=str(DEFAULT_ENV_FILE),
        help="Path to the env file to validate. Defaults to services/inference/.env if present.",
    )
    parser.add_argument(
        "--allow-missing-modal-cli",
        action="store_true",
        help="Do not fail if the modal CLI is missing from the current environment.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the readiness report as JSON.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    env_file = Path(args.env_file)
    try:
        resolved_env_file = resolve_env_file(env_file, default_path=DEFAULT_ENV_FILE)
    except FileNotFoundError as exc:
        raise SystemExit(str(exc)) from exc
    report = build_deploy_readiness_report(
        env_file=resolved_env_file,
        require_modal_cli=not args.allow_missing_modal_cli,
    )

    payload = {
        "ready": report.ready,
        "envFile": str(resolved_env_file) if resolved_env_file else "",
        "modalCliPath": report.modal_cli_path or "",
        "modelSource": classify_model_source(report.settings),
        "resolvedModelPath": report.settings.resolved_model_path,
        "errors": report.errors,
        "warnings": report.warnings,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"ready={report.ready}")
        print(f"env_file={payload['envFile'] or '(environment only)'}")
        print(f"modal_cli={payload['modalCliPath'] or '(missing)'}")
        print(f"model_source={payload['modelSource']}")
        print(f"resolved_model_path={payload['resolvedModelPath'] or '(unset)'}")
        if report.errors:
            print("errors:")
            for item in report.errors:
                print(f"  - {item}")
        if report.warnings:
            print("warnings:")
            for item in report.warnings:
                print(f"  - {item}")

    return 0 if report.ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
