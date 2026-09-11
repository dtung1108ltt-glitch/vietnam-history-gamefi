import base64

from app.core.security import (
    address_from_public_key,
    personal_message_digest,
    verify_personal_message,
)
from conftest import make_wallet, sign_message


def test_valid_ed25519_signature():
    signing_key, wallet = make_wallet()
    message = "vn-history-gamefi wallet login: abc123"
    assert verify_personal_message(wallet, message.encode(), sign_message(signing_key, message))


def test_wrong_message_fails():
    signing_key, wallet = make_wallet()
    signature = sign_message(signing_key, "message A")
    assert not verify_personal_message(wallet, b"message B", signature)


def test_wrong_wallet_fails():
    signing_key, wallet = make_wallet()
    _, other = make_wallet()
    message = "msg"
    assert not verify_personal_message(other, message.encode(), sign_message(signing_key, message))
    assert address_from_public_key(0, b"\x00" * 32) != wallet


def test_garbage_signature_fails():
    _, wallet = make_wallet()
    assert not verify_personal_message(wallet, b"msg", base64.b64encode(b"short").decode())
    assert not verify_personal_message(wallet, b"msg", "not-base64!!!")


def test_personal_message_digest_matches_sui_intent():
    # intent personal message (0x03) + BCS string prefix
    digest = personal_message_digest(b"hello")
    assert len(digest) == 32
    assert digest != personal_message_digest(b"hellp")
