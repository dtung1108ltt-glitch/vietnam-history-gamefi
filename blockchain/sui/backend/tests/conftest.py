import base64
import sys
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[0]))

from app.core.security import address_from_public_key, personal_message_digest
from app.main import create_app
from fake_adapter import FakeAdapter


@pytest.fixture()
def adapter():
    return FakeAdapter()


@pytest.fixture()
def client(adapter):
    app = create_app()
    app.state.adapter = adapter
    with TestClient(app) as test_client:
        yield test_client


def make_wallet():
    signing_key = ed25519.Ed25519PrivateKey.generate()
    pubkey = signing_key.public_key().public_bytes_raw()
    wallet = "0x" + address_from_public_key(0x00, pubkey)
    return signing_key, wallet


def sign_message(signing_key, message: str) -> str:
    sig = signing_key.sign(personal_message_digest(message.encode("utf-8")))
    payload = b"\x00" + sig + signing_key.public_key().public_bytes_raw()
    return base64.b64encode(payload).decode()


def login(client, wallet=None):
    signing_key, wallet = make_wallet() if wallet is None else (None, wallet)
    nonce_resp = client.post("/auth/nonce", json={"wallet": wallet}).json()
    signature = sign_message(signing_key, nonce_resp["message"])
    resp = client.post(
        "/auth/wallet",
        json={
            "wallet": wallet,
            "nonce": nonce_resp["nonce"],
            "message": nonce_resp["message"],
            "signature": signature,
        },
    )
    assert resp.status_code == 200, resp.text
    return wallet, resp.json()
