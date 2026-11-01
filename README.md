# NEAR Investment Thesis — evidence you can re-run

**NEAR HACKATHON · track: Investment Thesis (`thesis`)**

A long-term investment thesis for NEAR where every number comes from a pipeline anyone can re-run.
One command pulls free, keyless public data (NEAR RPC, NearBlocks, DefiLlama, CoinGecko), computes the
thesis metrics, runs a scenario model whose assumptions live in one YAML file, tests the hypothesis
"*NEAR Intents volume is a better leading indicator of network usage than token price*", and renders a
static dashboard plus `THESIS.md`. No API keys, no wallet, no hand-typed figures.

**Problem it solves:** most token theses quote numbers nobody can check. Here the thesis is a build
artifact: if the data changes, the bull/bear signals and the prose numbers change with it, and the
bear case is printed next to the bull case.

## Try it (judges / AI reviewers)

Requirements: Python 3.10+ and internet access.

```bash
pip install -r requirements.txt
python build.py
```

- **See:** the console lists every source with `ok` / `failed: …`, then
  `done. sources ok: N/15; metrics: … ; signals: X bull / Y bear / Z unknown`.
- **Open `docs/index.html`** in a browser → headline cards, a falsifiable-signals table (BULL/BEAR per
  signal), 9 charts each with a one-sentence reading and the exact endpoint behind it, and a table of
  which sources succeeded in this build.
- **Open `THESIS.md`** → claim, evidence snapshot, bull case, bear case, hypothesis test, model output,
  signals, every metric with how it was computed, limits, sources. All numbers are filled in by the build.

No network? Rebuild from the committed raw snapshots:

```bash
python build.py --offline
python -m unittest discover -s tests -v     # 8 tests: outputs exist, no unfilled placeholders, provenance, model math
```

Change an assumption and see the effect:

```bash
# e.g. set scenarios.bull.tx_growth to 2.0 in assumptions.yaml, then
python build.py --offline
# -> THESIS.md section 6 and the two "Model" charts update
```

## What it measures

| Area | Metric(s) | Source (keyless) |
|---|---|---|
| Usage | daily transactions, active accounts, new accounts (30d avg, YoY) | NearBlocks `GET /v1/charts` |
| Fees & burn | gas fees in NEAR and USD, 70% burn, fee per tx | NearBlocks; cross-checked with DefiLlama `summary/fees/near` |
| Supply & inflation | total supply, `max_inflation_rate`, `protocol_reward_rate`, realized 365d net supply growth, implied gross issuance | NEAR RPC `block`, `EXPERIMENTAL_protocol_config`; NearBlocks supply history |
| Staking | total staked, staking ratio, validator count, gross APR | NEAR RPC `validators` |
| Stablecoins | USD-pegged supply on NEAR, 30d/365d change, rank among chains | DefiLlama stablecoins API |
| DeFi | chain TVL, DEX volume on NEAR | DefiLlama |
| NEAR Intents | daily volume, 30d/1y/all-time, MoM & YoY, fees, share of NEAR DEX volume | DefiLlama `summary/dexs/near-intents`, `summary/fees/near-intents` |
| Price | NEAR/USD 365d (CoinGecko free; DefiLlama coins fallback), multi-year from NearBlocks | CoinGecko / DefiLlama / NearBlocks |
| Hypothesis | lead-lag correlation (−4…+4 weeks) of weekly log-changes: Intents→usage vs price→usage, with a 95% noise band | derived |
| Model | 5-year bear/base/bull: issuance, burn, net inflation, staker nominal & real yield, break-even tx/day | `near_thesis/model.py` + `assumptions.yaml` |

If an endpoint fails, the build logs it in `data/sources_log.json`, tries the next fallback (3 public
RPCs; CoinGecko → DefiLlama coins), or reuses the last good snapshot and labels it `stale snapshot used`.
A metric whose input is missing prints `n/a (source failed)` — it is never estimated.

## How NEAR fits in

- Reads chain state directly from NEAR mainnet JSON-RPC (supply, validator stakes, protocol inflation config).
- Tests whether **NEAR Intents** cross-chain volume tracks or leads on-chain usage, and whether its value
  shows up in NEAR fees/burn — the core of the long-term thesis.
- Scenario model of NEAR's token economics (2.5% max inflation, 70% gas burn, staking yield).

## Repository layout

```
build.py                    one command: fetch -> metrics -> model -> dashboard -> THESIS.md
assumptions.yaml            every model assumption + signal thresholds (edit and re-run)
near_thesis/sources.py      endpoints, retries, fallbacks, raw snapshots, source log
near_thesis/metrics.py      headline metrics (value, unit, as_of, source, how) + hypothesis test
near_thesis/model.py        scenario model
near_thesis/report.py       signal evaluation + THESIS.md rendering
near_thesis/dashboard.py    docs/index.html (Chart.js) + docs/data.json
templates/THESIS.template.md  thesis prose with {{metric}} placeholders
data/raw/*.json             raw API responses with URL + fetch time (reproducibility snapshot)
data/{metrics,model,signals,sources_log}.json
docs/index.html             static dashboard (GitHub Pages: Settings → Pages → Deploy from branch → /docs)
.github/workflows/rebuild.yml  daily rebuild at 03:17 UTC, tests, commits refreshed data/docs/THESIS.md
tests/test_pipeline.py      offline end-to-end tests
```

## Deploy the live dashboard

1. Push to GitHub, then Settings → Pages → *Deploy from a branch* → `main` / `/docs`.
2. Settings → Actions → General → Workflow permissions → *Read and write* (the daily job commits refreshed data).
3. The workflow runs daily and on demand (*Actions → Rebuild thesis data + dashboard → Run workflow*).

## Known limits

- NEAR Intents Explorer API requires a partner JWT → not used; Intents numbers come from DefiLlama's adapter.
- NEAR BigQuery public dataset needs a GCP account and bills queries → not used; NearBlocks daily charts instead
  (so "transaction" and "active account" follow NearBlocks' definitions).
- Average validator commission (10%) is an assumption, not fetched.
- CoinGecko's free tier serves 365 days of history; longer price history uses NearBlocks' `near_price`.
- Research, not financial advice.

## Hackathon disclosures

- All code in this repository was written during NEAR HACKATHON (window opened 2026-10-19; this code
  was started 2026-11-01). No pre-hackathon baseline.
- Built with AI coding assistance.
- Libraries: requests, pandas, numpy, PyYAML (Python); Chart.js 4.4.1 via jsDelivr CDN (dashboard).
- Data: NEAR RPC (rpc.mainnet.near.org, FastNEAR free RPC as fallback), NearBlocks API, DefiLlama APIs, CoinGecko API.

## License

MIT — see [LICENSE](LICENSE).
