"""Nonce + xác thực chữ ký ví — hỗ trợ cả SUI (personal message) và Solana
(ed25519 message signing thuần). Hai chain có định dạng địa chỉ khác nhau:
SUI là hex (không phân biệt hoa/thường -> chuẩn hoá lowercase), Solana là
base58 (PHÂN BIỆT hoa/thường -> không được lowercase, nếu không sẽ hỏng địa chỉ).
"""
from __future__ import annotations

import base64
import hashlib
import secrets
import time

import base58
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, ed25519
from cryptography.hazmat.primitives.asymmetric.utils import (
    Prehashed,
    encode_dss_signature,
)
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

FLAG_ED25519 = 0x00
FLAG_SECP256K1 = 0x01
FLAG_SECP256R1 = 0x02

LOGIN_MESSAGE_TEMPLATE = "vn-history-gamefi wallet login: {nonce}"

SUPPORTED_CHAINS = ("sui", "solana")


def normalize_wallet(chain: str, wallet: str) -> str:
    """Khoá dùng để tra cứu Player/nonce theo (chain, wallet).
    SUI: lowercase (địa chỉ hex không phân biệt hoa/thường).
    Solana: giữ nguyên (địa chỉ base58 PHÂN BIỆT hoa/thường).
    """
    if chain == "sui":
        return wallet.lower()
    return wallet


def _uleb128(value: int) -> bytes:
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        out.append(byte | (0x80 if value else 0x00))
        if not value:
            return bytes(out)


def personal_message_digest(message: bytes) -> bytes:
    """Digest mà ví SUI ký cho personal message: intent 0x03 + BCS string + blake2b-256."""
    body = b"\x03" + _uleb128(len(message)) + message
    return hashlib.blake2b(body, digest_size=32).digest()


def address_from_public_key(flag: int, public_key: bytes) -> str:
    return hashlib.blake2b(bytes([flag]) + public_key, digest_size=32).hexdigest()


def verify_personal_message(wallet: str, message: bytes, signature_b64: str) -> bool:
    """Kiểm tra chữ ký personal message đúng là của wallet (scheme ed25519/secp256k1/secp256r1)."""
    try:
        raw = base64.b64decode(signature_b64)
    except Exception:
        return False
    if len(raw) < 66:
        return False
    expected = wallet.lower().removeprefix("0x")
    flag = raw[0]
    digest = personal_message_digest(message)
    try:
        if flag == FLAG_ED25519:
            sig, pubkey = raw[1:65], raw[65:97]
            if len(pubkey) != 32:
                return False
            if address_from_public_key(flag, pubkey) != expected:
                return False
            ed25519.Ed25519PublicKey.from_public_bytes(pubkey).verify(sig, digest)
            return True
        if flag in (FLAG_SECP256K1, FLAG_SECP256R1):
            sig, pubkey = raw[1:65], raw[65:98]
            if len(pubkey) != 33:
                return False
            if address_from_public_key(flag, pubkey) != expected:
                return False
            curve = ec.SECP256K1() if flag == FLAG_SECP256K1 else ec.SECP256R1()
            r = int.from_bytes(sig[:32], "big")
            s = int.from_bytes(sig[32:64], "big")
            public_key = ec.EllipticCurvePublicKey.from_encoded_point(curve, pubkey)
            public_key.verify(
                encode_dss_signature(r, s),
                digest,
                ec.ECDSA(Prehashed(hashes.SHA256(), 32)),
            )
            return True
    except (InvalidSignature, ValueError):
        return False
    return False


def verify_solana_message(wallet: str, message: bytes, signature_b58: str) -> bool:
    """Verify chữ ký ed25519 thuần mà ví Solana (Phantom/Backpack/Solflare qua
    wallet-adapter) trả về từ `signMessage()` — không có lớp intent/BCS như SUI.
    """
    try:
        pubkey_bytes = base58.b58decode(wallet)
        signature_bytes = base58.b58decode(signature_b58)
        if len(pubkey_bytes) != 32 or len(signature_bytes) != 64:
            return False
        VerifyKey(pubkey_bytes).verify(message, signature_bytes)
        return True
    except BadSignatureError:
        return False
    except Exception:
        return False


def verify_wallet_signature(chain: str, wallet: str, message: bytes, signature: str) -> bool:
    """Điểm vào duy nhất mà auth.py cần gọi — tự chọn scheme verify theo chain,
    domain logic không cần biết chi tiết cryptographic format khác nhau ra sao.
    """
    if chain == "sui":
        return verify_personal_message(wallet, message, signature)
    if chain == "solana":
        return verify_solana_message(wallet, message, signature)
    return False


class NonceStore:
    def __init__(self, ttl_seconds: int):
        self.ttl = ttl_seconds
        self._nonces: dict[str, tuple[str, float]] = {}

    def create(self, chain: str, wallet: str) -> tuple[str, str]:
        nonce = secrets.token_hex(16)
        key = f"{chain}:{normalize_wallet(chain, wallet)}"
        self._nonces[key] = (nonce, time.time() + self.ttl)
        return nonce, LOGIN_MESSAGE_TEMPLATE.format(nonce=nonce)

    def consume(self, chain: str, wallet: str, nonce: str) -> bool:
        key = f"{chain}:{normalize_wallet(chain, wallet)}"
        entry = self._nonces.pop(key, None)
        if entry is None:
            return False
        stored, expires_at = entry
        return stored == nonce and time.time() < expires_at
