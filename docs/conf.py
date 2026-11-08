"""Configuration Sphinx du projet immo-price."""

project = "immo-price"
author = "Amsata Fall & Yi Xu"
release = "0.1.0"
language = "fr"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "sphinx_rtd_theme"
