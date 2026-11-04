# NEAR Investment Thesis — evidence first

> **This file is generated.** Every number below is filled in by `python build.py` from data the pipeline
> fetched itself (NEAR RPC, NearBlocks, DefiLlama, CoinGecko). Placeholders whose source failed print
> `n/a (source failed)` instead of a number. Edit the prose in `templates/THESIS.template.md`, never the numbers.
>
> Generated: 2026-11-04T10:54:50+00:00 UTC · Signals right now: **3 bull / 9 bear / 0 unknown** (of 12).

## 1. The claim

**Long-term thesis:** NEAR's value is shifting from *being a busy L1* to *being the settlement and
coordination layer for cross-chain intents (NEAR Intents) and AI agents*. If that is right, the metric
that matters is value settled through NEAR Intents, not raw transaction counts — and over time that
value has to show up in on-chain fees, stablecoin liquidity and a shrinking net inflation.

**Working hypothesis tested here (from the track prompt):** *cross-chain volume through NEAR Intents is a
better leading indicator of real network usage than token price.*

**Investment framing:** NEAR is held for its staking yield and for exposure to Intents/agent adoption.
The thesis is *wrong* if Intents growth stalls, or if it never feeds back into fees and burn, leaving
holders with ~2.5% dilution and nothing to offset it.

## 2. Evidence snapshot

