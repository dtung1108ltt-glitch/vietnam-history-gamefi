# Việt Sử Chiến Ký — MVP GameFi lịch sử Việt Nam

MVP theo tài liệu *MVP System Architecture Design*: backend FastAPI (modular monolith), frontend React, hợp đồng SUI Move và tầng adapter blockchain thống nhất.

```
backend/      FastAPI: auth (nonce + chữ ký ví), faction, reward, blockchain
frontend/     React + Vite + @mysten/dapp-kit: connect ví, mint NFT, claim reward
blockchain/   Move package `history_game`: faction_nft.move, reward.move + unit tests
assets/nft/   factions.json — metadata chuẩn hoá từ Artist 1
scripts/      deploy-sui.sh, e2e_checks.py, wrapper SUI CLI qua Docker
docs/         blockchain.md — thiết kế contract, adapter, deploy, tích hợp
deployments/  sui-<env>.json — package/object ID sau mỗi lần deploy
```

## Yêu cầu

- Python 3.11+ (đang dùng 3.14), Node 20+ (đang dùng 24)
- SUI CLI 1.79+. Trên Windows bị Smart App Control chặn `sui.exe`, chạy CLI trong container Docker `sui-dev` (mount repo tại `/work`, cổng 9000/9123) và dùng wrapper `scripts/sui-docker.cmd`.

## Chạy backend

```bash
cd backend
python -m venv .venv && ./.venv/Scripts/pip install -r requirements.txt
cp .env.example .env          # điền package/object ID từ deployments/sui-<env>.json
./.venv/Scripts/python -m uvicorn app.main:app --reload --port 8000
```

## Chạy frontend

```bash
cd frontend
npm install
cp .env.example .env          # VITE_SUI_PACKAGE_ID, VITE_SUI_CATALOG_ID
npm run dev                   # http://localhost:5173
```

## Deploy blockchain

```bash
SUI_BIN=scripts/sui-docker.cmd bash scripts/deploy-sui.sh local     # hoặc: testnet
```

Kết quả ghi vào `deployments/sui-<env>.json` — copy các ID sang `backend/.env` và `frontend/.env`. Chi tiết contract, endpoint RPC và các luồng tích hợp: [docs/blockchain.md](docs/blockchain.md).

## Kiểm thử

```bash
# Move unit tests (9)
MSYS2_ARG_CONV_EXCL="*" docker exec -w /work/blockchain/sui sui-dev sui move test --build-env testnet

# Backend (18)
cd backend && ./.venv/Scripts/python -m pytest -q

# E2E on-chain (5 check: publish TX, mint, verify_ownership, metadata, reward)
backend/.venv/Scripts/python scripts/e2e_checks.py \
  --deployment deployments/sui-local.json --rpc http://127.0.0.1:9000 \
  --cli scripts/sui-docker.cmd --wallet <ví người chơi> --faction 1
```

## API

| Method | Path | Mô tả |
| --- | --- | --- |
| POST | `/auth/nonce` | cấp nonce + message cho ví ký |
| POST | `/auth/wallet` | verify chữ ký → tạo/lấy `Player` (Wallet → Player) |
| GET | `/factions` | danh sách faction từ `assets/nft/factions.json` |
| GET | `/players/{wallet}` | thông tin player + `nft_object_id` |
| POST | `/players/{wallet}/faction` | gắn faction/NFT sau khi verify TX & ownership (Faction → NFT) |
| POST | `/rewards/claim` | gửi reward on-chain, trả `tx_digest` (Battle → Reward) |
| GET | `/players/{wallet}/rewards` | lịch sử reward |
| GET | `/blockchain/sui/transaction/{digest}` | trạng thái TX để UI xác nhận (TX Digest → UI) |
| GET | `/health` | health check |

Swagger: http://localhost:8000/docs

## Biến môi trường

Backend (`backend/.env`, xem `backend/.env.example`): `SUI_NETWORK`, `SUI_RPC_URL`, `SUI_GRAPHQL_URL`, `SUI_PACKAGE_ID`, `SUI_CATALOG_ID`, `SUI_TREASURY_ID`, `SUI_FACTION_ADMIN_ID`, `SUI_REWARD_ADMIN_ID`, `SUI_CLI_PATH`, `SUI_GAS_BUDGET`, `REWARD_AMOUNT_MIST`, `NONCE_TTL_SECONDS`.

Frontend (`frontend/.env`, xem `frontend/.env.example`): `VITE_API_URL`, `VITE_SUI_NETWORK`, `VITE_SUI_RPC_URL`, `VITE_SUI_PACKAGE_ID`, `VITE_SUI_CATALOG_ID`.

Private key **không** nằm trong env: backend ký TX qua keystore của SUI CLI, người chơi ký qua ví (Sui Wallet / dapp-kit).

## Trạng thái đầu việc Dev 2 (SUI)

| # | Đầu việc | Nơi triển khai |
| --- | --- | --- |
| 1, 5 | Setup project, Move.toml, env | `blockchain/sui/Move.toml`, `scripts/` |
| 2, 3 | Wallet integration, connect/disconnect | `frontend/src/providers.tsx`, `hooks/useWallet.ts`, `components/WalletBar.tsx` |
| 4, 16 | Nonce → ký → verify → Player | `backend/app/api/auth.py`, `core/security.py`, `WalletBar.tsx` |
| 6, 7 | `faction_nft.move` + metadata chuẩn hoá | `blockchain/sui/sources/faction_nft.move`, `assets/nft/factions.json` |
| 8, 17 | `mint_faction()` → NFT object ID | `faction_nft.move`, `frontend/src/components/FactionSelect.tsx`, `POST /players/{wallet}/faction` |
| 9, 10 | `reward.move`, Battle → TX Digest | `blockchain/sui/sources/reward.move`, `POST /rewards/claim` |
| 11–13 | `sui_adapter.py`: `get_transaction`, `verify_ownership` | `backend/app/blockchain/` |
| 14 | Deploy Testnet | `scripts/deploy-sui.sh testnet` → `deployments/sui-testnet.json` |
| 15 | Test mint/reward/verify | `blockchain/sui/tests/`, `backend/tests/`, `scripts/e2e_checks.py` |
| 18, 19 | TX Digest → UI "Reward confirmed" | `backend/app/api/blockchain.py`, `frontend/src/components/RewardPanel.tsx` |
