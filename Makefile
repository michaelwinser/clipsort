.PHONY: test test-cov lint format build clean help

help:             ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | sort | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

test:             ## Run tests
	pytest tests/ -v

test-cov:         ## Run tests with coverage report
	pytest tests/ -v --cov=clipsort --cov-report=term-missing

lint:             ## Check code quality
	ruff check src/ tests/

format:           ## Auto-format code
	ruff format src/ tests/

build:            ## Build Docker image
	docker build -t clipsort .

clean:            ## Remove build artifacts
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
