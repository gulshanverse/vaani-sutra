import os
import sys
from unittest import mock

import pytest

from config import settings


def test_get_env_missing_returns_default():
    os.environ.pop("TEST_ENV_VAR", None)
    assert settings.get_env("TEST_ENV_VAR", required=False, default="fallback") == "fallback"


def test_validate_google_api_key_raises_when_missing():
    os.environ.pop("GOOGLE_API_KEY", None)
    with pytest.raises(RuntimeError, match="GOOGLE_API_KEY not set"):
        settings.validate_google_api_key(required=True)


def test_validate_google_api_key_rejects_short_key():
    os.environ["GOOGLE_API_KEY"] = "short"
    with pytest.raises(RuntimeError, match="looks invalid"):
        settings.validate_google_api_key(required=True)


def test_get_videosdk_auth_from_token():
    os.environ["VIDEOSDK_AUTH_TOKEN"] = "token-value"
    assert settings.get_videosdk_auth() == "token-value"
    os.environ.pop("VIDEOSDK_AUTH_TOKEN", None)


def test_get_videosdk_auth_from_api_secret_without_resolver(monkeypatch):
    monkeypatch.delenv("VIDEOSDK_AUTH_TOKEN", raising=False)
    monkeypatch.setenv("VIDEOSDK_API_KEY", "api")
    monkeypatch.setenv("VIDEOSDK_SECRET_KEY", "secret")

    with mock.patch("config.settings.resolve_videosdk_auth_token", None):
        assert settings.get_videosdk_auth() == "api:secret"

    monkeypatch.delenv("VIDEOSDK_API_KEY", raising=False)
    monkeypatch.delenv("VIDEOSDK_SECRET_KEY", raising=False)


def test_get_videosdk_auth_uses_resolver(monkeypatch):
    monkeypatch.delenv("VIDEOSDK_AUTH_TOKEN", raising=False)
    monkeypatch.setenv("VIDEOSDK_API_KEY", "api")
    monkeypatch.setenv("VIDEOSDK_SECRET_KEY", "secret")

    with mock.patch("config.settings.resolve_videosdk_auth_token", return_value="resolved-token"):
        assert settings.get_videosdk_auth() == "resolved-token"

    monkeypatch.delenv("VIDEOSDK_API_KEY", raising=False)
    monkeypatch.delenv("VIDEOSDK_SECRET_KEY", raising=False)
