import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

from app.core.config import get_settings
from app.core.store import store
from app.schemas import FactionOut, FactionRegisterRequest, PlayerOut, SelectFactionRequest

router = APIRouter(tags=["faction"])


@router.get("/factions", response_model=list[FactionOut])
def list_factions():
    path = Path(get_settings().factions_file)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[3] / path
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return [FactionOut(**item) for item in data["factions"]]


@router.get("/players/{wallet}", response_model=PlayerOut)
def get_player(wallet: str, chain: str | None = None):
    player = store.get_player(chain, wallet) if chain else store.find_player_any_chain(wallet)
    if player is None:
        raise HTTPException(status_code=404, detail="Player chưa tồn tại")
    return PlayerOut(
        wallet=player.wallet,
        chain=player.chain,
        username=player.username,
        faction_id=player.faction_id,
        nft_object_id=player.nft_object_id,
        level=player.level,
        rice=player.rice,
        gold=player.gold,
        morale=player.morale,
        is_guest=player.is_guest,
    )


@router.post("/players/{wallet}/faction/select", response_model=PlayerOut)
def select_faction_f2p(wallet: str, body: SelectFactionRequest):
    """Chọn Faction cho người chơi F2P / Guest mà không bắt buộc phải mint NFT (Section 13)."""
    player = store.find_player_any_chain(wallet)
    if player is None:
        # Nếu là guest session chưa lưu, tự tạo
        player = store.get_or_create_player("sui", wallet)

    player.faction_id = body.faction_id
    # Tự động gán starting advisor của faction cho người chơi
    starting_adv = store.get_starting_advisor_for_faction(body.faction_id)
    if starting_adv:
        store.equip_advisor(wallet, starting_adv)

    return PlayerOut(
        wallet=player.wallet,
        chain=player.chain,
        username=player.username,
        faction_id=player.faction_id,
        nft_object_id=player.nft_object_id,
        level=player.level,
        rice=player.rice,
        gold=player.gold,
        morale=player.morale,
        is_guest=player.is_guest,
    )


@router.post("/players/{wallet}/faction", response_model=PlayerOut)
def register_player_faction(
    wallet: str,
    body: FactionRegisterRequest,
    request: Request,
    chain: str | None = None,
):
    player = store.get_player(chain, wallet) if chain else store.find_player_any_chain(wallet)
    if player is None:
        raise HTTPException(status_code=404, detail="Player chưa tồn tại — đăng nhập ví trước")

    adapter = request.app.state.resolver.get(player.chain)

    tx = adapter.get_transaction(body.tx_digest)
    if tx is None or not tx.succeeded:
        raise HTTPException(status_code=400, detail="TX mint chưa xác nhận on-chain")
    if not adapter.verify_ownership(player.wallet, body.nft_object_id):
        raise HTTPException(status_code=400, detail="NFT không thuộc ví này")

    player.faction_id = body.faction_id
    player.nft_object_id = body.nft_object_id
    
    # Gán starting advisor
    starting_adv = store.get_starting_advisor_for_faction(body.faction_id)
    if starting_adv:
        store.equip_advisor(wallet, starting_adv)

    return PlayerOut(
        wallet=player.wallet,
        chain=player.chain,
        username=player.username,
        faction_id=player.faction_id,
        nft_object_id=player.nft_object_id,
        level=player.level,
        rice=player.rice,
        gold=player.gold,
        morale=player.morale,
        is_guest=player.is_guest,
    )
