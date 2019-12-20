#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" setup.py for fdbutil """
import io
import os

from setuptools import find_packages, setup

# Package meta-data.
NAME = "fdbutil"
DESCRIPTION = "ops tool for running foundationdb"
URL = "https://phabricator.corp.wavefront.com/source/fdbutil"
EMAIL = "lborowski@vmware.com"
AUTHOR = "Len Borowski"
REQUIRES_PYTHON = ">=3.6.0"
VERSION = False

# What packages are required for this module to be executed?
REQUIRED = []

# What packages are optional?
EXTRAS = {}

HERE = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
        LONG_DESCRIPTION = "\n" + f.read()
except FileNotFoundError:
    LONG_DESCRIPTION = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
ABOUT = {}
if not VERSION:
    PROJECT_SLUG = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(HERE, PROJECT_SLUG, "__version__.py")) as f:
        exec(f.read(), ABOUT)
else:
    ABOUT["__version__"] = VERSION

setup(
    name=NAME,
    version=ABOUT["__version__"],
    description=DESCRIPTION,
    entry_points={"console_scripts": ["fdbutil = fdbutil.__main__:main"]},
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license="MIT",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
