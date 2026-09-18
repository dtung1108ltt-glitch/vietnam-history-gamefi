import React, { useState, useEffect } from 'react';
import { ChainType, PreGameStep, MapLocation, PlayerResources } from './types';
import { useWallet } from './hooks/useWallet';
import { useFaction } from './hooks/useFaction';
import { useAudio } from './hooks/useAudio';
import { apiService } from './services/api';
import { Header } from './components/Common/Header';
import { WalletModal } from './components/Wallet/WalletModal';
import { SplashScreen } from './components/PreGame/SplashScreen';
import { FactionSelection } from './components/PreGame/FactionSelection';
import { PreGameLobby } from './components/PreGame/PreGameLobby';
import { BattleTransition } from './components/PreGame/BattleTransition';
import { CampaignMap } from './components/Campaign/CampaignMap';
import { BattleScreen } from './components/Battle/BattleScreen';

export const App: React.FC = () => {
  const [step, setStep] = useState<PreGameStep>('splash');
  const [isWalletModalOpen, setIsWalletModalOpen] = useState<boolean>(false);
  const [serverOnline, setServerOnline] = useState<boolean>(true);
  const [selectedLocation, setSelectedLocation] = useState<MapLocation | null>(null);
  const [resources] = useState<PlayerResources>({ rice: 4500, gold: 12800, morale: 85 });

  // Audio system
  const { isMuted, toggleMute, playDrum, playGong, playSwordShink } = useAudio();

  // Wallet system
  const {
    chain,
    setChain,
    player,
    isConnected,
    isConnecting,
    authStep,
    error: walletError,
    connectAndAuth,
    updatePlayerFaction,
    disconnect,
  } = useWallet();

  // Faction system
  const {
    factions,
    selectedFactionId,
    setSelectedFactionId,
    selectedFaction,
    isMinting,
    mintStatus,
    mintFactionNft,
  } = useFaction(player, updatePlayerFaction);

  // Check Backend health on mount
  useEffect(() => {
    async function check() {
      const ok = await apiService.checkHealth();
      setServerOnline(ok);
    }
    check();
  }, []);

  // Xử lý khi nhấn "Tiến Vào Chiến Cuộc" ở Splash Screen
  const handleEnterFromSplash = () => {
    if (!isConnected) {
      setIsWalletModalOpen(true);
    } else if (player?.faction_id) {
      setStep('lobby');
    } else {
      setStep('faction_select');
    }
  };

  // Sau khi kết nối ví thành công từ modal
  const handleConnectWallet = async (chosenChain: ChainType) => {
    const p = await connectAndAuth(chosenChain);
    if (p.faction_id) {
      setStep('lobby');
    } else {
      setStep('faction_select');
    }
  };

  const handleDisconnect = () => {
    disconnect();
    setStep('splash');
  };

  return (
    <div className="min-h-screen bg-imperial-obsidian text-slate-100 flex flex-col selection:bg-amber-600 selection:text-white relative">
      
      {/* Ancient Header Navigation */}
      <Header
        chain={chain}
        onSelectChain={(c) => setChain(c)}
        player={player}
        onOpenWalletModal={() => setIsWalletModalOpen(true)}
        onDisconnect={handleDisconnect}
        isMuted={isMuted}
        onToggleMute={toggleMute}
        onPlayGong={playGong}
        serverOnline={serverOnline}
      />

      {/* Main Pre-Game Flow Routing */}
      <main className="flex-1 flex flex-col">
        {step === 'splash' && (
          <SplashScreen
            onEnter={handleEnterFromSplash}
            onSelectChain={(c) => setChain(c)}
            chain={chain}
            onPlayDrum={playDrum}
            onPlayGong={playGong}
          />
        )}

        {step === 'faction_select' && (
          <FactionSelection
            factions={factions}
            selectedFactionId={selectedFactionId}
            onSelectFactionId={(id) => setSelectedFactionId(id)}
            selectedFaction={selectedFaction}
            player={player}
            isMinting={isMinting}
            mintStatus={mintStatus}
            onMintFaction={mintFactionNft}
            onProceedToLobby={() => setStep('lobby')}
            onBackToSplash={() => setStep('splash')}
            onPlayDrum={playDrum}
            onPlayGong={playGong}
            onPlaySword={playSwordShink}
          />
        )}

        {step === 'lobby' && player && (
          <PreGameLobby
            player={player}
            faction={selectedFaction}
            onChangeFaction={() => setStep('faction_select')}
            onEnterBattle={() => setStep('battle_transition')}
            onPlayDrum={playDrum}
            onPlayGong={playGong}
            onPlaySword={playSwordShink}
          />
        )}

        {step === 'battle_transition' && player && (
          <BattleTransition
            player={player}
            faction={selectedFaction}
            onReturnToLobby={() => setStep('lobby')}
            onEnterCampaign={() => setStep('campaign_map')}
            onPlayDrum={playDrum}
          />
        )}

        {step === 'campaign_map' && player && (
          <CampaignMap
            player={player}
            faction={selectedFaction}
            resources={resources}
            onDeploy={(location) => {
              setSelectedLocation(location);
              setStep('battle');
            }}
            onBackToLobby={() => setStep('lobby')}
            onPlayDrum={playDrum}
            onPlayGong={playGong}
          />
        )}

        {step === 'battle' && player && selectedLocation && (
          <BattleScreen
            player={player}
            faction={selectedFaction}
            location={selectedLocation}
            onExitBattle={() => setStep('campaign_map')}
            onPlayDrum={playDrum}
            onPlaySword={playSwordShink}
            onPlayGong={playGong}
          />
        )}
      </main>

      {/* Multi-chain Wallet Modal */}
      <WalletModal
        isOpen={isWalletModalOpen}
        onClose={() => setIsWalletModalOpen(false)}
        onConnect={handleConnectWallet}
        isConnecting={isConnecting}
        authStep={authStep}
        error={walletError}
        onPlayDrum={playDrum}
        onPlayGong={playGong}
      />

      {/* Ancient Imperial Footer */}
      <footer className="w-full border-t border-imperial-border/60 bg-imperial-lacquer/80 backdrop-blur-sm py-4 px-4 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <div>
            <span className="font-cinzel text-imperial-lightgold font-bold">Vietnam History GameFi</span> &bull; Bản quyền Lịch sử &bull; Chuẩn kiến trúc FPD MVP
          </div>
          <div className="flex items-center space-x-4 text-[11px] text-slate-400">
            <span>Sui Move &amp; Solana Anchor</span>
            <span>&bull;</span>
            <span>FastAPI Monolith</span>
            <span>&bull;</span>
            <span>Off-Chain Battle Engine</span>
          </div>
        </div>
      </footer>

    </div>
  );
};

export default App;
