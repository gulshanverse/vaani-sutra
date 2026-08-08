import uuid

from vaani_sutra.agent.context import HostApplicationContext
from vaani_sutra.agent.runtime import AgentRuntime
from vaani_sutra.tools.builtin.calculator import CalculatorTool
from vaani_sutra.tools.executor import ToolExecutor
from vaani_sutra.tools.registry import ToolRegistry


def test_session_creation_and_metadata():
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    executor = ToolExecutor(registry)
    runtime = AgentRuntime(registry, executor)

    host_context = HostApplicationContext(
        application_id="rail-yatra",
        application_name="RailYatra",
        user_id="user_123",
        locale="en-IN",
    )
    session_id = str(uuid.uuid4())
    session = runtime.create_session(session_id, host_context, metadata={"flow": "voice"})

    assert session.session_id == session_id
    assert session.application_id == "rail-yatra"
    assert session.user_id == "user_123"
    assert session.locale == "en-IN"
    assert session.metadata["flow"] == "voice"
    assert session.available_tools == ["calculator"]


def test_invoke_tool_routes_to_executor():
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    executor = ToolExecutor(registry)
    runtime = AgentRuntime(registry, executor)

    host_context = HostApplicationContext(
        application_id="rail-yatra",
        application_name="RailYatra",
        user_id="user_123",
    )
    session_id = str(uuid.uuid4())
    runtime.create_session(session_id, host_context)

    result = runtime.invoke_tool(session_id, "calculator", {"expression": "5 * 5"})
    assert result.success
    assert result.data == 25.0


def test_close_session():
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    executor = ToolExecutor(registry)
    runtime = AgentRuntime(registry, executor)

    host_context = HostApplicationContext(
        application_id="rail-yatra",
        application_name="RailYatra",
        user_id="user_123",
    )
    session_id = str(uuid.uuid4())
    runtime.create_session(session_id, host_context)
    runtime.close_session(session_id)

    session = runtime.get_session(session_id)
    assert not session.is_active()
