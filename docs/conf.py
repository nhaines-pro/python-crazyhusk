"""Sphinx configuration."""
project = "CrazyHusk"
author = "Nick Haines"
copyright = "2022, Nick Haines"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
