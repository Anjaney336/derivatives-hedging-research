# Derivatives & Systematic Risk Research — calculation and decision guide

How much hedge error remains after controlling delta and gamma, and what does the hedge cost?

## Price and measure exposure

Use the pricing model to compute sensitivities, then compare exact spot/volatility repricing with the local delta-gamma-vega approximation. Large shocks expose higher-order and cross-risk.

## Hedge with explicit constraints

An option offsets gamma and stock offsets residual delta. Hedge-option positions are capped near unstable gamma denominators. Fees, discrete rebalancing and jump paths are retained.

## Compare error and cost

In the simulated diffusion case, hedge RMSE falls from about 0.615 to 0.249 model currency units with delta-gamma hedging, while mean fees rise from 0.176 to 0.198. These are model-based risk/cost trade-offs, not tradable option-chain results.

## Keep directional experiments separate

The Gann-inspired fan is a documented scaled rule, tested alongside a chronological rule selector and buy-and-hold. All fan variants underperform buy-and-hold in this sample; they are not a validated forecasting method.

## Calculation

Hedge-option units = −target gamma / hedge-option gamma (capped); stock units offset residual delta. Approximate ΔV = delta·ΔS + ½gamma·(ΔS)² + vega·Δσ.

## Graph interpretation

### Delta/gamma hedge distributions

Compare hedge-error distributions across diffusion and jump paths, then inspect fees in the downloadable summary. A narrower distribution is a hedging result, not a profitable trading signal. Calls are model-priced and fills are theoretical.

### Exact revaluation and Greek residuals

Exact revaluation is the benchmark for the local Greek approximation. Residuals grow when shocks leave the local neighbourhood; the omitted terms include cross sensitivities and higher orders. Volatility shocks are absolute changes in annualised volatility.

### Underlying strategy comparison

All specified fan slopes are shown, including poor performers. The experiment trades the underlying, not an option contract. Buy-and-hold wins in this sample, so the evidence does not support a Gann alpha claim.

## Review evidence

pricing.py · gamma_hedge.py · strategy_experiments.py · results/gamma_summary.json · results/greek_stress.csv

Demonstrates: Options risk, hedging trade-offs, numerical validation and disciplined hypothesis rejection.

All values are existing recorded outputs. No new performance experiment was run for this presentation update. Refer to the README and result JSON for data sources, access dates, units and limitations.
