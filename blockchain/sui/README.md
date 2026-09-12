# Việt Sử Chiến Ký — MVP GameFi lịch sử Việt Nam (phần SUI)

MVP theo tài liệu *MVP System Architecture Design*: backend FastAPI (modular monolith), frontend React, hợp đồng SUI Move và tầng adapter blockchain thống nhất.

> 📌 **Mới lần đầu chạy dự án này?** Đọc thẳng phần [Hướng dẫn chạy từ đầu (dành cho người mới)](#hướng-dẫn-chạy-từ-đầu-dành-cho-người-mới) — đi từng bước, có xử lý sẵn các lỗi thường gặp trên Windows.

```
backend/      FastAPI: auth (nonce + chữ ký ví), faction, reward, blockchain
frontend/     React + Vite + @mysten/dapp-kit: connect ví, mint NFT, claim reward
blockchain/   Move package `history_game`: faction_nft.move, reward.move + unit tests
assets/nft/   factions.json — metadata chuẩn hoá từ Artist 1
scripts/      deploy-sui.sh, e2e_checks.py, wrapper SUI CLI qua Docker
docs/         blockchain.md — thiết kế contract, adapter, deploy, tích hợp
deployments/  sui-<env>.json — package/object ID sau mỗi lần deploy
```

---

## Yêu cầu cài đặt trước

| Công cụ | Phiên bản | Vì sao cần | Kiểm tra đã cài chưa |
|---|---|---|---|
| **Python** | 3.11+ | chạy backend FastAPI | `python --version` |
| **Node.js** | 20+ | chạy frontend React | `node --version` |
| **Docker Desktop** | mới nhất | chạy SUI CLI trong container (xem lý do bên dưới) | `docker --version` |
| **Git for Windows** (có Git Bash) | mới nhất | chạy các script `.sh` | mở Start Menu tìm "Git Bash" |

⚠️ **Vì sao phải chạy SUI CLI qua Docker?** Trên nhiều máy Windows, Windows Defender **Smart App Control** chặn thẳng `sui.exe` không cho chạy. Cách ổn định nhất là chạy SUI CLI **bên trong 1 container Docker** tên `sui-dev`, và gọi vào nó qua script wrapper `scripts/sui-docker.cmd`. README này giả định bạn đi theo hướng đó.

---

## Hướng dẫn chạy từ đầu (dành cho người mới)

### Bước 0 — Hai loại cửa sổ dòng lệnh, đừng nhầm

Trên Windows có **2 loại terminal khác nhau**, và lệnh của 2 loại này **không dùng chung được**:

| Loại | Nhận biết prompt | Dùng để chạy |
|---|---|---|
| **cmd.exe** (Command Prompt) | `D:\tung\Gamefi>` | các lệnh `.venv\Scripts\python ...`, `docker ...` (dùng dấu `\`) |
| **Git Bash** | `user@MACHINE MINGW64 /d/tung/Gamefi (main)` | các script `.sh`, các lệnh có biến môi trường kiểu `VAR=value command` (dùng dấu `/`) |

Mẹo mở Git Bash nhanh: vào đúng thư mục trong File Explorer → chuột phải → **"Git Bash Here"**.

### Bước 1 — Chạy backend (cmd.exe)

```bat
cd blockchain\sui\backend
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env
```

Mở file `.env` vừa tạo, điền các ID SUI (xem [Bước 4](#bước-4--deploy-contract-lấy-object-id) nếu chưa deploy lần nào — có thể để trống trước, quay lại điền sau).

Chạy server (⚠️ **cổng 8000 có thể bị Windows chặn** — lỗi `WinError 10013`; nếu gặp, đổi sang cổng khác như 8001):

```bat
.venv\Scripts\python -m uvicorn app.main:app --reload --port 8001
```

Mở trình duyệt: `http://127.0.0.1:8001/docs` để xem/thử API (Swagger UI). Trang gốc `/` báo `Not Found` là **bình thường**, không phải lỗi.

Giữ cửa sổ này chạy — mở terminal **mới** cho các bước sau.

### Bước 2 — Chạy test backend (xác nhận cài đặt đúng)

```bat
cd blockchain\sui\backend
.venv\Scripts\python -m pytest -q
```
Kỳ vọng: `18 passed`.

### Bước 3 — Chuẩn bị container SUI CLI

Mở **Git Bash**, `cd` vào đúng `blockchain/sui` (không phải thư mục gốc repo):

```bash
cd /d/tung/Gamefi/blockchain/sui
docker run -d --name sui-dev -v "$PWD:/work" -w /work ubuntu:22.04 sleep infinity
```

> Nếu báo `container name "/sui-dev" already in use` — nghĩa là đã có sẵn rồi, dùng luôn, không cần tạo lại. Kiểm tra bằng `docker ps -a --filter "name=sui-dev"`.

Cài SUI CLI trong container (nếu image chưa có sẵn — kiểm tra bằng `docker exec sui-dev sui --version` trước, nếu báo `command not found` mới cần cài; cách cài nhanh nhất là dùng image có sẵn SUI CLI như `mysten/sui-tools:testnet` thay vì `ubuntu:22.04` ở trên).

Chạy thử Move unit test (lần đầu sẽ chậm vì phải tải dependency):

```bash
export MSYS2_ARG_CONV_EXCL="*"
scripts/sui-docker.cmd move test --build-env testnet
```

⚠️ **Luôn nhớ `export MSYS2_ARG_CONV_EXCL="*"` trước mỗi lệnh `docker exec ...` gọi trong Git Bash.** Thiếu dòng này, Git Bash sẽ tự "dịch" đường dẫn kiểu `/work/blockchain/sui` sang định dạng Windows và làm hỏng lệnh, gây lỗi khó hiểu như `Cwd must be an absolute path`.

Kỳ vọng: `Test result: OK. Total tests: 9; passed: 9; failed: 0`.

### Bước 4 — Deploy contract, lấy Object ID

**Khởi động mạng SUI local** trong container (mất khoảng 30–60 giây để sẵn sàng lần đầu):

```bash
docker exec -d sui-dev sui start --with-faucet --force-regenesis
```

Kiểm tra đã sẵn sàng chưa (lặp lại tới khi thấy JSON trả về, đừng vội nếu báo `Connection refused`):

```bash
curl -s -X POST http://127.0.0.1:9000 -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"sui_getChainIdentifier","params":[]}'
```

**Deploy:**

```bash
export MSYS2_ARG_CONV_EXCL="*"
SUI_BIN=scripts/sui-docker.cmd bash scripts/deploy-sui.sh local
```

> ⚠️ **Lỗi thường gặp:** `Ephemeral publication file "Pub.local.toml" has chain-id ... it cannot be used to publish to chain with id ...` — xảy ra khi bạn từng publish thử trước đó rồi sau đó tạo lại mạng local (`--force-regenesis`) nên chain-id đổi. Xoá file cũ **từ bên trong container** rồi deploy lại:
> ```bash
> docker exec sui-dev rm -f /work/blockchain/sui/Pub.local.toml
> ```

Kết quả deploy được ghi vào `deployments/sui-local.json`. **Copy các ID trong file này** vào `backend/.env` và `frontend/.env` (xem mục [Biến môi trường](#biến-môi-trường)).

Muốn deploy testnet thay vì local, xem cảnh báo ở mục [Deploy Testnet công khai](#deploy-testnet-công-khai--lưu-ý-quan-trọng) bên dưới trước khi thử.

### Bước 5 — Chạy frontend

```bash
cd frontend
npm install
cp .env.example .env    # điền VITE_SUI_PACKAGE_ID, VITE_SUI_CATALOG_ID từ deployments/sui-local.json
npm run dev             # http://localhost:5173
```

Cài extension **Sui Wallet** trên Chrome, trỏ mạng về `http://127.0.0.1:9000`, xin coin test qua faucet của container:
```bash
curl -X POST http://127.0.0.1:9123/gas -H 'Content-Type: application/json' \
  -d '{"FixedAmountRequest":{"recipient":"<địa_chỉ_ví_của_bạn>"}}'
```

---

## Việc cần làm mỗi khi mở lại dự án (sau khi tắt máy)

1. Mở Docker Desktop, đợi chạy xong.
2. Kiểm tra `sui-dev` còn sống: `docker ps -a --filter "name=sui-dev"`. Nếu `Exited`, khởi động lại: `docker start sui-dev`.
3. Nếu dùng mạng **local**, node SUI mất trạng thái sau khi container restart → chạy lại `sui start --with-faucet --force-regenesis` và **deploy lại** (Bước 4) — mạng local không lưu dữ liệu qua các lần khởi động lại theo mặc định.
4. Chạy lại backend (Bước 1) và frontend (Bước 5).

---

## Deploy Testnet công khai — lưu ý quan trọng

```bash
export MSYS2_ARG_CONV_EXCL="*"
SUI_BIN=scripts/sui-docker.cmd bash scripts/deploy-sui.sh testnet
```

⚠️ **Tính đến thời điểm viết README này (9/2026), hạ tầng JSON-RPC công khai của Sui đang trong giai đoạn bị khai tử dần** (Sui Foundation tắt JSON-RPC testnet công khai từ 7/2026, dự kiến gỡ hẳn khỏi phần mềm node giữa 10/2026). Vì vậy:

- Endpoint RPC cộng đồng mặc định trong script (`https://testnet.suiet.app`) **có thể không ổn định hoặc ngừng hoạt động** — nếu gặp lỗi kiểu `protocol error: received message with invalid compression flag`, đó là dấu hiệu RPC đang gặp sự cố, không phải lỗi ở phía bạn.
- **Khuyến nghị:** dùng **mạng local** (Bước 4) để phát triển và test hàng ngày — nhanh, miễn phí, không phụ thuộc hạ tầng bên ngoài. Chỉ deploy testnet khi cần demo công khai.
- Nếu bắt buộc phải deploy testnet mà RPC mặc định lỗi, thử đổi RPC khác bằng `sui client new-env --alias <tên> --rpc <url>` rồi `sui client switch --env <tên>` — hỏi kênh Discord chính thức của Sui (`discord.gg/sui`, kênh `#testnet-rpc`) để biết endpoint cộng đồng nào đang ổn định nhất tại thời điểm bạn đọc README này, vì tình hình có thể đã thay đổi.

---

## Kiểm thử

```bash
# Move unit tests (9 test) — nhớ export MSYS2_ARG_CONV_EXCL="*" trước
docker exec -w /work/blockchain/sui sui-dev sui move test --build-env testnet

# Backend (18 test)
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

Swagger: `http://127.0.0.1:8001/docs` (đổi port cho khớp port bạn đang chạy).

## Biến môi trường

Backend (`backend/.env`, xem `backend/.env.example`): `SUI_NETWORK`, `SUI_RPC_URL`, `SUI_GRAPHQL_URL`, `SUI_PACKAGE_ID`, `SUI_CATALOG_ID`, `SUI_TREASURY_ID`, `SUI_FACTION_ADMIN_ID`, `SUI_REWARD_ADMIN_ID`, `SUI_CLI_PATH`, `SUI_GAS_BUDGET`, `REWARD_AMOUNT_MIST`, `NONCE_TTL_SECONDS`.

Frontend (`frontend/.env`, xem `frontend/.env.example`): `VITE_API_URL`, `VITE_SUI_NETWORK`, `VITE_SUI_RPC_URL`, `VITE_SUI_PACKAGE_ID`, `VITE_SUI_CATALOG_ID`.

Private key **không** nằm trong env: backend ký TX qua keystore của SUI CLI, người chơi ký qua ví (Sui Wallet / dapp-kit).

---

## Xử lý sự cố thường gặp (Troubleshooting)

| Triệu chứng | Nguyên nhân | Cách xử lý |
|---|---|---|
| `'.' is not recognized as an internal or external command` | Gõ cú pháp bash (`./...`, `#comment`) trong cmd.exe | Dùng cmd thì bỏ `./`, đổi `/` → `\`; hoặc chuyển hẳn sang Git Bash |
| `[WinError 10013] An attempt was made to access a socket...` | Cổng bị Windows/antivirus chặn | Đổi sang cổng khác (`--port 8001`), hoặc chạy cmd với quyền Administrator |
| `Cwd must be an absolute path` khi `docker exec` từ Git Bash | Git Bash tự dịch đường dẫn `/work/...` sang path Windows | Thêm `export MSYS2_ARG_CONV_EXCL="*"` trước lệnh |
| `Ephemeral publication file "Pub.local.toml" has chain-id ... cannot be used` | File cache publish cũ không khớp chain-id mới (sau `--force-regenesis`) | `docker exec sui-dev rm -f /work/blockchain/sui/Pub.local.toml` rồi deploy lại |
| `protocol error: received message with invalid compression flag...` khi publish testnet | RPC testnet công khai đang gặp sự cố/đã ngừng JSON-RPC | Ưu tiên dùng mạng **local** để phát triển; xem mục [Deploy Testnet công khai](#deploy-testnet-công-khai--lưu-ý-quan-trọng) |
| `Gas selection failed ... insufficient SUI balance` khi `split-coin` dù ví có nhiều SUI | Ví chỉ có 1 coin duy nhất, không đủ để vừa trả gas vừa split | Dùng `sui client pay-sui --input-coins <coin> --recipients <chính-ví-mình> --amounts <số-MIST>` thay cho `split-coin` |
| `Player chưa tồn tại` khi test API | Chưa hoàn tất luồng `auth/nonce` → ký → `auth/wallet` để tạo Player | Đây là hành vi đúng, không phải bug — làm đủ 2 bước trước |
| Deploy dừng im lặng, không báo lỗi | Có thể do output bị "nuốt" qua nhiều lớp Docker/MSYS lồng nhau | Chạy tay từng lệnh `sui client ...` thay vì qua script, thêm `< /dev/null` và redirect `2> file.err` để thấy lỗi thật |

---

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
| 14 | Deploy (✅ xác nhận trên local network; testnet công khai phụ thuộc hạ tầng RPC bên ngoài, xem lưu ý ở trên) | `scripts/deploy-sui.sh local` → `deployments/sui-local.json` |
| 15 | Test mint/reward/verify (9 Move test + 18 backend test đã chạy PASS) | `blockchain/sui/tests/`, `backend/tests/`, `scripts/e2e_checks.py` |
| 18, 19 | TX Digest → UI "Reward confirmed" | `backend/app/api/blockchain.py`, `frontend/src/components/RewardPanel.tsx` |

Chi tiết thiết kế contract, endpoint RPC và các luồng tích hợp: [docs/blockchain.md](docs/blockchain.md).