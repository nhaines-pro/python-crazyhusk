"""Sphinx configuration."""
# Standard Library
from importlib import metadata as md

project = "CrazyHusk"
author = "Nick Haines"
copyright = "2022, Nick Haines"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "sphinx.ext.mathjax",
]
autodoc_typehints = "description"
html_theme = "furo"

basename = "crazyhusk"
_metadata = md.metadata(basename)
release = _metadata.get("Version")
version = ".".join(release.split(".")[:2])
