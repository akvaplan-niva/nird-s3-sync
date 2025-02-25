# -*- coding: utf-8 -*-


import json

import pytest

from nird_s3_sync.utils import get_credentials


@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("ACCESS_KEY_NIRD_S3", "SOME_ACCESS_KEY", prepend=False)
    monkeypatch.setenv("SECRET_KEY_NIRD_S3", "SOME_SECRET_KEY", prepend=False)


@pytest.fixture
def mock_missing_env_vars(monkeypatch):
    monkeypatch.delenv("ACCESS_KEY_NIRD_S3", raising=False)
    monkeypatch.delenv("SECRET_KEY_NIRD_S3", raising=False)


def test_get_credentials(mock_env_vars):
    credentials = get_credentials()
    expected_credentials = {
        "key": "SOME_ACCESS_KEY",
        "secret": "SOME_SECRET_KEY",
    }
    assert json.dumps(credentials, sort_keys=True) == json.dumps(
        expected_credentials, sort_keys=True
    )


def test_get_missing_credentials(mock_missing_env_vars):
    with pytest.raises(RuntimeError):
        _ = get_credentials()
