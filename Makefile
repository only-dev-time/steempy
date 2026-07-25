PROJECT := $(shell basename $(shell pwd))
PYTHON_FILES := steem steembase tests setup.py

.PHONY: clean test test-all lint package install-check fmt install

clean:
	rm -rf build/ dist/ *.egg-info .eggs/ .tox/ \
		__pycache__/ .cache/ .coverage htmlcov .pytest_cache src

test: clean
	tox -e py312

test-all: clean
	tox -e py38,py39,py310,py311,py312

lint:
	tox -e lint

package: clean
	tox -e package

install-check: package
	tox -e install-py38,install-py39,install-py310,install-py311,install-py312

fmt:
	yapf --recursive --in-place --style pep8 $(PYTHON_FILES)
	pycodestyle $(PYTHON_FILES)

install:
	python setup.py install
