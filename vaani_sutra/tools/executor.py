from __future__ import annotations

import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import Any

from .base import Tool
from .policy import ToolPolicy, ToolRiskLevel
from .result import ToolExecutionResult, ToolExecutionStatus

logger = logging.getLogger(__name__)


class ToolExecutionError(Exception):
    pass


class ToolExecutor:
    def __init__(self, registry: "ToolRegistry"):
        self.registry = registry
        self._executor = ThreadPoolExecutor(max_workers=2)

    def execute(self, tool_name: str, arguments: dict[str, Any], confirmed: bool = False) -> ToolExecutionResult:
        try:
            tool = self.registry.get(tool_name)
        except KeyError:
            return ToolExecutionResult(
                success=False,
                tool=tool_name,
                data=None,
                error="Tool not found",
                verified=False,
                status=ToolExecutionStatus.NOT_FOUND,
                latency_seconds=0.0,
            )

        if not ToolPolicy.is_execution_allowed(ToolRiskLevel(tool.metadata.risk_level), confirmed=confirmed):
            status = ToolExecutionStatus.REQUIRES_CONFIRMATION if tool.metadata.risk_level == ToolRiskLevel.CONFIRMATION_REQUIRED.value else ToolExecutionStatus.FAILURE
            return ToolExecutionResult(
                success=False,
                tool=tool_name,
                data=None,
                error="Execution blocked by policy",
                verified=False,
                status=status,
                latency_seconds=0.0,
            )

        try:
            tool.validate(arguments)
        except Exception as exc:
            return ToolExecutionResult(
                success=False,
                tool=tool_name,
                data=None,
                error=str(exc),
                verified=False,
                status=ToolExecutionStatus.FAILURE,
                latency_seconds=0.0,
            )

        start = time.time()
        future = self._executor.submit(tool.execute, arguments)
        try:
            result = future.result(timeout=tool.metadata.timeout_seconds)
            latency = time.time() - start
            logger.info("Tool %s executed in %.3fs", tool_name, latency)
            return ToolExecutionResult(
                success=True,
                tool=tool_name,
                data=result,
                error=None,
                verified=True,
                status=ToolExecutionStatus.SUCCESS,
                latency_seconds=latency,
            )
        except TimeoutError:
            future.cancel()
            latency = time.time() - start
            logger.warning("Tool %s timed out after %.3fs", tool_name, latency)
            return ToolExecutionResult(
                success=False,
                tool=tool_name,
                data=None,
                error="Tool execution timed out",
                verified=False,
                status=ToolExecutionStatus.TIMEOUT,
                latency_seconds=latency,
            )
        except Exception as exc:
            latency = time.time() - start
            logger.error("Tool %s execution failed: %s", tool_name, exc)
            return ToolExecutionResult(
                success=False,
                tool=tool_name,
                data=None,
                error=str(exc),
                verified=False,
                status=ToolExecutionStatus.FAILURE,
                latency_seconds=latency,
            )
