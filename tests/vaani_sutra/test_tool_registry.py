import pytest

from vaani_sutra.tools.registry import ToolRegistry
from vaani_sutra.tools.builtin.calculator import CalculatorTool
from vaani_sutra.tools.builtin.datetime_tool import DateTimeTool
from vaani_sutra.tools.builtin.domain_lookup import DomainLookupTool


def test_register_and_get_tool():
    registry = ToolRegistry()
    tool = CalculatorTool()

    registry.register(tool)
    assert registry.get("calculator") is tool


def test_duplicate_registration_raises():
    registry = ToolRegistry()
    tool = CalculatorTool()

    registry.register(tool)
    with pytest.raises(ValueError, match="Tool already registered"):
        registry.register(tool)


def test_unregister_tool():
    registry = ToolRegistry()
    tool = CalculatorTool()
    registry.register(tool)

    registry.unregister("calculator")
    with pytest.raises(KeyError):
        registry.get("calculator")


def test_list_tool_names():
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    assert registry.list_tool_names() == ["calculator"]


def test_schema_returns_metadata():
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    schema = registry.schema("calculator")

    assert schema["name"] == "calculator"
    assert schema["input_schema"]["expression"]["type"] == "string"
