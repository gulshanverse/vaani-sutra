import uuid

from vaani_sutra.agent.context import HostApplicationContext
from vaani_sutra.agent.runtime import AgentRuntime
from vaani_sutra.tools.builtin.calculator import CalculatorTool
from vaani_sutra.tools.builtin.datetime_tool import DateTimeTool
from vaani_sutra.tools.registry import ToolRegistry
from vaani_sutra.tools.executor import ToolExecutor


def test_fake_rail_yatra_application_flow():
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(DateTimeTool())
    executor = ToolExecutor(registry)
    runtime = AgentRuntime(registry, executor)

    host_context = HostApplicationContext(
        application_id="rail-yatra",
        application_name="RailYatra",
        user_id="passenger_001",
        locale="en-IN",
    )
    session_id = str(uuid.uuid4())
    runtime.create_session(session_id, host_context)

    tool_result = runtime.invoke_tool(session_id, "calculator", {"expression": "18 * 12"})
    assert tool_result.success
    assert tool_result.data == 216.0

    dt_result = runtime.invoke_tool(session_id, "datetime", {})
    assert dt_result.success
    assert dt_result.data["timezone"] == "UTC"
    assert dt_result.verified
