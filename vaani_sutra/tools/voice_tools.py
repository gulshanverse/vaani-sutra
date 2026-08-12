from __future__ import annotations

from typing import Any

from videosdk.agents import function_tool

from .executor import ToolExecutor


def _tool_payload(result) -> Any:
    if result.success:
        return result.data
    if isinstance(result.data, dict):
        return result.data
    return {
        "success": False,
        "verified": False,
        "status": getattr(result.status, "value", str(result.status)),
        "error": result.error,
    }


def build_voice_tools(executor: ToolExecutor) -> list[Any]:
    @function_tool(name="calculator")
    async def calculator(expression: str) -> Any:
        return _tool_payload(executor.execute("calculator", {"expression": expression}))

    @function_tool(name="datetime")
    async def datetime_tool(timezone: str | None = None, location: str | None = None) -> Any:
        arguments: dict[str, Any] = {}
        if timezone is not None:
            arguments["timezone"] = timezone
        if location is not None:
            arguments["location"] = location
        return _tool_payload(executor.execute("datetime", arguments))

    @function_tool(name="domain_lookup")
    async def domain_lookup(domain: str) -> Any:
        return _tool_payload(executor.execute("domain_lookup", {"domain": domain}))

    @function_tool(name="weather")
    async def weather(location: str | None = None, latitude: float | None = None, longitude: float | None = None) -> Any:
        arguments: dict[str, Any] = {}
        if location is not None:
            arguments["location"] = location
        if latitude is not None:
            arguments["latitude"] = latitude
        if longitude is not None:
            arguments["longitude"] = longitude
        return _tool_payload(executor.execute("weather", arguments))

    @function_tool(name="web_search")
    async def web_search(query: str, limit: int | None = None) -> Any:
        arguments: dict[str, Any] = {"query": query}
        if limit is not None:
            arguments["limit"] = limit
        return _tool_payload(executor.execute("web_search", arguments))

    @function_tool(name="remember")
    async def remember(
        application_id: str,
        user_id: str,
        key: str,
        value: str,
        category: str | None = None,
        scope: str | None = None,
        session_id: str | None = None,
        ttl_seconds: int | None = None,
    ) -> Any:
        arguments: dict[str, Any] = {
            "application_id": application_id,
            "user_id": user_id,
            "key": key,
            "value": value,
        }
        if category is not None:
            arguments["category"] = category
        if scope is not None:
            arguments["scope"] = scope
        if session_id is not None:
            arguments["session_id"] = session_id
        if ttl_seconds is not None:
            arguments["ttl_seconds"] = ttl_seconds
        return _tool_payload(executor.execute("remember", arguments))

    @function_tool(name="recall")
    async def recall(
        application_id: str,
        user_id: str,
        key: str,
        scope: str | None = None,
        session_id: str | None = None,
    ) -> Any:
        arguments: dict[str, Any] = {
            "application_id": application_id,
            "user_id": user_id,
            "key": key,
        }
        if scope is not None:
            arguments["scope"] = scope
        if session_id is not None:
            arguments["session_id"] = session_id
        return _tool_payload(executor.execute("recall", arguments))

    @function_tool(name="forget")
    async def forget(
        application_id: str,
        user_id: str,
        key: str,
        scope: str | None = None,
        session_id: str | None = None,
    ) -> Any:
        arguments: dict[str, Any] = {
            "application_id": application_id,
            "user_id": user_id,
            "key": key,
        }
        if scope is not None:
            arguments["scope"] = scope
        if session_id is not None:
            arguments["session_id"] = session_id
        return _tool_payload(executor.execute("forget", arguments))

    @function_tool(name="list_memories")
    async def list_memories(
        application_id: str,
        user_id: str,
        scope: str | None = None,
        session_id: str | None = None,
        limit: int | None = None,
    ) -> Any:
        arguments: dict[str, Any] = {
            "application_id": application_id,
            "user_id": user_id,
        }
        if scope is not None:
            arguments["scope"] = scope
        if session_id is not None:
            arguments["session_id"] = session_id
        if limit is not None:
            arguments["limit"] = limit
        return _tool_payload(executor.execute("list_memories", arguments))

    return [
        calculator,
        datetime_tool,
        domain_lookup,
        weather,
        web_search,
        remember,
        recall,
        forget,
        list_memories,
    ]