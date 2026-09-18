#!/usr/bin/env bash
# Wrapper gọi SUI CLI trong container docker (dành cho máy bị chặn chạy exe tải về).
# Dùng qua: SUI_BIN=scripts/sui-docker.sh
set -euo pipefail
exec docker exec -i -w /work/blockchain/sui sui-dev sui "$@"
