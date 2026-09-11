from conftest import login, make_wallet, sign_message


def test_nonce_then_verify_creates_player(client):
    wallet, player = login(client)
    assert player["wallet"] == wallet
    assert player["faction_id"] is None

    fetched = client.get(f"/players/{wallet}")
    assert fetched.status_code == 200
    assert fetched.json()["username"] == player["username"]


def test_verify_rejects_bad_signature(client):
    signing_key, wallet = make_wallet()
    nonce_resp = client.post("/auth/nonce", json={"wallet": wallet}).json()
    bad = sign_message(signing_key, "message khác hoàn toàn")
    resp = client.post(
        "/auth/wallet",
        json={
            "wallet": wallet,
            "nonce": nonce_resp["nonce"],
            "message": nonce_resp["message"],
            "signature": bad,
        },
    )
    assert resp.status_code == 401


def test_verify_rejects_reused_nonce(client):
    signing_key, wallet = make_wallet()
    nonce_resp = client.post("/auth/nonce", json={"wallet": wallet}).json()
    signature = sign_message(signing_key, nonce_resp["message"])
    body = {
        "wallet": wallet,
        "nonce": nonce_resp["nonce"],
        "message": nonce_resp["message"],
        "signature": signature,
    }
    assert client.post("/auth/wallet", json=body).status_code == 200
    assert client.post("/auth/wallet", json=body).status_code == 400


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

    wrong_owner = client.post(
        "/players/0xdeadbeef/faction",
        json={
            "faction_id": 1,
            "nft_object_id": object_id,
            "tx_digest": digest,
        },
    )
    assert wrong_owner.status_code == 400


def test_reward_claim_and_transaction_lookup(client):
    wallet, _ = login(client)
    resp = client.post("/rewards/claim", json={"wallet": wallet, "battle_id": 42})
    assert resp.status_code == 200, resp.text
    digest = resp.json()["tx_digest"]

    tx = client.get(f"/blockchain/sui/transaction/{digest}")
    assert tx.status_code == 200
    assert tx.json()["status"] == "success"

    rewards = client.get(f"/players/{wallet}/rewards").json()
    assert len(rewards) == 1
    assert rewards[0]["battle_id"] == 42

    missing = client.get("/blockchain/sui/transaction/0xunknown")
    assert missing.status_code == 404
