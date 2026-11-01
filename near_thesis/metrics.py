"""Turn raw API payloads into tidy daily series + headline thesis metrics.

Every headline metric carries: value, unit, as_of (UTC date of the last data point),
source (raw snapshot name) and a one-line `how` describing the computation.
If an input is missing the metric is recorded with value None and the reason - never guessed.
"""
from __future__ import annotations

import math
import re
from datetime import datetime, timezone

import numpy as np
import pandas as pd

YOCTO = 1e24
DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def _date(s) -> pd.Timestamp:
    if isinstance(s, (int, float)) or (isinstance(s, str) and s.isdigit()):
        return pd.Timestamp(int(s), unit="s").normalize()
    m = DATE_RE.search(str(s))
    return pd.Timestamp(m.group(1)) if m else pd.NaT


def _ts_frame(pairs, col, agg="last") -> pd.DataFrame:
    """Daily frame. agg='sum' for flows reported in pieces, 'last' for levels (price, TVL, supply)."""
    df = pd.DataFrame(pairs, columns=["date", col])
    df["date"] = df["date"].apply(_date)
    df[col] = pd.to_numeric(df[col], errors="coerce")
    g = df.dropna().sort_values("date").groupby("date", as_index=True)[col]
    return (g.sum() if agg == "sum" else g.last()).to_frame().sort_index()


def _at(s: pd.Series, t: pd.Timestamp, tol_days: int = 3):
    """Value at date t: last point on/before t, else first point within t + tol_days. None if no data."""
    b = s[s.index <= t]
    if len(b) and (t - b.index[-1]).days <= tol_days:
        return b.iloc[-1]
    a = s[(s.index > t) & (s.index <= t + pd.Timedelta(days=tol_days))]
    return a.iloc[0] if len(a) else None


class Metrics:
    def __init__(self):
        self.headline: dict[str, dict] = {}
        self.missing: list[str] = []

    def put(self, key, value, unit, as_of, source, how):
        if value is not None and isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            value = None
        if value is None:
            self.missing.append(key)
        self.headline[key] = {
            "value": None if value is None else (round(float(value), 6) if isinstance(value, (float, np.floating)) else value),
            "unit": unit,
            "as_of": None if as_of is None else str(pd.Timestamp(as_of).date()) if not isinstance(as_of, str) else as_of,
            "source": source,
            "how": how,
        }


def _window_sum(s: pd.Series, end: pd.Timestamp, days: int):
    w = s[(s.index > end - pd.Timedelta(days=days)) & (s.index <= end)]
    return w.sum() if len(w) >= int(days * 0.9) else None


def _window_mean(s: pd.Series, end: pd.Timestamp, days: int):
    w = s[(s.index > end - pd.Timedelta(days=days)) & (s.index <= end)]
    return w.mean() if len(w) >= int(days * 0.9) else None


def _pct(a, b):
    if a is None or b is None or b == 0:
        return None
    return (a / b - 1) * 100


