# API

- `POST /auth/wallet/nonce` accepts `wallet`, `chain`; returns a nonce, message, expiry.
- `POST /auth/wallet` verifies `{ wallet, chain, nonce, signature }`.
- `GET /blockchain/{chain}/transaction/{tx_hash}` queries the chain and returns `pending`, `confirmed`, `failed`, or `not_found`.

Gameplay endpoints are intentionally not fabricated in the scaffold: their request/response compatibility must be established from the actual game domain before implementation.
