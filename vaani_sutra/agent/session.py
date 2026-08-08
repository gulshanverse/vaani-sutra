from __future__ import annotations

import dataclasses
import datetime
from typing import Any

from .context import HostApplicationContext


class SessionState(str):
    ACTIVE = "active"
    CLOSED = "closed"


@dataclasses.dataclass(frozen=True)
class Session:
    session_id: str
    application_id: str
    user_id: str
    locale: str
    host_context: HostApplicationContext
    created_at: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.utcnow)
    state: str = SessionState.ACTIVE
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)
    available_tools: list[str] = dataclasses.field(default_factory=list)

    def is_active(self) -> bool:
        return self.state == SessionState.ACTIVE

    def close(self) -> None:
        object.__setattr__(self, "state", SessionState.CLOSED)
