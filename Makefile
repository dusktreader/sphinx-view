SHELL:=/bin/bash
PACKAGE_NAME:=sview
ROOT_DIR:=$(shell dirname $(shell pwd))

install:
	poetry install

test: install
	poetry run pytest

lint: install
	poetry run black --check ${PACKAGE_NAME} tests bin
	poetry run isort --check ${PACKAGE_NAME} tests bin
	poetry run flake8 --max-line-length=100 ${PACKAGE_NAME} tests bin

qa: test lint
	echo "All tests pass! Ready for deployment"

format: install
	poetry run black ${PACKAGE_NAME} tests bin
	poetry run isort ${PACKAGE_NAME} tests bin

publish: install
	git tag v$(poetry version --short)
	git push origin v$(poetry version --short)

clean: clean-eggs clean-build
	@find . -iname '*.pyc' -delete
	@find . -iname '*.pyo' -delete
	@find . -iname '*~' -delete
	@find . -iname '*.swp' -delete
	@find . -iname '__pycache__' -delete
	@rm -r .mypy_cache
	@rm -r .pytest_cache

clean-eggs:
	@find . -name '*.egg' -print0|xargs -0 rm -rf --
	@rm -rf .eggs/

clean-build:
	@rm -fr build/
	@rm -fr dist/
	@rm -fr *.egg-info
