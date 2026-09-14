"""Interface chung cho mọi blockchain adapter (thống nhất với Dev 1).

Domain logic chỉ gọi BlockchainAdapter, không import SDK của chain cụ thể.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class TransactionInfo:
    digest: str
    status: str  # "success" | "failure" | "pending"
    sender: str | None = None
    timestamp_ms: int | None = None
    events: list[dict] = field(default_factory=list)
    raw: dict = field(default_factory=dict)

    @property
    def succeeded(self) -> bool:
        return self.status == "success"


@dataclass
class NftInfo:
    object_id: str
    owner: str
    faction_id: int
    faction_name: str
    rarity: str
    image: str


class BlockchainAdapter(ABC):
    """Contract mà SUI Adapter và Solana Adapter phải implement."""

    @abstractmethod
    def chain_name(self) -> str:
        ...

    @abstractmethod
    def mint_faction(self, recipient: str, faction_id: int) -> tuple[str, str]:
        """Mint Faction NFT cho wallet. Trả về (tx_digest, nft_object_id)."""

    @abstractmethod
    def send_reward(self, recipient: str, amount: int, battle_id: int) -> str:
        """Battle Result -> Reward on-chain. Trả về tx digest."""

    @abstractmethod
    def get_transaction(self, digest: str) -> TransactionInfo | None:
        """Xác thực TX đã lên chain; None nếu digest chưa tồn tại."""

    @abstractmethod
    def verify_ownership(self, wallet: str, object_id: str) -> bool:
        """True nếu object thuộc về wallet (owner on-chain)."""

    @abstractmethod
    def get_faction_nfts(self, wallet: str) -> list[NftInfo]:
        ...
