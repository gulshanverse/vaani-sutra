from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from urllib import parse, request
import json


class LocationAmbiguityError(ValueError):
    pass


class LocationNotFoundError(ValueError):
    pass


@dataclass(frozen=True)
class LocationResult:
    name: str
    latitude: float
    longitude: float
    timezone: str | None = None
    country: str | None = None
    admin1: str | None = None
    feature_code: str | None = None

    def label(self) -> str:
        parts = [self.name]
        if self.admin1:
            parts.append(self.admin1)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)


class GeocodingProvider(Protocol):
    def resolve(self, query: str, *, limit: int = 5) -> list[LocationResult]:
        raise NotImplementedError


class OpenMeteoGeocodingProvider:
    def __init__(self, *, timeout_seconds: float = 5.0):
        self.timeout_seconds = timeout_seconds

    def resolve(self, query: str, *, limit: int = 5) -> list[LocationResult]:
        if not query or not query.strip():
            raise LocationNotFoundError("Location is required")

        params = parse.urlencode({"name": query, "count": limit, "language": "en", "format": "json"})
        url = f"https://geocoding-api.open-meteo.com/v1/search?{params}"
        req = request.Request(url, headers={"User-Agent": "VaaniSutra/1.0"})
        with request.urlopen(req, timeout=self.timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))

        results = payload.get("results") or []
        locations: list[LocationResult] = []
        for item in results:
            locations.append(
                LocationResult(
                    name=str(item.get("name") or query),
                    latitude=float(item["latitude"]),
                    longitude=float(item["longitude"]),
                    timezone=item.get("timezone"),
                    country=item.get("country"),
                    admin1=item.get("admin1"),
                    feature_code=item.get("feature_code"),
                )
            )
        return locations