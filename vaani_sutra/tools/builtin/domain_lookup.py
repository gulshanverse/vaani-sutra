from __future__ import annotations

from typing import Any

from ..base import Tool, ToolInputSchema, ToolMetadata


class DomainLookupTool(Tool):
    def __init__(self):
        metadata = ToolMetadata(
            name="domain_lookup",
            description="Checks domain availability when a real provider is configured, otherwise returns an unverified status.",
            timeout_seconds=3.0,
            risk_level="READ_ONLY",
            requires_confirmation=False,
        )
        input_schema = {
            "domain": ToolInputSchema(
                type="string",
                description="Domain name to verify, for example example.com.",
                required=True,
            )
        }
        super().__init__(metadata=metadata, input_schema=input_schema)

    def execute(self, arguments: dict[str, Any]) -> Any:
        domain = arguments.get("domain")
        if not isinstance(domain, str) or not domain.strip():
            raise ValueError("domain must be a non-empty string")

        return {
            "domain": domain,
            "status": "UNVERIFIED",
            "details": "No registrar API configured for domain verification.",
        }
