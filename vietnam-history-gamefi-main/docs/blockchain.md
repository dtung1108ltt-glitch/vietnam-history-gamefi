# Blockchain — kiến trúc đa chuỗi

Track Dev 2: contract Move, adapter thống nhất cho backend và hai triển khai
Sui Testnet/Solana Devnet. Backend domain chỉ gọi `AdapterResolver.get(chain)`;
không import SDK Sui hoặc Solana trực tiếp.

> Lưu ý bảo mật: mint/reward của Solana không cho phép backend ký bằng keypair.
> Người chơi phải ký giao dịch từ ví; backend chỉ xác minh digest và ownership.

## 1. Cấu trúc

```
blockchain/sui/
├── Move.toml                  # package history_game, edition 2024.beta, dep Sui framework/testnet
├── sources/faction_nft.move   # Faction NFT + catalog + admin
├── sources/reward.move        # Reward treasury + send_reward
└── tests/                     # Move unit tests (test_scenario)
backend/app/blockchain/
├── interface.py               # BlockchainAdapter (contract chung với Dev 1 - Solana)
└── sui_adapter.py             # SuiAdapter: đọc qua GraphQL/JSON-RPC, ghi qua `sui client call`
scripts/
├── deploy-sui.sh              # publish + register faction + tạo/nạp treasury -> deployments/sui-<env>.json
├── e2e_checks.py              # 5 check on-chain: publish TX, mint, verify_ownership, metadata, reward
├── sui-docker.cmd/.sh         # wrapper chạy SUI CLI trong container `sui-dev`
assets/nft/factions.json       # metadata chuẩn hoá từ Artist 1 (tên/rarity/ảnh)
```

## 2. `faction_nft.move`

Object:

| Object | Quyền sở hữu | Vai trò |
| --- | --- | --- |
| `FactionAdmin` | owned (deployer) | capability đăng ký faction / mint hộ người chơi |
| `FactionCatalog` | shared | bảng `names`/`rarities`/`images`/`owners`/`supply` |
| `FactionNft` | owned, `key, store` | NFT của người chơi: `faction_id`, `faction_name`, `rarity`, `image`, `owner` |
| `FACTION_NFT` | one-time witness | runtime tự tạo và truyền vào `init` lúc publish |

Hàm entry:

| Hàm | Ai gọi | Ghi chú |
| --- | --- | --- |
| `register_faction(admin, catalog, faction_id, name, rarity, image)` | admin | metadata lấy từ `assets/nft/factions.json`; trùng `faction_id` → abort 4 |
| `mint_faction(catalog, faction_id, ctx)` | người chơi (frontend ký TX) | mint cho `tx_context::sender` |
| `mint_faction_for(admin, catalog, faction_id, recipient, ctx)` | backend (trả gas) | mint hộ ví người chơi |
| `transfer_faction(catalog, nft, to, ctx)` | chủ NFT | cập nhật lại ánh xạ owner trong catalog |

Ràng buộc: mỗi wallet chỉ sở hữu **1 faction** (kiểm tra bằng `catalog.owners`).

Event: `FactionMinted { faction_id, owner, nft_id }`, `FactionTransferred { nft_id, faction_id, from, to }`.

Abort code: `1` faction chưa đăng ký · `2` ví đã có faction · `3` không phải chủ NFT · `4` faction đã tồn tại · `5` người nhận đã có faction.

`init` còn tạo `Display` cho `FactionNft` (`name`/`image`/`description`) để explorer hiển thị metadata.

> Lưu ý one-time witness: struct phải tên là module viết hoa, **không có field**, chỉ `drop`, và không được khởi tạo thủ công — vi phạm sẽ abort `ENotOneTimeWitness (0)` khi publish. Unit test không đi qua `init` thật nên dùng `package::test_claim` với `FactionNftTestOtw` (`#[test_only]`).

## 3. `reward.move`

| Object / hàm | Mô tả |
| --- | --- |
| `RewardAdmin` | capability của backend reward service |
| `create_treasury(admin, ctx)` | tạo `RewardTreasury` shared (`vault: Balance<SUI>`, `total_paid`, `reward_count`) |
| `fund_treasury(admin, treasury, payment: Coin<SUI>)` | nạp SUI vào vault |
| `send_reward(admin, treasury, recipient, amount, battle_id, ctx)` | Battle Result → Reward: rút `amount` MIST, cộng `total_paid`/`reward_count`, emit event, chuyển coin cho người thắng |
| `vault_value` / `total_paid` / `reward_count` | getter đọc trạng thái treasury |

Event: `RewardSent { recipient, amount, battle_id, treasury_id }` — cùng TX Digest là bằng chứng reward đã lên chain.

Abort code: `1` treasury không đủ SUI · `2` `amount == 0`.

## 4. Adapter thống nhất (`BlockchainAdapter`)

