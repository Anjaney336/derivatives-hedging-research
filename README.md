# Derivatives & Systematic Risk Research

[Open the research dashboard](https://anjaney336.github.io/portfolio/research/derivatives-hedging-research/) · [Earlier component methodology](docs/PRE_CONSOLIDATION.md)

## Research question and scope
Combines the derivatives hedging engine with the causal strategy research kernel. Option-risk experiments and underlying-direction experiments share accounting conventions but keep their P&L and assumptions separate.

## Results
The specified Gann-inspired fan variants all underperform DLF buy-and-hold in this retrospective test. Delta/gamma hedging reduces simulated hedge error under its pricing assumptions. Neither result establishes an executable options edge.

## Calculation conventions
Gamma hedge = −target gamma / hedge-option gamma, subject to position limits; stock offsets remaining delta. Exact spot/volatility repricing is compared with delta + half gamma + vega approximation. The fan line uses a trailing low and explicitly scaled price-change standard deviations per bar, observed through t−2.

## Data and sources
Seeded synthetic option paths plus vendor-adjusted DLF closes accessed 24 October 2026. Gann drawing reference: TradingView support; this normalized rule is our documented variant. Sources and hashes in result JSON.

## Reproduce
Python 3.12. Install `requirements.txt`, then run `python reproduce.py`. Default tests/research run offline; historical runs need the local authorized cache. New entry point: `strategy_experiments.py`. Add `--prices /path/to/prices.csv` for historical strategy/derivative experiments.

## Verification
37 tests across the consolidated reproduction command. CI runs the same command. See ENGINEERING.md for boundaries and release checks. The dashboard displays bundled reports; change its view selector to compare analyses, and download CSV/JSON evidence.

## Limits
Gann fan settings are one explicit experimental definition, not a canonical or validated predictive rule. Options are model-priced, with assumed liquidity and no real chain. Taylor residuals include cross and higher-order risk.

## Lineage and authorship
Consolidates existing research modules; original repositories remain as history. This is AI-assisted portfolio research, not code represented as deployed at a financial institution.

## Greek coverage and cost-inclusive hedge audit

[Full coverage, results and limitations](GREEKS_AND_HEDGING.md). All five Greeks and IV inversion are implemented; dynamic hedging covers delta/gamma. New paired simulations include the target entry fee and financing. 37 tests pass; 360 numerical Greek comparisons pass. Lower RMSE does not imply positive P&L or better downside protection.
