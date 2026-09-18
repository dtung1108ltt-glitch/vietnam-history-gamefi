"""Store in-memory cho phần integration của Dev 2.

Dev 1 sở hữu PostgreSQL repositories; lớp này chỉ giữ trạng thái tối thiểu
để các luồng wallet -> player -> faction NFT -> reward chạy end-to-end,
cho CẢ 2 chain (mục 34: phân biệt theo `chain`, không tách DB riêng).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from app.core.security import normalize_wallet


@dataclass
class Player:
    wallet: str
    chain: str
    username: str
    faction_id: int | None = None
    nft_object_id: str | None = None
    created_at: float = field(default_factory=time.time)


@dataclass
class RewardRecord:
    id: int
    wallet: str
    chain: str
    battle_id: int
    amount: int
    tx_digest: str
    status: str = "pending"


class Store:
    def __init__(self) -> None:
        self.players: dict[str, Player] = {}
        self.rewards: list[RewardRecord] = []
        self._reward_seq = 0

    @staticmethod
    def _key(chain: str, wallet: str) -> str:
        return f"{chain}:{normalize_wallet(chain, wallet)}"

    def get_or_create_player(self, chain: str, wallet: str) -> Player:
        key = self._key(chain, wallet)
        if key not in self.players:
            self.players[key] = Player(
                wallet=normalize_wallet(chain, wallet),
                chain=chain,
                username=f"player-{key[-6:]}",
            )
        return self.players[key]

    def get_player(self, chain: str, wallet: str) -> Player | None:
        return self.players.get(self._key(chain, wallet))

    def find_player_any_chain(self, wallet: str) -> Player | None:
        """Dùng khi endpoint không (hoặc chưa) nhận tham số chain tường minh —
        tra theo cả 2 chain. Nếu ví trùng nhau giữa 2 chain (cực hiếm vì khác
        định dạng địa chỉ) sẽ ưu tiên SUI trước."""
        for chain in ("sui", "solana"):
            player = self.get_player(chain, wallet)
            if player is not None:
                return player
        return None

    def add_reward(
        self, chain: str, wallet: str, battle_id: int, amount: int, tx_digest: str
    ) -> RewardRecord:
        self._reward_seq += 1
        record = RewardRecord(
            id=self._reward_seq,
            wallet=normalize_wallet(chain, wallet),
            chain=chain,
            battle_id=battle_id,
            amount=amount,
            tx_digest=tx_digest,
        )
        self.rewards.append(record)
        return record

    def rewards_of(self, chain: str, wallet: str) -> list[RewardRecord]:
        norm = normalize_wallet(chain, wallet)
        return [r for r in self.rewards if r.chain == chain and r.wallet == norm]

    def mark_reward_status(self, chain: str, tx_digest: str, status: str) -> None:
        for record in self.rewards:
            if record.chain == chain and record.tx_digest == tx_digest and record.status != status:
                record.status = status


store = Store()
