"""Explicit Gann-inspired benchmark and option revaluation stress.

The fan rule is a scale-defined research hypothesis, not a validated Gann edge.
"""
from pathlib import Path
import argparse,csv,hashlib,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pricing import greeks
from strategy_core.engine import validate,account,metrics,walk_forward


def fan_weights(prices,slope=1.,lookback=63):
    prices=validate(prices)
    if slope<=0 or lookback<3:raise ValueError('positive slope and adequate window required')
    weights=np.zeros_like(prices)
    for t in range(lookback+1,len(prices)):
        window=prices[t-lookback-1:t-1]
        anchor=np.argmin(window,axis=0);unit=np.std(np.diff(window,axis=0),axis=0,ddof=1)
        line=window[anchor,np.arange(window.shape[1])]+slope*unit*(lookback-1-anchor)
        signal=(window[-1]>line).astype(float)
        if signal.sum():weights[t]=signal/signal.sum()
    return weights


def stress():
    base=greeks(100,100,.25,.02,.25);rows=[]
    for ds in [-20,-10,0,10,20]:
        for dv in [-.1,0,.1,.2]:
            exact=greeks(100+ds,100,.25,.02,.25+dv)['price']-base['price']
            approx=base['delta']*ds+.5*base['gamma']*ds*ds+base['vega']*dv
            rows.append({'spot_change':ds,'vol_change':dv,'exact_pnl':exact,'greek_approximation':approx,'residual':exact-approx})
    return rows


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--prices');args=parser.parse_args()
    if args.prices:
        file=Path(args.prices);rows=list(csv.DictReader(file.open()));valid=[r for r in rows if r.get('DLF.NS')];assert all(a['Date']<b['Date'] for a,b in zip(valid,valid[1:]));prices=np.array([[float(r['DLF.NS'])] for r in valid]);mode='historical'
        source={'name':'Yahoo Finance adjusted DLF closes','url':'https://finance.yahoo.com/quote/DLF.NS/history/','access_date':'2026-10-24','sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
    else:
        rng=np.random.default_rng(20261024);prices=100*np.exp(np.cumsum(rng.normal(.0002,.015,(1200,1)),axis=0));mode='synthetic';source={'name':'Seeded geometric paths','url':'https://github.com/Anjaney336/derivatives-hedging-research/blob/main/strategy_experiments.py','access_date':'2026-10-24','seed':20261024}
    out=Path(__file__).parent/'results/strategy'/mode;out.mkdir(parents=True,exist_ok=True);start=505;rules={}
    selected,_=walk_forward(prices);rules['rolling_nine_rule_selection']=selected
    for slope in [.5,1,2]:rules[f'fan_slope_{slope}']=fan_weights(prices,slope)
    buyhold=np.zeros_like(prices);buyhold[start:]=1;rules['buy_hold']=buyhold
    results={};series={};fig,ax=plt.subplots(figsize=(10,4.5))
    for name,weights in rules.items():
        weights[:start]=0;r=account(prices,weights)['returns'][start:];results[name]=metrics(r);series[name]=r;ax.plot(np.cumprod(1+r),label=name)
    with (out/'returns.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(series);writer.writerows(zip(*series.values()))
    report={'source':source,'results':results,'cost_bps':10,'assumptions':'Fan anchored at trailing 63-observation low through t-2; slope in trailing standard-deviation-of-price-change units per bar. Equal allocation to positive signals, no shorts. Slopes .5/1/2 reported without selecting a winner.','reference':{'name':'TradingView Gann fan definition','url':'https://www.tradingview.com/support/solutions/43000518151-gann-fan-drawing-tool/','access_date':'2026-10-24'},'limitations':'Our normalized fan is an explicit experimental variant, not a uniquely canonical Gann implementation. Same historical sample previously inspected. Equity benchmark P&L is distinct from model-priced option hedge results. No empirical options alpha inferred.'}
    (out/'summary.json').write_text(json.dumps(report,indent=2));ax.set(title='Underlying direction experiments — all specified variants disclosed',xlabel='Evaluation observation',ylabel='Growth of 1 after assumed costs');ax.legend(fontsize=8);fig.tight_layout();fig.savefig(out/'strategies.svg');plt.close(fig)
    grid=stress();dest=Path(__file__).parent/'results';
    with (dest/'greek_stress.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=grid[0]);w.writeheader();w.writerows(grid)
    fig,axes=plt.subplots(1,2,figsize=(10,4));values=np.array([r['exact_pnl'] for r in grid]).reshape(5,4);residual=np.array([r['residual'] for r in grid]).reshape(5,4)
    for ax,mat,title in zip(axes,[values,residual],['Exact option revaluation','Taylor residual (cross/higher orders)']):
        im=ax.imshow(mat,origin='lower',aspect='auto',cmap='RdBu');ax.set(xticks=range(4),xticklabels=['−10','0','+10','+20'],yticks=range(5),yticklabels=['−20','−10','0','+10','+20'],xlabel='Volatility shock (percentage points)',ylabel='Spot shock',title=title);fig.colorbar(im,ax=ax)
    fig.tight_layout();fig.savefig(dest/'greek_stress.svg');plt.close(fig);print(json.dumps(results,indent=2))

if __name__=='__main__':main()
