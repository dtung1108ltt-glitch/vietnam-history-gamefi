using UnityEngine;

/// <summary>
/// Khớp với backend PlayerOut (wallet/chain/username/faction_id/nft_object_id
/// là dữ liệu THẬT lấy từ API). Các field score/wins/losses là state local
/// dùng cho battle simulation phía client — CHƯA có domain Battle ở backend
/// (xem docs/architecture-review section "Battle/Army/Quest/Leaderboard chưa
/// tồn tại"), nên các số liệu này chỉ tồn tại trong phiên chơi hiện tại, KHÔNG
/// được đồng bộ lên server.
/// </summary>
[System.Serializable]
public class PlayerModel
{
    // ---- Từ backend (PlayerDto) ----
    public string wallet_address;
    public string chain;           // "sui" | "solana"
    public string username;
    public int faction_id;         // 0 = chưa chọn faction; factions thật đánh số 1-5
    public string nft_object_id;   // null/"" = chưa mint

    // ---- Local-only, chưa có ở backend ----
    public string army_type;
    public int score;
    public int wins;
    public int losses;

    public PlayerModel(string wallet, string chain = "sui")
    {
        this.wallet_address = wallet;
        this.chain = chain;
        this.score = 0;
        this.wins = 0;
        this.losses = 0;
    }

    public static PlayerModel FromDto(VnHistoryGameFi.Network.PlayerDto dto)
    {
        var model = new PlayerModel(dto.wallet, dto.chain)
        {
            username = dto.username,
            faction_id = dto.faction_id,
            nft_object_id = dto.nft_object_id,
        };
        return model;
    }
}
