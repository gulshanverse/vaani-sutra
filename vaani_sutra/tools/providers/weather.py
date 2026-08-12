from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from typing import Protocol
from urllib import parse, request

from .geocoding import (
    GeocodingProvider,
    LocationAmbiguityError,
    LocationNotFoundError,
    LocationResult,
    OpenMeteoGeocodingProvider,
)


WEATHER_CODE_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    80: "Rain showers",
    81: "Rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with heavy hail",
}


class WeatherProvider(Protocol):
    def get_current_weather(
        self,
        *,
        location: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> dict:
        raise NotImplementedError


@dataclass(frozen=True)
class WeatherObservation:
    success: bool
    verified: bool
    status: str
    location: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    temperature_c: float | None = None
    apparent_temperature_c: float | None = None
    precipitation_mm: float | None = None
    wind_speed_kmh: float | None = None
    condition: str | None = None
    observed_at: str | None = None
    timezone: str | None = None
    source: str | None = None
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "verified": self.verified,
            "status": self.status,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "temperature_c": self.temperature_c,
            "apparent_temperature_c": self.apparent_temperature_c,
            "precipitation_mm": self.precipitation_mm,
            "wind_speed_kmh": self.wind_speed_kmh,
            "condition": self.condition,
            "observed_at": self.observed_at,
            "timezone": self.timezone,
            "source": self.source,
            "error": self.error,
        }


class OpenMeteoWeatherProvider:
    def __init__(
        self,
        *,
        geocoding_provider: GeocodingProvider | None = None,
        timeout_seconds: float = 5.0,
    ):
        self.geocoding_provider = geocoding_provider or OpenMeteoGeocodingProvider(timeout_seconds=timeout_seconds)
        self.timeout_seconds = timeout_seconds

    def _resolve_location(self, *, location: str | None, latitude: float | None, longitude: float | None) -> LocationResult:
        if latitude is not None and longitude is not None:
            return LocationResult(name=location or "Requested location", latitude=float(latitude), longitude=float(longitude), timezone="auto")
        if not location:
            raise LocationNotFoundError("Location is required")

        candidates = self.geocoding_provider.resolve(location)
        if not candidates:
            raise LocationNotFoundError(f"Could not resolve location: {location}")
        if len(candidates) > 1:
            labels = [candidate.label() for candidate in candidates[:5]]
            raise LocationAmbiguityError(f"Ambiguous location '{location}'. Candidates: {', '.join(labels)}")
        return candidates[0]

    def get_current_weather(
        self,
        *,
        location: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
    ) -> dict:
        resolved = self._resolve_location(location=location, latitude=latitude, longitude=longitude)
        query_params = parse.urlencode(
            {
                "latitude": resolved.latitude,
                "longitude": resolved.longitude,
                "current": "temperature_2m,apparent_temperature,precipitation,wind_speed_10m,weather_code",
                "timezone": resolved.timezone or "auto",
            }
        )
        url = f"https://api.open-meteo.com/v1/forecast?{query_params}"
        req = request.Request(url, headers={"User-Agent": "VaaniSutra/1.0"})
        with request.urlopen(req, timeout=self.timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))

        current = payload.get("current") or {}
        if not current:
            raise ValueError("Weather service returned no current data")

        observed_at = current.get("time")
        if observed_at and not observed_at.endswith("Z") and "T" in observed_at:
            # keep provider timestamp as-is
            pass

        return WeatherObservation(
            success=True,
            verified=True,
            status="SUCCESS",
            location=resolved.label(),
            latitude=resolved.latitude,
            longitude=resolved.longitude,
            temperature_c=current.get("temperature_2m"),
            apparent_temperature_c=current.get("apparent_temperature"),
            precipitation_mm=current.get("precipitation"),
            wind_speed_kmh=current.get("wind_speed_10m"),
            condition=WEATHER_CODE_MAP.get(int(current.get("weather_code", -1)), "Unknown"),
            observed_at=observed_at,
            timezone=payload.get("timezone") or resolved.timezone or "UTC",
            source="Open-Meteo",
        ).to_dict()