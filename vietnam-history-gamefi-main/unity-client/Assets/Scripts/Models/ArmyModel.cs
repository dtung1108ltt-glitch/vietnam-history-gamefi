using UnityEngine;

/// <summary>
/// Local-only: backend chưa có domain Army (không có bảng armies, không có
/// endpoint /players/{wallet}/army — xem báo cáo mức độ hoàn thiện, mục P1
/// "Battle/Army/Quest/Leaderboard chưa tồn tại"). Giữ nguyên định nghĩa từ
/// script/Models/ArmyModel.cs gốc để BattleEngine local simulation vẫn chạy
/// được, nhưng KHÔNG có nguồn dữ liệu thật nào đứng sau các con số này.
/// </summary>
[System.Serializable]
public class ArmyModel
{
    public string army_id;
    public string army_name;

    public float base_power;

    public string weak_against;
    public string strong_against;

    public ArmyModel(string id, string name, float power)
    {
        this.army_id = id;
        this.army_name = name;
        this.base_power = power;
    }
}
