#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os

import fsspec
import s3fs

NIRD_S3_ENDPOINT_URL = "https://s3.nird.sigma2.no"


def get_credentials() -> dict:
    """Get the credentials to access the NIRD S3 bucket.

    Raises
    ------
    `RuntimeError`
        If the environment variables corresponding to the credentials are not
        set at runtime.

    Returns
    -------
    `dict`
        Mapping of the credentials.
    """
    if (access_key := os.getenv("ACCESS_KEY_NIRD_S3")) is None:
        raise RuntimeError("The 'ACCESS_KEY_NIRD_S3' environment variable must be set.")
    if (secret_key := os.getenv("SECRET_KEY_NIRD_S3")) is None:
        raise RuntimeError("The 'SECRET_KEY_NIRD_S3' environment variable must be set.")
    credentials = {
        "key": access_key,
        "secret": secret_key,
    }
    return credentials


def get_fs(bucket_name: str) -> s3fs.core.S3FileSystem:
    """Get a file-system instance mapping to the NIRD S3 bucket.

    Parameters
    ----------
    bucket_name : `str`
        Name of the bucket.

    Raises
    ------
    `FileNotFoundError`
        If the specified bucket does not exist.

    Returns
    -------
    `s3fs.core.S3FileSystem`
        File-system instance.
    """
    credentials = get_credentials()
    fs = fsspec.filesystem(
        "s3",
        endpoint_url=NIRD_S3_ENDPOINT_URL,
        **credentials,
    )
    if not fs.exists(bucket_name):
        raise FileNotFoundError(f"The bucket {bucket_name!r} does not exist.")
    # Set the bucket_name to an instance attribute
    fs.bucket_name = bucket_name
    return fs