def compute(raw: dict, assumptions: dict) -> dict:
    M = Metrics()
    series: dict[str, pd.DataFrame] = {}
    burn_share = assumptions["protocol"]["fee_burn_share"]

    # ------------------------------------------------------------ NearBlocks daily activity
    nb = raw.get("nearblocks_charts")
    act = None
    if nb:
        df = pd.DataFrame(nb["charts"])
        df["date"] = df["date"].apply(_date)
        num = ["near_price", "total_supply", "txns", "txn_fee", "txn_fee_usd", "new_accounts", "active_accounts",
               "gas_used", "market_cap"]
        for c in num:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df = df.set_index("date").sort_index()
        df["fee_near"] = df["txn_fee"] / YOCTO
        df["total_supply_near"] = df["total_supply"] / YOCTO
        act = df
        end = df.index.max()
        src = "nearblocks_charts"
        yr = end - pd.Timedelta(days=365)
        for key, col, label in [("txns", "txns", "transactions/day"),
                                ("active_accounts", "active_accounts", "active accounts/day"),
                                ("new_accounts", "new_accounts", "new accounts/day")]:
            now_v = _window_mean(df[col], end, 30)
            prev = _window_mean(df[col], yr, 30)
            M.put(f"{key}_30d_avg", now_v, label, end, src, f"mean of daily `{col}` over the 30 days to as_of")
            M.put(f"{key}_30d_avg_yoy_pct", _pct(now_v, prev), "%", end, src,
                  f"30d mean of `{col}` vs the same 30d window one year earlier")
        fee30 = _window_sum(df["fee_near"], end, 30)
        fee30_prev = _window_sum(df["fee_near"], yr, 30)
        fee30_usd = _window_sum(df["txn_fee_usd"], end, 30)
        tx30 = _window_sum(df["txns"], end, 30)
        M.put("fees_near_30d", fee30, "NEAR", end, src, "sum of daily `txn_fee` (yoctoNEAR/1e24) over 30 days")
        M.put("fees_near_30d_yoy_pct", _pct(fee30, fee30_prev), "%", end, src, "30d fee sum vs same window a year earlier")
        M.put("fees_usd_30d_nearblocks", fee30_usd, "USD", end, src, "sum of daily `txn_fee_usd` over 30 days")
        M.put("fees_near_annualized", None if fee30 is None else fee30 * 365 / 30, "NEAR/yr", end, src,
              "30d fee sum x 365/30")
        M.put("burn_near_annualized", None if fee30 is None else fee30 * 365 / 30 * burn_share, "NEAR/yr", end, src,
              f"annualized fees x burn share {burn_share} (NEAR burns 70% of gas; 30% goes to contract devs)")
        M.put("fee_per_tx_near", None if not (fee30 and tx30) else fee30 / tx30, "NEAR/tx", end, src,
              "30d fee sum / 30d tx sum")
        # realized net supply change (issuance minus burn) over 365 days
        s_now = df["total_supply_near"].loc[end]
        prior = df["total_supply_near"][df.index <= yr]
        if len(prior):
            s_then = prior.iloc[-1]
            net = s_now - s_then
            M.put("supply_net_change_365d", net, "NEAR", end, src, "total_supply(as_of) - total_supply(as_of - 365d)")
            M.put("realized_net_inflation_365d_pct", net / s_then * 100, "%", end, src,
                  "net 365d supply change / supply a year ago (already net of burn)")
            fee365 = _window_sum(df["fee_near"], end, 365)
            if fee365 is not None:
                M.put("burn_near_365d", fee365 * burn_share, "NEAR", end, src, f"365d fee sum x {burn_share}")
                M.put("implied_gross_issuance_365d", net + fee365 * burn_share, "NEAR", end, src,
                      "net supply change + burn = what validators were minted")
        series["activity"] = df[["txns", "active_accounts", "new_accounts", "fee_near", "txn_fee_usd",
                                 "total_supply_near", "near_price"]]
    else:
        M.missing.append("nearblocks_charts")

    # ------------------------------------------------------------ RPC: supply, staking, protocol params
    blk = raw.get("rpc_block", {}).get("result")
    val = raw.get("rpc_validators", {}).get("result")
    cfg = raw.get("rpc_protocol_config", {}).get("result")
    supply = None
    if blk:
        h = blk["header"]
        supply = int(h["total_supply"]) / YOCTO
        t = pd.Timestamp(int(h["timestamp_nanosec"]), unit="ns")
        M.put("total_supply_rpc", supply, "NEAR", t, "rpc_block", f"block {h['height']} header.total_supply")
        M.put("block_height", int(h["height"]), "block", t, "rpc_block", "latest final block")
    infl = prr = None
    if cfg:
        n, d = cfg["max_inflation_rate"]
        infl = n / d
        a, b = cfg["protocol_reward_rate"]
        prr = a / b
        M.put("max_inflation_rate_pct", infl * 100, "%/yr", "latest", "rpc_protocol_config",
              "EXPERIMENTAL_protocol_config.max_inflation_rate")
        M.put("protocol_reward_rate_pct", prr * 100, "%", "latest", "rpc_protocol_config",
              "share of issuance sent to treasury (protocol_reward_rate)")
        M.put("protocol_version", cfg.get("protocol_version"), "", "latest", "rpc_protocol_config", "protocol_version")
    staked = None
    if val:
        staked = sum(int(v["stake"]) for v in val["current_validators"]) / YOCTO
        M.put("total_staked", staked, "NEAR", "latest", "rpc_validators", "sum of current_validators[].stake")
        M.put("validator_count", len(val["current_validators"]), "validators", "latest", "rpc_validators",
              "len(current_validators)")
        if supply:
            M.put("staking_ratio_pct", staked / supply * 100, "%", "latest", "rpc_validators+rpc_block",
                  "total_staked / total_supply")
    if supply and infl is not None:
        issuance = supply * infl
        M.put("max_gross_issuance_annual", issuance, "NEAR/yr", "latest", "rpc_protocol_config+rpc_block",
              "total_supply x max_inflation_rate (upper bound; actual scales with validator uptime)")
        if staked:
            M.put("staking_apr_gross_pct", issuance * (1 - prr) / staked * 100, "%", "latest", "rpc",
                  "issuance x (1 - protocol_reward_rate) / total_staked, before validator commission")
        b = M.headline.get("burn_near_annualized", {}).get("value")
        if b:
            M.put("burn_to_issuance_pct", b / issuance * 100, "%", M.headline["burn_near_annualized"]["as_of"],
                  "nearblocks_charts+rpc", "annualized 30d burn / max gross issuance")
        fpt = M.headline.get("fee_per_tx_near", {}).get("value")
        if fpt:
            M.put("breakeven_tx_per_day", issuance / 365 / (fpt * burn_share), "tx/day", "latest",
                  "nearblocks_charts+rpc",
                  "tx/day needed for burn = issuance at today's fee per tx")

    # ------------------------------------------------------------ DefiLlama: TVL, fees, stablecoins, DEX, Intents
    tvl = raw.get("llama_chain_tvl")
    if tvl:
        s = _ts_frame([(x["date"], x["tvl"]) for x in tvl], "tvl")["tvl"]
        end = s.index.max()
        M.put("tvl_usd", s.iloc[-1], "USD", end, "llama_chain_tvl", "latest DefiLlama chain TVL")
        M.put("tvl_yoy_pct", _pct(s.iloc[-1], _at(s, end - pd.Timedelta(days=365))), "%", end, "llama_chain_tvl",
              "TVL now vs 365d earlier")
        series["tvl"] = s.to_frame()

    for key, nm, unit_note in [("llama_chain_fees", "fees_usd", "chain gas fees"),
                               ("llama_chain_revenue", "revenue_usd", "burned share of fees")]:
        d = raw.get(key)
        if d and d.get("totalDataChart"):
            s = _ts_frame(d["totalDataChart"], nm, "sum")[nm]
            end = s.index.max()
            v30 = _window_sum(s, end, 30)
            v30p = _window_sum(s, end - pd.Timedelta(days=365), 30)
            M.put(f"llama_{nm}_30d", v30, "USD", end, key, f"DefiLlama {unit_note}, 30d sum")
            M.put(f"llama_{nm}_30d_yoy_pct", _pct(v30, v30p), "%", end, key, "30d sum vs same window a year earlier")
            M.put(f"llama_{nm}_1y", d.get("total1y"), "USD", end, key, "DefiLlama total1y field")
            series[nm] = s.to_frame()

    st = raw.get("llama_stablecoins")
    if st:
        s = _ts_frame([(x["date"], x["totalCirculatingUSD"].get("peggedUSD", 0)) for x in st], "stables")["stables"]
        end = s.index.max()
        M.put("stablecoin_supply_usd", s.iloc[-1], "USD", end, "llama_stablecoins",
              "DefiLlama totalCirculatingUSD.peggedUSD on NEAR")
        for days in (30, 365):
            M.put(f"stablecoin_supply_{days}d_change_pct", _pct(s.iloc[-1], _at(s, end - pd.Timedelta(days=days))), "%",
                  end, "llama_stablecoins", f"stablecoin supply vs {days}d earlier")
        series["stables"] = s.to_frame()
    sc = raw.get("llama_stablecoin_chains")
    if sc:
        ranked = sorted(sc, key=lambda x: -(x.get("totalCirculatingUSD", {}) or {}).get("peggedUSD", 0) or 0)
        names = [x["name"] for x in ranked]
        if "Near" in names:
            M.put("stablecoin_chain_rank", names.index("Near") + 1, "rank", "latest", "llama_stablecoin_chains",
                  f"NEAR's rank by USD-pegged stablecoin supply among {len(names)} chains")

    dex = raw.get("llama_chain_dex")
    if dex and dex.get("totalDataChart"):
        s = _ts_frame(dex["totalDataChart"], "dex_usd", "sum")["dex_usd"]
        end = s.index.max()
        M.put("dex_volume_near_30d", _window_sum(s, end, 30), "USD", end, "llama_chain_dex",
              "DefiLlama DEX volume attributed to NEAR chain, 30d sum (includes NEAR Intents)")
        series["dex"] = s.to_frame()

    iv = raw.get("llama_intents_volume")
    if iv and iv.get("totalDataChart"):
        s = _ts_frame(iv["totalDataChart"], "intents_usd", "sum")["intents_usd"]
        end = s.index.max()
        v30 = _window_sum(s, end, 30)
        v30p = _window_sum(s, end - pd.Timedelta(days=30), 30)
        v30y = _window_sum(s, end - pd.Timedelta(days=365), 30)
        M.put("intents_volume_30d", v30, "USD", end, "llama_intents_volume", "DefiLlama NEAR Intents volume, 30d sum")
        M.put("intents_volume_30d_mom_pct", _pct(v30, v30p), "%", end, "llama_intents_volume",
              "30d sum vs previous 30d")
        M.put("intents_volume_30d_yoy_pct", _pct(v30, v30y), "%", end, "llama_intents_volume",
              "30d sum vs same window a year earlier")
        M.put("intents_volume_1y", iv.get("total1y"), "USD", end, "llama_intents_volume", "DefiLlama total1y")
        M.put("intents_volume_all_time", iv.get("totalAllTime"), "USD", end, "llama_intents_volume",
              "DefiLlama totalAllTime")
        M.put("intents_first_day", str(s.index.min().date()), "date", end, "llama_intents_volume",
              "first day with volume in DefiLlama series")
        series["intents"] = s.to_frame()
    inf_ = raw.get("llama_intents_fees")
    if inf_ and inf_.get("totalDataChart"):
        s = _ts_frame(inf_["totalDataChart"], "intents_fees_usd", "sum")["intents_fees_usd"]
        end = s.index.max()
        M.put("intents_fees_30d", _window_sum(s, end, 30), "USD", end, "llama_intents_fees",
              "DefiLlama NEAR Intents fees, 30d sum")
        series["intents_fees"] = s.to_frame()
    if "intents" in series:
        a = M.headline.get("intents_volume_30d", {}).get("value")
        b = M.headline.get("dex_volume_near_30d", {}).get("value")
        if a and b:
            M.put("intents_share_of_near_dex_pct", a / b * 100, "%", M.headline["intents_volume_30d"]["as_of"],
                  "llama", "Intents 30d volume / all NEAR-chain DEX 30d volume")

    # ------------------------------------------------------------ price
    ph = raw.get("price_history")
    price = None
    if ph:
        if "prices" in ph:
            price = _ts_frame([(int(t / 1000), p) for t, p in ph["prices"]], "price")["price"]
            psrc = "price_history (CoinGecko)"
        else:
            pr = ph["coins"]["coingecko:near"]["prices"]
            price = _ts_frame([(x["timestamp"], x["price"]) for x in pr], "price")["price"]
            psrc = "price_history (DefiLlama coins)"
        price = price.groupby(level=0).last()
    if (price is None or len(price) < 30) and act is not None:
        price = act["near_price"].replace(0, np.nan).dropna()
        psrc = "nearblocks_charts (near_price)"
    if price is not None and len(price):
        end = price.index.max()
        M.put("near_price_usd", price.iloc[-1], "USD", end, psrc, "last daily close")
        M.put("near_price_365d_change_pct", _pct(price.iloc[-1], _at(price, end - pd.Timedelta(days=365))), "%", end,
              psrc, "price now vs ~365d earlier (nearest point within 3 days)")
        series["price"] = price.to_frame("price")
    nbs = raw.get("nearblocks_stats")
    if nbs and price is not None and len(price):
        nbp = float(nbs["stats"][0]["near_price"])
        M.put("price_crosscheck_nearblocks_diff_pct", _pct(nbp, price.iloc[-1]), "%", "latest",
              "nearblocks_stats vs " + psrc, "NearBlocks spot price vs primary price source (data-quality check)")
    if act is not None:
        # Long, single-source price history (same indexer as activity) for the multi-year charts + lead-lag test
        series["price_long"] = act["near_price"].replace(0, np.nan).dropna().to_frame("price")
    a30 = M.headline.get("fees_usd_30d_nearblocks", {}).get("value")
    b30 = M.headline.get("llama_fees_usd_30d", {}).get("value")
    if a30 and b30:
        M.put("fees_crosscheck_diff_pct", _pct(a30, b30), "%", M.headline["llama_fees_usd_30d"]["as_of"],
              "nearblocks_charts vs llama_chain_fees",
              "NearBlocks 30d fee USD vs DefiLlama 30d fee USD (independent indexers; data-quality check)")

    # ------------------------------------------------------------ Hypothesis test: Intents volume vs price / usage
    hyp = hypothesis_test(series)
    return {"headline": M.headline, "missing": M.missing, "series": series, "hypothesis": hyp,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}


