.PHONY: help install install-dev test lint format clean run docker build

help:
	@echo "Available commands:"
	@echo "  install     Install dependencies (with UV or pip fallback)"
	@echo "  install-dev Install dev dependencies"
	@echo "  install-pip Install using pip only"
	@echo "  test        Run tests"
	@echo "  test-all    Run comprehensive test suite"
	@echo "  lint        Run linting"
	@echo "  format      Format code"
	@echo "  clean       Clean build artifacts"
	@echo "  run         Run the server"
	@echo "  docker      Build Docker image"
	@echo "  build       Build package"

# Check if UV is available, fallback to pip
# Note: Windows PowerShell compatibility - use Select-String instead of grep
install:
	@if command -v uv >/dev/null 2>&1; then \
		echo "Using UV for installation..."; \
		uv sync; \
	else \
		echo "UV not found, using pip fallback..."; \
		pip install -e .; \
	fi

install-dev:
	@if command -v uv >/dev/null 2>&1; then \
		echo "Using UV for dev installation..."; \
		uv sync --dev; \
	else \
		echo "UV not found, using pip for dev installation..."; \
		pip install -e .; \
		pip install pytest pytest-cov freezegun ruff pyright; \
	fi

install-pip:
	pip install -e .

test:
	python -m pytest tests/ -v

test-all:
	python -m pytest tests/ --tb=short

test-coverage:
	python -m pytest tests/ --cov=chronos_protocol --cov-report=html

lint:
	ruff check .
	pyright .

format:
	ruff format .

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	python -m chronos_protocol

docker:
	docker build -t chronos-protocol .

run-docker:
	docker run -it --rm -v $(PWD)/data:/app/data chronos-protocol

build:
	@if command -v uv >/dev/null 2>&1; then \
		echo "Building with UV..."; \
		uv build; \
	else \
		echo "UV not found, using pip build..."; \
		python -m build; \
	fi