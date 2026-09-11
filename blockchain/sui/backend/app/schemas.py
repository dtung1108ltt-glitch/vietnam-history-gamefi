from pydantic import BaseModel


class NonceRequest(BaseModel):
    wallet: str


class NonceResponse(BaseModel):
    nonce: str
    message: str


class WalletVerifyRequest(BaseModel):
    wallet: str
    nonce: str
    message: str
    signature: str  # base64, định dạng SUI: flag || signature || pubkey


class PlayerOut(BaseModel):
    wallet: str
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
