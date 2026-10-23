"""Numerical Greek validation and all-in paired hedge diagnostics; synthetic only."""
from pathlib import Path
import csv, json, math, hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pricing import greeks
from hedging import path
from gamma_hedge import simulate

ROOT=Path(__file__).parent

def numerical(s,k,t,r,v,kind):
    price=lambda a,b,c,d:greeks(a,k,b,c,d,kind)['price']
    hs=s*1e-4; h=1e-5
    return dict(delta=(price(s+hs,t,r,v)-price(s-hs,t,r,v))/(2*hs),
        gamma=(price(s+hs,t,r,v)-2*price(s,t,r,v)+price(s-hs,t,r,v))/hs**2,
        vega=(price(s,t,r,v+h)-price(s,t,r,v-h))/(2*h),
        theta=-(price(s,t+h,r,v)-price(s,t-h,r,v))/(2*h),
        rho=(price(s,t,r+h,v)-price(s,t,r-h,v))/(2*h))

def audit_rows():
    rows=[]
    for kind in ['call','put']:
        for spot in [80,100,120]:
            for days in [5,21,63,252]:
                for vol in [.15,.25,.5]:
                    a=greeks(spot,100,days/252,.02,vol,kind);b=numerical(spot,100,days/252,.02,vol,kind)
                    for key in b:
                        rows.append(dict(kind=kind,spot=spot,days=days,vol=vol,greek=key,analytic=a[key],numerical=b[key],scaled_error=abs(a[key]-b[key])/max(1,abs(a[key]))))
    return rows

def all_in(prices,policy,target_bps=20):
    if not math.isfinite(target_bps) or target_bps<0:raise ValueError('invalid target option cost')
    result=simulate(prices,policy)
    maturity=(len(prices)-1)/252
    premium=greeks(prices[0],prices[0],maturity,.02,.25)['price']
    entry_cost=premium*target_bps/10000
    # Fund target-option entry cost from the same borrowing account until expiry.
    return dict(pnl=result['terminal_pnl']-entry_cost*math.exp(.02*maturity),
        trade_fees=result['fees']+entry_cost,target_entry_fee=entry_cost,
        target_fee_financing=entry_cost*math.expm1(.02*maturity))

def paired_ci(a,b,seed=73):
    if len(a)!=len(b) or len(a)<2:raise ValueError('paired samples required')
    a=np.asarray(a);b=np.asarray(b);rng=np.random.default_rng(seed)
    # Shared path indexes preserve policy pairing. Negative difference favours gamma hedge.
    draws=[]
    for _ in range(2000):
        ix=rng.integers(0,len(a),len(a));draws.append(np.sqrt(np.mean(b[ix]**2))-np.sqrt(np.mean(a[ix]**2)))
    return [float(x) for x in np.quantile(draws,[.025,.975])]

def write_csv(p,rows):
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)

def main():
    out=ROOT/'results';rows=audit_rows();write_csv(out/'greek_validation.csv',rows)
    trials=[];summary={}
    for regime in ['diffusion','jump']:
        paired={p:[] for p in ['delta','delta_gamma']}
        for seed in range(2000,2150):
            prices=path(seed,regime)
            for policy in paired:
                result=all_in(prices,policy);paired[policy].append(result['pnl'])
                trials.append(dict(regime=regime,seed=seed,policy=policy,**result))
        summary[regime]={}
        for policy,values in paired.items():
            z=np.asarray(values);fees=[x['trade_fees'] for x in trials if x['regime']==regime and x['policy']==policy]
            summary[regime][policy]=dict(paths=len(z),rmse=float(np.sqrt(np.mean(z*z))),mean_pnl=float(z.mean()),loss_probability=float(np.mean(z<0)),worst_5pct_mean=float(np.sort(z)[:math.ceil(.05*len(z))].mean()),mean_fees=float(np.mean(fees)))
        summary[regime]['paired_rmse_difference_95pct']=paired_ci(paired['delta'],paired['delta_gamma'])
    write_csv(out/'all_in_hedge_trials.csv',trials)
    errors={g:max(r['scaled_error'] for r in rows if r['greek']==g) for g in ['delta','gamma','vega','theta','rho']}
    report=dict(greek_checks=len(rows),max_scaled_errors=errors,results=summary,
        source=dict(name='Seeded synthetic diffusion and jump paths from hedging.py',url='https://github.com/Anjaney336/derivatives-hedging-research/blob/main/hedging.py',access_date='2026-10-24',seeds=[2000,2149]),
        assumptions=dict(target_entry_bps=20,stock_bps=5,hedge_option_bps=20,rate=.02,pricing_vol=.25,steps=63,option_multiplier=1,dividends=0,bootstrap_seed=73,bootstrap_resamples=2000),
        interpretation='Long one financed ATM call, hedged with stock and optionally a longer-dated option. P&L in model currency units per target option, not account return. Lower RMSE means lower hedge error, not positive alpha.',
        limits='Synthetic backtest, not historical option-chain returns. Same-close theoretical fills; unlimited funding/stock borrow, no margin, taxes, stochastic implied-volatility surface or empirical spreads. Target entry fee is newly charged; terminal target settlement has no assumed fee. Bootstrap is conditional on this simulator and is not empirical market confidence.',
        scope='All five Greeks validated; dynamic delta/gamma hedging only. Vega/theta/rho measured, not dynamically neutralised.',
        hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [out/'greek_validation.csv',out/'all_in_hedge_trials.csv']})
    (out/'greek_audit.json').write_text(json.dumps(report,indent=2))
    fig,axes=plt.subplots(2,3,figsize=(12,7));units={'delta':1,'gamma':1,'vega':.01,'theta':1/252,'rho':.01}
    labels={'delta':'Delta / spot unit','gamma':'Gamma / spot unit²','vega':'Vega / +1 vol point','theta':'Theta / trading day','rho':'Rho / +1 percentage point rate'}
    for ax,key in zip(axes.flat,units):
        for days in [5,21,63]:
            spots=np.linspace(70,130,121);ax.plot(spots,[greeks(s,100,days/252,.02,.25)[key]*units[key] for s in spots],label=f'{days} days')
        ax.set(title=labels[key],xlabel='Spot; strike = 100');ax.legend(fontsize=8)
    axes.flat[-1].axis('off');axes.flat[-1].text(0,.8,'European calls, no dividends\nVolatility 25%; rate 2%\nAssumptions, not market quotes\nTheta uses 252-day model clock',va='top')
    fig.tight_layout();fig.savefig(out/'all_greeks.svg');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,4))
    for ax,regime in zip(axes,['diffusion','jump']):
        z=summary[regime];ax.bar(['Delta','Delta + gamma'],[z[p]['rmse'] for p in ['delta','delta_gamma']],color=['#2c6485','#568c78']);ax.set(title=regime.title()+' · 150 paired paths',ylabel='All-in terminal hedge RMSE')
    fig.suptitle('Target entry, rehedging costs and financing included — synthetic');fig.tight_layout();fig.savefig(out/'all_in_hedging.svg');plt.close(fig)
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
