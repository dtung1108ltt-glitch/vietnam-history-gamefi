import base64
import sys
from pathlib import Path

import base58
import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from fastapi.testclient import TestClient
from solders.keypair import Keypair as SolanaKeypair

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[0]))

from app.core.security import address_from_public_key, personal_message_digest
from app.main import create_app
from fake_adapter import FakeAdapter


class StubResolver:
    """Thay AdapterResolver thật trong test — trả thẳng FakeAdapter theo chain,
    không cần cấu hình RPC/keypair thật."""

    def __init__(self, sui_adapter: FakeAdapter, solana_adapter: FakeAdapter):
        self._adapters = {"sui": sui_adapter, "solana": solana_adapter}

    def get(self, chain: str):
        from app.blockchain.adapter_resolver import UnsupportedChainError

        chain = chain.lower()
        if chain not in self._adapters:
            raise UnsupportedChainError(f"Chain '{chain}' không được hỗ trợ")
        return self._adapters[chain]


@pytest.fixture()
def adapter():
    """Fake SUI adapter — giữ tên cũ để tương thích các test hiện có."""
    return FakeAdapter(chain="sui")


@pytest.fixture()
def solana_adapter():
    return FakeAdapter(chain="solana")


@pytest.fixture()
def client(adapter, solana_adapter):
    app = create_app()
    app.state.resolver = StubResolver(adapter, solana_adapter)
    with TestClient(app) as test_client:
        yield test_client


# ---------- helpers ký chữ ký SUI ----------


def make_wallet():
    signing_key = ed25519.Ed25519PrivateKey.generate()
    pubkey = signing_key.public_key().public_bytes_raw()
    wallet = "0x" + address_from_public_key(0x00, pubkey)
    return signing_key, wallet


def sign_message(signing_key, message: str) -> str:
    sig = signing_key.sign(personal_message_digest(message.encode("utf-8")))
    payload = b"\x00" + sig + signing_key.public_key().public_bytes_raw()
    return base64.b64encode(payload).decode()


def login(client, wallet=None, chain: str = "sui"):
    signing_key, wallet = make_wallet() if wallet is None else (None, wallet)
    nonce_resp = client.post("/auth/nonce", json={"chain": chain, "wallet": wallet}).json()
    signature = sign_message(signing_key, nonce_resp["message"])
    resp = client.post(
        "/auth/wallet",
        json={
            "chain": chain,
            "wallet": wallet,
            "nonce": nonce_resp["nonce"],
            "message": nonce_resp["message"],
            "signature": signature,
        },
    )
    assert resp.status_code == 200, resp.text
    return wallet, resp.json()


# ---------- helpers ký chữ ký Solana ----------


def make_solana_wallet():
    kp = SolanaKeypair()
    return kp, str(kp.pubkey())


def sign_solana_message(kp: SolanaKeypair, message: str) -> str:
    sig = kp.sign_message(message.encode("utf-8"))
    return base58.b58encode(bytes(sig)).decode()


def login_solana(client, kp=None):
    kp, wallet = make_solana_wallet() if kp is None else (kp, str(kp.pubkey()))
    nonce_resp = client.post("/auth/nonce", json={"chain": "solana", "wallet": wallet}).json()
    signature = sign_solana_message(kp, nonce_resp["message"])
    resp = client.post(
        "/auth/wallet",
        json={
            "chain": "solana",
            "wallet": wallet,
            "nonce": nonce_resp["nonce"],
            "message": nonce_resp["message"],
            "signature": signature,
        },
    )
    assert resp.status_code == 200, resp.text
    return wallet, resp.json()
