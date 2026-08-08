from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ToolExecutionStatus(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    NOT_FOUND = "not_found"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class ToolExecutionResult:
    success: bool
    tool: str
    data: Any | None
    error: str | None
    verified: bool
    status: ToolExecutionStatus
    latency_seconds: float | None = None
