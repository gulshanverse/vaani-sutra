from __future__ import annotations

import datetime
import zoneinfo
from typing import Any

from ..base import Tool, ToolInputSchema, ToolMetadata
from ..providers.geocoding import LocationAmbiguityError, LocationNotFoundError, OpenMeteoGeocodingProvider


class DateTimeTool(Tool):
    def __init__(self):
        self.geocoding_provider = OpenMeteoGeocodingProvider()
        metadata = ToolMetadata(
            name="datetime",
            description="Provides the current date and time in UTC, a requested timezone, or a resolved location timezone.",
            timeout_seconds=2.0,
            risk_level="READ_ONLY",
            requires_confirmation=False,
        )
        input_schema = {
            "timezone": ToolInputSchema(
                type="string",
                description="Optional IANA timezone name or UTC offset like ‘UTC’ or ‘+5’.",
                required=False,
            ),
            "location": ToolInputSchema(
                type="string",
                description="Optional location name such as Delhi or Tokyo to resolve a timezone.",
                required=False,
            ),
        }
        super().__init__(metadata=metadata, input_schema=input_schema)

    def execute(self, arguments: dict[str, Any]) -> Any:
        timezone_name = arguments.get("timezone")
        location_name = arguments.get("location")
        now = datetime.datetime.now(datetime.timezone.utc)
        if not timezone_name and not location_name:
            return {
                "date": now.date().isoformat(),
                "time": now.time().isoformat(),
                "timezone": "UTC",
                "verified": True,
                "source": "system",
            }

        if location_name and not timezone_name:
            candidates = self.geocoding_provider.resolve(location_name)
            if not candidates:
                raise LocationNotFoundError(f"Could not resolve timezone for location: {location_name}")
            if len(candidates) > 1:
                labels = [candidate.label() for candidate in candidates[:5]]
                raise LocationAmbiguityError(
                    f"Ambiguous location '{location_name}'. Candidates: {', '.join(labels)}"
                )
            timezone_name = candidates[0].timezone or "UTC"

        timezone_name = str(timezone_name).strip()
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
            "verified": True,
            "source": "system",
        }
