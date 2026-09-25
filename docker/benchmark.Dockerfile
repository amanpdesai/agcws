# Layer on the verified project tool image; keep historical images unchanged.
ARG BASE_IMAGE
FROM ${BASE_IMAGE}
USER root
COPY tools/tools.lock /opt/agcws/tools.lock
ARG BUILD_JOBS=16
RUN . /opt/agcws/tools.lock && apt-get update && apt-get install -y --no-install-recommends "$AUTOCONF_PACKAGE" "$HELP2MAN_PACKAGE" \
    && rm -rf /var/lib/apt/lists/*
COPY --from=tool_sources verilator /tmp/agcws-verilator
RUN cd /tmp/agcws-verilator \
    && autoconf \
    && ./configure --prefix=/usr/local \
    && make -j "$BUILD_JOBS" \
    && make install \
    && cd / && rm -rf /tmp/agcws-verilator

ENV AGCWS_VERILATOR=/usr/local/bin/verilator

RUN . /opt/agcws/tools.lock && apt-get update && apt-get install -y --no-install-recommends "$PICOLIBC_PACKAGE" \
    && rm -rf /var/lib/apt/lists/*
