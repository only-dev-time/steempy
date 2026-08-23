# Python Library for the Steem Blockchain

[![CI](https://github.com/only-dev-time/steempy/actions/workflows/ci.yml/badge.svg)](https://github.com/only-dev-time/steempy/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/steempy?logo=pypi)](https://pypi.org/project/steempy/)
[![Python versions](https://img.shields.io/pypi/pyversions/steempy)](https://pypi.org/project/steempy/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

`steempy` is a Steem library for Python. It comes with a
BIP38 encrypted wallet and a practical CLI utility called `steempy`.
The [base version](https://github.com/only-dev-time/steempy/releases/tag/v1.0.1) is a fork of the [official python library](https://github.com/steemit/steem-python), which is no longer maintained. This repository continues that work as a maintained, actively developed fork for current Python and release workflows.

This library targets Python 3.8 to 3.12.

## Installation

With pip:

```bash
pip install steempy
```

From source:

```bash
git clone https://github.com/only-dev-time/steempy.git
cd steempy
python -m pip install .
```

## Homebrew Build Prereqs

If you're on a mac, you may need to do the following first:

```bash
brew install openssl
export CFLAGS="-I$(brew --prefix openssl)/include $CFLAGS"
export LDFLAGS="-L$(brew --prefix openssl)/lib $LDFLAGS"
```

## CLI tools bundled

The library comes with a few console scripts.

* `steempy`: rudimentary blockchain CLI (needs some TLC and more TLAs)
* `steemtail`: useful for e.g. `steemtail -f -j | jq --unbuffered --sort-keys .`

## Documentation

Documentation is maintained in this repository under [docs](docs).
You can build it locally via `make -C docs html`.

## Tests

This repository now uses `tox` for multi-version test automation.

Basic workflow:

* install `tox` in your dev environment
* make sure Python 3.8 to 3.12 interpreters are available locally
* run the matrix locally via `tox -e py38,py39,py310,py311,py312`

Convenience Make targets:

* `make test` runs tests on Python 3.12
* `make test-all` runs the full Python 3.8 to 3.12 matrix
* `make lint` runs ruff, isort, and mypy checks
* `make package` builds `sdist` and `wheel` and validates metadata
* `make build-check` builds tagged wheels for each Python version and validates metadata
* `make install-check` installs the built wheel in fresh tox envs and runs smoke checks
* `make verify-release` runs the full local release workflow: build checks, package build, and install validation

Release validation:

* push builds run test matrix checks
* tag pushes (`v*`) build package artifacts
* tags upload to TestPyPI first
* non-`rc` tags can upload to PyPI after TestPyPI + install checks

## TODO

* decide and publish a permanent documentation endpoint (GitHub Pages or Read the Docs)
* increase unit and integration coverage for core blockchain operations
* improve and align docs coverage with current CLI and release workflow
* evaluate migration to a dedicated CLI framework (for example click)
* ...

## Notice

This library is *under development*.  Beware.
