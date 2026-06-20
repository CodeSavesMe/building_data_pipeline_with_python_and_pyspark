FROM python:3.11-slim-bookworm AS base

COPY --from=ghcr.io/astral-sh/uv:0.9.21 /uv /uvx /bin/

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        curl \
        openjdk-17-jre-headless \
        procps \
    && ln -s /usr/lib/jvm/java-17-openjdk-* /opt/java \
    && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/opt/java \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYSPARK_PYTHON=/app/.venv/bin/python \
    PYSPARK_DRIVER_PYTHON=/app/.venv/bin/python \
    PATH="/app/.venv/bin:${PATH}"

WORKDIR /app

COPY pac_car/pyproject.toml pac_car/README.md ./

FROM base AS etl

RUN uv sync --no-dev --no-install-project

COPY pac_car/src ./src
COPY dataset/car_brand.csv ./dataset/car_brand.csv
COPY dataset/api_data.json ./dataset/api_data.json

RUN uv sync --no-dev

CMD ["/app/.venv/bin/pac-car-pipeline"]

FROM base AS development

RUN uv sync --no-install-project

COPY pac_car/src ./src
COPY dataset/car_brand.csv ./dataset/car_brand.csv
COPY dataset/api_data.json ./dataset/api_data.json

RUN uv sync

CMD ["/bin/bash"]
