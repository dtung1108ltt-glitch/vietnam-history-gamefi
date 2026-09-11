from fastapi import APIRouter, Depends, HTTPException, Request

from app.blockchain.interface import BlockchainAdapter
from app.core.config import get_settings
from app.core.store import store
from app.schemas import RewardClaimRequest, RewardOut

router = APIRouter(tags=["reward"])


def get_adapter(request: Request) -> BlockchainAdapter:
    return request.app.state.adapter


@router.post("/rewards/claim", response_model=RewardOut)
def claim_reward(
    body: RewardClaimRequest,
    adapter: BlockchainAdapter = Depends(get_adapter),
):
    player = store.get_player(body.wallet)
    if player is None:
        raise HTTPException(status_code=404, detail="Player chưa tồn tại")
    amount = body.amount or get_settings().reward_amount_mist
    digest = adapter.send_reward(player.wallet, amount, body.battle_id)
    record = store.add_reward(player.wallet, body.battle_id, amount, digest)
    return RewardOut(
        id=record.id,
        wallet=record.wallet,
        battle_id=record.battle_id,
        amount=record.amount,
        tx_digest=record.tx_digest,
        status=record.status,
    )


@router.get("/players/{wallet}/rewards", response_model=list[RewardOut])
def list_rewards(wallet: str):
    return [
        RewardOut(
            id=r.id,
            wallet=r.wallet,
            battle_id=r.battle_id,
            amount=r.amount,
            tx_digest=r.tx_digest,
            status=r.status,
        )
        for r in store.rewards_of(wallet)
    ]
