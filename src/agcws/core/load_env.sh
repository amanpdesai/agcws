#!/usr/bin/env bash
# Load non-secret repository configuration for shell entrypoints.
set -a
if [[ -f .env ]]; then
  # .env is user-controlled and should contain KEY=VALUE assignments only.
  source .env
fi
set +a
