import pytest

from vaani_sutra.tools.builtin.calculator import CalculatorTool
from vaani_sutra.tools.builtin.datetime_tool import DateTimeTool
from vaani_sutra.tools.builtin.domain_lookup import DomainLookupTool
from vaani_sutra.tools.base import Tool, ToolInputSchema, ToolMetadata
from vaani_sutra.tools.executor import ToolExecutor
from vaani_sutra.tools.registry import ToolRegistry
from vaani_sutra.tools.result import ToolExecutionStatus


def test_execute_tool_success():
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    executor = ToolExecutor(registry)

    result = executor.execute("calculator", {"expression": "2 + 2"})
    assert result.success
    assert result.data == 4.0
    assert result.status == ToolExecutionStatus.SUCCESS


def test_execute_datetime_tool():
    registry = ToolRegistry()
    registry.register(DateTimeTool())
    executor = ToolExecutor(registry)

    result = executor.execute("datetime", {})
    assert result.success
    assert result.data["timezone"] == "UTC"


def test_execute_domain_lookup_tool():
    registry = ToolRegistry()
    registry.register(DomainLookupTool())
    executor = ToolExecutor(registry)

    result = executor.execute("domain_lookup", {"domain": "example.com"})
    assert result.success
    assert result.data["status"] == "UNVERIFIED"


def test_execute_tool_not_found():
    registry = ToolRegistry()
    executor = ToolExecutor(registry)

    result = executor.execute("missing", {})
    assert not result.success
    assert result.status == ToolExecutionStatus.NOT_FOUND


def test_execute_tool_invalid_arguments():
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    executor = ToolExecutor(registry)

    result = executor.execute("calculator", {})
    assert not result.success
    assert "Missing required tool arguments" in result.error


def test_execute_tool_timeout(monkeypatch):
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    executor = ToolExecutor(registry)

    class SlowCalculator(CalculatorTool):
        def execute(self, arguments):
            import time

            time.sleep(3)
            return super().execute(arguments)

    registry.unregister("calculator")
    registry.register(SlowCalculator())

    result = executor.execute("calculator", {"expression": "1 + 1"})
    assert not result.success
    assert result.status == ToolExecutionStatus.TIMEOUT


def test_confirmation_required_blocking():
    class ConfirmTool(Tool):
        def __init__(self):
            metadata = ToolMetadata(
                name="confirm_tool",
                description="Test confirmation tool",
                timeout_seconds=2.0,
                risk_level="CONFIRMATION_REQUIRED",
                requires_confirmation=True,
            )
            input_schema = {
                "expression": ToolInputSchema(
                    type="string",
                    description="Expression to evaluate.",
                    required=True,
                )
            }
            super().__init__(metadata=metadata, input_schema=input_schema)

        def execute(self, arguments):
            return "confirmed"

    registry = ToolRegistry()
    registry.register(ConfirmTool())
    executor = ToolExecutor(registry)

    result = executor.execute("confirm_tool", {"expression": "1 + 1"})
    assert not result.success
    assert result.status == ToolExecutionStatus.REQUIRES_CONFIRMATION
