from __future__ import annotations

import logging
import time
from typing import Any

from .context import HostApplicationContext
from .session import Session
from ..tools.executor import ToolExecutor
from ..tools.registry import ToolRegistry
from ..tools.result import ToolExecutionResult

logger = logging.getLogger(__name__)


class AgentRuntime:
    """Core runtime that binds sessions, host context, and tool execution."""

    def __init__(self, registry: ToolRegistry, executor: ToolExecutor):
        self.registry = registry
        self.executor = executor
        self.sessions: dict[str, Session] = {}

    def create_session(
        self,
        session_id: str,
        host_context: HostApplicationContext,
        metadata: dict[str, Any] | None = None,
    ) -> Session:
        if session_id in self.sessions:
            raise ValueError(f"Session already exists: {session_id}")

        session = Session(
            session_id=session_id,
            application_id=host_context.application_id,
            user_id=host_context.user_id,
            locale=host_context.locale,
            host_context=host_context,
            metadata=metadata or {},
            available_tools=self.registry.list_tool_names(),
        )
        self.sessions[session_id] = session
        logger.info(
            "Created session %s for application %s user %s",
            session_id,
            host_context.application_id,
            host_context.user_id,
        )
        return session

    def get_session(self, session_id: str) -> Session:
        try:
            return self.sessions[session_id]
        except KeyError as exc:
            raise KeyError(f"Session not found: {session_id}") from exc

    def list_sessions(self) -> list[Session]:
        return list(self.sessions.values())

    def invoke_tool(
        self,
        session_id: str,
        tool_name: str,
        arguments: dict[str, Any],
        require_confirmation: bool = False,
    ) -> ToolExecutionResult:
        session = self.get_session(session_id)
        merged_arguments = dict(arguments)
        try:
            tool = self.registry.get(tool_name)
        except KeyError:
            return self.executor.execute(tool_name, merged_arguments)

        if "application_id" in tool.input_schema and "application_id" not in merged_arguments:
            merged_arguments["application_id"] = session.application_id
        if "user_id" in tool.input_schema and "user_id" not in merged_arguments:
            merged_arguments["user_id"] = session.user_id
        if "session_id" in tool.input_schema and "session_id" not in merged_arguments:
            merged_arguments["session_id"] = session.session_id
        if "locale" in tool.input_schema and "locale" not in merged_arguments:
            merged_arguments["locale"] = session.locale
        if require_confirmation:
            logger.warning(
                "Tool invocation requires explicit confirmation: %s",
                tool_name,
            )
            return ToolExecutionResult(
                success=False,
                tool=tool_name,
                data=None,
                error="Confirmation required",
                verified=False,
                status="requires_confirmation",
            )

        logger.info(
            "Session %s invoking tool %s",
            session_id,
            tool_name,
        )
        result = self.executor.execute(tool_name, merged_arguments)
        return result

    def close_session(self, session_id: str) -> None:
        if session_id in self.sessions:
            self.sessions[session_id].close()
            logger.info("Session %s closed", session_id)
        else:
            raise KeyError(f"Session not found: {session_id}")
