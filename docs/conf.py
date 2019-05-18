# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# http://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
from os.path import dirname, abspath
import sys

sys.path.insert(0, dirname(dirname(abspath(__file__))))


# -- Project information -----------------------------------------------------

project = 'PyFFI'
copyright = '2012-2019, NifTools'
author = 'Amorilia'

# The full version, including alpha/beta/rc tags
with open("../pyffi/VERSION", "rt") as f:
    release = f.read().strip()
# The short X.Y version.
version = '.'.join(release.split('.')[:2])


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.imgmath',
    'sphinx.ext.githubpages',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.doctest',
    'sphinx.ext.coverage',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None)
}

todo_include_todos = True
autosummary_generate = []

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_theme_options = {
    'home': 'http://niftools.org',
    'blog': 'http://niftools.org/blog',
    'about': 'http://niftools.org/about',
    'forums': 'http://forum.niftools.org',
    'badges': False,
    'github': 'niftools/pyffi'
}

# The name of an image file (within the static path) to place at the top of
# the sidebar.
html_logo = "_static/logo.png"

html_favicon = "_static/favicon.ico"
