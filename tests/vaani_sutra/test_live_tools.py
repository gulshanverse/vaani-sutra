import json
from types import SimpleNamespace

from vaani_sutra.tools.builtin.weather import WeatherTool
from vaani_sutra.tools.builtin.web_search import WebSearchTool
from vaani_sutra.tools.providers.geocoding import LocationAmbiguityError, LocationNotFoundError, LocationResult
from vaani_sutra.tools.providers.weather import OpenMeteoWeatherProvider
from vaani_sutra.tools.providers.web_search import NotConfiguredWebSearchProvider, WebSearchResult


class SuccessfulWeatherProvider:
    def get_current_weather(self, *, location=None, latitude=None, longitude=None):
        return {
            "success": True,
            "verified": True,
            "status": "SUCCESS",
            "location": location or "Bilaspur, Chhattisgarh",
            "latitude": latitude,
            "longitude": longitude,
            "temperature_c": 28.4,
            "apparent_temperature_c": 30.1,
            "precipitation_mm": 0.0,
            "wind_speed_kmh": 8.2,
            "condition": "Partly cloudy",
            "observed_at": "2026-08-12T10:00:00Z",
            "timezone": "Asia/Kolkata",
            "source": "Open-Meteo",
        }


class MissingWeatherProvider:
    def get_current_weather(self, *, location=None, latitude=None, longitude=None):
        raise LocationNotFoundError("Location is required")


class AmbiguousWeatherProvider:
    def get_current_weather(self, *, location=None, latitude=None, longitude=None):
        raise LocationAmbiguityError("Ambiguous location 'Springfield'")


class MalformedWeatherProvider:
    def get_current_weather(self, *, location=None, latitude=None, longitude=None):
        raise ValueError("Malformed provider response")


class DummySearchProvider:
    name = "dummy"

    def __init__(self, *, configured=True, should_fail=False):
        self._configured = configured
        self._should_fail = should_fail

    def is_configured(self):
        return self._configured

    def search(self, query, *, limit=5):
        if self._should_fail:
            raise RuntimeError("Search provider unavailable")
        return WebSearchResult(
            success=True,
            verified=True,
            status="SUCCESS",
            query=query,
            results=[{"title": "AI News", "snippet": "Latest update", "url": "https://example.com"}],
            provider=self.name,
        ).to_dict()

    def health_check(self):
        return self._configured


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def read(self):
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeRequest:
    def __init__(self, url, headers=None):
        self.full_url = url
        self.headers = headers or {}


def test_weather_tool_returns_verified_live_payload():
    tool = WeatherTool(provider=SuccessfulWeatherProvider())
    result = tool.execute({"location": "Bilaspur, Chhattisgarh"})

    assert result["success"] is True
    assert result["verified"] is True
    assert result["source"] == "Open-Meteo"
    assert result["temperature_c"] == 28.4


def test_weather_tool_reports_missing_and_ambiguous_locations():
    missing_tool = WeatherTool(provider=MissingWeatherProvider())
    missing_result = missing_tool.execute({"location": ""})
    assert missing_result["success"] is False
    assert missing_result["verified"] is False
    assert missing_result["status"] == "NOT_FOUND"

    ambiguous_tool = WeatherTool(provider=AmbiguousWeatherProvider())
    ambiguous_result = ambiguous_tool.execute({"location": "Springfield"})
    assert ambiguous_result["success"] is False
    assert ambiguous_result["verified"] is False
    assert ambiguous_result["status"] == "AMBIGUOUS_LOCATION"


def test_weather_tool_reports_malformed_provider_response():
    tool = WeatherTool(provider=MalformedWeatherProvider())
    result = tool.execute({"location": "Bilaspur"})
    assert result["success"] is False
    assert result["verified"] is False
    assert result["status"] == "FAILURE"


def test_open_meteo_weather_provider_integration(monkeypatch):
    geocoding_payload = {
        "results": [
            {
                "name": "Bilaspur",
                "latitude": 22.0797,
                "longitude": 82.1391,
                "timezone": "Asia/Kolkata",
                "country": "India",
                "admin1": "Chhattisgarh",
            }
        ]
    }
    weather_payload = {
        "timezone": "Asia/Kolkata",
        "current": {
            "time": "2026-08-12T10:00",
            "temperature_2m": 28.4,
            "apparent_temperature": 30.1,
            "precipitation": 0.0,
            "wind_speed_10m": 8.2,
            "weather_code": 2,
        },
    }

    def fake_urlopen(request_obj, timeout=0):
        url = getattr(request_obj, "full_url", str(request_obj))
        if "geocoding-api.open-meteo.com" in url:
            return FakeResponse(geocoding_payload)
        if "api.open-meteo.com" in url:
            return FakeResponse(weather_payload)
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr("vaani_sutra.tools.providers.geocoding.request.urlopen", fake_urlopen)
    monkeypatch.setattr("vaani_sutra.tools.providers.weather.request.urlopen", fake_urlopen)

    provider = OpenMeteoWeatherProvider()
    result = provider.get_current_weather(location="Bilaspur, Chhattisgarh")

    assert result["success"] is True
    assert result["verified"] is True
    assert result["temperature_c"] == 28.4
    assert result["condition"] == "Partly cloudy"
    assert result["source"] == "Open-Meteo"


def test_web_search_tool_reports_unconfigured_provider():
    tool = WebSearchTool(provider=NotConfiguredWebSearchProvider())
    result = tool.execute({"query": "AI news"})
    assert result["success"] is False
    assert result["verified"] is False
    assert result["status"] == "NOT_CONFIGURED"


def test_web_search_tool_uses_configured_provider_result():
    provider = DummySearchProvider()
    tool = WebSearchTool(provider=provider)
    result = tool.execute({"query": "AI news"})
    assert result["success"] is True
    assert result["verified"] is True
    assert result["results"][0]["title"] == "AI News"


def test_web_search_tool_reports_failure_when_provider_raises():
    provider = DummySearchProvider(should_fail=True)
    tool = WebSearchTool(provider=provider)
    result = tool.execute({"query": "AI news"})
    assert result["success"] is False
    assert result["verified"] is False
    assert result["status"] == "FAILURE"
