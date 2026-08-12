from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from .models import MemoryCategory, MemoryEntry, MemoryScope
from .policy import MemoryPolicy
from .store import MemoryStore


class MemoryManager:
    def __init__(self, store: MemoryStore, policy: MemoryPolicy | None = None):
        self.store = store
        self.policy = policy or MemoryPolicy()

    def remember(
        self,
        *,
        application_id: str,
        user_id: str,
        key: str,
        value: Any,
        category: MemoryCategory = MemoryCategory.OTHER,
        scope: MemoryScope = MemoryScope.USER,
        session_id: str | None = None,
        ttl_seconds: int | None = None,
    ) -> MemoryEntry | None:
        if not self.policy.allow_memory(key=key, value=value, category=category):
            return None
        if scope == MemoryScope.SESSION and not session_id:
            raise ValueError("session_id is required for session memory")
        expires_at = None
        if ttl_seconds is not None:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        entry = MemoryEntry(
            application_id=application_id,
            user_id=user_id,
            key=key,
            value=value,
            category=category,
            scope=scope,
            session_id=session_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            expires_at=expires_at,
        )
        return self.store.save(entry)

    def recall(
        self,
        *,
        application_id: str,
        user_id: str,
        key: str,
        scope: MemoryScope | None = None,
        session_id: str | None = None,
    ) -> MemoryEntry | None:
        if scope is None and session_id is not None:
            entry = self.store.get(
                application_id=application_id,
                user_id=user_id,
                key=key,
                scope=MemoryScope.SESSION,
                session_id=session_id,
            )
            if entry is None:
                entry = self.store.get(
                    application_id=application_id,
                    user_id=user_id,
                    key=key,
                    scope=MemoryScope.USER,
                )
        else:
            entry = self.store.get(
                application_id=application_id,
                user_id=user_id,
                key=key,
                scope=scope,
                session_id=session_id,
            )
        if entry is None:
            return None
        if entry.is_expired():
            self.store.delete(
                application_id=application_id,
                user_id=user_id,
                key=key,
                scope=entry.scope,
                session_id=entry.session_id,
            )
            return None
        return entry

    def forget(
        self,
        *,
        application_id: str,
        user_id: str,
        key: str,
        scope: MemoryScope | None = None,
        session_id: str | None = None,
    ) -> bool:
        return self.store.delete(
            application_id=application_id,
            user_id=user_id,
            key=key,
            scope=scope,
            session_id=session_id,
        )

    def list_memories(
        self,
        *,
        application_id: str,
        user_id: str,
        scope: MemoryScope | None = None,
        session_id: str | None = None,
        limit: int = 50,
    ) -> list[MemoryEntry]:
        if scope is None and session_id is not None:
            return [
                entry
                for entry in self.store.list(
                    application_id=application_id,
                    user_id=user_id,
                    scope=None,
                    session_id=session_id,
                    limit=limit,
                )
                if not entry.is_expired()
            ]
        return [
            entry
            for entry in self.store.list(
                application_id=application_id,
                user_id=user_id,
                scope=scope,
                session_id=session_id,
                limit=limit,
            )
            if not entry.is_expired()
        ]
