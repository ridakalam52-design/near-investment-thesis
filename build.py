#!/usr/bin/env python3
"""One command to rebuild everything from raw public data.

    python build.py            # fetch live data, recompute, rebuild dashboard + THESIS.md
    python build.py --offline  # recompute from the committed snapshots in data/raw/ (no network)

Outputs:
    data/raw/*.json          raw API responses (snapshot, with URL + fetch time)
    data/sources_log.json    which endpoint succeeded / failed this run
    data/metrics.json        headline metrics (value, unit, as_of, source, how)
    data/model.json          scenario model output
    data/signals.json        falsifiable signals with BULL/BEAR/UNKNOWN status
    docs/index.html          static dashboard (GitHub Pages: serve /docs)
    docs/data.json           everything the dashboard draws
    THESIS.md                rendered from templates/THESIS.template.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from near_thesis import dashboard, metrics, model, report, sources

ROOT = Path(__file__).resolve().parent


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="use data/raw snapshots, no network")
    args = ap.parse_args(argv)

    assumptions = yaml.safe_load((ROOT / "assumptions.yaml").read_text())
    raw_dir = ROOT / "data" / "raw"
    print(f"[1/5] fetching sources ({'offline snapshot' if args.offline else 'live'}) ...")
    raw, log = sources.fetch_all(raw_dir, offline=args.offline)
    for r in log:
        print(f"      {r['status'][:60]:<60} {r['source']}")
    required = [k for k in sources.SOURCES if k not in sources.OPTIONAL]
    have_required = [k for k in required if k in raw]
    if len(have_required) < len(required) // 2:
        print("ERROR: fewer than half of the required sources are available; refusing to build.", file=sys.stderr)
        return 2

    print("[2/5] computing metrics ...")
    res = metrics.compute(raw, assumptions)
    report.augment_with_hypothesis(res["headline"], res["hypothesis"])
    print("[3/5] running scenario model ...")
    mdl = model.run(res["headline"], assumptions)
    signals = report.evaluate_signals(res["headline"], assumptions["signals"])

    urls = {r["source"]: r.get("url") for r in log if r["status"].startswith("ok") or "snapshot" in r["status"]}
    out = ROOT / "data"
    (out / "sources_log.json").write_text(json.dumps(log, indent=1))
    (out / "metrics.json").write_text(json.dumps({"generated_at": res["generated_at"], "headline": res["headline"],
                                                  "missing": res["missing"], "hypothesis": res["hypothesis"]}, indent=1, default=str))
    (out / "model.json").write_text(json.dumps(mdl, indent=1, default=str))
    (out / "signals.json").write_text(json.dumps(signals, indent=1, default=str))

    print("[4/5] building dashboard docs/index.html ...")
    page, data = dashboard.build_html(res, mdl, signals, log, urls)
    docs = ROOT / "docs"
    docs.mkdir(exist_ok=True)
    (docs / "index.html").write_text(page)
    (docs / "data.json").write_text(json.dumps(data, default=str))
    (docs / ".nojekyll").write_text("")

    print("[5/5] rendering THESIS.md ...")
    T = report.tables(res["headline"], signals, log, res["hypothesis"], mdl, urls)
    extra = {"generated_at": res["generated_at"],
             "n_bull": sum(s["status"] == "BULL" for s in signals),
             "n_bear": sum(s["status"] == "BEAR" for s in signals),
             "n_unknown": sum(s["status"] == "UNKNOWN" for s in signals),
             "n_signals": len(signals)}
    if mdl.get("status") == "ok":
        be = mdl["breakeven"]
        extra.update({"be_multiple": be["multiple_of_current_tx"], "be_cagr": be["required_tx_cagr_pct_over_horizon"],
                      "be_years": be["horizon_years"], "realization": mdl["inputs"]["issuance_realization"],
                      "commission": mdl["inputs"]["validator_commission"] * 100})
        for name, sc in mdl["scenarios"].items():
            last = sc["years"][-1]
            extra[f"{name}_final_net_infl"] = last["net_inflation_pct"]
            extra[f"{name}_final_real_yield"] = last["staker_real_yield_pct"]
            extra[f"{name}_final_burn_ratio"] = last["burn_to_issuance_pct"]
            extra[f"{name}_tx_growth"] = sc["assumptions"]["tx_growth"] * 100
            extra[f"y0_real_yield"] = sc["years"][0]["staker_real_yield_pct"]
            extra[f"y0_nominal_apr"] = sc["years"][0]["staker_nominal_apr_pct"]
        bf = mdl["scenarios"].get("bull", {}).get("years", [{}])[-1].get("net_inflation_pct")
        if bf is not None:
            extra["bull_zero_text"] = (
                "still leaves net inflation above zero - **on these numbers the token's case cannot rest on burn**; "
                "it rests on staking yield and on Intents value capture." if bf > 0 else
                "reaches zero or negative net inflation - burn becomes a real part of the case.")
    for s in signals:
        extra[f"sig_{s['id']}"] = s["status"]
    H = res["headline"]
    extra["price_src"] = (H.get("near_price_usd") or {}).get("source", "n/a").replace("price_history ", "").strip("()")
    extra["price_asof"] = (H.get("near_price_usd") or {}).get("as_of")
    a, b = (H.get("intents_fees_30d") or {}).get("value"), (H.get("llama_fees_usd_30d") or {}).get("value")
    extra["intents_fee_multiple"] = a / b if a and b else None
    tpl = (ROOT / "templates" / "THESIS.template.md").read_text()
    (ROOT / "THESIS.md").write_text(report.render(tpl, res["headline"], extra, T))

    ok = sum(1 for r in log if r["status"] == "ok" or r["status"] == "ok (snapshot)")
    print(f"done. sources ok: {ok}/{len(sources.SOURCES)}; metrics: {len(res['headline'])} "
          f"({len(res['missing'])} missing); signals: {extra['n_bull']} bull / {extra['n_bear']} bear / {extra['n_unknown']} unknown")
    print(f"open {docs / 'index.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
