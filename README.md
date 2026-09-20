# Hào Khí Đại Việt — hướng tới DeFi minh bạch

Sản phẩm hướng tới **thiết kế tài chính phi tập trung minh bạch, an toàn và dễ tiếp cận**: thanh toán, tiết kiệm, lending, DEX, treasury dashboard, DAO tooling. Lớp lịch sử Việt Nam và Faction NFT giữ bản sắc / định danh; lớp on-chain phải công khai số liệu, không custody khóa, và dùng được bằng tiếng Việt trước khi ký.

MVP hiện tại vẫn là vertical slice GameFi (ví → NFT → chiến dịch). Màn **Kinh tế on-chain** là prototype UI của sáu module DeFi; adapter Sui/Solana hiện có sẽ được nối khi từng module lên chain.

> Trạng thái repo hiện tại: **đang phát triển**. README mô tả phần đã chạy và phần còn thiếu. Hướng DeFi: [`docs/defi.md`](docs/defi.md).

## 1. Game là gì

Người chơi kết nối ví (Sui hoặc Solana), chọn một trong **5 triều đại lịch sử Việt Nam** làm faction, sở hữu Faction NFT tương ứng, rồi bước vào trận chiến để nhận thưởng. Faction không quyết định toàn bộ sức mạnh chiến đấu — nó tạo identity/utility, giữ trải nghiệm công bằng cho người chơi F2P.

| Faction | Rarity | Bối cảnh lịch sử |
| --- | --- | --- |
| Nhà Lý | Common | Kỷ nguyên dựng kinh thành Thăng Long |
| Nhà Trần | Rare | Ba lần kháng chiến chống Nguyên Mông |
| Nhà Lê | Rare | Khởi nghĩa Lam Sơn thống nhất giang sơn |
| Tây Sơn | Epic | Thần tốc đại phá quân Thanh |
| Nhà Nguyễn | Legendary | Triều đại phong kiến cuối cùng |

Dữ liệu faction (tên, rarity, ảnh, mô tả) được tách hoàn toàn khỏi code ở `assets/nft/factions.json`, để đội nội dung/artist cập nhật mà không cần đụng vào backend.

### Luồng chơi dự kiến (theo thiết kế MVP)

```text
Connect Wallet -> Chọn Chain (Sui/Solana) -> Xác thực chữ ký
    -> Chọn Faction -> Mint Faction NFT -> Xác minh ownership
    -> Vào trận (Battle) -> Nhận Reward -> Xem NFT / thành tích on-chain
```

### Luồng chơi hiện có trong repo (thực tế đã code)

```text
Splash Screen -> Connect Wallet (chọn chain) -> Xác thực chữ ký
    -> Chọn Faction -> Mint Faction NFT -> Pre-Game Lobby
    -> Battle Transition (màn chuyển cảnh) -> [chưa có Battle Engine thật]
```

Phần **Wallet → Faction NFT** đã có đủ 2 đầu (frontend + backend + smart contract). Phần **Battle → Reward → Leaderboard** hiện mới dừng ở màn hình chuyển cảnh, chưa có battle engine, chưa có API `/battles`, `/leaderboard`, chưa có bảng `armies`/`battles`/`quests`/`leaderboard` trong database.

## 2. Kiến trúc

```text
Player
  -> Web Game Client (React + TypeScript)
  -> FastAPI Backend (Auth / Faction / Reward / Blockchain)
  -> BlockchainAdapter (interface chung)
       |- SuiAdapter    -> Sui Testnet
       `- SolanaAdapter -> Solana Devnet

PostgreSQL (thiết kế sẵn ở database/schema.sql):
  player, faction, army, battle, quest, leaderboard, reward references
```

- Backend là modular monolith, không phải microservices.
- Domain logic chỉ dùng `BlockchainAdapter` và không import SDK Sui/Solana trực tiếp.
- `AdapterResolver` chọn adapter từ `chain = "sui" | "solana"` đã lưu theo player, không tin `chain` do client tự gửi ở các thao tác ghi.
- Blockchain không chứa combat calculation, game state, army state hoặc leaderboard — chỉ ownership, reward, achievement.
- NFT tạo identity/utility, không quyết định toàn bộ sức mạnh combat.

> **Lưu ý triển khai hiện tại:** `PostgreSQL` mới ở dạng schema thiết kế (`database/schema.sql`), backend đang chạy với in-memory store (`app/core/store.py`) nên dữ liệu mất khi restart — chưa phải trạng thái sẵn sàng production.

## 3. Ranh giới dữ liệu on-chain / off-chain

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

## 4. Cấu trúc repository

```text
frontend/                Web game client (React + TypeScript)
  src/services/sui.ts      Kết nối/ký giao dịch Sui
  src/services/solana.ts   Kết nối/ký giao dịch Solana
  src/hooks/useWallet.ts   Chọn chain, auth theo wallet
  src/hooks/useFaction.ts  Chọn/mint Faction NFT
