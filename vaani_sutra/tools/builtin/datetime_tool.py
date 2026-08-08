from __future__ import annotations

import datetime
import zoneinfo
from typing import Any

from ..base import Tool, ToolInputSchema, ToolMetadata


class DateTimeTool(Tool):
    def __init__(self):
        metadata = ToolMetadata(
            name="datetime",
            description="Provides the current date and time in UTC or a requested timezone.",
            timeout_seconds=2.0,
            risk_level="READ_ONLY",
            requires_confirmation=False,
        )
        input_schema = {
            "timezone": ToolInputSchema(
                type="string",
                description="Optional IANA timezone name or UTC offset like ‘UTC’ or ‘+5’.",
                required=False,
            )
        }
        super().__init__(metadata=metadata, input_schema=input_schema)

    def execute(self, arguments: dict[str, Any]) -> Any:
        timezone_name = arguments.get("timezone")
        now = datetime.datetime.now(datetime.timezone.utc)
        if not timezone_name:
            return {
                "date": now.date().isoformat(),
                "time": now.time().isoformat(),
                "timezone": "UTC",
            }

        timezone_name = timezone_name.strip()
        try:
            if timezone_name.upper() == "UTC":
                tz = datetime.timezone.utc
            elif timezone_name.startswith(("+", "-")):
                offset_hours = int(timezone_name)
                tz = datetime.timezone(datetime.timedelta(hours=offset_hours))
            else:
                tz = zoneinfo.ZoneInfo(timezone_name)
        except Exception as exc:
            raise ValueError(
                "Timezone must be an IANA name like 'Asia/Kolkata' or an offset like '+5'."
            ) from exc

        localized = now.astimezone(tz)
        return {
            "date": localized.date().isoformat(),
            "time": localized.time().isoformat(),
            "timezone": timezone_name,
        }
