# -*- coding: utf-8 -*-


import json
import os
from unittest.mock import patch

import pytest
import s3fs

from nird_s3_sync import utils


@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("ACCESS_KEY_NIRD_S3", "SOME_ACCESS_KEY", prepend=False)
    monkeypatch.setenv("SECRET_KEY_NIRD_S3", "SOME_SECRET_KEY", prepend=False)


@pytest.fixture
def mock_missing_env_vars(monkeypatch):
    monkeypatch.delenv("ACCESS_KEY_NIRD_S3", raising=False)
    monkeypatch.delenv("SECRET_KEY_NIRD_S3", raising=False)


def test_get_credentials(mock_env_vars):
    credentials = utils.get_credentials()
    expected_credentials = {
        "key": "SOME_ACCESS_KEY",
        "secret": "SOME_SECRET_KEY",
    }
    assert json.dumps(credentials, sort_keys=True) == json.dumps(
        expected_credentials, sort_keys=True
    )


def test_get_missing_credentials(mock_missing_env_vars):
    with pytest.raises(RuntimeError):
        _ = utils.get_credentials()


def test_get_fs(monkeypatch, f_minio_fs_bucket):
    monkeypatch.setenv(
        "ACCESS_KEY_NIRD_S3",
        os.getenv("MINIO_ROOT_USER"),
        prepend=False,
    )
    monkeypatch.setenv(
        "SECRET_KEY_NIRD_S3",
        os.getenv("MINIO_ROOT_PASSWORD"),
        prepend=False,
    )
    _, bucket_name = f_minio_fs_bucket
    with patch.object(
        utils,
        "NIRD_S3_ENDPOINT_URL",
        f"http://127.0.0.1:{os.getenv('MINIO_PORT')}",
    ):
        fs = utils.get_fs(bucket_name)
        assert isinstance(fs, s3fs.core.S3FileSystem)
        assert hasattr(fs, "bucket_name")
        assert fs.bucket_name == bucket_name
        with pytest.raises(FileNotFoundError):
            _ = utils.get_fs("not_a_bucket")