backend/                 FastAPI API, domain boundary và blockchain adapters
blockchain/sui/          Move package: faction NFT, reward và Move tests
blockchain/solana/       Anchor program (history_game): mint/reward/achievement
database/schema.sql      PostgreSQL schema có phân biệt chain
assets/nft/              Faction metadata (tách khỏi code)
docs/                    Architecture, blockchain, API doc và báo cáo đánh giá
scripts/                 Sui/Solana deployment scripts
unity-client/            Client Unity thử nghiệm — gọi backend thật, KHÔNG phải client chính
```

> **`unity-client/` là gì:** một client Unity thay thế/bổ sung cho `frontend/`
> (không phải bản thay thế chính thức), gọi thật `GET /factions`,
> `GET /players/{wallet}`, `POST /auth/nonce`, `POST /auth/wallet`,
> `POST /players/{wallet}/faction`, `POST /rewards/claim` qua `UnityWebRequest`
> — không còn dữ liệu giả kiểu `Debug.Log` như bản nháp cũ. **Giới hạn còn lại:**
> việc ký chữ ký ví (bắt buộc để `POST /auth/wallet` thành công) chưa thể tự
> làm trong Unity C# thuần — cần build WebGL kèm bridge tới ví trình duyệt,
> hoặc tích hợp SDK ví mobile qua deep link. Domain Battle/Army/Quest/
> Leaderboard vẫn mô phỏng cục bộ vì bản thân backend chưa có domain này. Chi
> tiết đầy đủ: `unity-client/README.md`.

> **Cảnh báo khi test frontend độc lập:** nếu trình duyệt không có extension ví (Sui Wallet / Phantom), `services/sui.ts` và `services/solana.ts` hiện **tự động fallback sang địa chỉ/chữ ký/transaction giả lập** thay vì báo lỗi rõ ràng. Vì backend luôn xác minh transaction qua RPC thật, flow mint sẽ **không thành công end-to-end** trong chế độ này dù UI trông như chạy được — chỉ dùng để xem giao diện, không dùng để đánh giá tính năng blockchain.

## 5. Luồng wallet, NFT và reward

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

## 6. API cốt lõi

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

Các API theo thiết kế MVP nhưng **chưa được triển khai**: `GET /players/{wallet}/army`, `POST /battles`, `GET /battles/{battle_id}`, `GET /leaderboard` — vì domain Battle/Army/Leaderboard chưa tồn tại.

## 7. Cấu hình

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

## 8. Chạy và kiểm thử

```bash
cd backend
python -m pip install -r requirements.txt
python -m pytest -q
python -m uvicorn app.main:app --reload --port 8000
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

## 9. Trạng thái, giới hạn hiện tại & tài liệu

### Đã hoàn thiện
- Chọn 1-trong-2 chain (Sui / Solana) ở cả frontend lẫn backend qua `AdapterResolver`.
- Wallet authentication bằng chữ ký (nonce một lần, có hạn dùng) cho cả 2 chain.
- Flow chọn Faction → mint NFT → backend xác minh ownership thật qua RPC trước khi lưu.
- Smart contract Move (Sui) cho faction NFT + reward, và chương trình Anchor (Solana) cho mint/reward/achievement.
- 24 test tự động cho backend (`pytest`), pass toàn bộ.
- `unity-client/`: client Unity thử nghiệm, gọi thật các API đọc/ghi kể trên qua `UnityWebRequest` (thay bản nháp `Debug.Log` cũ) — chưa gồm bước ký ví thật, xem giới hạn #6 dưới đây.

### Giới hạn đã biết (ưu tiên xử lý)
1. **Wallet mock ngầm ở frontend** khi không có extension ví — không cảnh báo người dùng (xem cảnh báo ở mục 4).
2. **`POST /rewards/claim` lỗi không kiểm soát (HTTP 500) với player ở Solana** — `SolanaAdapter` chủ động từ chối ký reward phía server nhưng chưa có exception handler.
3. **Domain Battle/Army/Quest/Leaderboard chưa tồn tại** — cả backend, database lẫn frontend. Đây là phần lớn nhất còn thiếu để game chơi được trọn vòng lặp.
4. Backend đang lưu dữ liệu **in-memory**, chưa nối PostgreSQL dù `database/schema.sql` đã thiết kế sẵn.
5. `SOLANA_PROGRAM_ID` chưa deploy thật (còn placeholder); thiếu `achievement.move` phía Sui.
6. **`unity-client/` chưa ký được chữ ký ví thật** — Unity không có SDK ví Sui/Solana chính thức tương đương bản web; cần build WebGL kèm bridge sang ví trình duyệt, hoặc SDK ví mobile qua deep link.

Danh sách đầy đủ (kèm mức ưu tiên P0/P1/P2 và khuyến nghị thứ tự xử lý) nằm ở [`docs/architecture-review.md`](docs/architecture-review.md).

### Roadmap tiếp theo
1. Vá 2 lỗi P0 dễ nhất: exception handling cho reward Solana + bug nhỏ trong `solana_adapter.py`.
2. Thay lớp ví mock ở frontend bằng SDK ví thật (`@mysten/dapp-kit`, `@solana/wallet-adapter-*`).
3. Triển khai DeFi theo thứ tự an toàn: **thanh toán** (chuyển khoản + chứng từ) → **treasury dashboard** (đọc quỹ công khai) → **tiết kiệm** → **DEX** → **lending** → **DAO tooling**.
4. Xây domain Battle: schema DB (`armies`, `battles`), `battle_engine` service, API `POST /battles`, `GET /leaderboard`, UI tương ứng.
5. Nối backend vào PostgreSQL thật theo `database/schema.sql`.
6. Deploy chương trình Anchor lên Solana Devnet, hoàn thiện `achievement.move`.

### Tài liệu khác
- `docs/architecture.md`: modular monolith và domain boundary.
- `docs/blockchain.md`: blockchain architecture và deployment notes.
- `docs/api.md`: API hiện có.
- `docs/defi.md`: nguyên tắc thiết kế DeFi (minh bạch, an toàn, dễ tiếp cận) và sáu module.
