# Vietnam History GameFi MVP

MVP game chiến thuật lấy lịch sử Việt Nam làm nội dung. Gameplay được xử lý off-chain; blockchain chỉ là lớp ownership và proof cho Faction NFT, reward và achievement.

## Phạm vi MVP

Người chơi kết nối ví, chọn faction, sở hữu Faction NFT, tham gia battle và nhận reward/achievement có thể xác minh on-chain. Marketplace, Land NFT, DAO phức tạp, staking nâng cao và blockchain game server không thuộc phạm vi MVP.

## Kiến trúc

```text
Player -> Web Game Client -> FastAPI Backend -> BlockchainAdapter
                                                |- SuiAdapter -> Sui Testnet
                                                `- SolanaAdapter -> Solana Devnet

PostgreSQL: player, game state, army, battle, quest, leaderboard, reward references
```

- Backend là modular monolith, không phải microservices.
- Domain logic chỉ dùng `BlockchainAdapter` và không import SDK Sui/Solana trực tiếp.
- `AdapterResolver` chọn adapter từ `chain = "sui" | "solana"`.
- Blockchain không chứa combat calculation, game state, army state hoặc leaderboard.
- NFT tạo identity/utility, không quyết định toàn bộ sức mạnh combat.

## Ranh giới dữ liệu

| Thành phần | Off-chain | On-chain |
| --- | :---: | :---: |
| Player profile | ✓ | |
| Army và game state | ✓ | |
| Combat calculation | ✓ | |
| Quest progress | ✓ | |
| Leaderboard | ✓ | |
| Faction ownership / Faction NFT | | ✓ |
| Reward và achievement | record | proof/transaction |

Backend quyết định player state, battle result và reward eligibility. Blockchain quyết định ownership và transaction status. Không lưu private key/seed phrase; wallet của người chơi ký message và transaction.

## Cấu trúc repository

```text
backend/                 FastAPI API, domain boundary và blockchain adapters
blockchain/sui/          Move package: faction NFT, reward và Move tests
blockchain/solana/       Anchor workspace/program scaffold
database/schema.sql      PostgreSQL schema có phân biệt chain
assets/nft/              Faction metadata
docs/                    Architecture, blockchain và API documentation
scripts/                 Sui/Solana deployment scripts
```

## Luồng wallet, NFT và reward

### Wallet authentication

1. Client gọi `POST /auth/nonce` với wallet và chain.
2. Backend phát nonce một lần, có thời hạn, cùng message challenge.
3. Wallet ký đúng message theo format crypto của Sui hoặc Solana.
4. Client gọi `POST /auth/wallet`.
5. Backend consume nonce trước, xác minh signature và tạo/đọc player theo `(chain, wallet)`.

### Faction NFT

1. Player chọn faction sau authentication.
2. Wallet ký và gửi mint transaction.
3. Backend xác minh transaction digest trên chain.
4. Backend xác minh asset thuộc wallet thực tế.
5. Backend lưu faction cùng ownership reference.

### Battle reward

1. Battle engine ở backend tính kết quả và eligibility.
2. Backend tạo claim flow theo chain.
3. Wallet ký transaction khi cần; backend lưu reference là `pending`.
4. Adapter kiểm tra chain thật và cập nhật `confirmed` hoặc `failed`.

## API cốt lõi

| Method | Endpoint | Vai trò |
| --- | --- | --- |
| POST | `/auth/nonce` | Tạo wallet challenge |
| POST | `/auth/wallet` | Xác thực signature/player |
| GET | `/players/{wallet}` | Đọc player |
| GET | `/factions` | Danh sách faction |
| POST | `/players/{wallet}/faction` | Lưu Faction NFT đã xác minh |
| POST | `/rewards/claim` | Reward flow sau battle |
| GET | `/players/{wallet}/rewards` | Reward references |
| GET | `/blockchain/{chain}/transaction/{digest}` | Kiểm tra transaction |

## Cấu hình

Sao chép `.env.example`; không commit secret.

```dotenv
SUI_NETWORK=testnet
SUI_RPC_URL=
SUI_PACKAGE_ID=
SUI_CATALOG_ID=
SOLANA_NETWORK=devnet
SOLANA_RPC_URL=
SOLANA_PROGRAM_ID=
```

## Chạy và kiểm thử

```bash
cd backend
python -m pip install -r requirements.txt
python -m pytest -q
uvicorn app.main:app --reload
```

```bash
cd blockchain/sui
sui move build
sui move test
```

```bash
cd blockchain/solana
anchor build
anchor test
```

Sau deploy, cập nhật package/program ID qua environment. Không hard-code ID hoặc secret trong domain service.

## Tài liệu

- `docs/architecture.md`: modular monolith và domain boundary.
- `docs/blockchain.md`: blockchain architecture và deployment notes.
- `docs/api.md`: API hiện có.
