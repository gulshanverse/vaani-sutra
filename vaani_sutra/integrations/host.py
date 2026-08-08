from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class HostApplicationContext:
    application_id: str
    application_name: str
    user_id: str
    locale: str = "en-US"
    preferred_language: str = "en"
    metadata: dict[str, Any] = None
    system_instructions: str | None = None

    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, "metadata", {})
