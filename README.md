# 🇻🇳 Vietnam History GameFi — SUI MVP

A blockchain-integrated historical strategy game based on Vietnamese history.

The MVP focuses on a simple core experience:

**SUI Wallet → Connect → Select Faction → Own Faction NFT → Battle → Receive Reward → View Profile / Leaderboard**

Blockchain is used primarily as an ownership and proof layer, while the core gameplay state and battle calculation are handled by the backend.

---

## 1. Overview

Vietnam History GameFi is a historical strategy game that combines:

- Vietnamese historical factions
- Strategy-based combat
- Player progression
- SUI blockchain ownership
- NFT-based faction ownership
- On-chain reward proof

The project follows a **gameplay-first architecture**.

The blockchain does not directly control the entire game state. Instead:

- Backend manages gameplay state
- Database stores player/game data
- Battle Engine calculates combat results
- SUI manages ownership and blockchain proof
- Frontend provides the game interface and wallet interaction

---

## 2. MVP Scope

### Core Features

- SUI Wallet connection
- Wallet-based authentication
- Player profile
- Historical faction selection
- Faction NFT ownership
- PvE battle
- PvP battle
- Battle result
- Reward calculation
- SUI transaction reference
- Leaderboard

### Historical Factions

The MVP contains 6 factions:

| Faction | Example ID |
|---|---|
| Đinh | `dinh` |
| Lý | `ly` |
| Trần | `tran` |
| Lê | `le` |
| Nguyễn | `nguyen` |
| Lam Sơn | `lam_son` |

Each faction can have:

- Rarity
- Base attributes
- Combat modifiers
- Historical information

---

## 3. Architecture

```text
                         ┌──────────────────────┐
                         │      SUI Wallet      │
                         │  Connect / Sign Msg  │
                         └──────────┬───────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────┐
│                     Next.js Frontend                        │
│                                                             │
│  Wallet │ Factions │ Battle │ Profile │ Leaderboard         │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│                                                             │
│  Auth                                                     │
│  Faction                                                  │
│  Battle Engine                                            │
│  Reward                                                   │
│  Leaderboard                                              │
│  Blockchain Adapter                                       │
└──────────────┬───────────────────────┬──────────────────────┘
               │                       │
               ▼                       ▼
      ┌─────────────────┐      ┌─────────────────────┐
      │    Database     │      │     SUI Network     │
      │                 │      │                     │
      │ Player          │      │ Faction NFT         │
      │ Faction         │      │ Reward Transaction  │
      │ Army            │      │ Ownership Proof     │
      │ Battle          │      │                     │
      │ Reward          │      └─────────────────────┘
      │ Leaderboard     │
      └─────────────────┘
```

---

# 4. Technology Stack

## Frontend

### Next.js

Used as the main frontend framework.

Responsibilities:

- Application routing
- UI rendering
- Game interface
- Wallet integration
- API communication

Version:

```text
Next.js 14
```

### React

Used to build reusable UI components.

Main components:

```text
WalletConnect
FactionSelector
BattleArena
BattleResult
PlayerProfile
Leaderboard
```

### TypeScript

TypeScript is used throughout the frontend to provide:

- Static typing
- Better IDE support
- Safer API integration
- Reusable interfaces

Example:

```ts
interface Faction {
  id: string
  name: string
  rarity: string
  attack: number
  defense: number
}
```

### Tailwind CSS

Used for UI styling.

Advantages:

- Fast development
- Utility-first styling
- Responsive UI
- Easy component customization

---

## SUI Blockchain

### SUI Network

SUI is the blockchain used by the MVP.

The MVP uses SUI for:

- Wallet authentication
- Faction NFT ownership
- NFT minting
- Reward transaction/proof
- Transaction verification

The game does **not** require blockchain interaction for every gameplay action.

### SUI Wallet

Users connect their SUI-compatible wallet to the application.

Main flow:

```text
Connect Wallet
      ↓
Get Wallet Address
      ↓
Sign Authentication Message
      ↓
Backend Verification
      ↓
Create / Load Player
```

Wallet connection is handled on the frontend.

### @mysten/dapp-kit

SUI wallet integration library.

Used for:

- Wallet connection
- Wallet state
- Transaction signing
- SUI network interaction

Example:

```ts
import { ConnectButton } from '@mysten/dapp-kit'
```