| What | Value | As of (UTC) |
|---|---|---|
| NEAR price (CoinGecko) | $4.091 (+123.1% over 365d) | 2026-11-04 |
| NEAR Intents volume, last 30d | $3.97B (+125.5% YoY, -12.5% vs prior 30d) | DefiLlama |
| NEAR Intents volume, last 365d / all time | $32.95B / $36.39B (series starts 2024-12-10) | DefiLlama |
| NEAR Intents fees, last 30d | $5.8M | DefiLlama |
| Intents share of all DEX volume attributed to NEAR | 89.4% | DefiLlama |
| Transactions/day (30d avg) | 690,247 (-84.7% YoY) | NearBlocks |
| Active accounts/day (30d avg) | 62,208 (-77.0% YoY) | NearBlocks |
| New accounts/day (30d avg) | 9,605 (-95.9% YoY) | NearBlocks |
| Gas fees, last 30d | 36,038 NEAR ≈ $176,990 (-63.9% YoY in NEAR) | NearBlocks |
| Gas fees, last 30d (independent check) | $179,384 (NearBlocks differs by -1.3%) | DefiLlama |
| Annualized burn (70% of fees) | 306,926 NEAR | NearBlocks |
| Max annual issuance (2.5% of supply) | 32,769,501 NEAR | NEAR RPC |
| Burn as % of issuance | 0.9% | derived |
| Realized net supply growth, last 365d | 2.5% (31,724,286 NEAR) | NearBlocks |
| Total supply | 1,310,780,048 NEAR at block 223,007,070 | NEAR RPC |
| Staked / staking ratio / validators | 586,296,801 NEAR / 44.7% / 379 | NEAR RPC |
| Gross staking APR (before commission) | 5.6% | derived |
| Stablecoins on NEAR | $128.8M (+24.2% 30d, -45.5% YoY, rank #29) | DefiLlama |
| DeFi TVL | $188.5M (+30.9% YoY, USD) | DefiLlama |

Full metric table with the exact computation of each number is in section 8.

## 3. Bull case

1. **Intents volume.** NEAR Intents settled $32.95B over the last year and
   $3.97B in the last 30 days (+125.5% vs the same window a year ago).
   It is now 89.4% of all DEX volume DefiLlama attributes to NEAR — the product, not
   the L1's own DeFi, is where the volume is.
2. **Intents earns fees.** $5.8M of Intents fees in 30 days vs $179,384 of L1 gas fees
   (32.2× L1 gas). If even part of that value
   is routed back to NEAR (fees, staking demand, token-denominated settlement), the token's value capture changes.
3. **Security budget.** 44.7% of supply is staked across 379 validators;
   stakers earn ~5.0% nominal after an assumed 10.0% commission, i.e. a positive real
   yield of ~2.5% after dilution.
4. **Inflation is capped on-chain.** `max_inflation_rate` reads 2.5% straight
   from protocol config; realized net supply growth was 2.5% over the last year.
5. **Short-term liquidity.** Stablecoin supply moved +24.2% in 30 days;
   TVL is +30.9% YoY.

## 4. Bear case

1. **Raw L1 usage versus a year ago.** Transactions/day are -84.7% YoY and active accounts
   -77.0% YoY; new accounts -95.9%. Whatever drove
   last year's counts is what a re-run should explain before calling usage "growing".
2. **Fee burn versus issuance.** Burn offsets 0.9% of issuance. At today's
   fee per transaction (0.001740 NEAR) the chain would need ~73,710,554 tx/day —
   106.8× today — to stop net inflation. That is a 154.5%/yr growth rate for 5 years.
   Holders who don't stake are diluted ~2.5%/yr.
3. **Intents value does not obviously accrue to the NEAR token.** Intents fees ($5.8M/30d) are
   not NEAR gas; L1 gas fees moved -24.3% YoY in USD (DefiLlama) and -63.9%
   in NEAR terms, even while Intents volume rose. The value-capture link is the weakest part of the thesis.
4. **Stablecoin base versus a year ago.** $128.8M on NEAR, -45.5%
   YoY, rank #29 among chains — small for a chain pitching itself as a settlement layer.
5. **Intents momentum is not one-way.** The last 30 days were -12.5% vs the 30 days before.

## 5. Hypothesis test: does Intents volume lead usage better than price?

Method (`near_thesis/metrics.py::hypothesis_test`): weekly totals since Intents launched → log-differences →
Pearson correlation between the predictor in week *t* and the target in week *t+k*. Positive *k* means the
predictor moves first. 95 weekly observations; with that *n*, |corr| below ~0.201
is indistinguishable from noise (95%).

| Predictor -> target | k=-4w | k=-3w | k=-2w | k=-1w | k=+0w | k=+1w | k=+2w | k=+3w | k=+4w |
|---|---|---|---|---|---|---|---|---|---|
| intents->txns | -0.081 | 0.061 | 0.044 | -0.086 | 0.268 | 0.017 | -0.111 | 0.032 | 0.057 |
| intents->active_accounts | -0.010 | -0.019 | -0.008 | -0.039 | -0.069 | 0.089 | 0.022 | 0.010 | 0.061 |
| intents->fees | -0.075 | 0.033 | 0.066 | -0.145 | 0.301 | 0.019 | -0.120 | 0.059 | 0.049 |
| intents->price | -0.040 | -0.147 | -0.001 | 0.067 | -0.004 | 0.072 | -0.132 | -0.059 | 0.076 |
| price->txns | -0.012 | 0.006 | -0.015 | 0.052 | -0.000 | 0.143 | 0.088 | -0.068 | -0.190 |
| price->active_accounts | 0.091 | 0.066 | -0.033 | -0.162 | -0.054 | 0.095 | 0.066 | 0.048 | 0.044 |
| price->fees | -0.008 | 0.028 | -0.068 | 0.096 | 0.143 | 0.252 | 0.130 | -0.053 | -0.310 |

**Result.** Mean 1–4-week lead correlation: Intents 0.015, price 0.020
(noise band ±0.201). Same-week correlation: Intents 0.167,
price 0.030.

Signal status — Intents *leads* usage: **BEAR**; Intents is a better lead than price:
**BEAR**; Intents moves *with* usage in the same week: **BEAR**.

**Reading it honestly.** If the lead correlations sit inside the noise band, the data does **not** support
"leading indicator" for either Intents or price at weekly resolution; at most Intents is a *coincident*
indicator. Combined with section 4.1 (Intents up while L1 transaction counts are down), the evidence
says Intents volume and L1 transaction counts measure different things — so "network usage" has to be
redefined (value settled, fees earned) for the thesis to hold, and that redefinition is exactly what the
bear case attacks.

## 6. Model anyone can re-run

`near_thesis/model.py`, assumptions in `assumptions.yaml`. Starting values are live (supply, stake,
inflation, tx/day, fee per tx); only growth rates are assumptions. Issuance realization (share of the
max inflation actually minted) is calibrated from the realized supply change: **1.000**.

| Scenario | Year | Tx/day | Issuance | Burn | Burn/issuance | Net inflation | Staker APR (nominal) | Staker real yield |
|---|---|---|---|---|---|---|---|---|
| bear | 0 | 690,247 | 32.77M NEAR | 0.31M NEAR | 0.9% | 2.5% | 5.0% | 2.5% |
| bear | 1 | 517,686 | 33.58M NEAR | 0.23M NEAR | 0.7% | 2.5% | 5.3% | 2.7% |
| bear | 3 | 291,198 | 35.27M NEAR | 0.13M NEAR | 0.4% | 2.5% | 5.8% | 3.2% |
| bear | 5 | 163,799 | 37.05M NEAR | 0.07M NEAR | 0.2% | 2.5% | 6.5% | 3.9% |
| base | 0 | 690,247 | 32.77M NEAR | 0.31M NEAR | 0.9% | 2.5% | 5.0% | 2.5% |
| base | 1 | 862,809 | 33.58M NEAR | 0.38M NEAR | 1.1% | 2.5% | 5.0% | 2.5% |
| base | 3 | 1,348,139 | 35.26M NEAR | 0.60M NEAR | 1.7% | 2.5% | 5.0% | 2.5% |
| base | 5 | 2,106,468 | 37.01M NEAR | 0.94M NEAR | 2.5% | 2.4% | 5.0% | 2.5% |
| bull | 0 | 690,247 | 32.77M NEAR | 0.31M NEAR | 0.9% | 2.5% | 5.0% | 2.5% |
| bull | 1 | 1,380,495 | 33.58M NEAR | 0.61M NEAR | 1.8% | 2.5% | 4.9% | 2.4% |
| bull | 3 | 5,521,979 | 35.23M NEAR | 2.45M NEAR | 7.0% | 2.3% | 4.7% | 2.3% |
| bull | 5 | 22,087,916 | 36.83M NEAR | 9.82M NEAR | 26.7% | 1.8% | 4.5% | 2.6% |

After 5 years: net inflation bear 2.5% / base 2.4% /
bull 1.8%; burn covers bear 0.2% / base 2.5% /
bull 26.7% of issuance. Even the bull case (100.0%/yr tx growth at flat fee
per tx) still leaves net inflation above zero - **on these numbers the token's case cannot rest on burn**; it rests on staking yield and on Intents value capture.

## 7. Falsifiable signals — what would change my mind

| Signal | Metric | Value | Bull if | Status | As of |
|---|---|---|---|---|---|
| NEAR Intents 30d volume is higher than a year ago | `intents_volume_30d_yoy_pct` | 126 | > 0.000 | **BULL** | 2026-11-03 |
| NEAR Intents 30d volume is growing month over month | `intents_volume_30d_mom_pct` | -13 | > 0.000 | **BEAR** | 2026-11-03 |
| Daily active accounts (30d avg) higher than a year ago | `active_accounts_30d_avg_yoy_pct` | -77 | > 0.000 | **BEAR** | 2026-11-03 |
| Daily transactions (30d avg) higher than a year ago | `txns_30d_avg_yoy_pct` | -85 | > 0.000 | **BEAR** | 2026-11-03 |
| Gas fees (NEAR-denominated, 30d) higher than a year ago | `fees_near_30d_yoy_pct` | -64 | > 0.000 | **BEAR** | 2026-11-03 |
| Fee burn offsets at least 10% of max issuance | `burn_to_issuance_pct` | 0.937 | > 10.000 | **BEAR** | 2026-11-03 |
| Stablecoin supply on NEAR higher than a year ago | `stablecoin_supply_365d_change_pct` | -45 | > 0.000 | **BEAR** | 2026-11-04 |
| DeFi TVL on NEAR higher than a year ago (USD, price-sensitive) | `tvl_yoy_pct` | 31 | > 0.000 | **BULL** | 2026-11-04 |
| At least 40% of supply is staked | `staking_ratio_pct` | 45 | > 40.000 | **BULL** | latest |
| Weekly Intents volume changes lead on-chain usage changes by 1-4 weeks (corr above noise) | `hyp_intents_lead_corr` | 0.015 | > 0.201 | **BEAR** | 2026-11-01 |
| Intents volume is a better leading indicator of usage than NEAR price | `hyp_intents_minus_price_lead_corr` | -0.005 | > 0.000 | **BEAR** | 2026-11-01 |
| Weekly Intents volume moves together with on-chain usage in the same week (corr above noise) | `hyp_intents_coincident_corr` | 0.167 | > 0.201 | **BEAR** | 2026-11-01 |

Concretely, I abandon the long thesis if, on a re-run:

- `intents_volume_30d_yoy_pct` turns negative (Intents adoption has stalled), **or**
- Intents volume keeps rising but `fees_near_30d_yoy_pct` and `burn_to_issuance_pct` stay flat for two more
  quarters (no value capture), **or**
- `staking_ratio_pct` drops below 40 (security budget eroding).

I would upgrade conviction if `burn_to_issuance_pct` passes 10, active accounts turn positive YoY, and the
lead-lag correlation rises above the noise band.

## 8. Every metric, with how it was computed

| Metric | Value | Unit | As of (UTC) | Source | How |
|---|---|---|---|---|---|
| `txns_30d_avg` | 690,247 | transactions/day | 2026-11-03 | nearblocks_charts | mean of daily `txns` over the 30 days to as_of |
| `txns_30d_avg_yoy_pct` | -85 | % | 2026-11-03 | nearblocks_charts | 30d mean of `txns` vs the same 30d window one year earlier |
| `active_accounts_30d_avg` | 62,208 | active accounts/day | 2026-11-03 | nearblocks_charts | mean of daily `active_accounts` over the 30 days to as_of |
| `active_accounts_30d_avg_yoy_pct` | -77 | % | 2026-11-03 | nearblocks_charts | 30d mean of `active_accounts` vs the same 30d window one year earlier |
| `new_accounts_30d_avg` | 9,605 | new accounts/day | 2026-11-03 | nearblocks_charts | mean of daily `new_accounts` over the 30 days to as_of |
| `new_accounts_30d_avg_yoy_pct` | -96 | % | 2026-11-03 | nearblocks_charts | 30d mean of `new_accounts` vs the same 30d window one year earlier |
| `fees_near_30d` | 36,038 | NEAR | 2026-11-03 | nearblocks_charts | sum of daily `txn_fee` (yoctoNEAR/1e24) over 30 days |
| `fees_near_30d_yoy_pct` | -64 | % | 2026-11-03 | nearblocks_charts | 30d fee sum vs same window a year earlier |
| `fees_usd_30d_nearblocks` | 176,990 | USD | 2026-11-03 | nearblocks_charts | sum of daily `txn_fee_usd` over 30 days |
| `fees_near_annualized` | 438,466 | NEAR/yr | 2026-11-03 | nearblocks_charts | 30d fee sum x 365/30 |
| `burn_near_annualized` | 306,926 | NEAR/yr | 2026-11-03 | nearblocks_charts | annualized fees x burn share 0.7 (NEAR burns 70% of gas; 30% goes to contract devs) |
| `fee_per_tx_near` | 0.002 | NEAR/tx | 2026-11-03 | nearblocks_charts | 30d fee sum / 30d tx sum |
| `supply_net_change_365d` | 31,724,286 | NEAR | 2026-11-03 | nearblocks_charts | total_supply(as_of) - total_supply(as_of - 365d) |
| `realized_net_inflation_365d_pct` | 2.480 | % | 2026-11-03 | nearblocks_charts | net 365d supply change / supply a year ago (already net of burn) |
| `burn_near_365d` | 427,489 | NEAR | 2026-11-03 | nearblocks_charts | 365d fee sum x 0.7 |
| `implied_gross_issuance_365d` | 32,151,776 | NEAR | 2026-11-03 | nearblocks_charts | net supply change + burn = what validators were minted |
| `total_supply_rpc` | 1,310,780,048 | NEAR | 2026-11-04 | rpc_block | block 223007070 header.total_supply |
| `block_height` | 223,007,070 | block | 2026-11-04 | rpc_block | latest final block |
| `max_inflation_rate_pct` | 2.500 | %/yr | latest | rpc_protocol_config | EXPERIMENTAL_protocol_config.max_inflation_rate |
| `protocol_reward_rate_pct` | 0.000 | % | latest | rpc_protocol_config | share of issuance sent to treasury (protocol_reward_rate) |
| `protocol_version` | 86 |  | latest | rpc_protocol_config | protocol_version |
| `total_staked` | 586,296,801 | NEAR | latest | rpc_validators | sum of current_validators[].stake |
| `validator_count` | 379 | validators | latest | rpc_validators | len(current_validators) |
| `staking_ratio_pct` | 45 | % | latest | rpc_validators+rpc_block | total_staked / total_supply |
| `max_gross_issuance_annual` | 32,769,501 | NEAR/yr | latest | rpc_protocol_config+rpc_block | total_supply x max_inflation_rate (upper bound; actual scales with validator uptime) |
| `staking_apr_gross_pct` | 5.589 | % | latest | rpc | issuance x (1 - protocol_reward_rate) / total_staked, before validator commission |
| `burn_to_issuance_pct` | 0.937 | % | 2026-11-03 | nearblocks_charts+rpc | annualized 30d burn / max gross issuance |
| `breakeven_tx_per_day` | 73,710,554 | tx/day | latest | nearblocks_charts+rpc | tx/day needed for burn = issuance at today's fee per tx |
| `tvl_usd` | 188457342 | USD | 2026-11-04 | llama_chain_tvl | latest DefiLlama chain TVL |
| `tvl_yoy_pct` | 31 | % | 2026-11-04 | llama_chain_tvl | TVL now vs 365d earlier |
| `llama_fees_usd_30d` | 179,384 | USD | 2026-11-03 | llama_chain_fees | DefiLlama chain gas fees, 30d sum |
| `llama_fees_usd_30d_yoy_pct` | -24 | % | 2026-11-03 | llama_chain_fees | 30d sum vs same window a year earlier |
| `llama_fees_usd_1y` | 1,198,944 | USD | 2026-11-03 | llama_chain_fees | DefiLlama total1y field |
| `llama_revenue_usd_30d` | 125,567 | USD | 2026-11-03 | llama_chain_revenue | DefiLlama burned share of fees, 30d sum |
| `llama_revenue_usd_30d_yoy_pct` | -24 | % | 2026-11-03 | llama_chain_revenue | 30d sum vs same window a year earlier |
| `llama_revenue_usd_1y` | 839,856 | USD | 2026-11-03 | llama_chain_revenue | DefiLlama total1y field |
| `stablecoin_supply_usd` | 128,753,031 | USD | 2026-11-04 | llama_stablecoins | DefiLlama totalCirculatingUSD.peggedUSD on NEAR |
| `stablecoin_supply_30d_change_pct` | 24 | % | 2026-11-04 | llama_stablecoins | stablecoin supply vs 30d earlier |
| `stablecoin_supply_365d_change_pct` | -45 | % | 2026-11-04 | llama_stablecoins | stablecoin supply vs 365d earlier |
| `stablecoin_chain_rank` | 29 | rank | latest | llama_stablecoin_chains | NEAR's rank by USD-pegged stablecoin supply among 210 chains |
| `dex_volume_near_30d` | 4,440,390,619 | USD | 2026-11-04 | llama_chain_dex | DefiLlama DEX volume attributed to NEAR chain, 30d sum (includes NEAR Intents) |
| `intents_volume_30d` | 3970607022 | USD | 2026-11-03 | llama_intents_volume | DefiLlama NEAR Intents volume, 30d sum |
| `intents_volume_30d_mom_pct` | -13 | % | 2026-11-03 | llama_intents_volume | 30d sum vs previous 30d |
| `intents_volume_30d_yoy_pct` | 126 | % | 2026-11-03 | llama_intents_volume | 30d sum vs same window a year earlier |
| `intents_volume_1y` | 32,948,150,063 | USD | 2026-11-03 | llama_intents_volume | DefiLlama total1y |
| `intents_volume_all_time` | 36,386,550,029 | USD | 2026-11-03 | llama_intents_volume | DefiLlama totalAllTime |
| `intents_first_day` | 2024-12-10 | date | 2026-11-03 | llama_intents_volume | first day with volume in DefiLlama series |
| `intents_fees_30d` | 5,777,689 | USD | 2026-11-03 | llama_intents_fees | DefiLlama NEAR Intents fees, 30d sum |
| `intents_share_of_near_dex_pct` | 89 | % | 2026-11-03 | llama | Intents 30d volume / all NEAR-chain DEX 30d volume |
| `near_price_usd` | 4.091 | USD | 2026-11-04 | price_history (CoinGecko) | last daily close |
| `near_price_365d_change_pct` | 123 | % | 2026-11-04 | price_history (CoinGecko) | price now vs ~365d earlier (nearest point within 3 days) |
| `price_crosscheck_nearblocks_diff_pct` | -0.035 | % | latest | nearblocks_stats vs price_history (CoinGecko) | NearBlocks spot price vs primary price source (data-quality check) |
| `fees_crosscheck_diff_pct` | -1.335 | % | 2026-11-03 | nearblocks_charts vs llama_chain_fees | NearBlocks 30d fee USD vs DefiLlama 30d fee USD (independent indexers; data-quality check) |
| `hyp_intents_lead_corr` | 0.015 | corr | 2026-11-01 | derived (hypothesis test) | mean corr of weekly dlog Intents volume vs usage 1-4w later, 2025-01-12..2026-11-01 |
| `hyp_price_lead_corr` | 0.020 | corr | 2026-11-01 | derived (hypothesis test) | mean corr of weekly dlog NEAR price vs usage 1-4w later, 2025-01-12..2026-11-01 |
| `hyp_intents_minus_price_lead_corr` | -0.005 | corr | 2026-11-01 | derived (hypothesis test) | Intents lead corr minus price lead corr |
| `hyp_noise_band` | 0.201 | corr | 2026-11-01 | derived (hypothesis test) | ~95% noise band 1.96/sqrt(n), n=95 weeks |
| `hyp_intents_coincident_corr` | 0.167 | corr | 2026-11-01 | derived (hypothesis test) | mean same-week corr of weekly dlog intents vs usage (txns, active accounts, fees), 2025-01-12..2026-11-01 |
| `hyp_price_coincident_corr` | 0.030 | corr | 2026-11-01 | derived (hypothesis test) | mean same-week corr of weekly dlog price vs usage (txns, active accounts, fees), 2025-01-12..2026-11-01 |
| `hyp_weeks` | 95 | weeks | 2026-11-01 | derived | weekly observations in the test |

## 9. What this does *not* measure (limits)

- **NEAR Intents Explorer API** needs a partner JWT, so per-swap data is not used. Intents volume and fees
  come from DefiLlama's adapter (https://github.com/DefiLlama/dimension-adapters/tree/master/dexs/near-intents).
- **NEAR BigQuery public dataset** is not used: it needs a GCP account and bills queries. NearBlocks'
  public daily charts are used instead; their definition of "transaction" and "active account" is NearBlocks'.
- **Validator commission** is an assumption (`assumptions.yaml`), not fetched.
- **CoinGecko free tier** returns at most 365 days; the multi-year price line and the lead-lag test use
  NearBlocks' daily `near_price` (cross-checked against the primary price source, CoinGecko: -0.0% difference today). If CoinGecko rate-limits, the build falls back to DefiLlama's coins API and says so in the source table.
- Correlation is not causation; weekly data over < 2 years is a small sample.
- This is research, not financial advice.

## 10. Sources (this build)

| Source | Endpoint | Status | Fetched (UTC) |
|---|---|---|---|
| rpc_block | https://rpc.mainnet.near.org | ok | 2026-11-04T10:54:33+00:00 |
| rpc_validators | https://rpc.mainnet.near.org | ok | 2026-11-04T10:54:33+00:00 |
| rpc_protocol_config | https://rpc.mainnet.near.org | ok | 2026-11-04T10:54:33+00:00 |
| nearblocks_charts | https://api.nearblocks.io/v1/charts | ok | 2026-11-04T10:54:33+00:00 |
| nearblocks_stats | https://api.nearblocks.io/v1/stats | ok | 2026-11-04T10:54:33+00:00 |
| llama_chain_tvl | https://api.llama.fi/v2/historicalChainTvl/Near | ok | 2026-11-04T10:54:33+00:00 |
| llama_chain_fees | https://api.llama.fi/summary/fees/near?dataType=dailyFees | ok | 2026-11-04T10:54:33+00:00 |
| llama_chain_revenue | https://api.llama.fi/summary/fees/near?dataType=dailyRevenue | ok | 2026-11-04T10:54:33+00:00 |
| llama_stablecoins | https://stablecoins.llama.fi/stablecoincharts/Near | ok | 2026-11-04T10:54:33+00:00 |
| llama_stablecoin_chains | https://stablecoins.llama.fi/stablecoinchains | ok | 2026-11-04T10:54:33+00:00 |
| llama_chain_dex | https://api.llama.fi/overview/dexs/near | ok | 2026-11-04T10:54:33+00:00 |
| llama_intents_volume | https://api.llama.fi/summary/dexs/near-intents | ok | 2026-11-04T10:54:33+00:00 |
| llama_intents_fees | https://api.llama.fi/summary/fees/near-intents?dataType=dailyFees | ok | 2026-11-04T10:54:33+00:00 |
| price_history | https://api.coingecko.com/api/v3/coins/near/market_chart?vs_currency=usd&days=365&interval=daily | ok | 2026-11-04T10:54:33+00:00 |
| intents_explorer | https://explorer.near-intents.org/api/v0/transactions | failed: HTTP 400: {"code":"Bad Request","error":{"code":"MISSING_TOKEN","message":"Missing authorization header"}} | 2026-11-04T10:54:33+00:00 |
