from __future__ import annotations

from .agent.runtime import AgentRuntime
from .memory.manager import MemoryManager
from .memory.store import SQLiteMemoryStore
from .tools.executor import ToolExecutor
from .tools.registry import ToolRegistry
from .tools.builtin.calculator import CalculatorTool
from .tools.builtin.datetime_tool import DateTimeTool
from .tools.builtin.domain_lookup import DomainLookupTool
from .tools.builtin.memory_tools import RememberTool, RecallTool, ForgetTool, ListMemoriesTool
from .tools.builtin.weather import WeatherTool
from .tools.builtin.web_search import WebSearchTool
from .tools.providers.weather import OpenMeteoWeatherProvider
from .tools.providers.web_search import build_web_search_provider_from_env
from .tools.voice_tools import build_voice_tools


class VaaniSutraPlatform:
    """Convenience platform assembler for reusable Vaani Sutra runtimes."""

    def __init__(self) -> None:
        self.memory_store = SQLiteMemoryStore()
        self.memory_manager = MemoryManager(self.memory_store)
        self.weather_provider = OpenMeteoWeatherProvider()
        self.web_search_provider = build_web_search_provider_from_env()
        self.registry = ToolRegistry()
        self._register_builtin_tools()
        self.executor = ToolExecutor(self.registry)
        self.runtime = AgentRuntime(self.registry, self.executor)

    def _register_builtin_tools(self) -> None:
        self.registry.register(CalculatorTool())
        self.registry.register(DateTimeTool())
        self.registry.register(DomainLookupTool())
        self.registry.register(WeatherTool(provider=self.weather_provider))
        self.registry.register(WebSearchTool(provider=self.web_search_provider))
        self.registry.register(RememberTool(manager=self.memory_manager))
        self.registry.register(RecallTool(manager=self.memory_manager))
        self.registry.register(ForgetTool(manager=self.memory_manager))
        self.registry.register(ListMemoriesTool(manager=self.memory_manager))

    def get_runtime(self) -> AgentRuntime:
        return self.runtime

    def get_registry(self) -> ToolRegistry:
        return self.registry

    def get_agent_tools(self):
        return build_voice_tools(self.executor)
