"""Solana Adapter: implement BlockchainAdapter cho chương trình Anchor
`history_game` (Devnet/Localnet).

Đối xứng với sui_adapter.py:
- Read (get_transaction / verify_ownership / get_faction_nfts): JSON-RPC
  chuẩn của Solana qua httpx (Solana KHÔNG bị khai tử JSON-RPC như SUI).
- Write (mint / reward / register): dùng `solders` để build + ký transaction
  trực tiếp trong Python bằng keypair admin (KHÔNG shell ra CLI như SUI —
  Solana không bị Windows Smart App Control chặn theo cách `sui.exe` từng bị,
  nên không cần vòng qua Docker/CLI).
"""
from __future__ import annotations

import base64
import time
from typing import Any

import base58
import httpx
from solders.hash import Hash
from solders.instruction import AccountMeta, Instruction
from solders.message import Message
from solders.pubkey import Pubkey
from solders.system_program import ID as SYSTEM_PROGRAM_ID
from solders.transaction import Transaction

from app.blockchain.borsh_utils import BorshReader, BorshWriter, anchor_discriminator
from app.blockchain.interface import BlockchainAdapter, NftInfo, TransactionInfo
from app.core.config import Settings

FACTION_NFT_SEED = b"faction_nft"


class SolanaAdapterError(RuntimeError):
    pass


class SolanaAdapter(BlockchainAdapter):
    def __init__(self, settings: Settings, http: httpx.Client | None = None):
        self.s = settings
        self.http = http or httpx.Client(timeout=20)

    def chain_name(self) -> str:
        return "solana"

    # ------------------------------------------------------------- lazy init

    def _program_id(self) -> Pubkey:
        self._require_deployment()
        return Pubkey.from_string(self.s.solana_program_id)

    def _require_deployment(self) -> None:
        if not self.s.solana_program_id:
            raise SolanaAdapterError(
                "Thiếu cấu hình deploy: SOLANA_PROGRAM_ID. Chạy scripts/deploy-solana.sh trước."
            )

    # ---------------------------------------------------------------- PDAs

    def _config_pda(self) -> Pubkey:
        return Pubkey.find_program_address([b"config"], self._program_id())[0]

    def _treasury_pda(self) -> Pubkey:
        return Pubkey.find_program_address([b"treasury"], self._program_id())[0]

    def _faction_pda(self, faction_id: int) -> Pubkey:
        return Pubkey.find_program_address([b"faction", bytes([faction_id])], self._program_id())[0]

    def _faction_nft_pda(self, wallet: str) -> Pubkey:
        owner = Pubkey.from_string(wallet)
        return Pubkey.find_program_address([FACTION_NFT_SEED, bytes(owner)], self._program_id())[0]

    # ------------------------------------------------------------------ reads

    def get_transaction(self, digest: str) -> TransactionInfo | None:
        result = self._rpc(
            "getTransaction",
            [digest, {"encoding": "json", "commitment": "confirmed", "maxSupportedTransactionVersion": 0}],
        )
        if not result:
            return None
        err = (result.get("meta") or {}).get("err")
        sender = None
        try:
            sender = result["transaction"]["message"]["accountKeys"][0]
        except (KeyError, IndexError, TypeError):
            pass
        return TransactionInfo(
            digest=digest,
            status="success" if err is None else "failure",
            sender=sender,
            timestamp_ms=(result.get("blockTime") or 0) * 1000 or None,
            events=[],
            raw=result,
        )

    def verify_ownership(self, wallet: str, object_id: str) -> bool:
        raw = self._get_account_data(Pubkey.from_string(object_id))
        if raw is None:
            return False
        owner = base58.b58encode(BorshReader(raw, offset=8).read_pubkey()).decode()
        return owner == wallet

    def get_faction_nfts(self, wallet: str) -> list[NftInfo]:
        """Thiết kế hiện tại: mỗi ví mint tối đa 1 Faction NFT (PDA theo seed
        [faction_nft, wallet]) nên danh sách có 0 hoặc 1 phần tử."""
        nft_pda = self._faction_nft_pda(wallet)
        raw = self._get_account_data(nft_pda)
        if raw is None:
            return []
        r = BorshReader(raw, offset=8)
        owner = base58.b58encode(r.read_pubkey()).decode()
        faction_id = r.read_u8()
        name = r.read_string()
        rarity = r.read_string()
        image = r.read_string()
        return [
            NftInfo(
                object_id=str(nft_pda),
                owner=owner,
                faction_id=faction_id,
                faction_name=name,
                rarity=rarity,
                image=image,
            )
        ]

    # ----------------------------------------------------------------- writes

    def mint_faction(self, recipient: str, faction_id: int) -> tuple[str, str]:
        """Server-side signing is forbidden; wallet must submit the mint."""
        raise SolanaAdapterError(
            "Server-side Solana signing is disabled. Build the instruction in the client, "
            "submit it with the player's wallet, then register the verified transaction."
        )

    def send_reward(self, recipient: str, amount: int, battle_id: int) -> str:
        raise SolanaAdapterError(
            "Server-side Solana signing is disabled. Create a backend-authorized claim "
            "and require the player's wallet to submit its transaction."
        )

    def register_faction(self, faction_id: int, name: str, rarity: str, image: str) -> str:
        raise SolanaAdapterError("Server-side faction registration is disabled; use an authorized deployment workflow.")

    # -------------------------------------------------------------- internals

    def _rpc(self, method: str, params: list) -> Any:
        try:
            resp = self.http.post(
                self.s.solana_rpc_url,
                json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
            )
            body = resp.json()
        except (httpx.HTTPError, json.JSONDecodeError) as exc:
            raise SolanaAdapterError(f"Lỗi gọi RPC {method}: {exc}") from exc
        if "error" in body:
            raise SolanaAdapterError(f"RPC {method} trả lỗi: {body['error']}")
        return body.get("result")

    def _get_account_data(self, pubkey: Pubkey) -> bytes | None:
        result = self._rpc("getAccountInfo", [str(pubkey), {"encoding": "base64", "commitment": "confirmed"}])
        if result is None or result.get("value") is None:
            return None
        return base64.b64decode(result["value"]["data"][0])

    def _latest_blockhash(self) -> Hash:
        result = self._rpc("getLatestBlockhash", [{"commitment": "confirmed"}])
        return Hash.from_string(result["value"]["blockhash"])

    def _send(self, instruction: Instruction) -> str:
        raise SolanaAdapterError(
            "Backend transaction signing is disabled. This adapter is read/verification-only; "
            "the connected player wallet must sign and submit writes."
        )

    def _confirm(self, signature: str, timeout_s: float = 30.0, interval_s: float = 1.0) -> None:
        deadline = time.time() + timeout_s
        while time.time() < deadline:
            result = self._rpc("getSignatureStatuses", [[signature], {"searchTransactionHistory": True}])
            status = result["value"][0]
            if status is not None:
                if status.get("err"):
                    raise SolanaAdapterError(f"Transaction {signature} thất bại on-chain: {status['err']}")
                if status.get("confirmationStatus") in ("confirmed", "finalized"):
                    return
            time.sleep(interval_s)
        raise SolanaAdapterError(f"Transaction {signature} không confirm được sau {timeout_s}s")
