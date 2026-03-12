FROM python:3.12-slim AS builder

WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends libzbar0 tesseract-ocr tesseract-ocr-eng ffmpeg && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir --prefix=/install ".[qr,ocr,audio]"

# Dev stage — includes test/lint tools and test files
FROM python:3.12-slim AS dev

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libzbar0 tesseract-ocr tesseract-ocr-eng ffmpeg && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml .
COPY src/ src/
COPY tests/ tests/

RUN pip install --no-cache-dir -e ".[dev,qr,ocr,audio]"

# Production stage
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends libzbar0 tesseract-ocr tesseract-ocr-eng ffmpeg && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

WORKDIR /app

ENTRYPOINT ["python", "-m", "clipsort"]
