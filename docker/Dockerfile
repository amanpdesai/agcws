FROM python:3.10-slim

ARG OPENSTA_REPO=https://github.com/The-OpenROAD-Project/OpenSTA.git
ARG OPENSTA_REF=c821ad1ad07031de831fd567fc626bf70d522c49
ARG SV_ELAB_REPO=https://github.com/povik/sv-elab.git
ARG SV_ELAB_REF=84bbdaacf59f56ff9b5e7be486f9cc7df136b385

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    verilator yosys iverilog git make g++ cmake bison flex swig \
    tcl-dev zlib1g-dev libeigen3-dev \
    libboost-system-dev libboost-filesystem-dev libboost-program-options-dev \
    libboost-serialization-dev libboost-iostreams-dev libboost-regex-dev \
    libboost-thread-dev libgtest-dev libfl-dev wget graphviz ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q https://raw.githubusercontent.com/davidkebo/cudd/main/cudd_versions/cudd-3.0.0.tar.gz \
    -O /tmp/cudd-3.0.0.tar.gz && \
    tar -xzf /tmp/cudd-3.0.0.tar.gz -C /tmp && \
    cd /tmp/cudd-3.0.0 && ./configure --prefix=/tmp/cudd-install && \
    make --jobs 2 && make install

RUN git clone --no-checkout "$OPENSTA_REPO" /tmp/OpenSTA && \
    git -C /tmp/OpenSTA checkout --detach "$OPENSTA_REF" && \
    cmake -S /tmp/OpenSTA -B /tmp/OpenSTA/build -DCMAKE_BUILD_TYPE=Release \
      -DCUDD_DIR=/tmp/cudd-install -DBUILD_TESTS=OFF && \
    cmake --build /tmp/OpenSTA/build --parallel 2 && \
    install -Dm755 /tmp/OpenSTA/build/sta /usr/local/bin/sta && \
    rm -rf /tmp/OpenSTA

RUN git clone --recursive --no-checkout "$SV_ELAB_REPO" /tmp/sv-elab && \
    git -C /tmp/sv-elab checkout --detach "$SV_ELAB_REF" && \
    git -C /tmp/sv-elab submodule update --init --recursive && \
    cmake -S /tmp/sv-elab -B /tmp/sv-elab/build -DCMAKE_BUILD_TYPE=Release && \
    cmake --build /tmp/sv-elab/build --parallel 2 && \
    install -Dm755 /tmp/sv-elab/build/slang.so /usr/local/share/yosys/plugins/slang.so && \
    rm -rf /tmp/sv-elab

COPY tools/chia /opt/chia
COPY pyproject.toml /opt/agcws/pyproject.toml
COPY src /opt/agcws/src
COPY scripts /opt/agcws/scripts
COPY experiments /opt/agcws/experiments
COPY flows /opt/agcws/flows
COPY third_party/liberty /opt/agcws/third_party/liberty
COPY third_party/opentitan /opt/agcws/third_party/opentitan
WORKDIR /opt/agcws
RUN python -m pip install --upgrade pip && \
    python -m pip install -e /opt/chia
RUN python -m pip install -e .

ENV PYTHONUNBUFFERED=1 \
    AGCWS_OPENSTA=/usr/local/bin/sta \
    AGCWS_SLANG_PLUGIN=/usr/local/share/yosys/plugins/slang.so \
    AGCWS_LIBERTY=third_party/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib \
    AGCWS_LIBERTY_NANGATE45=third_party/liberty/nangate45/Nangate45_typ.lib
CMD ["python", "-c", "import agcws; print(agcws.__version__)"]
