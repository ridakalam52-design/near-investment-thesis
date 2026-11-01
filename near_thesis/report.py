"""Signals evaluation + THESIS.md rendering from templates/THESIS.template.md.

Placeholders: {{metric_key}} or {{metric_key:fmt}} with fmt in int|pct|spct|usd|usdm|usdb|near|nearm|float|raw.
A placeholder whose metric is missing renders as 'n/a (source failed)' - never a made-up number.
Tables: {{TABLE:signals}} {{TABLE:headline}} {{TABLE:sources}} {{TABLE:hypothesis}} {{TABLE:model}}.
"""
from __future__ import annotations

import re

NA = "n/a (source failed)"


def fmt(v, f="raw"):
    if v is None:
        return NA
    try:
        if f == "int":
            return f"{v:,.0f}"
        if f == "pct":
            return f"{v:.1f}%"
        if f == "spct":
            return f"{v:+.1f}%"
        if f == "usd":
            return f"${v:,.0f}"
        if f == "usdm":
            return f"${v / 1e6:,.1f}M"
        if f == "usdb":
            return f"${v / 1e9:,.2f}B"
        if f == "near":
            return f"{v:,.0f} NEAR"
        if f == "nearm":
            return f"{v / 1e6:,.2f}M NEAR"
        if f == "x1":
            return f"{v:,.1f}×"
        if f == "float":
            return f"{v:.3f}"
        if f == "small":
            return f"{v:.6f}"
    except (TypeError, ValueError):
        pass
    return str(v)


def augment_with_hypothesis(headline: dict, hyp: dict):
    s = hyp.get("mean_lead_corr_1to4w") or {}
    band = hyp.get("approx_95pct_noise_band")
    span = f"{hyp.get('start')}..{hyp.get('end')}"
    def put(k, v, how):
        headline[k] = {"value": v, "unit": "corr", "as_of": hyp.get("end"), "source": "derived (hypothesis test)", "how": how}
    put("hyp_intents_lead_corr", s.get("intents"), f"mean corr of weekly dlog Intents volume vs usage 1-4w later, {span}")
    put("hyp_price_lead_corr", s.get("price"), f"mean corr of weekly dlog NEAR price vs usage 1-4w later, {span}")
    put("hyp_intents_minus_price_lead_corr",
        None if s.get("intents") is None or s.get("price") is None else round(s["intents"] - s["price"], 3),
        "Intents lead corr minus price lead corr")
    put("hyp_noise_band", band, f"~95% noise band 1.96/sqrt(n), n={hyp.get('weeks')} weeks")
    res = hyp.get("results") or {}
    if res and 0 in hyp.get("lags", []):
        i0 = hyp["lags"].index(0)
        for pred in ("intents", "price"):
            v = [res[f"{pred}->{t}"][i0] for t in ("txns", "active_accounts", "fees")
                 if f"{pred}->{t}" in res and res[f"{pred}->{t}"][i0] is not None]
            put(f"hyp_{pred}_coincident_corr", round(sum(v) / len(v), 3) if v else None,
                f"mean same-week corr of weekly dlog {pred} vs usage (txns, active accounts, fees), {span}")
    headline["hyp_weeks"] = {"value": hyp.get("weeks"), "unit": "weeks", "as_of": hyp.get("end"),
                             "source": "derived", "how": "weekly observations in the test"}


def evaluate_signals(headline: dict, signals: list) -> list:
    out = []
    for s in signals:
        v = (headline.get(s["metric"]) or {}).get("value")
        thr = s["threshold"]
        if isinstance(thr, str):
            thr = (headline.get(thr) or {}).get("value")
        if v is None or thr is None:
            status = "UNKNOWN"
        else:
            ok = v > thr if s["direction"] == ">" else v < thr
            status = "BULL" if ok else "BEAR"
        out.append({**s, "value": v, "threshold_value": thr, "status": status,
                    "as_of": (headline.get(s["metric"]) or {}).get("as_of")})
    return out


