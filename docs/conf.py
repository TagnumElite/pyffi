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
# The short X.Y.Z version.
version = '.'.join(release.split('.')[:3])


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.imgmath',
    'sphinx.ext.githubpages',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.doctest',
    'sphinx.ext.coverage',
    'sphinx.ext.todo',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None)
}

todo_include_todos = True
autosummary_generate = []

default_role = 'any'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# A string of reStructuredText that will be included at the beginning of
# every source file that is read. This is a possible place to add
# substitutions that should be available in every file.
rst_prolog = """
"""

# A string of reStructuredText that will be included at the end of
# every source file that is read. This is a possible place to add
# substitutions that should be available in every file.
rst_epilog = """
.. |BUILD_WINDOWS| image:: https://img.shields.io/appveyor/ci/neomonkeus/pyffi/develop.svg?label=Windows%20Build&logo=appveyor&logoColor=fff
   :target: https://ci.appveyor.com/project/neomonkeus/pyffi
   :alt: Windows build status

.. |BUILD_DOCS| image:: https://img.shields.io/readthedocs/pyffi/develop.svg?label=Docs%20Build&logo=read-the-docs&logoColor=fff
   :target: https://pyffi.readthedocs.io
   :alt: Document build status

.. |BUILD_LINUX| image:: https://img.shields.io/travis/com/niftools/pyffi/develop.svg?label=Linux%20Build&logo=travis
   :target: https://travis-ci.org/niftools/pyffi
   :alt: Linux/MacOS build status

.. |COVERAGE| image:: https://img.shields.io/coveralls/github/niftools/pyffi/develop.svg?label=Coverage
   :target: https://coveralls.io/r/niftools/pyffi?branch=develop
   :alt: Current code coverage

.. |VERSION_PYPI| image:: https://img.shields.io/pypi/v/pyffi.svg?logo=python&logoColor=fff
   :target: https://pypi.org/project/PyFFI/
   :alt: Current Released Version

.. |VERSION_PYTHON| image:: https://img.shields.io/pypi/pyversions/pyffi.svg?logo=python&logoColor=fff
   :alt: Supported Python versions

.. |ISSUE_GITHUB| image:: https://img.shields.io/github/issues/niftools/pyffi.svg?logo=github&logoColor=fff
   :target: https://github.com/niftools/pyffi/issues
   :alt: Current open github issues

.. |PULL_GITHUB| image:: https://img.shields.io/github/issues-pr/niftools/pyffi.svg?logo=github&logoColor=fff
   :target: https://github.com/niftools/pyffi/pulls
   :alt: GitHub pull requests
"""

keep_warnings = True


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

# -- Options for AutoDoc ---------------------------------------------------

autodoc_default_options = {
    'special-members': '__init__',
}
