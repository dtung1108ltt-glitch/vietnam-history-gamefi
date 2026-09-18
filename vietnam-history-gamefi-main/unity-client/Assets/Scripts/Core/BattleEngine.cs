using UnityEngine;
using VnHistoryGameFi.Core;

/// <summary>
/// Thay thế script/CoreLogic/BattleEngine.cs gốc. Khác biệt chính:
///   - Bỏ "using UnityEngine.InputSystem.iOS;" (không dùng tới trong file gốc,
///     chỉ là import thừa) và "using UnityEngine.Rendering.Universal;" (cũng
///     không dùng tới — file gốc không có logic rendering nào).
///   - So khớp faction bằng faction_id (int) thay vì chuỗi "F_LY" tự bịa,
///     dùng đúng GameManager.Instance.GetFactionById() lấy từ backend thật.
///   - Trận đấu VẪN mô phỏng cục bộ (client-side) vì backend chưa có domain
///     Battle — đây là giới hạn thật, không che giấu. Nhưng sau khi có kết quả,
///     hàm ClaimRewardForWinner() gọi THẬT tới POST /rewards/claim (endpoint
///     này đã tồn tại ở backend), thay vì chỉ log ra console như bản cũ.
/// </summary>
public class BattleEngine : MonoBehaviour
{
    public GameManager gameManager;

    private void Awake()
    {
        if (gameManager == null) gameManager = GameManager.Instance;
    }

    /// <summary>
    /// Test PvE đơn giản để kiểm tra luồng: player thật (đã đăng nhập + có
    /// faction) đấu với một NPC boss cấu hình cứng tại chỗ (không có wallet
    /// thật, chỉ dùng để test local).
    /// </summary>
    public void TestPvEBattle()
    {
        if (gameManager == null || gameManager.currentPlayer == null)
        {
            Debug.LogWarning("[BattleEngine] Chưa có currentPlayer — cần đăng nhập ví và chọn faction trước.");
            return;
        }
        if (!gameManager.FactionsLoaded)
        {
            Debug.LogWarning("[BattleEngine] Faction chưa load xong từ backend — thử lại sau.");
            return;
        }

        PlayerModel npcEnemy = new PlayerModel("0x_npc_boss")
        {
            faction_id = 1, // "Nhà Lý" — chỉ để test, không phải wallet/player thật
            army_type = "infantry",
        };

        ResolveBattle(gameManager.currentPlayer, npcEnemy);
    }

    public void ResolveBattle(PlayerModel attacker, PlayerModel defender)
    {
        Debug.Log("--- BẮT ĐẦU TRẬN ĐẤU (mô phỏng local, backend chưa có domain Battle) ---");
        Debug.Log($"Người chơi (faction #{attacker.faction_id} - {attacker.army_type}) " +
                   $"VS Đối thủ (faction #{defender.faction_id} - {defender.army_type})");

        float attackerScore = CalculateFinalScore(attacker);
        float defenderScore = CalculateFinalScore(defender);

        Debug.Log($"Điểm Người chơi: {attackerScore:F2} | Điểm Đối thủ: {defenderScore:F2}");

        bool playerWon = attackerScore > defenderScore;
        if (playerWon)
        {
            Debug.Log("KẾT QUẢ: THẮNG (+50 điểm)");
            attacker.score += 50;
            attacker.wins += 1;
            defender.score += 10;
            defender.losses += 1;
        }
        else
        {
            Debug.Log("KẾT QUẢ: THUA (+10 điểm an ủi)");
            attacker.score += 10;
            attacker.losses += 1;
            defender.score += 50;
            defender.wins += 1;
        }

        // battle_id ở đây chỉ là số tăng dần cục bộ trong phiên chơi — backend
        // KHÔNG có bảng battles để xác minh trận này có thật hay không (xem
        // ghi chú BattleModel.cs). Endpoint /rewards/claim vẫn nhận battle_id
        // như một con số tham chiếu, không kiểm tra tính hợp lệ của trận đấu.
        if (playerWon)
        {
            ClaimRewardForWinner(attacker, localBattleId: attacker.wins + attacker.losses);
        }
    }

    private void ClaimRewardForWinner(PlayerModel winner, int localBattleId)
    {
        var adapter = gameManager.Adapter;
        if (adapter == null)
        {
            Debug.LogWarning("[BattleEngine] Không có adapter — bỏ qua bước claim reward thật.");
            return;
        }

        adapter.ClaimReward(winner.wallet_address, localBattleId,
            reward =>
            {
                Debug.Log($"[BattleEngine] Claim reward THẬT thành công: " +
                          $"tx={reward.tx_digest}, amount={reward.amount}, status={reward.status}");
            },
            error =>
            {
                // Nhắc lại đúng lỗi P0 đã ghi trong báo cáo mức độ hoàn thiện:
                // với player chain=solana, backend hiện ném lỗi 500 không được
                // xử lý gọn (SolanaAdapterError không được bắt trong reward.py).
                Debug.LogError($"[BattleEngine] Claim reward thất bại: {error}\n" +
                                "Nếu player.chain == \"solana\", đây là lỗi P0 đã biết ở backend " +
                                "(reward.py chưa bắt SolanaAdapterError) — không phải lỗi ở Unity client.");
            });
    }

    private float CalculateFinalScore(PlayerModel target)
    {
        ArmyModel army = gameManager.armyCatalog.Find(a => a.army_id == target.army_type);
        float basePower = army != null ? army.base_power : 0f;

        FactionModel faction = gameManager.GetFactionById(target.faction_id);
        float factionModifier = faction != null ? (1f + faction.attack_bonus / 100f) : 1f;

        float powerWithModifier = basePower * factionModifier;
        float randomFactor = Random.Range(0.9f, 1.1f);

        return powerWithModifier * randomFactor;
    }
}
