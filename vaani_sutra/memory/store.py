from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .base import MemoryStore
from .models import MemoryCategory, MemoryEntry, MemoryScope


class SQLiteMemoryStore(MemoryStore):
    def __init__(self, db_path: str | None = None):
        self.db_path = db_path or str(Path("~/.vaani_sutra/memory.sqlite3").expanduser())
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    application_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    category TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    session_id TEXT,
                    session_key TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    expires_at TEXT,
                    PRIMARY KEY (application_id, user_id, key, scope, session_key)
                )
                """
            )
            conn.commit()

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _serialize_value(self, value: Any) -> str:
        if isinstance(value, (str, int, float, bool)) or value is None:
            return json.dumps(value)
        return json.dumps(value)

    def _deserialize_value(self, value: str) -> Any:
        return json.loads(value)

    def save(self, entry: MemoryEntry) -> MemoryEntry:
        now = self._now()
        persisted = MemoryEntry(
            application_id=entry.application_id,
            user_id=entry.user_id,
            key=entry.key,
            value=entry.value,
            category=entry.category,
            scope=entry.scope,
            session_id=entry.session_id,
            created_at=entry.created_at or now,
            updated_at=entry.updated_at or now,
            expires_at=entry.expires_at,
        )
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO memories (
                    application_id, user_id, key, value, category, scope, session_id,
                    session_key, created_at, updated_at, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(application_id, user_id, key, scope, session_key) DO UPDATE SET
                    value=excluded.value,
                    category=excluded.category,
                    scope=excluded.scope,
                    session_id=excluded.session_id,
                    session_key=excluded.session_key,
                    updated_at=excluded.updated_at,
                    expires_at=excluded.expires_at
                """,
                (
                    persisted.application_id,
                    persisted.user_id,
                    persisted.key,
                    self._serialize_value(persisted.value),
                    persisted.category.value,
                    persisted.scope.value,
                    persisted.session_id,
                    persisted.session_id or "",
                    persisted.created_at.isoformat(),
                    persisted.updated_at.isoformat(),
                    persisted.expires_at.isoformat() if persisted.expires_at else None,
                ),
            )
            conn.commit()
        return persisted

    def get(
        self,
        *,
        application_id: str,
        user_id: str,
        key: str,
        scope: MemoryScope | None = None,
        session_id: str | None = None,
    ) -> MemoryEntry | None:
        with sqlite3.connect(self.db_path) as conn:
            if scope is not None:
                row = conn.execute(
                    "SELECT application_id, user_id, key, value, category, scope, session_id, created_at, updated_at, expires_at FROM memories WHERE application_id=? AND user_id=? AND key=? AND scope=? AND session_key=?",
                    (application_id, user_id, key, scope.value, session_id),
                ).fetchone()
            elif session_id is not None:
                row = conn.execute(
                    "SELECT application_id, user_id, key, value, category, scope, session_id, created_at, updated_at, expires_at FROM memories WHERE application_id=? AND user_id=? AND key=? AND ((scope='SESSION' AND session_key=?) OR scope='USER') ORDER BY CASE WHEN scope='SESSION' AND session_key=? THEN 0 ELSE 1 END, updated_at DESC LIMIT 1",
                    (application_id, user_id, key, session_id, session_id),
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT application_id, user_id, key, value, category, scope, session_id, created_at, updated_at, expires_at FROM memories WHERE application_id=? AND user_id=? AND key=? ORDER BY CASE WHEN scope='SESSION' THEN 0 ELSE 1 END, updated_at DESC LIMIT 1",
                    (application_id, user_id, key),
                ).fetchone()
        if not row:
            return None
        return self._row_to_entry(row)

    def update(self, entry: MemoryEntry) -> MemoryEntry:
        return self.save(entry)

    def delete(
        self,
        *,
        application_id: str,
        user_id: str,
        key: str,
        scope: MemoryScope | None = None,
        session_id: str | None = None,
    ) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            if scope is not None:
                cursor = conn.execute(
                    "DELETE FROM memories WHERE application_id=? AND user_id=? AND key=? AND scope=? AND session_key=?",
                    (application_id, user_id, key, scope.value, session_id),
                )
            elif session_id is not None:
                cursor = conn.execute(
                    "DELETE FROM memories WHERE application_id=? AND user_id=? AND key=? AND ((scope='SESSION' AND session_key=?) OR scope='USER')",
                    (application_id, user_id, key, session_id),
                )
            else:
                cursor = conn.execute(
                    "DELETE FROM memories WHERE application_id=? AND user_id=? AND key=?",
                    (application_id, user_id, key),
                )
            conn.commit()
        return cursor.rowcount > 0

    def list(
        self,
        *,
        application_id: str,
        user_id: str,
        scope: MemoryScope | None = None,
        session_id: str | None = None,
        limit: int = 50,
    ) -> list[MemoryEntry]:
        with sqlite3.connect(self.db_path) as conn:
            if scope is not None:
                rows = conn.execute(
                    "SELECT application_id, user_id, key, value, category, scope, session_id, created_at, updated_at, expires_at FROM memories WHERE application_id=? AND user_id=? AND scope=? AND session_key=? ORDER BY updated_at DESC LIMIT ?",
                    (application_id, user_id, scope.value, session_id, limit),
                ).fetchall()
            elif session_id is not None:
                rows = conn.execute(
                    "SELECT application_id, user_id, key, value, category, scope, session_id, created_at, updated_at, expires_at FROM memories WHERE application_id=? AND user_id=? AND (scope='USER' OR (scope='SESSION' AND session_key=?)) ORDER BY CASE WHEN scope='SESSION' AND session_key=? THEN 0 ELSE 1 END, updated_at DESC LIMIT ?",
                    (application_id, user_id, session_id, session_id, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT application_id, user_id, key, value, category, scope, session_id, created_at, updated_at, expires_at FROM memories WHERE application_id=? AND user_id=? ORDER BY updated_at DESC LIMIT ?",
                    (application_id, user_id, limit),
                ).fetchall()
        return [self._row_to_entry(row) for row in rows]

    def _row_to_entry(self, row: tuple[Any, ...]) -> MemoryEntry:
        application_id, user_id, key, value, category, scope, session_id, created_at, updated_at, expires_at = row
        return MemoryEntry(
            application_id=application_id,
            user_id=user_id,
            key=key,
            value=self._deserialize_value(value),
            category=MemoryCategory(category),
            scope=MemoryScope(scope),
            session_id=session_id,
            created_at=datetime.fromisoformat(created_at),
            updated_at=datetime.fromisoformat(updated_at),
            expires_at=datetime.fromisoformat(expires_at) if expires_at else None,
        )
