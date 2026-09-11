import type { FactionDef, Player, RewardRecord, TxStatus } from "../types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!resp.ok) {
    const detail = await resp.json().catch(() => ({}));
    throw new Error(detail.detail ?? `API ${resp.status}`);
  }
  return resp.json() as Promise<T>;
}

export const api = {
  getNonce: (wallet: string) =>
    request<{ nonce: string; message: string }>("/auth/nonce", {
      method: "POST",
      body: JSON.stringify({ wallet }),
    }),

  verifyWallet: (payload: {
    wallet: string;
    nonce: string;
    message: string;
    signature: string;
  }) => request<Player>("/auth/wallet", { method: "POST", body: JSON.stringify(payload) }),

  getPlayer: (wallet: string) => request<Player>(`/players/${wallet}`),

  getFactions: () => request<FactionDef[]>("/factions"),

  registerFaction: (
    wallet: string,
    payload: { faction_id: number; nft_object_id: string; tx_digest: string },
  ) =>
    request<Player>(`/players/${wallet}/faction`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  claimReward: (payload: { wallet: string; battle_id: number }) =>
    request<RewardRecord>("/rewards/claim", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  getTransaction: (digest: string) =>
    request<TxStatus>(`/blockchain/sui/transaction/${digest}`),
};
