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
