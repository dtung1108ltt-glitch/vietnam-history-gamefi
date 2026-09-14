CREATE TYPE blockchain_chain AS ENUM ('sui', 'solana');
CREATE TYPE blockchain_transaction_status AS ENUM ('pending', 'confirmed', 'failed');

CREATE TABLE players (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  wallet_address TEXT NOT NULL,
  chain blockchain_chain NOT NULL,
  username TEXT,
  faction_id TEXT,
  level INTEGER NOT NULL DEFAULT 1,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (chain, wallet_address)
);
CREATE TABLE blockchain_assets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  player_id UUID NOT NULL REFERENCES players(id),
  chain blockchain_chain NOT NULL,
  asset_type TEXT NOT NULL CHECK (asset_type IN ('faction', 'reward', 'achievement')),
  asset_identifier TEXT,
  transaction_hash TEXT,
  status blockchain_transaction_status NOT NULL DEFAULT 'pending',
  metadata_uri TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (chain, transaction_hash)
);
CREATE TABLE rewards (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  player_id UUID NOT NULL REFERENCES players(id),
  chain blockchain_chain,
  reward_type TEXT NOT NULL,
  amount INTEGER NOT NULL CHECK (amount >= 0),
  tx_hash TEXT,
  status blockchain_transaction_status NOT NULL DEFAULT 'pending',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
