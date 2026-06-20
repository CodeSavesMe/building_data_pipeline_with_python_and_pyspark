#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${JAVA_HOME:-}" || ! -d "${JAVA_HOME}" ]]; then
  export JAVA_HOME="$(dirname "$(dirname "$(readlink -f "$(command -v java)")")")"
fi

case "${SPARK_MODE:-master}" in
  master)
    exec "${SPARK_HOME}/bin/spark-class" org.apache.spark.deploy.master.Master \
      --host 0.0.0.0 \
      --port "${SPARK_MASTER_PORT:-7077}" \
      --webui-port "${SPARK_MASTER_WEBUI_PORT:-8080}"
    ;;
  worker)
    exec "${SPARK_HOME}/bin/spark-class" org.apache.spark.deploy.worker.Worker \
      "${SPARK_MASTER_URL:-spark://spark-master:7077}" \
      --webui-port "${SPARK_WORKER_WEBUI_PORT:-8081}" \
      --cores "${SPARK_WORKER_CORES:-2}" \
      --memory "${SPARK_WORKER_MEMORY:-2g}"
    ;;
  *)
    exec "$@"
    ;;
esac
