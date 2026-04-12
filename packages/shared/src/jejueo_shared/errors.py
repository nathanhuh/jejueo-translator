from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ApiError(Exception):
    status_code: int
    error: str
    message: str

    def __str__(self) -> str:
        return f"{self.status_code} {self.error}: {self.message}"
