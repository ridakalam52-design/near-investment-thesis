# NEAR Investment Thesis — evidence first

> **This file is generated.** Every number below is filled in by `python build.py` from data the pipeline
> fetched itself (NEAR RPC, NearBlocks, DefiLlama, CoinGecko). Placeholders whose source failed print
> `n/a (source failed)` instead of a number. Edit the prose in `templates/THESIS.template.md`, never the numbers.
>
> Generated: 2026-11-14T10:25:05+00:00 UTC · Signals right now: **2 bull / 10 bear / 0 unknown** (of 12).

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
| NEAR price (CoinGecko) | $3.326 (+41.1% over 365d) | 2026-11-14 |
| NEAR Intents volume, last 30d | $3.80B (+43.8% YoY, -21.5% vs prior 30d) | DefiLlama |
| NEAR Intents volume, last 365d / all time | $32.97B / $37.78B (series starts 2024-12-10) | DefiLlama |
| NEAR Intents fees, last 30d | $5.8M | DefiLlama |
| Intents share of all DEX volume attributed to NEAR | 92.1% | DefiLlama |
| Transactions/day (30d avg) | 678,139 (-84.5% YoY) | NearBlocks |
| Active accounts/day (30d avg) | 64,822 (-75.2% YoY) | NearBlocks |
| New accounts/day (30d avg) | 9,465 (-95.6% YoY) | NearBlocks |
| Gas fees, last 30d | 29,385 NEAR ≈ $129,332 (-70.0% YoY in NEAR) | NearBlocks |
| Gas fees, last 30d (independent check) | $129,456 (NearBlocks differs by -0.1%) | DefiLlama |
| Annualized burn (70% of fees) | 250,266 NEAR | NearBlocks |
| Max annual issuance (2.5% of supply) | 32,791,911 NEAR | NEAR RPC |
| Burn as % of issuance | 0.8% | derived |
| Realized net supply growth, last 365d | 2.5% (31,736,359 NEAR) | NearBlocks |
| Total supply | 1,311,676,454 NEAR at block 224,500,918 | NEAR RPC |
| Staked / staking ratio / validators | 589,075,142 NEAR / 44.9% / 345 | NEAR RPC |
| Gross staking APR (before commission) | 5.6% | derived |
| Stablecoins on NEAR | $133.4M (+3.5% 30d, -18.9% YoY, rank #28) | DefiLlama |
| DeFi TVL | $156.7M (-10.9% YoY, USD) | DefiLlama |

Full metric table with the exact computation of each number is in section 8.

## 3. Bull case

1. **Intents volume.** NEAR Intents settled $32.97B over the last year and
   $3.80B in the last 30 days (+43.8% vs the same window a year ago).
   It is now 92.1% of all DEX volume DefiLlama attributes to NEAR — the product, not
   the L1's own DeFi, is where the volume is.
2. **Intents earns fees.** $5.8M of Intents fees in 30 days vs $129,456 of L1 gas fees
   (45.0× L1 gas). If even part of that value
   is routed back to NEAR (fees, staking demand, token-denominated settlement), the token's value capture changes.
3. **Security budget.** 44.9% of supply is staked across 345 validators;
   stakers earn ~5.0% nominal after an assumed 10.0% commission, i.e. a positive real
   yield of ~2.5% after dilution.
4. **Inflation is capped on-chain.** `max_inflation_rate` reads 2.5% straight
   from protocol config; realized net supply growth was 2.5% over the last year.
5. **Short-term liquidity.** Stablecoin supply moved +3.5% in 30 days;
   TVL is -10.9% YoY.

## 4. Bear case

1. **Raw L1 usage versus a year ago.** Transactions/day are -84.5% YoY and active accounts
   -75.2% YoY; new accounts -95.6%. Whatever drove
   last year's counts is what a re-run should explain before calling usage "growing".
2. **Fee burn versus issuance.** Burn offsets 0.8% of issuance. At today's
   fee per transaction (0.001444 NEAR) the chain would need ~88,880,939 tx/day —
   131.1× today — to stop net inflation. That is a 165.2%/yr growth rate for 5 years.
   Holders who don't stake are diluted ~2.5%/yr.
3. **Intents value does not obviously accrue to the NEAR token.** Intents fees ($5.8M/30d) are
   not NEAR gas; L1 gas fees moved -42.7% YoY in USD (DefiLlama) and -70.0%
   in NEAR terms, even while Intents volume rose. The value-capture link is the weakest part of the thesis.
4. **Stablecoin base versus a year ago.** $133.4M on NEAR, -18.9%
   YoY, rank #28 among chains — small for a chain pitching itself as a settlement layer.
5. **Intents momentum is not one-way.** The last 30 days were -21.5% vs the 30 days before.

## 5. Hypothesis test: does Intents volume lead usage better than price?

Method (`near_thesis/metrics.py::hypothesis_test`): weekly totals since Intents launched → log-differences →
Pearson correlation between the predictor in week *t* and the target in week *t+k*. Positive *k* means the
predictor moves first. 96 weekly observations; with that *n*, |corr| below ~0.200
is indistinguishable from noise (95%).

| Predictor -> target | k=-4w | k=-3w | k=-2w | k=-1w | k=+0w | k=+1w | k=+2w | k=+3w | k=+4w |
|---|---|---|---|---|---|---|---|---|---|
| intents->txns | -0.081 | 0.061 | 0.044 | -0.085 | 0.265 | 0.019 | -0.116 | 0.020 | 0.060 |
| intents->active_accounts | -0.009 | -0.016 | -0.007 | -0.039 | -0.068 | 0.089 | 0.007 | -0.015 | 0.067 |
| intents->fees | -0.076 | 0.033 | 0.062 | -0.144 | 0.301 | 0.019 | -0.121 | 0.057 | 0.050 |
| intents->price | -0.040 | -0.147 | -0.001 | 0.068 | -0.003 | 0.070 | -0.125 | -0.047 | 0.072 |
| price->txns | -0.011 | 0.031 | -0.002 | 0.054 | -0.018 | 0.131 | 0.080 | -0.064 | -0.186 |
| price->active_accounts | 0.099 | 0.108 | -0.028 | -0.160 | -0.090 | 0.067 | 0.048 | 0.052 | 0.046 |
| price->fees | -0.021 | 0.038 | 0.004 | 0.095 | 0.139 | 0.249 | 0.129 | -0.052 | -0.310 |

**Result.** Mean 1–4-week lead correlation: Intents 0.011, price 0.016
(noise band ±0.200). Same-week correlation: Intents 0.166,
price 0.010.

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
| bear | 0 | 678,139 | 32.79M NEAR | 0.25M NEAR | 0.8% | 2.5% | 5.0% | 2.5% |
| bear | 1 | 508,604 | 33.61M NEAR | 0.19M NEAR | 0.6% | 2.5% | 5.2% | 2.7% |
| bear | 3 | 286,090 | 35.30M NEAR | 0.11M NEAR | 0.3% | 2.5% | 5.8% | 3.2% |
| bear | 5 | 160,926 | 37.08M NEAR | 0.06M NEAR | 0.2% | 2.5% | 6.4% | 3.9% |
| base | 0 | 678,139 | 32.79M NEAR | 0.25M NEAR | 0.8% | 2.5% | 5.0% | 2.5% |
| base | 1 | 847,674 | 33.61M NEAR | 0.31M NEAR | 0.9% | 2.5% | 5.0% | 2.5% |
| base | 3 | 1,324,490 | 35.29M NEAR | 0.49M NEAR | 1.4% | 2.5% | 5.0% | 2.5% |
| base | 5 | 2,069,515 | 37.05M NEAR | 0.76M NEAR | 2.1% | 2.4% | 5.0% | 2.5% |
| bull | 0 | 678,139 | 32.79M NEAR | 0.25M NEAR | 0.8% | 2.5% | 5.0% | 2.5% |
| bull | 1 | 1,356,278 | 33.61M NEAR | 0.50M NEAR | 1.5% | 2.5% | 4.9% | 2.4% |
| bull | 3 | 5,425,111 | 35.27M NEAR | 2.00M NEAR | 5.7% | 2.4% | 4.7% | 2.3% |
| bull | 5 | 21,700,443 | 36.90M NEAR | 8.01M NEAR | 21.7% | 2.0% | 4.5% | 2.5% |

After 5 years: net inflation bear 2.5% / base 2.4% /
bull 2.0%; burn covers bear 0.2% / base 2.1% /
bull 21.7% of issuance. Even the bull case (100.0%/yr tx growth at flat fee
per tx) still leaves net inflation above zero - **on these numbers the token's case cannot rest on burn**; it rests on staking yield and on Intents value capture.

## 7. Falsifiable signals — what would change my mind

| Signal | Metric | Value | Bull if | Status | As of |
|---|---|---|---|---|---|
| NEAR Intents 30d volume is higher than a year ago | `intents_volume_30d_yoy_pct` | 44 | > 0.000 | **BULL** | 2026-11-13 |
| NEAR Intents 30d volume is growing month over month | `intents_volume_30d_mom_pct` | -21 | > 0.000 | **BEAR** | 2026-11-13 |
| Daily active accounts (30d avg) higher than a year ago | `active_accounts_30d_avg_yoy_pct` | -75 | > 0.000 | **BEAR** | 2026-11-13 |
| Daily transactions (30d avg) higher than a year ago | `txns_30d_avg_yoy_pct` | -85 | > 0.000 | **BEAR** | 2026-11-13 |
| Gas fees (NEAR-denominated, 30d) higher than a year ago | `fees_near_30d_yoy_pct` | -70 | > 0.000 | **BEAR** | 2026-11-13 |
| Fee burn offsets at least 10% of max issuance | `burn_to_issuance_pct` | 0.763 | > 10.000 | **BEAR** | 2026-11-13 |
| Stablecoin supply on NEAR higher than a year ago | `stablecoin_supply_365d_change_pct` | -19 | > 0.000 | **BEAR** | 2026-11-14 |
| DeFi TVL on NEAR higher than a year ago (USD, price-sensitive) | `tvl_yoy_pct` | -11 | > 0.000 | **BEAR** | 2026-11-14 |
| At least 40% of supply is staked | `staking_ratio_pct` | 45 | > 40.000 | **BULL** | latest |
| Weekly Intents volume changes lead on-chain usage changes by 1-4 weeks (corr above noise) | `hyp_intents_lead_corr` | 0.011 | > 0.200 | **BEAR** | 2026-11-08 |
| Intents volume is a better leading indicator of usage than NEAR price | `hyp_intents_minus_price_lead_corr` | -0.005 | > 0.000 | **BEAR** | 2026-11-08 |
| Weekly Intents volume moves together with on-chain usage in the same week (corr above noise) | `hyp_intents_coincident_corr` | 0.166 | > 0.200 | **BEAR** | 2026-11-08 |

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
| `txns_30d_avg` | 678,139 | transactions/day | 2026-11-13 | nearblocks_charts | mean of daily `txns` over the 30 days to as_of |
| `txns_30d_avg_yoy_pct` | -85 | % | 2026-11-13 | nearblocks_charts | 30d mean of `txns` vs the same 30d window one year earlier |
| `active_accounts_30d_avg` | 64,822 | active accounts/day | 2026-11-13 | nearblocks_charts | mean of daily `active_accounts` over the 30 days to as_of |
| `active_accounts_30d_avg_yoy_pct` | -75 | % | 2026-11-13 | nearblocks_charts | 30d mean of `active_accounts` vs the same 30d window one year earlier |
| `new_accounts_30d_avg` | 9,465 | new accounts/day | 2026-11-13 | nearblocks_charts | mean of daily `new_accounts` over the 30 days to as_of |
| `new_accounts_30d_avg_yoy_pct` | -96 | % | 2026-11-13 | nearblocks_charts | 30d mean of `new_accounts` vs the same 30d window one year earlier |
| `fees_near_30d` | 29,385 | NEAR | 2026-11-13 | nearblocks_charts | sum of daily `txn_fee` (yoctoNEAR/1e24) over 30 days |
| `fees_near_30d_yoy_pct` | -70 | % | 2026-11-13 | nearblocks_charts | 30d fee sum vs same window a year earlier |
| `fees_usd_30d_nearblocks` | 129,332 | USD | 2026-11-13 | nearblocks_charts | sum of daily `txn_fee_usd` over 30 days |
| `fees_near_annualized` | 357,522 | NEAR/yr | 2026-11-13 | nearblocks_charts | 30d fee sum x 365/30 |
| `burn_near_annualized` | 250,266 | NEAR/yr | 2026-11-13 | nearblocks_charts | annualized fees x burn share 0.7 (NEAR burns 70% of gas; 30% goes to contract devs) |
| `fee_per_tx_near` | 0.001 | NEAR/tx | 2026-11-13 | nearblocks_charts | 30d fee sum / 30d tx sum |
| `supply_net_change_365d` | 31,736,359 | NEAR | 2026-11-13 | nearblocks_charts | total_supply(as_of) - total_supply(as_of - 365d) |
| `realized_net_inflation_365d_pct` | 2.480 | % | 2026-11-13 | nearblocks_charts | net 365d supply change / supply a year ago (already net of burn) |
| `burn_near_365d` | 410,952 | NEAR | 2026-11-13 | nearblocks_charts | 365d fee sum x 0.7 |
| `implied_gross_issuance_365d` | 32,147,311 | NEAR | 2026-11-13 | nearblocks_charts | net supply change + burn = what validators were minted |
| `total_supply_rpc` | 1,311,676,454 | NEAR | 2026-11-14 | rpc_block | block 224500918 header.total_supply |
| `block_height` | 224,500,918 | block | 2026-11-14 | rpc_block | latest final block |
| `max_inflation_rate_pct` | 2.500 | %/yr | latest | rpc_protocol_config | EXPERIMENTAL_protocol_config.max_inflation_rate |
| `protocol_reward_rate_pct` | 0.000 | % | latest | rpc_protocol_config | share of issuance sent to treasury (protocol_reward_rate) |
| `protocol_version` | 88 |  | latest | rpc_protocol_config | protocol_version |
| `total_staked` | 589,075,142 | NEAR | latest | rpc_validators | sum of current_validators[].stake |
| `validator_count` | 345 | validators | latest | rpc_validators | len(current_validators) |
| `staking_ratio_pct` | 45 | % | latest | rpc_validators+rpc_block | total_staked / total_supply |
| `max_gross_issuance_annual` | 32,791,911 | NEAR/yr | latest | rpc_protocol_config+rpc_block | total_supply x max_inflation_rate (upper bound; actual scales with validator uptime) |
| `staking_apr_gross_pct` | 5.567 | % | latest | rpc | issuance x (1 - protocol_reward_rate) / total_staked, before validator commission |
| `burn_to_issuance_pct` | 0.763 | % | 2026-11-13 | nearblocks_charts+rpc | annualized 30d burn / max gross issuance |
| `breakeven_tx_per_day` | 88,880,939 | tx/day | latest | nearblocks_charts+rpc | tx/day needed for burn = issuance at today's fee per tx |
| `tvl_usd` | 156679848 | USD | 2026-11-14 | llama_chain_tvl | latest DefiLlama chain TVL |
| `tvl_yoy_pct` | -11 | % | 2026-11-14 | llama_chain_tvl | TVL now vs 365d earlier |
| `llama_fees_usd_30d` | 129,456 | USD | 2026-11-13 | llama_chain_fees | DefiLlama chain gas fees, 30d sum |
| `llama_fees_usd_30d_yoy_pct` | -43 | % | 2026-11-13 | llama_chain_fees | 30d sum vs same window a year earlier |
| `llama_fees_usd_1y` | 1,150,300 | USD | 2026-11-13 | llama_chain_fees | DefiLlama total1y field |
| `llama_revenue_usd_30d` | 90,620 | USD | 2026-11-13 | llama_chain_revenue | DefiLlama burned share of fees, 30d sum |
| `llama_revenue_usd_30d_yoy_pct` | -43 | % | 2026-11-13 | llama_chain_revenue | 30d sum vs same window a year earlier |
| `llama_revenue_usd_1y` | 805,807 | USD | 2026-11-13 | llama_chain_revenue | DefiLlama total1y field |
| `stablecoin_supply_usd` | 133,383,698 | USD | 2026-11-14 | llama_stablecoins | DefiLlama totalCirculatingUSD.peggedUSD on NEAR |
| `stablecoin_supply_30d_change_pct` | 3.502 | % | 2026-11-14 | llama_stablecoins | stablecoin supply vs 30d earlier |
| `stablecoin_supply_365d_change_pct` | -19 | % | 2026-11-14 | llama_stablecoins | stablecoin supply vs 365d earlier |
| `stablecoin_chain_rank` | 28 | rank | latest | llama_stablecoin_chains | NEAR's rank by USD-pegged stablecoin supply among 215 chains |
| `dex_volume_near_30d` | 4,121,021,072 | USD | 2026-11-14 | llama_chain_dex | DefiLlama DEX volume attributed to NEAR chain, 30d sum (includes NEAR Intents) |
| `intents_volume_30d` | 3797462047 | USD | 2026-11-13 | llama_intents_volume | DefiLlama NEAR Intents volume, 30d sum |
| `intents_volume_30d_mom_pct` | -21 | % | 2026-11-13 | llama_intents_volume | 30d sum vs previous 30d |
| `intents_volume_30d_yoy_pct` | 44 | % | 2026-11-13 | llama_intents_volume | 30d sum vs same window a year earlier |
| `intents_volume_1y` | 32,969,281,080 | USD | 2026-11-13 | llama_intents_volume | DefiLlama total1y |
| `intents_volume_all_time` | 37,782,828,302 | USD | 2026-11-13 | llama_intents_volume | DefiLlama totalAllTime |
| `intents_first_day` | 2024-12-10 | date | 2026-11-13 | llama_intents_volume | first day with volume in DefiLlama series |
| `intents_fees_30d` | 5,831,933 | USD | 2026-11-13 | llama_intents_fees | DefiLlama NEAR Intents fees, 30d sum |
| `intents_share_of_near_dex_pct` | 92 | % | 2026-11-13 | llama | Intents 30d volume / all NEAR-chain DEX 30d volume |
| `near_price_usd` | 3.326 | USD | 2026-11-14 | price_history (CoinGecko) | last daily close |
| `near_price_365d_change_pct` | 41 | % | 2026-11-14 | price_history (CoinGecko) | price now vs ~365d earlier (nearest point within 3 days) |
| `price_crosscheck_nearblocks_diff_pct` | 0.124 | % | latest | nearblocks_stats vs price_history (CoinGecko) | NearBlocks spot price vs primary price source (data-quality check) |
| `fees_crosscheck_diff_pct` | -0.096 | % | 2026-11-13 | nearblocks_charts vs llama_chain_fees | NearBlocks 30d fee USD vs DefiLlama 30d fee USD (independent indexers; data-quality check) |
| `hyp_intents_lead_corr` | 0.011 | corr | 2026-11-08 | derived (hypothesis test) | mean corr of weekly dlog Intents volume vs usage 1-4w later, 2025-01-12..2026-11-08 |
| `hyp_price_lead_corr` | 0.016 | corr | 2026-11-08 | derived (hypothesis test) | mean corr of weekly dlog NEAR price vs usage 1-4w later, 2025-01-12..2026-11-08 |
| `hyp_intents_minus_price_lead_corr` | -0.005 | corr | 2026-11-08 | derived (hypothesis test) | Intents lead corr minus price lead corr |
| `hyp_noise_band` | 0.200 | corr | 2026-11-08 | derived (hypothesis test) | ~95% noise band 1.96/sqrt(n), n=96 weeks |
| `hyp_intents_coincident_corr` | 0.166 | corr | 2026-11-08 | derived (hypothesis test) | mean same-week corr of weekly dlog intents vs usage (txns, active accounts, fees), 2025-01-12..2026-11-08 |
| `hyp_price_coincident_corr` | 0.010 | corr | 2026-11-08 | derived (hypothesis test) | mean same-week corr of weekly dlog price vs usage (txns, active accounts, fees), 2025-01-12..2026-11-08 |
| `hyp_weeks` | 96 | weeks | 2026-11-08 | derived | weekly observations in the test |

## 9. What this does *not* measure (limits)

- **NEAR Intents Explorer API** needs a partner JWT, so per-swap data is not used. Intents volume and fees
  come from DefiLlama's adapter (https://github.com/DefiLlama/dimension-adapters/tree/master/dexs/near-intents).
- **NEAR BigQuery public dataset** is not used: it needs a GCP account and bills queries. NearBlocks'
  public daily charts are used instead; their definition of "transaction" and "active account" is NearBlocks'.
- **Validator commission** is an assumption (`assumptions.yaml`), not fetched.
- **CoinGecko free tier** returns at most 365 days; the multi-year price line and the lead-lag test use
  NearBlocks' daily `near_price` (cross-checked against the primary price source, CoinGecko: +0.1% difference today). If CoinGecko rate-limits, the build falls back to DefiLlama's coins API and says so in the source table.
- Correlation is not causation; weekly data over < 2 years is a small sample.
- This is research, not financial advice.

## 10. Sources (this build)

| Source | Endpoint | Status | Fetched (UTC) |
|---|---|---|---|
| rpc_block | https://rpc.mainnet.near.org | ok | 2026-11-14T10:24:50+00:00 |
| rpc_validators | https://rpc.mainnet.near.org | ok | 2026-11-14T10:24:50+00:00 |
| rpc_protocol_config | https://rpc.mainnet.near.org | ok | 2026-11-14T10:24:50+00:00 |
| nearblocks_charts | https://api.nearblocks.io/v1/charts | ok | 2026-11-14T10:24:50+00:00 |
| nearblocks_stats | https://api.nearblocks.io/v1/stats | ok | 2026-11-14T10:24:50+00:00 |
| llama_chain_tvl | https://api.llama.fi/v2/historicalChainTvl/Near | ok | 2026-11-14T10:24:50+00:00 |
| llama_chain_fees | https://api.llama.fi/summary/fees/near?dataType=dailyFees | ok | 2026-11-14T10:24:50+00:00 |
| llama_chain_revenue | https://api.llama.fi/summary/fees/near?dataType=dailyRevenue | ok | 2026-11-14T10:24:50+00:00 |
| llama_stablecoins | https://stablecoins.llama.fi/stablecoincharts/Near | ok | 2026-11-14T10:24:50+00:00 |
| llama_stablecoin_chains | https://stablecoins.llama.fi/stablecoinchains | ok | 2026-11-14T10:24:50+00:00 |
| llama_chain_dex | https://api.llama.fi/overview/dexs/near | ok | 2026-11-14T10:24:50+00:00 |
| llama_intents_volume | https://api.llama.fi/summary/dexs/near-intents | ok | 2026-11-14T10:24:50+00:00 |
| llama_intents_fees | https://api.llama.fi/summary/fees/near-intents?dataType=dailyFees | ok | 2026-11-14T10:24:50+00:00 |
| price_history | https://api.coingecko.com/api/v3/coins/near/market_chart?vs_currency=usd&days=365&interval=daily | ok | 2026-11-14T10:24:50+00:00 |
| intents_explorer | https://explorer.near-intents.org/api/v0/transactions | failed: HTTP 400: {"code":"Bad Request","error":{"code":"MISSING_TOKEN","message":"Missing authorization header"}} | 2026-11-14T10:24:50+00:00 |
