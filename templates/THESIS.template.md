# NEAR Investment Thesis — evidence first

> **This file is generated.** Every number below is filled in by `python build.py` from data the pipeline
> fetched itself (NEAR RPC, NearBlocks, DefiLlama, CoinGecko). Placeholders whose source failed print
> `n/a (source failed)` instead of a number. Edit the prose in `templates/THESIS.template.md`, never the numbers.
>
> Generated: {{generated_at}} UTC · Signals right now: **{{n_bull}} bull / {{n_bear}} bear / {{n_unknown}} unknown** (of {{n_signals}}).

## 1. The claim

**Long-term thesis:** NEAR's value is shifting from *being a busy L1* to *being the settlement and
coordination layer for cross-chain intents (NEAR Intents) and AI agents*. If that is right, the metric
that matters is value settled through NEAR Intents, not raw transaction counts — and over time that
value has to show up in on-chain fees, stablecoin liquidity and a shrinking net inflation.

**Working hypothesis tested here (from the track prompt):** *cross-chain volume through NEAR Intents is a
better leading indicator of real network usage than token price.*

**Investment framing:** NEAR is held for its staking yield and for exposure to Intents/agent adoption.
The thesis is *wrong* if Intents growth stalls, or if it never feeds back into fees and burn, leaving
holders with ~{{max_inflation_rate_pct:pct}} dilution and nothing to offset it.

## 2. Evidence snapshot

