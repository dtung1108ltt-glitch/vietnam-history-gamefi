import { useEffect, useState } from "react";
import { useSignAndExecuteTransaction, useSuiClient } from "@mysten/dapp-kit";
import type { SuiObjectChange } from "@mysten/sui/jsonRpc";
import { Transaction } from "@mysten/sui/transactions";
import { api } from "../services/api";
import { SUI_CONFIG, explorerObjectUrl, explorerTxUrl, shorten } from "../services/sui";
import type { FactionDef, Player } from "../types";

function findNftObjectId(changes: SuiObjectChange[] | null | undefined): string | null {
  const nftType = `${SUI_CONFIG.packageId}::faction_nft::FactionNft`;
  for (const change of changes ?? []) {
    if (change.type === "created" && change.objectType === nftType) {
      return change.objectId;
    }
  }
  return null;
}

export function FactionSelect({
  player,
  onPlayer,
}: {
  player: Player | null;
  onPlayer: (player: Player) => void;
}) {
  const [factions, setFactions] = useState<FactionDef[]>([]);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [lastMint, setLastMint] = useState<{ tx: string; nft: string } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { mutateAsync: signAndExecuteTransaction } = useSignAndExecuteTransaction();
  const suiClient = useSuiClient();

  useEffect(() => {
    api
      .getFactions()
      .then(setFactions)
      .catch((err) => setError(err.message));
  }, []);

  async function mint(faction: FactionDef) {
    if (!player) return;
    setBusyId(faction.faction_id);
    setError(null);
    try {
      const tx = new Transaction();
      tx.moveCall({
        target: `${SUI_CONFIG.packageId}::faction_nft::mint_faction`,
        arguments: [
          tx.object(SUI_CONFIG.catalogId),
          tx.pure.u8(faction.faction_id),
        ],
      });
      const result = await signAndExecuteTransaction({ transaction: tx });
      const response = await suiClient.waitForTransaction({
        digest: result.digest,
        options: { showObjectChanges: true },
      });
      const nftObjectId = findNftObjectId(response.objectChanges);
      if (!nftObjectId) {
        throw new Error("Không tìm thấy Faction NFT trong effects");
      }
      const updated = await api.registerFaction(player.wallet, {
        faction_id: faction.faction_id,
        nft_object_id: nftObjectId,
        tx_digest: result.digest,
      });
      setLastMint({ tx: result.digest, nft: nftObjectId });
      onPlayer(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusyId(null);
    }
  }

  if (!player) {
    return (
      <section className="panel">
        <h2>Faction NFT</h2>
        <p>Sign in bằng ví SUI để chọn faction và mint NFT.</p>
      </section>
    );
  }

  return (
    <section className="panel">
      <h2>Faction NFT</h2>
      {player.nft_object_id ? (
        <div className="owned">
          <p>
            Đang sở hữu Faction NFT #{player.faction_id}:{" "}
            <a href={explorerObjectUrl(player.nft_object_id)} target="_blank" rel="noreferrer">
              {shorten(player.nft_object_id)}
            </a>
          </p>
          {lastMint && (
            <p className="muted">
              TX mint:{" "}
              <a href={explorerTxUrl(lastMint.tx)} target="_blank" rel="noreferrer">
                {shorten(lastMint.tx)}
              </a>
            </p>
          )}
        </div>
      ) : (
        <div className="faction-grid">
          {factions.map((faction) => (
            <article key={faction.faction_id} className="faction-card">
              <h3>{faction.name}</h3>
              <span className={`rarity ${faction.rarity}`}>{faction.rarity}</span>
              <p>{faction.description}</p>
              <button
                onClick={() => mint(faction)}
                disabled={busyId !== null || !SUI_CONFIG.packageId}
              >
                {busyId === faction.faction_id ? "Đang mint..." : "Mint NFT"}
              </button>
            </article>
          ))}
        </div>
      )}
      {!SUI_CONFIG.packageId && (
        <p className="error">Thiếu VITE_SUI_PACKAGE_ID / VITE_SUI_CATALOG_ID trong .env</p>
      )}
      {error && <p className="error">{error}</p>}
    </section>
  );
}
