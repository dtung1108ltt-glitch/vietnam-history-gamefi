export interface FactionDef {
  faction_id: number;
  name: string;
  rarity: string;
  image: string;
  description: string;
}

export interface Player {
  wallet: string;
  username: string;
  faction_id: number | null;
  nft_object_id: string | null;
}

export interface RewardRecord {
  id: number;
  wallet: string;
  battle_id: number;
  amount: number;
  tx_digest: string;
  status: string;
}

export interface TxStatus {
  digest: string;
  status: "success" | "failure" | "pending" | string;
  sender: string | null;
  timestamp_ms: number | null;
  events: unknown[];
}
