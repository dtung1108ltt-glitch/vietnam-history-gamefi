import { ChainType, Faction, NonceResponse, Player, WalletVerifyRequest, FactionRegisterRequest } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

// Fallback metadata chuẩn theo assets/nft/factions.json và tài liệu kiến trúc PDF
export const DEFAULT_FACTIONS: Faction[] = [
  {
    faction_id: 1,
    name: "Nhà Lý",
    rarity: "common",
    image: "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=800&auto=format&fit=crop&q=80",
    description: "Kỷ nguyên dựng đô Thăng Long vĩ đại, rồng vàng thăng thiên, khởi sắc nền độc lập ngàn năm.",
    historical_era: "1009 – 1225",
    motto: "Nam quốc sơn hà Nam đế cư",
    attack_bonus: 10,
    defense_bonus: 20,
    movement_bonus: 10,
    special_unit: "Cấm Quân Cận Vệ & Cung Thủ Bách Bộ",
    banner_color: "from-amber-700 via-amber-600 to-yellow-500",
    coat_of_arms: "龍 (Long - Thần Long)"
  },
  {
    faction_id: 2,
    name: "Nhà Trần",
    rarity: "rare",
    image: "https://images.unsplash.com/photo-1542224566-6e85f2e6772f?w=800&auto=format&fit=crop&q=80",
    description: "Hào khí Đông A bất khuất, ba lần đại thắng Nguyên Mông, thủy chiến cắm cọc Bạch Đằng vang dội địa cầu.",
    historical_era: "1225 – 1400",
    motto: "Sát Thát - Phá Cường Địch Báo Hoàng Ân",
    attack_bonus: 25,
    defense_bonus: 15,
    movement_bonus: 15,
    special_unit: "Thủy Binh Bát Trạch & Kiếm Sư Đông A",
    banner_color: "from-red-800 via-crimson to-red-600",
    coat_of_arms: "武 (Vũ - Tinh Thần Đông A)"
  },
  {
    faction_id: 3,
    name: "Nhà Lê",
    rarity: "rare",
    image: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800&auto=format&fit=crop&q=80",
    description: "Khởi nghĩa Lam Sơn mười năm nếm mật nằm gai, gươm Thuận Thiên trừ bạo tàn, thái bình muôn thuở.",
    historical_era: "1428 – 1789",
    motto: "Lấy đại nghĩa thắng hung tàn, lấy chí nhân thay cường bạo",
    attack_bonus: 20,
    defense_bonus: 20,
    movement_bonus: 15,
    special_unit: "Thiết Kỵ Lam Sơn & Thần Tiễn Thủ",
    banner_color: "from-blue-900 via-indigo-700 to-cyan-600",
    coat_of_arms: "義 (Nghĩa - Bình Ngô Đại Cáo)"
  },
  {
    faction_id: 4,
    name: "Tây Sơn",
    rarity: "epic",
    image: "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=800&auto=format&fit=crop&q=80",
    description: "Áo vải cờ đào, hành quân thần tốc đại phá hai mươi vạn quân Thanh mùa xuân Kỷ Dậu rực lửa.",
    historical_era: "1778 – 1802",
    motto: "Đánh cho để dài tóc, đánh cho để đen răng, đánh cho sử tri Nam quốc anh hùng chi hữu chủ",
    attack_bonus: 35,
    defense_bonus: 10,
    movement_bonus: 30,
    special_unit: "Tượng Binh Pháo Chiến & Hỏa Hổ Thần Tốc",
    banner_color: "from-orange-700 via-amber-600 to-red-700",
    coat_of_arms: "威 (Uy - Quang Trung Hoàng Đế)"
  },
  {
    faction_id: 5,
    name: "Nhà Nguyễn",
    rarity: "legendary",
    image: "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=800&auto=format&fit=crop&q=80",
    description: "Triều đại thống nhất dải non sông từ Ải Nam Quan đến Mũi Cà Mau, pháo đài kiên cố và súng hỏa mai uy lực.",
    historical_era: "1802 – 1945",
    motto: "Kinh đô Huế nguy nga - Giang sơn liền một dải",
    attack_bonus: 30,
    defense_bonus: 25,
    movement_bonus: 20,
    special_unit: "Thần Cơ Doanh (Hỏa Mai & Đại Bác Tối Tân)",
    banner_color: "from-amber-600 via-yellow-600 to-amber-800",
    coat_of_arms: "統 (Thống - Vạn Lý Giang Sơn)"
  }
];

class GameApiService {
  private isServerHealthy: boolean | null = null;

  async checkHealth(): Promise<boolean> {
    try {
      const res = await fetch(`${API_BASE_URL}/health`, { method: 'GET', signal: AbortSignal.timeout(1500) });
      const data = await res.json();
      this.isServerHealthy = data?.status === 'ok';
      return this.isServerHealthy;
    } catch {
      this.isServerHealthy = false;
      return false;
    }
  }

  async getNonce(chain: ChainType, wallet: string): Promise<NonceResponse> {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/nonce`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chain, wallet }),
      });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      return await res.json();
    } catch (e) {
      console.warn('Using mock nonce fallback:', e);
      const mockNonce = Math.random().toString(36).substring(2, 18);
      return {
        nonce: mockNonce,
        message: `Dang nhap Vietnam History GameFi\nNonce: ${mockNonce}\nThoi gian: ${new Date().toISOString()}`
      };
    }
  }

  async verifyWallet(payload: WalletVerifyRequest): Promise<Player> {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/wallet`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const data = await res.json();
      return {
        ...data,
        level: 1,
        base_power: 1200,
      };
    } catch (e) {
      console.warn('Using mock player verification fallback:', e);
      return {
        wallet: payload.wallet,
        chain: payload.chain,
        username: `TuongQuan_${payload.wallet.substring(0, 6)}`,
        faction_id: null,
        nft_object_id: null,
        level: 1,
        base_power: 1200,
      };
    }
  }

  async getFactions(): Promise<Faction[]> {
    try {
      const res = await fetch(`${API_BASE_URL}/factions`, { method: 'GET' });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const data: Array<{ faction_id: number; name: string; rarity: any; image: string; description: string }> = await res.json();
      // Ghép nối với chỉ số lore & metadata nâng cao
      return data.map((item) => {
        const fallback = DEFAULT_FACTIONS.find(f => f.faction_id === item.faction_id) || DEFAULT_FACTIONS[0];
        return {
          ...fallback,
          ...item,
          rarity: item.rarity || fallback.rarity,
        };
      });
    } catch (e) {
      console.warn('Backend unavailable, using default rich faction metadata:', e);
      return DEFAULT_FACTIONS;
    }
  }

  async registerPlayerFaction(wallet: string, payload: FactionRegisterRequest): Promise<Player> {
    try {
      const res = await fetch(`${API_BASE_URL}/players/${wallet}/faction`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error(`HTTP error ${res.status}`);
      const data = await res.json();
      return {
        ...data,
        level: 1,
        base_power: 1500,
      };
    } catch (e) {
      console.warn('Using mock faction registration fallback:', e);
      return {
        wallet,
        chain: 'sui',
        username: `TuongQuan_${wallet.substring(0, 6)}`,
        faction_id: payload.faction_id,
        nft_object_id: payload.nft_object_id,
        level: 1,
        base_power: 1500,
      };
    }
  }
}

export const apiService = new GameApiService();
