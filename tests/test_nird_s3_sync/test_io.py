# -*- coding: utf-8 -*-


import hashlib

import hypothesis.strategies as st
from hypothesis import HealthCheck, given, settings

from nird_s3_sync.io import get_file_sha256_checksum


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
