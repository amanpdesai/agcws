# Layer on the verified project tool image; keep historical images unchanged.
ARG BASE_IMAGE=agcws:dev
FROM ${BASE_IMAGE}
USER root
ARG VERILATOR_REF=d0aa828c217410fffc73d92077b6f4f54830357c
ARG BUILD_JOBS=16
RUN apt-get update && apt-get install -y --no-install-recommends autoconf help2man \
    && rm -rf /var/lib/apt/lists/*
RUN git clone https://github.com/verilator/verilator.git /tmp/agcws-verilator \
    && cd /tmp/agcws-verilator \
    && git checkout --detach "$VERILATOR_REF" \
    && autoconf \
    && ./configure --prefix=/usr/local \
    && make -j "$BUILD_JOBS" \
    && make install \
    && cd / && rm -rf /tmp/agcws-verilator

ENV AGCWS_VERILATOR=/usr/local/bin/verilator

RUN apt-get update && apt-get install -y --no-install-recommends picolibc-riscv64-unknown-elf \
    && rm -rf /var/lib/apt/lists/*
