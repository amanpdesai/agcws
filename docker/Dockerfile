# Pin the architecture-specific base resolved by the verified build on
# 2026-08-31. Dependency/tool commits below are pinned independently.
FROM python:3.10-slim@sha256:38758a82a44d1acb9bae3dd5f7d2a55452fb44a5ceca7c4589f360f2c4aa3d0c

LABEL io.agcws.project=agcws

COPY tools/tools.lock /opt/agcws/tools.lock
COPY --from=tool_sources revisions.txt /opt/agcws/tool-source-revisions.txt
ARG BUILD_JOBS=8

ARG DEBIAN_FRONTEND=noninteractive
RUN . /opt/agcws/tools.lock && apt-get update && apt-get install -y --no-install-recommends \
    "$VERILATOR_PACKAGE" "$AUTOCONF_PACKAGE" "$GPERF_PACKAGE" \
    "$RISCV_GCC_PACKAGE" "$RISCV_BINUTILS_PACKAGE" \
    $BUILD_PACKAGES "$GTKWAVE_PACKAGE" \
    && rm -rf /var/lib/apt/lists/*

COPY --from=tool_sources yosys /tmp/yosys
RUN make -C /tmp/yosys config-gcc && \
    make -C /tmp/yosys -j "$BUILD_JOBS" PREFIX=/usr/local && \
    make -C /tmp/yosys install PREFIX=/usr/local && rm -rf /tmp/yosys

COPY --from=tool_sources iverilog /tmp/iverilog
RUN cd /tmp/iverilog && sh autoconf.sh && ./configure --prefix=/usr/local && \
    make -j "$BUILD_JOBS" && make install && cd / && rm -rf /tmp/iverilog

COPY --from=tool_sources cudd /tmp/cudd
COPY --from=tool_sources opensta /tmp/OpenSTA
RUN cd /tmp/cudd && ./configure --prefix=/tmp/cudd-install && \
    make -j "$BUILD_JOBS" && make install && \
    cmake -S /tmp/OpenSTA -B /tmp/OpenSTA/build -DCMAKE_BUILD_TYPE=Release \
      -DCUDD_DIR=/tmp/cudd-install -DBUILD_TESTS=OFF && \
    cmake --build /tmp/OpenSTA/build --parallel 2 && \
    install -Dm755 /tmp/OpenSTA/build/sta /usr/local/bin/sta && \
    install -Dm644 /tmp/OpenSTA/examples/sky130_hd.v /usr/local/share/agcws/sky130_hd.v && \
    install -Dm644 /tmp/OpenSTA/examples/sky130_hd_primitives.v /usr/local/share/agcws/sky130_hd_primitives.v && \
    cd / && rm -rf /tmp/OpenSTA /tmp/cudd /tmp/cudd-install

COPY --from=tool_sources sv-elab /tmp/sv-elab
COPY --from=tool_sources boost-regex /tmp/boost-regex
RUN cmake -S /tmp/sv-elab -B /tmp/sv-elab/build -DCMAKE_BUILD_TYPE=Release \
      -DFETCHCONTENT_SOURCE_DIR_BOOST_REGEX=/tmp/boost-regex \
      -DSLANG_USE_SYSTEM_TOMLPLUSPLUS=ON -DSLANG_USE_MIMALLOC=OFF && \
    cmake --build /tmp/sv-elab/build --parallel "$BUILD_JOBS" && \
    install -Dm755 /tmp/sv-elab/build/slang.so /usr/local/share/yosys/plugins/slang.so && \
    rm -rf /tmp/sv-elab /tmp/boost-regex

# Committed export excludes local CHIA edits without changing its worktree.
COPY --from=tool_sources chia /opt/chia
COPY pyproject.toml /opt/agcws/pyproject.toml
COPY src /opt/agcws/src
COPY docker/smoke.sh /opt/agcws/docker/smoke.sh
COPY benchmarks/support/liberty /opt/agcws/benchmarks/support/liberty
COPY benchmarks/opentitan /opt/agcws/benchmarks/opentitan
COPY benchmarks/verilog-axi /opt/agcws/benchmarks/verilog-axi
COPY benchmarks/ibex /opt/agcws/benchmarks/ibex
COPY benchmarks/support/bsg_fakeram /opt/agcws/benchmarks/support/bsg_fakeram
COPY benchmarks/support/basejump_stl /opt/agcws/benchmarks/support/basejump_stl
COPY benchmarks/redmule /opt/agcws/benchmarks/redmule
WORKDIR /opt/agcws
RUN mkdir -p /opt/agcws/out /opt/agcws/.dependencies && chmod 0777 /opt/agcws/out
ENV PIP_NO_CACHE_DIR=1
RUN . /opt/agcws/tools.lock && \
    python -m pip install "pip==$PIP_VERSION" "setuptools==$SETUPTOOLS_VERSION" "wheel==$WHEEL_VERSION" && \
    python -m pip install --no-build-isolation \
      "fusesoc==$FUSESOC_VERSION" "edalize==$EDALIZE_VERSION" \
      "cocotb==$COCOTB_VERSION" "cocotb-test==$COCOTB_TEST_VERSION" \
      "cocotbext-axi==$COCOTBEXT_AXI_VERSION" "myhdl==$MYHDL_VERSION" \
      -e /opt/chia '.[analysis,verification,research]'

# COPY preserves restrictive host modes; runtime uses the caller's unprivileged UID.
RUN chmod -R a+rX /opt/agcws /opt/chia

ENV PYTHONUNBUFFERED=1 \
    HOME=/tmp \
    VENV_PYTHON=python3 \
    MPLCONFIGDIR=/tmp/matplotlib \
    AGCWS_VERILATOR=/usr/bin/verilator \
    AGCWS_YOSYS=/usr/local/bin/yosys \
    AGCWS_IVERILOG=/usr/local/bin/iverilog \
    AGCWS_VVP=/usr/local/bin/vvp \
    AGCWS_IVERILOG_VPI=/usr/local/bin/iverilog-vpi \
    AGCWS_OPENSTA=/usr/local/bin/sta \
    AGCWS_SKY130_CELL_MODELS=/usr/local/share/agcws/sky130_hd.v \
    AGCWS_SKY130_PRIMITIVES=/usr/local/share/agcws/sky130_hd_primitives.v \
    AGCWS_SLANG_PLUGIN=/usr/local/share/yosys/plugins/slang.so \
    AGCWS_LIBERTY=benchmarks/support/liberty/sky130hd/sky130_fd_sc_hd__tt_025C_1v80.lib \
    AGCWS_LIBERTY_NANGATE45=benchmarks/support/liberty/nangate45/Nangate45_typ.lib
CMD ["agcws", "doctor"]