Domain logic chỉ phụ thuộc interface, không import SDK của chain cụ thể — Dev 1 implement bản Solana song song.

```python
chain_name() -> str
mint_faction(recipient, faction_id) -> (tx_digest, nft_object_id)
send_reward(recipient, amount, battle_id) -> tx_digest
get_transaction(digest) -> TransactionInfo | None     # .succeeded == (status == "success")
verify_ownership(wallet, object_id) -> bool
get_faction_nfts(wallet) -> list[NftInfo]
```

`SuiAdapter`:

- **Đọc**: GraphQL trước, fallback JSON-RPC (`sui_getTransactionBlock`, `sui_getObject`, `suix_getOwnedObjects`). Hiện không có public GraphQL/JSON-RPC nào của Mysten cho testnet, nên mặc định chỉ dùng JSON-RPC qua endpoint cộng đồng.
- **Ghi**: subprocess `sui client call … --json`; private key nằm trong keystore của SUI CLI, **không** nhúng vào code hay env.
- Thiếu `SUI_PACKAGE_ID`/`SUI_CATALOG_ID`/`SUI_TREASURY_ID`/… → `SuiAdapterError` yêu cầu chạy deploy script trước.

## 5. Deploy

```bash
# Local (SUI CLI chạy trong container docker `sui-dev`, repo mount tại /work)
SUI_BIN=scripts/sui-docker.cmd bash scripts/deploy-sui.sh local

# Testnet
SUI_BIN=scripts/sui-docker.cmd bash scripts/deploy-sui.sh testnet
```

Script thực hiện: switch env → faucet → `publish` (local dùng `test-publish --build-env testnet`) → `register_faction` cho 5 faction trong `assets/nft/factions.json` → `create_treasury` → `fund_treasury` (1 SUI) → ghi `deployments/sui-<env>.json`:

```json
{
  "network": "local",
  "deployer": "0x…",
  "package_id": "0x…",
  "tx_digest": "…",
  "faction_admin_id": "0x…",
  "catalog_id": "0x…",
  "reward_admin_id": "0x…",
  "treasury_id": "0x…"
}
```

Các giá trị này map thẳng sang `backend/.env` (`SUI_PACKAGE_ID`, `SUI_CATALOG_ID`, `SUI_TREASURY_ID`, `SUI_FACTION_ADMIN_ID`, `SUI_REWARD_ADMIN_ID`) và `frontend/.env` (`VITE_SUI_PACKAGE_ID`, `VITE_SUI_CATALOG_ID`).

Endpoint: `https://fullnode.testnet.sui.io:443` **đã ngừng phục vụ JSON-RPC công khai** (trả `-32601 Method not found`). RPC testnet đang dùng: `https://testnet.suiet.app` (chain id `4c78adac`), override bằng `SUI_TESTNET_RPC`. Nếu alias `testnet` trong `~/.sui/sui_config/client.yaml` còn trỏ URL cũ, script sẽ dừng và báo cách sửa — `sui client new-env` không ghi đè alias có sẵn.

## 6. Kiểm thử

```bash
# Move unit tests (9 test): mint theo catalog, chặn mint lần 2, admin mint hộ, transfer, reward
MSYS2_ARG_CONV_EXCL="*" docker exec -w /work/blockchain/sui sui-dev sui move test --build-env testnet

# Backend adapter + API (pytest, 18 test)
cd backend && ./.venv/Scripts/python -m pytest -q

# E2E on-chain sau khi deploy (5 check)
backend/.venv/Scripts/python scripts/e2e_checks.py \
  --deployment deployments/sui-local.json \
  --rpc http://127.0.0.1:9000 \
  --cli scripts/sui-docker.cmd \
  --wallet <địa chỉ người chơi> --faction 1
```

`e2e_checks.py` xác nhận: publish TX success · `mint_faction` trả về NFT object ID · `verify_ownership` đúng chủ = True / ví lạ = False · đọc được `faction_id`/`faction_name`/`rarity` · `send_reward` success và event chứa `battle_id`.

## 7. Bốn luồng tích hợp

| # | Luồng | Điểm nối |
| --- | --- | --- |
| 1 | Wallet → Player | `POST /auth/nonce` → ví ký personal message → `POST /auth/wallet` (`verify_personal_message` + nonce một lần) → `PlayerOut` |
| 2 | Faction → NFT | frontend `mint_faction` qua dapp-kit → lấy `objectId` từ `objectChanges` → `POST /players/{wallet}/faction` (backend verify TX + ownership) → `nft_object_id` |
| 3 | Battle → Reward | `POST /rewards/claim` → `send_reward` on-chain → `RewardOut.tx_digest` |
| 4 | TX Digest → UI | frontend poll `GET /blockchain/sui/transaction/{digest}` → `status == "success"` → "Reward confirmed on-chain" |
