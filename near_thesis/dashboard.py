"""Build docs/index.html (static, GitHub Pages ready) + docs/data.json from computed metrics.

Data is embedded inline so the page also works when opened from disk. Chart.js is loaded from a CDN.
Each chart carries: the plain-English sentence (generated from the numbers), and the exact
endpoint + transform that produced it.
"""
from __future__ import annotations

import html
import json

import pandas as pd

from .report import fmt

START = "2023-01-01"


def _s(df, col, roll=7, start=START, scale=1.0):
    s = df[col].astype(float)
    s = s[s.index >= start]
    if roll:
        s = s.rolling(roll, min_periods=1).mean()
    return s * scale


def _labels_values(s):
    return [str(d.date()) for d in s.index], [None if pd.isna(v) else round(float(v), 4) for v in s.values]


def _v(h, k):
    return (h.get(k) or {}).get("value")


def build_charts(res, model, urls):
    S, H = res["series"], res["headline"]
    charts = []

    if "activity" in S:
        a = S["activity"]
        tx = _s(a, "txns"); aa = _s(a, "active_accounts")
        l, v1 = _labels_values(tx); _, v2 = _labels_values(aa.reindex(tx.index))
        charts.append({
            "id": "activity", "title": "Daily transactions and active accounts (7-day avg)", "type": "line",
            "labels": l, "datasets": [{"label": "transactions/day", "data": v1, "yAxisID": "y"},
                                      {"label": "active accounts/day", "data": v2, "yAxisID": "y2"}],
            "sentence": f"30-day average: {fmt(_v(H,'txns_30d_avg'),'int')} tx/day ({fmt(_v(H,'txns_30d_avg_yoy_pct'),'spct')} YoY) "
                        f"and {fmt(_v(H,'active_accounts_30d_avg'),'int')} active accounts/day ({fmt(_v(H,'active_accounts_30d_avg_yoy_pct'),'spct')} YoY).",
            "query": f"GET {urls.get('nearblocks_charts')} -> charts[].txns, charts[].active_accounts; 7-day rolling mean."})

    if "intents" in S:
        iv = _s(S["intents"], "intents_usd", start="2024-12-01")
        l, v1 = _labels_values(iv)
        ds = [{"label": "NEAR Intents volume, USD/day (7d avg)", "data": v1, "yAxisID": "y"}]
        pl = S.get("price_long", S.get("price"))
        if pl is not None:
            p = pl["price"].reindex(iv.index)
            ds.append({"label": "NEAR price, USD", "data": _labels_values(p)[1], "yAxisID": "y2"})
        charts.append({
            "id": "intents", "title": "NEAR Intents cross-chain volume vs NEAR price", "type": "line", "labels": l, "datasets": ds,
            "sentence": f"Intents settled {fmt(_v(H,'intents_volume_30d'),'usdb')} in the last 30 days "
                        f"({fmt(_v(H,'intents_volume_30d_mom_pct'),'spct')} vs prior 30d, {fmt(_v(H,'intents_volume_30d_yoy_pct'),'spct')} YoY); "
                        f"price moved {fmt(_v(H,'near_price_365d_change_pct'),'spct')} over 365 days.",
            "query": f"GET {urls.get('llama_intents_volume')} -> totalDataChart; price: {urls.get('nearblocks_charts')} -> charts[].near_price"})

    if "activity" in S:
        a = S["activity"]
        fee = _s(a, "fee_near")
        l, v1 = _labels_values(fee)
        burn = [None if x is None else round(x * 0.7, 2) for x in v1]
        iss = _v(H, "max_gross_issuance_annual")
        ds = [{"label": "gas fees, NEAR/day (7d avg)", "data": v1, "yAxisID": "y"},
              {"label": "burned (70%), NEAR/day", "data": burn, "yAxisID": "y"}]
        if iss:
            ds.append({"label": "max issuance, NEAR/day (current)", "data": [round(iss / 365, 1)] * len(l), "yAxisID": "y2"})
        charts.append({
            "id": "burn", "title": "Fee burn vs issuance (NEAR per day)", "type": "line", "labels": l, "datasets": ds,
            "sentence": f"Annualized burn is {fmt(_v(H,'burn_near_annualized'),'nearm')} vs max issuance of "
                        f"{fmt(_v(H,'max_gross_issuance_annual'),'nearm')}/yr: burn offsets {fmt(_v(H,'burn_to_issuance_pct'),'pct')}. "
                        f"Break-even needs ~{fmt(_v(H,'breakeven_tx_per_day'),'int')} tx/day at today's fee per tx. (Issuance on right axis.)",
            "query": f"GET {urls.get('nearblocks_charts')} -> txn_fee/1e24; issuance = block.total_supply x protocol_config.max_inflation_rate (NEAR RPC)"})

        sup = _s(a, "total_supply_near", roll=0, start="2020-10-01", scale=1e-6)
        l, v = _labels_values(sup)
        charts.append({"id": "supply", "title": "Total NEAR supply (millions)", "type": "line", "labels": l,
                       "datasets": [{"label": "total supply, M NEAR", "data": v, "yAxisID": "y"}],
                       "sentence": f"Net supply grew {fmt(_v(H,'realized_net_inflation_365d_pct'),'pct')} in the last 365 days "
                                   f"({fmt(_v(H,'supply_net_change_365d'),'nearm')}), already net of burn.",
                       "query": f"GET {urls.get('nearblocks_charts')} -> charts[].total_supply / 1e24"})

    if "stables" in S:
        st = _s(S["stables"], "stables", roll=0, scale=1e-6)
        l, v = _labels_values(st)
        charts.append({"id": "stables", "title": "Stablecoin supply on NEAR (USD millions)", "type": "line", "labels": l,
                       "datasets": [{"label": "stablecoins, $M", "data": v, "yAxisID": "y"}],
                       "sentence": f"{fmt(_v(H,'stablecoin_supply_usd'),'usdm')} of stablecoins on NEAR "
                                   f"({fmt(_v(H,'stablecoin_supply_365d_change_pct'),'spct')} YoY, rank #{fmt(_v(H,'stablecoin_chain_rank'))} among chains).",
                       "query": f"GET {urls.get('llama_stablecoins')} -> totalCirculatingUSD.peggedUSD"})
    if "tvl" in S:
        tv = _s(S["tvl"], "tvl", roll=0, scale=1e-6)
        l, v = _labels_values(tv)
        charts.append({"id": "tvl", "title": "DeFi TVL on NEAR (USD millions)", "type": "line", "labels": l,
                       "datasets": [{"label": "TVL, $M", "data": v, "yAxisID": "y"}],
                       "sentence": f"TVL is {fmt(_v(H,'tvl_usd'),'usdm')} ({fmt(_v(H,'tvl_yoy_pct'),'spct')} YoY, USD terms so it moves with price).",
                       "query": f"GET {urls.get('llama_chain_tvl')}"})

    hyp = res["hypothesis"]
    if hyp.get("results"):
        ds = [{"label": k, "data": v} for k, v in hyp["results"].items() if k.split("->")[1] in ("txns", "active_accounts", "fees")]
        charts.append({"id": "hyp", "title": "Lead-lag test: does Intents volume (or price) lead usage?", "type": "bar",
                       "labels": [f"{k:+d}w" for k in hyp["lags"]], "datasets": ds,
                       "sentence": f"Mean correlation 1-4 weeks ahead: Intents {fmt(_v(H,'hyp_intents_lead_corr'),'float')}, "
                                   f"price {fmt(_v(H,'hyp_price_lead_corr'),'float')}; noise band ±{fmt(_v(H,'hyp_noise_band'),'float')} "
                                   f"(n={hyp.get('weeks')} weeks). Positive k = predictor moves first.",
                       "query": "weekly sums/means -> log-differences -> Pearson corr(predictor_t, target_t+k)"})

    if model.get("status") == "ok":
        sc = model["scenarios"]
        yrs = [f"Y{r['year']}" for r in next(iter(sc.values()))["years"]]
        charts.append({"id": "model_infl", "title": "Model: net inflation by scenario (%/yr)", "type": "line", "labels": yrs,
                       "datasets": [{"label": n, "data": [round(r["net_inflation_pct"], 3) for r in s["years"]]} for n, s in sc.items()],
                       "sentence": f"Zero net inflation needs ~{fmt(model['breakeven']['multiple_of_current_tx'],'x1')} today's tx count at today's fee per tx "
                                   f"(a {fmt(model['breakeven']['required_tx_cagr_pct_over_horizon'],'pct')}/yr growth rate over {model['breakeven']['horizon_years']} years).",
                       "query": "near_thesis/model.py with assumptions.yaml; starting values from RPC + NearBlocks"})
        charts.append({"id": "model_yield", "title": "Model: staker real yield by scenario (%/yr)", "type": "line", "labels": yrs,
                       "datasets": [{"label": n, "data": [round(r["staker_real_yield_pct"], 3) for r in s["years"]]} for n, s in sc.items()],
                       "sentence": "Real yield = nominal staking APR after commission, deflated by net supply growth.",
                       "query": "near_thesis/model.py"})
    return charts


