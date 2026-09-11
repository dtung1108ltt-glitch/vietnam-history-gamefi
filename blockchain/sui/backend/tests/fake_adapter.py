"""FakeAdapter cho pytest: implement BlockchainAdapter không cần mạng."""
from __future__ import annotations

from app.blockchain.interface import BlockchainAdapter, NftInfo, TransactionInfo


class FakeAdapter(BlockchainAdapter):
    def __init__(self) -> None:
        self.txs: dict[str, TransactionInfo] = {}
        self.ownership: dict[str, str] = {}
        self.nfts: dict[str, list[NftInfo]] = {}
        self._seq = 0

    def chain_name(self) -> str:
        return "sui"

    def mint_faction(self, recipient: str, faction_id: int) -> tuple[str, str]:
        self._seq += 1
        digest = f"0xfakedigest{self._seq}"
        object_id = f"0xnft{self._seq}"
        self.ownership[object_id] = recipient.lower()
        self.nfts.setdefault(recipient.lower(), []).append(
            NftInfo(object_id, recipient.lower(), faction_id, f"Faction {faction_id}", "rare", "img.png")
        )
        self.txs[digest] = TransactionInfo(
            digest=digest,
            status="success",
            sender=recipient,
            timestamp_ms=1_700_000_000_000,
            events=[{"eventType": "FactionMinted", "faction_id": faction_id}],
        )
        return digest, object_id

    def send_reward(self, recipient: str, amount: int, battle_id: int) -> str:
        self._seq += 1
        digest = f"0xfakedigest{self._seq}"
        self.txs[digest] = TransactionInfo(
            digest=digest,
            status="success",
            sender="0xadmin",
            timestamp_ms=1_700_000_000_001,
            events=[{"recipient": recipient, "amount": amount, "battle_id": battle_id}],
        )
        return digest

    def get_transaction(self, digest: str) -> TransactionInfo | None:
        return self.txs.get(digest)

    def verify_ownership(self, wallet: str, object_id: str) -> bool:
        return self.ownership.get(object_id) == wallet.lower()

    def get_faction_nfts(self, wallet: str) -> list[NftInfo]:
        return self.nfts.get(wallet.lower(), [])
