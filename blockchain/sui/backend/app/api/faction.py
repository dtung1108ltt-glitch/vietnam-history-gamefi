import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request

from app.blockchain.interface import BlockchainAdapter
from app.core.config import get_settings
from app.core.store import store
from app.schemas import FactionOut, FactionRegisterRequest, PlayerOut

router = APIRouter(tags=["faction"])


def get_adapter(request: Request) -> BlockchainAdapter:
    return request.app.state.adapter


@router.get("/factions", response_model=list[FactionOut])
def list_factions():
    path = Path(get_settings().factions_file)
    if not path.is_absolute():
        path = Path(__file__).resolve().parents[3] / path
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return [FactionOut(**item) for item in data["factions"]]


@router.get("/players/{wallet}", response_model=PlayerOut)
def get_player(wallet: str):
    player = store.get_player(wallet)
    if player is None:
        raise HTTPException(status_code=404, detail="Player chưa tồn tại")
    return PlayerOut(
        wallet=player.wallet,
        username=player.username,
        faction_id=player.faction_id,
        nft_object_id=player.nft_object_id,
    )


@router.post("/players/{wallet}/faction", response_model=PlayerOut)
def register_player_faction(
    wallet: str,
    body: FactionRegisterRequest,
    adapter: BlockchainAdapter = Depends(get_adapter),
):
    player = store.get_or_create_player(wallet)
    tx = adapter.get_transaction(body.tx_digest)
    if tx is None or not tx.succeeded:
        raise HTTPException(status_code=400, detail="TX mint chưa xác nhận on-chain")
    if not adapter.verify_ownership(player.wallet, body.nft_object_id):
        raise HTTPException(status_code=400, detail="NFT không thuộc ví này")
    player.faction_id = body.faction_id
    player.nft_object_id = body.nft_object_id
    return PlayerOut(
        wallet=player.wallet,
        username=player.username,
        faction_id=player.faction_id,
        nft_object_id=player.nft_object_id,
    )
