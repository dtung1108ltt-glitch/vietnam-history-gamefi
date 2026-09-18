import React from 'react';
import { Faction, Player } from '../../types';
import { FactionCard } from '../FactionCard/FactionCard';
import { Sparkles, Shield, Swords, Zap, ArrowLeft, ArrowRight, Loader2, CheckCircle, ExternalLink, Award } from 'lucide-react';

interface FactionSelectionProps {
  factions: Faction[];
  selectedFactionId: number;
  onSelectFactionId: (id: number) => void;
  selectedFaction: Faction;
  player: Player | null;
  isMinting: boolean;
  mintStatus: string;
  onMintFaction: (factionId: number) => Promise<any>;
  onProceedToLobby: () => void;
  onBackToSplash: () => void;
  onPlayDrum: () => void;
  onPlayGong: () => void;
  onPlaySword: () => void;
}

export const FactionSelection: React.FC<FactionSelectionProps> = ({
  factions,
  selectedFactionId,
  onSelectFactionId,
  selectedFaction,
  player,
  isMinting,
  mintStatus,
  onMintFaction,
  onProceedToLobby,
  onBackToSplash,
  onPlayDrum,
  onPlayGong,
  onPlaySword,
}) => {
  const isAlreadyOwned = player?.faction_id === selectedFaction.faction_id;

  const handleMint = async () => {
    onPlaySword();
    try {
      await onMintFaction(selectedFaction.faction_id);
    } catch (e) {
      // Handled in hook
    }
  };

  const handleProceed = () => {
    onPlayGong();
    onProceedToLobby();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      
      {/* Top Breadcrumb & Title */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 pb-4 border-b border-imperial-border">
        <div>
          <button
            onClick={onBackToSplash}
            className="inline-flex items-center space-x-1.5 text-xs text-slate-400 hover:text-imperial-lightgold transition-colors mb-2 cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Quay lại Màn hình Khởi đầu</span>
          </button>
          <h2 className="text-2xl sm:text-3xl font-cinzel font-black text-transparent bg-clip-text bg-gradient-to-r from-amber-100 via-imperial-lightgold to-yellow-500">
            Chiêu Mộ Tộc Hệ &bull; Lựa Chọn Triều Đại
          </h2>
          <p className="text-xs sm:text-sm text-slate-300 mt-1">
            Chọn một trong năm triều đại rạng danh sử sách để đúc Faction NFT và lãnh đạo quân đoàn của bạn.
          </p>
        </div>

        {/* Player Status Tag */}
        <div className="flex items-center space-x-3 bg-imperial-lacquer px-4 py-2 rounded-xl border border-imperial-border">
          <div className="text-right">
            <div className="text-xs text-slate-400">Tướng quân:</div>
            <div className="text-xs font-mono font-bold text-imperial-lightgold">
              {player?.username || 'Chưa đăng nhập'}
            </div>
          </div>
          <div className="w-9 h-9 rounded-lg bg-imperial-darkred flex items-center justify-center text-imperial-gold border border-imperial-gold/50 font-cinzel font-bold text-sm">
            {player?.chain === 'sui' ? 'SUI' : 'SOL'}
          </div>
        </div>
      </div>

      {/* Grid: 5 Faction Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        {factions.map((faction) => (
          <FactionCard
            key={faction.faction_id}
            faction={faction}
            isSelected={selectedFactionId === faction.faction_id}
            onSelect={(f) => onSelectFactionId(f.faction_id)}
            onPlayDrum={onPlayDrum}
          />
        ))}
      </div>

      {/* Inspector / Detail Banner for Selected Faction */}
      <div className="bg-imperial-lacquer/90 border-2 border-imperial-gold/70 rounded-2xl p-6 sm:p-8 gold-glow relative overflow-hidden corner-ornament">
        <div className="absolute -right-10 -bottom-10 text-9xl font-serif text-white/[0.03] pointer-events-none select-none">
          {selectedFaction.coat_of_arms.charAt(0)}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
          
          {/* Col 1: Dynasty Title & Special Unit */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs uppercase px-3 py-0.5 rounded-full font-bold bg-imperial-darkred text-imperial-lightgold border border-imperial-crimson">
                {selectedFaction.historical_era}
              </span>
              <span className="text-xs text-amber-300/80 font-mono">
                Ấn tín định danh NFT #00{selectedFaction.faction_id}
              </span>
            </div>

            <h3 className="text-3xl sm:text-4xl font-cinzel font-black text-white">
              {selectedFaction.name}
            </h3>

            <blockquote className="border-l-4 border-imperial-gold pl-4 py-1 italic text-amber-200/90 text-sm sm:text-base font-serif">
              "{selectedFaction.motto}"
            </blockquote>

            <p className="text-sm text-slate-300 leading-relaxed">
              {selectedFaction.description}
            </p>

            {/* Trait chips */}
            <div className="flex flex-wrap gap-2 pt-2">
              <div className="px-3 py-1 rounded-lg bg-black/40 border border-slate-700 text-xs text-slate-200 flex items-center space-x-1.5">
                <Swords className="w-3.5 h-3.5 text-red-400" />
                <span>Công: +{selectedFaction.attack_bonus}%</span>
              </div>
              <div className="px-3 py-1 rounded-lg bg-black/40 border border-slate-700 text-xs text-slate-200 flex items-center space-x-1.5">
                <Shield className="w-3.5 h-3.5 text-blue-400" />
                <span>Thủ: +{selectedFaction.defense_bonus}%</span>
              </div>
              <div className="px-3 py-1 rounded-lg bg-black/40 border border-slate-700 text-xs text-slate-200 flex items-center space-x-1.5">
                <Zap className="w-3.5 h-3.5 text-amber-400" />
                <span>Tốc: +{selectedFaction.movement_bonus}%</span>
              </div>
              <div className="px-3 py-1 rounded-lg bg-amber-950/40 border border-amber-600/40 text-xs text-amber-200 flex items-center space-x-1.5">
                <Award className="w-3.5 h-3.5 text-amber-400" />
                <span>Đặc quyền: {selectedFaction.special_unit}</span>
              </div>
            </div>
          </div>

          {/* Col 2: Action & Minting Box */}
          <div className="bg-black/50 border border-imperial-border rounded-xl p-5 flex flex-col items-center justify-center text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-imperial-darkred to-imperial-crimson p-1 border-2 border-imperial-gold shadow-lg flex items-center justify-center">
              <span className="font-cinzel text-imperial-gold font-black text-2xl">
                {selectedFaction.coat_of_arms.charAt(0)}
              </span>
            </div>

            <div>
              <h4 className="text-sm font-bold text-white font-cinzel">
                Khắc Ấn Tín {selectedFaction.name}
              </h4>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Được bảo chứng on-chain trên mạng {player?.chain?.toUpperCase()}
              </p>
            </div>

            {/* Mint Status message */}
            {mintStatus && (
              <div className="w-full p-2.5 rounded-lg bg-amber-950/50 border border-amber-500/50 text-xs text-amber-200 flex items-center justify-center space-x-2">
                {isMinting ? <Loader2 className="w-4 h-4 animate-spin text-amber-400" /> : <CheckCircle className="w-4 h-4 text-emerald-400" />}
                <span>{mintStatus}</span>
              </div>
            )}

            {/* Mint / Proceed Actions */}
            {isAlreadyOwned ? (
              <div className="w-full space-y-2">
                <div className="p-2 rounded-lg bg-emerald-950/60 border border-emerald-500/50 text-emerald-300 text-xs font-semibold flex items-center justify-center space-x-1.5">
                  <CheckCircle className="w-4 h-4 text-emerald-400" />
                  <span>Đã sở hữu Faction NFT</span>
                </div>
                <button
                  onClick={handleProceed}
                  className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-emerald-700 to-teal-600 hover:from-emerald-600 hover:to-teal-500 text-white font-bold text-sm shadow-lg shadow-emerald-950/50 flex items-center justify-center space-x-2 transition-all cursor-pointer"
                >
                  <span>Tiến Vào Sảnh Duyệt Quân</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <button
                onClick={handleMint}
                disabled={isMinting}
                className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-imperial-crimson via-red-600 to-imperial-darkred hover:from-red-600 hover:to-imperial-crimson text-imperial-lightgold border border-imperial-gold font-bold text-sm shadow-lg shadow-red-950/60 flex items-center justify-center space-x-2 transition-all disabled:opacity-50 cursor-pointer"
              >
                {isMinting ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Đang Đúc Ấn Tín...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-imperial-gold" />
                    <span>Đúc Ấn Tín & Gia Nhập</span>
                  </>
                )}
              </button>
            )}

            {player?.nft_object_id && (
              <div className="text-[10px] font-mono text-slate-500 truncate max-w-full">
                Token ID: {player.nft_object_id}
              </div>
            )}
          </div>

        </div>

      </div>

    </div>
  );
};
