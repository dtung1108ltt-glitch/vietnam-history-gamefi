from fastapi import APIRouter, Depends, HTTPException, Request

from app.blockchain.interface import BlockchainAdapter
from app.core.store import store
from app.schemas import TransactionOut

router = APIRouter(prefix="/blockchain", tags=["blockchain"])


def get_adapter(request: Request) -> BlockchainAdapter:
    return request.app.state.adapter


@router.get("/{chain}/transaction/{digest}", response_model=TransactionOut)
def get_transaction(
    chain: str,
    digest: str,
    adapter: BlockchainAdapter = Depends(get_adapter),
):
    if chain != adapter.chain_name():
        raise HTTPException(status_code=404, detail=f"Chain {chain} không hỗ trợ")
    tx = adapter.get_transaction(digest)
    if tx is None:
        raise HTTPException(status_code=404, detail="Không tìm thấy transaction")
    store.mark_reward_status(digest, tx.status)
    return TransactionOut(
        digest=tx.digest,
        status=tx.status,
        sender=tx.sender,
        timestamp_ms=tx.timestamp_ms,
        events=tx.events,
    )
