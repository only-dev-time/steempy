PROJECT := $(shell basename $(shell pwd))
PYTHON_FILES := steem steembase tests setup.py

.PHONY: help clean test test-all lint package build-check verify-release install-check show-tox-tools fmt install

help: ## Show available make targets
	@echo "Available targets:"
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

clean: ## Remove build, tox, cache, and coverage artifacts
	rm -rf build/ dist/ *.egg-info .eggs/ .tox/ \
		__pycache__/ .cache/ .coverage htmlcov .pytest_cache src

test: clean ## Run tests on Python 3.12 via tox
	tox -e py312

test-all: clean ## Run tests on Python 3.8-3.12 via tox
	tox -e py38,py39,py310,py311,py312

lint: ## Run linting and static checks via tox
	tox -e lint

package: clean ## Build sdist/wheel and validate metadata
	tox -e package

build-check: clean ## Build and validate wheel on each Python version
	tox -e build-py38,build-py39,build-py310,build-py311,build-py312

verify-release: build-check package install-check ## Run full release verification pipeline locally

install-check: package ## Install the prebuilt wheel across Python versions
	tox -e install-py38,install-py39,install-py310,install-py311,install-py312

show-tox-tools: ## Show runtime and build tool versions across tox envs
	@echo "(Info: tool versions can differ per Python version by design due to marker-based constraints.)"
	@echo "=== Runtime toolchain in install environments ==="
	@for env in install-py38 install-py39 install-py310 install-py311 install-py312; do \
		echo "=== $$env ==="; \
		if [ ! -x ".tox/$$env/bin/python" ]; then \
			echo "Creating $$env (no tests)..."; \
			tox -e $$env --notest; \
		fi; \
		.tox/$$env/bin/python -m pip show pip setuptools wheel | grep -E "^(Name|Version):"; \
		echo; \
	done
	@echo "=== Build toolchain in packaging/build environments ==="
	@for env in package build-py38 build-py39 build-py310 build-py311 build-py312; do \
		echo "=== $$env ==="; \
		if [ ! -x ".tox/$$env/bin/python" ]; then \
			echo "Creating $$env (no commands)..."; \
			tox -e $$env --notest; \
		fi; \
		.tox/$$env/bin/python -m pip show pip setuptools wheel build twine | grep -E "^(Name|Version):"; \
		echo; \
	done

fmt: ## Format imports and auto-fix lints
	isort $(PYTHON_FILES)
	ruff check --fix $(PYTHON_FILES)

install: ## Legacy local install via setup.py
	python setup.py install
