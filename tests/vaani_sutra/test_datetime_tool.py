from datetime import datetime

import pytest

from vaani_sutra.tools.builtin.datetime_tool import DateTimeTool
from vaani_sutra.tools.providers.geocoding import LocationResult


def test_datetime_tool_supports_utc():
    tool = DateTimeTool()
    result = tool.execute({})

    assert result["timezone"] == "UTC"
    assert result["verified"] is True
    assert result["source"] == "system"
    assert result["date"]
    assert result["time"]


def test_datetime_tool_supports_iana_timezone():
    tool = DateTimeTool()
    result = tool.execute({"timezone": "Asia/Kolkata"})

    assert result["timezone"] == "Asia/Kolkata"
    assert result["verified"] is True


def test_datetime_tool_supports_utc_offset():
    tool = DateTimeTool()
    result = tool.execute({"timezone": "+5"})

    assert result["timezone"] == "+5"
    assert result["verified"] is True


def test_datetime_tool_resolves_location_timezone(monkeypatch):
    tool = DateTimeTool()
    monkeypatch.setattr(
        tool.geocoding_provider,
        "resolve",
        lambda query, limit=5: [
            LocationResult(
                name="Delhi",
                latitude=28.6139,
                longitude=77.2090,
                timezone="Asia/Kolkata",
                country="India",
                admin1="Delhi",
            )
        ],
    )

    result = tool.execute({"location": "Delhi"})
    assert result["timezone"] == "Asia/Kolkata"
    assert result["verified"] is True


def test_datetime_tool_invalid_timezone_raises():
    tool = DateTimeTool()
    with pytest.raises(ValueError):
        tool.execute({"timezone": "Not/A_Timezone"})
