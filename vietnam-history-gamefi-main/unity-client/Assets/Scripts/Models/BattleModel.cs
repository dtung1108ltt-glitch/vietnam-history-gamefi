using UnityEngine;

/// <summary>
/// Local-only: backend chưa có domain Battle (không có bảng battles, không có
/// POST /battles hay GET /battles/{id}/GET /leaderboard). Kết quả trận đấu ở
/// đây chỉ tồn tại trong phiên chơi hiện tại của client, KHÔNG được ghi nhận
/// lại phía server — trừ battle_id gửi kèm khi gọi ClaimReward() (backend chỉ
/// dùng battle_id như một con số tham chiếu, không xác minh trận đấu có thật).
/// </summary>
[System.Serializable]
public class BattleModel
{
    public string battle_id;
    public string attacker_wallet;
    public string defender_wallet;
    public float attacker_score;
    public float defender_score;
    public string winner_wallet;
}