---

## Move

Move is the smart-contract language used by SUI.

The project contains Move contracts for the blockchain layer.

```text
blockchain/
└── sui/
    ├── Move.toml
    └── sources/
        ├── faction_nft.move
        └── reward.move
```

### Faction NFT

The Faction NFT represents ownership of a selected historical faction.

```text
Player
  │
  └── owns
        │
        ▼
   Faction NFT
        │
        ├── faction_id
        ├── faction_name
        ├── rarity
        └── owner
```

The NFT is an ownership/proof mechanism.

It is not the complete representation of the player's game state.

---

## Backend

### FastAPI

FastAPI is used as the main backend framework.

Responsibilities:

- REST API
- Authentication
- Player management
- Faction management
- Battle processing
- Reward processing
- Leaderboard
- Blockchain integration

Example:

```text
POST /auth/wallet
GET  /factions
POST /players/{wallet}/faction
POST /battles
GET  /battles/{battle_id}
POST /rewards/claim
GET  /leaderboard
```

### Python

Python is used for backend development and game logic.

Main reasons:

- Fast API development
- Easy implementation of game logic
- Good testing ecosystem
- Easy blockchain/API integration

### SQLAlchemy

SQLAlchemy is used as the ORM layer.

It maps Python models to database tables.

```text
Player Model
      ↓
players table

Battle Model
      ↓
battles table

Reward Model
      ↓
rewards table
```

### SQLite

SQLite is the default database for local development and MVP testing.

Advantages:

- No database server required
- Easy setup
- Lightweight
- Suitable for local demo

Default:

```text
SQLite
```

For production deployment, the project can use:

```text
PostgreSQL
```

---

# 5. Blockchain Adapter

The backend does not directly couple the entire game logic to SUI.

Instead, blockchain functionality is isolated behind an adapter.

```text
Backend
   │
   ▼
BlockchainAdapter
   │
   ▼
SuiAdapter
   │
   ▼
SUI Network
```

Example interface:

```python
class BlockchainAdapter:

    async def mint_faction(
        self,
        wallet: str,
        faction_id: str
    ):
        ...

    async def submit_reward(
        self,
        wallet: str,
        amount: int
    ):
        ...

    async def get_transaction(
        self,
        tx_hash: str
    ):
        ...

    async def verify_ownership(
        self,
        wallet: str,
        object_id: str
    ):
        ...
```

This allows the game logic to remain independent from blockchain implementation details.

---

# 6. Battle Engine

The Battle Engine is completely handled by the backend.

Basic calculation:

```text
Base Army Power
        ↓
Faction Modifier
        ↓
Random Factor
        ↓
Final Combat Power
        ↓
Battle Result
```

Example:

```text
Army Power = 100

Faction Modifier = 1.10

Random Factor = 0.95

Final Power
= 100 × 1.10 × 0.95
= 104.5
```

The random factor is approximately:

```text
0.90 → 1.10
```

The client does not determine the battle result.

This prevents the frontend from becoming the source of truth for combat.

---

# 7. Reward System

The MVP uses a simple reward model.

```text
Victory
   ↓
+50 Reward

Defeat
   ↓
+10 Reward
```

Reward flow:

```text
Battle Result
      ↓
Reward Service
      ↓
Calculate Reward
      ↓
Save Reward
      ↓
SUI Transaction / Proof
      ↓
Transaction Digest
      ↓
Database
      ↓
Frontend
```

The transaction digest can then be used to verify the blockchain transaction.

---

# 8. Project Structure

```text
vietnam-history-gamefi/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   │
│   │   ├── blockchain/
│   │   │   ├── interface.py
│   │   │   └── sui_adapter.py
│   │   │
│   │   ├── battle/
│   │   │   └── engine.py
│   │   │
│   │   └── main.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── hooks/
│   ├── lib/
│   ├── types/
│   ├── package.json
│   └── .env.local
│
├── blockchain/
│   └── sui/
│       ├── Move.toml
│       └── sources/
│           ├── faction_nft.move
│           └── reward.move
│
├── scripts/
│   ├── deploy-sui.sh
│   └── seed-data.py
│
├── docker-compose.yml
└── README.md
```

---

# 9. Requirements

Before installing the project, make sure the following are installed.

### Required

- Git
- Python 3.11+
- Node.js 18+
- npm
- SUI CLI

