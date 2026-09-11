"""E2E blockchain checks trên một mạng đã deploy: mint -> verify -> reward -> get_transaction.

Chạy bằng python của backend venv:
  backend/.venv/Scripts/python scripts/e2e_checks.py --deployment deployments/sui-local.json \
      --rpc http://127.0.0.1:9000 --cli scripts/sui-docker.cmd
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.blockchain.sui_adapter import SuiAdapter  # noqa: E402
from app.core.config import Settings  # noqa: E402

# Console Windows mặc định cp1252 -> crash khi in tiếng Việt.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--deployment", required=True)
    parser.add_argument("--rpc", default="http://127.0.0.1:9000")
    parser.add_argument("--graphql", default="")
    parser.add_argument("--cli", default="sui")
    parser.add_argument("--wallet", default="", help="Bỏ trống thì dùng active-address của SUI CLI")
    parser.add_argument("--faction", type=int, default=1, help="faction_id sẽ mint cho player")
    parser.add_argument("--reward-amount", type=int, default=1_000, help="MIST trả cho player")
    parser.add_argument("--battle-id", type=int, default=999, help="battle_id ghi trong event")
    args = parser.parse_args()

    deployment = json.load(open(args.deployment, encoding="utf-8"))
    settings = Settings(
        sui_network=deployment.get("network", "local"),
        sui_rpc_url=args.rpc,
        sui_graphql_url=args.graphql,
        sui_package_id=deployment["package_id"],
        sui_catalog_id=deployment["catalog_id"],
        sui_treasury_id=deployment["treasury_id"],
        sui_faction_admin_id=deployment["faction_admin_id"],
        sui_reward_admin_id=deployment["reward_admin_id"],
        sui_cli_path=args.cli,
    )
    adapter = SuiAdapter(settings)

    cli_executable = os.path.normpath(args.cli)
    cli = ["bash", args.cli] if args.cli.endswith(".sh") else [cli_executable]
    try:
        admin = subprocess.run(
            [*cli, "client", "active-address"],
            capture_output=True,
            text=True,
            check=True,
            stdin=subprocess.DEVNULL,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        admin = deployment["deployer"]
    player = args.wallet or admin
    print(f"admin  (giữ cap, trả gas): {admin}")
    print(f"player (nhận NFT + reward): {player}")

    results: list[tuple[str, bool, str]] = []

    def check(name: str, fn) -> None:
        try:
            fn()
            results.append((name, True, ""))
            print(f"[PASS] {name}")
        except Exception as exc:  # noqa: BLE001
            results.append((name, False, str(exc)))
            print(f"[FAIL] {name}: {exc}")

    def check_deploy_tx() -> None:
        tx = adapter.get_transaction(deployment["tx_digest"])
        assert tx is not None, "không đọc được TX publish"
        assert tx.succeeded, f"TX publish không success: {tx.status}"

    nft_state: dict[str, object] = {"id": "", "faction_id": args.faction}

    def check_mint() -> None:
        owned = adapter.get_faction_nfts(player)
        if owned:
            nft_state["id"] = owned[0].object_id
            nft_state["faction_id"] = owned[0].faction_id
            print(f"   player đã có NFT {owned[0].object_id}, bỏ qua mint")
            return
        digest, object_id = adapter.mint_faction(player, int(args.faction))
        print(f"   mint digest = {digest}")
        tx = adapter.get_transaction(digest)
        assert tx is not None and tx.succeeded, f"TX mint không success: {tx and tx.status}"
        nft_state["id"] = object_id
        print(f"   nft object id = {object_id}")

    def check_verify_ownership() -> None:
        assert adapter.verify_ownership(player, str(nft_state["id"])), "owner đúng phải True"
        stranger = "0x" + "1" * 64
        assert not adapter.verify_ownership(stranger, str(nft_state["id"])), "owner sai phải False"

    def check_nft_fields() -> None:
        nfts = adapter.get_faction_nfts(player)
        assert nfts, "không đọc được NFT của wallet"
        nft = next(n for n in nfts if n.object_id == nft_state["id"])
        assert nft.faction_id == nft_state["faction_id"], f"faction_id sai: {nft.faction_id}"
        assert nft.faction_name, "faction_name rỗng"
        assert nft.rarity, "rarity rỗng"
        assert nft.owner.lower() == player.lower(), f"owner sai: {nft.owner}"
        print(f"   {nft.faction_name} / {nft.rarity}")

    def check_reward() -> None:
        digest = adapter.send_reward(player, args.reward_amount, args.battle_id)
        print(f"   reward digest = {digest}")
        tx = adapter.get_transaction(digest)
        assert tx is not None and tx.succeeded, f"TX reward không success: {tx and tx.status}"
        blob = json.dumps(tx.events)
        assert str(args.battle_id) in blob, f"thiếu event RewardSent: {blob[:200]}"

    check("get_transaction(publish TX)", check_deploy_tx)
    check("mint_faction -> NFT object ID", check_mint)
    check("verify_ownership đúng/sai chủ", check_verify_ownership)
    check("get_faction_nfts đọc metadata", check_nft_fields)
    check("send_reward -> TX digest success", check_reward)

    failed = [name for name, ok, _ in results if not ok]
    print(f"\n== e2e: {len(results) - len(failed)}/{len(results)} PASS ==")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
