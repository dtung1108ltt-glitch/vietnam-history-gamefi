import React from 'react';
import { Faction, Player } from '../../types';
import { Swords, Shield, Zap, Users, Trophy, Play, CheckCircle2, RefreshCw, ChevronRight, Award, Compass } from 'lucide-react';

interface PreGameLobbyProps {
  player: Player;
  faction: Faction;
  onChangeFaction: () => void;
  onEnterBattle: () => void;
  onPlayDrum: () => void;
  onPlayGong: () => void;
  onPlaySword: () => void;
}

export const PreGameLobby: React.FC<PreGameLobbyProps> = ({
  player,
  faction,
  onChangeFaction,
  onEnterBattle,
  onPlayDrum,
  onPlayGong,
  onPlaySword,
}) => {
  const handleLaunch = () => {
    onPlaySword();
    onPlayGong();
    onEnterBattle();
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      
      {/* Top Welcome Title */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center space-x-2 px-4 py-1.5 rounded-full bg-imperial-lacquer border border-imperial-gold/60 text-imperial-lightgold text-xs font-semibold tracking-widest uppercase mb-3">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>Sảnh Tiền Trạm &bull; Sẵn Sàng Xuất Kích</span>
        </div>
        <h2 className="text-3xl sm:text-4xl font-cinzel font-black text-transparent bg-clip-text bg-gradient-to-r from-amber-100 via-imperial-lightgold to-yellow-500">
          Tổng Hành Dinh Tướng Quân
        </h2>
        <p className="text-sm text-slate-300 mt-2 max-w-xl mx-auto">
          Binh mã đã tề tựu dưới cờ lệnh triều đại {faction.name}. Hãy kiểm tra binh lực và sẵn sàng xuất quân vào trận địa.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        
        {/* Left Column: Commander Profile & Faction Badge */}
        <div className="bg-imperial-lacquer/90 border border-imperial-gold/60 rounded-2xl p-6 gold-glow flex flex-col justify-between corner-ornament">
          <div>
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-imperial-darkred to-imperial-crimson p-1 border-2 border-imperial-gold shadow-lg flex items-center justify-center">
                <span className="font-cinzel text-imperial-gold font-black text-2xl">
                  {faction.coat_of_arms.charAt(0)}
                </span>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-imperial-gold tracking-widest">
                  Thống Lĩnh Quân Đoàn
                </span>
                <h3 className="text-lg font-bold text-white font-cinzel">
                  {player.username}
                </h3>
                <div className="text-xs text-slate-400 font-mono">
                  {player.wallet.substring(0, 6)}...{player.wallet.substring(player.wallet.length - 4)}
                </div>
              </div>
            </div>

            <div className="space-y-3 pt-3 border-t border-imperial-border/80 text-xs">
              <div className="flex justify-between items-center py-1">
                <span className="text-slate-400">Triều đại quy phục:</span>
                <span className="font-bold text-amber-300 font-cinzel">{faction.name}</span>
              </div>
              <div className="flex justify-between items-center py-1">
                <span className="text-slate-400">Huy hiệu Faction NFT:</span>
                <span className="font-bold uppercase text-emerald-400">Đã xác minh</span>
              </div>
              <div className="flex justify-between items-center py-1">
                <span className="text-slate-400">Mạng bảo chứng:</span>
                <span className="font-mono uppercase text-cyan-300">{player.chain}</span>
              </div>
              <div className="flex justify-between items-center py-1">
                <span className="text-slate-400">Quân hàm sơ khởi:</span>
                <span className="font-bold text-white">Cấp {player.level} (Đô Đốc)</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => { onPlayDrum(); onChangeFaction(); }}
            className="mt-6 w-full py-2.5 px-3 rounded-xl bg-black/40 hover:bg-slate-800/80 border border-slate-700 text-slate-300 hover:text-white text-xs font-semibold flex items-center justify-center space-x-2 transition-all cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Đổi Triều Đại Khác</span>
          </button>
        </div>

        {/* Center Column: Army Stats & Military Units */}
        <div className="bg-imperial-lacquer/90 border border-imperial-border rounded-2xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <Users className="w-5 h-5 text-imperial-gold" />
                <h3 className="font-cinzel text-base font-bold text-white">
                  Binh Lực Cơ Bản (Army State)
                </h3>
              </div>
              <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/40 font-mono">
                Off-chain Engine
              </span>
            </div>

            {/* Power Score Box */}
            <div className="bg-gradient-to-r from-red-950/50 to-amber-950/40 border border-imperial-gold/40 rounded-xl p-4 mb-4 flex items-center justify-between">
              <div>
                <div className="text-[11px] uppercase tracking-wider text-slate-400">
                  Lực Lượng Tác Chiến (Combat Score)
                </div>
                <div className="text-3xl font-black font-mono text-imperial-lightgold mt-0.5">
                  {player.base_power} <span className="text-sm font-normal text-amber-300">Vạn Quân</span>
                </div>
              </div>
              <div className="w-10 h-10 rounded-full bg-imperial-darkred/80 border border-imperial-gold/60 flex items-center justify-center text-imperial-gold">
                <Swords className="w-5 h-5" />
              </div>
            </div>

            {/* Units breakdown */}
            <div className="space-y-2.5 text-xs text-slate-300">
              <div className="bg-black/30 p-2.5 rounded-lg border border-slate-800 flex justify-between items-center">
                <span>Binh Chủng Trấn Phái:</span>
                <span className="font-semibold text-imperial-lightgold">{faction.special_unit}</span>
              </div>
              <div className="bg-black/30 p-2.5 rounded-lg border border-slate-800 flex justify-between items-center">
                <span>Hệ Số Tấn Công:</span>
                <span className="font-bold text-red-400">+{faction.attack_bonus}% Sát Thương</span>
              </div>
              <div className="bg-black/30 p-2.5 rounded-lg border border-slate-800 flex justify-between items-center">
                <span>Hệ Số Phòng Thủ:</span>
                <span className="font-bold text-blue-400">+{faction.defense_bonus}% Giảm Thương</span>
              </div>
              <div className="bg-black/30 p-2.5 rounded-lg border border-slate-800 flex justify-between items-center">
                <span>Hệ Số Di Chuyển:</span>
                <span className="font-bold text-amber-400">+{faction.movement_bonus}% Hành Quân</span>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400 text-center">
            Theo nguyên tắc kiến trúc: NFT bảo chứng identity, kỹ năng chỉ huy quyết định thắng bại.
          </div>
        </div>

        {/* Right Column: Battle Modes & Action */}
        <div className="bg-gradient-to-b from-imperial-darkred/40 via-imperial-lacquer to-imperial-obsidian border border-imperial-gold/60 rounded-2xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <Compass className="w-5 h-5 text-amber-400" />
              <h3 className="font-cinzel text-base font-bold text-white">
                Mục Tiêu Chiến Trận (MVP Scope)
              </h3>
            </div>

            <div className="space-y-3 mb-6">
              <div className="p-3 rounded-xl bg-black/40 border border-slate-800 hover:border-imperial-gold/40 transition-colors">
                <div className="flex items-center justify-between text-xs font-bold text-white">
                  <span>Trận 1: Chiến Dịch Bạch Đằng Giang</span>
                  <span className="text-[10px] text-emerald-400 font-mono">Mở</span>
                </div>
                <p className="text-[11px] text-slate-400 mt-1">
                  Bày trận cọc ngầm, dụ địch theo con nước triều, tiêu diệt chiến thuyền ngoại xâm.
                </p>
              </div>

              <div className="p-3 rounded-xl bg-black/40 border border-slate-800 opacity-75">
                <div className="flex items-center justify-between text-xs font-bold text-slate-300">
                  <span>Trận 2: Phá Vây Rạch Gầm - Xoài Mút</span>
                  <span className="text-[10px] text-amber-400 font-mono">Chờ Lệnh</span>
                </div>
                <p className="text-[11px] text-slate-400 mt-1">
                  Tây Sơn thủy kỵ phục kích liên hoàn, hỏa hổ quét sạch quân địch.
                </p>
              </div>
            </div>
          </div>

          {/* Launch Action */}
          <div>
            <button
              onClick={handleLaunch}
              className="w-full py-4 px-6 rounded-2xl bg-gradient-to-r from-imperial-crimson via-red-600 to-imperial-darkred hover:from-red-600 hover:to-imperial-crimson text-imperial-lightgold font-cinzel font-black text-base uppercase tracking-wider border-2 border-imperial-gold shadow-2xl shadow-red-950/80 hover:scale-[1.02] transition-all flex items-center justify-center space-x-3 cursor-pointer"
            >
              <Play className="w-5 h-5 fill-current" />
              <span>Xuất Quân Vào Chiến Trường</span>
              <ChevronRight className="w-5 h-5" />
            </button>
            <p className="text-center text-[10px] text-slate-400 mt-2">
              Khởi động bàn cờ chiến thuật & vòng quay tác chiến off-chain
            </p>
          </div>

        </div>

      </div>

    </div>
  );
};