Check:

```bash
git --version
python --version
node --version
npm --version
sui --version
```

---

# 10. Clone Repository

```bash
git clone <REPOSITORY_URL>

cd vietnam-history-gamefi
```

---

# 11. Backend Installation

Move into the backend directory:

```bash
cd backend
```

Create virtual environment.

### Windows

```powershell
python -m venv .venv
```

Activate:

```powershell
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 12. Backend Environment Variables

Create:

```text
backend/.env
```

Example:

```env
DATABASE_URL=sqlite:///./game.db

SUI_NETWORK=testnet
SUI_PACKAGE_ID=

JWT_SECRET_KEY=change-this-secret

CORS_ORIGINS=http://localhost:3000
```

### SUI_PACKAGE_ID

If the Move contract has not been deployed:

```env
SUI_PACKAGE_ID=
```

The backend can still run the off-chain gameplay flow.

If the Move package is deployed:

```env
SUI_PACKAGE_ID=0xYOUR_PACKAGE_ID
```

---

# 13. Run Backend

From:

```text
backend/
```

Run:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

---

# 14. Frontend Installation

Open another terminal.

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

---

# 15. Frontend Environment Variables

Create:

```text
frontend/.env.local
```

Example:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000

NEXT_PUBLIC_SUI_NETWORK=testnet

NEXT_PUBLIC_SUI_PACKAGE_ID=
```

If the SUI contract is deployed:

```env
NEXT_PUBLIC_SUI_PACKAGE_ID=0xYOUR_PACKAGE_ID
```

---

# 16. Run Frontend

```bash
npm run dev
```

Open:

```text
http://localhost:3000
```

---

# 17. SUI Testnet Setup

The MVP uses SUI Testnet.

Configure the wallet to:

```text
Network: SUI Testnet
```

The wallet needs testnet SUI for transactions such as NFT minting.

Do not use real mainnet assets during development.

---

# 18. Deploy Move Contract

Move project:

```text
blockchain/sui/
```

Move into the directory:

```bash
cd blockchain/sui
```

Build:

```bash
sui move build
```

Test:

```bash
sui move test
```

Publish to SUI Testnet:

```bash
sui client publish --gas-budget 100000000
```

After publishing, copy the package ID.

Example:

```text
0x123456789abcdef...
```

Update:

```env
SUI_PACKAGE_ID=0x123456789abcdef...
```

and:

```env
NEXT_PUBLIC_SUI_PACKAGE_ID=0x123456789abcdef...
```

Restart the backend and frontend after changing environment variables.

---

# 19. Seed Database

For local development, seed the initial faction data:

```bash
python scripts/seed-data.py
```

The seed data creates the initial historical factions.

---

# 20. Running the Complete MVP

Start the backend:

```bash
cd backend
uvicorn app.main:app --reload
```

Start the frontend in another terminal:

```bash
cd frontend
npm run dev
```

Open:

```text
http://localhost:3000
```

Application flow:

```text
1. Connect SUI Wallet
        ↓
2. Sign Authentication Message
        ↓
3. Backend verifies wallet
        ↓
4. Create / Load Player
        ↓
5. Select Historical Faction
        ↓
6. Mint Faction NFT
        ↓
7. Enter Battle
        ↓
8. Battle Engine calculates result
        ↓
9. Calculate reward
        ↓
10. Submit SUI transaction / proof
        ↓
11. Save transaction digest
        ↓
12. Display Profile / Leaderboard
```

---

# 21. API Overview

## Authentication

```http
POST /auth/wallet
```

Authenticates a player using their SUI wallet.

## Factions

```http
GET /factions
```

Returns available historical factions.

```http
POST /players/{wallet}/faction
```

Selects a faction for the player.

## Player

```http
GET /players/{wallet}
```

Returns player information.

```http
GET /players/{wallet}/army
```

Returns the player's army.

## Battle

```http
POST /battles
```

Creates a new battle.

```http
GET /battles/{battle_id}
```

Returns the battle result.

## Rewards

```http
POST /rewards/claim
```

Processes a reward.

```http
GET /players/{wallet}/rewards
```

Returns the player's rewards.

## Leaderboard

```http
GET /leaderboard
```

Returns player rankings.

---

# 22. Testing

Backend tests:

```bash
cd backend
pytest
```

