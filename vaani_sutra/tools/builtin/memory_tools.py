from __future__ import annotations

from typing import Any

from ...memory.manager import MemoryManager
from ...memory.models import MemoryCategory, MemoryScope
from ..base import Tool, ToolInputSchema, ToolMetadata


def _parse_category(value: str | None) -> MemoryCategory:
    if not value:
        return MemoryCategory.OTHER
    try:
        return MemoryCategory(value.upper())
    except Exception as exc:
        raise ValueError(f"Unknown memory category: {value}") from exc


def _parse_scope(value: str | None) -> MemoryScope:
    if not value:
        return MemoryScope.USER
    try:
        return MemoryScope(value.upper())
    except Exception as exc:
        raise ValueError(f"Unknown memory scope: {value}") from exc


class RememberTool(Tool):
    def __init__(self, manager: MemoryManager):
        self.manager = manager
        metadata = ToolMetadata(
            name="remember",
            description="Stores an explicit memory for the current application and user when the user asks to remember something.",
            timeout_seconds=2.0,
            risk_level="READ_ONLY",
            requires_confirmation=False,
        )
        input_schema = {
            "application_id": ToolInputSchema(type="string", description="Application scope.", required=True),
            "user_id": ToolInputSchema(type="string", description="User scope.", required=True),
            "key": ToolInputSchema(type="string", description="Memory key.", required=True),
            "value": ToolInputSchema(type="string", description="Memory value.", required=True),
            "category": ToolInputSchema(type="string", description="Memory category.", required=False),
            "scope": ToolInputSchema(type="string", description="Memory scope: USER or SESSION.", required=False),
            "session_id": ToolInputSchema(type="string", description="Optional session identifier.", required=False),
            "ttl_seconds": ToolInputSchema(type="string", description="Optional expiration in seconds.", required=False),
        }
        super().__init__(metadata=metadata, input_schema=input_schema)

    def execute(self, arguments: dict[str, Any]) -> Any:
        category = _parse_category(arguments.get("category"))
        scope = _parse_scope(arguments.get("scope"))
        ttl_seconds = arguments.get("ttl_seconds")
        ttl_value = int(ttl_seconds) if ttl_seconds not in (None, "") else None
        entry = self.manager.remember(
            application_id=arguments["application_id"],
            user_id=arguments["user_id"],
            key=arguments["key"],
            value=arguments["value"],
            category=category,
            scope=scope,
            session_id=arguments.get("session_id"),
            ttl_seconds=ttl_value,
        )
        if entry is None:
            return {"success": False, "verified": False, "status": "BLOCKED", "error": "Memory policy rejected the request"}
        return {"success": True, "verified": True, "status": "SUCCESS", "memory": entry.to_dict()}


class RecallTool(Tool):
    def __init__(self, manager: MemoryManager):
        self.manager = manager
        metadata = ToolMetadata(
            name="recall",
            description="Recalls a stored memory for the current application and user.",
            timeout_seconds=2.0,
            risk_level="READ_ONLY",
            requires_confirmation=False,
        )
        input_schema = {
            "application_id": ToolInputSchema(type="string", description="Application scope.", required=True),
            "user_id": ToolInputSchema(type="string", description="User scope.", required=True),
            "key": ToolInputSchema(type="string", description="Memory key.", required=True),
            "scope": ToolInputSchema(type="string", description="Memory scope: USER or SESSION.", required=False),
            "session_id": ToolInputSchema(type="string", description="Optional session identifier.", required=False),
        }
        super().__init__(metadata=metadata, input_schema=input_schema)

    def execute(self, arguments: dict[str, Any]) -> Any:
        scope = _parse_scope(arguments.get("scope")) if arguments.get("scope") else None
        entry = self.manager.recall(
            application_id=arguments["application_id"],
            user_id=arguments["user_id"],
            key=arguments["key"],
            scope=scope,
            session_id=arguments.get("session_id"),
        )
        if entry is None:
            return {"success": True, "verified": True, "found": False, "status": "NOT_FOUND", "value": None}
        return {"success": True, "verified": True, "found": True, "status": "SUCCESS", "value": entry.value, "memory": entry.to_dict()}


class ForgetTool(Tool):
    def __init__(self, manager: MemoryManager):
        self.manager = manager
        metadata = ToolMetadata(
            name="forget",
            description="Deletes a stored memory for the current application and user.",
            timeout_seconds=2.0,
            risk_level="READ_ONLY",
            requires_confirmation=False,
        )
        input_schema = {
            "application_id": ToolInputSchema(type="string", description="Application scope.", required=True),
            "user_id": ToolInputSchema(type="string", description="User scope.", required=True),
            "key": ToolInputSchema(type="string", description="Memory key.", required=True),
            "scope": ToolInputSchema(type="string", description="Memory scope: USER or SESSION.", required=False),
            "session_id": ToolInputSchema(type="string", description="Optional session identifier.", required=False),
        }
        super().__init__(metadata=metadata, input_schema=input_schema)

    def execute(self, arguments: dict[str, Any]) -> Any:
        scope = _parse_scope(arguments.get("scope")) if arguments.get("scope") else None
        removed = self.manager.forget(
            application_id=arguments["application_id"],
            user_id=arguments["user_id"],
            key=arguments["key"],
            scope=scope,
            session_id=arguments.get("session_id"),
        )
        return {"success": True, "verified": True, "removed": removed, "status": "SUCCESS"}


class ListMemoriesTool(Tool):
    def __init__(self, manager: MemoryManager):
        self.manager = manager
        metadata = ToolMetadata(
            name="list_memories",
            description="Lists stored memories for the current application and user.",
            timeout_seconds=2.0,
            risk_level="READ_ONLY",
            requires_confirmation=False,
        )
        input_schema = {
            "application_id": ToolInputSchema(type="string", description="Application scope.", required=True),
            "user_id": ToolInputSchema(type="string", description="User scope.", required=True),
            "scope": ToolInputSchema(type="string", description="Memory scope: USER or SESSION.", required=False),
            "session_id": ToolInputSchema(type="string", description="Optional session identifier.", required=False),
            "limit": ToolInputSchema(type="string", description="Maximum items to return.", required=False),
        }
        super().__init__(metadata=metadata, input_schema=input_schema)

    def execute(self, arguments: dict[str, Any]) -> Any:
        scope = _parse_scope(arguments.get("scope")) if arguments.get("scope") else None
        limit_value = int(arguments.get("limit") or 50)
        entries = self.manager.list_memories(
            application_id=arguments["application_id"],
            user_id=arguments["user_id"],
            scope=scope,
            session_id=arguments.get("session_id"),
            limit=limit_value,
        )
        return {"success": True, "verified": True, "status": "SUCCESS", "items": [entry.to_dict() for entry in entries]}