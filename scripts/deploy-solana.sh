#!/usr/bin/env bash
set -euo pipefail
solana config set --url devnet
anchor build
anchor deploy
# Run `anchor keys list`, then replace the placeholder program id in Anchor.toml and lib.rs.
