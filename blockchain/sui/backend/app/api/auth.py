from fastapi import APIRouter, Depends, HTTPException, Request

from app.blockchain.interface import BlockchainAdapter
from app.core.security import NonceStore, verify_personal_message
from app.core.store import store
from app.schemas import (
    NonceRequest,
    NonceResponse,
    PlayerOut,
    WalletVerifyRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def get_nonce_store(request: Request) -> NonceStore:
    return request.app.state.nonce_store


@router.post("/nonce", response_model=NonceResponse)
def create_nonce(body: NonceRequest, nonces: NonceStore = Depends(get_nonce_store)):
    nonce, message = nonces.create(body.wallet)
    return NonceResponse(nonce=nonce, message=message)


@router.post("/wallet", response_model=PlayerOut)
def verify_wallet(
    body: WalletVerifyRequest,
    nonces: NonceStore = Depends(get_nonce_store),
):
    if not nonces.consume(body.wallet, body.nonce):
        raise HTTPException(status_code=400, detail="Nonce không hợp lệ hoặc hết hạn")
    if not verify_personal_message(
        body.wallet, body.message.encode("utf-8"), body.signature
    ):
        raise HTTPException(status_code=401, detail="Chữ ký ví không hợp lệ")
    player = store.get_or_create_player(body.wallet)
    return PlayerOut(
        wallet=player.wallet,
        username=player.username,
        faction_id=player.faction_id,
        nft_object_id=player.nft_object_id,
    )