def _table(rows, cols):
    lines = ["| " + " | ".join(c for c, _ in cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        lines.append("| " + " | ".join(str(fn(r)).replace("|", "/") for _, fn in cols) + " |")
    return "\n".join(lines)


def tables(headline, signals, sources_log, hyp, model, raw_urls):
    T = {}
    T["signals"] = _table(signals, [
        ("Signal", lambda r: r["claim"]), ("Metric", lambda r: f"`{r['metric']}`"),
        ("Value", lambda r: fmt(r["value"], "float") if r["value"] is not None and abs(r["value"]) < 1 and r["metric"].startswith("hyp") else fmt(r["value"], "float" if r["value"] is not None and abs(r["value"]) < 10 else "int") if r["value"] is not None else NA),
        ("Bull if", lambda r: f"{r['direction']} {fmt(r['threshold_value'], 'float')}"),
        ("Status", lambda r: f"**{r['status']}**"), ("As of", lambda r: r["as_of"])])
    rows = [{"k": k, **v} for k, v in headline.items()]
    T["headline"] = _table(rows, [
        ("Metric", lambda r: f"`{r['k']}`"), ("Value", lambda r: fmt(r["value"], "float") if isinstance(r["value"], float) and abs(r["value"]) < 10 else fmt(r["value"], "int") if isinstance(r["value"], (int, float)) else fmt(r["value"])),
        ("Unit", lambda r: r["unit"]), ("As of (UTC)", lambda r: r["as_of"]), ("Source", lambda r: r["source"]),
        ("How", lambda r: r["how"])])
    T["sources"] = _table(sources_log, [
        ("Source", lambda r: r["source"]), ("Endpoint", lambda r: r.get("url") or "-"),
        ("Status", lambda r: r["status"]), ("Fetched (UTC)", lambda r: r.get("fetched_at"))])
    if hyp.get("results"):
        lagcols = [(f"k={k:+d}w", (lambda i: (lambda r: fmt(r["vals"][i], "float")))(i)) for i, k in enumerate(hyp["lags"])]
        rr = [{"pair": p, "vals": v} for p, v in hyp["results"].items()]
        T["hypothesis"] = _table(rr, [("Predictor -> target", lambda r: r["pair"])] + lagcols)
    else:
        T["hypothesis"] = f"Hypothesis test skipped: {hyp.get('status')}"
    if model.get("status") == "ok":
        rows = []
        for name, sc in model["scenarios"].items():
            for y in sc["years"]:
                if y["year"] in (0, 1, 3, model["breakeven"]["horizon_years"]):
                    rows.append({"s": name, **y})
        T["model"] = _table(rows, [
            ("Scenario", lambda r: r["s"]), ("Year", lambda r: r["year"]), ("Tx/day", lambda r: fmt(r["tx_per_day"], "int")),
            ("Issuance", lambda r: fmt(r["issuance_near"], "nearm")), ("Burn", lambda r: fmt(r["burn_near"], "nearm")),
            ("Burn/issuance", lambda r: fmt(r["burn_to_issuance_pct"], "pct")),
            ("Net inflation", lambda r: fmt(r["net_inflation_pct"], "pct")),
            ("Staker APR (nominal)", lambda r: fmt(r["staker_nominal_apr_pct"], "pct")),
            ("Staker real yield", lambda r: fmt(r["staker_real_yield_pct"], "pct"))])
    else:
        T["model"] = f"Model skipped: {model.get('status')}"
    return T


PH = re.compile(r"\{\{\s*([A-Za-z0-9_:.]+)\s*\}\}")


def render(template: str, headline: dict, extra: dict, T: dict) -> str:
    def rep(m):
        key = m.group(1)
        if key.startswith("TABLE:"):
            return T.get(key[6:], f"(table {key[6:]} unavailable)")
        name, _, f = key.partition(":")
        if name in extra:
            return fmt(extra[name], f or "raw")
        if name not in headline:
            return NA
        return fmt(headline[name]["value"], f or "raw")
    return PH.sub(rep, template)
