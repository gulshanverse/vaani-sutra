from __future__ import annotations

from typing import Any

from ..base import Tool, ToolInputSchema, ToolMetadata
from ..providers.weather import OpenMeteoWeatherProvider, WeatherProvider
from ..providers.geocoding import LocationAmbiguityError, LocationNotFoundError


class WeatherTool(Tool):
    def __init__(self, provider: WeatherProvider | None = None):
        self.provider = provider or OpenMeteoWeatherProvider()
        metadata = ToolMetadata(
            name="weather",
            description="Gets current weather for a resolved location using live Open-Meteo data.",
            timeout_seconds=6.0,
            risk_level="READ_ONLY",
            requires_confirmation=False,
        )
        input_schema = {
            "location": ToolInputSchema(type="string", description="Location name such as Bilaspur, Chhattisgarh.", required=False),
            "latitude": ToolInputSchema(type="string", description="Latitude when already known.", required=False),
            "longitude": ToolInputSchema(type="string", description="Longitude when already known.", required=False),
        }
        super().__init__(metadata=metadata, input_schema=input_schema)

    def execute(self, arguments: dict[str, Any]) -> Any:
        try:
            latitude = arguments.get("latitude")
            longitude = arguments.get("longitude")
            return self.provider.get_current_weather(
                location=arguments.get("location"),
                latitude=float(latitude) if latitude not in (None, "") else None,
                longitude=float(longitude) if longitude not in (None, "") else None,
            )
        except LocationAmbiguityError as exc:
            return {"success": False, "verified": False, "status": "AMBIGUOUS_LOCATION", "error": str(exc)}
        except LocationNotFoundError as exc:
            return {"success": False, "verified": False, "status": "NOT_FOUND", "error": str(exc)}
        except Exception as exc:
            return {"success": False, "verified": False, "status": "FAILURE", "error": str(exc)}