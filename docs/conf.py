# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


import os
from pathlib import Path
import sys
import shutil


sys.path.insert(0, os.path.abspath('..'))

project = 'NIRD S3 Sync'
copyright = '2025, Mathieu Tachon'
author = 'Mathieu Tachon'

try:
    from nird_s3_sync import __version__ as version
except ImportError:
    version = ""

if not version or version.lower() == "unknown":
    version = os.getenv("READTHEDOCS_VERSION", "unknown")  # automatically set by RTD

release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
this_directory = Path(__file__).parent

try:
    shutil.rmtree(this_directory / "api")
except FileNotFoundError:
    pass

extensions = [
    "sphinx.ext.apidoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.autodoc",
    "myst_parser",
    "sphinx_rtd_theme",
    "sphinx.ext.napoleon",
]

autodoc_typehints = "none"
autodoc_member_order = "bysource"
autodoc_mock_imports = [
    "fsspec",
    "s3fs",
]

pkg_path = this_directory.parent / "nird_s3_sync"

apidoc_modules = [
    {
     "path": pkg_path.as_posix(),
     "destination": "source/api/",
     "automodule_options": {
         "members", "show-inheritance",
     },
     "module_first": True,
    }
]
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# The suffix of source filenames.
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# The reST default role (used for this markup: `text`) to use for all documents.
default_role = "py:obj"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ['_static']

intersphinx_mapping = {
    "fsspec": ("https://filesystem-spec.readthedocs.io/en/latest/", None),
}
