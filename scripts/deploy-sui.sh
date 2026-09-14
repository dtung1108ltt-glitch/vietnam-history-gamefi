#!/usr/bin/env bash
# Deploy package Move lên SUI (testnet mặc định, hoặc local).
# Usage: scripts/deploy-sui.sh [testnet|local]
# Env:   SUI_BIN (mặc định: sui; có thể trỏ tới scripts/sui-docker.sh)
set -euo pipefail

# Python trên Windows mặc định dùng cp1252 -> lỗi khi in tên faction tiếng Việt.
export PYTHONIOENCODING=utf-8

ENV_NAME="${1:-testnet}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SUI_BIN="${SUI_BIN:-sui}"
case "$SUI_BIN" in
  /*) ;;
  *)
    if [ -e "$ROOT/$SUI_BIN" ]; then
      SUI_BIN="$ROOT/$SUI_BIN"
    fi
    ;;
esac
PKG_DIR="$ROOT/blockchain/sui"
OUT_DIR="$ROOT/deployments"
mkdir -p "$OUT_DIR"
WORK="$OUT_DIR/.work"
mkdir -p "$WORK"

if [ "$ENV_NAME" = "local" ]; then
  RPC_URL="http://127.0.0.1:9000"
else
  # fullnode.testnet.sui.io đã ngừng phục vụ JSON-RPC công khai.
  RPC_URL="${SUI_TESTNET_RPC:-https://testnet.suiet.app}"
fi

echo "== [deploy] env=$ENV_NAME rpc=$RPC_URL =="
if ! $SUI_BIN client envs --json | grep -q "\"$ENV_NAME\""; then
  $SUI_BIN client new-env --alias "$ENV_NAME" --rpc "$RPC_URL" >/dev/null
fi
$SUI_BIN client switch --env "$ENV_NAME" >/dev/null

# `client new-env` từ chối ghi đè alias có sẵn nhưng vẫn exit 0, nên alias cũ
# có thể đang trỏ tới RPC đã chết -> báo lỗi rõ thay vì publish thất bại khó hiểu.
ACTIVE_RPC="$($SUI_BIN client envs --json | python -c "
import json, sys
payload = json.load(sys.stdin)
envs = payload[0] if payload and isinstance(payload[0], list) else payload
alias = sys.argv[1]
print(next((e.get('rpc') for e in envs if e.get('alias') == alias), ''))
" "$ENV_NAME")"
if [ -n "$ACTIVE_RPC" ] && [ "$ACTIVE_RPC" != "$RPC_URL" ]; then
  echo "== [deploy] ERROR: alias '$ENV_NAME' đang trỏ $ACTIVE_RPC, cần $RPC_URL"
  echo "    Sửa ~/.sui/sui_config/client.yaml (trong container nếu chạy qua Docker):"
  echo "      rpc: \"$RPC_URL\""
  exit 1
fi

ADDR="$($SUI_BIN client active-address 2>/dev/null || true)"
if [ -z "$ADDR" ]; then
  $SUI_BIN client new-address ed25519 deployer --json > "$WORK/newaddr.json"
  ADDR="$(python - "$WORK/newaddr.json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
if isinstance(data, list):
    data = data[0]
print(data.get("address") or data.get("newAddress"))
PY
)"
  $SUI_BIN client switch --address "$ADDR" >/dev/null
fi
echo "== [deploy] deployer=$ADDR =="

FAUCET_URL="${SUI_FAUCET:-https://faucet.testnet.sui.io/gas}"

# Faucet testnet giới hạn ~1 yêu cầu/phút/IP nên phải thử lại có chờ, không bỏ qua ngay.
request_faucet() {
  local recipient="$1" attempts="${2:-3}" i
  if [ "$ENV_NAME" = "local" ]; then
    $SUI_BIN client faucet --address "$recipient" >/dev/null 2>&1 < /dev/null || true
    return 0
  fi
  for ((i = 1; i <= attempts; i++)); do
    if curl -sf -m 30 -X POST "$FAUCET_URL" -H 'Content-Type: application/json' \
        -d "{\"FixedAmountRequest\":{\"recipient\":\"$recipient\"}}" >/dev/null; then
      echo "   faucet OK (lần $i)"
      return 0
    fi
    if [ "$i" -lt "$attempts" ]; then
      echo "   faucet giới hạn, chờ 45s (lần $i/$attempts)"
      sleep 45
    fi
  done
  echo "== [deploy] WARN: faucet $FAUCET_URL không trả coin cho $recipient"
  return 1
}

request_faucet "$ADDR" 3 || true

echo "== [deploy] publish package =="
cd "$PKG_DIR"
if [ "$ENV_NAME" = "local" ]; then
  # Mạng local không phải build-env hợp lệ của Move -> dùng test-publish (ephemeral).
  # Xoá file publication cũ để deploy lại được (nếu không sẽ báo "already published").
  rm -f "$PKG_DIR/Pub.$ENV_NAME.toml"
  $SUI_BIN client test-publish --build-env testnet --gas-budget 200000000 --json > "$WORK/publish.json"
else
  $SUI_BIN client publish --gas-budget 200000000 --json > "$WORK/publish.json"
fi

python - "$WORK/publish.json" "$OUT_DIR/sui-$ENV_NAME.json" "$ADDR" "$ENV_NAME" <<'PY'
import json, sys
publish_path, out_path, deployer, env = sys.argv[1:5]
raw = open(publish_path, encoding="utf-8", errors="replace").read()
start = raw.find("{")
assert start >= 0, f"không có JSON trong publish output:\n{raw[:400]}"
data = json.loads(raw[start:])

def is_shared(owner):
    if isinstance(owner, dict):
        return "Shared" in owner
    return owner == "Shared"

package_id = None
objects = {}
for change in data.get("objectChanges", []):
    ctype = change.get("type")
    otype = change.get("objectType", "")
    if ctype == "published":
        package_id = change.get("packageId")
    elif ctype == "created":
        owner = change.get("owner")
        key = None
        if "faction_nft::FactionAdmin" in otype:
            key = "faction_admin_id"
        elif "reward::RewardAdmin" in otype:
            key = "reward_admin_id"
        elif "faction_nft::FactionCatalog" in otype and is_shared(owner):
            key = "catalog_id"
        if key:
            objects[key] = change.get("objectId")
assert package_id, "không tìm thấy packageId trong publish output"
for key in ("faction_admin_id", "reward_admin_id", "catalog_id"):
    assert objects.get(key), f"thiếu {key} trong publish output"
out = {
    "network": env,
    "deployer": deployer,
    "package_id": package_id,
    "tx_digest": data.get("digest"),
    **objects,
}
json.dump(out, open(out_path, "w", encoding="utf-8"), indent=2)
print("== [deploy] package_id =", package_id)
print("== [deploy] catalog   =", objects["catalog_id"])
PY

DEPLOY_JSON="$OUT_DIR/sui-$ENV_NAME.json"
PACKAGE_ID="$(python -c "import json,sys; print(json.load(open(sys.argv[1]))['package_id'])" "$DEPLOY_JSON")"
CATALOG_ID="$(python -c "import json,sys; print(json.load(open(sys.argv[1]))['catalog_id'])" "$DEPLOY_JSON")"
FACTION_ADMIN="$(python -c "import json,sys; print(json.load(open(sys.argv[1]))['faction_admin_id'])" "$DEPLOY_JSON")"
REWARD_ADMIN="$(python -c "import json,sys; print(json.load(open(sys.argv[1]))['reward_admin_id'])" "$DEPLOY_JSON")"

echo "== [deploy] register factions từ assets/nft/factions.json =="
python - "$ROOT/assets/nft/factions.json" "$WORK/factions.tsv" <<'PY'
import json, sys
src, dst = sys.argv[1], sys.argv[2]
data = json.load(open(src, encoding="utf-8"))
with open(dst, "w", encoding="utf-8", newline="\n") as out:
    for f in data["factions"]:
        out.write("\t".join([str(f["faction_id"]), f["name"], f["rarity"], f["image"]]) + "\n")
PY
# Đọc TSV qua FD 3 và chặn stdin của CLI: nếu không `docker exec -i` sẽ nuốt stdin của vòng lặp.
while IFS=$'\t' read -r -u 3 FID FNAME FRARITY FIMAGE; do
  echo "   register faction $FID $FNAME"
  $SUI_BIN client call --package "$PACKAGE_ID" --module faction_nft --function register_faction \
    --args "$FACTION_ADMIN" "$CATALOG_ID" "$FID" "$FNAME" "$FRARITY" "$FIMAGE" \
    --gas-budget 50000000 >/dev/null < /dev/null
done 3< "$WORK/factions.tsv"

echo "== [deploy] create + fund reward treasury =="
$SUI_BIN client call --package "$PACKAGE_ID" --module reward --function create_treasury \
  --args "$REWARD_ADMIN" --gas-budget 50000000 --json > "$WORK/treasury.json"
TREASURY_ID="$(python - "$WORK/treasury.json" <<'PY'
import json, sys
raw = open(sys.argv[1], encoding="utf-8", errors="replace").read()
data = json.loads(raw[raw.find("{"):])
for change in data.get("objectChanges", []):
    owner = change.get("owner")
    shared = owner.get("Shared") if isinstance(owner, dict) else owner == "Shared"
    if change.get("type") == "created" and shared:
        print(change.get("objectId"))
        break
PY
)"
echo "   treasury=$TREASURY_ID"

# Cần 2 SUI coin khác nhau: 1 trả gas (chỉ định bằng --gas), 1 nạp vào treasury.
# `split-coin` không dùng được vì coin duy nhất không thể vừa trả gas vừa bị split.
for _ in 1 2 3; do
  $SUI_BIN client gas --json > "$WORK/gas.json" < /dev/null
  COIN_PAIR="$(python - "$WORK/gas.json" <<'PY'
import json, sys
raw = open(sys.argv[1], encoding="utf-8", errors="replace").read()
data = json.loads(raw[raw.find("{"):]) if "{" in raw else {}
coins = data.get("gasCoins") or data.get("data") or []

def coin_id(c):
    return c.get("gasCoinId") or c.get("coinId") or c.get("objectId")

coins.sort(key=lambda c: int(c.get("mistBalance") or 0), reverse=True)
if len(coins) >= 2:
    print(coin_id(coins[0]), coin_id(coins[1]))
PY
)"
  if [ -n "$COIN_PAIR" ]; then break; fi
  echo "   deployer mới có <2 coin, gọi faucet lần nữa..."
  request_faucet "$ADDR" 2 || true
  if [ "$ENV_NAME" = "local" ]; then sleep 3; else sleep 20; fi
done
if [ -z "$COIN_PAIR" ]; then
  echo "== [deploy] ERROR: cần ít nhất 2 SUI coin cho deployer $ADDR (faucet chưa trả coin?)"
  exit 1
fi
GAS_COIN="${COIN_PAIR%% *}"
FUND_COIN="${COIN_PAIR##* }"
echo "   gas_coin=$GAS_COIN fund_coin=$FUND_COIN"

$SUI_BIN client call --package "$PACKAGE_ID" --module reward --function fund_treasury \
  --args "$REWARD_ADMIN" "$TREASURY_ID" "$FUND_COIN" \
  --gas "$GAS_COIN" --gas-budget 50000000 --json > "$WORK/fund.json" < /dev/null
python - "$WORK/fund.json" <<'PY'
import json, sys
raw = open(sys.argv[1], encoding="utf-8", errors="replace").read()
data = json.loads(raw[raw.find("{"):]) if "{" in raw else {}
digest = data.get("digest")
assert digest, f"fund_treasury không trả digest:\n{raw[:400]}"
print("   fund_treasury digest =", digest)
PY

python - "$DEPLOY_JSON" "$TREASURY_ID" <<'PY'
import json, sys
path, treasury = sys.argv[1], sys.argv[2]
data = json.load(open(path, encoding="utf-8"))
data["treasury_id"] = treasury
json.dump(data, open(path, "w", encoding="utf-8"), indent=2)
print("== [deploy] DONE:", path)
PY
