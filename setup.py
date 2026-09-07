#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import find_packages
from setuptools import setup


# Package meta-data.
NAME = "steempy"
DESCRIPTION = "Python library for interacting with the Steem blockchain."
URL = "https://github.com/only-dev-time/steempy"
EMAIL = "111915936+only-dev-time@users.noreply.github.com"
AUTHOR = "Moecki"

# What packages are required for this module to be executed?
REQUIRED = [
    "appdirs",
    "certifi",
    "diff-match-patch",
    "ecdsa>=0.13",
    "funcy",
    'futures ; python_version < "3.0.0"',
    "future",
    "langdetect",
    "prettytable",
    "pycryptodome>=3.20.0",
    "pylibscrypt>=1.6.1",
    "scrypt>=0.8.0",
    "toolz",
    "ujson",
    "urllib3",
    "voluptuous",
    "w3lib",
]
TEST_REQUIRED = [
    "pep8",
    "pytest",
    'pytest-pylint ; python_version >= "3.4.0"',
    "pytest-xdist",
    "pytest-runner",
    "pytest-pep8",
    "pytest-cov",
    "yapf",
    "autopep8",
]

BUILD_REQUIRED = [
    "twine",
    "pypandoc",
    "recommonmark",
    "wheel",
    "setuptools",
    "sphinx",
    "sphinx_rtd_theme",
]
# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.rst' is present in your MANIFEST.in file!
# with io.open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
#     long_description = '\n' + f.read()


# Where the magic happens:
setup(
    name=NAME,
    version="1.0.3",
    description=DESCRIPTION,
    keywords=["steem", "cryptocurrency", "blockchain"],
    # long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    packages=find_packages(exclude=("tests", "scripts")),
    entry_points={
        "console_scripts": [
            "piston=steem.cli:legacyentry",
            "steempy=steem.cli:legacyentry",
            "steemtail=steem.cli:steemtailentry",
        ],
    },
    install_requires=REQUIRED,
    python_requires=">=3.8,<3.13",
    extras_require={
        "dev": TEST_REQUIRED + BUILD_REQUIRED,
        "build": BUILD_REQUIRED,
        "test": TEST_REQUIRED,
    },
    include_package_data=True,
    license="MIT",
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 4 - Beta",
    ],
)
