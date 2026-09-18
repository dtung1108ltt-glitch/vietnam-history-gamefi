# Frontend Khởi Động Trước Khi Vào Game - Vietnam History GameFi MVP

Giao diện khởi động tiền-trận đấu (Pre-Game Launcher & Onboarding) cho dự án **Vietnam History GameFi MVP**, được thiết kế bám sát 100% tài liệu kiến trúc **FPD (PDF)** và domain model của repository.

---

## 1. Tính Năng Cốt Lõi Đã Triển Khai

### 1.1 Màn hình Mở đầu & Giới thiệu Hào Khí (Splash & Title Screen)
- **Mỹ thuật Cổ phong Hào khí Đại Việt**: Họa tiết Trống đồng Đông Sơn xoay tròn huyền ảo, chim Lạc tung cánh, rồng mây và ánh lửa chiến trường.
- **Hệ thống Âm thanh Tác chiến (Web Audio API Synthesized)**:
  - Tiếng trống trận trầm hùng khi tương tác thẻ bài.
  - Tiếng chiêng đồng vang rền khi mở modal và kết nối.
  - Tiếng tuốt gươm lệnh khi đúc ấn tín Faction NFT và xuất kích.
  - Nút bật/tắt âm thanh (Mute/Unmute) trên Header.
- **Chuyển đổi Mạng Khởi Trận**: Lựa chọn giữa **Sui Testnet** (Sui Move) và **Solana Devnet** (Anchor Rust).
- **Bộ giám sát Trạng thái API Backend**: Tự động ping `/health` để hiển thị trạng thái Trực Tuyến / Cục Bộ.

### 1.2 Mô-đun Xác thực Ví Đa Chuỗi (Multi-Chain Wallet Integration)
- **Chuẩn xác theo Mục 5.1 & 13 của tài liệu FPD**:
  1. Yêu cầu sinh mã Nonce & challenge message từ server: `POST /auth/nonce`.
  2. Ký mật mã (Cryptographic signature - Ed25519) off-chain thông qua Wallet Extension (Sui Wallet / Phantom) hoặc Sandbox Test Mode.
  3. Gửi chữ ký xác thực về backend: `POST /auth/wallet` để tải hoặc khởi tạo hồ sơ Tướng quân (`PlayerOut`).
  4. Duy trì trạng thái phiên đăng nhập (Session Persistence) trong `localStorage`.

### 1.3 Bàn Cờ Chiêu Mộ Tộc Hệ & Đúc Kim Ấn Faction NFT
- **5 Triều đại chuẩn hóa theo `assets/nft/factions.json` & PDF**:
  1. **Nhà Lý** (Common - 1009–1225): Khởi dựng Thăng Long, Cấm quân cận vệ (+10% Công, +20% Thủ, +10% Tốc).
  2. **Nhà Trần** (Rare - 1225–1400): Hào khí Đông A, Thủy binh Bát Trạch (+25% Công, +15% Thủ, +15% Tốc).
  3. **Nhà Lê** (Rare - 1428–1789): Khởi nghĩa Lam Sơn, Thiết kỵ Lam Sơn (+20% Công, +20% Thủ, +15% Tốc).
  4. **Tây Sơn** (Epic - 1778–1802): Thần tốc áo vải cờ đào, Tượng binh Hỏa hổ (+35% Công, +10% Thủ, +30% Tốc).
  5. **Nhà Nguyễn** (Legendary - 1802–1945): Thống nhất sơn hà, Thần cơ doanh hỏa mai (+30% Công, +25% Thủ, +20% Tốc).
- **Quy trình Đúc Ấn Tín Faction NFT**:
  - Gửi giao dịch đúc ấn tín lên blockchain (Sui/Solana).
  - Backend xác thực `tx_digest` và quyền sở hữu NFT on-chain qua `POST /players/{wallet}/faction`.
  - Hiệu ứng pháo hoa hoàng kim vinh danh Tướng quân phong hàm.

