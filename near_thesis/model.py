"""Scenario model: fee burn vs issuance, net supply, staking yield.

Starting values come from fetched metrics; growth rates come from assumptions.yaml.
Outputs are in NEAR (no price forecast), plus USD at the *current* price, labelled as such.
"""
from __future__ import annotations

import math


def _v(h, k):
    x = h.get(k)
    return None if x is None else x.get("value")


def run(headline: dict, assumptions: dict) -> dict:
    need = ["total_supply_rpc", "total_staked", "max_inflation_rate_pct", "protocol_reward_rate_pct",
            "txns_30d_avg", "fee_per_tx_near"]
    miss = [k for k in need if _v(headline, k) is None]
    if miss:
        return {"status": f"skipped: missing inputs {miss}"}
    S0 = _v(headline, "total_supply_rpc")
    stake_ratio0 = _v(headline, "total_staked") / S0
    infl0 = _v(headline, "max_inflation_rate_pct") / 100
    prr = _v(headline, "protocol_reward_rate_pct") / 100
    tx0 = _v(headline, "txns_30d_avg")
    fpt0 = _v(headline, "fee_per_tx_near")
    price = _v(headline, "near_price_usd")
    burn_share = assumptions["protocol"]["fee_burn_share"]
    m = assumptions["model"]
    commission = m["avg_validator_commission"]
    H = int(m["horizon_years"])

    realization = m.get("issuance_realization")
    realization_src = "assumptions.yaml"
    if realization is None:
        gross = _v(headline, "implied_gross_issuance_365d")
        net = _v(headline, "supply_net_change_365d")
        if gross is not None and net is not None:
            s_then = S0 - net  # approx supply a year ago
            realization = max(0.0, min(1.0, gross / (s_then * infl0)))
            realization_src = "calibrated: implied 365d gross issuance / (supply_1y_ago x max_inflation)"
        else:
            realization, realization_src = 1.0, "default 1.0 (calibration inputs missing)"

    inputs = {
        "total_supply": S0, "staking_ratio": stake_ratio0, "max_inflation_rate": infl0,
        "protocol_reward_rate": prr, "tx_per_day": tx0, "fee_per_tx_near": fpt0, "burn_share": burn_share,
        "validator_commission": commission, "issuance_realization": realization,
        "issuance_realization_source": realization_src, "price_usd_constant": price,
    }
    out = {"status": "ok", "inputs": inputs, "scenarios": {}}
    for name, sc in assumptions["scenarios"].items():
        infl = sc.get("max_inflation_rate")
        infl = infl0 if infl is None else infl
        S, tx, fpt, sr = S0, tx0, fpt0, stake_ratio0
        rows = []
        for y in range(0, H + 1):
            issuance = S * infl * realization
            burn = tx * 365 * fpt * burn_share
            staked = S * sr
            apr = issuance * (1 - prr) * (1 - commission) / staked if staked else None
            net = issuance - burn
            net_infl = net / S
            rows.append({
                "year": y, "supply": S, "tx_per_day": tx, "fee_per_tx_near": fpt,
                "issuance_near": issuance, "burn_near": burn, "net_supply_change_near": net,
                "net_inflation_pct": net_infl * 100, "burn_to_issuance_pct": burn / issuance * 100,
                "staking_ratio_pct": sr * 100, "staker_nominal_apr_pct": None if apr is None else apr * 100,
                "staker_real_yield_pct": None if apr is None else ((1 + apr) / (1 + net_infl) - 1) * 100,
                "fees_usd_at_current_price": None if price is None else tx * 365 * fpt * price,
            })
            S = S + net
            tx = tx * (1 + sc["tx_growth"])
            fpt = fpt * (1 + sc["fee_per_tx_growth"])
            sr = min(0.95, max(0.05, sr + sc["staking_ratio_change_pp_per_year"] / 100))
        out["scenarios"][name] = {"description": sc.get("description"), "assumptions": sc, "years": rows}
    # How much usage would make NEAR net-deflationary at today's fee per tx?
    iss0 = S0 * infl0 * realization
    be_tx = iss0 / 365 / (fpt0 * burn_share)
    out["breakeven"] = {
        "tx_per_day_for_zero_net_inflation": be_tx,
        "multiple_of_current_tx": be_tx / tx0,
        "required_tx_cagr_pct_over_horizon": (math.pow(be_tx / tx0, 1 / H) - 1) * 100,
        "horizon_years": H,
    }
    return out
