from __future__ import annotations

from abc import ABC, abstractmethod

from .models import MemoryEntry, MemoryScope


class MemoryStore(ABC):
    @abstractmethod
    def save(self, entry: MemoryEntry) -> MemoryEntry:
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        *,
        application_id: str,
        user_id: str,
        key: str,
        scope: MemoryScope | None = None,
        session_id: str | None = None,
    ) -> MemoryEntry | None:
        raise NotImplementedError

    @abstractmethod
    def update(self, entry: MemoryEntry) -> MemoryEntry:
        raise NotImplementedError

    @abstractmethod
    def delete(
        self,
        *,
        application_id: str,
        user_id: str,
        key: str,
        scope: MemoryScope | None = None,
        session_id: str | None = None,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list(
        self,
        *,
        application_id: str,
        user_id: str,
        scope: MemoryScope | None = None,
        session_id: str | None = None,
        limit: int = 50,
    ) -> list[MemoryEntry]:
        raise NotImplementedError
