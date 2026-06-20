FROM pac_car-pipeline:latest

RUN uv pip install --python /app/.venv/bin/python --no-cache \
    "ipykernel>=6.29.0" \
    "jupyterlab>=4.2.0"

ENV PYTHONPATH=/app/src

CMD ["/app/.venv/bin/jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root", "--notebook-dir=/app", "--ServerApp.token=", "--ServerApp.password="]
