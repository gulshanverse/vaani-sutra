from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SessionCreateRequest:
    session_id: str
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


@dataclass(frozen=True)
class MessageCreateRequest:
    session_id: str
    user_id: str
    text: str
    locale: str | None = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, "metadata", {})


@dataclass(frozen=True)
class ToolResultResponse:
    session_id: str
    tool_name: str
    success: bool
    data: Any | None
    error: str | None
    verified: bool
    status: str
    latency_seconds: float | None = None
