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
