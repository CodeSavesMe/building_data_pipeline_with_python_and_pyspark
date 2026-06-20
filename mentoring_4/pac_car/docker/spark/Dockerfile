FROM python:3.11-slim-bookworm

ARG PYSPARK_VERSION=3.5.8

COPY --from=ghcr.io/astral-sh/uv:0.9.21 /uv /uvx /bin/

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        bash \
        openjdk-17-jre-headless \
        procps \
    && ln -s /usr/lib/jvm/java-17-openjdk-* /opt/java \
    && rm -rf /var/lib/apt/lists/*

RUN uv pip install --system --no-cache "pyspark==${PYSPARK_VERSION}"

ENV JAVA_HOME=/opt/java
ENV SPARK_HOME=/usr/local/lib/python3.11/site-packages/pyspark
ENV PATH="${SPARK_HOME}/bin:${PATH}"
ENV PYSPARK_PYTHON=python
ENV PYSPARK_DRIVER_PYTHON=python

COPY pac_car/docker/spark/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
