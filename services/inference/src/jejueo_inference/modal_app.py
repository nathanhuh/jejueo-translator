from __future__ import annotations

from .runtime import create_modal_app

try:
    app = create_modal_app()
except RuntimeError:
    app = None
