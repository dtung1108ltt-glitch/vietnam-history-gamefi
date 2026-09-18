from pydantic import BaseModel, field_validator

from app.blockchain.adapter_resolver import SUPPORTED_CHAINS


def _validate_chain(v: str) -> str:
    v = v.lower()
    if v not in SUPPORTED_CHAINS:
        raise ValueError(f"chain phải là một trong {SUPPORTED_CHAINS}")
    return v


class NonceRequest(BaseModel):
    chain: str  # "sui" | "solana"
    wallet: str

    _check_chain = field_validator("chain")(_validate_chain)


class NonceResponse(BaseModel):
    nonce: str
    message: str


class WalletVerifyRequest(BaseModel):
    chain: str  # "sui" | "solana"
    wallet: str
    nonce: str
    message: str
    signature: str  # SUI: base64 (flag||sig||pubkey). Solana: base58 (ed25519 thuần).

    _check_chain = field_validator("chain")(_validate_chain)


class PlayerOut(BaseModel):
    wallet: str
    chain: str
    username: str
    faction_id: int | None
    nft_object_id: str | None


class FactionOut(BaseModel):
    faction_id: int
    name: str
    rarity: str
    image: str
    description: str


class FactionRegisterRequest(BaseModel):
    faction_id: int
    nft_object_id: str
    tx_digest: str


class RewardClaimRequest(BaseModel):
    wallet: str
    battle_id: int
    amount: int | None = None


class RewardOut(BaseModel):
    id: int
    wallet: str
    chain: str
    battle_id: int
    amount: int
    tx_digest: str
    status: str


class TransactionOut(BaseModel):
    digest: str
    status: str
    sender: str | None
    timestamp_ms: int | None
    events: list[dict]