Recommended test cases:

```text
✓ Winning battle
✓ Losing battle
✓ Faction modifier
✓ Random combat factor
✓ Reward calculation
✓ Player creation
✓ Faction selection
✓ Battle API
✓ Reward API
✓ Leaderboard
```

---

# 23. Development Modes

The project supports two modes.

## Mode 1 — Off-chain Development

Use when the SUI Move contract is not deployed.

```env
SUI_PACKAGE_ID=
```

The following features still work:

- Player
- Faction
- Army
- Battle
- Reward calculation
- Leaderboard

NFT minting and blockchain transactions are mocked or skipped.

---

## Mode 2 — SUI Testnet

Use when the Move contract has been deployed.

```env
SUI_PACKAGE_ID=0xYOUR_PACKAGE_ID
```

The application enables:

- SUI Wallet
- Faction NFT minting
- Blockchain ownership
- Reward transaction/proof
- Transaction verification

---

# 24. Data Ownership Model

The MVP intentionally separates gameplay data from blockchain data.

### Off-chain

```text
Player
Army
Battle
Combat Result
Quest / Progression
Leaderboard
Reward State
```

### On-chain

```text
Faction NFT
NFT Ownership
Blockchain Transaction
Reward Proof
Achievement Proof
```

The blockchain is therefore used as an ownership and verification layer rather than the primary database for all game state.

---

# 25. Security Principles

## Never Trust the Frontend

The frontend should never be responsible for:

```text
Battle Result
Reward Amount
Player Power
Leaderboard Score
```

These values must be validated or calculated by the backend.

## Wallet Authentication

Do not authenticate users using only:

```text
wallet_address
```

Recommended flow:

```text
Backend → Generate Nonce
       ↓
Frontend → Wallet signs message
       ↓
Frontend → Send signature
       ↓
Backend → Verify signature
       ↓
Backend → Create session / JWT
```

## Blockchain Verification

Blockchain transaction hashes/digests should be verified before treating an on-chain action as completed.

---

# 26. Why This Architecture?

The MVP separates the system into three major layers:

```text
┌─────────────────────┐
│      Frontend       │
│      Game UI        │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│       Backend       │
│   Game Authority    │
└──────────┬──────────┘
           │
┌──────────▼──────────┐
│    SUI Blockchain   │
│ Ownership / Proof   │
└─────────────────────┘
```

This provides:

- Faster gameplay
- Lower blockchain usage
- Easier development
- Easier testing
- Better separation of concerns
- Lower coupling between gameplay and blockchain
- Ability to evolve the game without putting every state change on-chain

---

# 27. MVP Design Principle

The core principle is:

> **Play first. Own and prove through blockchain.**

The blockchain should add:

```text
Ownership
+
Verification
+
Digital Assets
```

while the backend handles:

```text
Gameplay
+
Combat
+
Progression
+
Game State
```

---

# 28. Out of Scope

The following features are intentionally excluded from the current MVP:

- Solana integration
- Marketplace
- Land NFT
- Staking
- DAO
- Complex tokenomics
- Cross-chain bridge
- Advanced DeFi
- Full on-chain combat
- Fully decentralized game state

These can be considered in future versions.

---

# 29. Troubleshooting

## Backend cannot start

Check Python:

```bash
python --version
```

Check virtual environment:

```powershell
.venv\Scripts\activate
```

Reinstall dependencies:

```bash
pip install -r requirements.txt
```

## Frontend cannot start

Windows PowerShell:

```powershell
Remove-Item -Recurse -Force node_modules
```

Then:

```bash
npm install
npm run dev
```

## Wallet cannot connect

Check:

```text
SUI network = Testnet
```

Check:

```env
NEXT_PUBLIC_SUI_NETWORK=testnet
```

## NFT is not minted

Check:

```env
SUI_PACKAGE_ID
```

Make sure the Move package has been published to SUI Testnet.

Check that the connected wallet has testnet SUI for gas.

## Backend works but NFT does not

This is expected when:

```env
SUI_PACKAGE_ID=
```

The application is running in:

```text
OFF-CHAIN DEVELOPMENT MODE
```

Deploy the Move package and configure the package ID to enable blockchain functionality.

---

# 30. License

This project is developed as a Vietnam historical GameFi MVP for educational, research, and hackathon purposes.
