FROM python:3.10-slim

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    verilator yosys iverilog git make g++ graphviz ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY tools/chia /opt/chia
COPY pyproject.toml /opt/agcws/pyproject.toml
COPY src /opt/agcws/src
WORKDIR /opt/agcws
RUN python -m pip install --upgrade pip && \
    python -m pip install -e /opt/chia
RUN python -m pip install -e .

ENV PYTHONUNBUFFERED=1
CMD ["python", "-c", "import agcws; print(agcws.__version__)"]
