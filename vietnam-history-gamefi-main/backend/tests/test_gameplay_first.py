"""Kiểm thử toàn diện cho kiến trúc Gameplay-First:
1. Chơi Free-to-Play không cần ví (Guest / F2P)
2. Chọn Faction không cần mint NFT
3. Quản lý quân đội và trang bị Tướng Cố Vấn
4. Tính toán trận đánh off-chain (Battle Engine không đụng blockchain)
5. Nhiệm vụ (Quests) và Bảng xếp hạng (Leaderboard)
6. Chợ Tướng Cố Vấn (Marketplace & P2P Trade)
"""
import pytest


def test_f2p_guest_flow(client):
    # 1. Đăng nhập Guest không cần ví
    resp = client.post("/auth/guest", json={"username": "TuongQuan_DaiViet"})
    assert resp.status_code == 200
    player = resp.json()
    assert player["is_guest"] is True
    assert "guest_" in player["wallet"]
    assert player["faction_id"] is None

    # 2. Xem danh sách 8 tộc hệ lịch sử
    factions_resp = client.get("/factions")
    assert factions_resp.status_code == 200
    factions = factions_resp.json()
    assert len(factions) >= 8

    # 3. Chọn Faction Nhà Trần F2P (không cần mint NFT)
    tran_faction = next(f for f in factions if f["name"] == "Nhà Trần")
    sel_resp = client.post(
        f"/players/{player['wallet']}/faction/select",
        json={"faction_id": tran_faction["faction_id"]},
    )
    assert sel_resp.status_code == 200
    updated_player = sel_resp.json()
    assert updated_player["faction_id"] == tran_faction["faction_id"]

    # 4. Kiểm tra quân đội tự động được gán starting advisor (Trần Hưng Đạo)
    army_resp = client.get(f"/players/{player['wallet']}/army")
    assert army_resp.status_code == 200
    army = army_resp.json()
    assert army["equipped_advisor_id"] == "tran_hung_dao"
    assert "Trần Hưng Đạo" in army["equipped_advisor_name"]
    assert army["total_power"] > 500


def test_advisor_catalog(client):
    # Lấy danh sách tướng cố vấn
    resp = client.get("/advisors")
    assert resp.status_code == 200
    advisors = resp.json()
    assert len(advisors) >= 10

    # Lọc theo tộc hệ Nhà Trần (faction_id = 5)
    tran_advisors = client.get("/advisors?faction_id=5").json()
    assert any(a["id"] == "tran_hung_dao" for a in tran_advisors)

    # Xem chi tiết Trần Hưng Đạo
    thd = client.get("/advisors/tran_hung_dao").json()
    assert thd["rarity"] == "legendary"
    assert "Vạn Kiếp" in thd["passive_name"]
    assert "Hịch Tướng Sĩ" in thd["active_skill"]
    assert thd["base_leadership"] == 100

    # Kiểm tra endpoint ownership
    own_resp = client.get("/advisors/tran_hung_dao/ownership")
    assert own_resp.status_code == 200


def test_offchain_battle_engine(client):
    # Tạo player F2P
    player = client.post("/auth/guest", json={"username": "ChiHuyTruong"}).json()
    client.post(
        f"/players/{player['wallet']}/faction/select",
        json={"faction_id": 5},  # Nhà Trần
    )

    # Thực hiện trận đánh Đại Chiến Bạch Đằng (không có blockchain transaction)
    battle_req = {
        "player_wallet": player["wallet"],
        "scenario_id": "bach_dang_1288",
        "tactical_formation": "defensive",
        "advisor_id": "tran_hung_dao",
    }
    battle_resp = client.post("/battles", json=battle_req)
    assert battle_resp.status_code == 200
    result = battle_resp.json()
    assert "battle-" in result["battle_id"]
    assert result["scenario_id"] == "bach_dang_1288"
    assert len(result["combat_logs"]) == 5
    assert result["reward_rice"] > 0
    assert result["reward_gold"] > 0

    # Kiểm tra log chiến thuật có nhắc đến skill của Trần Hưng Đạo
    log_messages = " ".join(log["log_message"] for log in result["combat_logs"])
    assert "Trần Hưng Đạo" in log_messages or "Vạn Kiếp" in log_messages

    # Đọc lại trận đánh bằng GET /battles/{id}
    fetch_resp = client.get(f"/battles/{result['battle_id']}")
    assert fetch_resp.status_code == 200
    assert fetch_resp.json()["battle_id"] == result["battle_id"]


def test_quests_and_leaderboard(client):
    # Kiểm tra danh sách nhiệm vụ lịch sử
    quests_resp = client.get("/quests")
    assert quests_resp.status_code == 200
    quests = quests_resp.json()
    assert len(quests) >= 4
    assert any("Bạch Đằng" in q["title"] for q in quests)

    # Kiểm tra bảng xếp hạng off-chain
    lb_resp = client.get("/leaderboard")
    assert lb_resp.status_code == 200
    lb = lb_resp.json()
    assert isinstance(lb, list)


def test_marketplace_and_trades(client):
    # Lấy danh sách niêm yết trên chợ tướng
    market_resp = client.get("/marketplace")
    assert market_resp.status_code == 200
    listings = market_resp.json()
    assert len(listings) >= 1

    listing = listings[0]
    assert "listing_id" in listing
    assert listing["status"] == "active"

    # Tạo niêm yết mới
    new_listing_req = {
        "advisor_id": "ly_thuong_kiet",
        "seller_wallet": "0x1111222233334444555566667777888899990000111122223333444455556666",
        "chain": "sui",
        "price": 45.0,
        "currency": "SUI",
        "token_id": "0xltk_token_01",
    }
    create_resp = client.post("/marketplace/list", json=new_listing_req)
    assert create_resp.status_code == 200
    created = create_resp.json()
    assert created["advisor_id"] == "ly_thuong_kiet"
    assert created["status"] == "active"

    # Mua tướng niêm yết
    buy_resp = client.post(
        "/marketplace/buy",
        json={
            "listing_id": created["listing_id"],
            "buyer_wallet": "0x9999888877776666555544443333222211110000999988887777666655554444",
            "tx_digest": "0xbought_digest_123",
        },
    )
    assert buy_resp.status_code == 200
    assert buy_resp.json()["status"] == "sold"

    # Tạo đề nghị trao đổi P2P giữa hai người chơi
    trade_req = {
        "initiator_wallet": "0x9999888877776666555544443333222211110000999988887777666655554444",
        "target_wallet": "0x1111222233334444555566667777888899990000111122223333444455556666",
        "offered_advisor_id": "ly_thuong_kiet",
        "requested_advisor_id": "tran_hung_dao",
        "chain": "sui",
    }
    trade_resp = client.post("/trades", json=trade_req)
    assert trade_resp.status_code == 200
    trade = trade_resp.json()
    assert trade["status"] == "pending"

    # Chấp nhận trao đổi
    accept_resp = client.post(
        f"/trades/{trade['trade_id']}/accept",
        json={
            "trade_id": trade["trade_id"],
            "wallet": "0x1111222233334444555566667777888899990000111122223333444455556666",
            "tx_digest": "0xtrade_digest_456",
        },
    )
    assert accept_resp.status_code == 200
    assert accept_resp.json()["status"] == "accepted"

