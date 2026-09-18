from conftest import login, login_solana, make_wallet, sign_message


def test_nonce_then_verify_creates_player(client):
    wallet, player = login(client)
    assert player["wallet"] == wallet
    assert player["chain"] == "sui"
    assert player["faction_id"] is None

    fetched = client.get(f"/players/{wallet}")
    assert fetched.status_code == 200
    assert fetched.json()["username"] == player["username"]


def test_verify_rejects_bad_signature(client):
    signing_key, wallet = make_wallet()
    nonce_resp = client.post("/auth/nonce", json={"chain": "sui", "wallet": wallet}).json()
    bad = sign_message(signing_key, "message khác hoàn toàn")
    resp = client.post(
        "/auth/wallet",
        json={
            "chain": "sui",
            "wallet": wallet,
            "nonce": nonce_resp["nonce"],
            "message": nonce_resp["message"],
            "signature": bad,
        },
    )
    assert resp.status_code == 401


def test_verify_rejects_reused_nonce(client):
    signing_key, wallet = make_wallet()
    nonce_resp = client.post("/auth/nonce", json={"chain": "sui", "wallet": wallet}).json()
    signature = sign_message(signing_key, nonce_resp["message"])
    body = {
        "chain": "sui",
        "wallet": wallet,
        "nonce": nonce_resp["nonce"],
        "message": nonce_resp["message"],
        "signature": signature,
    }
    assert client.post("/auth/wallet", json=body).status_code == 200
    assert client.post("/auth/wallet", json=body).status_code == 400


def test_nonce_rejects_unsupported_chain(client):
    resp = client.post("/auth/nonce", json={"chain": "bitcoin", "wallet": "abc"})
    assert resp.status_code == 422  # pydantic validator chặn ngay tại schema


def test_faction_mint_register_flow(client, adapter):
    wallet, _ = login(client)
    factions = client.get("/factions").json()
    assert len(factions) >= 5

    digest, object_id = adapter.mint_faction(wallet, factions[1]["faction_id"])
    resp = client.post(
        f"/players/{wallet}/faction",
        json={
            "faction_id": factions[1]["faction_id"],
            "nft_object_id": object_id,
            "tx_digest": digest,
        },
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["nft_object_id"] == object_id


def test_faction_register_rejects_ownership_mismatch(client, adapter):
    """Player B đã đăng nhập nhưng cố gắn NFT thực ra thuộc ví khác -> 400."""
    victim_wallet, _ = login(client)
    digest, object_id = adapter.mint_faction(victim_wallet, 1)

    attacker_wallet, _ = login(client)
    resp = client.post(
        f"/players/{attacker_wallet}/faction",
        json={"faction_id": 1, "nft_object_id": object_id, "tx_digest": digest},
    )
    assert resp.status_code == 400


def test_faction_register_requires_login_first(client):
    resp = client.post(
        "/players/0xchuatungdangnhap/faction",
        json={"faction_id": 1, "nft_object_id": "0xabc", "tx_digest": "0xdigest"},
    )
    assert resp.status_code == 404


def test_reward_claim_and_transaction_lookup(client):
    wallet, _ = login(client)
    resp = client.post("/rewards/claim", json={"wallet": wallet, "battle_id": 42})
    assert resp.status_code == 200, resp.text
    digest = resp.json()["tx_digest"]
    assert resp.json()["chain"] == "sui"

    tx = client.get(f"/blockchain/sui/transaction/{digest}")
    assert tx.status_code == 200
    assert tx.json()["status"] == "success"

    rewards = client.get(f"/players/{wallet}/rewards").json()
    assert len(rewards) == 1
    assert rewards[0]["battle_id"] == 42

    missing = client.get("/blockchain/sui/transaction/0xunknown")
    assert missing.status_code == 404


def test_blockchain_route_rejects_unsupported_chain(client):
    resp = client.get("/blockchain/dogecoin/transaction/abc")
    assert resp.status_code == 404


# ---------------------------------------------------------------- multi-chain


def test_solana_login_creates_player_with_correct_chain(client):
    wallet, player = login_solana(client)
    assert player["chain"] == "solana"
    assert player["wallet"] == wallet  # không bị lowercase (base58 phân biệt hoa/thường)


def test_two_players_different_chains_share_faction_reward_domain(client, adapter, solana_adapter):
    """Section 30 — Multi-chain E2E: Player A (SUI) và Player B (Solana) dùng
    chung API /factions, /rewards/claim, nhưng mỗi người đi qua đúng adapter
    của chain mình đã đăng nhập."""
    wallet_a, _ = login(client)  # SUI
    wallet_b, _ = login_solana(client)  # Solana

    digest_a, obj_a = adapter.mint_faction(wallet_a, 1)
    client.post(
        f"/players/{wallet_a}/faction",
        json={"faction_id": 1, "nft_object_id": obj_a, "tx_digest": digest_a},
    ).raise_for_status()

    digest_b, obj_b = solana_adapter.mint_faction(wallet_b, 2)
    r = client.post(
        f"/players/{wallet_b}/faction",
        json={"faction_id": 2, "nft_object_id": obj_b, "tx_digest": digest_b},
    )
    assert r.status_code == 200, r.text

    reward_a = client.post("/rewards/claim", json={"wallet": wallet_a, "battle_id": 1}).json()
    reward_b = client.post("/rewards/claim", json={"wallet": wallet_b, "battle_id": 1}).json()
    assert reward_a["chain"] == "sui"
    assert reward_b["chain"] == "solana"

    # TX của A không lẫn sang danh sách reward của B và ngược lại
    assert reward_a["tx_digest"] in adapter.txs
    assert reward_b["tx_digest"] in solana_adapter.txs
    assert reward_a["tx_digest"] not in solana_adapter.txs
