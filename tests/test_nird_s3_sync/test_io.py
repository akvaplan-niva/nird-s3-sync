# -*- coding: utf-8 -*-


import hashlib
from pathlib import Path
from random import shuffle

import hypothesis.strategies as st
import pytest
from hypothesis import HealthCheck, given, settings

from nird_s3_sync import io as io_


@settings(
    max_examples=10,
    suppress_health_check=[HealthCheck(9)],
)
@given(bytes_=st.binary(min_size=10, max_size=100))
def test_get_file_sha256_checksum(f_tmp_file, f_tmp_local_fs, bytes_):
    sha256_hash = hashlib.sha256(bytes_)
    with open(f_tmp_file, mode="wb") as f:
        f.write(bytes_)
    assert sha256_hash.hexdigest() == io_.get_file_sha256_checksum(
        f_tmp_local_fs, f_tmp_file
    )


def test_fs2fs_copy(tmp_path, f_minio_fs_file, f_tmp_local_fs):
    minio_fs, minio_filepath = f_minio_fs_file
    # Write random content in file
    with minio_fs.open(
        minio_filepath,
        mode="w",
        encoding="utf-8",
    ) as f:
        f.write("Some content")
    output_path = tmp_path / Path(minio_filepath).name
    assert not output_path.exists()
    _ = io_.fs2fs_copy(
        minio_fs,
        minio_filepath,
        f_tmp_local_fs,
        output_path.as_posix(),
    )
    assert output_path.exists()


def test_safe_fs2fs_copy(tmp_path, f_minio_fs_file, f_tmp_local_fs, monkeypatch):
    minio_fs, minio_filepath = f_minio_fs_file
    # Write random content in file
    content = "Some content"
    with minio_fs.open(
        minio_filepath,
        mode="w",
        encoding="utf-8",
    ) as f:
        f.write(content)
    output_path = tmp_path / Path(minio_filepath).name
    assert not output_path.exists()
    io_.safe_fs2fs_copy(
        minio_fs,
        minio_filepath,
        f_tmp_local_fs,
        output_path.as_posix(),
    )
    assert output_path.exists()
    output_path.unlink()
    assert not output_path.exists()

    def mockreturn(*args, **kargs):
        sha256 = ret = io_.fs2fs_copy(*args, **kargs)
        while sha256 != ret:
            ret = "".join(shuffle(list(ret)))
        return ret

    monkeypatch.setattr(io_, "fs2fs_copy", mockreturn)
    with pytest.raises(RuntimeError):
        io_.safe_fs2fs_copy(
            minio_fs,
            minio_filepath,
            f_tmp_local_fs,
            output_path.as_posix(),
        )
    assert not output_path.exists()
