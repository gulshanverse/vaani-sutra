from __future__ import annotations

import logging
from typing import Any

from .base import Tool

logger = logging.getLogger(__name__)


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.metadata.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.metadata.name}")
        self._tools[tool.metadata.name] = tool
        logger.info("Registered tool %s", tool.metadata.name)

    def unregister(self, tool_name: str) -> None:
        if tool_name not in self._tools:
            raise KeyError(f"Tool not found: {tool_name}")
        del self._tools[tool_name]
        logger.info("Unregistered tool %s", tool_name)

    def get(self, tool_name: str) -> Tool:
        try:
            return self._tools[tool_name]
        except KeyError as exc:
            raise KeyError(f"Tool not found: {tool_name}") from exc

    def list(self) -> list[Tool]:
        return list(self._tools.values())

    def list_tool_names(self) -> list[str]:
        return list(self._tools.keys())

    def schema(self, tool_name: str) -> dict[str, Any]:
        tool = self.get(tool_name)
        return {
            "name": tool.metadata.name,
            "description": tool.metadata.description,
            "timeout_seconds": tool.metadata.timeout_seconds,
            "risk_level": tool.metadata.risk_level,
            "requires_confirmation": tool.metadata.requires_confirmation,
            "input_schema": {
                name: {
                    "type": schema.type,
                    "description": schema.description,
                    "required": schema.required,
                }
                for name, schema in tool.input_schema.items()
            },
        }