CARDS = [("NEAR price", "near_price_usd", "usd2"), ("Tx/day (30d avg)", "txns_30d_avg", "int"),
         ("Active accounts/day", "active_accounts_30d_avg", "int"), ("Intents volume 30d", "intents_volume_30d", "usdb"),
         ("Stablecoins on NEAR", "stablecoin_supply_usd", "usdm"), ("Staking ratio", "staking_ratio_pct", "pct"),
         ("Burn / issuance", "burn_to_issuance_pct", "pct"), ("Net inflation 365d", "realized_net_inflation_365d_pct", "pct")]


def build_html(res, model, signals, sources_log, urls) -> tuple[str, dict]:
    H = res["headline"]
    charts = build_charts(res, model, urls)
    def card_val(k, f):
        v = _v(H, k)
        return f"${v:,.2f}" if (f == "usd2" and v is not None) else fmt(v, f)
    cards = "".join(
        f'<div class="card"><div class="k">{html.escape(t)}</div><div class="v">{html.escape(card_val(k, f))}</div>'
        f'<div class="d">as of {html.escape(str((H.get(k) or {}).get("as_of")))}</div></div>' for t, k, f in CARDS)
    sig_rows = "".join(
        f'<tr><td>{html.escape(s["claim"])}</td><td><code>{s["metric"]}</code></td><td>{html.escape(fmt(s["value"], "float"))}</td>'
        f'<td>{s["direction"]} {html.escape(fmt(s["threshold_value"], "float"))}</td><td class="{s["status"].lower()}">{s["status"]}</td></tr>'
        for s in signals)
    src_rows = "".join(
        f'<tr><td>{html.escape(r["source"])}</td><td class="u">{html.escape(r.get("url") or "-")}</td><td>{html.escape(r["status"])}</td><td>{html.escape(str(r.get("fetched_at")))}</td></tr>'
        for r in sources_log)
    data = {"generated_at": res["generated_at"], "headline": H, "signals": signals, "charts": charts,
            "model": model, "hypothesis": res["hypothesis"], "sources": sources_log}
    blocks = "".join(
        f'<section class="chart"><h3>{html.escape(c["title"])}</h3><p class="s">{html.escape(c["sentence"])}</p>'
        f'<div class="cv"><canvas id="c_{c["id"]}"></canvas></div><details><summary>Query behind this chart</summary><code>{html.escape(c["query"])}</code></details></section>'
        for c in charts)
    page = TEMPLATE.replace("%%CARDS%%", cards).replace("%%CHARTS%%", blocks).replace("%%SIGNALS%%", sig_rows) \
        .replace("%%SOURCES%%", src_rows).replace("%%GEN%%", html.escape(res["generated_at"])) \
        .replace("%%DATA%%", json.dumps(data, default=str).replace("</", "<\\/"))
    return page, data


TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>NEAR Investment Thesis - live evidence dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
:root{--bg:#0b0f14;--fg:#e8edf2;--mut:#8a97a6;--line:#1e2833;--acc:#00ec97;--bad:#ff6b6b}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 -apple-system,Segoe UI,Inter,Roboto,sans-serif}
main{max-width:1180px;margin:auto;padding:28px 18px 60px}h1{margin:0 0 4px;font-size:28px}h2{margin:36px 0 12px;font-size:20px}
.sub{color:var(--mut);margin:0 0 20px}.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:12px}
.card{border:1px solid var(--line);border-radius:10px;padding:12px 14px;background:#0f151c}.card .k{color:var(--mut);font-size:12px;text-transform:uppercase;letter-spacing:.04em}
.card .v{font-size:22px;font-weight:650;margin:4px 0}.card .d{color:var(--mut);font-size:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(520px,1fr));gap:16px}
.chart{border:1px solid var(--line);border-radius:10px;padding:14px;background:#0f151c;min-width:0}.chart h3{margin:0 0 4px;font-size:16px}
.chart .s{color:#c6d0da;margin:0 0 10px;font-size:14px}.cv{position:relative;height:280px}
details{margin-top:8px;color:var(--mut);font-size:12px}code{word-break:break-all;color:#b7c4d1}
table{width:100%;border-collapse:collapse;font-size:13px}td,th{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{color:var(--mut);font-weight:500}.bull{color:var(--acc);font-weight:700}.bear{color:var(--bad);font-weight:700}.unknown{color:var(--mut)}
td.u{word-break:break-all;max-width:420px;color:var(--mut)}a{color:var(--acc)}
@media(max-width:600px){.grid{grid-template-columns:1fr}}
</style></head><body><main>
<h1>NEAR Investment Thesis: the evidence</h1>
<p class="sub">Every number on this page was fetched from free public endpoints (NEAR RPC, NearBlocks, DefiLlama, CoinGecko) by <code>python build.py</code>. Generated %%GEN%% UTC. Nothing is typed in by hand.</p>
<div class="cards">%%CARDS%%</div>
<h2>Falsifiable signals</h2>
<p class="sub">Thresholds live in <code>assumptions.yaml</code>. BULL = the data currently supports the bull case for that signal; BEAR = it does not.</p>
<table><tr><th>Claim</th><th>Metric</th><th>Value</th><th>Bull if</th><th>Status</th></tr>%%SIGNALS%%</table>
<h2>Charts</h2><div class="grid">%%CHARTS%%</div>
<h2>Data sources (this build)</h2>
<table><tr><th>Source</th><th>Endpoint</th><th>Status</th><th>Fetched (UTC)</th></tr>%%SOURCES%%</table>
<p class="sub" style="margin-top:20px">Raw data: <a href="data.json">data.json</a>. Re-run: <code>pip install -r requirements.txt &amp;&amp; python build.py</code>.</p>
</main>
<script>
const DATA = %%DATA%%;
const PAL=['#00ec97','#5aa9ff','#ffb547','#ff6b6b','#c58cff','#7ee0ff'];
Chart.defaults.color='#8a97a6';Chart.defaults.borderColor='#1e2833';
for(const c of DATA.charts){
  const el=document.getElementById('c_'+c.id); if(!el) continue;
  const two=c.datasets.some(d=>d.yAxisID==='y2');
  const ds=c.datasets.map((d,i)=>Object.assign({borderColor:PAL[i%PAL.length],backgroundColor:PAL[i%PAL.length]+(c.type==='bar'?'cc':'33'),pointRadius:0,borderWidth:1.6,tension:.15,spanGaps:true},d));
  const scales={x:{ticks:{maxTicksLimit:8}},y:{position:'left',ticks:{callback:v=>Intl.NumberFormat('en',{notation:'compact'}).format(v)}}};
  if(two) scales.y2={position:'right',grid:{drawOnChartArea:false},ticks:{callback:v=>Intl.NumberFormat('en',{notation:'compact'}).format(v)}};
  new Chart(el,{type:c.type,data:{labels:c.labels,datasets:ds},options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},plugins:{legend:{labels:{boxWidth:12}}},scales}});
}
</script></body></html>
"""
