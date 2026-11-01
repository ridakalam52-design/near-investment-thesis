import json, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.dates as md
from datetime import datetime
d=json.load(open('docs/data.json')); C={c['id']:c for c in d['charts']}
plt.rcParams.update({'font.size':12,'axes.spines.top':False,'axes.spines.right':False})
def dates(l): return [datetime.fromisoformat(x) for x in l]
# 1: Intents vs txns
fig,ax=plt.subplots(figsize=(12,6.75),dpi=120)
a=C['activity']; i=C['intents']
ia=i['datasets'][0]; ad=a['datasets'][0]
start=dates(i['labels'])[0]
x=[t for t in dates(a['labels'])]; y=[v for v in ad['data']]
xs=[(t,v) for t,v in zip(x,y) if t>=start and v is not None]
ax.plot([t for t,_ in xs],[v/1e6 for _,v in xs],color='#666',lw=2,label='L1 transactions/day (M, 7d avg)')
ax.set_ylabel('Transactions/day (millions)')
ax2=ax.twinx(); ax2.spines['top'].set_visible(False)
ax2.plot(dates(i['labels']),[ (v or 0)/1e6 for v in ia['data']],color='#00C08B',lw=2.5,label='NEAR Intents volume ($M/day, 7d avg)')
ax2.set_ylabel('Intents volume, $M/day')
ax.set_title('NEAR: value moved to Intents, base-layer usage fell',fontsize=17,fontweight='bold',loc='left')
fig.text(0.01,0.01,'Intents: $3.91B last 30d (+139% YoY). L1 tx/day 30d avg: 715,881 (-84% YoY). Source: DefiLlama, NearBlocks.',fontsize=10,color='#444')
h1,l1=ax.get_legend_handles_labels();h2,l2=ax2.get_legend_handles_labels();ax.legend(h1+h2,l1+l2,loc='upper left',frameon=False)
ax.xaxis.set_major_formatter(md.DateFormatter('%b %Y'))
fig.tight_layout(rect=(0,0.04,1,1)); fig.savefig('media/1_intents_vs_usage.png')
# 2: signals scorecard
s=d['signals']; fig,ax=plt.subplots(figsize=(12,6.75),dpi=120); ax.axis('off')
ax.set_title('12 falsifiable signals, re-run daily from public data: %d bull / %d bear'%(sum(x['status']=='BULL' for x in s),sum(x['status']!='BULL' for x in s)),fontsize=16,fontweight='bold',loc='left')
for k,x in enumerate(s):
    yy=0.93-k*0.077; col='#00A676' if x['status']=='BULL' else '#D64545'
    ax.text(0.0,yy,x['status'],color='white',fontweight='bold',fontsize=11,bbox=dict(boxstyle='round',fc=col,ec=col),transform=ax.transAxes)
    ax.text(0.09,yy,x['claim'].replace(' (corr above noise)','').replace(' changes lead on-chain usage changes by 1-4 weeks',' leads usage by 1-4 weeks').replace(' moves together with on-chain usage in the same week',' moves with usage same week'),fontsize=11.5,transform=ax.transAxes)
    v=x['value']; ax.text(0.97,yy,('%.2f'%v) if isinstance(v,(int,float)) else str(v),ha='right',fontsize=11.5,color='#333',transform=ax.transAxes)
fig.savefig('media/2_signals.png')
# 3: burn vs issuance
b=C['burn']; fig,ax=plt.subplots(figsize=(12,6.75),dpi=120)
for ds,c in zip(b['datasets'][:2],['#D64545','#333']):
    ax.plot(dates(b['labels']),ds['data'],lw=2,color=c,label=ds['label'])
for ds in b['datasets'][2:]:
    ax.plot(dates(b['labels']),ds['data'],lw=2.5,color='#3366CC',ls='--',label=ds['label'])
ax.set_yscale('log'); ax.legend(frameon=False,loc='upper right',bbox_to_anchor=(1,0.92),ncol=3,fontsize=10); ax.set_ylabel('NEAR per day (log)')
ax.set_title('Fee burn covers ~1% of NEAR issuance',fontsize=17,fontweight='bold',loc='left')
fig.text(0.01,0.01,b['sentence'].replace(' (Issuance on right axis.)',''),fontsize=9.5,color='#444')
fig.tight_layout(rect=(0,0.04,1,1)); fig.savefig('media/3_burn_vs_issuance.png')