def hypothesis_test(series: dict) -> dict:
    """Working hypothesis (track prompt): NEAR Intents volume is a better leading indicator of real
    network usage than token price.  Test on weekly log-changes:
      * corr(dlog intents_t, dlog X_{t+k}) for k = -4..+4 weeks, X in {txns, active accounts, fees}
      * same with price as the predictor
    A 'leading indicator' should show meaningfully positive corr at k > 0. n is reported for every value."""
    if "intents" not in series or "activity" not in series:
        return {"status": "skipped: missing intents or activity series"}
    a = series["activity"]
    w = pd.DataFrame({
        "intents": series["intents"]["intents_usd"].resample("W-SUN").sum(),
        "txns": a["txns"].resample("W-SUN").sum(),
        "active_accounts": a["active_accounts"].resample("W-SUN").mean(),
        "fees": a["fee_near"].resample("W-SUN").sum(),
    })
    psrc = series.get("price_long") if "price_long" in series else series.get("price")
    if psrc is not None:
        w["price"] = psrc["price"].resample("W-SUN").mean()
    start = series["intents"]["intents_usd"].gt(0).idxmax() + pd.Timedelta(days=14)
    w = w[(w.index >= start)]
    w = w.iloc[1:-1]  # drop partial first/last weeks
    w = w[(w > 0).all(axis=1)]
    d = np.log(w).diff().dropna()
    out = {"weeks": int(len(d)), "start": str(d.index.min().date()) if len(d) else None,
           "end": str(d.index.max().date()) if len(d) else None, "lags": list(range(-4, 5)), "results": {}}
    for pred in ["intents", "price"]:
        if pred not in d:
            continue
        for tgt in ["txns", "active_accounts", "fees"] + (["price"] if pred == "intents" else []):
            vals = []
            for k in out["lags"]:
                c = d[pred].corr(d[tgt].shift(-k))
                vals.append(None if pd.isna(c) else round(float(c), 3))
            out["results"][f"{pred}->{tgt}"] = vals
    # summary: best positive lead (k>=1) correlation per predictor, averaged over usage targets
    summ = {}
    for pred in ["intents", "price"]:
        leads = []
        for tgt in ["txns", "active_accounts", "fees"]:
            r = out["results"].get(f"{pred}->{tgt}")
            if r:
                leads.append(np.nanmean([x for x, k in zip(r, out["lags"]) if k >= 1 and x is not None]))
        summ[pred] = round(float(np.nanmean(leads)), 3) if leads else None
    out["mean_lead_corr_1to4w"] = summ
    n = max(len(d), 4)
    out["approx_95pct_noise_band"] = round(1.96 / math.sqrt(n), 3)
    return out
