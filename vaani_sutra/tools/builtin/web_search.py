from __future__ import annotations

from typing import Any

from ..base import Tool, ToolInputSchema, ToolMetadata
from ..providers.web_search import WebSearchProvider, build_web_search_provider_from_env, NotConfiguredWebSearchProvider


class WebSearchTool(Tool):
    def __init__(self, provider: WebSearchProvider | None = None):
        self.provider = provider or build_web_search_provider_from_env()
        metadata = ToolMetadata(
            name="web_search",
            description="Performs current-information web search using a configured external provider.",
            timeout_seconds=6.0,
            risk_level="READ_ONLY",
            requires_confirmation=False,
        )
        input_schema = {
            "query": ToolInputSchema(type="string", description="Search query.", required=True),
            "limit": ToolInputSchema(type="string", description="Maximum results to return.", required=False),
        }
        super().__init__(metadata=metadata, input_schema=input_schema)

    def execute(self, arguments: dict[str, Any]) -> Any:
        query = arguments.get("query")
        if not isinstance(query, str) or not query.strip():
            return {"success": False, "verified": False, "status": "FAILURE", "error": "query is required"}

        limit_value = int(arguments.get("limit") or 5)
        is_configured = getattr(self.provider, "is_configured", lambda: True)
        if isinstance(self.provider, NotConfiguredWebSearchProvider) or not is_configured():
            return self.provider.search(query, limit=limit_value)

        try:
            return self.provider.search(query, limit=limit_value)
        except Exception as exc:
            return {"success": False, "verified": False, "status": "FAILURE", "error": str(exc), "provider": getattr(self.provider, "name", "unknown")}