| What | Value | As of (UTC) |
|---|---|---|
| NEAR price ({{price_src}}) | ${{near_price_usd:float}} ({{near_price_365d_change_pct:spct}} over 365d) | {{price_asof}} |
| NEAR Intents volume, last 30d | {{intents_volume_30d:usdb}} ({{intents_volume_30d_yoy_pct:spct}} YoY, {{intents_volume_30d_mom_pct:spct}} vs prior 30d) | DefiLlama |
| NEAR Intents volume, last 365d / all time | {{intents_volume_1y:usdb}} / {{intents_volume_all_time:usdb}} (series starts {{intents_first_day}}) | DefiLlama |
| NEAR Intents fees, last 30d | {{intents_fees_30d:usdm}} | DefiLlama |
| Intents share of all DEX volume attributed to NEAR | {{intents_share_of_near_dex_pct:pct}} | DefiLlama |
| Transactions/day (30d avg) | {{txns_30d_avg:int}} ({{txns_30d_avg_yoy_pct:spct}} YoY) | NearBlocks |
| Active accounts/day (30d avg) | {{active_accounts_30d_avg:int}} ({{active_accounts_30d_avg_yoy_pct:spct}} YoY) | NearBlocks |
| New accounts/day (30d avg) | {{new_accounts_30d_avg:int}} ({{new_accounts_30d_avg_yoy_pct:spct}} YoY) | NearBlocks |
| Gas fees, last 30d | {{fees_near_30d:near}} ≈ {{fees_usd_30d_nearblocks:usd}} ({{fees_near_30d_yoy_pct:spct}} YoY in NEAR) | NearBlocks |
| Gas fees, last 30d (independent check) | {{llama_fees_usd_30d:usd}} (NearBlocks differs by {{fees_crosscheck_diff_pct:spct}}) | DefiLlama |
| Annualized burn (70% of fees) | {{burn_near_annualized:near}} | NearBlocks |
| Max annual issuance ({{max_inflation_rate_pct:pct}} of supply) | {{max_gross_issuance_annual:near}} | NEAR RPC |
| Burn as % of issuance | {{burn_to_issuance_pct:pct}} | derived |
| Realized net supply growth, last 365d | {{realized_net_inflation_365d_pct:pct}} ({{supply_net_change_365d:near}}) | NearBlocks |
| Total supply | {{total_supply_rpc:near}} at block {{block_height:int}} | NEAR RPC |
| Staked / staking ratio / validators | {{total_staked:near}} / {{staking_ratio_pct:pct}} / {{validator_count:int}} | NEAR RPC |
| Gross staking APR (before commission) | {{staking_apr_gross_pct:pct}} | derived |
| Stablecoins on NEAR | {{stablecoin_supply_usd:usdm}} ({{stablecoin_supply_30d_change_pct:spct}} 30d, {{stablecoin_supply_365d_change_pct:spct}} YoY, rank #{{stablecoin_chain_rank}}) | DefiLlama |
| DeFi TVL | {{tvl_usd:usdm}} ({{tvl_yoy_pct:spct}} YoY, USD) | DefiLlama |

Full metric table with the exact computation of each number is in section 8.

## 3. Bull case

1. **Intents volume.** NEAR Intents settled {{intents_volume_1y:usdb}} over the last year and
   {{intents_volume_30d:usdb}} in the last 30 days ({{intents_volume_30d_yoy_pct:spct}} vs the same window a year ago).
   It is now {{intents_share_of_near_dex_pct:pct}} of all DEX volume DefiLlama attributes to NEAR — the product, not
   the L1's own DeFi, is where the volume is.
2. **Intents earns fees.** {{intents_fees_30d:usdm}} of Intents fees in 30 days vs {{llama_fees_usd_30d:usd}} of L1 gas fees
   ({{intents_fee_multiple:x1}} L1 gas). If even part of that value
   is routed back to NEAR (fees, staking demand, token-denominated settlement), the token's value capture changes.
3. **Security budget.** {{staking_ratio_pct:pct}} of supply is staked across {{validator_count:int}} validators;
   stakers earn ~{{y0_nominal_apr:pct}} nominal after an assumed {{commission:pct}} commission, i.e. a positive real
   yield of ~{{y0_real_yield:pct}} after dilution.
4. **Inflation is capped on-chain.** `max_inflation_rate` reads {{max_inflation_rate_pct:pct}} straight
   from protocol config; realized net supply growth was {{realized_net_inflation_365d_pct:pct}} over the last year.
5. **Short-term liquidity.** Stablecoin supply moved {{stablecoin_supply_30d_change_pct:spct}} in 30 days;
   TVL is {{tvl_yoy_pct:spct}} YoY.

## 4. Bear case

1. **Raw L1 usage versus a year ago.** Transactions/day are {{txns_30d_avg_yoy_pct:spct}} YoY and active accounts
   {{active_accounts_30d_avg_yoy_pct:spct}} YoY; new accounts {{new_accounts_30d_avg_yoy_pct:spct}}. Whatever drove
   last year's counts is what a re-run should explain before calling usage "growing".
2. **Fee burn versus issuance.** Burn offsets {{burn_to_issuance_pct:pct}} of issuance. At today's
   fee per transaction ({{fee_per_tx_near:small}} NEAR) the chain would need ~{{breakeven_tx_per_day:int}} tx/day —
   {{be_multiple:x1}} today — to stop net inflation. That is a {{be_cagr:pct}}/yr growth rate for {{be_years}} years.
   Holders who don't stake are diluted ~{{realized_net_inflation_365d_pct:pct}}/yr.
3. **Intents value does not obviously accrue to the NEAR token.** Intents fees ({{intents_fees_30d:usdm}}/30d) are
   not NEAR gas; L1 gas fees moved {{llama_fees_usd_30d_yoy_pct:spct}} YoY in USD (DefiLlama) and {{fees_near_30d_yoy_pct:spct}}
   in NEAR terms, even while Intents volume rose. The value-capture link is the weakest part of the thesis.
4. **Stablecoin base versus a year ago.** {{stablecoin_supply_usd:usdm}} on NEAR, {{stablecoin_supply_365d_change_pct:spct}}
   YoY, rank #{{stablecoin_chain_rank}} among chains — small for a chain pitching itself as a settlement layer.
5. **Intents momentum is not one-way.** The last 30 days were {{intents_volume_30d_mom_pct:spct}} vs the 30 days before.

## 5. Hypothesis test: does Intents volume lead usage better than price?

Method (`near_thesis/metrics.py::hypothesis_test`): weekly totals since Intents launched → log-differences →
Pearson correlation between the predictor in week *t* and the target in week *t+k*. Positive *k* means the
predictor moves first. {{hyp_weeks}} weekly observations; with that *n*, |corr| below ~{{hyp_noise_band:float}}
is indistinguishable from noise (95%).

{{TABLE:hypothesis}}

**Result.** Mean 1–4-week lead correlation: Intents {{hyp_intents_lead_corr:float}}, price {{hyp_price_lead_corr:float}}
(noise band ±{{hyp_noise_band:float}}). Same-week correlation: Intents {{hyp_intents_coincident_corr:float}},
price {{hyp_price_coincident_corr:float}}.

Signal status — Intents *leads* usage: **{{sig_intents_leads_usage}}**; Intents is a better lead than price:
**{{sig_intents_beats_price}}**; Intents moves *with* usage in the same week: **{{sig_intents_coincident_usage}}**.

**Reading it honestly.** If the lead correlations sit inside the noise band, the data does **not** support
"leading indicator" for either Intents or price at weekly resolution; at most Intents is a *coincident*
indicator. Combined with section 4.1 (Intents up while L1 transaction counts are down), the evidence
says Intents volume and L1 transaction counts measure different things — so "network usage" has to be
redefined (value settled, fees earned) for the thesis to hold, and that redefinition is exactly what the
bear case attacks.

## 6. Model anyone can re-run

`near_thesis/model.py`, assumptions in `assumptions.yaml`. Starting values are live (supply, stake,
inflation, tx/day, fee per tx); only growth rates are assumptions. Issuance realization (share of the
max inflation actually minted) is calibrated from the realized supply change: **{{realization:float}}**.

{{TABLE:model}}

After {{be_years}} years: net inflation bear {{bear_final_net_infl:pct}} / base {{base_final_net_infl:pct}} /
bull {{bull_final_net_infl:pct}}; burn covers bear {{bear_final_burn_ratio:pct}} / base {{base_final_burn_ratio:pct}} /
bull {{bull_final_burn_ratio:pct}} of issuance. Even the bull case ({{bull_tx_growth:pct}}/yr tx growth at flat fee
per tx) {{bull_zero_text}}

## 7. Falsifiable signals — what would change my mind

{{TABLE:signals}}

Concretely, I abandon the long thesis if, on a re-run:

- `intents_volume_30d_yoy_pct` turns negative (Intents adoption has stalled), **or**
- Intents volume keeps rising but `fees_near_30d_yoy_pct` and `burn_to_issuance_pct` stay flat for two more
  quarters (no value capture), **or**
- `staking_ratio_pct` drops below 40 (security budget eroding).

I would upgrade conviction if `burn_to_issuance_pct` passes 10, active accounts turn positive YoY, and the
lead-lag correlation rises above the noise band.

## 8. Every metric, with how it was computed

{{TABLE:headline}}

## 9. What this does *not* measure (limits)

- **NEAR Intents Explorer API** needs a partner JWT, so per-swap data is not used. Intents volume and fees
  come from DefiLlama's adapter (https://github.com/DefiLlama/dimension-adapters/tree/master/dexs/near-intents).
- **NEAR BigQuery public dataset** is not used: it needs a GCP account and bills queries. NearBlocks'
  public daily charts are used instead; their definition of "transaction" and "active account" is NearBlocks'.
- **Validator commission** is an assumption (`assumptions.yaml`), not fetched.
- **CoinGecko free tier** returns at most 365 days; the multi-year price line and the lead-lag test use
  NearBlocks' daily `near_price` (cross-checked against the primary price source, {{price_src}}: {{price_crosscheck_nearblocks_diff_pct:spct}} difference today). If CoinGecko rate-limits, the build falls back to DefiLlama's coins API and says so in the source table.
- Correlation is not causation; weekly data over < 2 years is a small sample.
- This is research, not financial advice.

## 10. Sources (this build)

{{TABLE:sources}}
