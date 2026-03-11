FROM python:3.12-slim AS builder

WORKDIR /build
COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir --prefix=/install .

# Dev stage — includes test/lint tools and test files
FROM python:3.12-slim AS dev

WORKDIR /app
COPY pyproject.toml .
COPY src/ src/
COPY tests/ tests/

RUN pip install --no-cache-dir -e ".[dev]"

# Production stage
FROM python:3.12-slim

COPY --from=builder /install /usr/local

WORKDIR /app

ENTRYPOINT ["python", "-m", "clipsort"]