### 1.4 Sảnh Tiền Trạm Duyệt Quân (Pre-Game Staging Lobby)
- **Tổng Hành Dinh Tướng Quân**:
  - Thẻ định danh Thống soái: Địa chỉ ví rút gọn, Huy hiệu Faction NFT đã xác minh on-chain.
  - Thống kê Binh lực cơ bản: Combat Score (Lực lượng tác chiến off-chain), Binh chủng trấn phái.
  - Xem trước các chiến dịch lịch sử: *Chiến dịch Bạch Đằng Giang*, *Phá vây Rạch Gầm - Xoài Mút*.
  - Nút chuyển đổi phe triều đại linh hoạt.
  - Nút **"XUẤT QUÂN VÀO CHIẾN TRƯỜNG"**: Kích hoạt đếm ngược xuất trận và chuyển cảnh sang Gameplay Engine.

---

## 2. Cấu Trúc Thư Mục Chuẩn Kiến Trúc FPD

```text
frontend/
├── index.html                  # HTML template với typography Việt sử hào hùng
├── package.json                # Dependencies: React 18, Vite, Tailwind CSS, Lucide, Confetti
├── vite.config.ts              # Proxy kết nối FastAPI backend (http://127.0.0.1:8000)
├── tailwind.config.js          # Hệ màu hoàng triều (Imperial Crimson, Royal Gold, Jade, Obsidian)
├── public/
│   └── drum_icon.svg           # Icon Trống đồng Đông Sơn dát vàng
└── src/
    ├── main.tsx                # Entry point
    ├── App.tsx                 # Điều phối state machine luồng khởi động
    ├── index.css               # Nền hoa văn Trống đồng, viền vàng cổ phong, glow effects
    ├── types/
    │   └── index.ts            # Type definitions (Player, Faction, ChainType, Nonce, Verify)
    ├── services/
    │   ├── api.ts              # Giao tiếp FastAPI (Auth, Faction, Player, Health) + Fallback data
    │   ├── sui.ts              # Sui Wallet Adapter (Sui Move testnet & sandbox)
    │   └── solana.ts           # Solana Wallet Adapter (Phantom/Solflare & sandbox)
    ├── hooks/
    │   ├── useWallet.ts        # Quản lý kết nối ví, nonce challenge & signature
    │   ├── useFaction.ts       # Quản lý nạp danh sách phe & mint Faction NFT
    │   └── useAudio.ts         # Hệ thống âm thanh tổng hợp Web Audio (Trống, Chiêng, Kiếm)
    └── components/
        ├── Common/
        │   ├── Header.tsx      # Thanh điều hướng cổ phong, trạng thái mạng & âm thanh
        │   └── DrumOrnament.tsx# Vector SVG Trống đồng Ngọc Lũ xoay chậm
        ├── Wallet/
        │   └── WalletModal.tsx # Hộp thoại kết nối Sui/Solana & xác thực chữ ký
        ├── FactionCard/
        │   └── FactionCard.tsx # Thẻ bài triều đại 3D, chỉ số chiến thuật & bối cảnh
        └── PreGame/
            ├── SplashScreen.tsx    # Màn hình mở đầu & đề tự hào khí
            ├── FactionSelection.tsx# Bàn cờ chiêu mộ tộc hệ & đúc kim ấn
            ├── PreGameLobby.tsx    # Sảnh tiền trạm duyệt quân trước xuất kích
            └── BattleTransition.tsx# Chuyển cảnh tiến vào trận địa chiến thuật
```

---

## 3. Hướng Dẫn Khởi Chạy

### 3.1 Cài đặt & Chạy Frontend Development Server
```bash
cd frontend
npm install
npm run dev
```
Trình duyệt sẽ mở tại: `http://localhost:5173`

### 3.2 Build kiểm tra Production
```bash
cd frontend
npm run build
```

### 3.3 Chạy song song cùng Backend FastAPI (Tùy chọn)
Trong một terminal khác:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```
Frontend đã được cấu hình proxy tự động chuyển tiếp `/api` hoặc gọi trực tiếp `http://127.0.0.1:8000`. Khi backend chưa chạy, Frontend vẫn hoạt động độc lập trơn tru nhờ lớp Sandbox Fallback thông minh.
