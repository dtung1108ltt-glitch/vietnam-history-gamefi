import { useEffect, useRef, useState } from "react";
import { api } from "../services/api";
import { explorerTxUrl, shorten } from "../services/sui";
import type { Player, TxStatus } from "../types";

export function RewardPanel({ player }: { player: Player | null }) {
  const [battleId, setBattleId] = useState(1);
  const [digest, setDigest] = useState<string | null>(null);
  const [tx, setTx] = useState<TxStatus | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const timer = useRef<number | null>(null);

  useEffect(() => () => {
    if (timer.current) window.clearInterval(timer.current);
  }, []);

  function stopPolling() {
    if (timer.current) {
      window.clearInterval(timer.current);
      timer.current = null;
    }
  }

  async function claim() {
    if (!player) return;
    setBusy(true);
    setError(null);
    setTx(null);
    stopPolling();
    try {
      const reward = await api.claimReward({ wallet: player.wallet, battle_id: battleId });
      setDigest(reward.tx_digest);
      timer.current = window.setInterval(async () => {
        try {
          const status = await api.getTransaction(reward.tx_digest);
          setTx(status);
          if (status.status === "success" || status.status === "failure") {
            stopPolling();
          }
        } catch {
          // TX chưa được index thì thử lại lượt sau
        }
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel">
      <h2>Battle Reward</h2>
      {!player ? (
        <p>Sign in bằng ví SUI để nhận reward on-chain.</p>
      ) : (
        <>
          <div className="row">
            <label>
              Battle ID{" "}
              <input
                type="number"
                value={battleId}
                onChange={(e) => setBattleId(Number(e.target.value))}
              />
            </label>
            <button onClick={claim} disabled={busy}>
              {busy ? "Đang gửi TX..." : "Claim reward (SUI TX)"}
            </button>
          </div>
          {digest && (
            <p className="muted">
              TX Digest:{" "}
              <a href={explorerTxUrl(digest)} target="_blank" rel="noreferrer">
                {shorten(digest)}
              </a>
            </p>
          )}
          {digest && !tx && <p className="pending">Đang chờ TX lên chain...</p>}
          {tx?.status === "success" && (
            <p className="confirmed">Reward confirmed on-chain</p>
          )}
          {tx?.status === "failure" && (
            <p className="error">TX thất bại on-chain</p>
          )}
          {error && <p className="error">{error}</p>}
        </>
      )}
    </section>
  );
}
