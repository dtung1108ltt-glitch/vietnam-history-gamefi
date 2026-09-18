export type ChainType = 'sui' | 'solana';

export type RarityType = 'common' | 'rare' | 'epic' | 'legendary';

export interface Faction {
  faction_id: number;
  name: string;
  rarity: RarityType;
  image: string;
  description: string;
  historical_era: string;
  motto: string;
  attack_bonus: number;
  defense_bonus: number;
  movement_bonus: number;
  special_unit: string;
  banner_color: string;
  coat_of_arms: string;
}

export interface Player {
  wallet: string;
  chain: ChainType;
  username: string;
  faction_id: number | null;
  nft_object_id: string | null;
  level: number;
  base_power: number;
  created_at?: string;
}

export interface NonceResponse {
  nonce: string;
  message: string;
}

export interface WalletVerifyRequest {
  chain: ChainType;
  wallet: string;
  nonce: string;
  message: string;
  signature: string;
}

export interface FactionRegisterRequest {
  faction_id: number;
  nft_object_id: string;
  tx_digest: string;
}

export type PreGameStep = 
  | 'splash'            // Màn hình mở đầu & đề tự hào khí
  | 'faction_select'   // Chọn triều đại & chiêu mộ tộc hệ
  | 'lobby'            // Sảnh tiền trạm duyệt binh trước khi xuất quân
  | 'battle_transition' // Chuyển cảnh tiến vào trận chiến
  | 'campaign_map'      // Bản đồ Chiến Dịch Lịch Sử (chọn mặt trận)
  | 'battle';           // Bàn cờ chiến thuật theo lượt (hex tactical battle)

export interface WalletInfo {
  name: string;
  icon: string;
  chain: ChainType;
  installed: boolean;
  adapterName: string;
}

// ---------------------------------------------------------------------------
// Chiến Dịch Lịch Sử (Historic Campaign) — Bản đồ chiến dịch
// ---------------------------------------------------------------------------

export type ChapterStatus = 'active' | 'available' | 'locked';

export interface CampaignChapter {
  chapter_id: number;
  faction_id: number;
  code: string;
  title_vi: string;
  title_en: string;
  era: string;
  status: ChapterStatus;
}

export interface MapLocation {
  location_id: string;
  chapter_id: number;
  name: string;
  sub_label: string;
  flag_glyph: string;
  x: number; // vị trí % theo chiều ngang trên bản đồ
  y: number; // vị trí % theo chiều dọc trên bản đồ
  is_capital?: boolean;
  is_target?: boolean;
  tooltip?: string;
}

export interface PlayerResources {
  rice: number;
  gold: number;
  morale: number;
}

// ---------------------------------------------------------------------------
// Bàn Cờ Chiến Thuật (Tactical Hex Battle)
// ---------------------------------------------------------------------------

export type TerrainType = 'plain' | 'hill' | 'forest' | 'mud' | 'river' | 'stakes' | 'fort';

export type BattleZone = 'ally' | 'enemy' | 'neutral';

export interface HexTile {
  col: number;
  row: number;
  terrain: TerrainType;
  zone: BattleZone;
  label?: string;
  effect?: string;
}

export type UnitSide = 'player' | 'enemy';
export type UnitIcon = 'spear' | 'archer' | 'elephant' | 'cavalry';

export interface BattleUnitStats {
  at: number;   // Quân số (Troop Strength)
  atk: number;  // Tấn công
  def: number;  // Phòng thủ
  asTk: number; // Tốc độ tác chiến (Attack Speed / Tốc kích)
  atf: number;  // Hỏa lực tầm xa (Attack Force)
  reg: number;  // Hồi phục (Regeneration)
}

export interface BattleUnit {
  unit_id: string;
  name: string;
  side: UnitSide;
  icon: UnitIcon;
  col: number;
  row: number;
  stats: BattleUnitStats;
}

export type TacticalAction = 'move' | 'attack' | 'formation' | 'fire_arrow';

export type TideState = 'rising' | 'high' | 'ebbing' | 'low';
