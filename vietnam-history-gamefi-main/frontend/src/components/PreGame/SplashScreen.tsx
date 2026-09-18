import React from 'react';
import { DrumOrnament } from '../Common/DrumOrnament';
import { Shield, Swords, Sparkles, Coins, ArrowRight, Play, Compass, Flame } from 'lucide-react';
import { ChainType } from '../../types';

interface SplashScreenProps {
  onEnter: () => void;
  onSelectChain: (chain: ChainType) => void;
  chain: ChainType;
  onPlayDrum: () => void;
  onPlayGong: () => void;
}

export const SplashScreen: React.FC<SplashScreenProps> = ({
  onEnter,
  onSelectChain,
  chain,
  onPlayDrum,
  onPlayGong,
}) => {
  const handleStart = () => {
    onPlayGong();
    onEnter();
  };

  return (
    <div className="relative min-h-[calc(100vh-65px)] flex flex-col items-center justify-center px-4 py-8 overflow-hidden text-center">
      
      {/* Background Drum Rotating Effect */}
      <div className="absolute inset-0 flex items-center justify-center opacity-30 pointer-events-none">
        <DrumOrnament size={650} animate={true} />
      </div>

      {/* Floating Embers / Glow */}
      <div className="absolute top-1/4 left-1/3 w-72 h-72 bg-amber-500/10 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/3 w-80 h-80 bg-red-700/15 rounded-full blur-[120px] pointer-events-none" />

      {/* Hero Content Box */}
      <div className="relative z-10 max-w-4xl mx-auto flex flex-col items-center">
        
        {/* Imperial Badge */}
        <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-imperial-lacquer/90 border border-imperial-gold/60 text-imperial-lightgold text-xs font-semibold tracking-widest uppercase mb-6 shadow-lg shadow-amber-950/30">
          <Flame className="w-3.5 h-3.5 text-amber-400" />
          <span>Bản Hùng Ca Ngàn Năm Đại Việt &bull; Web3 MVP</span>
        </div>

        {/* Main Title */}
        <h1 className="font-cinzel text-4xl sm:text-6xl lg:text-7xl font-black text-transparent bg-clip-text bg-gradient-to-b from-amber-100 via-imperial-lightgold to-amber-500 tracking-tight leading-none mb-4 drop-shadow-md">
          HÀO KHÍ ĐẠI VIỆT
        </h1>
        <p className="font-serif italic text-lg sm:text-2xl text-amber-200/90 font-medium tracking-wide mb-6 max-w-2xl">
          "Nam quốc sơn hà Nam đế cư &bull; Tiệt nhiên định phận tại thiên thư"
        </p>

        {/* Historical Prologue */}
        <p className="text-sm sm:text-base text-slate-300 max-w-2xl mx-auto leading-relaxed mb-8">
          Trải qua hàng ngàn năm dựng nước và giữ nước, các triều đại anh hùng đã khắc ghi những trang sử vàng chói lọi. 
          Trong phiên bản MVP này, hãy kết nối ví, chiêu mộ Tộc hệ, đúc Kim Ấn Faction NFT và lãnh đạo đại quân tiến vào chiến cuộc!
        </p>

        {/* Chain Selector pills */}
        <div className="flex items-center space-x-3 bg-black/60 backdrop-blur-md p-1.5 rounded-2xl border border-imperial-border mb-8 shadow-inner">
          <span className="text-xs text-slate-400 pl-3 font-medium">Chọn Mạng Khởi Trận:</span>
          <button
            onClick={() => { onPlayDrum(); onSelectChain('sui'); }}
            className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-bold flex items-center space-x-1.5 transition-all ${
              chain === 'sui'
                ? 'bg-gradient-to-r from-blue-700 to-cyan-600 text-white shadow-lg shadow-cyan-900/50 scale-105'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <span>💧 Sui Testnet</span>
          </button>
          <button
            onClick={() => { onPlayDrum(); onSelectChain('solana'); }}
            className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-bold flex items-center space-x-1.5 transition-all ${
              chain === 'solana'
                ? 'bg-gradient-to-r from-purple-700 to-indigo-600 text-white shadow-lg shadow-purple-900/50 scale-105'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <span>⚡ Solana Devnet</span>
          </button>
        </div>

        {/* CTA Launch Button */}
        <div className="flex flex-col sm:flex-row items-center gap-4 mb-12">
          <button
            onClick={handleStart}
            className="group relative px-8 sm:px-10 py-4 rounded-2xl bg-gradient-to-r from-imperial-crimson via-red-600 to-imperial-darkred text-imperial-lightgold font-cinzel font-black text-base sm:text-lg tracking-wider uppercase border-2 border-imperial-gold shadow-2xl shadow-red-950/80 hover:scale-105 transition-all duration-300 flex items-center space-x-3 cursor-pointer"
          >
            <Play className="w-5 h-5 fill-current text-imperial-lightgold" />
            <span>Tiến Vào Chiến Cuộc</span>
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>

        {/* Core Pillars Feature Grid (From Architecture PDF) */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 w-full max-w-3xl text-left">
          
          <div className="bg-imperial-lacquer/80 border border-imperial-border/80 rounded-2xl p-4 flex items-start space-x-3">
            <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/30 text-imperial-gold shrink-0">
              <Shield className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-imperial-lightgold uppercase tracking-wider">
                Quyền Sở Hữu Kỹ Thuật Số
              </h4>
              <p className="text-[11px] text-slate-400 mt-1">
                Faction NFT & chiến tích vinh quang được khắc ghi bất biến trên Sui/Solana.
              </p>
            </div>
          </div>

          <div className="bg-imperial-lacquer/80 border border-imperial-border/80 rounded-2xl p-4 flex items-start space-x-3">
            <div className="p-2.5 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 shrink-0">
              <Swords className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-imperial-lightgold uppercase tracking-wider">
                Gameplay Off-Chain Thuần Khiết
              </h4>
              <p className="text-[11px] text-slate-400 mt-1">
                Chiến thuật bày binh mượt mà, phản hồi tức thì, bảo vệ trải nghiệm công bằng F2P.
              </p>
            </div>
          </div>

          <div className="bg-imperial-lacquer/80 border border-imperial-border/80 rounded-2xl p-4 flex items-start space-x-3">
            <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 shrink-0">
              <Compass className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-xs font-bold text-imperial-lightgold uppercase tracking-wider">
                Chuẩn Mực Lịch Sử Dân Tộc
              </h4>
              <p className="text-[11px] text-slate-400 mt-1">
                Nội dung các thời kỳ Lý, Trần, Lê, Tây Sơn, Nguyễn được nghiên cứu chỉn chu.
              </p>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
};
