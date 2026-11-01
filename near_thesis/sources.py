"""Data acquisition layer.

Every external call goes through `fetch()`, which
  * tries the primary URL, then each fallback, with retries/backoff,
  * saves the raw JSON response to data/raw/<name>.json (the snapshot judges can re-run on),
  * records success / failure per attempt in a source log (data/sources_log.json).

No API keys, no wallet. All endpoints are free and public.
In --offline mode nothing is fetched; raw snapshots in data/raw/ are used instead.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

UA = {"User-Agent": "near-thesis/0.1 (+https://github.com/; reproducible research pipeline)"}

RPC_ENDPOINTS = [
    "https://rpc.mainnet.near.org",
    "https://free.rpc.fastnear.com",
    "https://rpc.mainnet.fastnear.com",
]


def _rpc(method, params):
    return {"jsonrpc": "2.0", "id": "near-thesis", "method": method, "params": params}


# name -> list of attempts (first that works wins). Each attempt: (label, method, url, body)
SOURCES: dict[str, list[tuple]] = {
    # ---- NEAR protocol, read straight from chain via JSON-RPC ----
    "rpc_block": [(f"NEAR RPC {u}", "POST", u, _rpc("block", {"finality": "final"})) for u in RPC_ENDPOINTS],
    "rpc_validators": [(f"NEAR RPC {u}", "POST", u, _rpc("validators", [None])) for u in RPC_ENDPOINTS],
    "rpc_protocol_config": [
        (f"NEAR RPC {u}", "POST", u, _rpc("EXPERIMENTAL_protocol_config", {"finality": "final"})) for u in RPC_ENDPOINTS
    ],
    # ---- NearBlocks public API (indexer over mainnet), no key needed for these endpoints ----
    "nearblocks_charts": [("NearBlocks daily charts", "GET", "https://api.nearblocks.io/v1/charts", None)],
    "nearblocks_stats": [("NearBlocks stats", "GET", "https://api.nearblocks.io/v1/stats", None)],
    # ---- DefiLlama (free, keyless) ----
    "llama_chain_tvl": [("DefiLlama chain TVL", "GET", "https://api.llama.fi/v2/historicalChainTvl/Near", None)],
    "llama_chain_fees": [
        ("DefiLlama NEAR chain fees", "GET", "https://api.llama.fi/summary/fees/near?dataType=dailyFees", None)
    ],
    "llama_chain_revenue": [
        ("DefiLlama NEAR chain revenue (burn)", "GET", "https://api.llama.fi/summary/fees/near?dataType=dailyRevenue", None)
    ],
    "llama_stablecoins": [
        ("DefiLlama stablecoins on NEAR", "GET", "https://stablecoins.llama.fi/stablecoincharts/Near", None)
    ],
    "llama_stablecoin_chains": [
        ("DefiLlama stablecoins by chain", "GET", "https://stablecoins.llama.fi/stablecoinchains", None)
    ],
    "llama_chain_dex": [("DefiLlama DEX volume on NEAR", "GET", "https://api.llama.fi/overview/dexs/near", None)],
    "llama_intents_volume": [
        ("DefiLlama NEAR Intents volume", "GET", "https://api.llama.fi/summary/dexs/near-intents", None)
    ],
    "llama_intents_fees": [
        ("DefiLlama NEAR Intents fees", "GET", "https://api.llama.fi/summary/fees/near-intents?dataType=dailyFees", None)
    ],
    # ---- Price history: CoinGecko free tier first, DefiLlama coins API as fallback ----
    "price_history": [
        ("CoinGecko market_chart 365d", "GET",
         "https://api.coingecko.com/api/v3/coins/near/market_chart?vs_currency=usd&days=365&interval=daily", None),
        ("DefiLlama coins chart (fallback)", "GET",
         "https://coins.llama.fi/chart/coingecko:near?start={start365}&span=400&period=1d", None),
    ],
    # NEAR Intents Explorer API requires a partner JWT -> recorded as unavailable, not used.
    "intents_explorer": [
        ("NEAR Intents Explorer API (needs JWT)", "GET", "https://explorer.near-intents.org/api/v0/transactions", None)
    ],
}

OPTIONAL = {"intents_explorer", "price_history", "llama_stablecoin_chains", "llama_intents_fees"}


def _render(url: str) -> str:
    start365 = int(time.time()) - 400 * 86400
    return url.replace("{start365}", str(start365))


def _ok_payload(name: str, data) -> bool:
    if data is None:
        return False
    if isinstance(data, dict) and "error" in data and "result" not in data:
        return False
    if name.startswith("rpc_"):
        return isinstance(data, dict) and "result" in data
    if name == "price_history":
        if isinstance(data, dict) and "prices" in data:
            return len(data["prices"]) > 30
        if isinstance(data, dict) and "coins" in data:
            return len(data["coins"].get("coingecko:near", {}).get("prices", [])) > 30
        return False
    return True


def fetch_all(raw_dir: Path, offline: bool = False, retries: int = 3) -> tuple[dict, list]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    out, log = {}, []
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for name, attempts in SOURCES.items():
        path = raw_dir / f"{name}.json"
        if offline:
            if path.exists():
                snap = json.loads(path.read_text())
                out[name] = snap["data"]
                log.append({"source": name, "label": snap.get("label"), "url": snap.get("url"),
                            "status": "ok (snapshot)", "fetched_at": snap.get("fetched_at")})
            else:
                log.append({"source": name, "status": "missing snapshot", "url": None, "fetched_at": None})
            continue
        got = False
        for label, method, url, body in attempts:
            url = _render(url)
            err = None
            for i in range(retries):
                try:
                    if method == "POST":
                        r = requests.post(url, json=body, headers=UA, timeout=45)
                    else:
                        r = requests.get(url, headers=UA, timeout=45)
                    if r.status_code == 429:
                        err = "HTTP 429 rate limited"
                        time.sleep(4 * (i + 1))
                        continue
                    if r.status_code != 200:
                        err = f"HTTP {r.status_code}: {r.text[:160]}"
                        break
                    data = r.json()
                    if not _ok_payload(name, data):
                        err = f"unexpected payload: {str(data)[:160]}"
                        break
                    path.write_text(json.dumps({"label": label, "url": url, "fetched_at": now, "data": data}))
                    out[name] = data
                    log.append({"source": name, "label": label, "url": url, "status": "ok", "fetched_at": now})
                    got = True
                    break
                except Exception as e:  # network / JSON errors
                    err = f"{type(e).__name__}: {e}"[:200]
                    time.sleep(2 * (i + 1))
            if got:
                break
            log.append({"source": name, "label": label, "url": url, "status": f"failed: {err}", "fetched_at": now})
        if not got and path.exists():
            # fall back to the last good snapshot, and say so
            snap = json.loads(path.read_text())
            out[name] = snap["data"]
            log.append({"source": name, "label": snap.get("label"), "url": snap.get("url"),
                        "status": "stale snapshot used", "fetched_at": snap.get("fetched_at")})
    return out, log
