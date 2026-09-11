"""SUI Adapter: implement BlockchainAdapter cho mạng SUI (testnet/local).

Read (get_transaction / verify_ownership / get_faction_nfts): SUI GraphQL,
fallback JSON-RPC (local node) vì public fullnode đã bỏ JSON-RPC.
Write (mint / reward / register): gọi `sui client call` qua subprocess,
key của backend nằm trong keystore của SUI CLI (không nhúng private key vào code).
"""
from __future__ import annotations

import json
import os
import subprocess
from typing import Any

import httpx

from app.blockchain.interface import BlockchainAdapter, NftInfo, TransactionInfo
from app.core.config import Settings

FACTION_NFT_TYPE = "faction_nft::FactionNft"


class SuiAdapterError(RuntimeError):
    pass


class SuiAdapter(BlockchainAdapter):
    def __init__(self, settings: Settings, http: httpx.Client | None = None):
        self.s = settings
        self.http = http or httpx.Client(timeout=20)

    def chain_name(self) -> str:
        return "sui"

    # ------------------------------------------------------------------ reads

    def get_transaction(self, digest: str) -> TransactionInfo | None:
        info = self._tx_via_graphql(digest)
        if info is None:
            info = self._tx_via_rpc(digest)
        return info

    def verify_ownership(self, wallet: str, object_id: str) -> bool:
        owner = self._object_owner_via_graphql(object_id)
        if owner is None:
            owner = self._object_owner_via_rpc(object_id)
        if owner is None:
            return False
        return owner.lower() == wallet.lower()

    def get_faction_nfts(self, wallet: str) -> list[NftInfo]:
        nfts = self._owned_nfts_via_graphql(wallet)
        if nfts is None:
            nfts = self._owned_nfts_via_rpc(wallet)
        return nfts or []

    # ----------------------------------------------------------------- writes

    def mint_faction(self, recipient: str, faction_id: int) -> tuple[str, str]:
        self._require_deployment("sui_catalog_id", "sui_faction_admin_id")
        digest, created = self._client_call(
            "faction_nft",
            "mint_faction_for",
            [
                self.s.sui_faction_admin_id,
                self.s.sui_catalog_id,
                str(faction_id),
                recipient,
            ],
        )
        nft_id = self._find_created(created, FACTION_NFT_TYPE, recipient)
        return digest, nft_id

    def send_reward(self, recipient: str, amount: int, battle_id: int) -> str:
        self._require_deployment("sui_treasury_id", "sui_reward_admin_id")
        digest, _ = self._client_call(
            "reward",
            "send_reward",
            [
                self.s.sui_reward_admin_id,
                self.s.sui_treasury_id,
                recipient,
                str(amount),
                str(battle_id),
            ],
        )
        return digest

    def register_faction(
        self, faction_id: int, name: str, rarity: str, image: str
    ) -> str:
        self._require_deployment("sui_catalog_id", "sui_faction_admin_id")
        digest, _ = self._client_call(
            "faction_nft",
            "register_faction",
            [
                self.s.sui_faction_admin_id,
                self.s.sui_catalog_id,
                str(faction_id),
                name,
                rarity,
                image,
            ],
        )
        return digest

    # -------------------------------------------------------------- internals

    def _require_deployment(self, *fields: str) -> None:
        missing = [
            field.upper()
            for field in ("sui_package_id", *fields)
            if not getattr(self.s, field)
        ]
        if missing:
            raise SuiAdapterError(
                "Thiếu cấu hình deploy: " + ", ".join(missing)
                + ". Chạy scripts/deploy-sui.sh trước."
            )

    def _client_call(
        self, module: str, function: str, args: list[str]
    ) -> tuple[str, list[dict]]:
        cmd = [
            os.path.normpath(self.s.sui_cli_path),
            "client",
            "call",
            "--package",
            self.s.sui_package_id,
            "--module",
            module,
            "--function",
            function,
            "--gas-budget",
            str(self.s.sui_gas_budget),
            "--args",
            *args,
            "--json",
        ]
        if self.s.sui_cli_config:
            cmd += ["--client-config", self.s.sui_cli_config]
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180,
                stdin=subprocess.DEVNULL,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise SuiAdapterError(f"sui CLI lỗi: {exc}") from exc
        if proc.returncode != 0:
            raise SuiAdapterError(
                f"sui client call {module}::{function} thất bại: {proc.stderr.strip()[-2000:]}"
            )
        try:
            out = json.loads(proc.stdout[proc.stdout.find("{") :])
        except json.JSONDecodeError as exc:
            raise SuiAdapterError(f"sui CLI trả về không phải JSON: {proc.stdout[:500]}") from exc
        digest = out.get("digest")
        effects = out.get("effects")
        if not digest and isinstance(effects, dict):
            digest = effects.get("transactionDigest")
        if not digest:
            raise SuiAdapterError(f"Không tìm thấy digest trong output: {proc.stdout[:500]}")
        created = []
        for change in out.get("objectChanges", []):
            if change.get("type") == "created":
                created.append(
                    {
                        "objectId": change.get("objectId"),
                        "objectType": change.get("objectType", ""),
                        "owner": change.get("owner", {}),
                    }
                )
        created.extend(
            {
                "objectId": c.get("objectId"),
                "objectType": c.get("objectType", ""),
                "owner": c.get("owner", {}),
            }
            for c in out.get("created", [])
        )
        return digest, created

    @staticmethod
    def _find_created(created: list[dict], type_suffix: str, owner: str) -> str:
        for obj in created:
            if type_suffix in obj.get("objectType", ""):
                return obj["objectId"]
        raise SuiAdapterError(
            f"Không tìm thấy object {type_suffix} cho {owner} trong created objects"
        )

    # GraphQL ---------------------------------------------------------------

    def _graphql(self, query: str, variables: dict) -> dict | None:
        if not self.s.sui_graphql_url:
            return None
        try:
            resp = self.http.post(
                self.s.sui_graphql_url,
                json={"query": query, "variables": variables},
            )
        except httpx.HTTPError:
            return None
        if resp.status_code != 200:
            return None
        body = resp.json()
        if body.get("errors") or "data" not in body:
            return None
        return body["data"]

    def _tx_via_graphql(self, digest: str) -> TransactionInfo | None:
        data = self._graphql(
            """
            query ($digest: String!) {
              transactionBlock(digest: $digest) {
                digest
                status
                sender { address }
                timestamp
                events { nodes { contents } }
              }
            }
            """,
            {"digest": digest},
        )
        if not data or not data.get("transactionBlock"):
            return None
        tx = data["transactionBlock"]
        return TransactionInfo(
            digest=tx["digest"],
            status=str(tx.get("status", "")).lower(),
            sender=(tx.get("sender") or {}).get("address"),
            timestamp_ms=_parse_ms(tx.get("timestamp")),
            events=[n.get("contents", {}) for n in (tx.get("events") or {}).get("nodes", [])],
            raw=tx,
        )

    def _object_owner_via_graphql(self, object_id: str) -> str | None:
        data = self._graphql(
            """
            query ($id: String!) {
              object(address: $id) {
                address
                owner {
                  __typename
                  ... on AddressOwner { owner { address } }
                }
              }
            }
            """,
            {"id": object_id},
        )
        if not data or not data.get("object"):
            return None
        owner = data["object"].get("owner") or {}
        if owner.get("__typename") != "AddressOwner":
            return None
        return ((owner.get("owner") or {}).get("address"))

    def _owned_nfts_via_graphql(self, wallet: str) -> list[NftInfo] | None:
        if not self.s.sui_package_id:
            return None
        type_tag = f"{self.s.sui_package_id}::{FACTION_NFT_TYPE}"
        data = self._graphql(
            """
            query ($wallet: String!, $type: String!) {
              address(address: $wallet) {
                objects(filter: {type: $type}, first: 50) {
                  nodes {
                    address
                    contents
                    owner {
                      __typename
                      ... on AddressOwner { owner { address } }
                    }
                  }
                }
              }
            }
            """,
            {"wallet": wallet, "type": type_tag},
        )
        if not data or not data.get("address"):
            return None
        nfts = []
        for node in data["address"]["objects"]["nodes"]:
            fields = (node.get("contents") or {}).get("json") or node.get("contents") or {}
            owner = (((node.get("owner") or {}).get("owner") or {}).get("address")) or wallet
            nfts.append(_nft_from_fields(node["address"], owner, fields))
        return nfts

    # JSON-RPC fallback (local node / RPC provider còn hỗ trợ) ---------------

    def _rpc(self, method: str, params: list) -> Any:
        if not self.s.sui_rpc_url:
            return None
        try:
            resp = self.http.post(
                self.s.sui_rpc_url,
                json={"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
            )
            body = resp.json()
        except (httpx.HTTPError, json.JSONDecodeError):
            return None
        if "error" in body:
            return None
        return body.get("result")

    def _tx_via_rpc(self, digest: str) -> TransactionInfo | None:
        result = self._rpc(
            "sui_getTransactionBlock",
            [digest, {"showEffects": True, "showEvents": True, "showInput": True}],
        )
        if not result:
            return None
        effects = result.get("effects") or {}
        status_field = effects.get("status") or {}
        status = status_field.get("status") or status_field.get("type") or "unknown"
        events = [
            (e.get("parsedJson") or e.get("contents") or {})
            for e in result.get("events") or []
        ]
        return TransactionInfo(
            digest=result.get("digest", digest),
            status=str(status).lower(),
            sender=(result.get("transaction") or {}).get("data", {}).get("sender"),
            timestamp_ms=_parse_ms(result.get("timestampMs")),
            events=events,
            raw=result,
        )

    def _object_owner_via_rpc(self, object_id: str) -> str | None:
        result = self._rpc(
            "sui_getObject", [object_id, {"showOwner": True, "showContent": True}]
        )
        if not result:
            return None
        owner = (result.get("data") or result).get("owner")
        if isinstance(owner, dict) and "AddressOwner" in owner:
            return owner["AddressOwner"]
        return None

    def _owned_nfts_via_rpc(self, wallet: str) -> list[NftInfo] | None:
        result = self._rpc(
            "suix_getOwnedObjects",
            [
                wallet,
                {
                    "options": {"showContent": True, "showOwner": True, "showType": True},
                },
                None,
            ],
        )
        if result is None:
            return None
        # So khớp type chính xác: `0x2::display::Display<...::faction_nft::FactionNft>`
        # cũng chứa chuỗi "faction_nft::FactionNft" nhưng không phải NFT.
        expected_type = f"{self.s.sui_package_id}::{FACTION_NFT_TYPE}"
        nfts = []
        for item in result.get("data", []):
            data = item.get("data") or {}
            object_id = item.get("objectId") or data.get("objectId")
            if not object_id or data.get("type") != expected_type:
                continue
            content = (data.get("content") or {}).get("fields") or {}
            owner = data.get("owner")
            owner_addr = owner.get("AddressOwner", wallet) if isinstance(owner, dict) else wallet
            nfts.append(_nft_from_fields(object_id, owner_addr, content))
        return nfts


def _nft_from_fields(object_id: str, owner: str, fields: dict) -> NftInfo:
    return NftInfo(
        object_id=object_id,
        owner=owner,
        faction_id=int(fields.get("faction_id", 0)),
        faction_name=str(fields.get("faction_name", "")),
        rarity=str(fields.get("rarity", "")),
        image=str(fields.get("image", "")),
    )


def _parse_ms(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        pass
    try:
        from datetime import datetime

        return int(datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp() * 1000)
    except (ValueError, TypeError):
        return None
