# Option Greeks and hedging audit

## Coverage

| Component | Implemented and checked | Boundary |
|---|---|---|
| Delta, gamma | Analytical call/put Greeks; finite-difference grid; dynamic stock/option hedging | Discrete, same-close model fills |
| Vega | Analytical sensitivity; numerical grid; spot/volatility repricing stress | No dynamic vega-neutral portfolio or calibrated surface |
| Theta | Analytical time decay; numerical grid; Taylor P&L attribution | Model clock uses 252 days/year; not actual expiry calendars |
| Rho | Analytical rate sensitivity; numerical grid | No dynamic rate hedge |
| Implied volatility | Bracketed inversion and round-trip tests | No historical chain calibration |
| Costs and financing | Stock/hedge-option fees; target entry fee and its financing in new audit | No margin, borrow charges, taxes or empirical bid/ask |

Greek units: delta per spot unit; gamma per spot unit squared; internal vega/rho per 1.0 absolute volatility/rate change, displayed per 0.01; theta internally per year, displayed per 1/252 year. Long European calls/puts, no dividends. The five-Greek numerical audit contains 72 input combinations and 360 comparisons; this is not 360 independent test functions. Maximum scaled error is below 3.51e-7 using absolute error divided by max(1, absolute analytical value).

## Paired cost-inclusive simulation

Run `python greek_audit.py`, or `python reproduce.py` for the full suite. 37 tests pass. Seeds 2000–2149 are reused across two policies in each of two regimes: 300 distinct paths, 600 policy evaluations. No new policy selection is performed. The 2,000-resample bootstrap resamples paired path indices; confidence intervals are conditional on this synthetic simulator, not market evidence.

Long one financed ATM call on normalised spot 100, 63 observations to expiry. Assumed pricing volatility 25%, financing 2%, stock trading 5bp, hedge-option trading 20bp and target-option entry 20bp. Terminal target settles without a fee; the longer-dated hedge option is liquidated. Target entry fees and their financing are added in the new audit; older `gamma_summary.json` intentionally retains its original cost convention.

| Regime | Policy | Terminal RMSE | Mean P&L | Mean fees | Worst 5% mean P&L |
|---|---|---:|---:|---:|---:|
| diffusion | delta | 0.6191 | -0.2685 | 0.1860 | -1.5003 |
| diffusion | delta_gamma | 0.2571 | -0.2102 | 0.2083 | -0.6032 |
| jump | delta | 2.4904 | 1.5075 | 0.1858 | -0.7953 |
| jump | delta_gamma | 0.5450 | -0.2691 | 0.2247 | -1.5564 |

All values are model currency units per target option, not annualised returns or account Sharpe ratios. Lower RMSE is not a profit signal: delta-gamma mean P&L is negative in both regimes. Jump-regime lower-tail P&L is worse despite lower RMSE. Under diffusion all 150 delta-gamma trials lose money after costs. That is visible evidence of the hedging cost, not a result to hide.

95% paired-bootstrap intervals for RMSE(delta-gamma) minus RMSE(delta): diffusion −0.4301 to −0.2917; jump −2.3793 to −1.5051. These do not quantify real-market execution uncertainty.

## Quant-trader interpretation

Explain exposure before the hedge, position sizing, residual risk after caps, financing, transaction costs and lower-tail behaviour. Gamma neutrality does not imply vega neutrality when option maturities differ. The useful contribution is a reproducible risk/cost comparison, not a claim to profitable derivatives trading. Gann remains a separate underlying-only hypothesis test.

This is a synthetic hedging backtest. Existing historical-underlying replays use hypothetical options and must not be called historical option-chain backtests. Real-chain validation would require dated contract identifiers, strikes, expiries, bid/ask, calendar conventions, dividends, financing and liquidity evidence. None is fabricated here.

## Sources and evidence

- Synthetic generator: https://github.com/Anjaney336/derivatives-hedging-research/blob/main/hedging.py — generated/accessed 24 October 2026. Seeds and assumptions in results/greek_audit.json.
- Greek definitions: https://prd-web.optionseducation.org/advancedconcepts/understanding-options-greeks — accessed 24 October 2026. Educational reference, not a source of market prices.
- Code: greek_audit.py, pricing.py, gamma_hedge.py and test_greek_audit.py.
- Evidence: results/greek_validation.csv, results/all_in_hedge_trials.csv and results/greek_audit.json. Input provenance and output hashes are recorded in JSON.
