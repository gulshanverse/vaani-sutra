from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any


class MemoryCategory(str, Enum):
    PROFILE = "PROFILE"
    PREFERENCE = "PREFERENCE"
    CONTEXT = "CONTEXT"
    TASK = "TASK"
    OTHER = "OTHER"


class MemoryScope(str, Enum):
    USER = "USER"
    SESSION = "SESSION"


@dataclass(frozen=True)
class MemoryEntry:
    application_id: str
    user_id: str
    key: str
    value: Any
    category: MemoryCategory
    scope: MemoryScope = MemoryScope.USER
    session_id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    expires_at: datetime | None = None

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) >= self.expires_at

    def to_dict(self) -> dict[str, Any]:
        return {
            "application_id": self.application_id,
            "user_id": self.user_id,
            "key": self.key,
            "value": self.value,
            "category": self.category.value,
            "scope": self.scope.value,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }
