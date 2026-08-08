import os
import sys
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


def test_get_videosdk_auth_from_api_secret():
    os.environ.pop("VIDEOSDK_AUTH_TOKEN", None)
    os.environ["VIDEOSDK_API_KEY"] = "api"
    os.environ["VIDEOSDK_SECRET_KEY"] = "secret"
    assert settings.get_videosdk_auth() == "api:secret"
    os.environ.pop("VIDEOSDK_API_KEY", None)
    os.environ.pop("VIDEOSDK_SECRET_KEY", None)
