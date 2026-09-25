.DEFAULT_GOAL := help
PYTHON ?= python3
VENV_PYTHON ?= .venv/bin/python
AGCWS = $(VENV_PYTHON) -m agcws

.PHONY: help install test lint doctor container-build container-smoke container-prune
help:
	$(AGCWS) --help

install:
	$(PYTHON) -m venv .venv
	$(VENV_PYTHON) -m pip install -e '.[dev,research,analysis,verification]'

test:
	$(VENV_PYTHON) -m pytest -q

lint:
	$(VENV_PYTHON) -m ruff check src tests

doctor:
	$(AGCWS) doctor

container-build:
	bash docker/build.sh

container-smoke:
	bash docker/run.sh bash docker/smoke.sh

container-prune:
	bash docker/prune.sh
