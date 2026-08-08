from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class ToolInputSchema:
    type: str
    description: str
    required: bool = True


@dataclass(frozen=True)
class ToolMetadata:
    name: str
    description: str
    timeout_seconds: float = 5.0
    risk_level: str = "READ_ONLY"
    requires_confirmation: bool = False


class Tool:
    metadata: ToolMetadata

    def __init__(self, metadata: ToolMetadata, input_schema: dict[str, ToolInputSchema]):
        self.metadata = metadata
        self.input_schema = input_schema

    def validate(self, arguments: dict[str, Any]) -> None:
        missing = [
            name
            for name, schema in self.input_schema.items()
            if schema.required and name not in arguments
        ]
        if missing:
            raise ValueError(f"Missing required tool arguments: {', '.join(missing)}")

        for name, value in arguments.items():
            if name not in self.input_schema:
                raise ValueError(f"Unexpected tool argument: {name}")

    def execute(self, arguments: dict[str, Any]) -> Any:
        raise NotImplementedError("Tool.execute must be implemented by subclasses")
