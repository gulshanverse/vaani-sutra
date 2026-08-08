import os
import pytest
from unittest import mock

from main import main


def test_main_exit_code_when_credentials_missing(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("VIDEOSDK_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("VIDEOSDK_API_KEY", raising=False)
    monkeypatch.delenv("VIDEOSDK_SECRET_KEY", raising=False)

    exit_code = main()
    assert exit_code == 1


def test_main_initializes_event_loop(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "valid-google-key-12345")
    monkeypatch.setenv("VIDEOSDK_AUTH_TOKEN", "token")

    with mock.patch("main.build_worker_job") as build_job:
        fake_job = mock.Mock()
        fake_job.start.return_value = None
        build_job.return_value = fake_job

        exit_code = main()

    assert exit_code == 0
    fake_job.start.assert_called_once()


def test_make_context_uses_playground_flag(monkeypatch):
    import asyncio

    from main import RuntimeConfig, make_context

    monkeypatch.setenv("GOOGLE_API_KEY", "valid-google-key-12345")
    monkeypatch.setenv("VIDEOSDK_AUTH_TOKEN", "token")
    monkeypatch.setenv("VAANI_SUTRA_PLAYGROUND", "true")

    event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(event_loop)

    try:
        monkeypatch.setattr(
            "main.runtime_config",
            RuntimeConfig(
                google_api_key="valid-google-key-12345",
                videosdk_auth="token",
                playground=True,
            ),
        )

        ctx = make_context()

        assert ctx.room_options.playground is True
        assert ctx.room_options.auth_token == "token"
    finally:
        event_loop.close()
        asyncio.set_event_loop(None)


def test_build_worker_job_direct_playground_mode(monkeypatch):
    from main import RuntimeConfig, build_worker_job

    monkeypatch.setenv("GOOGLE_API_KEY", "valid-google-key-12345")
    monkeypatch.setenv("VIDEOSDK_AUTH_TOKEN", "token")
    monkeypatch.setenv("VAANI_SUTRA_PLAYGROUND", "true")

    monkeypatch.setattr(
        "main.runtime_config",
        RuntimeConfig(
            google_api_key="valid-google-key-12345",
            videosdk_auth="token",
            playground=True,
        ),
    )

    job = build_worker_job()

    assert job.options.register is False
    assert job.options.auth_token == "token"
