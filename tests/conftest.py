# -*- coding: utf-8 -*-


import os
import tempfile

import fsspec
import pytest


@pytest.fixture
def f_tmp_file():
    _, filename = tempfile.mkstemp()
    yield filename
    os.unlink(filename)


@pytest.fixture
def f_tmp_local_fs():
    return fsspec.filesystem("file")


@pytest.fixture
def f_minio_fs_file():
    fs = fsspec.filesystem(
        "s3",
        key=os.getenv("MINIO_ROOT_USER"),
        secret=os.getenv("MINIO_ROOT_PASSWORD"),
        endpoint_url=f"http://127.0.0.1:{os.getenv('MINIO_PORT')}",
    )
    bucket_name = os.getenv("MINIO_BUCKET_NAME")
    print(f"MINIO_ROOT_USER: {os.getenv('MINIO_ROOT_USER')}")
    fs.mkdir(bucket_name)
    test_filename = "test_file.txt"
    filepath = os.path.join(bucket_name, test_filename)
    yield fs, filepath
    fs.rm(bucket_name, recursive=True)
