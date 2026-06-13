FROM python:3.12-slim-bookworm AS base

COPY --from=ghcr.io/astral-sh/uv:0.9.21 /uv /uvx /bin/

RUN apt-get update \
    && apt-get install --no-install-recommends -y openjdk-17-jre-headless procps \
    && rm -rf /var/lib/apt/lists/*

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYSPARK_PYTHON=/app/.venv/bin/python \
    PATH="/app/.venv/bin:${PATH}"

WORKDIR /app

COPY pyproject.toml uv.lock ./

FROM base AS etl

RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    uv sync --frozen --no-dev

COPY src ./src

ENV PYTHONPATH=/app/src

CMD ["/app/.venv/bin/python", "-m", "bank_etl.main"]

FROM base AS development

RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    uv sync --frozen

COPY src ./src
COPY script ./script

ENV PYTHONPATH=/app/src

CMD ["/app/.venv/bin/jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--ServerApp.token="]
