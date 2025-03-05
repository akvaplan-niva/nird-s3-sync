# -*- coding: utf-8 -*-


import hashlib
from pathlib import Path

import hypothesis.strategies as st
from hypothesis import HealthCheck, given, settings

from nird_s3_sync.io import fs2fs_copy, get_file_sha256_checksum


@settings(
    max_examples=10,
    suppress_health_check=[HealthCheck(9)],
)
@given(bytes_=st.binary(min_size=10, max_size=100))
def test_get_file_sha256_checksum(f_tmp_file, f_tmp_local_fs, bytes_):
    sha256_hash = hashlib.sha256(bytes_)
    with open(f_tmp_file, mode="wb") as f:
        f.write(bytes_)
    assert sha256_hash.hexdigest() == get_file_sha256_checksum(
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
    _ = fs2fs_copy(
        minio_fs,
        minio_filepath,
        f_tmp_local_fs,
        output_path.as_posix(),
    )
    assert output_path.exists()
