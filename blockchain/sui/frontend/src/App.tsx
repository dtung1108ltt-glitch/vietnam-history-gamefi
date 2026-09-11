import { useState } from "react";
import { FactionSelect } from "./components/FactionSelect";
import { RewardPanel } from "./components/RewardPanel";
import { WalletBar } from "./components/WalletBar";
import type { Player } from "./types";

export function App() {
  const [player, setPlayer] = useState<Player | null>(null);
  return (
    <div className="app">
      <WalletBar onPlayer={setPlayer} />
      <main>
        <FactionSelect player={player} onPlayer={setPlayer} />
        <RewardPanel player={player} />
      </main>
    </div>
  );
}
