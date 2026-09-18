# Architecture

`Player -> Faction -> Army -> Battle -> Reward` is the game-domain path. It stays in FastAPI services and PostgreSQL. `BlockchainAdapter` is a port beneath the domain; `SuiAdapter` and `SolanaAdapter` are the only locations where chain RPC semantics belong. Frontend wallets sign only user-owned messages/transactions. The backend determines battle outcomes and reward eligibility.
