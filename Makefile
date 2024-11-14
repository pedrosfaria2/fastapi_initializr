SHELL := /bin/bash
PY = python3
POETRY := poetry
PYTHON := $(POETRY) run python
SERVICE_NAME := fastapi-initializr

.PHONY: help
help:
	@echo "Usage: make [target]"
	@echo "Targets:"
	@echo " setup        	Install dependencies using Poetry"
	@echo " run            Run the application"
	@echo " run-docker     Run the application using Docker"
	@echo " run-compose    Run the application with Compose"
	@echo " update       	Update dependencies using Poetry"
	@echo " lock         	Generate Poetry lock file"
	@echo " test         	Run tests"
	@echo " test-coverage  Run tests to get coverage"
	@echo " lint         	Lint the code using flake8"
	@echo " format       	Format the code using black"
	@echo " clean        	Clean the project"

.PHONY: run-docker
run-docker:
	docker build --pull --rm -f docker/Dockerfile -t $(SERVICE_NAME):latest . || (echo "Build failed" && exit 1)
	docker rm -f $(SERVICE_NAME) 2>/dev/null || true
	docker run -d --name $(SERVICE_NAME) -p 8000:8000 $(SERVICE_NAME):latest

.PHONY: run-compose
run-compose:
	@if [ ! -f .env ]; then \
		echo "Creating .env file from example..."; \
		cp .env.example .env || touch .env; \
	fi
	docker compose -f docker/docker-compose.yml up --build dev

.PHONY: run
run:
	$(PYTHON) src/main.py

.PHONY: setup
setup:
	$(PY) -m venv .venv && \
	source .venv/bin/activate && \
	$(PY) -m pip install --upgrade pip && \
	$(PY) -m pip install poetry && \
	$(PY) -m poetry config virtualenvs.create true && \
	$(PY) -m poetry config virtualenvs.in-project true && \
	$(PY) -m poetry config virtualenvs.path .venv && \
	$(PY) -m poetry install && \
	pre-commit install -f && \
	pre-commit install --hook-type commit-msg -f
	@echo "To activate the virtual environment, run: source .venv/bin/activate |OR| poetry shell"

.PHONY: update
update:
	$(POETRY) update

.PHONY: lock
lock:
	$(POETRY) lock

.PHONY: test
test:
	$(PYTHON) -m pytest

.PHONY: test-coverage
test-coverage:
	$(PYTHON) -m pytest --cov=src --cov-report=term tests/

.PHONY: lint
lint:
	$(PYTHON) -m flake8 .

.PHONY: format
format:
	$(PYTHON) -m black .

.PHONY: clean
clean:
	@rm -rf .pytest_cache
	@rm -rf __pycache__
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@find . -name "*.pyc" -delete
	@find . -name "*.pyo" -delete
	@find . -name "*~" -delete
