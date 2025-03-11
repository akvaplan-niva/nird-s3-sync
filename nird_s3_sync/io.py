# -*- coding: utf-8 -*-


import hashlib

import fsspec


def get_file_sha256_checksum(
    fs: fsspec.spec.AbstractFileSystem,
    path: str,
    chunk_size: int = 1024**2,  # 1 MB
) -> str:
    """Get the SHA256-checksum of a file on a file-system.

    Parameters
    ----------
    fs : `fsspec.spec.AbstractFileSystem`
        File-system instance where the file is located.
    path : `str`
        Path of the file on the file-system.
    chunk_size : `int`
        Number of bytes to read at a time to update the hash object state.

    Returns
    -------
    `str`
        SHA256-checksum.
    """
    sha256_hash = hashlib.sha256()
    with fs.open(path, mode="rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def fs2fs_copy(
    fs_src: fsspec.spec.AbstractFileSystem,
    path_src: str,
    fs_dest: fsspec.spec.AbstractFileSystem,
    path_dest: str,
    chunk_size: int = 1024**2,  # 1 MB
) -> str:
    """Copy a file from one file-system to another.

    Copy a file from a file-system instance at a given path, to another
    file-system instance at a given path. Return the SHA256-checksum computed
    from the bytes read from the file on the source file-system.

    Parameters
    ----------
    fs_src : `fsspec.spec.AbstractFileSystem`
        Instance of the (source) file-system where the file to be copied is.
    path_src : `str`
        Path of the file to be copied on the source file-system.
    fs_dest : `fsspec.spec.AbstractFileSystem`
        Instance of the (destination) file-system to which the file will be copied.
    path_dest : `str`
        Path of the file to be copied on the destination file-system.
    chunk_size : `int`, default: 1048576
        Number of bytes to copy at a time. Default is 1048576 (1MB).

    Returns
    -------
    `str`
        SHA256-checksum of the file read on the source file-system.
    """
    sha256_hash = hashlib.sha256()
    with (
        fs_src.open(path_src, mode="rb") as f_src,
        fs_dest.open(path_dest, mode="wb") as f_dest,
    ):
        while chunk := f_src.read(chunk_size):
            sha256_hash.update(chunk)
            f_dest.write(chunk)
    return sha256_hash.hexdigest()


def safe_fs2fs_copy(
    fs_src: fsspec.spec.AbstractFileSystem,
    path_src: str,
    fs_dest: fsspec.spec.AbstractFileSystem,
    path_dest: str,
    chunk_size: int = 1024**2,  # 1 MB
    n_retries: int = 3,
) -> None:
    """Copy a file from one file-system to another and ensure data integrity.

    Copy a file from a file-system instance at a given path, to another
    file-system instance at a given path. Ensure data integrity by computing
    the SHA256-checksum of the copied file on the destination file-system, and
    verifying that it matches the checksum computed from the file read on the
    source file-system.

    Parameters
    ----------
    fs_src : `fsspec.spec.AbstractFileSystem`
        Instance of the (source) file-system where the file to be copied is.
    path_src : `str`
        Path of the file to be copied on the source file-system.
    fs_dest : `fsspec.spec.AbstractFileSystem`
        Instance of the (destination) file-system to which the file will be copied.
    path_dest : `str`
        Path of the file to be copied on the destination file-system.
    chunk_size : `int`, default: 1048576
        Number of bytes to copy at a time. Default is 1048576 (1MB). The same
        ``chunk_size`` will be used to read and compute the checksum of the
        file copied on the destination file-system.
    n_retries : `int`, default: 3
        Maximum number of times to restart the copy operation for, if the data
        was corrupted while copied. Default is 3. If the data is still
        corrupted after ``n_retries`` times, the copied data is deleted on the
        destination file-system.

    Raises
    ------
    `RuntimeError`
        If the data was corrupted while copied, after a given number of
        attempts (see ``n_retries``).

    See Also
    --------
    :func:`fs2fs_copy` : Copy file between file-systems without data integrity
        check.

    Returns
    -------
    `None`
    """
    while n_retries:
        checksum_src = fs2fs_copy(fs_src, path_src, fs_dest, path_dest, chunk_size)
        checksum_dest = get_file_sha256_checksum(fs_dest, path_dest, chunk_size)
        if checksum_src != checksum_dest:
            n_retries -= 1
            continue
        else:
            return
    else:
        fs_dest.rm(path_dest)
        raise RuntimeError(
            f"The file {path_src!r} was not copied successfully to {path_dest!r}."
        )
