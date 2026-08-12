from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Protocol
from urllib import parse, request


@dataclass(frozen=True)
class SearchResult:
    title: str
    snippet: str | None = None
    url: str | None = None

    def to_dict(self) -> dict:
        return {"title": self.title, "snippet": self.snippet, "url": self.url}


@dataclass(frozen=True)
class WebSearchResult:
    success: bool
    verified: bool
    status: str
    query: str
    results: list[dict]
    provider: str
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "verified": self.verified,
            "status": self.status,
            "query": self.query,
            "results": self.results,
            "provider": self.provider,
            "error": self.error,
        }


class WebSearchProvider(Protocol):
    name: str

    def is_configured(self) -> bool:
        raise NotImplementedError

    def search(self, query: str, *, limit: int = 5) -> dict:
        raise NotImplementedError

    def health_check(self) -> bool:
        raise NotImplementedError


class NotConfiguredWebSearchProvider:
    name = "not_configured"

    def is_configured(self) -> bool:
        return False

    def search(self, query: str, *, limit: int = 5) -> dict:
        return WebSearchResult(
            success=False,
            verified=False,
            status="NOT_CONFIGURED",
            query=query,
            results=[],
            provider=self.name,
            error="Live web search is not configured",
        ).to_dict()

    def health_check(self) -> bool:
        return False


class BraveWebSearchProvider:
    name = "brave"

    def __init__(self, api_key: str, *, endpoint: str | None = None, timeout_seconds: float = 5.0):
        self.api_key = api_key
        self.endpoint = endpoint or "https://api.search.brave.com/res/v1/web/search"
        self.timeout_seconds = timeout_seconds

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def search(self, query: str, *, limit: int = 5) -> dict:
        params = parse.urlencode({"q": query, "count": limit, "search_lang": "en"})
        url = f"{self.endpoint}?{params}"
        req = request.Request(
            url,
            headers={
                "Accept": "application/json",
                "X-Subscription-Token": self.api_key,
                "User-Agent": "VaaniSutra/1.0",
            },
        )
        with request.urlopen(req, timeout=self.timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))

        results: list[dict] = []
        for item in (payload.get("web", {}) or {}).get("results", [])[:limit]:
            results.append(
                SearchResult(
                    title=str(item.get("title") or "Untitled result"),
                    snippet=item.get("description"),
                    url=item.get("url"),
                ).to_dict()
            )

        return WebSearchResult(
            success=True,
            verified=True,
            status="SUCCESS",
            query=query,
            results=results,
            provider=self.name,
        ).to_dict()

    def health_check(self) -> bool:
        return self.is_configured()


def build_web_search_provider_from_env() -> WebSearchProvider:
    provider_name = os.getenv("VAANI_SUTRA_SEARCH_PROVIDER", "").strip().lower()
    api_key = os.getenv("VAANI_SUTRA_SEARCH_API_KEY", "").strip()
    if provider_name == "brave" and api_key:
        return BraveWebSearchProvider(api_key=api_key)
    return NotConfiguredWebSearchProvider()