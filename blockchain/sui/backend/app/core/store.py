"""Store in-memory cho phần integration của Dev 2.

Dev 1 sở hữu PostgreSQL repositories; lớp này chỉ giữ trạng thái tối thiểu
để các luồng wallet -> player -> faction NFT -> reward chạy end-to-end.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class Player:
    wallet: str
    username: str
    faction_id: int | None = None
    nft_object_id: str | None = None
    created_at: float = field(default_factory=time.time)


@dataclass
class RewardRecord:
    id: int
    wallet: str
    battle_id: int
    amount: int
    tx_digest: str
    status: str = "pending"


class Store:
    def __init__(self) -> None:
        self.players: dict[str, Player] = {}
        self.rewards: list[RewardRecord] = []
        self._reward_seq = 0

    def get_or_create_player(self, wallet: str) -> Player:
        key = wallet.lower()
        if key not in self.players:
            self.players[key] = Player(
                wallet=key, username=f"player-{key[:6]}"
            )
        return self.players[key]

    def get_player(self, wallet: str) -> Player | None:
        return self.players.get(wallet.lower())

    def add_reward(self, wallet: str, battle_id: int, amount: int, tx_digest: str) -> RewardRecord:
        self._reward_seq += 1
        record = RewardRecord(
            id=self._reward_seq,
            wallet=wallet.lower(),
            battle_id=battle_id,
            amount=amount,
            tx_digest=tx_digest,
        )
        self.rewards.append(record)
        return record

    def rewards_of(self, wallet: str) -> list[RewardRecord]:
        return [r for r in self.rewards if r.wallet == wallet.lower()]

    def mark_reward_status(self, tx_digest: str, status: str) -> None:
        for record in self.rewards:
            if record.tx_digest == tx_digest and record.status != status:
                record.status = status


store = Store()
