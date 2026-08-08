from __future__ import annotations

from .agent.runtime import AgentRuntime
from .tools.executor import ToolExecutor
from .tools.registry import ToolRegistry
from .tools.builtin.calculator import CalculatorTool
from .tools.builtin.datetime_tool import DateTimeTool
from .tools.builtin.domain_lookup import DomainLookupTool


class VaaniSutraPlatform:
    """Convenience platform assembler for reusable Vaani Sutra runtimes."""

    def __init__(self) -> None:
        self.registry = ToolRegistry()
        self._register_builtin_tools()
        self.executor = ToolExecutor(self.registry)
        self.runtime = AgentRuntime(self.registry, self.executor)

    def _register_builtin_tools(self) -> None:
        self.registry.register(CalculatorTool())
        self.registry.register(DateTimeTool())
        self.registry.register(DomainLookupTool())

    def get_runtime(self) -> AgentRuntime:
        return self.runtime

    def get_registry(self) -> ToolRegistry:
        return self.registry
