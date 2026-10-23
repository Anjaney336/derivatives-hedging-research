"""Self-financing delta/gamma hedge with a longer-dated model-priced option."""
import math,csv,json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pricing import greeks
from hedging import path

def positions(g,h,policy):
 if policy not in ['delta','delta_gamma']:raise ValueError('invalid policy')
 q=-g['gamma']/h['gamma'] if policy=='delta_gamma' and h['gamma']>1e-8 else 0.
 q=max(-5.,min(5.,q)) # explicit gross option position cap
 return -g['delta']-q*h['delta'],q

def simulate(prices,policy='delta_gamma',stock_bps=5,option_bps=20):
 if len(prices)<3 or any(not math.isfinite(s) or s<=0 for s in prices) or min(stock_bps,option_bps)<0:raise ValueError('invalid inputs')
 n=len(prices)-1;dt=1/252;r=.02;vol=.25;k=prices[0];cash=-greeks(k,k,n*dt,r,vol)['price'];stock=opt=0.;fees=0.;ledger=[]
 for i,s in enumerate(prices):
  if i:cash*=math.exp(r*dt)
  g=greeks(s,k,(n-i)*dt,r,vol);h=greeks(s,k,(n-i+21)*dt,r,vol)
  pre=cash+stock*s+opt*h['price']+g['price']
  ns,no=positions(g,h,policy) if i<n else (0.,0.)
  fee=abs(ns-stock)*s*stock_bps/1e4+abs(no-opt)*h['price']*option_bps/1e4
  cash-=(ns-stock)*s+(no-opt)*h['price']+fee;stock,opt=ns,no;fees+=fee
  post=cash+stock*s+opt*h['price']+g['price']
  ledger.append(dict(step=i,pre_wealth=pre,post_wealth=post,fee=fee,stock=stock,hedge_options=opt,residual_delta=g['delta']+stock+opt*h['delta'],residual_gamma=g['gamma']+opt*h['gamma']))
 return {'terminal_pnl':cash+g['price'],'fees':fees,'ledger':ledger}

def run():
 out=Path(__file__).parent/'results';rows=[]
 for regime in ['diffusion','jump']:
  for seed in range(2000,2150):
   for policy in ['delta','delta_gamma']:
    r=simulate(path(seed,regime),policy);rows.append({'regime':regime,'seed':seed,'policy':policy,'terminal_pnl':r['terminal_pnl'],'fees':r['fees']})
 with (out/'gamma_trials.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
 report={}
 for regime in ['diffusion','jump']:
  for policy in ['delta','delta_gamma']:
   z=[r for r in rows if r['regime']==regime and r['policy']==policy];report[regime+'_'+policy]={'runs':len(z),'rmse':math.sqrt(sum(r['terminal_pnl']**2 for r in z)/len(z)),'mean_pnl':sum(r['terminal_pnl'] for r in z)/len(z),'mean_fees':sum(r['fees'] for r in z)/len(z)}
 (out/'gamma_summary.json').write_text(json.dumps({'results':report,'assumptions':{'pricing_vol':.25,'rate':.02,'hedge_option_extra_days':21,'stock_cost_bps':5,'option_cost_bps':20,'max_hedge_options':5},'source':'Synthetic price paths, hedging.py; model-priced calls','source_url':'https://github.com/Anjaney336/derivatives-hedging-research/blob/main/hedging.py','access_date':'2026-10-24','limits':'Same-close theoretical fills, no option chain, margin, borrow fees, dividends or liquidity constraint. Gamma capped near unstable denominators; residual risk reported.'},indent=2))
 fig,axs=plt.subplots(1,2,figsize=(10,4.5))
 for ax,reg in zip(axs,['diffusion','jump']):
  ax.boxplot([[r['terminal_pnl'] for r in rows if r['regime']==reg and r['policy']==pol] for pol in ['delta','delta_gamma']],tick_labels=['Delta','Delta + gamma']);ax.set(title=reg.title(),ylabel='Terminal model P&L per option');ax.axhline(0,color='gray')
 fig.suptitle('600 paired-policy stress runs — costs included');fig.tight_layout();fig.savefig(out/'gamma_hedging.svg');print(json.dumps(report,indent=2))
if __name__=='__main__':run()
