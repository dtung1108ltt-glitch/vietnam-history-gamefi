import { useState } from "react";
import { ConnectModal, useSignPersonalMessage } from "@mysten/dapp-kit";
import { useWallet } from "../hooks/useWallet";
import { api } from "../services/api";
import { shorten } from "../services/sui";
import type { Player } from "../types";

export function WalletBar({ onPlayer }: { onPlayer: (player: Player) => void }) {
  const { address, isConnected, disconnect } = useWallet();
  const { mutateAsync: signPersonalMessage } = useSignPersonalMessage();
  const [player, setPlayer] = useState<Player | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function signIn() {
    if (!address) return;
    setBusy(true);
    setError(null);
    try {
      const { nonce, message } = await api.getNonce(address);
      const { signature } = await signPersonalMessage({
        message: new TextEncoder().encode(message),
      });
      const verified = await api.verifyWallet({
        wallet: address,
        nonce,
        message,
        signature,
      });
      setPlayer(verified);
      onPlayer(verified);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <header className="wallet-bar">
      <strong>Việt Sử Chiến Ký</strong>
      {isConnected && address ? (
        <div className="wallet-actions">
          <span className="address" title={address}>
            {shorten(address)}
          </span>
          {player ? (
            <span className="badge">Player: {player.username}</span>
          ) : (
            <button onClick={signIn} disabled={busy}>
              {busy ? "Đang ký..." : "Sign in (ký nonce)"}
            </button>
          )}
          <button className="secondary" onClick={disconnect}>
            Disconnect
          </button>
        </div>
      ) : (
        <ConnectModal
          trigger={
            <button>
              Connect Wallet
            </button>
          }
        />
      )}
      {error && <span className="error">{error}</span>}
    </header>
  );
}
