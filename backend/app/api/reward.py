from fastapi import APIRouter, HTTPException, Request

from app.core.config import get_settings
from app.core.store import store
from app.schemas import RewardClaimRequest, RewardOut

router = APIRouter(tags=["reward"])


@router.post("/rewards/claim", response_model=RewardOut)
def claim_reward(body: RewardClaimRequest, request: Request):
    player = store.find_player_any_chain(body.wallet)
    if player is None:
        raise HTTPException(status_code=404, detail="Player chưa tồn tại")

    adapter = request.app.state.resolver.get(player.chain)
    settings = get_settings()
    default_amount = (
        settings.reward_amount_mist if player.chain == "sui" else settings.reward_amount_lamports
    )
    # Reward amount là authority của backend/battle domain. Giữ field cũ trong
    # schema chỉ để tương thích request cũ, nhưng tuyệt đối không dùng giá trị client gửi.
    amount = default_amount

    digest = adapter.send_reward(player.wallet, amount, body.battle_id)
    record = store.add_reward(player.chain, player.wallet, body.battle_id, amount, digest)
    return RewardOut(
        id=record.id,
        wallet=record.wallet,
        chain=record.chain,
        battle_id=record.battle_id,
        amount=record.amount,
        tx_digest=record.tx_digest,
        status=record.status,
    )


@router.get("/players/{wallet}/rewards", response_model=list[RewardOut])
def list_rewards(wallet: str, chain: str | None = None):
    player = store.get_player(chain, wallet) if chain else store.find_player_any_chain(wallet)
    if player is None:
        return []
    return [
        RewardOut(
            id=r.id,
            wallet=r.wallet,
            chain=r.chain,
            battle_id=r.battle_id,
            amount=r.amount,
            tx_digest=r.tx_digest,
            status=r.status,
        )
        for r in store.rewards_of(player.chain, player.wallet)
    ]
