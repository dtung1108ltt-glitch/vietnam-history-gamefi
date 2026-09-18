import json
import subprocess

import httpx
import pytest

from app.blockchain.sui_adapter import SuiAdapter, SuiAdapterError
from app.core.config import Settings


def settings(**overrides) -> Settings:
    base = dict(
        sui_package_id="0xpkg",
        sui_catalog_id="0xcatalog",
        sui_treasury_id="0xtreasury",
        sui_faction_admin_id="0xfadmin",
        sui_reward_admin_id="0xradmin",
        sui_graphql_url="https://gql.test/graphql",
        sui_rpc_url="http://rpc.test",
    )
    base.update(overrides)
    return Settings(**base)


def mock_client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


def test_get_transaction_via_graphql():
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert "transactionBlock" in body["query"]
        return httpx.Response(
            200,
            json={
                "data": {
                    "transactionBlock": {
                        "digest": "0xd1",
                        "status": "SUCCESS",
                        "sender": {"address": "0xsender"},
                        "timestamp": None,
                        "events": {"nodes": [{"contents": {"amount": "5"}}]},
                    }
                }
            },
        )

    adapter = SuiAdapter(settings(), http=mock_client(handler))
    tx = adapter.get_transaction("0xd1")
    assert tx is not None and tx.succeeded
    assert tx.sender == "0xsender"
    assert tx.events == [{"amount": "5"}]


def test_get_transaction_falls_back_to_rpc():
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        calls.append(body.get("method"))
        if request.url.host == "gql.test":
            return httpx.Response(200, json={"data": {"transactionBlock": None}})
        return httpx.Response(
            200,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "digest": "0xd2",
                    "effects": {"status": {"status": "success"}},
                    "transaction": {"data": {"sender": "0xrpc"}},
                    "timestampMs": "1700000000000",
                    "events": [{"parsedJson": {"battle_id": 7}}],
                },
            },
        )

    adapter = SuiAdapter(settings(), http=mock_client(handler))
    tx = adapter.get_transaction("0xd2")
    assert tx is not None and tx.succeeded
    assert tx.sender == "0xrpc"
    assert tx.timestamp_ms == 1700000000000
    assert calls == [None, "sui_getTransactionBlock"]


def test_verify_ownership_via_graphql():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "data": {
                    "object": {
                        "address": "0xnft",
                        "owner": {
                            "__typename": "AddressOwner",
                            "owner": {"address": "0xowner"},
                        },
                    }
                }
            },
        )

    adapter = SuiAdapter(settings(), http=mock_client(handler))
    assert adapter.verify_ownership("0xowner", "0xnft")
    assert not adapter.verify_ownership("0xsomeone", "0xnft")


def test_get_faction_nfts_parses_contents():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "data": {
                    "address": {
                        "objects": {
                            "nodes": [
                                {
                                    "address": "0xnft1",
                                    "contents": {
                                        "json": {
                                            "faction_id": 3,
                                            "faction_name": "Nhà Lê",
                                            "rarity": "rare",
                                            "image": "le.png",
                                        }
                                    },
                                    "owner": {
                                        "__typename": "AddressOwner",
                                        "owner": {"address": "0xowner"},
                                    },
                                }
                            ]
                        }
                    }
                }
            },
        )

    adapter = SuiAdapter(settings(), http=mock_client(handler))
    nfts = adapter.get_faction_nfts("0xowner")
    assert len(nfts) == 1
    assert nfts[0].faction_id == 3
    assert nfts[0].faction_name == "Nhà Lê"


def test_get_faction_nfts_falls_back_to_rpc():
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        seen.append(body.get("method"))
        if request.url.host == "gql.test":
            return httpx.Response(200, json={"data": {"address": None}})
        return httpx.Response(
            200,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "result": {
                    "data": [
                        {
                            "objectId": "0xcoin",
                            "data": {"type": "0x2::coin::Coin<0x2::sui::SUI>"},
                        },
                        {
                            "objectId": "0xdisplay",
                            "data": {
                                "type": "0x2::display::Display<0xpkg::faction_nft::FactionNft>",
                                "owner": {"AddressOwner": "0xowner"},
                            },
                        },
                        {
                            "objectId": "0xnft1",
                            "data": {
                                "type": "0xpkg::faction_nft::FactionNft",
                                "owner": {"AddressOwner": "0xowner"},
                                "content": {
                                    "fields": {
                                        "faction_id": 4,
                                        "faction_name": "Tây Sơn",
                                        "rarity": "epic",
                                        "image": "tayson.png",
                                    }
                                },
                            },
                        },
                    ],
                    "nextCursor": None,
                    "hasNextPage": False,
                },
            },
        )

    adapter = SuiAdapter(settings(), http=mock_client(handler))
    nfts = adapter.get_faction_nfts("0xowner")
    assert "suix_getOwnedObjects" in seen
    assert len(nfts) == 1
    assert nfts[0].object_id == "0xnft1"
    assert nfts[0].owner == "0xowner"
    assert nfts[0].faction_id == 4
    assert nfts[0].faction_name == "Tây Sơn"
    assert nfts[0].rarity == "epic"


def test_client_call_parses_digest_and_created(monkeypatch):
    sample = {
        "digest": "0xtxdigest",
        "objectChanges": [
            {
                "type": "created",
                "objectId": "0xnftnew",
                "objectType": "0xpkg::faction_nft::FactionNft",
                "owner": {"AddressOwner": "0xplayer"},
            }
        ],
    }

    def fake_run(cmd, **kwargs):
        fake_run.cmd = cmd
        return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps(sample), stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    adapter = SuiAdapter(settings(), http=mock_client(lambda r: httpx.Response(200, json={})))
    digest, nft_id = adapter.mint_faction("0xplayer", 2)
    assert digest == "0xtxdigest"
    assert nft_id == "0xnftnew"
    assert "--args" in fake_run.cmd
    assert fake_run.cmd[fake_run.cmd.index("--function") + 1] == "mint_faction_for"
    args = fake_run.cmd[fake_run.cmd.index("--args") + 1 :]
    assert args[:4] == ["0xfadmin", "0xcatalog", "2", "0xplayer"]
    assert fake_run.cmd[-1] == "--json"


def test_client_call_raises_on_cli_failure(monkeypatch):
    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 1, stdout="", stderr="boom")

    monkeypatch.setattr(subprocess, "run", fake_run)
    adapter = SuiAdapter(settings(), http=mock_client(lambda r: httpx.Response(200, json={})))
    with pytest.raises(SuiAdapterError):
        adapter.send_reward("0xplayer", 10, 1)


def test_missing_deployment_config_raises():
    adapter = SuiAdapter(
        settings(sui_package_id="", sui_catalog_id=""),
        http=mock_client(lambda r: httpx.Response(200, json={})),
    )
    with pytest.raises(SuiAdapterError):
        adapter.mint_faction("0xplayer", 1)
